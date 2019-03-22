#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-08-09
:Author: wuyq
:Description:
            1、在节点A（los节点）中创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
            2、使用2个主机与节点A建立iscsi连接，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
            3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
            4、在步骤3中的业务运行过程中，将主oJmgs进程挂住；
            5、主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
            6、比较存储内部数据一致性。
:Changerlog:
"""
import os,sys
import commands
import threading
import random
import time
import utils_path
import common2
import common
import log
import get_config
import ReliableTest
import login
import prepare_x1000
import breakdown

conf_file = common2.CONF_FILE    #配置文件路径
osan = common2.oSan()
reliable = breakdown.Os_Reliable()
disk = breakdown.disk()
node = common.Node()
# 初始化日志文件
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)     #获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)       #初始化日志文件
osan.init_win_log(file_name)                    #初始化windows日志文件
#获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()
#修改vdbench配置文件的参数值
mix_R_Align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                               xfersize="(4k,80,16k,20)",
                               seekpct=0,
                               rdpct=0)
mix_R = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(4k,80,16,20)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)
mix_R_win = osan.gen_win_vdb_conf(xfersize="(4k,80,16k,20)",
                                  seekpct=0,
                                  rdpct=0)
# 获取主ojmgs的IP
(stdout,m_oJmgs_ip)=reliable.oJmgs_master_id()
log.info("Get fault process:master oJmgs")

def up_down():
    time.sleep(100)
    log.info("Step4:将节点主oJmgs进程挂住,节点: %s." %(m_oJmgs_ip))
    reliable.run_pause_process('oJmgs',m_oJmgs_ip)
    time.sleep(100)
    (stdout, oJmgs_ip) = reliable.oJmgs_master_id()
    log.info("Step5:检查节点新主oJmgs进程状态,节点: %s." % (oJmgs_ip))
    reliable.check_process_stat(oJmgs_ip,'oJmgs')
    log.info("Step5:检查挂起节点oJmgs进程状态,节点: %s." % (m_oJmgs_ip))
    reliable.check_process_stat(m_oJmgs_ip,'oJmgs')
    time.sleep(100)
    log.info("Step5:恢复挂起节点oJmgs进程,节点: %s." % (m_oJmgs_ip))
    reliable.run_process('oJmgs', m_oJmgs_ip)
    time.sleep(100)
    log.info("Step5:检查恢复后节点oJmgs进程状态,节点: %s." % (m_oJmgs_ip))
    reliable.check_process_stat(m_oJmgs_ip, 'oJmgs')

def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0],jn_jro="jn",time=900)
    log.info("Step6:主机1上业务完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")
def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0],time=1200)

def win_vdb_run():
    log.info("Step3:在windows主机上运行vdbench -f mix-R-win.conf.")
    osan.run_win_vdb(file_name, mix_R_win, jn_jro="jn", time=900)

def case():
    test_threads = []
    test_threads.append(threading.Thread(target=up_down))
    test_threads.append(threading.Thread(target=vdb_jn))
    test_threads.append(threading.Thread(target=win_vdb_run))
    test_threads.append(threading.Thread(target=vdb_run))
    for test_thread in test_threads:
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()
    for c_ip in client_ips:
        osan.vdb_check(c_ip=c_ip, time=100, oper="iops", output=deploy_ips[0])
    for ip in vip:
        for cli in client_ips:
			pass
            #osan.iscsi_logout(cli,vip=ip)
def main():
    prepare_x1000.x1000_test_prepare(file_name)
    case()
if __name__ == '__main__':
    main()

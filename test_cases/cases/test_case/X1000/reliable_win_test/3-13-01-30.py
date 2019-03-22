#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-09-15
:Author: wuyq
"1、在节点A（los节点）上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机与节点A建立iscsi连接，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
4、在步骤3中的业务运行过程中，将节点A和原日志组节点B同时断开数据网；
5、业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
6、比较存储内部数据一致性。"

:Changerlog:
"""
import os
import sys
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
import error
import breakdown

conf_file = common2.CONF_FILE    #配置文件路径
osan = common2.oSan()
reliable = breakdown.Os_Reliable()
disk = breakdown.disk()
node = common.Node()

file_name = os.path.basename(__file__)
file_name = file_name[:-3]                      # 获取本脚本名，去掉.py后缀
#log_file_path = log.get_log_path(file_name)     #获取日志目录，即test_cases/Log/Case_log
#log.init(log_file_path, True)                   #初始化日志文件
error.rel_check_before_run(file_name, jnl_rep=3, node_num=3)  # 运行前检查集群环境
osan.init_win_log(file_name)

# 获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()
# 修改vdbench配置文件的参数值
mix_R_win = osan.gen_win_vdb_conf(xfersize="(4k,80,16k,20)",
                                  seekpct=0,
                                  rdpct=0)
mix_R_Align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                               xfersize="(4k,80,16k,20)",
                               seekpct=0,
                               rdpct=0)
mix_R = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(4k,80,16k,20)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)

# 从所有服务节点中选出日志节点A
jnl_node_ids = error.get_jnl_node_id()
if len(jnl_node_ids) < 3:
    log.error("jnl node numbers less than 3!")
    os._exit(1)
fault_node_ids = random.sample(jnl_node_ids, 2)

def up_down():
    log.info("故障点:将两个日志节点数据网络连续故障恢复")
    time.sleep(100)
    for fault_id in fault_node_ids:
        fault_ip = disk.get_node_ip_by_id(n_id=fault_id)
        data_eth_list = error.get_data_eth(fault_id)
        log.info("Step4:业务过程中,将日志节点的数据网故障,日志节点:%s" % fault_ip)
        thread_list = []
        for eth_name in data_eth_list:
            thread_list.append(threading.Thread(target=reliable.network_test, args=(fault_ip, eth_name, 'down')))
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()
        time.sleep(100)
        log.info("Step5:100s后,将日志节点的数据网恢复,日志节点:%s" % fault_ip)
        thread_list = []
        for eth_name in data_eth_list:
            thread_list.append(threading.Thread(target=reliable.network_test, args=(fault_ip, eth_name, 'up')))
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()

    log.info("Step7:数据修复完成系统恢复正常后,比较内部数据一致性")
    reliable.compare_data()

def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jn",time=900)
    log.info("Step6:主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")

def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0],time=1000)
def win_vdb_run():
    log.info("Step3:在windows主机上运行vdbench -f mix-R-win.conf.")
    osan.run_win_vdb(file_name, mix_R_win, jn_jro="jn", time=900)


def case():
    test_threads = []
    test_threads.append(threading.Thread(target=up_down))
    test_threads.append(threading.Thread(target=vdb_jn))
    test_threads.append(threading.Thread(target=vdb_run))
    test_threads.append(threading.Thread(target=win_vdb_run))
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

if __name__ == '__main__':
    case()

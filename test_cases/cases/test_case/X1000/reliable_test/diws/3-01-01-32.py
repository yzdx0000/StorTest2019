#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-08-14
:Author: diws
:Description:
            1、系统上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
            2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
            3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
            4、在步骤3中的业务运行过程中，将节点A掉电；
            5、五分钟后节点A恢复等数据修复完成；
            6、重复步骤4，步骤5依次故障日志组中剩下的4个节点；
            7、在主机1上运行vdbench -f mix-S-Align.conf -jro比较数据一致性；
            7、数据修复完成后，比较存储内部数据一致性。
:Changerlog:
"""
import os,sys
import commands
import threading
import random
import time
import re
import utils_path
import common2
import common
import log
import get_config
import ReliableTest
import login
import error
import breakdown
import prepare_clean

conf_file = common2.CONF_FILE    #配置文件路径
osan = common2.oSan()
disk = breakdown.disk()
node = common.Node()
# 初始化日志文件
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
#获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()
#修改vdbench配置文件的参数值
mix_R_Align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                               xfersize="(1k,100)",
                               seekpct=0,
                               rdpct=0)
mix_R = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(3k,100)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)
#检查日志节点副本数
disk_rep = disk.get_jnl_replica(s_ip=deploy_ips[0])
if disk_rep == 1:
    log.error("Sorry,I can not going on,because there is only one jnl replica.")
    exit(1)
else:
    fault_node_ip = []
    jnl_ids = disk.get_jnl_node_id()
    fault_ids = jnl_ids
    # 选择所有日志节点ID并获取其IP
    for id in fault_ids:
        fault_node_ip = node.get_node_ip_by_id(id))
def up_down(pipeout):
    time.sleep(100)
    for ip in fault_node_ip:
        log.info("Step4:将节点%s重启." %(ip))
        tmp = error.down_node(fault_ip=ip)
        tmp = re.sub('\r','',tmp)
        time.sleep(1)
        error.up_node(node_info=tmp)
        """检查修复"""
        log.info("Step4:等待数据修复")
        for id in fault_ids:
            while 'HEALTHY' not in node.get_node_state(id):
                time.sleep(30)
                log.info("Step4:等待节点%s数据修复ing" %(ip))
    os.write(pipeout,"check")
def vdb_jn(pipein):
    log.info("Step3:在主机1上运行vdbench -f mix_R_Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0],jn_jro="jn")
    while True:
        line = os.read(pipein,32)
        if len(line) != 0:
            log.info("所有3个节点重启完毕。")
            break
        time.sleep(30)
    for ip in deploy_ips:
        common.check_ip(ip)
    log.info("Step7:修复完成后在主机1上执行vdbench -f mix_R_Align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")
def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0],time=2400)
def case():
    (pipein,pipeout) = os.pipe()
    test_threads = []
    test_threads.append(threading.Thread(target=up_down, args=(pipeout,)))
    test_threads.append(threading.Thread(target=vdb_jn, args=(pipein,)))
    test_threads.append(threading.Thread(target=vdb_run))
    for test_thread in test_threads:
        test_thread.setDaemon(True)
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()
    for c_ip in client_ips:
        osan.vdb_check(c_ip=c_ip, time=100, oper="iops", output=deploy_ips[0])
    for ip in vip:
        for cli in client_ips:
            osan.iscsi_logout(cli,vip=ip)
def main():
    prepare_clean.test_prepare(file_name,node_num=5)
    case()
if __name__ == '__main__':
    common.case_main(main)

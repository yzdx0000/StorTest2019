#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-08-15
:Author: diws
:Description:
            1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
            2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
            3、在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
            4、在步骤3中的业务运行过程中，将节点A掉电；
            5、日志free节点D在接管节点A日志后整系统掉电；
            6、将整系统4节点都上电恢复；
            7、日志同步后，节点D再次掉电；
            8、在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性；
            9、节点D上电恢复，数据修复完成后，比较存储内部数据一致性。
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
mix_S_Align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                               xfersize="(1k,100)",
                               seekpct=0,
                               rdpct=0)
mix_S = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(3k,100)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)
#检查日志节点副本数
disk_rep = disk.get_jnl_replica(s_ip=deploy_ips[0])
#获取所有节点
nodes = osan.get_nodes(s_ip=deploy_ips[0])
free_jnl_ips = []
use_jnl_ips = []
if disk_rep == 1:
    log.error("Sorry,I can not going on,because there is only one jnl replica.")
    exit(1)
else:
    use_jnl_ids = osan.get_same_jnl_group(1)
    if len(use_jnl_ids) < 1:
        print "There is not enough jnl nodes.We need three,but there is noly %d nodes." %(len(use_jnl_ids))
        exit(1)
    else:
        for id in use_jnl_ids:
            use_jnl_ips.append(node.get_node_ip_by_id(id))
    free_jnl_ids = error.get_free_jnl_id()
    if len(free_jnl_ids) == 0:
        print "There is no free jnl nodes."
        exit(1)
    else:
        for id in free_jnl_ids:
            free_jnl_ips.append(node.get_node_ip_by_id(id))
fault_node_a_ip = random.choice(use_jnl_ips)
use_jnl_ips.remove(fault_node_a_ip)
node_info = []
def up_down():
    time.sleep(100)
    log.info("Step4:将节点A掉电 : %s." %(fault_node_a_ip))
    tmp = error.down_node(fault_ip=fault_node_a_ip)
    tmp = re.sub('\r','',tmp)
    node_info.append(tmp.strip())
def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix-S-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_S_Align, output=deploy_ips[0],jn_jro="jn")
    time.sleep(30)
    #将整集群掉电
    log.info("Step5:日志free节点D接管后，整系统掉电.")
    for ip in use_jnl_ips:
        log.info("节点%s下电." % (ip))
        tmp = error.down_node(fault_ip=ip)
        tmp = re.sub('\r', '', tmp)
        node_info.append(tmp.strip())
    for ip in free_jnl_ips:
        log.info("节点%s下电." % (ip))
        tmp = error.down_node(fault_ip=ip)
        tmp = re.sub('\r', '', tmp)
        node_info.append(tmp.strip())
    #将集群上电
    log.info("Step6:将集群四节点上电.")
    for vid in node_info:
        error.up_node(node_info=vid.strip())
    for ip in deploy_ips:
        common.check_ip(ip)
    log.info("Step7:将节点D再次掉电.")
    tmp = error.down_node(fault_ip=free_jnl_ips[0])
    log.info("Step8:在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_S_Align, output=deploy_ips[0], jn_jro="jro")
    log.info("Step9:节点D上电恢复。")
    error.up_node(node_info=tmp)
    log.info("Step9:等待系统修复。")
    for id in nodes:
        while 'HEALTHY' not in node.get_node_state(id):
            time.sleep(20)
            log.info("Step9:等待数据修复ing")
    log.info("Step9:数据修复完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_S_Align, output=deploy_ips[0], jn_jro="jro")
def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-S.conf.")
    osan.run_vdb(client_ips[1], mix_S, output=deploy_ips[0],time=2400)
def case():
    test_threads = []
    test_threads.append(threading.Thread(target=up_down))
    test_threads.append(threading.Thread(target=vdb_jn))
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
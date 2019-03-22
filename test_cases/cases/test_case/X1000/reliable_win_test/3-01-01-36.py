#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-08-15
:Author: diws
:Description:
            1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
            2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
            3、在主机1上运行vdbench -f mix-R-align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
            4、在步骤3中的业务运行过程中，将节点A重启；
            5、节点B在接管节点A日志后重建过程中，将节点B重启；
            6、数据修复完成后，在主机1上执行vdbench -f mix-R-align.conf -jro比较一致性；
            7、比较存储内部数据一致性。
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
import prepare_x1000

conf_file = common2.CONF_FILE    #配置文件路径
osan = common2.oSan()
disk = breakdown.disk()
node = common.Node()
# 初始化日志文件
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
error.rel_check_before_run(file_name, jnl_rep=3, node_num=3, free_jnl_num=0, data_rep=3)
osan.init_win_log(file_name)

#获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()
#修改vdbench配置文件的参数值
mix_R_win = osan.gen_win_vdb_conf(xfersize="(4k,80,16k,20)",
                                  seekpct=0,
                                  rdpct=0)
mix_S_align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                               xfersize="(4k,80,16k,20)",
                               seekpct=0,
                               rdpct=0)
mix_S = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(4k,80,16k,20)",
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
    if len(use_jnl_ids) < 2:
        print "There is not enough jnl nodes.We need three,but there is noly %d nodes." %(len(use_jnl_ids))
        exit(1)
    else:
        for id in use_jnl_ids:
            use_jnl_ips.append(node.get_node_ip_by_id(id))
    free_jnl_ids = error.get_free_jnl_id()
    if len(free_jnl_ids) != 0:
        print "Sorry,I can not run for I detect your cluster have free jnl node."
    else:
        for id in free_jnl_ids:
            free_jnl_ips.append(node.get_node_ip_by_id(id))
fault_node_a_ip = random.choice(use_jnl_ips)
use_jnl_ips.remove(fault_node_a_ip)
fault_node_b_ip = random.choice(use_jnl_ips)
node_info = []
def up_down():
    time.sleep(100)
    log.info("Step4:将节点A重启 : %s." %(fault_node_a_ip))
    #将节点A下电
    tmp = error.down_node(fault_ip=fault_node_a_ip)
    tmp = re.sub('\r','',tmp)
    #将节点A上电
    error.up_node(node_info=tmp)
    for ip in deploy_ips:
        common.check_ip(ip)
        error.check_host(ip)
    time.sleep(5)
    #将日志节点B下电
    log.info("Step5:将日志节点B重启 : %s." % (fault_node_b_ip))
    tmp = error.down_node(fault_ip=fault_node_b_ip)
    tmp = re.sub('\r','',tmp)
    #将日志节点B上电
    error.up_node(node_info=tmp)
    for ip in deploy_ips:
        common.check_ip(ip)
        error.check_host(ip)
def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix-S-align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0],jn_jro="jn")
    time.sleep(30)
    for ip in deploy_ips:
        common.check_ip(ip)
        error.check_host(ip)
    log.info("Step6:等待系统修复。")
    for id in nodes:
        while 'HEALTHY' not in node.get_node_state(id):
            time.sleep(20)
            log.info("Step9:等待数据修复ing")
    log.info("Step6:数据修复完成后，在主机1上执行vdbench -f mix-S-align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-S.conf.")
    osan.run_vdb(client_ips[1], mix_S, output=deploy_ips[0],time=2400)

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
def main():
    case()
if __name__ == '__main__':
    common.case_main(main)

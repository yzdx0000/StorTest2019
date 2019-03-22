#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-08-06
:Author: diws
:Description:
            1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
            2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
            3、在主机1上运行vdbench -f mix-S-align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
            4、将非日志节点D下电；
            5、十分钟后节点D上电；
            6、重复步骤4，5共3次；
            7、业务完成后，在主机1上执行vdbench -f mix-S-align.conf -jro比较一致性；
            8、数据修复完成后比较存储内部数据一致性.
:Changerlog:
"""
# testlink case: 1000-32527
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
error.rel_check_before_run(file_name, jnl_rep=3, node_num=5, free_jnl_num=0, data_rep=3)

#log_file_path = log.get_log_path(file_name)     #获取日志目录，即test_cases/Log/Case_log
#log.init(log_file_path, True)       #初始化日志文件
#获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()
#修改vdbench配置文件的参数值
mix_S_align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                         xfersize="(3k,100)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)
mix_S = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(3k,100)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)
# 获取日志节点ID及其IP
jnl_nodes_id = disk.get_jnl_node_id()
nodeids = osan.get_nodes(deploy_ips[0])
# 获取非日志节点ID
node_no_jnl_ids = list(set(nodeids).difference(set(jnl_nodes_id)))
if len(node_no_jnl_ids) == 0:
    node_no_jnl_ids = nodeids
# 随机选择一个业务接入节点ID并获取其IP
fault_node_id = random.choice(node_no_jnl_ids)
fault_node_ip = node.get_node_ip_by_id(fault_node_id)
log.info("Get fault ip:%s" % (fault_node_ip))
def up_down():
    time.sleep(100)
    for i in range(3):
        log.info("Step4:将日志节点D下电 : %s." %(fault_node_ip))
        fault_node_info = error.down_node(fault_ip=fault_node_ip)
        time.sleep(300)
        log.info("Step4:五分钟后节点D上电 : %s." % (fault_node_info))
        error.up_node(node_info=fault_node_info.strip())
        time.sleep(200)
def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix-S-align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0],jn_jro="jn")
    log.info("Step5:主机1上业务完成后，在主机1上执行vdbench  mix-S-align.conf -jro比较一致性..")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    for ip in deploy_ips:
        common.check_ip(ip)
        error.check_host(ip)
    log.info("Step6:数据修复中，在主机1上执行vdbench -f mix-S-align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    log.info("Step7:等待数据修复")
    for id in nodeids:
        while 'HEALTHY' not in node.get_node_state(id):
            time.sleep(20)
            log.info("Step7:等待数据修复ing")
    log.info("Step7:节点C数据修复完成，在主机1上执行vdbench -f mix-S-align.conf -jro比较一致性；")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-S.conf.")
    osan.run_vdb(client_ips[1], mix_S, output=deploy_ips[0],time=1200)
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
            pass
            #osan.iscsi_logout(cli,vip=ip)
def main():
    case()
if __name__ == '__main__':
    main()

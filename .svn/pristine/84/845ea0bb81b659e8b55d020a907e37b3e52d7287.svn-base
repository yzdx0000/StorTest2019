#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-08-06
:Author: diws
:Description:
            1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
            2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
            3、在主机1上运行vdbench -f mix-S-align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
            4、将非日志节点D和节点E下电；
            5、十分钟后节点D和节点E上电；
            6、重复步骤4，5共3次；
            7、业务完成后，在主机1上执行vdbench -f mix-S-align.conf -jro比较一致性；
            8、数据修复完成后比较存储内部数据一致性.
:Changerlog:
"""
# testlink case: 1000-32530
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
error.rel_check_before_run(file_name, jnl_rep=3, node_num=5, free_jnl_num=0, data_rep=3)

#获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()
#修改vdbench配置文件的参数值
mix_S_align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                               xfersize="(1k,100)",
                               seekpct=45,
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
fault_node_ip = []
for i in range(2):
    # 随机选择一个非日志节点ID并获取其IP
    fault_node_id = random.choice(node_no_jnl_ids)
    node_no_jnl_ids.remove(fault_node_id)
    fault_node_ip.append(node.get_node_ip_by_id(fault_node_id))
    #如果非日志节点只有一个，则退出
    if len(node_no_jnl_ids) == 0:
        break
def up_down():
    time.sleep(100)
    for i in range(3):
        fault_node_info = []
        for ip in fault_node_ip:
            log.info("Step4:将节点下电 : %s." %(ip))
            tmp = error.down_node(fault_ip=ip)
            tmp = re.sub('\r', '', tmp)
            fault_node_info.append(tmp.strip())
        time.sleep(200)
        for ip in fault_node_info:
            tmp = re.sub('\r','',ip)
            log.info("Step4:节点上电 : %s." % (tmp.strip()))
            error.up_node(node_info=tmp.strip())
        time.sleep(300)
def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix_S_align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0],jn_jro="jn")
    log.info("Step5:主机1上业务完成后，在主机1上执行vdbench -f mix_S_align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    for ip in deploy_ips:
        common.check_ip(ip)
        error.check_host(ip)
    log.info("Step6:等待数据修复")
    for id in nodeids:
        while 'HEALTHY' not in node.get_node_state(id):
            time.sleep(20)
            log.info("Step6:等待数据修复ing")
    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-R.conf.")
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

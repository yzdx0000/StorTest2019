#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-08-07
:Author: wuyq
:Description:
            1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
            2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
            3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
            4、在步骤3中的业务运行过程中，将节点D数据网断开；
            5、主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
            6、等待节点D超时后，将节点E数据网断开；
            7、恢复数据网，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；:Changerlog:
"""
# testlink case: 1000-32948
import os,sys
import threading
import commands
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
# 初始化日志文件
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
error.rel_check_before_run(file_name, jnl_rep=3, node_num=4)
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
                         xfersize="(4k,80,16k,20)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)

# 随机选择两个个业务接入节点ID并获取其IP
non_free_node_ids = error.get_non_free_node_id()
if len(non_free_node_ids) == 0:
    non_free_node_ids = osan.get_nodes()
fault_node_id1 = random.choice(non_free_node_ids)
fault_node_ip1 = node.get_node_ip_by_id(fault_node_id1)
non_free_node_ids.remove(fault_node_id1)
fault_node_id2 = random.choice(non_free_node_ids)
fault_node_ip2 = node.get_node_ip_by_id(fault_node_id2)
fault_eth_list1 = error.get_data_eth(fault_node_id1)
fault_eth_list2 = error.get_data_eth(fault_node_id2)
log.info("Get fault ip:%s,%s" % (fault_node_ip1, fault_node_ip2))

def up_down():
    time.sleep(200)
    log.info("Step4:将节点A的数据网断开 : %s." % (fault_node_ip1))
    for fault_eth_name in fault_eth_list1:
        breakdown.network_test(fault_node_ip1,fault_eth_name,'down')
    cmd = 'ssh ' + fault_node_ip1 + ' "pscli --command=update_param --section=MGR --name=node_isolate_timeout --current=60000"'
    rc = os.system(cmd)
    if 0 != rc:
        log.info("update param failed!!!")
    time.sleep(100)
    log.info("Step5:节点A超时后将节点B的数据网断开 : %s." % (fault_node_ip2))
    for fault_eth_name in fault_eth_list2:
        breakdown.network_test(fault_node_ip2, fault_eth_name, 'down')
    log.info("Step6:将节点A的数据网恢复,节点: %s" % (fault_node_ip1))
    for fault_eth_name in fault_eth_list1:
        breakdown.network_test(fault_node_ip1, fault_eth_name, 'up')
    log.info("Step6:将节点B的数据网恢复,节点: %s" % (fault_node_ip2))
    for fault_eth_name in fault_eth_list2:
        breakdown.network_test(fault_node_ip2, fault_eth_name, 'up')
    cmd = 'ssh ' + fault_node_ip1 + ' "pscli --command=update_param --section=MGR --name=node_isolate_timeout --current=86400000"'
    rc = os.system(cmd)
    if 0 != rc:
        log.info("update param failed!!!")

def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f OLTP.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0],jn_jro="jn",time=1200)
    log.info("Step5:主机1上业务完成后，执行vdbench -f mix-S-Align.conf -jro比较一致性")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")

    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0],time=1200)
def case():
    test_threads = []
    test_threads.append(threading.Thread(target=up_down))
    test_threads.append(threading.Thread(target=vdb_jn))
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
    case()
if __name__ == '__main__':
    main()
#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-09-10
:Author: wuyq
:Description:
1、在节点A（los节点）中创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机与节点A建立iscsi连接，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
4、在步骤3中的业务运行过程中，将节点A一个业务网和所有节点的数据网断开；
5、检查主机业务运行状态
6、主机1上业务完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性；
7、比较存储内部数据一致性。
:Changerlog:
"""
# testlink case: 1000-32709
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

conf_file = common2.CONF_FILE    # 配置文件路径
osan = common2.oSan()
reliable = breakdown.Os_Reliable()
disk = breakdown.disk()
node = common.Node()

file_name = os.path.basename(__file__)
file_name = file_name[:-3]                      # 获取本脚本名，去掉.py后缀
error.rel_check_before_run(file_name, free_jnl_num=1, jnl_rep=3, node_num=4)
# 获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()
# 修改vdbench配置文件的参数值
mix_R_Align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                               xfersize="(4k,80,16k,20)",
                               seekpct=0,
                               rdpct=0)
mix_R = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(4k,80,16k,20)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)

# 随机选择一个业务接入节点ID并获取其IP
fault_vip = random.choice(vip)
fault_io_ip = osan.get_node_by_vip(fault_vip)
fault_io_id = node.get_node_id_by_ip(fault_io_ip)
io_eth_list = error.get_io_eth(fault_io_id)
io_eth_name = random.choice(io_eth_list)

event1 = threading.Event()
event2 = threading.Event()
event3 = threading.Event()
def up_down():
    log.info("故障点:一个节点的一个业务网卡和所有节点的数据网卡同时故障")
    time.sleep(100)
    log.info("Step4:在步骤3中的业务运行过程中，先将业务节点的一根业务网断开,节点: %s." % fault_io_ip)
    thread_list = []
    data_eth_lists = []
    reliable.network_test(fault_io_ip, io_eth_name, 'down')

    event1.wait()
    event3.wait()
    log.info("Step5:业务完成后,后将所有节点的数据网断开")
    for fault_ip in deploy_ips:
        fault_id = node.get_node_id_by_ip(fault_ip)
        data_eth_list = error.get_data_eth(fault_id)
        data_eth_lists.append(data_eth_list)
        for eth_name in data_eth_list:
            thread_list.append(threading.Thread(target=reliable.network_test, args=(fault_ip, eth_name, 'down')))
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()

    time.sleep(100)
    log.info("Step5:将故障业务节点的业务网恢复,节点: %s." %(fault_io_ip))
    reliable.network_test(fault_io_ip, io_eth_name, 'up')
    eth_index = 0
    for fault_ip in deploy_ips:
        log.info("Step6:将所有节点的所有数据网卡恢复,节点:%s" % (fault_ip))
        for eth_name in data_eth_lists[eth_index]:
            reliable.network_test(fault_ip, eth_name, 'up')
        eth_index += 1

    event2.set()
    log.info("Step8:数据修复完成系统恢复正常后，比较内部数据一致性")
    reliable.compare_data()

def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0],jn_jro="jn",time=1200)
    time.sleep(15)
    event1.set()
    event2.wait()
    log.info("Step6:主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")
    disk.multi_check_part_lun_uniform_by_ip()

def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0],time=1200)
    time.sleep(15)
    event3.set()

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

if __name__ == '__main__':
    case()
#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-12-25
:Author: wuyq
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
4、在步骤3中的业务运行过程中，将所有节点的数据网和业务网反复故障
5、数据网恢复后系统检查数据，系统配置恢复正常"

:Changerlog:
"""
# testlink case: 1000-32961
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
file_name = file_name[:-3]                                    # 获取本脚本名，去掉.py后缀
error.rel_check_before_run(file_name, jnl_rep=3, node_num=3)  # 运行前检查集群环境
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

event1 = threading.Event()
event2 = threading.Event()
event3 = threading.Event()

def up_down():
    log.info("故障点:业务完成后,将所有节点的业务网和数据网故障后恢复,后再进行数据校验.")
    time.sleep(100)
    event1.wait()
    event2.wait()
    time.sleep(15)
    thread_list_down = []
    thread_list_up = []
    for node_ip in deploy_ips:
        node_id = node.get_node_id_by_ip(node_ip)
        data_eth_list = error.get_data_eth(node_id)
        io_eth_list = error.get_io_eth(node_id)
        eth_list = list(set(data_eth_list + io_eth_list))
        for eth in eth_list:
            thread_list_down.append(threading.Thread(target=reliable.network_test, args=(node_ip, eth, 'down')))
            thread_list_up.append(threading.Thread(target=reliable.network_test, args=(node_ip, eth, 'up')))
    log.info("将所有节点的业务网和数据网络反复故障")
    for count in range(3):
        log.info("第 %s 次故障所有节点的业务网络和数据网络" % (count + 1))
        log.info("Step4:将所有节点的业务网络和数据网络故障.")
        for thread in thread_list_down:
            thread.start()
        for thread in thread_list_down:
            thread.join()
        time.sleep(60)
        log.info("Step5:将所有节点的业务网络和数据网络恢复.")
        for thread in thread_list_up:
            thread.start()
        for thread in thread_list_up:
            thread.join()
        time.sleep(60)
    time.sleep(15)
    event3.set()
    time.sleep(100)
    log.info("Step7:数据修复完成系统恢复正常后,比较内部数据一致性")
    reliable.compare_data()

def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jn", time=1200)
    event1.set()
    event3.wait()
    log.info("Step6:主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")

def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0], time=1200)
    event2.set()

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

if __name__ == '__main__':
    case()

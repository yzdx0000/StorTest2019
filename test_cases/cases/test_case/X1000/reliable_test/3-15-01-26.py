#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-09-15
:Author: wuyq
:Description:
1、在节点A（los节点）中创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机与节点A建立iscsix连接，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
4、在步骤3中的业务运行过程中，将节点D数据网断开；
5、数据开始修复，修复完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
6、等待超时后将节点E数据网断开；
7、数据开始修复，修复完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
:Changerlog:
"""
# testlink case: 1000-32901
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
error.rel_check_before_run(file_name, free_jnl_num=0, jnl_rep=2, node_num=3, data_rep=2)
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

# 从所有服务节点中选取服务节点A和非日志节点B


non_jnl_node = error.get_non_free_node_id()
if len(non_jnl_node) < 2:
    log.error("Error,the Non_JNL Node Number is less than 2!!! %s" % non_jnl_node)
    os._exit(-110)
non_jnl_id_A = random.choice(non_jnl_node)
non_jnl_node.remove(non_jnl_id_A)
non_jnl_id_B = random.choice(non_jnl_node)
non_jnl_ip_A = node.get_node_ip_by_id(non_jnl_id_A)
non_jnl_ip_B = node.get_node_ip_by_id(non_jnl_id_B)

data_eth_list_A = error.get_data_eth(non_jnl_id_A)
data_eth_list_B = error.get_data_eth(non_jnl_id_B)

def up_down():
    log.info("故障点:两个非日志节点的数据网故障,其中一个数据网故障超时")
    time.sleep(100)
    log.info("Step4:将非日志节点A的所有数据网故障,节点:%s" % non_jnl_ip_A)
    thread_list_A = []
    for eth_name in data_eth_list_A:
        thread_list_A.append(threading.Thread(target=reliable.network_test, args=(non_jnl_ip_A, eth_name, 'down')))
    for thread in thread_list_A:
        thread.start()
    for thread in thread_list_A:
        thread.join()
    time.sleep(60)
    log.info("Step5:将非日志节点A的数据网故障超时,节点:%s" % non_jnl_ip_A)
    reliable.run_down_node_wait(non_jnl_ip_B,'300000')
    time.sleep(300)
    log.info("Step6:将非日志节点B的所有数据网断开,节点:%s" % non_jnl_ip_B)
    thread_list_B = []
    for eth_name in data_eth_list_B:
        thread_list_B.append(threading.Thread(target=reliable.network_test, args=(non_jnl_ip_B, eth_name, 'down')))
    for thread in thread_list_B:
        thread.start()
    for thread in thread_list_B:
        thread.join()
    time.sleep(100)
    log.info("Step7:将故障节点的所有数据网络恢复,节点:%s,%s" % (non_jnl_ip_A, non_jnl_ip_B))
    for eth_name in data_eth_list_A:
        reliable.network_test(non_jnl_ip_A, eth_name, 'up')
    for eth_name in data_eth_list_B:
        reliable.network_test(non_jnl_ip_B, eth_name, 'up')


def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jn",time=1200)
    log.info("Step6:主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")

    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0], time=1200)

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

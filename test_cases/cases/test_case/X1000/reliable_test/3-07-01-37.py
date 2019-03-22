#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-09-15
:Author: wuyq
:Description:
"1、在节点A（los节点）中创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机与节点A建立iscsi连接，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
4、在步骤3中的业务运行过程中，先将日志节点节点C的业务网断开，再将日志节点数据网断开
5、等待30秒后同时将节点A和节点B数据网恢复；
6、业务完成后，主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性
7、数据修复完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性；
8、比较存储内部数据一致性"

:Changerlog:
"""
# testlink case: 1000-32681
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

# 从所有服务节点中选出日志节点A
jnl_node_list = error.get_jnl_node_id()
jnl_node_id = random.choice(jnl_node_list)
jnl_node_ip = node.get_node_ip_by_id(jnl_node_id)
# 获取节点的业务网卡与数据网卡
fault_io_eth_list = error.get_io_eth(jnl_node_id)
fault_data_eth_list = error.get_io_eth(jnl_node_id)

def up_down():
    log.info("故障点:先将故障节点的业务网断开,再将数据网断开")
    time.sleep(100)
    log.info("Step4:在步骤3中的业务运行过程中，先将故障的节点的业务网断开,节点:%s" % jnl_node_ip)
    for eth_name in fault_io_eth_list:
        reliable.network_test(jnl_node_ip, eth_name, 'down')
    time.sleep(30)
    log.info("Step5:再将故障的节点的数据网断开,节点:%s" % jnl_node_ip)
    for eth_name in fault_data_eth_list:
        reliable.network_test(jnl_node_ip, eth_name, 'down')
    time.sleep(30)
    log.info("Step6:30s后将故障的节点的业务网和数据网同时恢复,节点:%s" % jnl_node_ip)
    thread_list = []
    for io_eth_name in fault_io_eth_list:
        thread_list.append(threading.Thread(target=reliable.network_test, args=(jnl_node_ip, io_eth_name, 'up')))
    for data_eth_name in fault_data_eth_list:
        thread_list.append(threading.Thread(target=reliable.network_test, args=(jnl_node_ip, data_eth_name, 'up')))
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()

    log.info("Step7:数据修复完成系统恢复正常后，比较内部数据一致性")
    reliable.compare_data()

def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jn",time=1200)
    log.info("Step6:主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性")
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

if __name__ == '__main__':
    case()
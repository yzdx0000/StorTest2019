#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2019-02-26
:Author: wuyq
:Description:
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
4、在步骤3中的业务运行过程中，将日志节点A节点数据网出现10%数据包损坏；
5、主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
6、检查系统是否出现异常
:Changerlog:
"""
import os
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
import prepare_clean
import breakdown

conf_file = common2.CONF_FILE
osan = common2.oSan()
reliable = breakdown.Os_Reliable()
disk = breakdown.disk()
node = common.Node()

# 初始化日志文件
file_name = os.path.basename(__file__)
file_name = file_name[:-3]
prepare_clean.rel_check_before_run(file_name, jnl_rep=2, node_num=3, data_rep=2)

# 获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()

# 修改vdbench配置文件的参数值
mix_R_Align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                               xfersize="(4k,80,12k,20)",
                               seekpct=0,
                               rdpct=0)
mix_R = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(4k,80,12k,20)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)

# vdbench改为大块混合
# 获取某故障节点IP
event1 = threading.Event()
event2 = threading.Event()
fault_node_ip = random.choice(deploy_ips)
fault_node_id = node.get_node_id_by_ip(fault_node_ip)
data_eth_list = error.get_data_eth(fault_node_id)
phy_eth_ip = reliable.get_ip_by_eth(fault_node_ip, data_eth_list[0])

def up_down():
    time.sleep(100)
    log.info("数据网络注入故障前的延迟及丢包情况,节点:%s" % fault_node_ip)
    reliable.check_ping(fault_ip=fault_node_ip, fault_eth_ip=phy_eth_ip)
    log.info("Step4:业务读写过程中,将日志节点数据网数据包损坏部分,节点:%s" % fault_node_ip)
    thread_list = []
    for data_eth in data_eth_list:
        cmd = ("ssh %s 'tc qdisc add dev %s root netem corrupt 10%%'" % (fault_node_ip, data_eth))
        log.info(cmd)
        thread_list.append(threading.Thread(target=os.system, args=(cmd,)))
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()

    time.sleep(10)
    log.info("数据网络注入故障后延迟及丢包情况,节点:%s" % fault_node_ip)
    reliable.check_ping(fault_ip=fault_node_ip, fault_eth_ip=phy_eth_ip)
    time.sleep(100)
    log.info("检查网络异常节点管理通路是否正常")
    osan.get_nodes(fault_node_ip)

    event1.wait()
    event2.wait()

    log.info("检查集群是否出现坏对象及修复任务")
    disk.check_bad_obj()

    log.info("Step6:等待业务结束后,将网络恢复正常,节点:%s" % fault_node_ip)
    for data_eth in data_eth_list:
        cmd = ("ssh %s 'tc qdisc del dev %s root netem corrupt 10%%'" % (fault_node_ip, data_eth))
        log.info(cmd)
        rc = os.system(cmd)
        if rc == 0:
            log.info("数据网 %s 恢复成功,节点:%s" % (data_eth, fault_node_ip))

def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jn", time=1200)
    log.info("Step5:主机1上业务完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")
    event1.set()

    log.info("Step7:检查集群内部数据一致性.")
    disk.multi_check_part_lun_uniform_by_ip()

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

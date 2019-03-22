#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-11-21
:Author: wuyq
:Description:
"1、创建VIP地址池，配置4倍节点个数的VIP，IP切换均衡策略使用轮询，自动均衡策略设置为自动
2、查看自动均衡策略设置
3、创建LUN和对应的映射，并在主机端登录并下发读写业务
4、故障带业务的节点A的一个业务网卡，1分钟后故障另外一个业务网卡
5、等待自动均衡完成后，查看均衡情况和业务情况
6、恢复节点A的两个业务网卡
7、等待自动均衡完成后，查看均衡情况和业务情况"
:Changerlog:
"""

import os
import sys
import commands
import threading
import random
import time
import utils_path
import common
import common2
import Lun_managerTest
import log
import get_config
import env_manage_lun_manage
from get_config import config_parser as cp
import error
import breakdown

# 重新部署系统
conf_file = common2.CONF_FILE   # 配置文件路径
osan = Lun_managerTest.oSan()
reliable = breakdown.Os_Reliable()
disk = breakdown.disk()
node = common.Node()
com2 = common2.oSan()

file_name = os.path.basename(__file__)
file_name = file_name[:-3]      # 获取本脚本名，去掉.py后缀
# error.rel_check_before_run(file_name, jnl_rep=3, node_num=3)
log_file_path = log.get_log_path(file_name)
log.init(log_file_path, True)
# 重新部署系统
env_manage_lun_manage.xstor_install()

# 获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
sever_ips = deploy_ips[:]

def case():
    log.info("Step1:创建VIP地址池,配置4倍节点个数的VIP.VIP均衡策略:轮询,VIP均衡开关:自动.")
    subnet_id = osan.get_subnet_id(deploy_ips[0])
    vip = cp('add_vip_address_pool', 'vips')
    osan.add_vip_address_pool(s_ip=deploy_ips[0], subnet_id=subnet_id[0], domain_name='sugon.com', vip=vip,
                              ip_failover_policy='IF_ROUND_ROBIN', rebalance_policy='RB_AUTOMATIC')
    osan.enable_san(s_ip=deploy_ips[0], access_zone_id=1)

    time.sleep(30)
    log.info("Step2:查看自动均衡策略设置是否符合预期.")
    rebalance_policy, ip_failover_policy = osan.get_vip_policy(deploy_ips[0])
    if rebalance_policy == 'RB_AUTOMATIC' and ip_failover_policy == 'IF_ROUND_ROBIN':
        log.info("自动均衡策略设置成功.")
    else:
        log.error("自动均衡策略设置失败.\n期望:均衡策略->轮询;均衡开关->自动\n实际:均衡策略->%s;均衡开关->%s."
                  % (ip_failover_policy, rebalance_policy))
        os._exit(1)

    time.sleep(10)
    log.info("Step3:创建12条Lun,映射给主机,并下发读写业务")
    log.info("a.创建12条Lun")
    for count in range(12):
        lun_name = 'lun' + str(count + 1)
        osan.create_lun(s_ip=deploy_ips[0], lun_name=lun_name, stor_pool_id=2, acc_zone_id=1)
    log.info("b.创建一个主机组,然后添加一个主机")
    osan.create_host_group(deploy_ips[0], 'host_group1')
    osan.add_host(deploy_ips[0], 'host1', 1)

    log.info("c.将所有Lun映射给主机")
    for count in range(12):
        osan.map_lun(deploy_ips[0], count+1, 1)

    log.info("d.添加启动器,并修改主机启动器名称配置文件")
    iqn = cp('add_initiator', 'iqn')
    alias = cp('add_initiator', 'alias')
    osan.add_initiator(s_ip=deploy_ips[0], h_id=1, iqn=iqn, alias=alias)
    osan.write_iqn(client_ips[0], iqn)

    log.info("e.发现iscsi启动器,并且执行login操作")
    vips = osan.get_vips_by_pool(deploy_ips[0], 1)
    for vip in vips:
        target = osan.discover_scsi(client_ips[0], vip)
        osan.iscsi_login(client_ips[0], target)
    time.sleep(10)

def up_down():
    time.sleep(100)
    log.info("Step4:故障一个带业务节点的两个业务网卡")
    log.info("故障前集群vip的分布情况:")
    osan.get_vips_layout()
    fault_ip = random.choice(sever_ips)
    fault_id = breakdown.disk().get_node_id_by_ip(n_ip=fault_ip)
    io_eth_list = error.get_io_eth(fault_id)
    log.info("先故障一个业务网卡")
    reliable.network_test(fault_ip, io_eth_list[0], 'down')
    time.sleep(60)
    log.info("再故障另一个业务网卡")
    reliable.network_test(fault_ip, io_eth_list[1], 'down')
    time.sleep(100)
    log.info("Step5:等待自动均衡完成后,查看其他两个健康节点均衡情况")
    sever_ips.remove(fault_ip)
    while osan.check_vip_state() != 0:
        log.info("等待自动均衡完成中.")
        time.sleep(1)
    log.info("故障后集群vip的分布情况:")
    osan.get_vips_layout()
    vips = [len(osan.get_vips_by_node(x, 1)) for x in sever_ips]
    if len(set(vips)) == 1 and sum(vips) == len(deploy_ips) * 4:
        log.info("VIP自动均衡成功!健康两节点每个节点VIP数量为6")
    else:
        log.error("异常!VIP自动均衡失败,数量分布情况:%s" % ','.join(map(str, vips)))
        reliable.network_test(fault_ip, io_eth_list[0], 'up')
        reliable.network_test(fault_ip, io_eth_list[1], 'up')
        os._exit(1)

    log.info("Step6:恢复故障节点的两个业务网卡")
    reliable.network_test(fault_ip, io_eth_list[0], 'up')
    reliable.network_test(fault_ip, io_eth_list[1], 'up')
    time.sleep(100)
    log.info("Step5:等待自动均衡完成后,查看此时各均衡情况")
    while osan.check_vip_state() != 0:
        log.info("等待自动均衡完成中.")
        time.sleep(1)
    log.info("均衡后集群vip的分布情况:")
    osan.get_vips_layout()
    vips = [len(osan.get_vips_by_node(x, 1)) for x in deploy_ips]
    if len(set(vips)) == 1 and sum(vips) == len(deploy_ips) * 4:
        log.info("VIP自动均衡成功!每个节点VIP数量为4")
    else:
        log.error("异常!VIP自动均衡失败,数量分布情况:%s" % ','.join(map(str, vips)))
        os._exit(1)

    for node_ip in deploy_ips:
        node_id = node.get_node_id_by_ip(node_ip)
        io_eth_list = error.get_io_eth(node_id)
        eth_vips = [len(osan.get_vips_by_eth(node_ip, 1, x)) for x in io_eth_list]
        if len(set(eth_vips)) == 1 and sum(eth_vips) == 4:
            log.info("VIP在节点 %s 的业务网卡间均衡" % node_ip)
        else:
            log.error("异常!VIP在节点 %s 的业务网卡间未均衡,数量分布:%s" % (node_ip, eth_vips))
            os._exit(1)

def vdb_jn():
    mix_R_Align = com2.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                                   xfersize="(4k,80,16k,20)",
                                   seekpct=0,
                                   rdpct=0)
    log.info("Step4:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    com2.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jn", time=900)
    log.info("Step5:主机1上业务完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性.")
    com2.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")

def main():
    case()
    test_threads = []
    test_threads.append(threading.Thread(target=up_down))
    test_threads.append(threading.Thread(target=vdb_jn))
    for test_thread in test_threads:
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()
    for c_ip in client_ips:
        com2.vdb_check(c_ip=c_ip, time=100, oper="iops", output=deploy_ips[0])

if __name__ == '__main__':
    main()
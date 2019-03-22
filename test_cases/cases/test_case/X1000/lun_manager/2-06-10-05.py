#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-11-21
:Author: wuyq
:Description:
1、创建VIP地址池，配置4倍节点个数的VIP，IP切换均衡策略使用轮询，自动均衡策略设置为自动
2、查看自动均衡策略设置
3、下电一节点A，不恢复
4、等待2分钟，查看均衡是否启动
5、自动均衡完成后，查看3个节点的VIP均衡情况
6、步骤3中下电的节点A恢复
7、等待2分钟后，查看均衡是否启动，
8、自动均衡完成后，查看系统3个节点的VIP均衡情况

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

conf_file = common2.CONF_FILE   # 配置文件路径
osan = Lun_managerTest.oSan()
reliable = breakdown.Os_Reliable()
disk = breakdown.disk()
node = common.Node()

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

    time.sleep(30)
    fault_ip = random.choice(sever_ips)
    log.info("故障前集群vip的分布情况:")
    osan.get_vips_layout()
    log.info("Step3:故障一个业务节点,暂不恢复.节点:%s" % fault_ip)
    vm_id = error.down_node(fault_ip)

    time.sleep(100)
    while osan.check_vip_state() != 0:
        log.info("等待自动均衡完成中.")
        time.sleep(1)
    log.info("Step4:查看业务子网中节点VIP自动均衡情况")
    log.info("故障后集群vip的分布情况:")
    osan.get_vips_layout()
    sever_ips.remove(fault_ip)
    node_vips_list = [len(osan.get_vips_by_node(x, 1)) for x in sever_ips]
    if sum(node_vips_list) == len(deploy_ips) * 4:
        log.info("VIP迁移到了其他节点上")
    else:
        log.error("异常!VIP迁移失败,或VIP丢失")
        error.up_node(vm_id)
        os._exit(1)

    time.sleep(10)
    log.info("Step5:重新启动故障节点,等待故障节点重新启动,节点:%s" % fault_ip)
    error.up_node(vm_id)
    reliable.get_os_status_1(fault_ip)

    log.info("Step6:等待自动均衡完成后,业务子网节点的VIP分布情况")
    time.sleep(100)
    while osan.check_vip_state() != 0:
        log.info("等待自动均衡完成中.")
        time.sleep(1)
    log.info("均衡后集群vip的分布情况:")
    osan.get_vips_layout()
    node_vips_list = [len(osan.get_vips_by_node(x, 1)) for x in deploy_ips]
    if len(set(node_vips_list)) == 1 and sum(node_vips_list) == len(deploy_ips) * 4:
        log.info("业务子网中所有节点的VIP已均衡")
    else:
        log.error("异常!VIP迁移或均衡失败,分布情况:%s" % [osan.get_vips_by_node(x, 1) for x in deploy_ips])
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

if __name__ == '__main__':
    case()
# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-20
# @summary：
#   负载均衡策略修改带宽
# @steps:
#   1、创建3节点访问区az1，启动nas服务；
#   2、创建业务子网；
#   3、添加vip池，输入正确的vip地址、掩码等参数；
#   pscli --command=add_vip_address_pool --subnet_id=x --domain_name=xxxx.com --vip_addresses=x.x.x.11-20 --supported_protocol=NAS --allocation_method=STATIC
#   4、通过pscli --command=get_vip_address_pools查看与配置的信息是否匹配；
#   5、命令行通过IP addr观察VIP是否绑定到3个节点到对应的网卡上（相同网段的网卡）；
#   6、通过命令行修改vip地址池；
#   pscli --command=update_vip_address_pool --id=x --load_balance_policy=LB_THROUGHPUT
#   7、通过pscli --command=get_vip_address_pools查看与配置的信息是否匹配；
# @changelog：
#   None
######################################################

import os

import utils_path
import log
import common
import nas_common
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]     # 脚本名称


def executing_case():
    """测试执行
    :return:无
    """
    log.info('（2）executing_case')

    # for create_access_zone
    node_ids = nas_common.get_node_ids()
    access_zone_name = 'nas_16_0_3_63_access_zone_name'
    # for create_subnet
    subnet_name = 'nas_16_0_3_63_subnet_name'
    ip_family = nas_common.IPv4
    svip = nas_common.SUBNET_SVIP
    subnet_mask = nas_common.SUBNET_MASK
    subnet_gateway = nas_common.SUBNET_GATEWAY
    network_interfaces = nas_common.SUBNET_NETWORK_INTERFACES
    # for add_vip_address_pool
    domain_name = nas_common.VIP_DOMAIN_NAME
    vip_addresses = nas_common.VIP_ADDRESSES
    supported_protocol = nas_common.NAS
    allocation_method = nas_common.STATIC
    # for update_vip_address_pool
    load_balance_policy = nas_common.BALANCE_LB_THROUGHPUT

    """创建访问区"""
    msg = nas_common.create_access_zone(node_ids=node_ids,
                                        name=access_zone_name)
    if msg['detail_err_msg'] != '':
        raise Exception('%s Failed' % FILE_NAME)
    access_zone_id = msg['result']

    """使能访问区"""
    msg = nas_common.enable_nas(access_zone_id=access_zone_id)
    if msg['detail_err_msg'] != '':
        raise Exception('%s Failed' % FILE_NAME)

    """创建子网"""
    msg = nas_common.create_subnet(access_zone_id=access_zone_id,
                                   name=subnet_name,
                                   ip_family=ip_family,
                                   svip=svip,
                                   subnet_mask=subnet_mask,
                                   subnet_gateway=subnet_gateway,
                                   network_interfaces=network_interfaces)
    if msg['detail_err_msg'] != '':
        raise Exception('%s Failed' % FILE_NAME)
    subnet_id = msg['result']

    """创建vip地址池"""
    msg = nas_common.add_vip_address_pool(subnet_id=subnet_id,
                                          domain_name=domain_name,
                                          vip_addresses=vip_addresses,
                                          supported_protocol=supported_protocol,
                                          allocation_method=allocation_method)
    if msg['detail_err_msg'] != '':
        raise Exception('%s Failed' % FILE_NAME)
    vip_address_pool_id = msg['result']

    """查询vip地址池"""
    msg = nas_common.get_vip_address_pools(ids=vip_address_pool_id)
    if msg['detail_err_msg'] != '':
        raise Exception('%s Failed' % FILE_NAME)
    ip_address_pool = msg['result']['ip_address_pools'][0]
    if cmp(ip_address_pool, {
                "allocation_method": allocation_method,
                "domain_name": domain_name,
                "id": int(vip_address_pool_id),
                "ip_failover_policy": "IF_ROUND_ROBIN",
                "ipaddr_pool_state": "IPADDR_POOL_READY",
                "key": int(vip_address_pool_id),
                "load_balance_policy": "LB_ROUND_ROBIN",
                "rebalance_policy": "RB_DISABLED",
                "subnet_id": int(subnet_id),
                "supported_protocol": supported_protocol,
                "version": 1,
                "vip_addresses": [
                    vip_addresses
                ]
            }):
        raise Exception('%s Failed' % FILE_NAME)

    """网卡上确认vip分布正确性"""
    ip_dict, xml_ip_list, eth_ip_list = nas_common.get_vip_from_eth()
    rc = nas_common.judge_vip_layinfo(ip_dict, xml_ip_list, eth_ip_list)
    common.judge_rc(rc, 0, 'judge_vip_layinfo failed')

    """修改vip地址池"""
    msg = nas_common.update_vip_address_pool(vip_address_pool_id=vip_address_pool_id,
                                             load_balance_policy=load_balance_policy)
    if msg['detail_err_msg'] != '':
        raise Exception('%s Failed' % FILE_NAME)

    """检查修改是否成功"""
    """（1）get_vip_address_pools"""
    msg = nas_common.get_vip_address_pools(ids=vip_address_pool_id)
    if msg['detail_err_msg'] != '':
        raise Exception('%s Failed' % FILE_NAME)
    ip_address_pool = msg['result']['ip_address_pools'][0]
    if cmp(ip_address_pool, {
                "allocation_method": allocation_method,
                "domain_name": domain_name,
                "id": int(vip_address_pool_id),
                "ip_failover_policy": "IF_ROUND_ROBIN",
                "ipaddr_pool_state": "IPADDR_POOL_READY",
                "key": int(vip_address_pool_id),
                "load_balance_policy": load_balance_policy,
                "rebalance_policy": "RB_DISABLED",
                "subnet_id": int(subnet_id),
                "supported_protocol": supported_protocol,
                "version": ip_address_pool['version'],
                "vip_addresses": [
                    vip_addresses
                ]
            }):
        raise Exception('%s Failed' % FILE_NAME)

    """（2）网卡上确认vip分布正确性"""
    ip_dict, xml_ip_list, eth_ip_list = nas_common.get_vip_from_eth()
    rc = nas_common.judge_vip_layinfo(ip_dict, xml_ip_list, eth_ip_list)
    common.judge_rc(rc, 0, 'judge_vip_layinfo failed')

    return


def nas_main():
    """脚本入口函数
    :return:无
    """
    prepare_clean.nas_test_prepare(FILE_NAME)
    executing_case()
    if nas_common.DEBUG != 'on':
        prepare_clean.nas_test_clean()
    return


if __name__ == '__main__':
    common.case_main(nas_main)

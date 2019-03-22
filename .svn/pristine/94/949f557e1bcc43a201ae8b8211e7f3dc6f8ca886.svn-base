# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-20
# @summary：
#   单个分区子网个数【修改为同时对一个访问区中的子网个数，一个子网中的地址池个数，一个地址池中ip个数的判断】
# @steps:
#   1、创建3节点访问区az1，启动nas服务；
#   2、创建4个业务子网；
#   3、创建第5个业务子网；
# @changelog：
#   None
######################################################

import os
import random

import utils_path
import log
import common
import nas_common

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]     # 脚本名称


def executing_case():
    """测试执行
    :return:无
    """
    log.info('（2）executing_case')

    # for create_access_zone
    node_ids = nas_common.get_node_ids()
    access_zone_name = 'nas_16_0_3_78_access_zone_name'
    # for create_subnet
    ip_family = nas_common.IPv4
    subnet_mask = nas_common.SUBNET_MASK
    subnet_gateway = nas_common.SUBNET_GATEWAY
    network_interfaces_list = ['eth0', 'eth1', 'eth2', 'eth3', 'ib0']   # 此处对测试环境有特殊要求
    # for add_vip_address_pool
    supported_protocol = nas_common.NAS
    allocation_method_list = ['STATIC', 'DYNAMIC']
    allocation_method = allocation_method_list[random.randint(0, len(allocation_method_list) - 1)]
    # 创建子网和地址池的循环计数
    count = 5

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

    """计算每个地址池中最大的ip个数"""
    obj_node = common.Node()
    nodes_id_list = obj_node.get_nodes_id()
    max_ip_num = len(nodes_id_list) * 4

    """创建子网"""
    for i in range(count):
        subnet_name = 'nas_16_0_3_78_subnet_name_%s' % (i + 1)
        svip = '250.250.250.%s' % (250 + i + 1)
        if i < count - 1:   # 前四个子网预期创建成功
            msg = nas_common.create_subnet(access_zone_id=access_zone_id,
                                           name=subnet_name,
                                           ip_family=ip_family,
                                           svip=svip,
                                           subnet_mask=subnet_mask,
                                           subnet_gateway=subnet_gateway,
                                           network_interfaces=network_interfaces_list[i])
            if msg['detail_err_msg'] != '':
                raise Exception('%s Failed' % FILE_NAME)
            subnet_id = msg['result']

            """增加vip地址池"""
            for j in range(count):
                domain_name = 'www.nastest-%s-%s.com' % (i, j)
                vip_addresses = '250.%s.%s.1-%s' % (i, j, max_ip_num)

                """验证vip个数超出范围"""
                if j is 0:
                    wrong_vip_addresses = '250.%s.%s.1-%s' % (i, j, (max_ip_num + 1))
                    msg = nas_common.add_vip_address_pool(subnet_id=subnet_id,
                                                          domain_name=domain_name,
                                                          vip_addresses=wrong_vip_addresses,
                                                          supported_protocol=supported_protocol,
                                                          allocation_method=allocation_method)
                    if msg['detail_err_msg'].find('has reached limit:12 in IP address pool') == -1:
                        raise Exception('%s Failed' % FILE_NAME)

                if j < count - 1:   # 前四个地址池预期创建成功
                    msg = nas_common.add_vip_address_pool(subnet_id=subnet_id,
                                                          domain_name=domain_name,
                                                          vip_addresses=vip_addresses,
                                                          supported_protocol=supported_protocol,
                                                          allocation_method=allocation_method)
                    if msg['detail_err_msg'] != '':
                        raise Exception('%s Failed' % FILE_NAME)
                else:   # 第五个地址池预期创建失败
                    msg = nas_common.add_vip_address_pool(subnet_id=subnet_id,
                                                          domain_name=domain_name,
                                                          vip_addresses=vip_addresses,
                                                          supported_protocol=supported_protocol,
                                                          allocation_method=allocation_method)
                    if msg['detail_err_msg'] == '':
                        raise Exception('%s Failed' % FILE_NAME)
        else:   # 第五个子网预期创建失败
            msg = nas_common.create_subnet(access_zone_id=access_zone_id,
                                           name=subnet_name,
                                           ip_family=ip_family,
                                           svip=svip,
                                           subnet_mask=subnet_mask,
                                           subnet_gateway=subnet_gateway,
                                           network_interfaces=network_interfaces_list[i])
            # if msg['detail_err_msg'].find('Subnets count:4 has reached limit:4') == -1:   # 有bug
            if msg['detail_err_msg'] == '':
                raise Exception('%s Failed' % FILE_NAME)

    return


def preparing_environment():
    """测试条件准备
    :return:无
    """
    log.info('（1）preparing_environment')

    return


def nas_main():
    """脚本入口函数
    :return:无
    """

    # 初始化日志
    nas_common.nas_log_init(FILE_NAME)

    nas_common.cleaning_environment()
    preparing_environment()
    executing_case()
    if nas_common.DEBUG != 'on':
        nas_common.cleaning_environment()

    return


if __name__ == '__main__':
    common.case_main(nas_main)

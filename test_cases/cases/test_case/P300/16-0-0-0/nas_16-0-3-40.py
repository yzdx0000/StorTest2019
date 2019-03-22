# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import prepare_clean
import get_config
import nas_common

####################################################################################
#
# Author: liyao
# date 2018-08-21
# @summary：
#    无效IP配置测试
# @steps:
#   1、创建3节点访问分区az1，启动nas服务；
#   2、在az1上创建业务子网，配置正确的az1 ID、svip、掩码、网关，与接口信息；
#   3、添加vip池，输入非IP参数；
#   4、通过pscli --command=get_vip_address_pools查看与配置的信息是否匹配；
#   5、通过pscli --command=get_subnets命令查看业务子网信息；
#   6、disable nas, 删除vip_pool、删除子网、访问分区，清理环境
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)
DATA_DIR = os.path.join(NAS_TRUE_PATH, 'data_dir')                  # /mnt/volume1/nas_test_dir/nas_16_0_3_24/data_dir/
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


def case():
    '''函数执行主体'''
    '''1> 创建3节点访问分区az1，启动nas服务'''
    """创建AD认证"""
    log.info("\t[ 2.add_auth_provider_ad ]")
    ad_server_name = 'ad_server_' + FILE_NAME
    exe_info = nas_common.add_auth_provider_ad(ad_server_name, nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                                               nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                                               services_for_unix="NONE")
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('add auth provider ad %s failed !!!' % ad_server_name)
        raise Exception('add auth provider ad %s failed !!!' % ad_server_name)
    ad_server_id = exe_info['result']

    """get_auth_providers_ad"""
    log.info("\t[ 3.get_auth_provider_ad ]")
    exe_info = nas_common.get_auth_providers_ad(ad_server_id)
    ad_server = exe_info['result']['auth_providers'][0]
    if ad_server['name'] == ad_server_name and ad_server['domain_name'] == nas_common.AD_DOMAIN_NAME and \
            ad_server['id'] == ad_server_id and ad_server['name'] == ad_server_name:
        log.info('params of auth provider are correct !')
    else:
        log.error('params of auth provider are wrong !!!')
        raise Exception('params of auth provider are wrong !!!')

    """check_auth_provider"""
    nas_common.check_auth_provider(ad_server_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('check auth provider failed !!!')
        raise Exception('check auth provider failed !!!')

    """创建访问分区"""
    obj_node = common.Node()
    nodes_id_list = obj_node.get_nodes_id()
    nodes_id_str = ','.join(str(p) for p in nodes_id_list)
    access_zone_name = 'az_' + FILE_NAME
    exe_info = nas_common.create_access_zone(nodes_id_str, access_zone_name, ad_server_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create access zone %s failed !!!' % access_zone_name)
        raise Exception('create access zone %s failed !!!' % access_zone_name)
    access_zone_id = exe_info['result']

    """启动nas服务"""
    exe_info = nas_common.enable_nas(access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('enable nas failed !!!')
        raise Exception('enable nas failed !!!')

    '''2> 在az1上创建业务子网，配置正确的az1 ID、svip、掩码、网关，与接口信息'''
    subnet_name = 'subnet_' + FILE_NAME
    ip_family = 'IPv4'
    exe_info = nas_common.create_subnet(access_zone_id=access_zone_id, name=subnet_name, ip_family=ip_family,
                                        svip=nas_common.SUBNET_SVIP, subnet_mask=nas_common.SUBNET_MASK,
                                        subnet_gateway=nas_common.SUBNET_GATEWAY,
                                        network_interfaces=nas_common.SUBNET_NETWORK_INTERFACES)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create subnet %s failed !!!' % subnet_name)
        raise Exception('create subnet %s failed !!!' % subnet_name)
    subnet_id = exe_info['result']

    """通过pscli --command=get_subnets命令查看业务子网信息"""
    exe_info = nas_common.get_subnets(subnet_id)
    subnet = exe_info['result']['subnets'][0]
    if subnet['id'] == subnet_id and subnet['name'] == subnet_name and subnet['svip'] == nas_common.SUBNET_SVIP and \
            subnet['subnet_mask'] == int(nas_common.SUBNET_MASK) and subnet['subnet_gateway'] == nas_common.SUBNET_GATEWAY \
            and subnet['network_interfaces'][0] == nas_common.SUBNET_NETWORK_INTERFACES:
        log.info('subnet params are correct !')
    else:
        log.error('subnet params are wrong !!! ')
        raise Exception('subnet params are wrong !!!')

    log.info('waiting for 10s')
    time.sleep(10)

    '''3> 添加vip池，输入非IP参数'''
    allocation_method_list = ['STATIC', 'DYNAMIC']
    used_protocol = 'NAS'
    used_method = random.choice(allocation_method_list)
    vip_address_split = nas_common.VIP_ADDRESSES.split('.')
    part_count = random.randint(1, 3)   # 从被'.'分割的内容中选取部分组合成新的字符串，作为非法ip
    illegal_vip_address = '.'
    for i in range(part_count + 1):
        illegal_vip_address = illegal_vip_address + '.' + vip_address_split[i]

    nas_common.add_vip_address_pool(subnet_id=subnet_id,
                                    domain_name=nas_common.VIP_DOMAIN_NAME,
                                    vip_addresses=illegal_vip_address,
                                    supported_protocol=used_protocol,
                                    allocation_method=used_method,
                                    rebalance_policy='RB_AUTOMATIC')
    # cmd = 'pscli --command=add_vip_address_pool --subnet_id=%s --domain_name=%s --vip_addresses=%s ' \
    #       '--supported_protocol=%s --allocation_method=%s --rebalance_policy=%s' % (subnet_id,
    #        nas_common.VIP_DOMAIN_NAME, illegal_vip_address, used_protocol, used_method, 'RB_AUTOMATIC')
    # rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    # common.judge_rc_unequal(rc, 0, 'domain name length limitation did not work well !!!')

    '''4> 通过pscli --command=get_vip_address_pools查看与配置的信息是否匹配'''
    exe_info = nas_common.get_vip_address_pools()
    vip_pool_info = exe_info['result']['total']
    if vip_pool_info != 0:
        common.except_exit('vip address pool information is wrong !!!')

    '''5> 通过pscli --command=get_subnets命令查看业务子网信息'''
    exe_info = nas_common.get_subnets(subnet_id)
    subnet = exe_info['result']['subnets'][0]
    if subnet['name'] != subnet_name:
        log.error('subnet information is wrong !!!')
        raise Exception('subnet information is wrong !!!')

    '''6> disable nas, 删除vip_pool、子网、访问分区，清理环境'''
    """disable nas 服务"""
    exe_info = nas_common.disable_nas(access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('disable nas failed !!!')
        raise Exception('disable nas failed !!!')

    """删除业务子网"""
    exe_info = nas_common.delete_subnet(subnet_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('delete subnet failed !!!')

    """删除访问分区"""
    exe_info = nas_common.delete_access_zone(access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('delete access zone failed !!!')

    """删除AD认证服务器"""
    exe_info = nas_common.delete_auth_providers(ad_server_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('delete ad provider failed !!!')

    return


def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    prepare_clean.nas_test_clean()
    # nas_common.cleaning_environment()
    case()
    prepare_clean.nas_test_clean()
    log.info('%s succeed!' % FILE_NAME)

    return


if __name__ == '__main__':
    nas_main()
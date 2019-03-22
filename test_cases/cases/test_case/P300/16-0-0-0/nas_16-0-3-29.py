# -*-coding:utf-8 -*

import os
import time

import utils_path
import log
import common
import get_config
import nas_common
import make_fault
import prepare_clean


####################################################################################
#
# Author: liyao
# date 2018-08-20
# @summary：
#    绑定网卡ifdown，SVIP漂移
# @steps:
#   1、创建3节点访问分区az1，启动nas服务；
#   2、在az1上创建业务子网，配置正确的az1 ID、svip、掩码、网关，与接口信息；
#   3、通过pscli --command=get_subnets命令查看业务子网信息；
#   4、通过命令行ip addr观察SVIP绑定到哪个节点ethx上；
#   5、通过ifconfig down方式故障SVIP绑定节点的ethx网卡，观察SVIP状态；
#   6、通过命令行ip addr观察SVIP是否到其他节点的ethx上；
#   7、删除子网、访问分区，清理环境
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)
DATA_DIR = os.path.join(NAS_TRUE_PATH, 'data_dir')                  # /mnt/volume1/nas_test_dir/nas_16_0_3_24/data_dir/
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


def check_eth_svip(svip_judge, eth_judge, stdout, node_ip):
    split_line_list = stdout.splitlines()
    for line in split_line_list:
        if svip_judge in line:
            for mem in eth_judge:
                if mem in line:
                    log.info('svip is on %s' % node_ip)
                    return True, mem, node_ip   # 寻找并记录svip飘到的网卡及节点
                else:
                    common.except_exit("svip in %s, not in %s" % (line.split()[-1], eth_judge))
    return False, -1, -2


def case():
    '''函数执行主体'''
    '''1> 创建3节点访问分区az1，不启动nas服务'''
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

    '''3> 通过pscli --command=get_subnets命令查看业务子网信息'''
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

    '''4> 通过命令行ip addr观察SVIP绑定到哪个节点ethx上'''
    obj_node = common.Node()
    node_ip_list = obj_node.get_nodes_ip()
    svip_judge = nas_common.SUBNET_SVIP + '/' + nas_common.SUBNET_MASK
    eth_judge_str = nas_common.SUBNET_NETWORK_INTERFACES
    eth_judge_lst = eth_judge_str.split(',')
    for node_ip in node_ip_list:
        cmd = 'ip addr'
        rc, stdout = common.run_command(node_ip, cmd)
        rc, svip_eth_1, first_node_ip = check_eth_svip(svip_judge, eth_judge_lst, stdout, node_ip)
        if rc:
            break
    else:
        common.except_exit('svip is not on any system node !!!')

    '''5> 通过ifconfig down方式故障SVIP绑定节点的ethx网卡，观察SVIP状态'''
    """故障网卡并查看svip是否正确飘到其他节点"""
    node_connect_list = []   # 存放未被断网卡的节点ip
    for mem in node_ip_list:
        if mem != first_node_ip:
            node_connect_list.append(mem)

    rc = make_fault.down_eth(first_node_ip, svip_eth_1)
    common.judge_rc(rc, 0, 'ifconfig down %s executed failed !!!' % svip_eth_1)
    log.info('waiting for 30s')
    time.sleep(30)

    for node_ip in node_connect_list:
        cmd = 'ip addr'
        rc, stdout = common.run_command(node_ip, cmd)
        rc, svip_eth_2, second_node_ip = check_eth_svip(svip_judge, eth_judge_lst, stdout, node_ip)
        if rc:
            break
    else:
        common.except_exit('svip is not on any connected system node !!!')

    """ifconfig up恢复网卡"""
    rc = make_fault.up_eth(first_node_ip, svip_eth_1)
    common.judge_rc(rc, 0, 'ifconfig up %s failed !!!' % svip_eth_1)

    '''6> 通过pscli --command=get_subnets命令查看业务子网信息'''
    exe_info = nas_common.get_subnets(subnet_id)
    subnet = exe_info['result']['subnets'][0]
    if subnet['name'] != subnet_name:
        log.error('subnet information is wrong !!!')
        raise Exception('subnet information is wrong !!!')

    '''7> 清理环境'''
    """disable nas 服务"""
    exe_info = nas_common.disable_nas(access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('disable nas failed !!!')
        raise Exception('disable nas failed !!!')

    """删除业务子网"""
    exe_info = nas_common.delete_subnet(subnet_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('delete subnet %s failed !!!' % subnet_name)
        raise Exception('delete subnet %s failed !!!' % subnet_name)

    """删除访问分区"""
    exe_info = nas_common.delete_access_zone(access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('delete access zone %s failed !!!' % access_zone_name)
        raise Exception('delete access zone %s failed !!!' % access_zone_name)

    """删除AD认证服务器"""
    exe_info = nas_common.delete_auth_providers(ad_server_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('delete auth provider %s failed !!!' % ad_server_name)
        raise Exception('delete auth provider %s failed !!!' % ad_server_name)

    return


def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    # nas_common.cleaning_environment()
    case()
    prepare_clean.nas_test_clean()
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    nas_main()
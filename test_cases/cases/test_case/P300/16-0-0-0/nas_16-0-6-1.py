# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-08-02
# @summary：
# 16_0_6_1     分区策略正确性查看
# @steps:
# case1、配置IP故障转移策略；
# pscli --command=add_vip_address_pool --subnet_id=x --domain_name=www.domain.com --vip_addresses=x.x.x.1-x
# --supported_protocol=NAS --allocation_method=DYNAMIC --load_balance_policy=LB_ROUND_ROBIN
# --ip_failover_policy=IF_ROUND_ROBIN
# 2、查询IP故障转移策略是否满足预期；
# pscli --command=get_vip_address_pools

# @changelog：
#
#######################################################
import os
import time
import random
import commands
import utils_path
import common
import nas_common
import log
import shell
import get_config
import json
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_6_1
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：通过启动nas服务来启动本地认证服务器服务；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：通过启动nas服务来启动本地认证服务器服务；
# @return：
#       check_result —— 无
# @steps:
# 1> 创建访问分区
# 2> 获取访问分区信息
# 3> 创建子网
# 4> 获取子网信息
# 5> 创建VIP地址池
# 6> 获取vip地址池信息
# 7> 启动NAS
# 8> 查看NAS是否按配置启动
# 9> 关闭NAS
#######################################################
def executing_case1():
    # 若访问分区已经创建好，该步骤需要注释掉

    # 1> 创建访问分区
    log.info("\t[case1-1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_6_1"
    cmd = 'pscli --command=get_nodes'
    rc, stdout, stderr = shell.ssh(node_ip, cmd)
    outtext = common.json_loads(stdout)
    nodes = outtext['result']['nodes']
    ids = []
    for node in nodes:
        ids.append(node['data_disks'][0]['nodeId'])
    print ids
    access_zone_node_id_16_0_6_1 = ','.join(str(p) for p in ids)
    cmd = "ssh %s pscli --command=create_access_zone --node_ids=%s " \
          "--name=%s" % (node_ip, access_zone_node_id_16_0_6_1, access_zone_name)
    check_result1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_6_1, name=access_zone_name)
    log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s create_access_zone failed!!!' % node_ip)
    access_zone_id_16_0_6_1 = msg1["result"]

    # 2>获取访问分区信息
    log.info("\t[case1-2 get_access_zones ]")
    cmd = "ssh %s pscli --command=get_access_zones --ids=%s" % (node_ip, access_zone_id_16_0_6_1)
    check_result1 = nas_common.get_access_zones(ids=access_zone_id_16_0_6_1)
    log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s get_access_zones failed!!!' % node_ip)
    name = msg1["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        raise Exception('%s get_access_zones failed!!!' % node_ip)

    # 3> 创建子网
    log.info("\t[case1-3 create_subnet ]")
    sub_name = "subnet_16_0_6_1"
    # cmd = 'S=`ip addr | grep " 10.2.*"` && F=`echo ${S#*global }` && echo $F'
    # rc, stdout, stderr = shell.ssh(node_ip, cmd)
    # stdout = common.json_loads(stdout)
    # sub_network_interfaces = stdout[0:4]
    sub_network_interfaces = nas_common.SUBNET_NETWORK_INTERFACES
    print sub_network_interfaces
    sub_svip = nas_common.SUBNET_SVIP
    sub_subnet_mask = nas_common.SUBNET_MASK
    sub_subnet_gateway = nas_common.SUBNET_GATEWAY
    sub_mtu = nas_common.SUBNET_MTU
    cmd = "ssh %s pscli --command=create_subnet --access_zone_id=%s --name=%s --ip_family=%s" \
          "--svip=%s --subnet_mask=%s --subnet_gateway=%s " \
          "--network_interfaces=%s --mtu=%s" % (node_ip, access_zone_id_16_0_6_1, sub_name, nas_common.IPv4,
                                                sub_svip, sub_subnet_mask, sub_subnet_gateway,
                                                sub_network_interfaces, sub_mtu)
    check_result1 = nas_common.create_subnet(access_zone_id=access_zone_id_16_0_6_1,
                                             name=sub_name,
                                             ip_family=nas_common.IPv4,
                                             svip=sub_svip,
                                             subnet_mask=sub_subnet_mask,
                                             subnet_gateway=sub_subnet_gateway,
                                             network_interfaces=sub_network_interfaces,
                                             mtu=sub_mtu)
    log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s create_subnet failed!!!' % node_ip)
    subnet_id_16_0_6_1 = msg1["result"]

    # 4> 获取子网信息
    log.info("\t[case1-4 get_subnets ]")
    cmd = "ssh %s pscli --command=get_subnets --ids=%s" % (node_ip, subnet_id_16_0_6_1)
    check_result1 = nas_common.get_subnets(ids=subnet_id_16_0_6_1)
    log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s get_subnets failed!!!' % node_ip)
    access_zone_id = msg1["result"]["subnets"][0]["access_zone_id"]
    if access_zone_id != access_zone_id_16_0_6_1:
        raise Exception('%s access_zone_id failed %s != %s !!!' % (node_ip, access_zone_id, access_zone_id_16_0_6_1))
    id = msg1["result"]["subnets"][0]["id"]
    if id != subnet_id_16_0_6_1:
        raise Exception('%s id failed %s != %s !!!' % (node_ip, id, subnet_id_16_0_6_1))
    mtu = msg1["result"]["subnets"][0]["mtu"]
    if mtu != int(sub_mtu):
        raise Exception('%s mtu failed %s != %s !!!' % (node_ip, mtu, sub_mtu))
    name = msg1["result"]["subnets"][0]["name"]
    if name != sub_name:
        raise Exception('%s name failed %s != %s !!!' % (node_ip, name, sub_name))
    network_interfaces = msg1["result"]["subnets"][0]["network_interfaces"][0]
    if network_interfaces != sub_network_interfaces:
        raise Exception(
            '%s network_interfaces failed %s != %s !!!' % (node_ip, network_interfaces, sub_network_interfaces))
    subnet_gateway = msg1["result"]["subnets"][0]["subnet_gateway"]
    if subnet_gateway != sub_subnet_gateway:
        raise Exception('%s subnet_gateway failed %s != %s !!!' % (node_ip, subnet_gateway, sub_subnet_gateway))
    subnet_mask = msg1["result"]["subnets"][0]["subnet_mask"]
    if subnet_mask != int(sub_subnet_mask):
        raise Exception('%s subnet_mask failed %s != %s !!!' % (node_ip, subnet_mask, sub_subnet_mask))
    subnet_state = msg1["result"]["subnets"][0]["subnet_state"]
    if subnet_state != "SUBNET_READY":
        raise Exception('%s subnet_state failed %s != SUBNET_READY !!!' % (node_ip, subnet_state))
    svip = msg1["result"]["subnets"][0]["svip"]
    if svip != sub_svip:
        raise Exception('%s svip failed %s != %s !!!' % (node_ip, svip, sub_svip))

    # 5>创建vip地址池
    log.info("\t[case1-5 add_vip_address_pool ]")
    vip_domain_name = nas_common.VIP_DOMAIN_NAME
    vip_vip_addresses = nas_common.VIP_ADDRESSES
    vip_supported_protocol = "NAS"
    vip_allocation_method = "DYNAMIC"
    vip_load_balance_policy = "LB_ROUND_ROBIN"
    vip_ip_failover_policy = "IF_ROUND_ROBIN"
    cmd = "ssh %s pscli --command=add_vip_address_pool --subnet_id=%s --domain_name=%s " \
          "--vip_addresses=%s --supported_protocol=%s --allocation_method=%s " \
          "--load_balance_policy=%s --ip_failover_policy=%s" \
          % (node_ip, subnet_id_16_0_6_1, vip_domain_name, vip_vip_addresses,
             vip_supported_protocol, vip_allocation_method, vip_load_balance_policy, vip_ip_failover_policy)
    check_result1 = nas_common.add_vip_address_pool(subnet_id=subnet_id_16_0_6_1,
                                                    domain_name=vip_domain_name,
                                                    vip_addresses=vip_vip_addresses,
                                                    supported_protocol=vip_supported_protocol,
                                                    allocation_method=vip_allocation_method,
                                                    load_balance_policy=vip_load_balance_policy,
                                                    ip_failover_policy=vip_ip_failover_policy)
    log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s add_vip_address_pool failed!!!' % node_ip)
    vip_address_pool_id_16_0_6_1 = msg1["result"]

    # 6>获取vip地址池信息
    log.info("\t[case1-6 get_vip_address_pools ]")
    cmd = "ssh %s pscli --command=get_vip_address_pools --ids=%s" % (node_ip, vip_address_pool_id_16_0_6_1)
    check_result1 = nas_common.get_vip_address_pools(ids=vip_address_pool_id_16_0_6_1)
    log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s get_vip_address_pools!!!' % node_ip)
    allocation_method = msg1["result"]["ip_address_pools"][0]["allocation_method"]
    if allocation_method != vip_allocation_method:
        raise Exception(
            '%s allocation_method failed %s != %s !!!' % (node_ip, allocation_method, vip_allocation_method))
    domain_name = msg1["result"]["ip_address_pools"][0]["domain_name"]
    if domain_name != vip_domain_name:
        raise Exception('%s domain_name failed %s != %s !!!' % (node_ip, domain_name, vip_domain_name))
    id = msg1["result"]["ip_address_pools"][0]["id"]
    if id != vip_address_pool_id_16_0_6_1:
        raise Exception('%s id failed %s != %s !!!' % (node_ip, id, vip_address_pool_id_16_0_6_1))
    ip_failover_policy = msg1["result"]["ip_address_pools"][0]["ip_failover_policy"]
    if ip_failover_policy != vip_ip_failover_policy:
        raise Exception(
            '%s ip_failover_policy failed %s != %s !!!' % (node_ip, ip_failover_policy, vip_ip_failover_policy))
    ipaddr_pool_state = msg1["result"]["ip_address_pools"][0]["ipaddr_pool_state"]
    if ipaddr_pool_state != "IPADDR_POOL_READY":
        raise Exception('%s ipaddr_pool_state failed %s != "IPADDR_POOL_READY" !!!' % (node_ip, ipaddr_pool_state))
    load_balance_policy = msg1["result"]["ip_address_pools"][0]["load_balance_policy"]
    if load_balance_policy != vip_load_balance_policy:
        raise Exception(
            '%s load_balance_policy failed %s != %s !!!' % (node_ip, load_balance_policy, vip_load_balance_policy))
    subnet_id = msg1["result"]["ip_address_pools"][0]["subnet_id"]
    if subnet_id != subnet_id_16_0_6_1:
        raise Exception('%s subnet_id failed %s != %s !!!' % (node_ip, subnet_id, subnet_id_16_0_6_1))
    supported_protocol = msg1["result"]["ip_address_pools"][0]["supported_protocol"]
    if supported_protocol != vip_supported_protocol:
        raise Exception(
            '%s supported_protocol failed %s != %s !!!' % (node_ip, supported_protocol, vip_supported_protocol))
    vip_addresses = msg1["result"]["ip_address_pools"][0]["vip_addresses"][0]
    if vip_addresses != vip_vip_addresses:
        raise Exception('%s vip_addresses failed %s != %s !!!' % (node_ip, vip_addresses, vip_vip_addresses))

    # 7> 启动NAS
    log.info("\t[ case1-7 enable_nas ]")
    cmd = "pscli --command=enable_nas --access_zone_id=%s" % access_zone_id_16_0_6_1
    check_result2 = nas_common.enable_nas(access_zone_id=access_zone_id_16_0_6_1)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    wait_time1 = random.randint(10, 15)
    time.sleep(wait_time1)
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s enable_nas failed!!!' % node_ip)

    # 8> 查看NAS是否按配置启动
    log.info("\t[ case1-8 get_access_zones ]")
    cmd = "ssh %s pscli --command=get_access_zones --ids=%s" % (node_ip, access_zone_id_16_0_6_1)
    check_result1 = nas_common.get_access_zones(ids=access_zone_id_16_0_6_1)
    log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s get_access_zones failed!!!' % node_ip)
    name = msg1["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        raise Exception('%s get_access_zones failed!!!' % node_ip)

    # 9> 关闭NAS
    log.info("\t[ case1-9 disable_nas ]")
    cmd = "pscli --command=disable_nas --access_zone_id=%s" % access_zone_id_16_0_6_1
    check_result2 = nas_common.disable_nas(access_zone_id=access_zone_id_16_0_6_1)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    wait_time1 = random.randint(10, 15)
    time.sleep(wait_time1)
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s disble_nas failed!!!' % node_ip)
    return


#######################################################
# @function：清理环境
# @parameter：
# @return：
# @steps:
#######################################################
def clearing_environment():
    log.info("（3）clearing_environment")
    """
    访问分区删除交付后添加删除访问分区、删除vip池、删除subbet
    """
    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    log.info("（1）preparing_environment")

    '''
    1、下发nas相关的配置
    2、创建nas测试相关的目录和文件
    '''

    return


#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    preparing_environment()
    log.info("（2）executing_case")
    executing_case1()
    prepare_clean.nas_test_clean()


    return


if __name__ == '__main__':
    common.case_main(nas_main)

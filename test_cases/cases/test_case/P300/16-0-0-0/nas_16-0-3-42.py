
# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-08-18
# @summary：
# 16_0_3_42     VIP的冲突检测
# @steps:
# 1、创建3节点访问区az1，启动nas服务；
# 2、创建业务子网；
# 3、添加vip池1；
# 4、通过pscli --command=get_vip_address_pools查看与配置的信息是否匹配；
# 5、添加vip池2，存在原有网卡上的IP与配置的VIP冲突；
# 6、添加vip池3，svip与配置的VIP冲突；
# 7、添加vip池4，原有集群其他网卡上的IP与配置的VIP冲突；
# 8、通过pscli --command=get_vip_address_pools查看与配置的信息是否匹配；
# 9、命令行通过IP addr观察VIP是否绑定到3个节点到对应的网卡上（相同网段的网卡）；

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
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_3_42
SYSTEM_IP = get_config.get_parastor_ip()


def executing_case1():
    """1、创建3节点访问区az1，启动nas服务；"""
    """创建访问分区"""
    log.info("\t[1-1 create_access_zone ]")
    node_ip = SYSTEM_IP
    access_zone_name = "access_zone_16_0_3_42"
    node = common.Node()
    ids = node.get_nodes_id()
    print ids
    access_zone_node_id_16_0_3_42 = ','.join(str(p) for p in ids)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_3_42, name=access_zone_name)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s create_access_zone failed!!!' % node_ip)
    access_zone_id_16_0_3_42 = msg1["result"]

    """获取访问分区信息"""
    log.info("\t[1-2 get_access_zones ]")
    msg1 = nas_common.get_access_zones(ids=access_zone_id_16_0_3_42)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s get_access_zones failed!!!' % node_ip)
    name = msg1["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        raise Exception('%s get_access_zones failed!!!' % node_ip)

    """启动NAS"""
    log.info("\t[ 1-3 enable_nas ]")
    msg2 = nas_common.enable_nas(access_zone_id=access_zone_id_16_0_3_42)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s enable_nas failed!!!' % node_ip)

    """2、创建业务子网"""
    log.info("\t[2 create_subnet ]")
    sub_name = "subnet_16_0_3_42"
    sub_network_interfaces = nas_common.SUBNET_NETWORK_INTERFACES
    sub_svip = nas_common.SUBNET_SVIP
    sub_subnet_mask = nas_common.SUBNET_MASK
    sub_subnet_gateway = nas_common.SUBNET_GATEWAY
    sub_mtu = nas_common.SUBNET_MTU
    sub_ip_family = nas_common.IPv4
    check_result1 = nas_common.create_subnet(access_zone_id=access_zone_id_16_0_3_42,
                                             name=sub_name,
                                             ip_family=sub_ip_family,
                                             svip=sub_svip,
                                             subnet_mask=sub_subnet_mask,
                                             subnet_gateway=sub_subnet_gateway,
                                             network_interfaces=sub_network_interfaces,
                                             mtu=sub_mtu)
    if check_result1["err_msg"] != "" or check_result1["detail_err_msg"] != "":
        common.except_exit('%s create_subnet failed!!!' % node_ip)
    subnet_id_16_0_3_42 = check_result1["result"]

    """获取子网信息"""
    log.info("\t[2 get_subnets ]")
    msg1 = nas_common.get_subnets(ids=subnet_id_16_0_3_42)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s get_subnets failed!!!' % node_ip)
    access_zone_id = msg1["result"]["subnets"][0]["access_zone_id"]
    if access_zone_id != access_zone_id_16_0_3_42:
        raise Exception('%s access_zone_id failed %s != %s !!!' % (node_ip, access_zone_id, access_zone_id_16_0_3_42))
    idd = msg1["result"]["subnets"][0]["id"]
    if idd != subnet_id_16_0_3_42:
        raise Exception('%s id failed %s != %s !!!' % (node_ip, idd, subnet_id_16_0_3_42))
    ip_family = msg1["result"]["subnets"][0]["ip_family"]
    if ip_family != sub_ip_family:
        raise Exception('%s ip_family failed %s != %s !!!' % (node_ip, ip_family, sub_ip_family))
    mtu = msg1["result"]["subnets"][0]["mtu"]
    if mtu != int(sub_mtu):
        raise Exception('%s mtu failed %s != %s !!!' % (node_ip, mtu, sub_mtu))
    name = msg1["result"]["subnets"][0]["name"]
    if name != sub_name:
        raise Exception('%s name failed %s != %s !!!' % (node_ip, name, sub_name))
    network_interfaces = msg1["result"]["subnets"][0]["network_interfaces"]
    for network_interface in network_interfaces:
        if network_interface not in sub_network_interfaces:
            raise Exception(
                '%s network_interfaces failed %s != %s !!!' % (node_ip, network_interface, sub_network_interfaces))
    subnet_gateway = msg1["result"]["subnets"][0]["subnet_gateway"]
    if subnet_gateway != sub_subnet_gateway:
        raise Exception('%s subnet_gateway failed %s != %s !!!' % (node_ip, subnet_gateway, sub_subnet_gateway))
    subnet_mask = msg1["result"]["subnets"][0]["subnet_mask"]
    if subnet_mask != int(sub_subnet_mask):
        raise Exception('%s subnet_mask failed %s != %s !!!' % (node_ip, subnet_mask, sub_subnet_mask))
    subnet_mask = msg1["result"]["subnets"][0]["subnet_mask"]
    if subnet_mask != int(sub_subnet_mask):
        raise Exception('%s subnet_mask failed %s != %s !!!' % (node_ip, subnet_mask, sub_subnet_mask))
    subnet_state = msg1["result"]["subnets"][0]["subnet_state"]
    if subnet_state != "SUBNET_READY":
        raise Exception('%s subnet_state failed %s != SUBNET_READY !!!' % (node_ip, subnet_state))
    svip = msg1["result"]["subnets"][0]["svip"]
    if svip != sub_svip:
        raise Exception('%s svip failed %s != %s !!!' % (node_ip, svip, sub_svip))

    '''通过命令行ip addr观察SVIP绑定到哪个节点ethx上'''
    log.info("\t[2 check_svip_in_eth ]")
    rc = nas_common.check_svip_in_eth(sub_svip, sub_subnet_mask, sub_network_interfaces)
    common.judge_rc(rc, 0, "svip没有落到集群内节点的网卡上")

    """3、添加vip池1"""
    log.info("\t[3 add_vip_address_pool ]")
    vip_domain_name = nas_common.VIP_DOMAIN_NAME
    vip_vip_addresses = nas_common.VIP_ADDRESSES
    vip_supported_protocol = "NAS"
    vip_allocation_method = "DYNAMIC"
    vip_load_balance_policy = "LB_ROUND_ROBIN"
    vip_ip_failover_policy = "IF_ROUND_ROBIN"
    msg1 = nas_common.add_vip_address_pool(subnet_id=subnet_id_16_0_3_42,
                                           domain_name=vip_domain_name,
                                           vip_addresses=vip_vip_addresses,
                                           supported_protocol=vip_supported_protocol,
                                           allocation_method=vip_allocation_method,
                                           load_balance_policy=vip_load_balance_policy,
                                           ip_failover_policy=vip_ip_failover_policy)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s add_vip_address_pool failed!!!' % node_ip)
    vip_address_pool_id_16_0_3_42 = msg1["result"]

    """4、通过pscli --command=get_vip_address_pools查看与配置的信息是否匹配"""
    log.info("\t[4 get_vip_address_pools ]")
    msg1 = nas_common.get_vip_address_pools(ids=vip_address_pool_id_16_0_3_42)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s get_vip_address_pools!!!' % node_ip)
    allocation_method = msg1["result"]["ip_address_pools"][0]["allocation_method"]
    if allocation_method != vip_allocation_method:
        raise Exception(
            '%s allocation_method failed %s != %s !!!' % (node_ip, allocation_method, vip_allocation_method))
    domain_name = msg1["result"]["ip_address_pools"][0]["domain_name"]
    if domain_name != vip_domain_name:
        raise Exception('%s domain_name failed %s != %s !!!' % (node_ip, domain_name, vip_domain_name))
    idd = msg1["result"]["ip_address_pools"][0]["id"]
    if idd != vip_address_pool_id_16_0_3_42:
        raise Exception('%s id failed %s != %s !!!' % (node_ip, idd, vip_address_pool_id_16_0_3_42))
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
    if subnet_id != subnet_id_16_0_3_42:
        raise Exception('%s subnet_id failed %s != %s !!!' % (node_ip, subnet_id, subnet_id_16_0_3_42))
    supported_protocol = msg1["result"]["ip_address_pools"][0]["supported_protocol"]
    if supported_protocol != vip_supported_protocol:
        raise Exception(
            '%s supported_protocol failed %s != %s !!!' % (node_ip, supported_protocol, vip_supported_protocol))
    vip_addresses = msg1["result"]["ip_address_pools"][0]["vip_addresses"][0]
    if vip_addresses != vip_vip_addresses:
        raise Exception('%s vip_addresses failed %s != %s !!!' % (node_ip, vip_addresses, vip_vip_addresses))

    """5、添加vip池2，存在原有网卡上的IP与配置的VIP冲突"""
    log.info("\t[5 add_vip_address_pool_2 ]")
    node = common.Node()
    result = node.get_nodes()
    data_ip_list = []
    data_ips = result['result']['nodes'][0]['data_ips']
    for data_ip in data_ips:
        ip = data_ip['ip_address']
        data_ip_list.append(ip)
    local_data_ip = ','.join(str(p) for p in data_ip_list)
    vip_2_domain_name = nas_common.VIP_2_DOMAIN_NAME
    vip_2_vip_addresses = local_data_ip
    vip_2_supported_protocol = "NAS"
    vip_2_allocation_method = "DYNAMIC"
    vip_2_load_balance_policy = "LB_ROUND_ROBIN"
    vip_2_ip_failover_policy = "IF_ROUND_ROBIN"
    msg1 = nas_common.add_vip_address_pool(subnet_id=subnet_id_16_0_3_42,
                                           domain_name=vip_2_domain_name,
                                           vip_addresses=vip_2_vip_addresses,
                                           supported_protocol=vip_2_supported_protocol,
                                           allocation_method=vip_2_allocation_method,
                                           load_balance_policy=vip_2_load_balance_policy,
                                           ip_failover_policy=vip_2_ip_failover_policy)
    if msg1["err_msg"] != "ILLEGAL_ARGUMENT" or \
                    msg1["detail_err_msg"].find("conflict with node data ip or control ip") == -1:
        common.except_exit('%s add_vip_address_pool_2 failed!!!' % node_ip)

    # sub_network_interfaces_list = sub_network_interfaces.split(',')
    # print sub_network_interfaces_list
    # for sub_network_interface in sub_network_interfaces_list:
    #     cmd = "ip addr | grep %s | grep -v mtu | grep -v secondary" % sub_network_interface
    #     rc, stdout = common.run_command(node_ip, cmd)
    #     local_eth_ip = stdout.split()[1].split("/")[0]
    #     vip_2_domain_name = nas_common.VIP_2_DOMAIN_NAME
    #     vip_2_vip_addresses = local_eth_ip
    #     vip_2_supported_protocol = "NAS"
    #     vip_2_allocation_method = "DYNAMIC"
    #     vip_2_load_balance_policy = "LB_ROUND_ROBIN"
    #     vip_2_ip_failover_policy = "IF_ROUND_ROBIN"
    #     msg1 = nas_common.add_vip_address_pool(subnet_id=subnet_id_16_0_3_42,
    #                                            domain_name=vip_2_domain_name,
    #                                            vip_addresses=vip_2_vip_addresses,
    #                                            supported_protocol=vip_2_supported_protocol,
    #                                            allocation_method=vip_2_allocation_method,
    #                                            load_balance_policy=vip_2_load_balance_policy,
    #                                            ip_failover_policy=vip_2_ip_failover_policy)
    #     if msg1["err_msg"] != "ILLEGAL_ARGUMENT" or \
    #        msg1["detail_err_msg"].find("conflict with node data ip or control ip") == -1:
    #         common.except_exit('%s add_vip_address_pool_2 failed!!!' % node_ip)

    """6、添加vip池3，IP地址与第一个VIP池相同"""
    log.info("\t[6 add_vip_address_pool_3 ]")
    vip_3_domain_name = nas_common.VIP_2_DOMAIN_NAME
    vip_3_vip_addresses = sub_svip
    vip_3_supported_protocol = "NAS"
    vip_3_allocation_method = "DYNAMIC"
    vip_3_load_balance_policy = "LB_ROUND_ROBIN"
    vip_3_ip_failover_policy = "IF_ROUND_ROBIN"
    msg1 = nas_common.add_vip_address_pool(subnet_id=subnet_id_16_0_3_42,
                                           domain_name=vip_3_domain_name,
                                           vip_addresses=vip_3_vip_addresses,
                                           supported_protocol=vip_3_supported_protocol,
                                           allocation_method=vip_3_allocation_method,
                                           load_balance_policy=vip_3_load_balance_policy,
                                           ip_failover_policy=vip_3_ip_failover_policy)
    if msg1["err_msg"] != "ILLEGAL_ARGUMENT" or \
       msg1["detail_err_msg"].find("has already been used by svip in subnet") == -1:
        common.except_exit('%s add_vip_address_pool_3 failed!!!' % node_ip)

    """7、添加vip池4，原有集群其他网卡上的IP与配置的VIP冲突"""
    log.info("\t[7 add_vip_address_pool_4 ]")
    vip_4_domain_name = nas_common.VIP_2_DOMAIN_NAME
    node = common.Node()
    vip_4_vip_addresses = "".join(random.sample(node.get_nodes_ip(), 1)).split("'")[0]
    vip_4_supported_protocol = "NAS"
    vip_4_allocation_method = "DYNAMIC"
    vip_4_load_balance_policy = "LB_ROUND_ROBIN"
    vip_4_ip_failover_policy = "IF_ROUND_ROBIN"
    msg1 = nas_common.add_vip_address_pool(subnet_id=subnet_id_16_0_3_42,
                                           domain_name=vip_4_domain_name,
                                           vip_addresses=vip_4_vip_addresses,
                                           supported_protocol=vip_4_supported_protocol,
                                           allocation_method=vip_4_allocation_method,
                                           load_balance_policy=vip_4_load_balance_policy,
                                           ip_failover_policy=vip_4_ip_failover_policy)
    if msg1["err_msg"] != "ILLEGAL_ARGUMENT" or \
       msg1["detail_err_msg"].find("conflict with node data ip or control ip") == -1:
        common.except_exit('%s add_vip_address_pool_4 failed!!!' % node_ip)

    """8、通过pscli - -command = get_vip_address_pools查看与配置的信息是否匹配"""
    log.info("\t[8 get_vip_address_pools_2-4 ]")
    msg1 = nas_common.get_vip_address_pools()
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s get_vip_address_pools!!!' % node_ip)
    ip_address_pools = msg1["result"]["ip_address_pools"]
    domain_name_list = []
    for ip_address_pool in ip_address_pools:
        domain_name_list.append(ip_address_pool["domain_name"])
    print domain_name_list
    if nas_common.VIP_2_DOMAIN_NAME in domain_name_list:
        common.except_exit('添加vip池2-4，IP地址有冲突，依然添加成功，与预期不符')
        raise Exception('%s domain_name failed %s != %s !!!' % (node_ip, domain_name, vip_domain_name))

    """9、命令行通过IP addr观察VIP是否绑定到3个节点到对应的网卡上（相同网段的网卡）"""
    log.info("\t[9 ip addr ]")
    ip_dict, xml_ip_list, eth_ip_list = nas_common.get_vip_from_eth(subnet_network_interfaces=sub_network_interfaces,
                                                                    vip_addresses=vip_vip_addresses,
                                                                    subnet_mask=sub_subnet_mask)
    rc = nas_common.judge_vip_layinfo(ip_dict, xml_ip_list, eth_ip_list)
    common.judge_rc(rc, 0, "通过IP addr观察VIP绑定情况有误")

    """关闭NAS"""
    log.info("\t[ disable_nas ]")
    cmd = "disable_nas "
    check_result2 = nas_common.disable_nas(access_zone_id=access_zone_id_16_0_3_42)
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
    prepare_clean.nas_test_clean()
    preparing_environment()
    log.info("（2）executing_case")
    executing_case1()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)

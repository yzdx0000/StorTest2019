# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-06-12
# @summary：
# 16-0-1-28          中文用户、用户组测试
# @steps:
# case1、连上含有带中文用户名和用户组名的AD认证服务器；2、查看用户名和用户组名是否显示正确
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
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume/nas/nas_16_0_1_28
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：3节点集群，使用ad认证服务器；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：3节点集群，使用ad认证服务器；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#  1> add_auth_provider_ad
#  2> get_auth_providers_ad
#  3> check_auth_provider
#  4> create_access_zone
#  5> get_access_zones
#  6> enable_nas
#  7> 查看NAS服务状态
#  8> get_auth_users
#  9> get_auth_groups

#######################################################
def executing_case1():

    '''1> add_auth_provider_ad '''
    log.info("\t[case1-1 set_ntp ]")
    nas_common.set_ntp(is_enabled='true', ntp_servers=nas_common.AD_DNS_ADDRESSES)

    log.info("\t[case1 add_auth_provider_ad ]")
    global ad_name
    ad_name = "nas_16_0_1_28_ad"

    cmd = "add_auth_provider_ad "
    check_result2 = nas_common.add_auth_provider_ad(name=ad_name,
                                                    domain_name=nas_common.AD_DOMAIN_NAME,
                                                    dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                                    username=nas_common.AD_USER_NAME,
                                                    password=nas_common.AD_PASSWORD,
                                                    services_for_unix="NONE",
                                                    unix_id_range="%s-%s" % (1000, 210000),
                                                    other_unix_id_range="%s-%s" % (210001, 210002))
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s add_auth_provider_ad failed!!!' % (node_ip))
    global ad_id_16_0_1_28
    ad_id_16_0_1_28 = msg2["result"]

    '''2> get_auth_providers_ad'''
    log.info("\t[case1-2 get_auth_provider_ad ]")
    cmd = "get_auth_providers_ad"
    check_result2 = nas_common.get_auth_providers_ad(ids=ad_id_16_0_1_28)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_providers_ad failed!!!' % node_ip)
    dns_addresses = msg2["result"]["auth_providers"][0]["dns_addresses"][0]
    domain_name = msg2["result"]["auth_providers"][0]["domain_name"]
    id = msg2["result"]["auth_providers"][0]["id"]
    key = msg2["result"]["auth_providers"][0]["key"]
    name = msg2["result"]["auth_providers"][0]["name"]
    services_for_unix = msg2["result"]["auth_providers"][0]["services_for_unix"]
    type = msg2["result"]["auth_providers"][0]["type"]
    unix_id_range = msg2["result"]["auth_providers"][0]["unix_id_range"]
    username = msg2["result"]["auth_providers"][0]["username"]
    if dns_addresses != "10.2.41.251":
        raise Exception('%s dns_addresses error!!!' % node_ip)
    if domain_name != "adtest.com":
        raise Exception('%s domain_name error!!!' % node_ip)
    if id != ad_id_16_0_1_28:
        raise Exception('%s id error!!!' % node_ip)
    if key != ad_id_16_0_1_28:
        raise Exception('%s key error!!!' % node_ip)
    if name != ad_name:
        raise Exception('%s name error!!!' % node_ip)
    if services_for_unix != "NONE":
        raise Exception('%s services_for_unix error!!!' % node_ip)
    if type != "AD":
        raise Exception('%s type error!!!' % node_ip)
    if unix_id_range != [
                1000,
                210000
    ]:
        raise Exception('%s unix_id_range error!!!' % node_ip)
    if username != "administrator":
        raise Exception('%s username error!!!' % node_ip)

    '''3> check_auth_provider'''
    log.info("\t[case1-3 check_auth_provider AD ]")
    cmd = "check_auth_provider "
    check_result2 = nas_common.check_auth_provider(provider_id=ad_id_16_0_1_28)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s check_auth_provider ad failed!!!' % (node_ip))

    '''4> create_access_zone'''
    log.info("\t[case1-4 create_access_zone ]")
    global access_zone_name
    access_zone_name = "access_zone_16_0_1_28"
    node = common.Node()
    ids_list = node.get_nodes_id()
    global ids_list
    global access_zone_node_id_16_0_1_28
    access_zone_node_id_16_0_1_28 = ','.join(str(p) for p in ids_list)
    global m
    m = len(ids_list)
    cmd = "create_access_zone"
    check_result2 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_1_28,
                                                  name=access_zone_name,
                                                  auth_provider_id=ad_id_16_0_1_28)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_access_zone failed!!!' % (node_ip))
    global access_zone_id_16_0_1_28
    access_zone_id_16_0_1_28 = msg2["result"]

    '''5> get_access_zones'''
    log.info("\t[case1-5 get_access_zones ]")
    cmd = "get_access_zones"
    check_result2 = nas_common.get_access_zones(ids=access_zone_id_16_0_1_28)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_access_zone failed!!!' % (node_ip))
    auth_provider_id = msg2["result"]["access_zones"][0]["auth_provider"]["id"]
    auth_provider_name = msg2["result"]["access_zones"][0]["auth_provider"]["name"]
    auth_provider_type = msg2["result"]["access_zones"][0]["auth_provider"]["type"]
    access_zones_id = msg2["result"]["access_zones"][0]["id"]
    access_zones_name_1 = msg2["result"]["access_zones"][0]["name"]
    if auth_provider_id != ad_id_16_0_1_28:
        raise Exception('%s auth_provider_id %s != %s error!!!' % (node_ip, auth_provider_id, ad_id_16_0_1_28))
    if auth_provider_name != ad_name:
        raise Exception('%s auth_provider_name %s != %s error!!!' % (node_ip, auth_provider_name, ad_name))
    if auth_provider_type != type:
        raise Exception('%s auth_provider_type %s != %s error!!!' % (node_ip, auth_provider_type, type))
    if access_zones_id != access_zone_id_16_0_1_28:
        raise Exception('%s access_zones_id %s != %s error!!!' % (node_ip, access_zones_id, access_zone_id_16_0_1_28))
    if access_zones_name_1 != access_zone_name:
        raise Exception('%s access_zones_name %s != %s error!!!' % (node_ip, access_zones_name_1, access_zone_name))

    '''6> enable_nas'''
    log.info("\t[case1-6enable_nas ]")
    cmd = "enable_nas "
    check_result2 = nas_common.enable_nas(access_zone_id=access_zone_id_16_0_1_28)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s enable_nass failed!!!' % (node_ip))

    '''7> 查看NAS服务状态'''
    for j in range(0, m):
        k = ids_list[j]
        log.info("\t[ case1-7 查看NAS服务状态 node=%s]" % (k))
        node = common.Node()
        msg4 = node.get_nodes(ids=k)
        status = msg4["result"]["nodes"][0]["reported_info"]["nas_protocol"]["server_status"][
            "auth_provider_server_status"]
        print status
        if (msg4["result"]["nodes"][0]["reported_info"]["nas_protocol"]
        ["server_status"]["auth_provider_server_status"] != "SERV_STATE_OK"):
            raise Exception('ip=%s, node_id=%s auth_provider_server_status ERROR!!!' % (node_ip, k))

    '''8> get_auth_users'''
    log.info("\t[case1-8 get_auth_users ]")
    wait_time1 = random.randint(120, 125)
    time.sleep(wait_time1)
    cmd = "get_auth_users "
    rc, check_result2 = nas_common.get_auth_users(auth_provider_id=ad_id_16_0_1_28)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users failed!!!' % node_ip)
    totalnumber = msg2["result"]["total"]
    name_list = []
    for n in range(0, totalnumber):
        name_list.append(msg2["result"]["auth_users"][n]["name"])
    if "曙光" not in name_list:
        log.error('node_ip = %s, ad中获取用户失败' % (node_ip))
        raise Exception('%s ad中获取用户失败!!!' % node_ip)

    '''9> get_auth_groups'''
    log.info("\t[case1-9 get_auth_groups ]")
    wait_time1 = random.randint(10, 15)
    time.sleep(wait_time1)
    cmd = "get_auth_groups "
    check_result2 = nas_common.get_auth_groups(auth_provider_id=ad_id_16_0_1_28)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users failed!!!' % node_ip)
    totalnumber = msg2["result"]["total"]
    name_list = []
    for n in range(0, totalnumber):
        name_list.append(msg2["result"]["auth_groups"][n]["name"])
    if "曙光组" not in name_list:
        log.error('node_ip = %s, ad中获取用户组失败' % (node_ip))
        raise Exception('%s ad中获取用户组失败!!!' % node_ip)

    return


#######################################################
# @function：清理环境
# @parameter：
# @return：
# @steps:
#######################################################
def clearing_environment():
    log.info("（3）clearing_environment")

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
    preparing_environment()
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("（2）executing_case")
    executing_case1()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
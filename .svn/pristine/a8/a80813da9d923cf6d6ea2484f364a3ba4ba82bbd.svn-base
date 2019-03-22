# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-06-11
# @summary：
# 16-0-0-102         认证服务器切换
# @steps:
# case1、3节点集群，使用ad认证服务器；
# case2、启动nas服务，切换ldap认证服务；
# @changelog：
#
#######################################################
import os
import random
import time
import commands
import utils_path
import common
import get_config
import log
import nas_common
import shell
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume/nas/nas_16_0_0_102
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
#  7> get_nodes
#  8> enable_nas
#  9> disable_nas
#######################################################
def executing_case1():

    '''1> add_auth_provider_ad '''

    log.info("\t[case1 add_auth_provider_ad ]")
    global ad_name
    ad_name = "nas_16_0_0_102_ad"

    cmd = "add_auth_provider_ad "
    check_result2 = nas_common.add_auth_provider_ad(name=ad_name,
                                                    domain_name=nas_common.AD_DOMAIN_NAME,
                                                    dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                                    username=nas_common.AD_USER_NAME,
                                                    password=nas_common.AD_PASSWORD,
                                                    services_for_unix="NONE",
                                                    unix_id_range="%s-%s" % (1000, 1999),
                                                    other_unix_id_range="%s-%s" % (2000, 2999))
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s add_auth_provider_ad failed!!!' % (node_ip))
    global ad_id_16_0_0_102
    ad_id_16_0_0_102 = msg2["result"]

    '''2> get_auth_providers_ad'''
    log.info("\t[case1-2 get_auth_provider_ad ]")
    cmd = "get_auth_providers_ad"
    check_result2 = nas_common.get_auth_providers_ad(ids=ad_id_16_0_0_102)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_providers_ad failed!!!' % (node_ip))
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
    if id != ad_id_16_0_0_102:
        raise Exception('%s id error!!!' % node_ip)
    if key != ad_id_16_0_0_102:
        raise Exception('%s key error!!!' % node_ip)
    if name != ad_name:
        raise Exception('%s name error!!!' % node_ip)
    if services_for_unix != "NONE":
        raise Exception('%s services_for_unix error!!!' % node_ip)
    if type != "AD":
        raise Exception('%s type error!!!' % node_ip)
    if unix_id_range != [
                1000,
                1999
    ]:
        raise Exception('%s unix_id_range error!!!' % node_ip)
    if username != "administrator":
        raise Exception('%s username error!!!' % node_ip)

    '''3> check_auth_provider'''
    log.info("\t[case1-3 check_auth_provider AD ]")
    cmd = "check_auth_provider "
    check_result2 = nas_common.check_auth_provider(provider_id=ad_id_16_0_0_102)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s check_auth_provider ad failed!!!' % node_ip)

    '''4> create_access_zone'''
    log.info("\t[case1-4 create_access_zone ]")
    global access_zone_name
    access_zone_name = "access_zone_16_0_0_102"

    node = common.Node()
    global ids_list
    ids_list = node.get_nodes_id()
    global access_zone_node_id_16_0_0_102
    access_zone_node_id_16_0_0_102 = ','.join(str(p) for p in ids_list)
    global m
    m = len(ids_list)
    cmd = "create_access_zone"
    check_result2 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_0_102,
                                                  name=access_zone_name,
                                                  auth_provider_id=ad_id_16_0_0_102)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_access_zone failed!!!' % (node_ip))
    global access_zone_id_16_0_0_102
    access_zone_id_16_0_0_102 = msg2["result"]

    '''5> get_access_zones'''
    log.info("\t[case1-5 get_access_zones ]")
    cmd = "get_access_zones"
    check_result2 = nas_common.get_access_zones(ids=access_zone_id_16_0_0_102)
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
    if auth_provider_id != ad_id_16_0_0_102:
        raise Exception('%s auth_provider_id %s != %s error!!!' % (node_ip, auth_provider_id, ad_id_16_0_0_102))
    if auth_provider_name != ad_name:
        raise Exception('%s auth_provider_name %s != %s error!!!' % (node_ip, auth_provider_name, ad_name))
    if auth_provider_type != type:
        raise Exception('%s auth_provider_type %s != %s error!!!' % (node_ip, auth_provider_type, type))
    if access_zones_id != access_zone_id_16_0_0_102:
        raise Exception('%s access_zones_id %s != %s error!!!' % (node_ip, access_zones_id, access_zone_id_16_0_0_102))
    if access_zones_name_1 != access_zone_name:
        raise Exception('%s access_zones_name %s != %s error!!!' % (node_ip, access_zones_name_1, access_zone_name))

    '''6> enable_nas'''
    log.info("\t[case1-6 enable_nas ]")
    cmd = "enable_nas"
    check_result2 = nas_common.enable_nas(access_zone_id=access_zone_id_16_0_0_102)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s enable_nass failed!!!' % (node_ip))

    '''7> 查看NAS服务状态'''
    for j in range(0, m):
        k = ids_list[j]
        log.info("\t[ case1-7 查看NAS服务状态 node=%s]" % k)
        # cmd = "pscli --command=get_nodes --ids=%s" % k
        # rc, stdout, stderr = shell.ssh(node_ip, cmd)
        # msg4 = common.json_loads(stdout)
        node = common.Node()
        msg4 = node.get_nodes(ids=k)
        status = msg4["result"]["nodes"][0]["reported_info"]["nas_protocol"]["server_status"]["auth_provider_server_status"]
        print status
        if msg4["result"]["nodes"][0]["reported_info"]["nas_protocol"]["server_status"]["auth_provider_server_status"] != "SERV_STATE_OK":
            raise Exception('ip=%s, node_id=%s auth_provider_server_status ERROR!!!' % (node_ip, k))

    '''8> get_auth_users'''
    log.info("\t[case1-8 get_auth_users ]")
    cmd = "get_auth_users "
    rc, check_result2 = nas_common.get_auth_users(auth_provider_id=ad_id_16_0_0_102)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users failed!!!' % node_ip)
    totalnumber = msg2["result"]["total"]
    name_list = []
    for n in range(0, totalnumber):
        name_list.append(msg2["result"]["auth_users"][n]["name"])
    if "administrator" not in name_list:
        log.error('node_ip = %s, ad中获取用户失败' % (node_ip))
        raise Exception('%s ad中获取用户失败!!!' % node_ip)

    '''9> disable_nas'''
    log.info("\t[case1-9 disable_nas ]")
    cmd = "disable_nas "
    check_result2 = nas_common.disable_nas(access_zone_id=access_zone_id_16_0_0_102)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s disable_nass failed!!!' % (node_ip))

    return


#######################################################
# 2.executing_case2
# @function：启动nas服务，切换ldap认证服务；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：启动nas服务，切换ldap认证服务；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#  1> add_auth_provider_ldap
#  2> get_auth_providers_ldap
#  3> check_auth_provider
#  4> update_access_zone
#  5> get_access_zones
#  6> enable_nas
#  7> get_nodes
#  8> enable_nas
#  9> disable_nas
#
#######################################################
def executing_case2():
    '''1> add_auth_provider_ldap'''
    log.info("\t[case2-1 add_auth_provider_ldap ]")
    global ldap_name
    ldap_name = "nas_16_0_0_102_ldap"
    global LDAP_IP
    LDAP_IP = nas_common.LDAP_IP_ADDRESSES
    global LDAP_BASE_DN
    LDAP_BASE_DN = nas_common.LDAP_BASE_DN
    cmd = "add_auth_provider_ldap  "
    check_result2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=LDAP_BASE_DN,
                                                      ip_addresses=LDAP_IP, port=389)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s add_auth_provider_ldap failed!!!' % (node_ip))
    global ldap_id_16_0_0_102
    ldap_id_16_0_0_102 = msg2["result"]

    '''2> get_auth_providers_ldap'''
    log.info("\t[case2-2 get_auth_providers_ldap ]")
    cmd = "get_auth_providers_ldap "
    check_result2 = nas_common.get_auth_providers_ldap(ids=ldap_id_16_0_0_102)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_providers_ldap failed!!!' % (node_ip))
    name1 = msg2["result"]["auth_providers"][0]["name"]
    base_dn1 = msg2["result"]["auth_providers"][0]["base_dn"]
    id1 = msg2["result"]["auth_providers"][0]["id"]
    key1 = msg2["result"]["auth_providers"][0]["key"]
    ip_addresses1 = msg2["result"]["auth_providers"][0]["ip_addresses"][0]
    port1 = msg2["result"]["auth_providers"][0]["port"]
    type1 = msg2["result"]["auth_providers"][0]["type"]
    if name1 != ldap_name:
        raise Exception('%s name1 error!!!' % node_ip)
    if base_dn1 != LDAP_BASE_DN:
        raise Exception('%s base_dn1 error!!!' % node_ip)
    if id1 != ldap_id_16_0_0_102:
        raise Exception('%s id1 error!!!' % node_ip)
    if key1 != ldap_id_16_0_0_102:
        raise Exception('%s key1 error!!!' % node_ip)
    if ip_addresses1 != LDAP_IP:
        raise Exception('%s ip_addresses1 error!!!' % node_ip)
    if port1 != 389:
        raise Exception('%s port1 error!!!' % node_ip)
    if type1 != "LDAP":
        raise Exception('%s type1 error!!!' % node_ip)

    '''3> check_auth_provider'''
    log.info("\t[case2-3 check_auth_provider]")
    cmd = "check_auth_provider "
    check_result2 = nas_common.check_auth_provider(provider_id=ldap_id_16_0_0_102)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s check_auth_provider failed!!!' % (node_ip))

    '''4> update_access_zone'''
    log.info("\t[case2-4 update_access_zone]")
    cmd = "update_access_zone"
    check_result2 = nas_common.update_access_zone(access_zone_id=access_zone_id_16_0_0_102,
                                                  auth_provider_id=ldap_id_16_0_0_102)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s update_access_zone failed!!!' % node_ip)

    '''5> get_access_zones'''
    log.info("\t[case2-5 get_access_zones ]")
    cmd = "get_access_zones"
    check_result2 = nas_common.get_access_zones(ids=access_zone_id_16_0_0_102)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_access_zone failed!!!' % node_ip)
    auth_provider_id = msg2["result"]["access_zones"][0]["auth_provider"]["id"]
    auth_provider_name = msg2["result"]["access_zones"][0]["auth_provider"]["name"]
    auth_provider_type = msg2["result"]["access_zones"][0]["auth_provider"]["type"]
    access_zones_id = msg2["result"]["access_zones"][0]["id"]
    access_zones_name_1 = msg2["result"]["access_zones"][0]["name"]
    if auth_provider_id != ldap_id_16_0_0_102:
        raise Exception('%s auth_provider_id %s != %s error!!!' % (node_ip, auth_provider_id, ldap_id_16_0_0_102))
    if auth_provider_name != ldap_name:
        raise Exception('%s auth_provider_name %s != %s error!!!' % (node_ip, auth_provider_name, ldap_name))
    if auth_provider_type != type1:
        raise Exception('%s auth_provider_type %s != %s error!!!' % (node_ip, auth_provider_type, type1))
    if access_zones_id != access_zone_id_16_0_0_102:
        raise Exception('%s access_zones_id %s != %s error!!!' % (node_ip, access_zones_id, access_zone_id_16_0_0_102))
    if access_zones_name_1 != access_zone_name:
        raise Exception('%s access_zones_name %s != %s error!!!' % (node_ip, access_zones_name_1, access_zone_name))

    '''6> enable_nas'''
    log.info("\t[case2-6 enable_nas ]")
    cmd = "enable_nas"
    check_result2 = nas_common.enable_nas(access_zone_id=access_zone_id_16_0_0_102)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s enable_nass failed!!!' % node_ip)

    '''7> 查看NAS服务状态'''
    for j in range(0, m):
        k = ids_list[j]
        log.info("\t[ case2-7 查看NAS服务状态 node=%s]" % k)
        # cmd = "pscli --command=get_nodes --ids=%s" % k
        # rc, stdout, stderr = shell.ssh(node_ip, cmd)
        # msg4 = common.json_loads(stdout)
        node = common.Node()
        msg4 = node.get_nodes(ids=k)
        if msg4["result"]["nodes"][0]["reported_info"]["nas_protocol"]["server_status"]["auth_provider_server_status"] != "SERV_STATE_OK":
            raise Exception('ip=%s, node_id=%s auth_provider_server_status ERROR!!!' % (node_ip, k))

    '''8> get_auth_users'''
    log.info("\t[case2-8 get_auth_users ]")
    cmd = "get_auth_users"
    rc, check_result2 = nas_common.get_auth_users(auth_provider_id=ldap_id_16_0_0_102)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users failed!!!' % node_ip)
    totalnumber = msg2["result"]["total"]
    name_list = []
    for n in range(0, totalnumber):
        name_list.append(msg2["result"]["auth_users"][n]["name"])
    if nas_common.LDAP_USER_3_NAME not in name_list:
        log.error('node_ip = %s, ldap中获取用户失败' % (node_ip))
        raise Exception('%s ldap中获取用户失败!!!' % node_ip)

    '''9> disable_nas'''
    log.info("\t[case2-9 disable_nas ]")
    cmd = "disable_nas"
    check_result2 = nas_common.disable_nas(access_zone_id=access_zone_id_16_0_0_102)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s disable_nass failed!!!' % node_ip)

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
def executing_case():
    log.info("（2）executing_case")

    '''
    1、测试执行
    2、结果检查
    '''

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
    executing_case2()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
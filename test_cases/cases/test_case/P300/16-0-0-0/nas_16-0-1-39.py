# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-06-13
# @summary：
# 16_0_1_39         用户/用户组查询
# @steps:
# case1、未启动NAS获取用户/用户组；
# case2、启动NAS获取用户/用户组；
#
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
import prepare_clean


FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)              # /mnt/volume/nas/nas_16_0_1_39
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：查询nis用户/用户组；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：查询nis用户/用户组；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#  1> add_auth_provider_nis
#  2> get_auth_providers_nis
#  3> check_auth_provider
#  4> get_auth_users
#  5> get_auth_groups
#  6> delete_auth_providers
#######################################################
def executing_case1():
    '''1> add_auth_provider_nis'''
    log.info("\t[case1-1 add_auth_provider_nis ]")
    global nis_name
    nis_name = "nas_16_0_1_39_nis"
    cmd = "add_auth_provider_nis "
    check_result2 = nas_common.add_auth_provider_nis(name=nis_name,
                                                     domain_name=nas_common.NIS_DOMAIN_NAME,
                                                     ip_addresses=nas_common.NIS_IP_ADDRESSES)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s add_auth_provider_nis failed!!!' % (node_ip))
    global nis_id_16_0_1_39
    nis_id_16_0_1_39 = msg2["result"]

    '''2> get_auth_providers_ldap'''
    log.info("\t[case1-2 get_auth_providers_nis ]")
    cmd = "get_auth_providers_nis "
    check_result2 = nas_common.get_auth_providers_nis(ids=nis_id_16_0_1_39)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_providers_nis %s failed!!!' % (node_ip, nis_id_16_0_1_39))
    domain_name = msg2["result"]["auth_providers"][0]["domain_name"]
    id = msg2["result"]["auth_providers"][0]["id"]
    key = msg2["result"]["auth_providers"][0]["key"]
    ip_addresses = msg2["result"]["auth_providers"][0]["ip_addresses"][0]
    name = msg2["result"]["auth_providers"][0]["name"]
    type = msg2["result"]["auth_providers"][0]["type"]
    if domain_name != "nistest":
        raise Exception('%s domain_name error!!!' % node_ip)
    if id != nis_id_16_0_1_39:
        raise Exception('%s id error!!!' % node_ip)
    if key != nis_id_16_0_1_39:
        raise Exception('%s key error!!!' % node_ip)
    if ip_addresses != nas_common.NIS_IP_ADDRESSES:
        raise Exception('%s ip_addresses error!!!' % node_ip)
    if name != nis_name:
        raise Exception('%s name error!!!' % node_ip)
    if type != "NIS":
        raise Exception('%s type error!!!' % node_ip)

    '''3> check_auth_provider'''
    log.info("\t[case1-3 check_auth_provider ]")
    cmd = "check_auth_provider "
    check_result2 = nas_common.check_auth_provider(provider_id=nis_id_16_0_1_39)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s check_auth_provider failed!!!' % node_ip)

    '''4> get_auth_users'''
    log.info("\t[case1-4 get_auth_users]")
    cmd = "get_auth_users "
    rc, check_result2 = nas_common.get_auth_users(auth_provider_id=nis_id_16_0_1_39)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "" or msg2["result"]["auth_users"] == []:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users failed!!!' % node_ip)
    totalnumber = msg2["result"]["total"]
    name_list = []
    for i in range(0, totalnumber):
        name_list.append(msg2["result"]["auth_users"][i]["name"])
    if "nisserver" not in name_list:
        log.error('node_ip = %s, nis获取用户没有被正确显示' % node_ip)
        raise Exception('%s nis获取用户用户没有被正确显示!!!' % node_ip)

    '''5> get_auth_groups'''
    log.info("\t[case1-5 get_auth_groups ]")
    cmd = "get_auth_groups "
    check_result2 = nas_common.get_auth_groups(auth_provider_id=nis_id_16_0_1_39)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "" or msg2["result"]["auth_groups"] == []:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_groups failed!!!' % node_ip)
    totalnumber = msg2["result"]["total"]
    name_list = []
    for i in range(0, totalnumber):
        name_list.append(msg2["result"]["auth_groups"][i]["name"])
    if "nisserver" not in name_list:
        log.error('node_ip = %s, nis获取用户组没有被正确显示' % node_ip)
        raise Exception('%s nis获取用户组没有被正确显示!!!' % node_ip)

    '''6> delete_auth_providers'''
    cmd = "delete_auth_providers "
    check_result2 = nas_common.delete_auth_providers(ids=nis_id_16_0_1_39)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s delete_auth_providers falied!!!' % node_ip)
    return


#######################################################
# 2.executing_case2
# @function：启动NAS，查询nis用户/用户组；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：查询nis用户/用户组；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#  1> add_auth_provider_nis
#  2> get_auth_providers_nis
#  3> check_auth_provider
#  4> create_access_zone
#  5> get_access_zones
#  6> enable_nas
#  7> 查看NAS服务状态
#  8> get_auth_users
#  9> get_auth_groups
#  10> disable_nas
#######################################################
def executing_case2():
    '''1> add_auth_provider_nis'''
    log.info("\t[case2-1 add_auth_provider_nis ]")
    global nis_name
    nis_name = "nas_16_0_1_39_nis"
    cmd = "add_auth_provider_nis"
    check_result2 = nas_common.add_auth_provider_nis(name=nis_name,
                                                     domain_name=nas_common.NIS_DOMAIN_NAME,
                                                     ip_addresses=nas_common.NIS_IP_ADDRESSES)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s add_auth_provider_nis failed!!!' % (node_ip))
    global nis_id_16_0_1_39
    nis_id_16_0_1_39 = msg2["result"]

    '''2> get_auth_providers_nis'''
    log.info("\t[case2-2 get_auth_providers_nis ]")
    cmd = "get_auth_providers_nis "
    check_result2 = nas_common.get_auth_providers_nis(ids=nis_id_16_0_1_39)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_providers_nis %s failed!!!' % (node_ip, nis_id_16_0_1_39))
    domain_name = msg2["result"]["auth_providers"][0]["domain_name"]
    id = msg2["result"]["auth_providers"][0]["id"]
    key = msg2["result"]["auth_providers"][0]["key"]
    ip_addresses = msg2["result"]["auth_providers"][0]["ip_addresses"][0]
    name = msg2["result"]["auth_providers"][0]["name"]
    type = msg2["result"]["auth_providers"][0]["type"]
    if domain_name != "nistest":
        raise Exception('%s domain_name error!!!' % node_ip)
    if id != nis_id_16_0_1_39:
        raise Exception('%s id error!!!' % node_ip)
    if key != nis_id_16_0_1_39:
        raise Exception('%s key error!!!' % node_ip)
    if ip_addresses != nas_common.NIS_IP_ADDRESSES:
        raise Exception('%s ip_addresses error!!!' % node_ip)
    if name != nis_name:
        raise Exception('%s name error!!!' % node_ip)
    if type != "NIS":
        raise Exception('%s type error!!!' % node_ip)

    '''3> check_auth_provider'''
    log.info("\t[case2-3 check_auth_provider ]")
    cmd = "check_auth_provider"
    check_result2 = nas_common.check_auth_provider(provider_id=nis_id_16_0_1_39)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s check_auth_provider failed!!!' % node_ip)

    '''4> create_access_zone'''
    log.info("\t[case1-4 create_access_zone ]")
    global access_zone_name
    access_zone_name = "access_zone_16_0_1_39"
    node = common.Node()
    ids_list = node.get_nodes_id()
    global ids_list
    print ids_list
    global access_zone_node_id_16_0_1_39
    access_zone_node_id_16_0_1_39 = ','.join(str(p) for p in ids_list)
    global m
    m = len(ids_list)
    cmd = "create_access_zone"
    check_result2 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_1_39,
                                                  name=access_zone_name,
                                                  auth_provider_id=nis_id_16_0_1_39)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_access_zone failed!!!' % (node_ip))
    global access_zone_id_16_0_1_39
    access_zone_id_16_0_1_39 = msg2["result"]

    '''5> get_access_zones'''
    log.info("\t[case1-5 get_access_zones ]")
    cmd = "get_access_zones "
    check_result2 = nas_common.get_access_zones(ids=access_zone_id_16_0_1_39)
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
    if auth_provider_id != nis_id_16_0_1_39:
        raise Exception('%s auth_provider_id %s != %s error!!!' % (node_ip, auth_provider_id, nis_id_16_0_1_39))
    if auth_provider_name != nis_name:
        raise Exception('%s auth_provider_name %s != %s error!!!' % (node_ip, auth_provider_name, nis_name))
    if auth_provider_type != type:
        raise Exception('%s auth_provider_type %s != %s error!!!' % (node_ip, auth_provider_type, type))
    if access_zones_id != access_zone_id_16_0_1_39:
        raise Exception('%s access_zones_id %s != %s error!!!' % (node_ip, access_zones_id, access_zone_id_16_0_1_39))
    if access_zones_name_1 != access_zone_name:
        raise Exception('%s access_zones_name %s != %s error!!!' % (node_ip, access_zones_name_1, access_zone_name))

    '''6> enable_nas'''
    log.info("\t[case1-6enable_nas ]")
    cmd = "enable_nas "
    check_result2 = nas_common.enable_nas(access_zone_id=access_zone_id_16_0_1_39)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s enable_nass failed!!!' % (node_ip))

    '''7> 查看NAS服务状态'''
    rc = nas_common.check_nas_status()
    common.judge_rc(rc, 0, "NAS服务状态不正确，请查看NAS相关的服务状态")
    # for j in range(0, m):
    #     k = ids_list[j]
    #     log.info("\t[ case1-7 查看NAS服务状态 node=%s]" % (k))
    #     cmd = "pscli --command=get_nodes --ids=%s" % k
    #     rc, stdout, stderr = shell.ssh(node_ip, cmd)
    #     msg4 = common.json_loads(stdout)
    #     status = msg4["result"]["nodes"][0]["reported_info"]["nas_protocol"]["server_status"][
    #         "auth_provider_server_status"]
    #     print status
    #     if msg4["result"]["nodes"][0]["reported_info"]["nas_protocol"]["server_status"][
    #         "auth_provider_server_status"] != "SERV_STATE_OK":
    #         raise Exception('ip=%s, node_id=%s auth_provider_server_status ERROR!!!' % (node_ip, k))

    '''8> get_auth_users'''
    log.info("\t[case1-8 get_auth_users]")
    cmd = "get_auth_users "
    rc, check_result2 = nas_common.get_auth_users(auth_provider_id=nis_id_16_0_1_39)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "" or msg2["result"]["auth_users"] == []:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users failed!!!' % node_ip)
    totalnumber = msg2["result"]["total"]
    name_list = []
    for i in range(0, totalnumber):
        name_list.append(msg2["result"]["auth_users"][i]["name"])
    if "nisserver" not in name_list:
        log.error('node_ip = %s, nis获取用户没有被正确显示' % (node_ip))
        raise Exception('%s nis获取用户用户没有被正确显示!!!' % node_ip)

    '''9> get_auth_groups'''
    log.info("\t[case1-9 get_auth_groups ]")
    cmd = "get_auth_groups"
    check_result2 = nas_common.get_auth_groups(auth_provider_id=nis_id_16_0_1_39)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "" or msg2["result"]["auth_groups"] == []:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_groups!!!' % node_ip)
    totalnumber = msg2["result"]["total"]
    name_list = []
    for i in range(0, totalnumber):
        name_list.append(msg2["result"]["auth_groups"][i]["name"])
    if "nisserver" not in name_list:
        log.error('node_ip = %s, nis获取用户组没有被正确显示' % (node_ip))
        raise Exception('%s nis获取用户组没有被正确显示!!!' % node_ip)

    '''10> disable_nas'''
    log.info("\t[case1-10 disable_nas ]")
    cmd = "disable_nas "
    check_result2 = nas_common.disable_nas(access_zone_id=access_zone_id_16_0_1_39)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s disable_nass failed!!!' % (node_ip))

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
    executing_case2()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
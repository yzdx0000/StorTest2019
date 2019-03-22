# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-06-12
# @summary：
# 16-0-1-27          用户/用户组查询
# @steps:
#  1> add_auth_provider_ad
#  2> get_auth_providers_ad
#  3> check_auth_provider
#  4> get_auth_users
#  5> get_auth_groups

# case1、查询AD认证用户；
# pscli --command=get_auth_users --auth_provider_id=x，x为AD认证服务器id
# case2、查询AD认证用户组；
# pscli --command=get_auth_groups --auth_provider_id=x，x为AD认证服务器id
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
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume/nas/nas_16_0_1_27
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


def executing_case1():

    '''1> add_auth_provider_ad '''
    log.info("\t[case1 add_auth_provider_ad ]")
    global ad_name
    ad_name = "nas_16_0_1_27_ad"

    cmd = "add_auth_provider_ad"
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
    global ad_id_16_0_1_27
    ad_id_16_0_1_27 = msg2["result"]

    '''2> get_auth_providers_ad'''
    log.info("\t[case1-2 get_auth_provider_ad ]")
    cmd = "get_auth_providers_ad "
    check_result2 = nas_common.get_auth_providers_ad(ids=ad_id_16_0_1_27)
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
    if id != ad_id_16_0_1_27:
        raise Exception('%s id error!!!' % node_ip)
    if key != ad_id_16_0_1_27:
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
    check_result2 = nas_common.check_auth_provider(provider_id=ad_id_16_0_1_27)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s check_auth_provider ad failed!!!' % (node_ip))

    '''4> get_auth_users'''
    log.info("\t[case1-4 get_auth_users ]")
    cmd = "get_auth_users "
    rc, check_result2 = nas_common.get_auth_users(auth_provider_id=ad_id_16_0_1_27)
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

    '''5> get_auth_groups'''
    log.info("\t[case1-5 get_auth_groups ]")
    cmd = "get_auth_groups"
    check_result2 = nas_common.get_auth_groups(auth_provider_id=ad_id_16_0_1_27)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users failed!!!' % node_ip)
    totalnumber = msg2["result"]["total"]
    name_list = []
    for n in range(0, totalnumber):
        name_list.append(msg2["result"]["auth_groups"][n]["name"])
    if "domain users" not in name_list:
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
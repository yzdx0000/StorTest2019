# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-19
# @summary：
# 16-0-0-62           查询LDAP认证服务器信息测试
# @steps:
# case1、集群添加ldap认证；
# pscli --command=add_auth_provider_ldap --name=ldap_test --ip_addresses=x.x.x.x --base_dn=dc=xxx,dc=com --port=389
# --bind_dn=cn=root,dc=test,dc=com --bind_password=111111
# --user_search_path=ou=People,dc=test,dc=com --group_search_path=ou=Group,dc=test,dc=com
# case2、通过命令pscli --command=get_auth_provider_ldap查看ldap认证服务器配置信息；
# case3、通过命令行pscli --command=check_auth_provider --ids=x查看认证配置信息是否能够正确的连接ldap认证服务器；
# pscli --command=update_auth_provider_ldap --id=x
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
import get_config
import prepare_clean


FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)              # /mnt/volume/nas/nas_16_0_0_62
node_ip = get_config.get_parastor_ip()


def executing_case1():
    # 1.集群添加ldap认证
    log.info("\t[case1 add_auth_provider_ldap]")
    global LDAP_IP
    LDAP_IP = nas_common.LDAP_IP_ADDRESSES
    global LDAP_BASE_DN
    LDAP_BASE_DN = nas_common.LDAP_BASE_DN
    global LDAP_BIND_DN
    LDAP_BIND_DN = nas_common.LDAP_BIND_DN
    global LDAP_BIND_PASSWORD
    LDAP_BIND_PASSWORD = nas_common.LDAP_BIND_PASSWORD
    global LDAP_USER_SEARCH_PATH
    LDAP_USER_SEARCH_PATH = nas_common.LDAP_USER_SEARCH_PATH
    global LDAP_GROUP_SEARCH_PATH
    LDAP_GROUP_SEARCH_PATH = nas_common.LDAP_GROUP_SEARCH_PATH
    global LDAP_DOMAIN_PASSWORD
    LDAP_DOMAIN_PASSWORD = nas_common.LDAP_DOMAIN_PASSWORD
    cmd = "add_auth_provider_ldap"
    check_result2 = nas_common.add_auth_provider_ldap(name="nas_16_0_0_62_ldap", base_dn=LDAP_BASE_DN,
                                                      ip_addresses=LDAP_IP, port=389,
                                                      bind_dn=LDAP_BIND_DN, bind_password=LDAP_BIND_PASSWORD,
                                                      domain_password=LDAP_DOMAIN_PASSWORD,
                                                      user_search_path=LDAP_USER_SEARCH_PATH,
                                                      group_search_path=LDAP_GROUP_SEARCH_PATH)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s add_auth_provider_ldap failed!!!' % node_ip)
    global id_16_0_0_62
    id_16_0_0_62 = msg2["result"]

    # 2. 通过命令pscli --command=get_auth_provider_ldap查看ldap认证配置信息是否正确
    log.info("\t[case2 get_auth_providers_ldap ]")
    wait_time1 = random.randint(1, 3)
    time.sleep(wait_time1)
    cmd = "get_auth_providers_ldap "
    check_result2 = nas_common.get_auth_providers_ldap(ids=id_16_0_0_62)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_providers_ldap failed!!!' % node_ip)
    base_dn = msg2["result"]["auth_providers"][0]["base_dn"]
    bind_dn = msg2["result"]["auth_providers"][0]["bind_dn"]
    ip_addresses = msg2["result"]["auth_providers"][0]["ip_addresses"][0]
    name = msg2["result"]["auth_providers"][0]["name"]
    port = msg2["result"]["auth_providers"][0]["port"]
    type = msg2["result"]["auth_providers"][0]["type"]
    group_search_path = msg2["result"]["auth_providers"][0]["group_search_path"]
    user_search_path = msg2["result"]["auth_providers"][0]["user_search_path"]
    if base_dn != LDAP_BASE_DN:
        raise Exception('%s base_dn error!!!' % node_ip)
    if bind_dn != LDAP_BIND_DN:
        raise Exception('%s bind_dn error!!!' % node_ip)
    if ip_addresses != LDAP_IP:
        raise Exception('%s ip_addresses error!!!' % node_ip)
    if name != "nas_16_0_0_62_ldap":
        raise Exception('%s name error!!!' % node_ip)
    if port != 389:
        raise Exception('%s port error!!!' % node_ip)
    if type != "LDAP":
        raise Exception('%s type error!!!' % node_ip)
    if group_search_path != LDAP_GROUP_SEARCH_PATH:
        raise Exception('%s group_search_path error!!!' % node_ip)
    if user_search_path != LDAP_USER_SEARCH_PATH:
        raise Exception('%s user_search_path error!!!' % node_ip)

    # 3.通过命令行pscli --command=check_auth_provider --ids=x查看认证配置信息是否能够正确的连接ldap认证
    log.info("\t[case3 check_auth_provider ]")
    cmd = "check_auth_provider"
    check_result2 = nas_common.check_auth_provider(provider_id=id_16_0_0_62)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s check_auth_provider failed!!!' % node_ip)
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
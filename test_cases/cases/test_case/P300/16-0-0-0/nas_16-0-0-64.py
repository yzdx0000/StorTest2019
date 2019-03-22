# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-20
# @summary：
# 16-0-0-64          删除LDAP认证服务器测试（使用中）
# @steps:
# case1、集群添加ldap认证；
# pscli --command=add_auth_provider_ldap --name=ldap_test --ip_addresses=x.x.x.x --base_dn=dc=xxx,dc=com --port=389
# case2、通过命令pscli --command=get_auth_provider_ldap查看ldap认证服务器配置信息；
# case3、通过命令行pscli --command=check_auth_provider --ids=x查看认证配置信息是否能够正确的连接ldap认证服务器；
# case4、配置访问区分，使用上面创建的认证；
# case5、删除认证；
# pscli --command=delete_auth_providers --id=x
# case6、通过命令pscli --command=get_auth_provider_ldap查看ldap认证配置信息是否正确
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
import shell
import log
import get_config
import prepare_clean


FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)              # /mnt/volume/nas/nas_16_0_0_64
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


def executing_case1():
    # 1.集群添加ldap认证
    log.info("\t[case1 add_auth_provider_ldap]")
    global LDAP_IP
    LDAP_IP = nas_common.LDAP_IP_ADDRESSES
    global LDAP_BASE_DN
    LDAP_BASE_DN = nas_common.LDAP_BASE_DN
    cmd = "add_auth_provider_ldap "
    check_result2 = nas_common.add_auth_provider_ldap(name="nas_16_0_0_64_ldap_2", base_dn=LDAP_BASE_DN,
                                                      ip_addresses=LDAP_IP, port=389)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s add_auth_provider_ldap failed!!!' % node_ip)
    global id_16_0_0_64
    id_16_0_0_64 = msg2["result"]

    # 2.通过命令pscli --command=get_auth_provider_ldap查看ldap认证配置信息是否正确
    log.info("\t[case2 get_auth_providers_ldap ]")
    cmd = "get_auth_providers_ldap"
    check_result2 = nas_common.get_auth_providers_ldap(ids=id_16_0_0_64)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_providers_ldap failed!!!' % node_ip)
    base_dn = msg2["result"]["auth_providers"][0]["base_dn"]
    ip_addresses = msg2["result"]["auth_providers"][0]["ip_addresses"][0]
    name = msg2["result"]["auth_providers"][0]["name"]
    port = msg2["result"]["auth_providers"][0]["port"]
    type = msg2["result"]["auth_providers"][0]["type"]
    if base_dn != LDAP_BASE_DN:
        raise Exception('%s base_dn error!!!' % node_ip)
    if ip_addresses != LDAP_IP:
        raise Exception('%s ip_addresses error!!!' % node_ip)
    if name != "nas_16_0_0_64_ldap_2":
        raise Exception('%s name error!!!' % node_ip)
    if port != 389:
        raise Exception('%s port error!!!' % node_ip)
    if type != "LDAP":
        raise Exception('%s type error!!!' % node_ip)

    # 3.通过命令行pscli --command=check_auth_provider --ids=x查看认证配置信息是否能够正确的连接ldap认证
    log.info("\t[case3 check_auth_provider ]")
    wait_time1 = random.randint(2, 5)
    time.sleep(wait_time1)
    cmd = "check_auth_provider"
    check_result2 = nas_common.check_auth_provider(provider_id=id_16_0_0_64)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s check_auth_provider failed!!!' % node_ip)

    # 4.配置访问区分，使用上面创建的认证
    log.info("\t[case4 create_access_zone ]")
    access_zone_name = "access_zone_16_0_0_64_1"
    node = common.Node()
    ids = node.get_nodes_id()
    access_zone_node_id_16_0_0_64 = ','.join(str(p) for p in ids)
    cmd = "create_access_zone "
    check_result1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_0_64, auth_provider_id=id_16_0_0_64,
                                                  name=access_zone_name, isns_address="10.22.0.78")
    log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s create_access_zone failed!!!' % node_ip)

    # 5.删除认证
    log.info("\t[case5 delete_auth_provider]")
    cmd = "delete_auth_providers"
    check_result2 = nas_common.delete_auth_providers(ids=id_16_0_0_64)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("is being used by access zone") == -1:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s delete_auth_provider failed!!!' % node_ip)

    # 6.通过命令pscli --command=get_auth_provider_ldap查看ldap认证配置信息是否正确
    log.info("\t[case6 get_auth_providers_ldap ]")
    cmd = "get_auth_providers_ldap "
    check_result2 = nas_common.get_auth_providers_ldap(ids=id_16_0_0_64)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_providers_ldap failed!!!' % node_ip)

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
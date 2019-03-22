# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-19
# @summary：
# 16-0-0-51         规格外连接ldap认证服务器
# @steps:
# case 1、创建第128个认证，观察是否创建成功；
# case 2、验证是否有128个；
# case 3、创建第129个认证，观察是否创建成功；
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

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)              # /mnt/volume/nas/nas_16_0_0_51
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：创建第128个认证，观察是否创建成功；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：创建第128个认证，观察是否创建成功；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#
#######################################################
def executing_case1():
    log.info("\t[case1-1 add_auth_provider_ldap 128]")
    global ldap_id_16_0_0_51_list
    ldap_id_16_0_0_51_list = []
    global LDAP_IP
    LDAP_IP = nas_common.LDAP_IP_ADDRESSES
    global LDAP_BASE_DN
    LDAP_BASE_DN = nas_common.LDAP_BASE_DN
    check_result = nas_common.get_auth_providers_ldap()
    ldap_provider_num = check_result["result"]["total"]
    for i in range(ldap_provider_num + 1, 129):
        log.info("\t[case1-2 add_auth_provider_ldap %s]" % i)
        global ldap_name
        ldap_name = "nas_16_0_0_51_ldap_%s" % i
        cmd = "add_auth_provider_ldap  "
        check_result2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=LDAP_BASE_DN,
                                                          ip_addresses=LDAP_IP, port=389)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s add_auth_provider_ldap %s failed!!!' % (node_ip, i))
        global ldap_id_16_0_0_51
        ldap_id_16_0_0_51 = msg2["result"]
        ldap_id_16_0_0_51_list.append(msg2["result"])

        '''3> get_auth_providers_ldap'''
        log.info("\t[case1-3 get_auth_providers_ldap %s]" % i)
        cmd = "get_auth_providers_ldap"
        check_result2 = nas_common.get_auth_providers_ldap(ids=ldap_id_16_0_0_51)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s get_auth_providers_ldap %s failed!!!' % (node_ip, i))
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
        if id1 != ldap_id_16_0_0_51:
            raise Exception('%s id1 error!!!' % node_ip)
        if key1 != ldap_id_16_0_0_51:
            raise Exception('%s key1 error!!!' % node_ip)
        if ip_addresses1 != LDAP_IP:
            raise Exception('%s ip_addresses1 error!!!' % node_ip)
        if port1 != 389:
            raise Exception('%s port1 error!!!' % node_ip)
        if type1 != "LDAP":
            raise Exception('%s type1 error!!!' % node_ip)

        '''4> check_auth_provider'''
        log.info("\t[case1-4 check_auth_provider %s]" % i)
        cmd = "check_auth_provider "
        check_result2 = nas_common.check_auth_provider(provider_id=ldap_id_16_0_0_51)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s check_auth_provider %s failed!!!' % (node_ip, i))
    return


#######################################################
# 2.executing_case2
# @function：验证是否有128个；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：验证是否有128个；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#
#
#######################################################
def executing_case2():
    log.info("\t[case2 get_auth_providers_ldap ]")
    cmd = "get_auth_providers_ldap "
    check_result2 = nas_common.get_auth_providers_ldap()
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_providers_ldap failed!!!' % node_ip)
    total = msg2["result"]["total"]
    if total != 128:
        raise Exception('%s get_auth_providers_ldap 128 failed!!!' % node_ip)
    return


#######################################################
# 3.executing_case3
# @function：创建第129个认证，观察是否创建成功；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：创建第129个认证，观察是否创建成功；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#
#######################################################
def executing_case3():
    log.info("\t[case3 add_auth_provider_ldap 129]")
    cmd = "add_auth_provider_ldap  "
    check_result2 = nas_common.add_auth_provider_ldap(name="nas_16_0_0_51_ldap_129", base_dn=LDAP_BASE_DN,
                                                      ip_addresses=LDAP_IP, port=389)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "ILLEGAL_OPERATION" or \
       msg2["detail_err_msg"] != "LDAP authentication providers count:128 has reached limit:128":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s add_auth_provider_ldap 129 failed!!!' % node_ip)
    return


#######################################################
# @function：清理环境
# @parameter：
# @return：
# @steps:
#######################################################
def clearing_environment():

    log.info("（3）clearing_environment")
    delete_ldap_num = len(ldap_id_16_0_0_51_list)
    for j in range(0, delete_ldap_num):
        m = ldap_id_16_0_0_51_list[j]
        log.info("\t[ delete_auth_providers ldap %s]" % m)
        cmd = "delete_auth_providers "
        check_result2 = nas_common.delete_auth_providers(ids=m)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s delete_auth_providers ldap %s failed!!!' % (node_ip, m))

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
    executing_case3()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
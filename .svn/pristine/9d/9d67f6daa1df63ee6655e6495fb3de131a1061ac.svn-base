# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-19
# @summary：
# 16-0-0-52         验证ldap认证服务器配置测试
# @steps:
# step 1、配置128个相同的ldap认证；
# step 2、验证是否有128个；
# step3、通过pscli --command=check_auth_providers --ids=x查看认证配置信息是否能够正确的连接LDAP认证；
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
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)              # /mnt/volume/nas/nas_16_0_0_52
node_ip = get_config.get_parastor_ip()


def executing_case1():
    global ldap_id_16_0_0_52_list
    ldap_id_16_0_0_52_list = []
    global LDAP_IP
    LDAP_IP = nas_common.LDAP_IP_ADDRESSES
    global LDAP_BASE_DN
    LDAP_BASE_DN = nas_common.LDAP_BASE_DN
    check_result = nas_common.get_auth_providers_ldap()
    ldap_provider_num = check_result["result"]["total"]
    for i in range(ldap_provider_num +1, 129):

        """
        1.添加auth_provider_ldap
        """
        log.info("\t[step1 add_auth_provider_ldap %s]" % i)
        cmd = "add_auth_provider_ldap "
        ldap_name = "nas_16_0_0_52_ldap_%s" % i
        check_result2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=LDAP_BASE_DN,
                                                          ip_addresses=LDAP_IP, port=389)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s add_auth_provider_ldap failed!!!' % node_ip)
        global id_16_0_0_52
        id_16_0_0_52 = msg2["result"]
        ldap_id_16_0_0_52_list.append(msg2["result"])

        """
        2.查看auth_provider_ldap
        """
        log.info("\t[step2 get_auth_providers_ldap ]")
        cmd = "get_auth_providers_ldap"
        check_result2 = nas_common.get_auth_providers_ldap(ids=id_16_0_0_52)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s get_auth_providers_ldap failed!!!' % node_ip)
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
        if id1 != id_16_0_0_52:
            raise Exception('%s id1 error!!!' % node_ip)
        if key1 != id_16_0_0_52:
            raise Exception('%s key1 error!!!' % node_ip)
        if ip_addresses1 != LDAP_IP:
            raise Exception('%s ip_addresses1 error!!!' % node_ip)
        if port1 != 389:
            raise Exception('%s port1 error!!!' % node_ip)
        if type1 != "LDAP":
            raise Exception('%s type1 error!!!' % node_ip)

        """
        3.验证auth_provider_ldap是否可以连接
        """
        log.info("\t[step3 check_auth_provider ]")
        cmd = "check_auth_provider"
        check_result2 = nas_common.check_auth_provider(provider_id=id_16_0_0_52)
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
    delete_ldap_num = len(ldap_id_16_0_0_52_list)
    for j in range(0, delete_ldap_num):
        m = ldap_id_16_0_0_52_list[j]
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
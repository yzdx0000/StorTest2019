# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-05-25
# @summary：
# 16-0-0-101         规格极限情况下认证服务器的连接
# @steps:
# case1、创建128个ad认证；
# case2、创建128个ldap认证；
# case3、创建128个ad认证；
# case4、删除创建的认证；
# @changelog：
#
#######################################################
import os
import commands
import utils_path
import common
import get_config
import log
import nas_common
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)              # /mnt/volume/nas/nas_16_0_0_101
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：创建128个ad认证；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：创建128个ad认证；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#  1> add_auth_provider_ad
#  2> get_auth_providers_ad
#  3> check_auth_provider
#######################################################
def executing_case1():
    '''1> add_auth_provider_ad '''
    log.info("\t[case1 add_auth_provider_ad 128]")
    global ad_id_16_0_0_101_list
    ad_id_16_0_0_101_list = []
    check_result = nas_common.get_auth_providers_ad()
    ad_provider_num = check_result["result"]["total"]
    check_result = nas_common.get_auth_providers_ldap()
    ldap_provider_num = check_result["result"]["total"]
    check_result = nas_common.get_auth_providers_nis()
    nis_provider_num = check_result["result"]["total"]
    global pre_provider_num
    pre_provider_num = ad_provider_num + ldap_provider_num + nis_provider_num
    for i in range(ad_provider_num + 1, 129):
        log.info("\t[case1-1 add_auth_provider_ad %s]" % i)
        global ad_name
        ad_name = "nas_16_0_0_101_ad_%s" % i
        cmd = "add_auth_provider_ad "
        check_result2 = nas_common.add_auth_provider_ad(name=ad_name,
                                                        domain_name=nas_common.AD_DOMAIN_NAME,
                                                        dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                                        username=nas_common.AD_USER_NAME,
                                                        password=nas_common.AD_PASSWORD,
                                                        services_for_unix="NONE",
                                                        unix_id_range="%s-%s" % ((i + 1) * 1000,
                                                                                ((i + 1) * 1000 + 499)),
                                                        other_unix_id_range="%s-%s" % (((i + 1) * 1000+500),
                                                                                ((i + 1) * 1000 + 999)))
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s add_auth_provider_ad %s failed!!!' % (node_ip, i))
        global ad_id_16_0_0_101
        ad_id_16_0_0_101 = msg2["result"]
        ad_id_16_0_0_101_list.append(msg2["result"])

        '''2> get_auth_providers_ad'''
        log.info("\t[case1-2 get_auth_provider_ad %s]" % (i))
        cmd = "get_auth_providers_ad "
        check_result2 = nas_common.get_auth_providers_ad(ids=ad_id_16_0_0_101)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s get_auth_providers_ad %s failed!!!' % (node_ip, i))
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
        if id != ad_id_16_0_0_101:
            raise Exception('%s id error!!!' % node_ip)
        if key != ad_id_16_0_0_101:
            raise Exception('%s key error!!!' % node_ip)
        if name != ad_name:
            raise Exception('%s name error!!!' % node_ip)
        if services_for_unix != "NONE":
            raise Exception('%s services_for_unix error!!!' % node_ip)
        if type != "AD":
            raise Exception('%s type error!!!' % node_ip)
        if unix_id_range != [
                    (i+1)*1000,
                    ((i+1)*1000+499)
                ]:
            raise Exception('%s unix_id_range error!!!' % node_ip)
        if username != "administrator":
            raise Exception('%s username error!!!' % node_ip)

        '''3> check_auth_provider'''
        log.info("\t[case1-3 check_auth_provider AD %s]" % i)
        cmd = "check_auth_provider "
        check_result2 = nas_common.check_auth_provider(provider_id=ad_id_16_0_0_101)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s check_auth_provider ad %s failed!!!' % (node_ip, i))

    return


#######################################################
# 2.executing_case2
# @function：创建128个ldap认证；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：删除128 个ad认证，创建128个ldap认证；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> add_auth_provider_ldap
# 2> get_auth_providers_ldap
# 3> check_auth_provider
#######################################################
def executing_case2():

    '''1> add_auth_provider_ldap'''
    log.info("\t[case2-1 add_auth_provider_ldap 128]")
    global ldap_id_16_0_0_101_list
    ldap_id_16_0_0_101_list = []
    global LDAP_IP
    LDAP_IP = nas_common.LDAP_IP_ADDRESSES
    global LDAP_BASE_DN
    LDAP_BASE_DN = nas_common.LDAP_BASE_DN
    check_result = nas_common.get_auth_providers_ad()
    ad_provider_num = check_result["result"]["total"]
    check_result = nas_common.get_auth_providers_ldap()
    ldap_provider_num = check_result["result"]["total"]
    check_result = nas_common.get_auth_providers_nis()
    nis_provider_num = check_result["result"]["total"]
    global pre_provider_num
    pre_provider_num = ad_provider_num + ldap_provider_num + nis_provider_num
    for i in range(ldap_provider_num + 1, 129):
        log.info("\t[case2-2 add_auth_provider_ldap %s]" % i)
        global ldap_name
        ldap_name = "nas_16_0_0_101_ldap_%s" % i
        cmd = "add_auth_provider_ldap"
        check_result2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=LDAP_BASE_DN,
                                                          ip_addresses=LDAP_IP, port=389)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s add_auth_provider_ldap %s failed!!!' % (node_ip, i))
        global ldap_id_16_0_0_101
        ldap_id_16_0_0_101 = msg2["result"]
        ldap_id_16_0_0_101_list.append(msg2["result"])

        '''3> get_auth_providers_ldap'''
        log.info("\t[case2-3 get_auth_providers_ldap %s]" % i)
        cmd = "get_auth_providers_ldap "
        check_result2 = nas_common.get_auth_providers_ldap(ids=ldap_id_16_0_0_101)
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
        if id1 != ldap_id_16_0_0_101:
            raise Exception('%s id1 error!!!' % node_ip)
        if key1 != ldap_id_16_0_0_101:
            raise Exception('%s key1 error!!!' % node_ip)
        if ip_addresses1 != LDAP_IP:
            raise Exception('%s ip_addresses1 error!!!' % node_ip)
        if port1 != 389:
            raise Exception('%s port1 error!!!' % node_ip)
        if type1 != "LDAP":
            raise Exception('%s type1 error!!!' % node_ip)

        '''4> check_auth_provider'''
        log.info("\t[case2-4 check_auth_provider %s]" % i)
        cmd = "check_auth_provider"
        check_result2 = nas_common.check_auth_provider(provider_id=ldap_id_16_0_0_101)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s check_auth_provider %s failed!!!' % (node_ip, i))

    return


#######################################################
# 3.executing_case3
# @function：创建128个nis认证；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：删除128个ldap认证，创建128个ad认证；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> add_auth_provider_nis
# 2> get_auth_providers_nis
# 3> check_auth_provider
#######################################################
def executing_case3():
    '''1> add_auth_provider_nis'''
    log.info("\t[case3-1 add_auth_provider_nis 128]")
    global nis_id_16_0_0_101_list
    nis_id_16_0_0_101_list = []
    check_result = nas_common.get_auth_providers_ad()
    ad_provider_num = check_result["result"]["total"]
    check_result = nas_common.get_auth_providers_ldap()
    ldap_provider_num = check_result["result"]["total"]
    check_result = nas_common.get_auth_providers_nis()
    nis_provider_num = check_result["result"]["total"]
    global pre_provider_num
    pre_provider_num = ad_provider_num + ldap_provider_num + nis_provider_num
    for i in range(nis_provider_num + 1, 129):
        log.info("\t[case3-2 add_auth_provider_nis %s]" % i)
        global nis_name
        nis_name = "nas_16_0_0_101_nis_%s" % i
        cmd = "add_auth_provider_nis "
        check_result2 = nas_common.add_auth_provider_nis(name=nis_name,
                                                         domain_name=nas_common.NIS_DOMAIN_NAME,
                                                         ip_addresses=nas_common.NIS_IP_ADDRESSES)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s add_auth_provider_nis %s failed!!!' % (node_ip, i))
        global nis_id_16_0_0_101
        nis_id_16_0_0_101 = msg2["result"]
        nis_id_16_0_0_101_list.append(msg2["result"])

        '''3> get_auth_providers_ldap'''
        log.info("\t[case3-3 get_auth_providers_nis %s]" % i)
        cmd = "get_auth_providers_nis "
        check_result2 = nas_common.get_auth_providers_nis(ids=nis_id_16_0_0_101)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s get_auth_providers_nis %s failed!!!' % (node_ip, i))
        domain_name = msg2["result"]["auth_providers"][0]["domain_name"]
        id = msg2["result"]["auth_providers"][0]["id"]
        key = msg2["result"]["auth_providers"][0]["key"]
        ip_addresses = msg2["result"]["auth_providers"][0]["ip_addresses"][0]
        name = msg2["result"]["auth_providers"][0]["name"]
        type = msg2["result"]["auth_providers"][0]["type"]
        if domain_name != "nistest":
            raise Exception('%s domain_name error!!!' % node_ip)
        if id != nis_id_16_0_0_101:
            raise Exception('%s id error!!!' % node_ip)
        if key != nis_id_16_0_0_101:
            raise Exception('%s key error!!!' % node_ip)
        if ip_addresses != "10.2.41.247":
            raise Exception('%s ip_addresses error!!!' % node_ip)
        if name != nis_name:
            raise Exception('%s name error!!!' % node_ip)
        if type != "NIS":
            raise Exception('%s type error!!!' % node_ip)

        '''4> check_auth_provider'''
        log.info("\t[case3-4 check_auth_provider %s]" % i)
        cmd = "check_auth_provider"
        check_result2 = nas_common.check_auth_provider(provider_id=nis_id_16_0_0_101)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s check_auth_provider %s failed!!!' % (node_ip, i))

    return


#######################################################
# 4.executing_case4
# @function：删除创建的认证；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：删除创建的认证；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> delete_auth_providers AD
# 2> delete_auth_providers ldap
# 3> delete_auth_providers nis
#######################################################
def executing_case4():
    '''1> delete_auth_providers AD'''
    log.info("\t[case4-1 delete_auth_providers AD]")
    delete_ad_num = len(ad_id_16_0_0_101_list)
    for j in range(0, delete_ad_num):
        m = ad_id_16_0_0_101_list[j]
        log.info("\t[case4-1 delete_auth_providers AD %s]" % m)
        cmd = "delete_auth_providers "
        check_result2 = nas_common.delete_auth_providers(ids=m)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s delete_auth_providers AD %s failed!!!' % (node_ip, m))

    '''2> delete_auth_providers AD'''
    log.info("\t[case4-2 delete_auth_providers ldap]")
    delete_ldap_num = len(ldap_id_16_0_0_101_list)
    for j in range(0, delete_ldap_num):
        m = ldap_id_16_0_0_101_list[j]
        log.info("\t[case4-2 delete_auth_providers ldap %s]" % m)
        cmd = "delete_auth_providers "
        check_result2 = nas_common.delete_auth_providers(ids=m)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s delete_auth_providers ldap %s failed!!!' % (node_ip, m))

    '''3> delete_auth_providers nis'''
    log.info("\t[case4-3 delete_auth_providers nis]")
    delete_nis_num = len(nis_id_16_0_0_101_list)
    for j in range(0, delete_nis_num):
        m = nis_id_16_0_0_101_list[j]
        log.info("\t[case4-3 delete_auth_providers nis %s]" % m)
        cmd = "delete_auth_providers "
        check_result2 = nas_common.delete_auth_providers(ids=m)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s delete_auth_providers nis %s failed!!!' % (node_ip, m))
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
    executing_case3()
    executing_case4()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
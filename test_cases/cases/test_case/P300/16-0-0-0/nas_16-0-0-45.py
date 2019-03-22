# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-04-18
# @summary：
# 16-0-0-45         LDAPIP错误连接测试
# @steps:
# case 1、集群添加ldap认证，输入错误的IP地址；
# pscli --command=add_auth_provider_ldap --name=ldap_test --ip_addresses=x.x.x.x --base_dn=dc=xxx,dc=com --port=389
# case2、通过命令pscli --command=get_auth_provider_ldap查看ldap认证配置信息是否正确；
# case3、通过命令行pscli --command=check_auth_provider --ids=x查看认证配置信息是否能够正确的连接ldap认证
# @changelog：
#
#######################################################
import os
import utils_path
import common
import nas_common
import log
import get_config
import prepare_clean


FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)              # /mnt/volume/nas/nas_16_0_0_39
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP
LDAP_IP = nas_common.LDAP_IP_ADDRESSES
LDAP_BASE_DN = nas_common.LDAP_BASE_DN


def executing_case1():
    """1、集群添加ldap认证，输入错误的IP地址"""
    log.info("\t[case1 add_auth_provider_ldap ]")
    msg2 = nas_common.add_auth_provider_ldap(name="nas_16_0_0_45_ldap", base_dn=LDAP_BASE_DN,
                                             ip_addresses="10.0.0.1", port=389)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s add_auth_provider_ldap failed!!!' % node_ip)
    id_16_0_0_45 = msg2["result"]

    """2、通过命令pscli --command=get_auth_provider_ldap查看ldap认证配置信息是否正确"""
    log.info("\t[case2 get_auth_providers_ldap ]")
    msg2 = nas_common.get_auth_providers_ldap(ids=id_16_0_0_45)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s get_auth_providers_ldap failed!!!' % node_ip)
    ip_addresses = msg2["result"]["auth_providers"][0]["ip_addresses"][0]
    name = msg2["result"]["auth_providers"][0]["name"]
    if ip_addresses != "10.0.0.1":
        raise Exception('%s ip_addresses error!!!' % node_ip)
    if name != "nas_16_0_0_45_ldap":
        raise Exception('%s name error!!!' % node_ip)

    """3、通过命令行pscli --command=check_auth_provider --ids=x查看认证配置信息是否能够正确的连接ldap认证"""
    log.info("\t[case3 check_auth_provider ]")
    auth_providers_ldap = nas_common.get_auth_providers_ldap(ids=id_16_0_0_45)
    id_id = auth_providers_ldap["result"]["auth_providers"][0]["id"]
    msg2 = nas_common.check_auth_provider(provider_id=id_id)
    if msg2["err_msg"] != "CONNECT_AUTH_PROVIDER_FAILED" or msg2["detail_err_msg"] == "":
        common.except_exit('%s check_auth_provider failed!!!' % node_ip)
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
    prepare_clean.nas_test_clean()
    log.info("（2）executing_case")
    executing_case1()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
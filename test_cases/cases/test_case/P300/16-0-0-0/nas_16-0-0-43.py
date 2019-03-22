# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-04-18
# @summary：
# 16-0-0-43       错误DN连接测试
# @steps:
# case 1、集群添加ldap认证，输入错误的DN号；
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
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)              # /mnt/volume/nas/nas_16_0_0_43
node_ip = get_config.get_parastor_ip()
LDAP_IP = nas_common.LDAP_IP_ADDRESSES
LDAP_BASE_DN = nas_common.LDAP_BASE_DN


def executing_case1():
    """1、集群添加ldap认证，输入错误的DN号"""
    log.info("\t[case1 add_auth_provider_ldap ]")
    msg2 = nas_common.add_auth_provider_ldap(name="nas_16_0_0_43_ldap", base_dn="dc=testtt,dc=com",
                                             ip_addresses=LDAP_IP, port=389)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s add_auth_provider_ldap failed!!!' % node_ip)
    id_16_0_0_43 = msg2["result"]

    """2、通过命令pscli - -command = get_auth_provider_ldap查看ldap认证配置信息是否正确"""
    log.info("\t[case2 get_auth_providers_ldap ]")
    msg2 = nas_common.get_auth_providers_ldap(ids=id_16_0_0_43)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s get_auth_providers_ldap failed!!!' % node_ip)
    name1 = msg2["result"]["auth_providers"][0]["name"]
    base_dn1 = msg2["result"]["auth_providers"][0]["base_dn"]
    id1 = msg2["result"]["auth_providers"][0]["id"]
    key1 = msg2["result"]["auth_providers"][0]["key"]
    ip_addresses1 = msg2["result"]["auth_providers"][0]["ip_addresses"][0]
    port1 = msg2["result"]["auth_providers"][0]["port"]
    type1 = msg2["result"]["auth_providers"][0]["type"]
    if name1 != "nas_16_0_0_43_ldap":
        raise Exception('%s name1 error!!!' % node_ip)
    if base_dn1 != "dc=testtt,dc=com":
        raise Exception('%s base_dn1 error!!!' % node_ip)
    if id1 != id_16_0_0_43:
        raise Exception('%s id1 error!!!' % node_ip)
    if key1 != id_16_0_0_43:
        raise Exception('%s key1 error!!!' % node_ip)
    if ip_addresses1 != LDAP_IP:
        raise Exception('%s ip_addresses1 error!!!' % node_ip)
    if port1 != 389:
        raise Exception('%s port1 error!!!' % node_ip)
    if type1 != "LDAP":
        raise Exception('%s type1 error!!!' % node_ip)

    """3、通过命令行pscli --command=check_auth_provider --ids=x查看认证配置信息是否能够正确的连接ldap认证"""
    log.info("\t[case3 check_auth_provider ]")
    auth_providers_ldap = nas_common.get_auth_providers_ldap(ids=id_16_0_0_43)
    id_id = auth_providers_ldap["result"]["auth_providers"][0]["id"]
    msg2 = nas_common.check_auth_provider(provider_id=id_id)
    if msg2["err_msg"] != "CONNECT_AUTH_PROVIDER_FAILED" or \
       msg2["detail_err_msg"].find("Connect to the authentication provider failed") == -1:
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
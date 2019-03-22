# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-04-18
# @summary：
# 16-0-0-42      认证服务重复检测
# @steps:
# case 1、集群添加第一个ldap认证，填写正确的IP地址、端口号和基准DN；
# pscli --command=add_auth_provider_ldap --name=ldap_test1 --ip_addresses=x.x.x.x --base_dn=dc=xxx,dc=com --port=389
# case2、集群添加第二个ldap认证，填写正确的IP地址、端口号和基准DN；
# pscli --command=add_auth_provider_ldap --name=ldap_test2 --ip_addresses=x.x.x.x --base_dn=dc=xxx,dc=com --port=389
# case3、通过命令pscli --command=get_auth_provider_ldap查看ldap认证配置信息是否正确；
# @changelog：
#
#######################################################
import os
import utils_path
import common
import get_config
import log
import nas_common
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)              # /mnt/volume/nas/nas_16_0_0_42
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP
LDAP_IP = nas_common.LDAP_IP_ADDRESSES
LDAP_BASE_DN = nas_common.LDAP_BASE_DN


def executing_case1():
    """1、集群添加第一个ldap认证，填写正确的IP地址、端口号和基准DN"""
    log.info("\t[1. add_auth_provider_ldap ]")
    msg2 = nas_common.add_auth_provider_ldap(name="nas_16_0_0_42_ldap1", base_dn=LDAP_BASE_DN,
                                             ip_addresses=LDAP_IP, port=389)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s add_auth_provider_ldap failed!!!' % node_ip)
    id_16_0_0_42_1 = msg2["result"]

    """2、集群添加第二个ldap认证，填写正确的IP地址、端口号和基准DN"""
    log.info("\t[2. add_auth_provider_ldap ]")
    msg2 = nas_common.add_auth_provider_ldap(name="nas_16_0_0_42_ldap2", base_dn=LDAP_BASE_DN,
                                             ip_addresses=LDAP_IP, port=389)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s add_auth_provider_ldap second failed!!!' % node_ip)
    id_16_0_0_42_2 = msg2["result"]

    """3、通过命令pscli --command=get_auth_provider_ldap查看ldap认证配置信息是否正确"""
    log.info("\t[3. get_auth_providers_ldap ]")
    msg2 = nas_common.get_auth_providers_ldap(ids=id_16_0_0_42_1)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s get_auth_providers_ldap failed!!!' % node_ip)
    name1 = msg2["result"]["auth_providers"][0]["name"]
    base_dn1 = msg2["result"]["auth_providers"][0]["base_dn"]
    id1 = msg2["result"]["auth_providers"][0]["id"]
    key1 = msg2["result"]["auth_providers"][0]["key"]
    ip_addresses1 = msg2["result"]["auth_providers"][0]["ip_addresses"][0]
    port1 = msg2["result"]["auth_providers"][0]["port"]
    type1 = msg2["result"]["auth_providers"][0]["type"]
    if name1 != "nas_16_0_0_42_ldap1":
        raise Exception('%s name1 error!!!' % node_ip)
    if base_dn1 != LDAP_BASE_DN:
        raise Exception('%s base_dn1 error!!!' % node_ip)
    if id1 != id_16_0_0_42_1:
        raise Exception('%s id1 error!!!' % node_ip)
    if key1 != id_16_0_0_42_1:
        raise Exception('%s key1 error!!!' % node_ip)
    if ip_addresses1 != LDAP_IP:
        raise Exception('%s ip_addresses1 error!!!' % node_ip)
    if port1 != 389:
        raise Exception('%s port1 error!!!' % node_ip)
    if type1 != "LDAP":
        raise Exception('%s type1 error!!!' % node_ip)

    msg2 = nas_common.get_auth_providers_ldap(ids=id_16_0_0_42_2)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s get_auth_providers_ldap failed!!!' % node_ip)
    name2 = msg2["result"]["auth_providers"][0]["name"]
    base_dn2 = msg2["result"]["auth_providers"][0]["base_dn"]
    id2 = msg2["result"]["auth_providers"][0]["id"]
    key2 = msg2["result"]["auth_providers"][0]["key"]
    ip_addresses2 = msg2["result"]["auth_providers"][0]["ip_addresses"][0]
    port2 = msg2["result"]["auth_providers"][0]["port"]
    type2 = msg2["result"]["auth_providers"][0]["type"]
    if name2 != "nas_16_0_0_42_ldap2":
        raise Exception('%s name2 error!!!' % node_ip)
    if base_dn2 != LDAP_BASE_DN:
        raise Exception('%s base_dn2 error!!!' % node_ip)
    if id2 != id_16_0_0_42_2:
        raise Exception('%s id2 error!!!' % node_ip)
    if key2 != id_16_0_0_42_2:
        raise Exception('%s key2 error!!!' % node_ip)
    if ip_addresses2 != LDAP_IP:
        raise Exception('%s ip_addresses2 error!!!' % node_ip)
    if port2 != 389:
        raise Exception('%s port2 error!!!' % node_ip)
    if type2 != "LDAP":
        raise Exception('%s type2 error!!!' % node_ip)
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
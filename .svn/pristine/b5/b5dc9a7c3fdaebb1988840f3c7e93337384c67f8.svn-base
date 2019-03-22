# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-04-17
# @summary：
# 16-0-0-37     正常连接LDAP认证服务器
# @steps:
# 1> 集群添加ldap认证服务器，填写正确的IP地址、端口号和基准DN；
# pscli --command=add_auth_provider_ldap --name=ldap_test --ip_addresses=x.x.x.x --base_dn=dc=xxx,dc=com --port=389
# 2> 通过命令pscli --command=get_auth_providers_ldap查看ldap认证服务器配置信息是否正确；
# 3> 通过命令行pscli --command=check_auth_provider_ldap --ids=x查看认证配置信息是否能够正确的连接ldap认证服务器；
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
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)              # /mnt/volume/nas/nas_16_0_0_37
node_ip = get_config.get_parastor_ip()
LDAP_IP = nas_common.LDAP_IP_ADDRESSES
LDAP_BASE_DN = nas_common.LDAP_BASE_DN


def executing_case1():
    """1> 集群添加ldap认证服务器，填写正确的IP地址、端口号和基准DN"""
    log.info("\t[1.add_auth_provider_ldap ]")
    msg2 = nas_common.add_auth_provider_ldap(name="nas_16_0_0_37_ldap",
                                             base_dn=LDAP_BASE_DN,
                                             ip_addresses=LDAP_IP,
                                             port=389)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s create_file failed!!!' % node_ip)
    id_16_0_0_37 = msg2["result"]

    """ 2> 通过命令pscli --command=get_auth_providers_ldap查看ldap认证服务器配置信息是否正确 """
    log.info("\t[2.get_auth_providers_ldap ]")
    msg2 = nas_common.get_auth_providers_ldap(ids=id_16_0_0_37)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s get_auth_providers_ldap failed!!!' % node_ip)
    base_dn = msg2["result"]["auth_providers"][0]["base_dn"]
    ip_addresses = msg2["result"]["auth_providers"][0]["ip_addresses"][0]
    name = msg2["result"]["auth_providers"][0]["name"]
    port = msg2["result"]["auth_providers"][0]["port"]
    typee = msg2["result"]["auth_providers"][0]["type"]
    if base_dn != LDAP_BASE_DN:
        raise Exception('%s base_dn Error!!!' % node_ip)
    if ip_addresses != LDAP_IP:
        raise Exception('%s ip_addresses Error!!!' % node_ip)
    if name != "nas_16_0_0_37_ldap":
        raise Exception('%s name Error!!!' % node_ip)
    if port != 389:
        raise Exception('%s port Error!!!' % node_ip)
    if typee != "LDAP":
        raise Exception('%s type Error!!!' % node_ip)

    """ 3> 通过命令行pscli --command=check_auth_provider_ldap --ids=x查看认证配置信息是否能够正确的连接ldap认证服务器"""
    log.info("\t[case3 check_auth_provider ]")
    msg2 = nas_common.check_auth_provider(provider_id=id_16_0_0_37)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
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


if __name__ == '__main__':
    common.case_main(nas_main)
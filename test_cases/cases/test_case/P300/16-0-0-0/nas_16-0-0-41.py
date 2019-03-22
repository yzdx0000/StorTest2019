# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-04-17
# @summary：
# 16-0-0-41      名称重复检测
# @steps:
# case 1、集群添加第一个ldap认证，填写正确的IP地址、端口号和基准DN；
# pscli --command=add_auth_provider_ldap --name=ldap_test --ip_addresses=x.x.x.x --base_dn=dc=xxx,dc=com --port=389
# case2、集群添加第二个ldap认证，填写正确的IP地址、端口号和基准DN；
# pscli --command=add_auth_provider_ldap --name=ldap_test --ip_addresses=x.x.x.x --base_dn=dc=xxx,dc=com --port=389
# case3、通过命令pscli --command=get_auth_provider_ldap查看ldap认证配置信息是否正确；
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
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)              # /mnt/volume/nas/nas_16_0_0_41
node_ip = get_config.get_parastor_ip()
LDAP_IP = nas_common.LDAP_IP_ADDRESSES
LDAP_BASE_DN = nas_common.LDAP_BASE_DN


def executing_case1():
    """1、集群添加第一个ldap认证，填写正确的IP地址、端口号和基准DN"""
    log.info("\t[1. add_auth_provider_ldap ]")
    msg2 = nas_common.add_auth_provider_ldap(name="nas_16_0_0_41_ldap", base_dn=LDAP_BASE_DN,
                                             ip_addresses=LDAP_IP, port=389)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s add_auth_provider_ldap failed!!!' % node_ip)

    """2、集群添加第二个ldap认证，填写正确的IP地址、端口号和基准DN"""
    log.info("\t[2. add_auth_provider_ldap ]")
    msg2 = nas_common.add_auth_provider_ldap(name="nas_16_0_0_41_ldap", base_dn=LDAP_BASE_DN,
                                             ip_addresses=LDAP_IP, port=389)
    if msg2["detail_err_msg"] != "Authentication provider name:nas_16_0_0_41_ldap already exist.":
        common.except_exit('%s add_auth_provider_ldap again failed!!!' % node_ip)

    """3、通过命令pscli --command=get_auth_provider_ldap查看ldap认证配置信息是否正确"""
    log.info("\t[3. get_auth_providers_ldap ]")
    msg2 = nas_common.get_auth_providers_ldap()
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s get_auth_providers_ldap failed!!!' % node_ip)
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
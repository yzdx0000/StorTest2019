# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-04-17
# @summary：
# 16-0-0-39      名称/域名的特殊字符测试
# @steps:
# 1、集群添加ldap认证，输入特殊字符的域名，观察是否配置是否可以下发成功；
# 2、通过命令pscli --command=get_auth_providers_ladp查看ldap认证配置信息是否正确；
# 3、集群添加ldap认证，输入特殊字符的名称，观察是否配置是否可以下发成功；
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
    """1、集群添加ldap认证，输入特殊字符的域名，观察是否配置是否可以下发成功"""
    log.info("\t[1. add_auth_provider_ldap ]")
    msg2 = nas_common.add_auth_provider_ldap(name="nas_16_0_0_39_ldap", base_dn='"dc=#test,dc=com"',
                                             ip_addresses=LDAP_IP, port=389)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"] != "LDAP base dn dc=#test,dc=com is invalid," \
                                                                          " format: xxx=yyy, separated by commas (,).":
        common.except_exit('%s create_file failed!!!' % node_ip)
    id_16_0_0_39 = msg2["result"]

    """ 2、通过命令pscli - -command = get_auth_providers_ladp查看ldap认证配置信息是否正确 """
    log.info("\t[2. get_auth_providers_ldap ]")
    msg2 = nas_common.get_auth_providers_ldap(ids=id_16_0_0_39)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s get_auth_providers_ldap failed!!!' % node_ip)

    """ 3、集群添加ldap认证，输入特殊字符的名称，观察是否配置是否可以下发成功 """
    log.info("\t[3. add_auth_provider_ldap ]")
    msg2 = nas_common.add_auth_provider_ldap(name="@nas_16_0_0_39_ldap", base_dn=LDAP_BASE_DN,
                                             ip_addresses=LDAP_IP, port=389)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"] == "":
        common.except_exit('%s create_file failed!!!' % node_ip)

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
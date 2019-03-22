# -*-coding:utf-8 -*
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

####################################################################################
#
# author liyi
# date 2018-07-21
# @summary：
#       添加ldap时，bind_password错误，查看连接是否会报错
# @steps:
#     1、添加ldap认证服务器，使bind_password错误(使用命令pscli --command=add_auth_provider_ldap)；
#     2、检测连接是否会报错(pscli --command=check_auth_provider)
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字


def case():
    # 1> 添加ldap认证服务器
    check_result = nas_common.add_auth_provider_ldap(name="LDAP_"+FILE_NAME,
                                                     base_dn=nas_common.LDAP_BASE_DN,
                                                     ip_addresses= nas_common.LDAP_IP_ADDRESSES,
                                                     port=389,
                                                     bind_dn=nas_common.LDAP_BIND_DN,
                                                     bind_password=222222,
                                                     domain_password=nas_common.LDAP_DOMAIN_PASSWORD,
                                                     user_search_path=nas_common.LDAP_USER_SEARCH_PATH,
                                                     group_search_path=nas_common.LDAP_GROUP_SEARCH_PATH)
    if check_result["detail_err_msg"] != "":
        log.info("add_auth_provider_ldap is failed!!")
    ldap_id = check_result["result"]

    # 2> 检测ldap认证服务连接可用性
    time.sleep(3)
    check_result = nas_common.check_auth_provider(ldap_id)
    """bind_password错误，预计检测不通过，如果通过此系统有bug"""
    if check_result["detail_err_msg"] == "":
         log.error("BUG:the bind_password is invalid,but add auth provider succeed!!")


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

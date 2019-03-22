# -*-coding:utf-8 -*
import os
import time
import random

import utils_path
import common
import nas_common
import log
import get_config
import prepare_clean

####################################################################################
#
# author liyi
# date 2018-07-23
# @summary：
#       添加ldap，ssh本机后执行获取信息命令是否成功
# @steps:
#     1、添加ldap认证服务器(使用命令pscli --command=add_auth_provider_ldap)；
#     2、检测认证(pscli --command=check_auth_provider)
#     3、NAS端获取ldap用户信息
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SYSTEM_IP = get_config.get_parastor_ip()


def case():
    """
    :return:
    """
    '''1>添加ldap认证服务器'''
    check_result = nas_common.add_auth_provider_ldap(name="nas_1419_ldap",
                                                     base_dn=nas_common.LDAP_BASE_DN,
                                                     ip_addresses=nas_common.LDAP_IP_ADDRESSES,
                                                     port=389,
                                                     user_search_path=nas_common.LDAP_USER_SEARCH_PATH,
                                                     group_search_path=nas_common.LDAP_GROUP_SEARCH_PATH)
    if check_result["detail_err_msg"] != "":
        common.except_exit("add_auth_provider_ldap failed!")
    ldap_id = check_result["result"]
    '''2>检测ldap认证'''
    wait_time1 = random.randint(2, 5)
    time.sleep(wait_time1)
    check_result = nas_common.check_auth_provider(ldap_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("check_auth_provider failed!")
    '''3>NAS端获取ldap用户信息'''
    stdout = nas_common.get_auth_providers_ldap(ids=ldap_id)
    common.judge_rc(stdout['err_no'], 0, "get_auth_providers_ldap failed!")


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    prepare_clean.nas_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

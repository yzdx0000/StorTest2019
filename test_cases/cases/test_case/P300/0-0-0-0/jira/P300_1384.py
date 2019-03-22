# -*-coding:utf-8 -*
import os
import time
import random
import utils_path
import common
import nas_common
import log
import get_config
import re
import prepare_clean

####################################################################################
#
# author 李一
# date 2018-07-30
# @summary：
#      查看是否能正确显示ldap服务器端的中文用户
# @steps:
#     1、添加ldap认证(使用命令pscli --command=add_auth_provider_ldap)；
#     2、查看认证配置信息是否能够正确的连接ldap认证服务器(使用命令pscli --command=check_auth_provider)；
#     3、检测在ldapserver端是否有中文用户
#     4、查看ldapserver端创建的中文用户是否可以正常显示(使用命令pscli --command=get_auth_user)；
# @changelog：
####################################################################################
system_ip = get_config.get_parastor_ip(0)
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')


def case():
    ldap_zh_user = "用户1"
    # 1> 添加ldap认证
    check_result = nas_common.add_auth_provider_ldap(name="LDAP_"+FILE_NAME,
                                                     base_dn=nas_common.LDAP_BASE_DN,
                                                     ip_addresses=nas_common.LDAP_IP_ADDRESSES,
                                                     port=389,
                                                     bind_dn=nas_common.LDAP_BIND_DN,
                                                     bind_password=nas_common.LDAP_BIND_PASSWORD,
                                                     domain_password=nas_common.LDAP_DOMAIN_PASSWORD,
                                                     user_search_path=nas_common.LDAP_USER_SEARCH_PATH,
                                                     group_search_path=nas_common.LDAP_GROUP_SEARCH_PATH)
    if check_result["detail_err_msg"] != "":
        raise Exception("add_auth_provider_ldap failed!!")
    ldap_id = check_result["result"]

    # 2> 查看认证配置信息是否能够正确的连接ldap认证服务器
    time.sleep(3)
    check_result = nas_common.check_auth_provider(ldap_id)
    if check_result["detail_err_msg"] != "":
        raise Exception("check_auth_provider failed!!")

    # 3> 检测在ldapserver端用户中是否有中文用户
    rc, check_result = nas_common.get_auth_users(auth_provider_id=ldap_id)
    auth_users = check_result["result"]["auth_users"]
    auth_users_list = []
    for auth_user in auth_users:
        auth_users_list.append(auth_user['name'])  # 生成用户名字列表
    ch_name_list = []
    for ch_name in auth_users_list:
        if contain_zh(ch_name):                       # 对auth_user_name_list中元素检查，是否有中文元素
            ch_name_list.append(ch_name)              # 如果存在中文元素，将这些中文元素放到列表中

    # 4> 查看ldapserver端创建的中文用户是否可以正常显示
    if ldap_zh_user in ch_name_list:                 # 判断ldap服务器上的用户是否在获取的中文列表中
        log.info("中文用户可以正常显示")
    else:
        log.error("BUG!!中文用户显示不正常！！！")
        raise Exception("%s Failed" % FILE_NAME)


def contain_zh(word):
    """
    :author:        liyi
    :date:          2018.7.30
    :description:   判断传入字符串是否包含中文
    :param word: 待判断字符串
    :return: True:包含中文  False:不包含中文
    """
    global zh_pattern
    match = zh_pattern.search(word)
    return match


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    prepare_clean.nas_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

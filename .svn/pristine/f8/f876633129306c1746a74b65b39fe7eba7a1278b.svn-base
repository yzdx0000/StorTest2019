# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-11-21
# @summary：
# x-x-x-x     用户/用户组，添加认证服务器，未被访问分区引用
# @steps:
# 1.创建ad，ldap，ldap-pdc，nis认证
# 2.查看对应认证服务器下的部分用户（NAS配置文件中存在的用户）是否存在，存在则认为通过
# @changelog：
#
#######################################################
import os
import time
import random

import utils_path
import common
import nas_common
import log
import get_config
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_4_104
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


def executing_case1():
    """1 创建认证"""
    auth_provider_id_list = []
    """a.创建ad认证"""
    log.info("\t[1 add_auth_provider_ad]")
    ad_name = "ad_auth_provider"
    msg2 = nas_common.add_auth_provider_ad(name=ad_name,
                                           domain_name=nas_common.AD_DOMAIN_NAME,
                                           dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                           username=nas_common.AD_USER_NAME,
                                           password=nas_common.AD_PASSWORD,
                                           services_for_unix="NONE")

    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("add_auth_provider_ad failed")
    ad_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(ad_auth_provider_id)

    """获取用户"""
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ad_auth_provider_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("get_auth_users failed")
    auth_users = msg2["result"]["auth_users"]
    ad_auth_user_list = []
    for auth_user in auth_users:
        ad_auth_user_list.append(auth_user["name"])
    if nas_common.AD_USER_1 not in ad_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.AD_USER_1)
    if nas_common.AD_USER_2 not in ad_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.AD_USER_2)
    if nas_common.AD_USER_3 not in ad_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.AD_USER_3)
    """获取用户组"""
    msg2 = nas_common.get_auth_groups(auth_provider_id=ad_auth_provider_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("get_auth_groups failed")
    auth_groups = msg2["result"]["auth_groups"]
    ad_auth_group_list = []
    for auth_group in auth_groups:
        ad_auth_group_list.append(auth_group["name"])
    if nas_common.AD_GROUP not in ad_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.AD_GROUP)

    """b.创建ldap认证"""
    log.info("\t[1 add_auth_provider_ldap]")
    ldap_name = "ldap_auth_provider"
    msg2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_BASE_DN,
                                             ip_addresses=nas_common.LDAP_IP_ADDRESSES, port=389)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("add_auth_provider_ldap failed")
    ldap_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(ldap_auth_provider_id)

    """获取用户"""
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ldap_auth_provider_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("get_auth_users failed")
    auth_users = msg2["result"]["auth_users"]
    ldap_auth_user_list = []
    for auth_user in auth_users:
        ldap_auth_user_list.append(auth_user["name"])
    if nas_common.LDAP_USER_1_NAME not in ldap_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.LDAP_USER_1_NAME)
    if nas_common.LDAP_USER_2_NAME not in ldap_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.LDAP_USER_2_NAME)
    if nas_common.LDAP_USER_3_NAME not in ldap_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.LDAP_USER_3_NAME)
    """获取用户组"""
    msg2 = nas_common.get_auth_groups(auth_provider_id=ldap_auth_provider_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("get_auth_groups failed")
    auth_groups = msg2["result"]["auth_groups"]
    ldap_auth_group_list = []
    for auth_group in auth_groups:
        ldap_auth_group_list.append(auth_group["name"])
    if nas_common.LDAP_GROUP_1_NAME not in ldap_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.LDAP_GROUP_1_NAME)
    if nas_common.LDAP_GROUP_2_NAME not in ldap_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.LDAP_GROUP_2_NAME)
    if nas_common.LDAP_GROUP_3_NAME not in ldap_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.LDAP_GROUP_3_NAME)

    """c.创建ldap_pdc认证"""
    log.info("\t[1 add_auth_provider_ldap_pdc]")
    ldap_name = "ldap_pdc_auth_provider"
    msg2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_2_BASE_DN,
                                             ip_addresses=nas_common.LDAP_2_IP_ADDRESSES, port=389,
                                             bind_dn=nas_common.LDAP_2_BIND_DN,
                                             bind_password=nas_common.LDAP_2_BIND_PASSWORD,
                                             domain_password=nas_common.LDAP_2_DOMAIN_PASSWORD,
                                             user_search_path=nas_common.LDAP_2_USER_SEARCH_PATH,
                                             group_search_path=nas_common.LDAP_2_GROUP_SEARCH_PATH)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("add_auth_provider_ldap_pdc failed")
    ldap_pdc_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(ldap_pdc_auth_provider_id)

    """获取用户"""
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ldap_pdc_auth_provider_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("get_auth_users failed")
    auth_users = msg2["result"]["auth_users"]
    ldap_pdc_auth_user_list = []
    for auth_user in auth_users:
        ldap_pdc_auth_user_list.append(auth_user["name"])
    if nas_common.LDAP_USER_1_NAME not in ldap_pdc_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.LDAP_USER_1_NAME)
    if nas_common.LDAP_2_USER_1_NAME not in ldap_pdc_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.LDAP_2_USER_1_NAME)
    """获取用户组"""
    msg2 = nas_common.get_auth_groups(auth_provider_id=ldap_pdc_auth_provider_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("get_auth_groups failed")
    auth_groups = msg2["result"]["auth_groups"]
    ldap_pdc_auth_group_list = []
    for auth_group in auth_groups:
        ldap_pdc_auth_group_list.append(auth_group["name"])
    if nas_common.LDAP_2_GROUP_1_NAME not in ldap_pdc_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.LDAP_2_GROUP_1_NAME)

    """d.创建nis认证"""
    log.info("\t[1 add_auth_provider_nis]")
    nis_name = "nis_auth_provider"
    msg2 = nas_common.add_auth_provider_nis(name=nis_name,
                                            domain_name=nas_common.NIS_DOMAIN_NAME,
                                            ip_addresses=nas_common.NIS_IP_ADDRESSES)

    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("add_auth_provider_nis failed")
    nis_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(nis_auth_provider_id)

    """获取用户"""
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=nis_auth_provider_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("get_auth_users failed")
    auth_users = msg2["result"]["auth_users"]
    nis_auth_user_list = []
    for auth_user in auth_users:
        nis_auth_user_list.append(auth_user["name"])
    if nas_common.NIS_USER_1 not in nis_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.NIS_USER_1)
    if nas_common.NIS_USER_2 not in nis_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.NIS_USER_2)
    """获取用户组"""
    msg2 = nas_common.get_auth_groups(auth_provider_id=nis_auth_provider_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("get_auth_groups failed")
    auth_groups = msg2["result"]["auth_groups"]
    nis_auth_group_list = []
    for auth_group in auth_groups:
        nis_auth_group_list.append(auth_group["name"])
    if nas_common.NIS_GROUP_1 not in nis_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.NIS_GROUP_1)
    if nas_common.NIS_GROUP_2 not in nis_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.NIS_GROUP_2)

    return


#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    executing_case1()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-11-27
# @summary：
# x-x-x-x     用户/用户组，修改认证服务器，未被访问分区引用
# @steps:
# 1.创建ad，ldap，ldap-pdc，nis认证
# 2.在步骤1中，
# ① 每创建一个认证，查看对应认证服务器下的部分用户（NAS配置文件中存在的用户）是否存在，存在则认为通过
# ② 修改认证服务器的参数到错误参数，获取用户/用户组预期失败
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
    get_ad_user_group(auth_provider_id=ad_auth_provider_id)
    """修改ad认证"""
    update_auth_provider_ad(ad_auth_provider_id=ad_auth_provider_id)

    """b.创建ldap认证"""
    log.info("\t[1 add_auth_provider_ldap]")
    ldap_name = "ldap_auth_provider"
    msg2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_BASE_DN,
                                             ip_addresses=nas_common.LDAP_IP_ADDRESSES, port=389)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("add_auth_provider_ldap failed")
    ldap_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(ldap_auth_provider_id)
    get_ldap_user_group(auth_provider_id=ldap_auth_provider_id)
    """修改ldap认证"""
    update_auth_provider_ldap(ldap_auth_provider_id=ldap_auth_provider_id)

    """c.创建ldap_pdc认证"""
    log.info("\t[1 add_auth_provider_ldap_pdc]")
    ldap_name = "ldap_pdc_auth_provider"
    msg2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_2_BASE_DN,
                                             ip_addresses=nas_common.LDAP_2_IP_ADDRESSES, port=389,
                                             bind_dn=nas_common.LDAP_2_BIND_DN,
                                             bind_password=nas_common.LDAP_2_BIND_PASSWORD,
                                             domain_password=nas_common.LDAP_2_DOMAIN_PASSWORD)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("add_auth_provider_ldap_pdc failed")
    ldap_pdc_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(ldap_pdc_auth_provider_id)
    get_ldap_pdc_user_group(auth_provider_id=ldap_pdc_auth_provider_id)
    """修改ldap_pdc认证"""
    update_auth_provider_ldap_pdc(ldap_pdc_auth_provider_id=ldap_pdc_auth_provider_id)

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
    get_nis_user_group(auth_provider_id=nis_auth_provider_id)
    """修改nis认证"""
    update_auth_provider_nis(nis_auth_provider_id=nis_auth_provider_id)

    return


def get_auth_users_list(auth_provider_id):
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=auth_provider_id, print_flag=False)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("get_auth_users failed")
    auth_users = msg2["result"]["auth_users"]
    first_auth_user_list = []
    for auth_user in auth_users:
        first_auth_user_list.append(auth_user["name"])
    return first_auth_user_list


def get_auth_groups_list(auth_provider_id):
    msg2 = nas_common.get_auth_groups(auth_provider_id=auth_provider_id, print_flag=False)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("get_auth_groups failed")
    auth_groups = msg2["result"]["auth_groups"]
    first_auth_group_list = []
    for auth_group in auth_groups:
        first_auth_group_list.append(auth_group["name"])
    return first_auth_group_list


def get_ad_user_group(auth_provider_id):
    """获取用户"""
    ad_auth_user_list = get_auth_users_list(auth_provider_id=auth_provider_id)
    if nas_common.AD_USER_1 not in ad_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.AD_USER_1)
    if nas_common.AD_USER_2 not in ad_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.AD_USER_2)
    if nas_common.AD_USER_3 not in ad_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.AD_USER_3)
    """获取用户组"""
    ad_auth_group_list = get_auth_groups_list(auth_provider_id=auth_provider_id)
    if nas_common.AD_GROUP not in ad_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.AD_GROUP)
    return


def get_ldap_user_group(auth_provider_id):
    """获取用户"""
    ldap_auth_user_list = get_auth_users_list(auth_provider_id=auth_provider_id)
    if nas_common.LDAP_USER_1_NAME not in ldap_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.LDAP_USER_1_NAME)
    if nas_common.LDAP_USER_2_NAME not in ldap_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.LDAP_USER_2_NAME)
    if nas_common.LDAP_USER_3_NAME not in ldap_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.LDAP_USER_3_NAME)
    """获取用户组"""
    ldap_auth_group_list = get_auth_groups_list(auth_provider_id=auth_provider_id)
    if nas_common.LDAP_GROUP_1_NAME not in ldap_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.LDAP_GROUP_1_NAME)
    if nas_common.LDAP_GROUP_2_NAME not in ldap_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.LDAP_GROUP_2_NAME)
    if nas_common.LDAP_GROUP_3_NAME not in ldap_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.LDAP_GROUP_3_NAME)
    return


def get_ldap_pdc_user_group(auth_provider_id):
    """获取用户"""
    ldap_pdc_auth_user_list = get_auth_users_list(auth_provider_id=auth_provider_id)
    if nas_common.LDAP_USER_1_NAME not in ldap_pdc_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.LDAP_USER_1_NAME)
    if nas_common.LDAP_2_USER_1_NAME not in ldap_pdc_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.LDAP_2_USER_1_NAME)
    """获取用户组"""
    ldap_pdc_auth_group_list = get_auth_groups_list(auth_provider_id=auth_provider_id)
    if nas_common.LDAP_2_GROUP_1_NAME not in ldap_pdc_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.LDAP_2_GROUP_1_NAME)
    return


def get_nis_user_group(auth_provider_id):
    """获取用户"""
    nis_auth_user_list = get_auth_users_list(auth_provider_id=auth_provider_id)
    if nas_common.NIS_USER_1 not in nis_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.NIS_USER_1)
    if nas_common.NIS_USER_2 not in nis_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.NIS_USER_2)
    """获取用户组"""
    nis_auth_group_list = get_auth_groups_list(auth_provider_id=auth_provider_id)
    if nas_common.NIS_GROUP_1 not in nis_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.NIS_GROUP_1)
    if nas_common.NIS_GROUP_2 not in nis_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.NIS_GROUP_2)
    return


def update_auth_provider_ad(ad_auth_provider_id):
    get_ad_user_list = get_auth_users_list(ad_auth_provider_id)
    get_ad_group_list = get_auth_groups_list(ad_auth_provider_id)
    log.info("\t[1 update_auth_provider_ad_name]")
    ad_name = "ad_auth_provider_update"
    msg2 = nas_common.update_auth_provider_ad(provider_id=ad_auth_provider_id, name=ad_name)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ad_name failed")
    get_ad_user_list_1 = get_auth_users_list(ad_auth_provider_id)
    if get_ad_user_list != get_ad_user_list_1:
        log.error("get_ad_user_list= %s, get_ad_user_list_1=%s" % (get_ad_user_list, get_ad_user_list_1))
        common.except_exit("update_auth_provider_ad name failed")
    get_ad_group_list_1 = get_auth_groups_list(ad_auth_provider_id)
    if get_ad_group_list != get_ad_group_list_1:
        log.error("get_ad_group_list= %s, get_ad_group_list_1=%s" % (get_ad_group_list, get_ad_group_list_1))
        common.except_exit("update_auth_provider_ad name failed")

    log.info("\t[1 update_auth_provider_ad_domain_name]")
    msg2 = nas_common.update_auth_provider_ad(provider_id=ad_auth_provider_id, domain_name="addtest")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ad_name failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ad_auth_provider_id)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("remaining name") == -1:
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_ad(provider_id=ad_auth_provider_id, domain_name=nas_common.AD_DOMAIN_NAME)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ad_name failed")

    log.info("\t[1 update_auth_provider_dns_addresses]")
    msg2 = nas_common.update_auth_provider_ad(provider_id=ad_auth_provider_id, dns_addresses="10.2.40.1")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ad_name failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ad_auth_provider_id, print_flag=False)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("remaining name") == -1:
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_ad(provider_id=ad_auth_provider_id,
                                              dns_addresses=nas_common.AD_DNS_ADDRESSES)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ad_name failed")

    log.info("\t[1 update_auth_provider_username]")
    msg2 = nas_common.update_auth_provider_ad(provider_id=ad_auth_provider_id, username="addtest_cucu")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ad_name failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ad_auth_provider_id, print_flag=False)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("AcceptSecurityContext") == -1:
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_ad(provider_id=ad_auth_provider_id, username=nas_common.AD_USER_NAME)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ad_name failed")

    log.info("\t[1 update_auth_provider_password]")
    msg2 = nas_common.update_auth_provider_ad(provider_id=ad_auth_provider_id, password="addtest_cucu")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ad_name failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ad_auth_provider_id, print_flag=False)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("AcceptSecurityContext") == -1:
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_ad(provider_id=ad_auth_provider_id, password=nas_common.AD_PASSWORD)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ad_name failed")
    return


def update_auth_provider_ldap(ldap_auth_provider_id):
    get_ldap_user_list = get_auth_users_list(ldap_auth_provider_id)
    get_ldap_group_list = get_auth_groups_list(ldap_auth_provider_id)
    log.info("\t[1 update_auth_provider_ldap_name]")
    ldap_name = "ldap_auth_provider_update"
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_auth_provider_id, name=ldap_name)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_name failed")
    get_ldap_user_list_1 = get_auth_users_list(ldap_auth_provider_id)
    if get_ldap_user_list != get_ldap_user_list_1:
        log.error("get_ldap_user_list= %s, get_ldap_user_list_1=%s" % (get_ldap_user_list, get_ldap_user_list_1))
        common.except_exit("update_auth_provider_ldap name failed")
    get_ldap_group_list_1 = get_auth_groups_list(ldap_auth_provider_id)
    if get_ldap_group_list != get_ldap_group_list_1:
        log.error("get_ldap_group_list= %s, get_ldap_group_list_1=%s" % (get_ldap_group_list, get_ldap_group_list_1))
        common.except_exit("update_auth_provider_ldap name failed")

    log.info("\t[1 update_auth_provider_base_dn]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_auth_provider_id, base_dn="dc=ddc,dc=ddc")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_base_dn failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ldap_auth_provider_id, print_flag=False)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("remaining name") == -1:
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_auth_provider_id, base_dn=nas_common.LDAP_BASE_DN)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_base_dn failed")

    log.info("\t[1 update_auth_provider_ip_addresses]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_auth_provider_id, ip_addresses="10.2.40.1")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_ip_addresses failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ldap_auth_provider_id, print_flag=False)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"] == "":
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_auth_provider_id,
                                                ip_addresses=nas_common.LDAP_IP_ADDRESSES)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_ip_addresses failed")

    log.info("\t[1 update_auth_provider_port]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_auth_provider_id, port=380)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_port failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ldap_auth_provider_id, print_flag=False)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("Connection refused") == -1:
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_auth_provider_id, port=389)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_port failed")

    log.info("\t[1 update_auth_provider_user_search_path]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_auth_provider_id,
                                                user_search_path="ou=People,dc=ddc,dc=com")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_user_search_path failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ldap_auth_provider_id, print_flag=False)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("remaining name") == -1:
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_auth_provider_id,
                                                user_search_path="")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_user_search_path failed")

    log.info("\t[1 update_auth_provider_group_search_path]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_auth_provider_id,
                                                group_search_path="ou=Group,dc=ddc,dc=com")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_group_search_path failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ldap_auth_provider_id, print_flag=False)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("remaining name") == -1:
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_auth_provider_id,
                                                group_search_path="")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_group_search_path failed")
    return


def update_auth_provider_ldap_pdc(ldap_pdc_auth_provider_id):
    get_ldap_pdc_user_list = get_auth_users_list(ldap_pdc_auth_provider_id)
    get_ldap_pdc_group_list = get_auth_groups_list(ldap_pdc_auth_provider_id)
    log.info("\t[1 update_auth_provider_ldap_pdc_name]")
    ldap_pdc_name = "ldap_pdc_auth_provider_update"
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id, name=ldap_pdc_name)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_name failed")
    get_ldap_pdc_user_list_1 = get_auth_users_list(ldap_pdc_auth_provider_id)
    if get_ldap_pdc_user_list != get_ldap_pdc_user_list_1:
        log.error("get_ldap_pdc_user_list= %s, get_ldap_pdc_user_list_1=%s"
                  % (get_ldap_pdc_user_list, get_ldap_pdc_user_list_1))
        common.except_exit("update_auth_provider_ldap_pdc name failed")
    get_ldap_pdc_group_list_1 = get_auth_groups_list(ldap_pdc_auth_provider_id)
    if get_ldap_pdc_group_list != get_ldap_pdc_group_list_1:
        log.error("get_ldap_pdc_group_list= %s, get_ldap_pdc_group_list_1=%s"
                  % (get_ldap_pdc_group_list, get_ldap_pdc_group_list_1))
        common.except_exit("update_auth_provider_ldap_pdc name failed")

    log.info("\t[1 update_auth_provider_base_dn]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id, base_dn="dc=ddc,dc=ddc")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_base_dn failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ldap_pdc_auth_provider_id, print_flag=False)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("remaining name") == -1:
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id,
                                                base_dn=nas_common.LDAP_2_BASE_DN)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_base_dn failed")

    log.info("\t[1 update_auth_provider_ip_addresses]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id, ip_addresses="10.2.40.1")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_ip_addresses failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ldap_pdc_auth_provider_id, print_flag=False)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("Invalid Credentials") == -1:
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id,
                                                ip_addresses=nas_common.LDAP_2_IP_ADDRESSES)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_ip_addresses failed")

    log.info("\t[1 update_auth_provider_port]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id, port=380)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_port failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ldap_pdc_auth_provider_id, print_flag=False)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("Connection refused") == -1:
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id, port=389)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_port failed")

    log.info("\t[1 update_auth_provider_bind_dn]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id,
                                                bind_dn="cn=manager,dc=ddc,dc=com")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_bind_dn failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ldap_pdc_auth_provider_id, print_flag=False)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("Invalid Credentials") == -1:
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id,
                                                bind_dn=nas_common.LDAP_2_BIND_DN)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_bind_dn failed")

    log.info("\t[1 update_auth_provider_bind_password]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id, bind_password="ddccom")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_bind_password failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ldap_pdc_auth_provider_id, print_flag=False)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("Invalid Credentials") == -1:
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id,
                                                bind_password=nas_common.LDAP_2_BIND_PASSWORD)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_bind_password failed")

    log.info("\t[1 update_auth_provider_domain_password]")
    # 有Bug jira PV-167
    # bug解了后 msg2["err_msg"] ！= "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("Invalid Credentials") != -1
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id, domain_password="ddccom")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_domain_password failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ldap_pdc_auth_provider_id, print_flag=False)
    # msg2 = common.json_loads(msg2)
    if msg2["err_msg"] == "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("Invalid Credentials") != -1:   # == -1
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id,
                                                domain_password=nas_common.LDAP_2_DOMAIN_PASSWORD)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_domain_password failed")

    log.info("\t[1 update_auth_provider_user_search_path]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id,
                                                user_search_path="ou=People,dc=ddc,dc=com")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_user_search_path failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ldap_pdc_auth_provider_id, print_flag=False)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("remaining name") == -1:
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id,
                                                user_search_path=nas_common.LDAP_2_USER_SEARCH_PATH)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_user_search_path failed")

    log.info("\t[1 update_auth_provider_group_search_path]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id,
                                                group_search_path="ou=Group,dc=ddc,dc=com")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_group_search_path failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ldap_pdc_auth_provider_id, print_flag=False)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("remaining name") == -1:
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id,
                                                group_search_path=nas_common.LDAP_2_GROUP_SEARCH_PATH)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_group_search_path failed")
    return


def update_auth_provider_nis(nis_auth_provider_id):
    get_nis_user_list = get_auth_users_list(nis_auth_provider_id)
    get_nis_group_list = get_auth_groups_list(nis_auth_provider_id)
    log.info("\t[1 update_auth_provider_nis_name]")
    nis_name = "nis_auth_provider_update"
    msg2 = nas_common.update_auth_provider_nis(provider_id=nis_auth_provider_id, name=nis_name)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_nis_name failed")
    get_nis_user_list_1 = get_auth_users_list(nis_auth_provider_id)
    if get_nis_user_list != get_nis_user_list_1:
        log.error("get_nis_user_list= %s, get_nis_user_list_1=%s"
                  % (get_nis_user_list, get_nis_user_list_1))
        common.except_exit("update_auth_provider_nis name failed")
    get_nis_group_list_1 = get_auth_groups_list(nis_auth_provider_id)
    if get_nis_group_list != get_nis_group_list_1:
        log.error("get_nis_group_list= %s, get_nis_group_list_1=%s"
                  % (get_nis_group_list, get_nis_group_list_1))
        common.except_exit("update_auth_provider_nis name failed")

    log.info("\t[1 update_auth_provider_domain_name]")
    msg2 = nas_common.update_auth_provider_nis(provider_id=nis_auth_provider_id, domain_name="nistestt")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_nis_domain_name failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=nis_auth_provider_id, print_flag=False)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("No such domain") == -1:
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_nis(provider_id=nis_auth_provider_id, domain_name=nas_common.NIS_DOMAIN_NAME)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_nis_domain_name failed")

    log.info("\t[1 update_auth_provider_ip_addresses]")
    msg2 = nas_common.update_auth_provider_nis(provider_id=nis_auth_provider_id, ip_addresses="10.2.40.1")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_nis_ip_addresses failed")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=nis_auth_provider_id, print_flag=False)
    msg2 = common.json_loads(msg2)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("not registered]") == -1:
        common.except_exit("get_auth_users failed")
    msg2 = nas_common.update_auth_provider_nis(provider_id=nis_auth_provider_id,
                                               ip_addresses=nas_common.NIS_IP_ADDRESSES)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_nis_ip_addresses failed")
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
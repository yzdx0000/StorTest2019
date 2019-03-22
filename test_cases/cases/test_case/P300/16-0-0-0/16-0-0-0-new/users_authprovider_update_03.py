# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-11-28
# @summary：
# x-x-x-x     用户/用户组，修改认证服务器，被enable的访问分区引用
# @steps:
# 1.创建ad，ldap，ldap-pdc，nis认证
# 2.在步骤1中，
# ① 每创建一个认证，创建访问分区，启动NAS
# ② 查看对应认证服务器下的部分用户（NAS配置文件中存在的用户）是否存在，存在则认为通过
# ③ 修改认证服务器的参数到错误参数，预期修改失败，使用认证服务器中的用户验证FTP功能
# ④ 关闭NAS，删除访问分区
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
    """创建访问分区"""
    access_zone_id, az_node_id = create_access_zone([ad_auth_provider_id])
    """启动NAS"""
    enable_nas(access_zone_id=access_zone_id)
    """修改ad认证"""
    update_auth_provider_ad(ad_auth_provider_id=ad_auth_provider_id)
    """验证FTP的功能"""
    ftp_id = random.choice(az_node_id)
    node = common.Node()
    ftp_ip = node.get_node_ip_by_id(node_id=ftp_id)
    ftp_export(access_zone_id=access_zone_id, node_ip=ftp_ip)
    """关闭NAS"""
    msg2 = nas_common.disable_nas(access_zone_id=access_zone_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("disable_nas failed")
    """删除访问分区"""
    msg2 = nas_common.delete_access_zone(access_zone_id=access_zone_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("delete_access_zone failed")

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
    """创建访问分区"""
    access_zone_id, az_node_id = create_access_zone([ldap_auth_provider_id])
    """启动NAS"""
    enable_nas(access_zone_id=access_zone_id)
    """修改ldap认证"""
    update_auth_provider_ldap(ldap_auth_provider_id=ldap_auth_provider_id)
    """验证FTP的功能"""
    ftp_id = random.choice(az_node_id)
    node = common.Node()
    ftp_ip = node.get_node_ip_by_id(node_id=ftp_id)
    ftp_export(access_zone_id=access_zone_id, node_ip=ftp_ip)
    """关闭NAS"""
    msg2 = nas_common.disable_nas(access_zone_id=access_zone_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("disable_nas failed")
    """删除访问分区"""
    msg2 = nas_common.delete_access_zone(access_zone_id=access_zone_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("delete_access_zone failed")

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
    """创建访问分区"""
    access_zone_id, az_node_id = create_access_zone([ldap_pdc_auth_provider_id])
    """启动NAS"""
    enable_nas(access_zone_id=access_zone_id)
    """修改ldap_pdc认证"""
    update_auth_provider_ldap_pdc(ldap_pdc_auth_provider_id=ldap_pdc_auth_provider_id)
    """验证FTP的功能"""
    ftp_id = random.choice(az_node_id)
    node = common.Node()
    ftp_ip = node.get_node_ip_by_id(node_id=ftp_id)
    ftp_export(access_zone_id=access_zone_id, node_ip=ftp_ip)
    """关闭NAS"""
    msg2 = nas_common.disable_nas(access_zone_id=access_zone_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("disable_nas failed")
    """删除访问分区"""
    msg2 = nas_common.delete_access_zone(access_zone_id=access_zone_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("delete_access_zone failed")

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
    """创建访问分区"""
    access_zone_id, az_node_id = create_access_zone([nis_auth_provider_id])
    """启动NAS"""
    enable_nas(access_zone_id=access_zone_id)
    """修改nis认证"""
    update_auth_provider_nis(nis_auth_provider_id=nis_auth_provider_id)
    """验证FTP的功能"""
    ftp_id = random.choice(az_node_id)
    node = common.Node()
    ftp_ip = node.get_node_ip_by_id(node_id=ftp_id)
    ftp_export(access_zone_id=access_zone_id, node_ip=ftp_ip)
    """关闭NAS"""
    msg2 = nas_common.disable_nas(access_zone_id=access_zone_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("disable_nas failed")
    """删除访问分区"""
    msg2 = nas_common.delete_access_zone(access_zone_id=access_zone_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("delete_access_zone failed")

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
    time.sleep(60)
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
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED" or \
       msg2["detail_err_msg"].find("Resource temporarily unavailable while getting initial credentials") == -1:
        common.except_exit("update_auth_provider_ad_domain_name failed")

    log.info("\t[1 update_auth_provider_ad_dns_addresses]")
    msg2 = nas_common.update_auth_provider_ad(provider_id=ad_auth_provider_id, dns_addresses="10.2.40.1")
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED" or \
       msg2["detail_err_msg"].find("Resource temporarily unavailable while getting initial credentials") == -1:
        common.except_exit("update_auth_provider_ad_dns_addresses failed")

    log.info("\t[1 update_auth_provider_ad_username]")
    msg2 = nas_common.update_auth_provider_ad(provider_id=ad_auth_provider_id, username="addtest_cucu")
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED" or \
       msg2["detail_err_msg"].find("not found in Kerberos database while getting initial credentials") == -1:
        common.except_exit("update_auth_provider_ad_username failed")

    log.info("\t[1 update_auth_provider_ad_password]")
    msg2 = nas_common.update_auth_provider_ad(provider_id=ad_auth_provider_id, password="addtest_cucu")
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED" or \
       msg2["detail_err_msg"].find("Password incorrect while getting initial credentials") == -1:
        common.except_exit("update_auth_provider_ad_password failed")

    time.sleep(60)
    get_ad_user_list_1 = get_auth_users_list(ad_auth_provider_id)
    if get_ad_user_list != get_ad_user_list_1:
        log.error("get_ad_user_list= %s, get_ad_user_list_1=%s" % (get_ad_user_list, get_ad_user_list_1))
        common.except_exit("update_auth_provider_ad name failed")
    get_ad_group_list_1 = get_auth_groups_list(ad_auth_provider_id)
    if get_ad_group_list != get_ad_group_list_1:
        log.error("get_ad_group_list= %s, get_ad_group_list_1=%s" % (get_ad_group_list, get_ad_group_list_1))
        common.except_exit("update_auth_provider_ad name failed")

    return


def update_auth_provider_ldap(ldap_auth_provider_id):
    get_ldap_user_list = get_auth_users_list(ldap_auth_provider_id)
    get_ldap_group_list = get_auth_groups_list(ldap_auth_provider_id)
    log.info("\t[1 update_auth_provider_ldap_name]")
    ldap_name = "ldap_auth_provider_update"
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_auth_provider_id, name=ldap_name)
    time.sleep(60)
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

    log.info("\t[1 update_auth_provider_ldap_base_dn]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_auth_provider_id, base_dn="dc=ddc,dc=ddc")
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED" or \
       msg2["detail_err_msg"].find("Authentication server search path is invalid") == -1:
        common.except_exit("update_auth_provider_ldap_base_dn failed")

    log.info("\t[1 update_auth_provider_ldap_ip_addresses]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_auth_provider_id, ip_addresses="10.2.40.1")
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED":
        common.except_exit("update_auth_provider_ldap_ip_addresses failed")
    # msg2["detail_err_msg"].find("Can't contact LDAP server") == -1         # 两种错误都可能出现
    # msg2["detail_err_msg"].find("Authentication server search path is invalid") == -1

    log.info("\t[1 update_auth_provider_ldap_port]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_auth_provider_id, port=380)
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED" or \
       msg2["detail_err_msg"].find("Can't contact LDAP server") == -1:
        common.except_exit("update_auth_provider_ldap_port failed")

    log.info("\t[1 update_auth_provider_ldap_user_search_path]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_auth_provider_id,
                                                user_search_path="ou=People,dc=ddc,dc=com")
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED" or\
       msg2["detail_err_msg"].find("Authentication server search path is invalid") == -1:
        common.except_exit("update_auth_provider_ldap_user_search_path failed")

    log.info("\t[1 update_auth_provider_ldap_group_search_path]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_auth_provider_id,
                                                group_search_path="ou=Group,dc=ddc,dc=com")
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED" or \
       msg2["detail_err_msg"].find("Authentication server search path is invalid") == -1:
        common.except_exit("update_auth_provider_ldap_group_search_path failed")

    time.sleep(60)
    get_ldap_user_list_1 = get_auth_users_list(ldap_auth_provider_id)
    if get_ldap_user_list != get_ldap_user_list_1:
        log.error("get_ldap_user_list= %s, get_ldap_user_list_1=%s" % (get_ldap_user_list, get_ldap_user_list_1))
        common.except_exit("update_auth_provider_ldap name failed")
    get_ldap_group_list_1 = get_auth_groups_list(ldap_auth_provider_id)
    if get_ldap_group_list != get_ldap_group_list_1:
        log.error("get_ldap_group_list= %s, get_ldap_group_list_1=%s" % (get_ldap_group_list, get_ldap_group_list_1))
        common.except_exit("update_auth_provider_ldap name failed")
    return


def update_auth_provider_ldap_pdc(ldap_pdc_auth_provider_id):
    get_ldap_pdc_user_list = get_auth_users_list(ldap_pdc_auth_provider_id)
    get_ldap_pdc_group_list = get_auth_groups_list(ldap_pdc_auth_provider_id)
    log.info("\t[1 update_auth_provider_ldap_pdc_name]")
    ldap_pdc_name = "ldap_pdc_auth_provider_update"
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id, name=ldap_pdc_name)
    time.sleep(60)
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

    log.info("\t[1 update_auth_provider_ldap_pdc_base_dn]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id, base_dn="dc=ddc,dc=ddc")
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED" or \
       msg2["detail_err_msg"].find("Authentication server search path is invalid") == -1:
        common.except_exit("update_auth_provider_ldap_pdc_base_dn failed")

    log.info("\t[1 update_auth_provider_ldap_pdc_ip_addresses]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id, ip_addresses="10.2.40.1")
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED":
        common.except_exit("update_auth_provider_ldap_pdc_ip_addresses failed")
    # msg2["detail_err_msg"].find("Invalid credentials") == -1      # 两种错误都可能出现
    # msg2["detail_err_msg"].find("Can't contact LDAP server") == -1

    log.info("\t[1 update_auth_provider_ldap_pdc_port]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id, port=380)
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED" or \
       msg2["detail_err_msg"].find("Can't contact LDAP server") == -1:
        common.except_exit("update_auth_provider_ldap_pdc_port failed")

    log.info("\t[1 update_auth_provider_ldap_pdc_bind_dn]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id,
                                                bind_dn="cn=manager,dc=ddc,dc=com")
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED" or \
       msg2["detail_err_msg"].find("auth:ldap_bind: Invalid credentials") == -1:
        common.except_exit("update_auth_provider_ldap_pdc_bind_dn failed")

    log.info("\t[1 update_auth_provider_ldap_pdc_bind_password]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id, bind_password="ddccom")
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED" or \
       msg2["detail_err_msg"].find("auth:ldap_bind: Invalid credentials") == -1:
        common.except_exit("update_auth_provider_ldap_pdc_bind_password failed")

    log.info("\t[1 update_auth_provider_ldap_pdc_domain_password]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id, domain_password="ddccom")
    # 有Bug jira PV-167
    # bug解了后 if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED" or msg2["detail_err_msg"].find("'net rpc join' failed") == -1:
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("update_auth_provider_ldap_pdc_domain_password failed")

    log.info("\t[1 update_auth_provider_ldap_pdc_user_search_path]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id,
                                                user_search_path="ou=People,dc=ddc,dc=com")
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED" or\
       msg2["detail_err_msg"].find("Authentication server search path is invalid") == -1:
        common.except_exit("update_auth_provider_ldap_pdc_user_search_path failed")

    log.info("\t[1 update_auth_provider_ldap_pdc_group_search_path]")
    msg2 = nas_common.update_auth_provider_ldap(provider_id=ldap_pdc_auth_provider_id,
                                                group_search_path="ou=Group,dc=ddc,dc=com")
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED" or\
       msg2["detail_err_msg"].find("Authentication server search path is invalid") == -1:
        common.except_exit("update_auth_provider_ldap_pdc_group_search_path failed")

    time.sleep(60)
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
    return


def update_auth_provider_nis(nis_auth_provider_id):
    time.sleep(10)
    get_nis_user_list = get_auth_users_list(nis_auth_provider_id)
    get_nis_group_list = get_auth_groups_list(nis_auth_provider_id)
    log.info("\t[1 update_auth_provider_nis_name]")
    nis_name = "nis_auth_provider_update"
    msg2 = nas_common.update_auth_provider_nis(provider_id=nis_auth_provider_id, name=nis_name)
    time.sleep(60)
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

    log.info("\t[1 update_auth_provider_nis_domain_name]")
    msg2 = nas_common.update_auth_provider_nis(provider_id=nis_auth_provider_id, domain_name="nistestt")
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED" or \
       msg2["detail_err_msg"].find("Can't communicate with ypbind") == -1:
        common.except_exit("update_auth_provider_nis_domain_name failed")

    log.info("\t[1 update_auth_provider_nis_ip_addresses]")
    msg2 = nas_common.update_auth_provider_nis(provider_id=nis_auth_provider_id, ip_addresses="10.2.40.1")
    if msg2["err_msg"] != "UPDATE_AUTH_PROVIDER_FAILED" or \
       msg2["detail_err_msg"].find("Can't communicate with ypbind") == -1:
        common.except_exit("update_auth_provider_nis_ip_addresses failed")

    time.sleep(60)
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
    return


def create_access_zone(auth_provider_id_list):
    log.info("\t[create_access_zone ]")
    node = common.Node()
    ids = node.get_nodes_id()
    num = len(ids)
    access_zone_name = "access_zone_first"
    az_auth_provider_id = random.choice(auth_provider_id_list)  # 随机选一种认证服务
    a = []
    for d in range(1, num + 1):
        a.append(d)
    node_id_num = random.choice(a)
    node_id_a = random.sample(ids, int(node_id_num))
    node_id = [str(p) for p in node_id_a]
    access_zone_node_ids = ','.join(node_id)  # 随机选取节点
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_ids, name=access_zone_name,
                                         auth_provider_id=az_auth_provider_id)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('create_access_zone failed!!!')
    access_zone_id = msg1["result"]
    time.sleep(10)

    return access_zone_id, node_id


def enable_nas(access_zone_id):
    log.info("\t[ enable_nas ]")
    protocol_types_list = ["NFS", "SMB"]
    protocol_types = ",".join(random.sample(protocol_types_list,
                                            random.choice(range(1, len(protocol_types_list) + 1)))) + ",FTP"
    msg2 = nas_common.enable_nas(access_zone_id=access_zone_id, protocol_types=protocol_types)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('enable_nas failed!!!')
    time.sleep(10)
    return


def ftp_export(access_zone_id, node_ip, d=0):
    # access_zone_id为访问分区的id，d为一个数字，为了区别路导出径名称
    log.info("\t[ 创建ftp导出 ]")
    """创建目录"""
    log.info("\t[ create_file ]")
    m = access_zone_id + d
    ftp_path = nas_common.ROOT_DIR + "ftp_dir_%s" % m
    nas_ftp_path = get_config.get_one_nas_test_path() + "/ftp_dir_%s" % m
    msg6 = nas_common.create_file(path=ftp_path, posix_permission="rwxr-xr-x")
    if msg6["err_msg"] != "" or msg6["detail_err_msg"] != "":
        common.except_exit('create_file failed!!!')

    """ 检查file是否创建成功"""
    log.info("\t[ get_file_list ]")
    msg7 = nas_common.get_file_list(path=ftp_path)
    if msg7["err_msg"] != "" or msg7["detail_err_msg"] != "":
        common.except_exit('get_file_list failed!!!')

    """创建导出路径"""
    log.info("\t[ create_ftp_export ]")
    msg = nas_common.get_access_zones(ids=access_zone_id)
    access_zone_type = msg["result"]["access_zones"][0]["auth_provider"]["type"]
    ftp_user_name = ""
    if access_zone_type == "LDAP":
        ftp_user_name = nas_common.LDAP_USER_1_NAME
    elif access_zone_type == "AD":
        ftp_user_name = nas_common.AD_USER_1
    elif access_zone_type == "NIS":
        ftp_user_name = nas_common.NIS_USER_1
    msg1 = nas_common.create_ftp_export(access_zone_id=access_zone_id, user_name=ftp_user_name, export_path=ftp_path,
                                        enable_upload="true")
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('create_ftp_export failed!!!')
    ftp_export_id = msg1["result"]

    """客户端上传文件"""
    log.info("\t[ FTP client put file ]")
    ftp_sh_file = "/root/ftp.file.sh"
    ftp_client_ip = nas_common.FTP_1_CLIENT_IP
    cmd = "echo "" > %s &&" \
          "echo '#!/bin/bash' >> %s &&" \
          "echo 'ftp -nv << EOF' >> %s &&" \
          "echo 'open %s' >> %s &&" \
          "echo 'user %s 111111' >> %s &&" \
          "echo 'prompt off' >> %s &&" \
          "echo 'put %s /ftp' >> %s &&" \
          "echo 'close' >> %s &&" \
          "echo 'bye' >> %s &&" \
          "echo 'EOF' >> %s &&" \
          "echo 'sleep 2' >> %s " % (ftp_sh_file, ftp_sh_file, ftp_sh_file, node_ip, ftp_sh_file, ftp_user_name,
                                     ftp_sh_file, ftp_sh_file, ftp_sh_file, ftp_sh_file, ftp_sh_file, ftp_sh_file,
                                     ftp_sh_file, ftp_sh_file)
    rc, stdout = common.run_command(ftp_client_ip, cmd)
    log.info(stdout)
    common.judge_rc(rc, 0, 'FTP client create file failed !!!')
    time.sleep(5)

    cmd = "sh %s" % ftp_sh_file
    rc, stdout = common.run_command(ftp_client_ip, cmd)
    common.judge_rc(rc, 0, 'FTP client %s put file failed !!!' % ftp_client_ip)

    """验证ftp文件是否上传成功"""
    log.info("\t[ FTP server check file ]")
    cmd = "cd %s && ls" % nas_ftp_path
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, 'FTP server %s check file failed !!!' % node_ip)
    if stdout == "":
        common.except_exit('FTP server %s can not find ftp file!!!' % node_ip)

    """FTP server删除文件"""
    log.info("\t[ FTP server delete file ]")
    cmd = "cd %s && rm -rf *" % nas_ftp_path
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, 'FTP server %s delete file failed !!!' % node_ip)

    """删除FTP导出"""
    log.info("\t[ delete_ftp_exports ]")
    msg1 = nas_common.delete_ftp_exports(ids=ftp_export_id)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('delete_ftp_export failed!!!')
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
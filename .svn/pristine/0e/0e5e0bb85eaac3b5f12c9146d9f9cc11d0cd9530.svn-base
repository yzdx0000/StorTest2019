# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-11-29
# @summary：
# x-x-x-x     用户/用户组，删除认证服务器，被disable的访问分区引用
# @steps:
# 1.创建ad，ldap，ldap-pdc，nis认证：每创建一种认证，创建一个访问分区引用认证，删除认证（预期失败），删除访问分区
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
    """a.创建ad认证"""
    auth_provider_id_list_ad = add_auth_provider_ad(m=1)   # 返回列表类型[1]
    """创建访问分区"""
    access_zone_id = create_access_zone(auth_provider_id_list_ad)
    """删除ad认证"""
    log.info("\t[1 delete_auth_providers_ad]")
    auth_provider_id = [str(p) for p in auth_provider_id_list_ad]
    auth_provider_id = ','.join(auth_provider_id)  # 将[1] 转换为 1
    msg2 = nas_common.delete_auth_providers(ids=auth_provider_id)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("is being used by access zone") == -1:
        common.except_exit("delete_auth_providers_ad failed")
    """删除访问分区"""
    msg2 = nas_common.delete_access_zone(access_zone_id=access_zone_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("delete_access_zone failed")

    """b.创建ldap认证"""
    auth_provider_id_list_ldap = add_auth_provider_ldap(m=1)  # 返回列表类型[1]
    """创建访问分区"""
    access_zone_id = create_access_zone(auth_provider_id_list_ldap)
    """删除ldap认证"""
    log.info("\t[1 delete_auth_providers_ldap]")
    auth_provider_id = [str(p) for p in auth_provider_id_list_ldap]
    auth_provider_id = ','.join(auth_provider_id)  # 将[1] 转换为 1
    msg2 = nas_common.delete_auth_providers(ids=auth_provider_id)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("is being used by access zone") == -1:
        common.except_exit("delete_auth_providers_ldap failed")
    """删除访问分区"""
    msg2 = nas_common.delete_access_zone(access_zone_id=access_zone_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("delete_access_zone failed")

    """c.创建ldap_pdc认证"""
    auth_provider_id_list_ldap_pdc = add_auth_provider_ldap_pdc(m=1)  # 返回列表类型[1]
    """创建访问分区"""
    access_zone_id = create_access_zone(auth_provider_id_list_ldap_pdc)
    """删除ldap_pdc认证"""
    log.info("\t[1 delete_auth_providers_ldap_pdc]")
    auth_provider_id = [str(p) for p in auth_provider_id_list_ldap_pdc]
    auth_provider_id = ','.join(auth_provider_id)  # 将[1] 转换为 1
    msg2 = nas_common.delete_auth_providers(ids=auth_provider_id)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("is being used by access zone") == -1:
        common.except_exit("delete_auth_providers_ldap_pdc failed")
    """删除访问分区"""
    msg2 = nas_common.delete_access_zone(access_zone_id=access_zone_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("delete_access_zone failed")

    """d.创建nis认证"""
    auth_provider_id_list_nis = add_auth_provider_nis(m=1)  # 返回列表类型[1]
    """创建访问分区"""
    access_zone_id = create_access_zone(auth_provider_id_list_nis)
    """删除nis认证"""
    log.info("\t[1 delete_auth_providers_nis]")
    auth_provider_id = [str(p) for p in auth_provider_id_list_nis]
    auth_provider_id = ','.join(auth_provider_id)  # 将[1] 转换为 1
    msg2 = nas_common.delete_auth_providers(ids=auth_provider_id)
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"].find("is being used by access zone") == -1:
        common.except_exit("delete_auth_providers_nis failed")
    """删除访问分区"""
    msg2 = nas_common.delete_access_zone(access_zone_id=access_zone_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("delete_access_zone failed")

    """删除所有的认证"""
    auth_provider_id_list = auth_provider_id_list_ad + auth_provider_id_list_ldap + auth_provider_id_list_ldap_pdc + \
                            auth_provider_id_list_nis
    auth_provider_id = [str(p) for p in auth_provider_id_list]
    auth_provider_id = ','.join(auth_provider_id)  # 将[1, 2, 3, 4, 5]转换为1,2,3,4,5
    msg2 = nas_common.delete_auth_providers(ids=auth_provider_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("delete_auth_providers_nis failed")

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


def add_auth_provider_ad(m):
    auth_provider_id_list = []
    for i in range(1, m+1):
        log.info("\t[1 add_auth_provider_ad %s/%s]" % (i, m))
        ad_name = "ad_auth_provider_%s" % i
        msg2 = nas_common.add_auth_provider_ad(name=ad_name,
                                               domain_name=nas_common.AD_DOMAIN_NAME,
                                               dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                               username=nas_common.AD_USER_NAME,
                                               password=nas_common.AD_PASSWORD,
                                               services_for_unix="NONE",
                                               )

        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("add_auth_provider_ad failed")
        ad_auth_provider_id = msg2["result"]
        get_ad_user_group(auth_provider_id=ad_auth_provider_id)
        auth_provider_id_list.append(ad_auth_provider_id)
    return auth_provider_id_list


def add_auth_provider_ldap(m):
    auth_provider_id_list = []
    for i in range(1, m+1):
        log.info("\t[1 add_auth_provider_ldap %s/%s]" % (i, m))
        ldap_name = "ldap_auth_provider_%s" % i
        msg2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_BASE_DN,
                                                 ip_addresses=nas_common.LDAP_IP_ADDRESSES, port=389)
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("add_auth_provider_ldap failed")
        ldap_auth_provider_id = msg2["result"]
        get_ldap_user_group(auth_provider_id=ldap_auth_provider_id)
        auth_provider_id_list.append(ldap_auth_provider_id)
    return auth_provider_id_list


def add_auth_provider_ldap_pdc(m):
    auth_provider_id_list = []
    for i in range(1, m+1):
        log.info("\t[1 add_auth_provider_ldap_pdc %s/%s]" % (i, m))
        ldap_name = "ldap_pdc_auth_provider_%s" % i
        msg2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_2_BASE_DN,
                                                 ip_addresses=nas_common.LDAP_2_IP_ADDRESSES, port=389,
                                                 bind_dn=nas_common.LDAP_2_BIND_DN,
                                                 bind_password=nas_common.LDAP_2_BIND_PASSWORD,
                                                 domain_password=nas_common.LDAP_2_DOMAIN_PASSWORD)
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("add_auth_provider_ldap_pdc failed")
        ldap_pdc_auth_provider_id = msg2["result"]
        get_ldap_pdc_user_group(auth_provider_id=ldap_pdc_auth_provider_id)
        auth_provider_id_list.append(ldap_pdc_auth_provider_id)
    return auth_provider_id_list


def add_auth_provider_nis(m):
    auth_provider_id_list = []
    for i in range(1, m+1):
        log.info("\t[1 add_auth_provider_nis %s/%s]" % (i, m))
        nis_name = "nis_auth_provider_%s" % i
        msg2 = nas_common.add_auth_provider_nis(name=nis_name,
                                                domain_name=nas_common.NIS_DOMAIN_NAME,
                                                ip_addresses=nas_common.NIS_IP_ADDRESSES)

        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("add_auth_provider_nis failed")
        nis_auth_provider_id = msg2["result"]
        get_nis_user_group(auth_provider_id=nis_auth_provider_id)
        auth_provider_id_list.append(nis_auth_provider_id)
    return auth_provider_id_list


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
    return access_zone_id


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
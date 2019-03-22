# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-11-29
# @summary：
# x-x-x-x     用户/用户组，删除认证服务器，未被访问分区引用
# @steps:
# 1.测试一个一个的删除认证服务器：创建ad，ldap，ldap-pdc，nis认证，每种1个，每创建1个删除1个
# 2.测试同种类型认证服务器的批量删除：创建ad，ldap，ldap-pdc，nis认证，每种n个,每种创建完n个，删除同种的n个
# 3.测试不同种类型认证服务器的批量删除：创建ad，ldap，ldap-pdc，nis认证，每种n个,全部创建完，一起删除
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
    number_of_same_type = 5     # 测试同种类型认证服务器的批量删除时，每种类型的认证服务器个数
    number_of_different_type = 2    # 测试不同种类型认证服务器的批量删除时，每种类型的认证服务器个数
    """1 测试一个一个的删除认证服务器"""
    log.info("\t[1 测试一个一个的删除认证服务器]")
    """a.创建ad认证"""
    auth_provider_id_list = add_auth_provider_ad(m=1)   # 返回列表类型[1]
    """删除ad认证"""
    log.info("\t[1 delete_auth_providers_ad]")
    auth_provider_id = [str(p) for p in auth_provider_id_list]
    auth_provider_id = ','.join(auth_provider_id)  # 将[1] 转换为 1
    msg2 = nas_common.delete_auth_providers(ids=auth_provider_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("delete_auth_providers_ad failed")

    """b.创建ldap认证"""
    auth_provider_id_list = add_auth_provider_ldap(m=1)  # 返回列表类型[1]
    """删除ldap认证"""
    log.info("\t[1 delete_auth_providers_ldap]")
    auth_provider_id = [str(p) for p in auth_provider_id_list]
    auth_provider_id = ','.join(auth_provider_id)  # 将[1] 转换为 1
    msg2 = nas_common.delete_auth_providers(ids=auth_provider_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("delete_auth_providers_ldap failed")

    """c.创建ldap_pdc认证"""
    auth_provider_id_list = add_auth_provider_ldap_pdc(m=1)  # 返回列表类型[1]
    """删除ldap_pdc认证"""
    log.info("\t[1 delete_auth_providers_ldap_pdc]")
    auth_provider_id = [str(p) for p in auth_provider_id_list]
    auth_provider_id = ','.join(auth_provider_id)  # 将[1] 转换为 1
    msg2 = nas_common.delete_auth_providers(ids=auth_provider_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("delete_auth_providers_ldap_pdc failed")

    """d.创建nis认证"""
    auth_provider_id_list = add_auth_provider_nis(m=1)  # 返回列表类型[1]
    """删除nis认证"""
    log.info("\t[1 delete_auth_providers_nis]")
    auth_provider_id = [str(p) for p in auth_provider_id_list]
    auth_provider_id = ','.join(auth_provider_id)  # 将[1] 转换为 1
    msg2 = nas_common.delete_auth_providers(ids=auth_provider_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("delete_auth_providers_nis failed")

    """2 测试同种类型认证服务器的批量删除"""
    log.info("\t[2 测试同种类型认证服务器的批量删除]")
    """a.创建ad认证"""
    auth_provider_id_list = add_auth_provider_ad(m=1)   # 返回列表类型[1, 2, 3, 4, 5]
    """删除ad认证"""
    log.info("\t[1 delete_auth_providers_ad]")
    auth_provider_id = [str(p) for p in auth_provider_id_list]
    auth_provider_id = ','.join(auth_provider_id)  # 将[1] 转换为 1
    msg2 = nas_common.delete_auth_providers(ids=auth_provider_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("delete_auth_providers_ad failed")

    """b.创建ldap认证"""
    auth_provider_id_list = add_auth_provider_ldap(m=number_of_same_type)  # 返回列表类型[1, 2, 3, 4, 5]
    """删除ldap认证"""
    log.info("\t[1 delete_auth_providers_ldap]")
    auth_provider_id = [str(p) for p in auth_provider_id_list]
    auth_provider_id = ','.join(auth_provider_id)  # 将[1, 2, 3, 4, 5]转换为1,2,3,4,5
    msg2 = nas_common.delete_auth_providers(ids=auth_provider_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("delete_auth_providers_ldap failed")

    """c.创建ldap_pdc认证"""
    auth_provider_id_list = add_auth_provider_ldap_pdc(m=number_of_same_type)  # 返回列表类型[1, 2, 3, 4, 5]
    """删除ldap_pdc认证"""
    log.info("\t[1 delete_auth_providers_ldap_pdc]")
    auth_provider_id = [str(p) for p in auth_provider_id_list]
    auth_provider_id = ','.join(auth_provider_id)  # 将[1, 2, 3, 4, 5]转换为1,2,3,4,5
    msg2 = nas_common.delete_auth_providers(ids=auth_provider_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("delete_auth_providers_ldap_pdc failed")

    """d.创建nis认证"""
    auth_provider_id_list = add_auth_provider_nis(m=number_of_same_type)  # 返回列表类型[1, 2, 3, 4, 5]
    """删除nis认证"""
    log.info("\t[1 delete_auth_providers_nis]")
    auth_provider_id = [str(p) for p in auth_provider_id_list]
    auth_provider_id = ','.join(auth_provider_id)  # 将[1, 2, 3, 4, 5]转换为1,2,3,4,5
    msg2 = nas_common.delete_auth_providers(ids=auth_provider_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("delete_auth_providers_nis failed")

    """3 测试不同种类型认证服务器的批量删除"""
    log.info("\t[3 测试不同种类型认证服务器的批量删除]")
    """a.创建ad认证"""
    auth_provider_id_list_ad = add_auth_provider_ad(m=1)   # 返回列表类型[1, 2, 3, 4, 5]
    """b.创建ldap认证"""
    auth_provider_id_list_ldap = add_auth_provider_ldap(m=number_of_different_type)  # 返回列表类型[1, 2, 3, 4, 5]
    """c.创建ldap_pdc认证"""
    auth_provider_id_list_ldap_pdc = add_auth_provider_ldap_pdc(m=number_of_different_type)  # 返回列表类型[1, 2, 3, 4, 5]
    """d.创建nis认证"""
    auth_provider_id_list_nis = add_auth_provider_nis(m=number_of_different_type)  # 返回列表类型[1, 2, 3, 4, 5]
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
        unix_id_range_list = [i*1000, i*1000+900]
        msg2 = nas_common.add_auth_provider_ad(name=ad_name,
                                               domain_name=nas_common.AD_DOMAIN_NAME,
                                               dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                               username=nas_common.AD_USER_NAME,
                                               password=nas_common.AD_PASSWORD,
                                               services_for_unix="NONE",
                                               unix_id_range="%s-%s" % (unix_id_range_list[0],
                                                                        unix_id_range_list[1]),
                                               other_unix_id_range="%s-%s" % (unix_id_range_list[1] + 1,
                                                                              unix_id_range_list[1] + 2)
                                               )

        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("add_auth_provider_ad failed")
        ad_auth_provider_id = msg2["result"]
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
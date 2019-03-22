# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-11-20
# @summary：
#   随机勾选"NFS", "SMB", "FTP"，并enable nas
# @steps:
#   1、随机使用认证服务器创建访问分区；
#   2、随机勾选"NFS", "SMB", "FTP"，并enable nas指定的次数（参数为COUNT）；
# @changelog：
#   None
######################################################

import os
import random

import utils_path
import log
import common
import nas_common
import prepare_clean

# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
COUNT = 30      # 随机勾选协议并enable nas的次数


def executing_case():
    """测试执行
    :return:无
    """
    log.info("（2）executing_case")

    """1 创建认证"""
    auth_provider_id_list = []
    """a.创建ad认证"""
    ad_name = "ad_auth_provider"
    msg = nas_common.add_auth_provider_ad(name=ad_name,
                                           domain_name=nas_common.AD_DOMAIN_NAME,
                                           dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                           username=nas_common.AD_USER_NAME,
                                           password=nas_common.AD_PASSWORD,
                                           services_for_unix="NONE")
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        common.except_exit("add_auth_provider_ad failed")
    ad_auth_provider_id = msg["result"]
    auth_provider_id_list.append(ad_auth_provider_id)

    """b.创建ldap认证"""
    ldap_name = "ldap_auth_provider"
    msg = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_BASE_DN,
                                             ip_addresses=nas_common.LDAP_IP_ADDRESSES, port=389)
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        common.except_exit("add_auth_provider_ldap failed")
    ldap_auth_provider_id = msg["result"]
    auth_provider_id_list.append(ldap_auth_provider_id)

    """c.创建ldap_pdc认证"""
    ldap_name = "ldap_pdc_auth_provider"
    msg = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_2_BASE_DN,
                                            ip_addresses=nas_common.LDAP_2_IP_ADDRESSES, port=389,
                                            bind_dn=nas_common.LDAP_2_BIND_DN,
                                            bind_password=nas_common.LDAP_2_BIND_PASSWORD,
                                            domain_password=nas_common.LDAP_2_DOMAIN_PASSWORD)
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        common.except_exit("add_auth_provider_ldap_pdc failed")
    ldap_pdc_auth_provider_id = msg["result"]
    auth_provider_id_list.append(ldap_pdc_auth_provider_id)

    """d.创建nis认证"""
    nis_name = "nis_auth_provider"
    msg = nas_common.add_auth_provider_nis(name=nis_name,
                                           domain_name=nas_common.NIS_DOMAIN_NAME,
                                           ip_addresses=nas_common.NIS_IP_ADDRESSES)
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        common.except_exit("add_auth_provider_nis failed")
    nis_auth_provider_id = msg["result"]
    auth_provider_id_list.append(nis_auth_provider_id)

    """2.创建访问分区，并enable nas"""
    access_zone_name = "access_zone"
    auth_provider_id = random.choice(auth_provider_id_list)
    access_zone_node_ids = nas_common.get_node_ids()
    msg = nas_common.create_access_zone(node_ids=access_zone_node_ids,
                                        name=access_zone_name,
                                        auth_provider_id=auth_provider_id)
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        common.except_exit('create_access_zone failed!!!')
    access_zone_id = msg["result"]

    for i in range(COUNT):
        log.info("count = %s" % int(i+1))
        protocol_types_list = ["NFS", "SMB", "FTP"]
        protocol_types = ",".join(random.sample(protocol_types_list,
                                                random.choice(range(1, len(protocol_types_list) + 1))))
        log.info(protocol_types)
        msg = nas_common.enable_nas(access_zone_id=access_zone_id, protocol_types=protocol_types)
        if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
            common.except_exit('enable_nas failed!!!')


def nas_main():
    """脚本入口函数
    :return:无
    """
    prepare_clean.nas_test_prepare(FILE_NAME)
    executing_case()
    if nas_common.DEBUG != 'on':
        prepare_clean.nas_test_clean()
    return


if __name__ == '__main__':
    common.case_main(nas_main)

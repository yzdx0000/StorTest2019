# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-08-07
# @summary：
# 16_0_2_8    3节点创建访问分区（AD认证）
# @steps:
# 1> 同步FTP
# 2> 创建AD认证
# 3> 使用AD认证创建访问分区
# 4> 获取访问分区信息
# 4.1获取本地认证id
# 4.2获取AD认证version
# 4.3获取访问分区信息
# @changelog：
#
#######################################################
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

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_13_0_0_0
node_ip = get_config.get_parastor_ip()

AD_IP = nas_common.AD_DNS_ADDRESSES
ad_name = "ad_16_0_2_8"
AD_DOMAIN_NAME = nas_common.AD_DOMAIN_NAME
AD_USER_NAME = nas_common.AD_USER_NAME
AD_PASSWORD = nas_common.AD_PASSWORD


def executing_case1():
    """ 1> 同步FTP"""
    log.info("\t[ 1.set_ntp ]")
    nas_common.set_ntp(is_enabled="true", ntp_servers=AD_IP)

    """ 2> 创建AD认证 """
    log.info("\t[ 2.add_auth_provider_ad ]")
    cmd = "add_auth_provider_ad "
    check_result4 = nas_common.add_auth_provider_ad(name=ad_name,
                                                    domain_name=AD_DOMAIN_NAME,
                                                    dns_addresses=AD_IP,
                                                    username=AD_USER_NAME,
                                                    password=AD_PASSWORD,
                                                    services_for_unix="NONE",
                                                    unix_id_range="%s-%s" % (1000, 1999))
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result4))
    msg4 = check_result4
    if msg4["err_msg"] != "" or msg4["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result4))
        raise Exception('%s add_auth_provider_ad failed!!!' % (node_ip))
    ad_id_16_0_2_8 = msg4["result"]

    """3> 使用AD认证创建访问分区"""
    log.info("\t[ 3.create_access_zone ]")
    access_zone_name = "access_zone_16_0_2_8"
    node = common.Node()
    ids = node.get_nodes_id()
    print ids
    access_zone_node_id_16_0_2_8 = ','.join(str(p) for p in ids)
    node_name_list = nas_common.get_node_name_list(ids)
    cmd = "create_access_zone"
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_2_8,
                                         name=access_zone_name,
                                         auth_provider_id=ad_id_16_0_2_8)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, msg1))
        raise Exception('%s create_access_zone failed!!!' % node_ip)
    access_zone_id = msg1["result"]

    """ 4> 查看访问分区信息 """
    log.info("\t[4.get_access_zones ]")
    """4.1获取本地认证id"""
    cmd = " get_auth_providers_local"
    check_result3 = nas_common.get_auth_providers_local()
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result3))
    auth_providers_local_id = check_result3["result"]["auth_providers"][0]["id"]
    if check_result3["detail_err_msg"] != "" or check_result3["err_msg"] != "":
        log.error('node_ip = %s, get_auth_providers_local failed' % node_ip)
        raise Exception('%s get_auth_providers_local failed!!!' % node_ip)

    """4.2获取AD认证version"""
    cmd = "get_auth_providers_ad "
    check_result3 = nas_common.get_auth_providers_ad(ids=ad_id_16_0_2_8)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result3))
    auth_providers_ad_version = check_result3["result"]["auth_providers"][0]["version"]
    if check_result3["detail_err_msg"] != "" or check_result3["err_msg"] != "":
        log.error('node_ip = %s, get_auth_providers_ad failed' % node_ip)
        raise Exception('%s get_auth_providers_ad failed!!!' % node_ip)

    """4.3获取访问分区信息"""
    cmd = "get_access_zones"
    check_result3 = nas_common.get_access_zones(ids=access_zone_id)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result3))
    access_zone_state = check_result3["result"]["access_zones"][0]["access_zone_state"]
    if access_zone_state != "ACCESSZONE_READY":
        log.error('node_ip = %s, %s = ACCESSZONE_READY' % (node_ip, access_zone_state))
        raise Exception('%s access_zone_state failed!!!' % node_ip)
    id = check_result3["result"]["access_zones"][0]["auth_provider"]["id"]
    if id != ad_id_16_0_2_8:
        log.error('node_ip = %s, %s = %s' % (node_ip, id, ad_id_16_0_2_8))
        raise Exception('%s auth_providers_local_id failed!!!' % node_ip)
    key = check_result3["result"]["access_zones"][0]["auth_provider"]["key"]
    if key != ad_id_16_0_2_8:
        log.error('node_ip = %s, %s = %s ' % (node_ip, key, ad_id_16_0_2_8))
        raise Exception('%s auth provider key failed!!!' % node_ip)
    name = check_result3["result"]["access_zones"][0]["auth_provider"]["name"]
    if name != ad_name:
        log.error('node_ip = %s, %s = %s' % (node_ip, name, ad_name))
        raise Exception('%s auth provider name failed!!!' % node_ip)
    type = check_result3["result"]["access_zones"][0]["auth_provider"]["type"]
    if type != "AD":
        log.error('node_ip = %s, %s = AD' % (node_ip, type))
        raise Exception('%s type failed!!!' % node_ip)
    version = check_result3["result"]["access_zones"][0]["auth_provider"]["version"]
    if version != auth_providers_ad_version:
        log.error('node_ip = %s, %s = %s' % (node_ip, version, auth_providers_ad_version))
        raise Exception('%s auth_providers_ad_version failed!!!' % node_ip)
    auth_provider_id = check_result3["result"]["access_zones"][0]["auth_provider_id"]
    if auth_provider_id != ad_id_16_0_2_8:
        log.error('node_ip = %s, %s = %s' % (node_ip, auth_provider_id, ad_id_16_0_2_8))
        raise Exception('%s auth_provider_id failed!!!' % node_ip)
    enable_ftp = check_result3["result"]["access_zones"][0]["enable_ftp"]
    if enable_ftp is not False:
        log.error('node_ip = %s, %s = False' % (node_ip, enable_ftp))
        raise Exception('%s enable_ftp failed!!!' % node_ip)
    enable_http = check_result3["result"]["access_zones"][0]["enable_http"]
    if enable_http is not False:
        log.error('node_ip = %s, %s = False' % (node_ip, enable_http))
        raise Exception('%s enable_http failed!!!' % node_ip)
    enable_nfs = check_result3["result"]["access_zones"][0]["enable_nfs"]
    if enable_nfs is not False:
        log.error('node_ip = %s, %s = False' % (node_ip, enable_nfs))
        raise Exception('%s enable_nfs failed!!!' % node_ip)
    enable_san = check_result3["result"]["access_zones"][0]["enable_san"]
    if enable_san is not False:
        log.error('node_ip = %s, %s = False' % (node_ip, enable_san))
        raise Exception('%s enable_san failed!!!' % node_ip)
    enable_smb = check_result3["result"]["access_zones"][0]["enable_smb"]
    if enable_smb is not False:
        log.error('node_ip = %s, %s = False' % (node_ip, enable_smb))
        raise Exception('%s enable_smb failed!!!' % node_ip)
    id = check_result3["result"]["access_zones"][0]["id"]
    if id != access_zone_id:
        log.error('node_ip = %s, %s = %s' % (node_ip, id, access_zone_id))
        raise Exception('%s access_zone_id failed!!!' % node_ip)
    key = check_result3["result"]["access_zones"][0]["key"]
    if key != access_zone_id:
        log.error('node_ip = %s, %s = %s' % (node_ip, key, access_zone_id))
        raise Exception('%s access_zone_key failed!!!' % node_ip)
    local_auth_provider_id = check_result3["result"]["access_zones"][0]["local_auth_provider_id"]
    if local_auth_provider_id != auth_providers_local_id:
        log.error('node_ip = %s, %s = %s' % (node_ip, local_auth_provider_id, auth_providers_local_id))
        raise Exception('%s local_auth_provider_id failed!!!' % node_ip)
    name = check_result3["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        log.error('node_ip = %s, %s = %s' % (node_ip, name, access_zone_name))
        raise Exception('%saccess_zone_name failed!!!' % node_ip)
    nas_service_enabled = check_result3["result"]["access_zones"][0]["nas_service_enabled"]
    if nas_service_enabled is not False:
        log.error('node_ip = %s, %s = False' % (node_ip, nas_service_enabled))
        raise Exception('%s nas_service_enabled failed!!!' % node_ip)
    node_ids = check_result3["result"]["access_zones"][0]["node_ids"]
    if node_ids != ids:
        log.error('node_ip = %s, %s = %s' % (node_ip, node_ids, ids))
        raise Exception('%s node_ids failed!!!' % node_ip)
    for i in range(0, len(ids)):
        managernode = check_result3["result"]["access_zones"][0]["nodes"][i]["managerNode"]
        if managernode is not False:
            log.error('node_ip = %s, %s = False' % (node_ip, managernode))
            raise Exception('%s managernode failed!!!' % node_ip)
        node_id = check_result3["result"]["access_zones"][0]["nodes"][i]["node_id"]
        if node_id != ids[i]:
            log.error('node_ip = %s, %s = %s' % (node_ip, node_id, ids[i]))
            raise Exception('%s node_id failed!!!' % node_ip)
        node_name = check_result3["result"]["access_zones"][0]["nodes"][i]["node_name"]
        if node_name != node_name_list[i]:
            log.error('node_ip = %s, %s = %s' % (node_ip, node_name, node_name_list[i]))
            raise Exception('%s node_name failed!!!' % node_ip)
    san_protocol_state = check_result3["result"]["access_zones"][0]["san_protocol_state"]
    if san_protocol_state != "ISCSI_UNKNOWN":
        log.error('node_ip = %s, %s = ISCSI_UNKNOWN' % (node_ip, san_protocol_state))
        raise Exception('%s san_protocol_state failed!!!' % node_ip)
    version = check_result3["result"]["access_zones"][0]["version"]
    if version != 0:
        log.error('node_ip = %s, %s = 0' % (node_ip, version))
        raise Exception('%s version failed!!!' % node_ip)

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
    log.info("（2）executing_case")
    executing_case1()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)

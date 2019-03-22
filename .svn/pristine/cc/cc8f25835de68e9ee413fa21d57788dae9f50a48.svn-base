# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-23
# @summary：
# 16-0-1-15     用户组删除
# @steps:
# case1、删除本地用户组group1；
# pscli --command=delete_auth_groups --ids=x
# case2、查询删除后的本地用户组group1信息；
# pscli --command=get_auth_groups --auth_provider_id=x
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
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_1_15
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：删除本地用户组group1；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：删除本地用户组group1；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> 创建用户组group
# 2> 查看用户组group
# 3> 删除用户组group
#######################################################
def executing_case1():
    # 1> 创建访问分区
    log.info("\t[case1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_1_15"
    node = common.Node()
    ids = node.get_nodes_id()
    access_zone_node_id_16_0_1_15 = ','.join(str(p) for p in ids)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_1_15, name=access_zone_name)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s create_access_zone failed!!!' % node_ip)
    access_zone_id = msg1["result"]

    # 2> 启动NAS
    log.info("\t[ enable_nas ]")
    msg2 = nas_common.enable_nas(access_zone_id=access_zone_id, protocol_types="NFS")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s enable_nas failed!!!' % node_ip)

    # 3> 查看NAS是否按配置启动
    log.info("\t[ get_access_zones ]")
    check_result3 = nas_common.get_access_zones(ids=access_zone_id)
    name = check_result3["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        common.except_exit('%s enable_nas failed!!!' % node_ip)
    auth_provider_id_16_0_1_15 = check_result3["result"]["access_zones"][0]["auth_provider_id"]
    global auth_provider_id_16_0_1_15

    """ 1> 创建用户组group"""
    log.info("\t[case1 create_auth_group 1]")
    cmd = "create_auth_group "
    check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_15, name="group_16_0_1_15")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_auth_group 1 failed!!!' % node_ip)
    global primary_group_id_16_0_1_15
    primary_group_id_16_0_1_15 = msg2["result"]

    """2> 查看用户组group"""
    log.info("\t[case1 get_auth_groups ]")
    cmd = "get_auth_groups"
    check_result2 = nas_common.get_auth_groups(auth_provider_id=auth_provider_id_16_0_1_15)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_groups failed!!!' % node_ip)
    auth_groups=msg2["result"]["auth_groups"]
    d=len(auth_groups)-1
    group_id=msg2["result"]["auth_groups"][d]["id"]
    group_name=msg2["result"]["auth_groups"][d]["name"]
    if group_id != primary_group_id_16_0_1_15:
        raise Exception('%s group_id ERROR!!!' % node_ip)
    if group_name != "group_16_0_1_15":
        raise Exception('%s group_name ERROR!!!' % node_ip)

    """ 3> 删除用户组group"""
    log.info("\t[ delete_auth_groups ]")
    cmd = "delete_auth_groups"
    check_result2 = nas_common.delete_auth_groups(ids=primary_group_id_16_0_1_15)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s delete_auth_groups failed!!!' % node_ip)

    return


#######################################################
# 2.executing_case2
# @function：查询删除后的本地用户组group1信息；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：查询删除后的本地用户组group1信息；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#
#######################################################
def executing_case2():
    log.info("\t[case2 get_auth_groups ]")
    cmd = "get_auth_groups"
    check_result2 = nas_common.get_auth_groups(auth_provider_id=auth_provider_id_16_0_1_15)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_groups failed!!!' % node_ip)
    auth_groups=msg2["result"]["auth_groups"]
    if auth_groups != []:
        common.except_exit('%s delete_auth_groups failed!!!' % node_ip)
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
    executing_case2()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)

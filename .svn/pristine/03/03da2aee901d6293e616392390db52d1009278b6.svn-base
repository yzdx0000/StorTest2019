# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-23
# @summary：
# 16-0-1-6      用户查看
# @steps:
# case 1、查看本地用户信息；
# 1> 创建用户组group1
# 2> 创建用户组group2
# 3> 创建用户组group3
# 4> 创建用户user1
# 5> 查看用户user1
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
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_1_6
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


def executing_case1():
    # 1> 创建访问分区
    log.info("\t[case1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_1_6"
    node = common.Node()
    ids = node.get_nodes_id()
    access_zone_node_id_16_0_1_6 = ','.join(str(p) for p in ids)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_1_6, name=access_zone_name)
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
    auth_provider_id_16_0_1_6 = check_result3["result"]["access_zones"][0]["auth_provider_id"]
    global auth_provider_id_16_0_1_6

    """ 1> 创建用户组group1"""
    log.info("\t[case1 create_auth_group 1]")
    cmd = "create_auth_group "
    check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_6, name="group_16_0_1_6_1")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_auth_group 1 failed!!!' % node_ip)
    global primary_group_id_16_0_1_6_1
    primary_group_id_16_0_1_6_1 = msg2["result"]

    """ 2> 创建用户组group2"""
    log.info("\t[case1 create_auth_group 2 ]")
    cmd = "create_auth_group "
    check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_6, name="group_16_0_1_6_2")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_auth_group 2 failed!!!' % node_ip)
    global second_group_id_16_0_1_6_2
    second_group_id_16_0_1_6_2 = msg2["result"]

    """ 3> 创建用户组group3"""
    log.info("\t[case1 create_auth_group 3 ]")
    cmd = "create_auth_group "
    check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_6, name="group_16_0_1_6_3")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_auth_group 3 failed!!!' % node_ip)
    global second_group_id_16_0_1_6_3
    second_group_id_16_0_1_6_3 = msg2["result"]

    """ 4> 创建用户user1"""
    log.info("\t[ create_auth_user ]")
    second_group_id_16_0_1_6 = "%s,%s" % (second_group_id_16_0_1_6_2, second_group_id_16_0_1_6_3)
    print second_group_id_16_0_1_6
    cmd = "create_auth_user"
    check_result2 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_16_0_1_6,
                                                name="user_16_0_1_6", password='111111',
                                                primary_group_id=primary_group_id_16_0_1_6_1,
                                                secondary_group_ids=second_group_id_16_0_1_6,
                                                home_dir="/home/user_16_0_1_6")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_auth_user failed!!!' % node_ip)
    global user_id_16_0_1_6
    user_id_16_0_1_6 = msg2["result"]

    """ 5> 查看用户user1"""
    log.info("\t[get_auth_users ]")
    cmd = "get_auth_users "
    rc, check_result2 = nas_common.get_auth_users(auth_provider_id=auth_provider_id_16_0_1_6,
                                                  group_id=primary_group_id_16_0_1_6_1)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users failed!!!' % node_ip)
    home_dir = msg2["result"]["auth_users"][0]["home_dir"]
    id = msg2["result"]["auth_users"][0]["id"]
    name = msg2["result"]["auth_users"][0]["name"]
    primary_group_id = msg2["result"]["auth_users"][0]["primary_group_id"]
    primary_group_name = msg2["result"]["auth_users"][0]["primary_group_name"]
    secondary_group_ids_1 = msg2["result"]["auth_users"][0]["secondary_group_ids"][0]
    secondary_group_ids_2 = msg2["result"]["auth_users"][0]["secondary_group_ids"][1]
    secondary_groups_1_id = msg2["result"]["auth_users"][0]["secondary_groups"][0]["id"]
    secondary_groups_1_name = msg2["result"]["auth_users"][0]["secondary_groups"][0]["name"]
    secondary_groups_2_id = msg2["result"]["auth_users"][0]["secondary_groups"][1]["id"]
    secondary_groups_2_name = msg2["result"]["auth_users"][0]["secondary_groups"][1]["name"]
    if home_dir != "/home/user_16_0_1_6":
        raise Exception('%s home_dir Error!!!' % node_ip)
    if id != user_id_16_0_1_6:
        raise Exception('%s id Error!!!' % node_ip)
    if name != "user_16_0_1_6":
        raise Exception('%s name Error!!!' % node_ip)
    if primary_group_id != primary_group_id_16_0_1_6_1:
        raise Exception('%s primary_group_id Error!!!' % node_ip)
    if primary_group_name != "group_16_0_1_6_1":
        raise Exception('%s primary_group_name Error!!!' % node_ip)
    if secondary_group_ids_1 != second_group_id_16_0_1_6_2:
        raise Exception('%s second_group_id Error!!!' % node_ip)
    if secondary_group_ids_2 != second_group_id_16_0_1_6_3:
        raise Exception('%s second_group_id Error!!!' % node_ip)
    if secondary_groups_1_id != second_group_id_16_0_1_6_2:
        raise Exception('%s secondary_groups_1_id Error!!!' % node_ip)
    if secondary_groups_1_name != "group_16_0_1_6_2":
        raise Exception('%s secondary_groups_1_name Error!!!' % node_ip)
    if secondary_groups_2_id != second_group_id_16_0_1_6_3:
        raise Exception('%s secondary_groups_1_id Error!!!' % node_ip)
    if secondary_groups_2_name != "group_16_0_1_6_3":
        raise Exception('%s secondary_groups_1_name Error!!!' % node_ip)
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

# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-24
# @summary：
# 16-0-1-20      1个用户组有多个用户
# @steps:
# case1、创建本地用户组group1；
# case2、创建本地用户user1、user2、user3、user4、user5；
# case3、把本地用户user1、user2、user3、user4、user5分别添加到本地用户组group1；
# 注：步骤3通过修改用户附属组实现的；
# case4、查看修改结果是否正确；
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
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：创建本地用户组group1；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：创建本地用户组group1；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> 创建用户组group0
# 2>  创建用户组group1
#######################################################
def executing_case1():
    # 1> 创建访问分区
    log.info("\t[case1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_1_20"
    node = common.Node()
    ids = node.get_nodes_id()
    access_zone_node_id_16_0_1_20 = ','.join(str(p) for p in ids)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_1_20, name=access_zone_name)
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
    auth_provider_id_16_0_1_20 = check_result3["result"]["access_zones"][0]["auth_provider_id"]
    global auth_provider_id_16_0_1_20

    """ 1> 创建用户组group0"""
    log.info("\t[case1 create_auth_group 0]")
    cmd = "create_auth_group "
    check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_20, name="group_16_0_1_20_0")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_auth_group 0 failed!!!' % node_ip)
    global primary_group_id_16_0_1_20_0
    primary_group_id_16_0_1_20_0 = msg2["result"]

    """ 2> 创建用户组group1"""
    log.info("\t[case1 create_auth_group 1]")
    cmd = "create_auth_group"
    check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_20, name="group_16_0_1_20_1")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_auth_group 1 failed!!!' % node_ip)
    global primary_group_id_16_0_1_20_1
    primary_group_id_16_0_1_20_1 = msg2["result"]
    return


#######################################################
# 2.executing_case2
# @function：创建本地用户user1、user2、user3、user4、user5；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：创建本地用户user1、user2、user3、user4、user5；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> 创建本地用户user1
# 2> 创建本地用户user2
# 3> 创建本地用户user3
# 4> 创建本地用户user4
# 5> 创建本地用户user5
#######################################################
def executing_case2():
    """ 1> 创建本地用户user1"""
    log.info("\t[ create_auth_user 1 ]")
    check_result2 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_16_0_1_20,
                                                name="user_16_0_1_20_1", password='111111',
                                                primary_group_id=primary_group_id_16_0_1_20_0,
                                                home_dir="/home/user_16_0_1_20_1")
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s create_auth_user 1 failed!!!' % node_ip)
    global user_id_16_0_1_20_1
    user_id_16_0_1_20_1 = msg2["result"]

    """ 2> 创建本地用户user2"""
    log.info("\t[ create_auth_user 2 ]")
    check_result2 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_16_0_1_20,
                                                name="user_16_0_1_20_2", password='111111',
                                                primary_group_id=primary_group_id_16_0_1_20_0,
                                                home_dir="/home/user_16_0_1_20_2")
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s create_auth_user 2 failed!!!' % node_ip)
    global user_id_16_0_1_20_2
    user_id_16_0_1_20_2 = msg2["result"]

    """ 3> 创建本地用户user3"""
    log.info("\t[ create_auth_user 3 ]")
    check_result2 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_16_0_1_20,
                                                name="user_16_0_1_20_3", password='111111',
                                                primary_group_id=primary_group_id_16_0_1_20_0,
                                                home_dir="/home/user_16_0_1_20_3")
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s create_auth_user 3 failed!!!' % node_ip)
    global user_id_16_0_1_20_3
    user_id_16_0_1_20_3 = msg2["result"]

    """ 4> 创建本地用户user4"""
    log.info("\t[ create_auth_user 4 ]")
    check_result2 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_16_0_1_20,
                                                name="user_16_0_1_20_4", password='111111',
                                                primary_group_id=primary_group_id_16_0_1_20_0,
                                                home_dir="/home/user_16_0_1_20_4")
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s create_auth_user 4 failed!!!' % node_ip)
    global user_id_16_0_1_20_4
    user_id_16_0_1_20_4 = msg2["result"]

    """ 5> 创建本地用户user5"""
    log.info("\t[ create_auth_user 5 ]")
    check_result2 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_16_0_1_20,
                                                name="user_16_0_1_20_5", password='111111',
                                                primary_group_id=primary_group_id_16_0_1_20_0,
                                                home_dir="/home/user_16_0_1_20_5")
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s create_auth_user 5 failed!!!' % node_ip)
    global user_id_16_0_1_20_5
    user_id_16_0_1_20_5 = msg2["result"]

    return


#######################################################
# 3.executing_case3
# @function：把本地用户user1、user2、user3、user4、user5分别添加到本地用户组group1；
# 注：步骤3通过修改用户附属组实现的；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：把本地用户user1、user2、user3、user4、user5分别添加到本地用户组group1；
# 注：步骤3通过修改用户附属组实现的；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> 把本地用户user1添加到本地用户组group1；
# 2> 把本地用户user2添加到本地用户组group1；
# 3> 把本地用户user3添加到本地用户组group1；
# 4> 把本地用户user4添加到本地用户组group1；
# 5> 把本地用户user5添加到本地用户组group1；
#######################################################
def executing_case3():
    """1> 把本地用户user1添加到本地用户组group1；"""
    log.info("\t[case3 update_auth_user 1 ]")
    cmd = "update_auth_user "
    check_result1 = nas_common.update_auth_user(user_id=user_id_16_0_1_20_1, password="222222",
                                                primary_group_id=primary_group_id_16_0_1_20_1,
                                                secondary_group_ids=primary_group_id_16_0_1_20_0)
    log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s update_auth_user 1 failed!!!' % node_ip)

    """2> 把本地用户user2添加到本地用户组group1；"""
    log.info("\t[case3 update_auth_user 2 ]")
    cmd = "update_auth_user "
    check_result1 = nas_common.update_auth_user(user_id=user_id_16_0_1_20_2, password="222222",
                                                primary_group_id=primary_group_id_16_0_1_20_1,
                                                secondary_group_ids=primary_group_id_16_0_1_20_0)
    log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s update_auth_user 2 failed!!!' % node_ip)

    """3> 把本地用户user3添加到本地用户组group1；"""
    log.info("\t[case3 update_auth_user 3 ]")
    cmd = "update_auth_user "
    check_result1 = nas_common.update_auth_user(user_id=user_id_16_0_1_20_3, password="222222",
                                                primary_group_id=primary_group_id_16_0_1_20_1,
                                                secondary_group_ids=primary_group_id_16_0_1_20_0)
    log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s update_auth_user 3 failed!!!' % node_ip)

    """4> 把本地用户user4添加到本地用户组group1；"""
    log.info("\t[case3 update_auth_user 4 ]")
    cmd = "update_auth_user "
    check_result1 = nas_common.update_auth_user(user_id=user_id_16_0_1_20_4, password="222222",
                                                primary_group_id=primary_group_id_16_0_1_20_1,
                                                secondary_group_ids=primary_group_id_16_0_1_20_0)
    log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s update_auth_user 4 failed!!!' % node_ip)

    """5> 把本地用户user5添加到本地用户组group1；"""
    log.info("\t[case3 update_auth_user 5 ]")
    cmd = "update_auth_user"
    check_result1 = nas_common.update_auth_user(user_id=user_id_16_0_1_20_5, password="222222",
                                                primary_group_id=primary_group_id_16_0_1_20_1,
                                                secondary_group_ids=primary_group_id_16_0_1_20_0)
    log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s update_auth_user 5 failed!!!' % node_ip)
    return


#######################################################
# 4.executing_case4
# @function：查看修改结果是否正确
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：查看修改结果是否正确
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> get_auth_users
# 2> 判断信息是否正确
#######################################################
def executing_case4():
    # 1> get_auth_users
    log.info("\t[case4 get_auth_users ]")
    cmd = "get_auth_users "
    rc, check_result2 = nas_common.get_auth_users(auth_provider_id=auth_provider_id_16_0_1_20,
                                              group_id=primary_group_id_16_0_1_20_1)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users failed!!!' % node_ip)

    # 2> 判断信息是否正确
    auth_users1_name = msg2["result"]["auth_users"][0]["name"]
    auth_users1_group = msg2["result"]["auth_users"][0]["primary_group_name"]
    auth_users2_name = msg2["result"]["auth_users"][1]["name"]
    auth_users2_group = msg2["result"]["auth_users"][1]["primary_group_name"]
    auth_users3_name = msg2["result"]["auth_users"][2]["name"]
    auth_users3_group = msg2["result"]["auth_users"][2]["primary_group_name"]
    auth_users4_name = msg2["result"]["auth_users"][3]["name"]
    auth_users4_group = msg2["result"]["auth_users"][3]["primary_group_name"]
    auth_users5_name = msg2["result"]["auth_users"][4]["name"]
    auth_users5_group = msg2["result"]["auth_users"][4]["primary_group_name"]

    if auth_users1_name != "user_16_0_1_20_1":
        raise Exception('%s user1_name Error!!!' % node_ip)
    if auth_users1_group != "group_16_0_1_20_1":
        raise Exception('%s user1_group Error!!!' % node_ip)
    if auth_users2_name != "user_16_0_1_20_2":
        raise Exception('%s user2_name Error!!!' % node_ip)
    if auth_users2_group != "group_16_0_1_20_1":
        raise Exception('%s user2_group Error!!!' % node_ip)
    if auth_users3_name != "user_16_0_1_20_3":
        raise Exception('%s user1_name Error!!!' % node_ip)
    if auth_users3_group != "group_16_0_1_20_1":
        raise Exception('%s user3_group Error!!!' % node_ip)
    if auth_users4_name != "user_16_0_1_20_4":
        raise Exception('%s user4_name Error!!!' % node_ip)
    if auth_users4_group != "group_16_0_1_20_1":
        raise Exception('%s user4_group Error!!!' % node_ip)
    if auth_users5_name != "user_16_0_1_20_5":
        raise Exception('%s user5_name Error!!!' % node_ip)
    if auth_users5_group != "group_16_0_1_20_1":
        raise Exception('%s user5_group Error!!!' % node_ip)

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
    executing_case3()
    executing_case4()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
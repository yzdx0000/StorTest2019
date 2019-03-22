# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-24
# @summary：
# 16-0-1-25        创建/删除/创建100个用户，观察uid循环递增不重复
# @steps:
# case1、创建本地用户组group1；
# case2、创建2个删除1个用户，直到创建100个；观察这100个用户的uid
# case3、查看用户
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
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_1_25
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
# 1> 创建用户组group
#######################################################
def executing_case1():
    # 1> 创建访问分区
    log.info("\t[case1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_1_25"
    node = common.Node()
    ids = node.get_nodes_id()
    access_zone_node_id_16_0_1_25 = ','.join(str(p) for p in ids)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_1_25, name=access_zone_name)
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
    auth_provider_id_16_0_1_25 = check_result3["result"]["access_zones"][0]["auth_provider_id"]
    global auth_provider_id_16_0_1_25

    log.info("\t[case1 create_auth_group]")
    cmd = "create_auth_group"
    check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_25, name="group_16_0_1_25")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_auth_group failed!!!' % node_ip)
    global primary_group_id_16_0_1_25
    primary_group_id_16_0_1_25 = msg2["result"]

    return


#######################################################
# 2.executing_case2
# @function：创建2个删除1个用户，直到创建100个；观察这100个用户的uid；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：创建2个删除1个用户，直到创建100个；观察这100个用户的uid；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> 创建第一个用户
# 2> 创建第二个用户
# 3> 删除第一个用户
# 4> 比较用户的uid
#######################################################
def executing_case2():
    global user_id_16_0_1_25_delete_list
    user_id_16_0_1_25_delete_list = []
    user_id_16_0_1_25_list = []
    user_id_16_0_1_25_list.append(0)
    for i in range(1, 101):
        """1> 创建第一个用户"""
        log.info("\t[case2 create_auth_user %s 1]" % i)
        user_name = "user_16_0_1_25_%s_1" % i
        cmd = "create_auth_user "
        check_result2 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_16_0_1_25,
                                                    name=user_name, password='111111',
                                                    primary_group_id=primary_group_id_16_0_1_25,
                                                    home_dir="/home/user_16_0_1_25")
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('create_auth_user %s_1 failed!!!' % i)
        user_id_16_0_1_25_l = msg2["result"]

        """2> 创建第二个用户"""
        log.info("\t[case2 create_auth_user %s 2]" % i)
        user_name = "user_16_0_1_25_%s_2" % i
        cmd = "create_auth_user "
        check_result2 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_16_0_1_25,
                                                    name=user_name, password='111111',
                                                    primary_group_id=primary_group_id_16_0_1_25,
                                                    home_dir="/home/user_16_0_1_25")
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('create_auth_user %s_2 failed!!!' % i)
        user_id_16_0_1_25_list.append(msg2["result"])
        user_id_16_0_1_25_delete_list.append(msg2["result"])

        """3> 删除第一个用户"""
        log.info("\t[ delete_auth_user 1 ]")
        cmd = "delete_auth_users"
        check_result2 = nas_common.delete_auth_users(ids=user_id_16_0_1_25_l)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s delete_auth_user failed!!!' % node_ip)

        """4> 比较用户的uid"""
        a = user_id_16_0_1_25_list[i] - user_id_16_0_1_25_list[i-1]
        if a <= 0:
            log.error('user_id_16_0_1_25_list[%s] is ERROR' % i)
            raise Exception('user_id_16_0_1_25_list[%s] is ERROR' % i)
    return


#######################################################
# 3.executing_case3
# @function：查看用户
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：查看用户
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> get_auth_users
# 2>
#######################################################
def executing_case3():
    # 1> get_auth_users
    log.info("\t[case3 get_auth_users ]")
    cmd = "get_auth_users"
    rc, check_result2 = nas_common.get_auth_users(auth_provider_id=auth_provider_id_16_0_1_25,
                                              group_id=primary_group_id_16_0_1_25)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "" or msg2["result"]["auth_users"] == []:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users failed!!!' % node_ip)
    auth_users = msg2["result"]["auth_users"]
    d = len(auth_users)
    print d

    return


#######################################################
# @function：清理环境
# @parameter：
# @return：
# @steps:
#######################################################
def clearing_environment():
    log.info("（3）clearing_environment")
    log.info("（3）删除用户")
    user_id_16_0_1_25_delete = ','.join(str(p) for p in user_id_16_0_1_25_delete_list)
    cmd = "delete_auth_users"
    check_result2 = nas_common.delete_auth_users(ids=user_id_16_0_1_25_delete)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s delete_auth_users failed!!!' % node_ip)
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
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
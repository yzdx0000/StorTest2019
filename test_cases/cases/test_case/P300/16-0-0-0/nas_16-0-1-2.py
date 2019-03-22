# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-20
# @summary：
# 16-0-1-2     用户名边界测试
# @steps:
# case1、创建一个以字母开头的含数字和下划线的用户名长度超过31位的用户；
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
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_1_2
node_ip = get_config.get_parastor_ip()


#######################################################
# 1.executing_case1
# @function：创建一个以字母开头的含数字和下划线的用户名长度超过31位的用户；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：创建一个以字母开头的含数字和下划线的用户名长度超过31位的用户；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> 创建用户组group1
# 2> 创建用户user1
#######################################################
def executing_case1():
    # 1> 创建访问分区
    log.info("\t[case1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_1_2"
    node = common.Node()
    ids = node.get_nodes_id()
    access_zone_node_id_16_0_1_2 = ','.join(str(p) for p in ids)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_1_2, name=access_zone_name)
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
    auth_provider_id_16_0_1_2 = check_result3["result"]["access_zones"][0]["auth_provider_id"]
    global auth_provider_id_16_0_1_2

    # 1> 创建用户组group1
    log.info("\t[case1 create_auth_group ]")
    cmd = "create_auth_group "
    check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_2,
                                                 name="group_16_0_1_2")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_auth_group failed!!!' % node_ip)
    primary_group_id_16_0_1_2 = msg2["result"]
    global primary_group_id_16_0_1_2

    # 2> 创建用户user1
    log.info("\t[ create_auth_user ]")
    cmd = "create_auth_user"
    check_result2 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_16_0_1_2,
                                                name="user_16_0_1_2_aaaaaaaaaaaaaaaaaaaa", password='111111',
                                                primary_group_id=primary_group_id_16_0_1_2,
                                                secondary_group_ids="", home_dir="/home")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"] != "Name 'user_16_0_1_2_aaaaaaaaaaaaaaaa" \
                                                                          "aaaa' length:34 exceed the max length:31":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_auth_user failed!!!' % node_ip)
    user_id_16_0_1_2 = msg2["result"]
    global user_id_16_0_1_2
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

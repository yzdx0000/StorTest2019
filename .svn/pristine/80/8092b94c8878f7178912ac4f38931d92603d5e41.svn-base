# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-23
# @summary：
# 16-0-1-3     用户名特殊字符测试
# @steps:
# case1、创建一个以字母开头的，除了含数字和下划线还含有其他字符的用户名（用户名长度在1-31之间）；
# 1> 创建用户组group1
# 2> 创建用户user1
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
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_1_3
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


def executing_case1():
    # 1> 创建访问分区
    log.info("\t[case1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_1_3"
    node = common.Node()
    ids = node.get_nodes_id()
    access_zone_node_id_16_0_1_3 = ','.join(str(p) for p in ids)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_1_3, name=access_zone_name)
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
    auth_provider_id_16_0_1_3 = check_result3["result"]["access_zones"][0]["auth_provider_id"]
    global auth_provider_id_16_0_1_3

    # 1> 创建用户组group1
    log.info("\t[case1 create_auth_group ]")
    cmd = "create_auth_group"
    check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_3, name="group_16_0_1_3")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_auth_group failed!!!' % node_ip)
    primary_group_id_16_0_1_3 = msg2["result"]

    # 2> 创建用户user1
    log.info("\t[ create_auth_user ]")
    cmd = "create_auth_user "
    check_result2 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_16_0_1_3,
                                                name="user_16_0_1_3_@", password='111111',
                                                primary_group_id=primary_group_id_16_0_1_3,
                                                secondary_group_ids="", home_dir="/home")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "ILLEGAL_ARGUMENT" or msg2["detail_err_msg"] != "Name 'user_16_0_1_3_@' can only " \
                                                                          "consist of letters, numbers and underlines, " \
                                                                          "begin with a letter.":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_auth_user failed!!!' % node_ip)
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

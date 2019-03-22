# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-08-07
# @summary：
# 16_0_2_6    名称冲突检测
# @steps:
# 1> 创建第一个访问分区
# 2> 创建第二个访问分区，与第一个访问分区名字相同
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


def executing_case1():
    """ 1> 创建第一个访问分区 """
    log.info("\t[1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_2_6"
    node = common.Node()
    ids = node.get_nodes_id()
    print ids
    access_zone_node_id_16_0_2_6 = ','.join(str(p) for p in ids)
    cmd = "create_access_zone "
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_2_6, name=access_zone_name)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, msg1))
        raise Exception('%s create_access_zone failed!!!' % node_ip)

    """ 2> 创建第二个访问分区，与第一个访问分区名字相同"""
    log.info("\t[2 create_access_zone ]")
    cmd = "create_access_zone "
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_2_6, name=access_zone_name)
    if msg1["err_msg"] != "ILLEGAL_ARGUMENT" or \
       msg1["detail_err_msg"].find("already exist") == -1:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, msg1))
        raise Exception('%s create_access_zone failed!!!' % node_ip)

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

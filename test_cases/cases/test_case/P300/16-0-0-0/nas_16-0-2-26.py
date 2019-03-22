# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-08-08
# @summary：
# 16_0_2_26     删除输入错误的访问区id
# @steps:
# 1> 创建访问分区（本地认证）
# 2> 查看访问分区信息
# 3> 删除访问分区
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
    """ 1> 创建访问分区 """
    log.info("\t[1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_2_26"
    node = common.Node()
    ids = node.get_nodes_id()
    access_zone_node_id_16_0_2_26 = ','.join(str(p) for p in ids)
    node_name_list = nas_common.get_node_name_list(ids)
    cmd = "create_access_zone "
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_2_26, name=access_zone_name)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, msg1))
        raise Exception('%s create_access_zone failed!!!' % node_ip)
    access_zone_id = msg1["result"]

    """ 2> 查看访问分区信息 """
    log.info("\t[2 get_access_zones ]")
    cmd = "get_access_zones "
    check_result3 = nas_common.get_access_zones(ids=access_zone_id)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result3))
    if check_result3["detail_err_msg"] != "" or check_result3["err_msg"] != "":
        log.error('node_ip = %s, get_access_zones failed' % node_ip)
        raise Exception('%s get_access_zones failed!!!' % node_ip)

    """ 3> 删除访问分区 """
    log.info("\t[3 delete_access_zone ]")
    access_zone_id = access_zone_id + 1
    cmd = "delete_access_zone "
    check_result4 = nas_common.delete_access_zone(access_zone_id=access_zone_id)
    if check_result4["detail_err_msg"].find("Can not find access zone") == -1 or \
       check_result4["err_msg"] != "ILLEGAL_OPERATION":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result4))
        raise Exception('%s delete_access_zone failed!!!' % node_ip)

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

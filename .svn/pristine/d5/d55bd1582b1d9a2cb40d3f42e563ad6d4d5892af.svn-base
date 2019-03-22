# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-08-07
# @summary：
# 16_0_2_5     名称边界值、异常测试
# @steps:
# 1> 创建一个名称以字母开头的含数字和下划线的长度超过31位的访问区
# 2> 创建一个名称以字母开头的，除了含数字和下划线还含有其他字符的访问区（用户名长度在1-31之间）
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
    """ 1> 创建一个名称以字母开头的含数字和下划线的长度超过31位的访问区 """
    log.info("\t[1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_2_5_aaaaaaaaaaa"
    cmd = 'pscli --command=get_nodes'
    rc, stdout, stderr = shell.ssh(node_ip, cmd)
    outtext = common.json_loads(stdout)
    nodes = outtext['result']['nodes']
    ids = []
    for node in nodes:
        ids.append(node['data_disks'][0]['nodeId'])
    print ids
    access_zone_node_id_16_0_2_5 = ','.join(str(p) for p in ids)
    cmd = "ssh %s pscli --command=create_access_zone --node_ids=%s --name=%s" \
          % (node_ip, access_zone_node_id_16_0_2_5, access_zone_name)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_2_5, name=access_zone_name)
    if msg1["err_msg"] != "ILLEGAL_ARGUMENT" or msg1["detail_err_msg"].find("exceed the max length:31") == -1:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, msg1))
        raise Exception('%s create_access_zone failed!!!' % node_ip)

    """ 2> 创建一个名称以字母开头的，除了含数字和下划线还含有其他字符的访问区（用户名长度在1-31之间）"""
    log.info("\t[2 create_access_zone ]")
    access_zone_name = "access_zone_16_0_2_5_@***"
    cmd = "ssh %s pscli --command=create_access_zone --node_ids=%s --name=%s" \
          % (node_ip, access_zone_node_id_16_0_2_5, access_zone_name)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_2_5, name=access_zone_name)
    if msg1["err_msg"] != "ILLEGAL_ARGUMENT" or \
       msg1["detail_err_msg"].find("can only consist of letters, numbers and underlines, begin with a letter") == -1:
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

# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-25
# @summary：
# 16-0-4-86      共享名异常字符测试
# @steps:
# case1、创建一个共享名以字母开头的，除了含数字和下划线还含有其他字符的NFS共享（用户名长度在1-31之间）；
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
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_4_86
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：创建一个共享名以字母开头的，除了含数字和下划线还含有其他字符的NFS共享（用户名长度在1-31之间）；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：创建一个共享名以字母开头的，除了含数字和下划线还含有其他字符的NFS共享（用户名长度在1-31之间）；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> 检查目录并creat file
# 2> 检查file是否创建成功
# 3> 创建导出路径
#######################################################
def executing_case1():
    """准备环境"""
    # 1> 创建访问分区
    log.info("\t[case1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_4_86"
    node = common.Node()
    ids = node.get_nodes_id()
    print ids
    access_zone_node_id_16_0_4_86 = ','.join(str(p) for p in ids)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_4_86, name=access_zone_name)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s create_access_zone failed!!!' % node_ip)
    global access_zone_id_16_0_4_86
    access_zone_id_16_0_4_86 = msg1["result"]

    # 2> 启动NAS
    log.info("\t[ enable_nas ]")
    msg2 = nas_common.enable_nas(access_zone_id=access_zone_id_16_0_4_86, protocol_types="NFS")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s enable_nas failed!!!' % node_ip)

    # 3> 查看NAS是否按配置启动
    log.info("\t[ get_access_zones ]")
    check_result3 = nas_common.get_access_zones(ids=access_zone_id_16_0_4_86)
    name = check_result3["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        common.except_exit('%s enable_nas failed!!!' % node_ip)
    global auth_provider_id_16_0_4_86
    auth_provider_id_16_0_4_86 = check_result3["result"]["access_zones"][0]["auth_provider_id"]

    """1> 检查目录并creat file"""
    log.info("\t[ case1 create_file ]")
    # prepath = '/mnt/volume/nas'
    # isExists = os.path.exists(prepath)
    # if not isExists:
    #     os.makedirs(prepath)
    global nfs_path
    nfs_path = nas_common.ROOT_DIR + "nfs_dir_16_0_4_86"
    global NAS_PATH
    NAS_PATH = get_config.get_one_nas_test_path() + "/nfs_dir_16_0_4_86"
    cmd = "create_file "
    check_result6 = nas_common.create_file(path=nfs_path, posix_permission="rwxr-xr-x")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result6))
    msg6 = check_result6
    if msg6["err_msg"] != "" or msg6["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result6))
        raise Exception('%s create_file failed!!!' % node_ip)

    """2> 检查file是否创建成功"""
    log.info("\t[case1 get_file_list ]")
    cmd = "get_file_list "
    check_result7 = nas_common.get_file_list(path=nfs_path)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result7))
    msg7 = check_result7
    if msg7["err_msg"] != "" or msg7["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result7))
        raise Exception('%s get_file_list failed!!!' % node_ip)

    """3> 创建导出路径"""
    log.info("\t[ case1 create_nfs_export ]")
    global nfs_export_name
    nfs_export_name = "nfs_exp_test_16_0_4_86_@"
    cmd = "create_nfs_export"
    check_result1 = nas_common.create_nfs_export(access_zone_id=access_zone_id_16_0_4_86, export_name=nfs_export_name,
                                                 export_path=nfs_path)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] == "" or msg1["detail_err_msg"] != "Export name 'nfs_exp_test_16_0_4_86_@' can" \
                                                          " only consist of letters, numbers and underlines, " \
                                                          "begin with a letter.":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s create_nfs_export failed!!!' % node_ip)
    global nfs_export_id_16_0_4_86
    nfs_export_id_16_0_4_86 = msg1["result"]

    return


#######################################################
# @function：清理环境
# @parameter：
# @return：
# @steps:
#######################################################
def clearing_environment():
    log.info("（3）clearing_environment")
    '''1> 删除export'''
    log.info("\t[ 删除export ]")
    cmd = "delete_nfs_exports"
    check_result1 = nas_common.delete_nfs_exports(ids=nfs_export_id_16_0_4_86)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "ILLEGAL_ARGUMENT" or msg1["detail_err_msg"] != "Nfs export ids can not be empty.":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s delete_nfs_export failed!!!' % node_ip)

    '''2> 删除目录'''
    log.info("\t[ 删除目录 ]")
    cmd = 'rm -rf %s' % NAS_PATH
    rc, stdout, stderr = shell.ssh(node_ip, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \n cmd = %s\n stdout = %s\n stderr = %s" % (cmd, stdout, stderr))
    log.info(stdout)
    # prepath1 = '/mnt/volume/nas/nfs_dir_16_0_4_86'
    # prepath2 = '/mnt/volume/nas'
    # check_result1 = os.rmdir(prepath1)
    # log.info('node_ip = %s, check_result1 = %s' % (node_ip, check_result1))
    # check_result2 = os.rmdir(prepath2)
    # log.info('node_ip = %s, check_result1 = %s' % (node_ip, check_result2))
    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    log.info("（2）executing_case")

    '''
    1、测试执行
    2、结果检查
    '''

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
    executing_case1()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
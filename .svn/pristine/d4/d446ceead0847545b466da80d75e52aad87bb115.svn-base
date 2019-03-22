# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-24
# @summary：
# 16-0-4-83     正常创建NFS共享测试
# @steps:
# 1-1> 检查目录并creat file
# 1-2> 检查file是否创建成功
# 2> 在az1上创建nfs共享，输入正确的名称和共享路径
# 3> get_ftp_exports
# 4> 对比设置参数

# case1、创建共享路径volume:/nas/nfs_dir
# pscli --command=create_file --path=volume:/nas/nfs_dir
# case2、在az1上创建nfs共享，输入正确的名称和共享路径；
# pscli --command=create_nfs_export --access_zone_id=x --export_name=nfs_exp_test --export_path=volume:/nas/nfs_dir
# case3、查看nfs共享路径配置成功，信息是否与配置信息匹配；
# pscli --command=get_nfs_exports
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
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_4_82
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


def executing_case1():
    """0> 准备环境"""
    log.info("\t[case0 create_access_zone ]")
    access_zone_name = "access_zone_16_0_4_82"
    node = common.Node()
    ids = node.get_nodes_id()
    print ids
    access_zone_node_id_16_0_4_82 = ','.join(str(p) for p in ids)
    cmd = "create_access_zone "
    check_result1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_4_82,
                                                  name=access_zone_name,
                                                  isns_address="10.22.0.78")
    log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s create_access_zone failed!!!' % node_ip)
    global access_zone_id_16_0_4_82
    access_zone_id_16_0_4_82 = msg1["result"]

    # 1-1> 检查目录并creat file
    log.info("\t[ case1-1 create_file ]")
    # cmd = 'folder="/mnt/volume/nas" && if [ ! -d "$folder"]; then mkdir "$folder" fi'
    # rc, stdout, stderr = shell.ssh(node_ip, cmd)
    # if rc != 0:
    #     log.info("rc = %s" % (rc))
    #     log.info("WARNING: \n cmd = %s\n stdout = %s\n stderr = %s" % (cmd, stdout, stderr))
    # log.info(stdout)

    global nfs_path
    nfs_path = nas_common.ROOT_DIR + "nfs_dir_16_0_4_82"
    global NAS_PATH
    NAS_PATH = get_config.get_one_nas_test_path() + "/nfs_dir_16_0_4_82"
    cmd = "create_file "
    check_result6 = nas_common.create_file(path=nfs_path, posix_permission="rwxr-xr-x")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result6))
    msg6 = check_result6
    if msg6["err_msg"] != "" or msg6["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result6))
        raise Exception('%s create_file failed!!!' % node_ip)

    # 1-2> 检查file是否创建成功
    log.info("\t[ case1-2 get_file_list ]")
    cmd = "get_file_list"
    check_result7 = nas_common.get_file_list(path=nfs_path)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result7))
    msg7 = check_result7
    if msg7["err_msg"] != "" or msg7["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result7))
        raise Exception('%s get_file_list failed!!!' % node_ip)

    # 2.在az1上创建nfs共享，输入正确的名称和共享路径
    log.info("\t[ case2 create_nfs_export ]")
    global nfs_export_name
    nfs_export_name = "nfs_exp_test_16_0_4_82"
    cmd = "create_nfs_export "
    check_result1 = nas_common.create_nfs_export(access_zone_id=access_zone_id_16_0_4_82, export_name=nfs_export_name,
                                                 export_path=nfs_path)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s create_nfs_export failed!!!' % node_ip)
    global nfs_export_id_16_0_4_82
    nfs_export_id_16_0_4_82 = msg1["result"]

    '''0> 启动NAS'''
    log.info("\t[ enable_nas ]")
    cmd = "enable_nas "
    check_result2 = nas_common.enable_nas(access_zone_id=access_zone_id_16_0_4_82, protocol_types="NFS")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg = check_result2
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s enable_nas failed!!!' % node_ip)

    # 3. get_ftp_exports
    log.info("\t[ case3 get_nfs_exports ]")
    cmd = "get_nfs_exports "
    check_result = nas_common.get_nfs_exports(ids=nfs_export_id_16_0_4_82)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
    msg = check_result
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
        raise Exception('%s get_nfs_exports failed!!!' % node_ip)

    # 4> 对比设置参数
    access_zone_id = check_result["result"]["exports"][0]["access_zone_id"]
    export_name = check_result["result"]["exports"][0]["export_name"]
    export_path = check_result["result"]["exports"][0]["export_path"]
    if access_zone_id != access_zone_id_16_0_4_82:
        raise Exception('%s creat and get_nfs_exports failed1!!!' % node_ip)
    if export_name != nfs_export_name:
        raise Exception('%s creat and get_nfs_exports failed2!!!' % node_ip)
    if export_path != nfs_path:
        raise Exception('%s creat and get_nfs_exports failed3!!!' % node_ip)
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
    cmd = "delete_nfs_exports "
    check_result1 = nas_common.delete_nfs_exports(ids=nfs_export_id_16_0_4_82)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
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
    # prepath1 = '/mnt/volume/nas/nfs_dir_16_0_4_82'
    # check_result1 = os.rmdir(prepath1)
    # log.info('node_ip = %s, check_result1 = %s' % (node_ip, check_result1))

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
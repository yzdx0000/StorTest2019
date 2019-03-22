# -*-coding:utf-8 -*
# !/usr/bin/python

import os
import time
import commands
import json
import hashlib
from multiprocessing import Process

import utils_path
import common
import snap_common
import nas_common
import quota_common
import random
import log
import shell
import get_config
import tool_use
import prepare_clean
import logging

# =================================================================================
#  latest update:2018-08-21                                                   =
#  Author:wanggl                                                           =
# =================================================================================
# 2018-08-21:
# Author：wanggl
# @summary：
#   nfs客户端压缩解压缩场景
# @steps:
#   1、在nfs客户端通过命令行循环压缩解压缩10000个1m小文件；

#

# changelog:


######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
nfs_path = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/wangguanglin/nas_test_dir/cus_6_1_0_41
Private_clientIP1 = get_config.get_client_ip(0)
Compress_name = "%s.tar.gz" % FILE_NAME
nas_test_dir_name = os.path.basename(nas_common.NAS_PATH)
nas_volume_name = os.path.basename(os.path.dirname(nas_common.NAS_PATH))
create_file_path = nas_volume_name + ':/' + nas_test_dir_name + '/' + FILE_NAME
SYSTEM_IP = get_config.get_parastor_ip()


def tar_log(pwd_dir, tar_name, src_dir, node_ip):
    """
    :Author:         wanggl
    :date  :         2018.08.21
    :description:    压缩目录
    :param pwd_dir:  操作目录
    :param src_dir:  要压缩的源目录
    :param tar_name: 压缩包的名字
    :param node_ip:  执行命令的节点
    :return:
    """
    cmd = 'cd %s && tar zcvf %s %s --remove-files' % (pwd_dir, tar_name, src_dir)
    info_str = "node %s  tar %s  to  %s" % (node_ip, src_dir, tar_name)
    logging.info(info_str)
    rc, stdout = common.run_command(node_ip, cmd)
    if rc != 0:
        logging.error(stdout)
        logging.error("tar failed!!!")
    return rc, stdout


def tar_xvflog(pwd_dir, tar_name, node_ip):
    """
    :Author:         wanggl
    :date  :         2018.08.21
    :description:    解压缩目录
    :param pwd_dir:  操作目录
    :param tar_name: 压缩包的名字
    :param node_ip:  执行命令的节点
    :return:
    """
    cmd = 'cd %s && tar xvf %s && rm -rf %s' % (pwd_dir, tar_name, tar_name)
    info_str = "node %s  uncompress %s  " % (node_ip, tar_name)
    logging.info(info_str)
    rc, stdout = common.run_command(node_ip, cmd)
    if rc != 0:
        logging.error(stdout)
        logging.error("xtar failed!!!")
    return rc, stdout


def case():
    log.info('1> 在nfs客户端通过命令行循环压缩解压缩10000个1m小文件')
    """创建访问分区"""
    access_zone_name = FILE_NAME+"_access_zone_name1"
    ob_node = common.Node()
    node_ids = []
    node_ids = ob_node.get_nodes_id()
    access_zone_node_id_6_1_0_41 = ','.join(str(p) for p in node_ids)
    check_result1 = nas_common.create_access_zone(node_ids=access_zone_node_id_6_1_0_41, name=access_zone_name)
    if check_result1["err_msg"] != "" or check_result1["detail_err_msg"] != "":
        log.error('%s Failed ' % FILE_NAME)
        raise Exception('%s create_access_zone failed!!!' % FILE_NAME)
    id_6_1_0_41 = check_result1["result"]

    """配置共享目录、授权协议、对外IP地址、授权客户端IP"""
    """enable nas"""
    check_result2 = nas_common.enable_nas(access_zone_id=id_6_1_0_41)
    wait_time1 = random.randint(10, 15)
    time.sleep(wait_time1)
    if check_result2["err_msg"] != "" or check_result2["detail_err_msg"] != "":
        log.error('check_result = %s Failed' % (FILE_NAME))
        raise Exception('%s enable_nas failed!!!' % FILE_NAME)

    """查看NAS是否按配置启动"""
    check_result3 = nas_common.get_access_zones(ids=id_6_1_0_41)
    name = check_result3["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        raise Exception('%s enable_nas failed!!!' % FILE_NAME)
    auth_provider_id_6_1_0_41 = check_result3["result"]["access_zones"][0]["auth_provider_id"]

    """创建目录"""
    check_result4 = nas_common.create_file(path=create_file_path)
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s create_file Failed") % FILE_NAME)

    """添加本地用户组/用户"""
    check_result5 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_6_1_0_41,
                                                 name="group_6_1_0_41")

    if check_result5["err_msg"] != "" or check_result4["detail_err_msg"] != "":
        log.error('%s Failed' % (FILE_NAME))
        raise Exception('%s create_auth_group Failed!!!' % FILE_NAME)
    primary_group_id_6_1_0_41 = check_result5["result"]
    """添加本地用户"""
    check_result6 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_6_1_0_41,
                                                name='user_6_1_0_41', password='111111',
                                                primary_group_id=primary_group_id_6_1_0_41)
    if check_result6["err_msg"] != "" or check_result5["detail_err_msg"] != "":
        log.error('%s Failed' % FILE_NAME)
        raise Exception('%s create_auth_user Failed!!!' % FILE_NAME)

    # 导出目录
    nfs_export_name = "nfs_export"+FILE_NAME
    check_result7 = nas_common.create_nfs_export(access_zone_id=id_6_1_0_41,
                                                 export_name=nfs_export_name,
                                                 export_path=create_file_path)
    if check_result7["err_msg"] != "" or check_result7["detail_err_msg"] != "":
        log.error(' %s failed' % FILE_NAME)
        raise Exception('%s create_nfs_export failed!!!' % FILE_NAME)
    nfs_export_id_6_1_0_41 = check_result7["result"]

    """添加nfs nas 用户"""
    """添加nfs客户端1"""
    auth_clients_name1 = get_config.get_client_ip(3)
    auth_clients_permission_level = 'rw'
    auth_permission_constraint = 'no_root_squash'
    check_result8 = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id_6_1_0_41,
                                                           name=auth_clients_name1,
                                                           permission_level=auth_clients_permission_level,
                                                           permission_constraint=auth_permission_constraint)
    if check_result8["err_msg"] != "" or check_result8["detail_err_msg"] != "":
        log.error(' %s failed' % FILE_NAME)
        raise Exception('%s add_nfs_export_auth_clients failed!!!' % FILE_NAME)

    """客户端mount"""
    global auth_clients_mount_dir
    auth_clients_mount_dir = os.path.join('/mnt/', FILE_NAME)
    common.mkdir_path(auth_clients_name1, auth_clients_mount_dir)

    """客户端mount共享路径"""
    wait_time1 = random.randint(8, 10)
    time.sleep(wait_time1)
    cmd1 = "ssh %s mount -t nfs %s:%s %s " \
           % (auth_clients_name1, SYSTEM_IP, nfs_path, auth_clients_mount_dir)
    common.run_command(auth_clients_name1, cmd1)

    """先创建10000个1m小文件"""
    Date_path = os.path.join(auth_clients_mount_dir, 'nfs')
    common.mkdir_path(auth_clients_name1, Date_path)
    cmd = "cd %s && for i in {1..10000}; do dd if=/dev/zero of=file_$i bs=1M count=1; done" % Date_path
    rc, stdout = common.run_command(auth_clients_name1, cmd)
    common.judge_rc(rc, 0, 'create file')
    """循环压缩解压缩10000个1m小文件"""
    Execute_path = os.path.dirname(Date_path)
    source_name = os.path.basename(Date_path)
    print source_name
    for i in range(2):
        rc, stdout = tar_log(Execute_path, Compress_name, source_name, auth_clients_name1)
        common.judge_rc(rc, 0, 'compress')
        rc, stdout = tar_xvflog(Execute_path, Compress_name, auth_clients_name1)
        common.judge_rc(rc, 0, 'umcompress')

    """ 清理环境"""
    cmd = "ssh %s umount %s " % (auth_clients_name1, auth_clients_mount_dir)
    common.rm_exe(auth_clients_name1, auth_clients_mount_dir)
    common.run_command(auth_clients_name1, cmd)

    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info('succeed!')


if __name__ == '__main__':
    common.case_main(main)





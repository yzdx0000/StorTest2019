# -*-coding:utf-8 -*
# !/usr/bin/python

import os
import time
import commands
import json
import hashlib
import random
from multiprocessing import Process

import utils_path
import common
import snap_common
import nas_common
import log
import shell
import get_config
import tool_use
import prepare_clean

# =================================================================================
#  latest update:2018-08-16                                                    =
#  Author:wanggl                                                           =
# =================================================================================
# 2018-08-16:
# Author：wanggl
# @summary：
#   POSIX锁问题
# @steps:
#   1、3节点集群，1个独立私有客户端A，1个nas客户端B；
#   2、私有客户端分别对cli_dlm_enqueue_notimeout和cli_file_locks_grant函数注入故障错误码-10800007和-2；
#   私有客户端和机头节点分别执行一下两个命令
#   echo "cli_dlm_enqueue_notimeout -10800007 100" > /proc/parastor/cli_inject_error
#   echo "lcli_file_locks_grant -2 100" > /proc/parastor/cli_inject_error
#   观察cat /proc/parastor/cli_inject_error都恢复[FAULT-0]:, 2147483647, 0则检查环境；
#   3 、观察客户端读写业务正常，无报错退出，无core产生；
#
#

# changelog:


######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
nfs_path = os.path.join(nas_common.NAS_PATH, FILE_NAME)                  # /mnt/wangguanglin/nas_test_dir/cus_6_1_0_45
# create_file_path = os.path.join(nas_common.ROOT_DIR, FILE_NAME)          # wangguanglin:/nas_test_dir/cus_6_1_0_45
nas_test_dir_name = os.path.basename(nas_common.NAS_PATH)
nas_volume_name = os.path.basename(os.path.dirname(nas_common.NAS_PATH))
create_file_path = nas_volume_name + ':/' + nas_test_dir_name + '/' + FILE_NAME
SYSTEM_IP = get_config.get_parastor_ip()
Private_clientIP1 = get_config.get_client_ip(0)
Private_clientIP2 = get_config.get_client_ip(1)
Private_clientIP3 = get_config.get_client_ip(2)


def case():

    log.info('1> 3节点集群，1个独立私有客户端A，1个nas客户端B')
    """若访问分区已经创建好，该步骤需要注释掉"""
    """创建访问分区"""
    access_zone_name = FILE_NAME+"_access_zone_name1"
    ob_node = common.Node()
    node_ids = []
    node_ids = ob_node.get_nodes_id()
    access_zone_node_id_6_1_0_45 = ','.join(str(p) for p in node_ids)
    check_result1 = nas_common.create_access_zone(node_ids=access_zone_node_id_6_1_0_45, name=access_zone_name)
    if check_result1["err_msg"] != "" or check_result1["detail_err_msg"] != "":
        log.error('%s Failed ' % FILE_NAME)
        raise Exception('%s create_access_zone failed!!!' % FILE_NAME)
    id_6_1_0_45 = check_result1["result"]

    """配置共享目录、授权协议、对外IP地址、授权客户端IP"""
    """enable nas"""
    check_result2 = nas_common.enable_nas(access_zone_id=id_6_1_0_45)
    wait_time1 = random.randint(10, 15)
    time.sleep(wait_time1)
    if check_result2["err_msg"] != "" or check_result2["detail_err_msg"] != "":
        log.error('check_result = %s Failed' % (FILE_NAME))
        raise Exception('%s enable_nas failed!!!' % FILE_NAME)

    """查看NAS是否按配置启动"""
    check_result3 = nas_common.get_access_zones(ids=id_6_1_0_45)
    name = check_result3["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        raise Exception('%s enable_nas failed!!!' % FILE_NAME)
    auth_provider_id_6_1_0_45 = check_result3["result"]["access_zones"][0]["auth_provider_id"]

    """创建目录"""
    check_result4 = nas_common.create_file(path=create_file_path)
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s create_file Failed") % FILE_NAME)

    """添加本地用户组/用户"""
    check_result5 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_6_1_0_45,
                                                 name="group_6_1_0_45")

    if check_result5["err_msg"] != "" or check_result4["detail_err_msg"] != "":
        log.error('%s Failed' % (FILE_NAME))
        raise Exception('%s create_auth_group Failed!!!' % FILE_NAME)
    primary_group_id_6_1_0_45 = check_result5["result"]
    """添加本地用户"""
    check_result6 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_6_1_0_45,
                                                name='user_6_1_0_45', password='111111',
                                                primary_group_id=primary_group_id_6_1_0_45)
    if check_result6["err_msg"] != "" or check_result5["detail_err_msg"] != "":
        log.error('%s Failed' % FILE_NAME)
        raise Exception('%s create_auth_user Failed!!!' % FILE_NAME)

    # 导出目录
    nfs_export_name = "nfs_export"+FILE_NAME
    check_result7 = nas_common.create_nfs_export(access_zone_id=id_6_1_0_45,
                                                 export_name=nfs_export_name,
                                                 export_path=create_file_path)
    if check_result7["err_msg"] != "" or check_result7["detail_err_msg"] != "":
        log.error(' %s failed' % FILE_NAME)
        raise Exception('%s create_nfs_export failed!!!' % FILE_NAME)
    nfs_export_id_6_1_0_45 = check_result7["result"]

    """添加nfs nas 用户"""
    """添加nfs客户端1"""
    auth_clients_name1 = get_config.get_client_ip(3)
    auth_clients_permission_level = 'rw'
    auth_permission_constraint = 'no_root_squash'
    check_result8 = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id_6_1_0_45,
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
    nfs_file1 = os.path.join(auth_clients_mount_dir, 'test_file1')

    """客户端mount共享路径"""
    wait_time1 = random.randint(8, 10)
    time.sleep(wait_time1)
    cmd1 = "ssh %s mount -t nfs %s:%s %s " \
           % (auth_clients_name1, snap_common.SYSTEM_IP, nfs_path, auth_clients_mount_dir)
    common.run_command(snap_common.SYSTEM_IP, cmd1)

    log.info('2> 私有客户端和机头节点分别执行一下两个命令'
             ' echo "cli_dlm_enqueue_notimeout -10800007 100" > /proc/parastor/cli_inject_error'
             'echo "lcli_file_locks_grant -2 100" > /proc/parastor/cli_inject_error')

    cmd = "echo 'cli_dlm_enqueue_notimeout -10800007 100' > /proc/parastor/cli_inject_error"
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'Private client inject error  ')
    cmd = "echo 'lcli_file_locks_grant -2 100' > /proc/parastor/cli_inject_error"
    rc, stdout = common.run_command(snap_common.SYSTEM_IP, cmd)
    common.judge_rc(rc, 0, 'NAS head node  inject error ')

    log.info('3> 观察客户端读写业务正常，无报错退出，无core产生')
    vdb = tool_use.Vdbenchrun(depth=2, width=3, files=40)
    rc_vdb = vdb.run_create(nfs_path, '/tmp', Private_clientIP1)

    """ 恢复配置文件"""
    cmd = "echo 0 > /proc/parastor/cli_inject_error"
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'Private client restore environment')
    cmd = "echo 0 > /proc/parastor/cli_inject_error"
    rc, stdout = common.run_command(snap_common.SYSTEM_IP, cmd)
    common.judge_rc(rc, 0, 'NAS head node restore environment')

    # 避免出错后直接退出，先恢复环境再检查
    common.judge_rc(rc_vdb, 0, 'vdbench run ')

    """ 清理环境"""
    cmd = "ssh %s umount %s " % (auth_clients_name1, auth_clients_mount_dir)
    common.run_command(auth_clients_name1, cmd)
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info('succeed!')


if __name__ == '__main__':
    common.case_main(main)
# -*-coding:utf-8 -*
# !/usr/bin/python

import os
import time
import commands
import json
import hashlib

import utils_path
import common
import snap_common
import nas_common

import random
import log
import shell
import get_config
import tool_use
import prepare_clean
from multiprocessing import Process

# =================================================================================
#  latest update:2018-08-06                                                    =
#  author:wanggl                                                           =
# =================================================================================
# 2018-08-06:
# 修改者：wanggl
# @summary：
#   存储系统某个目录ls卡住
# @steps:
#   1、创建3节点访问区，确定nas服务；
#   2、配置共享目录、授权协议、对外IP地址、授权客户端IP；
#   3、linux客户端通过授权的用户挂载目录；
#   4、在3个客户端10线程使用mpi并发重复创建同一个文件；
#
#
#

# changelog:


######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
nfs_path = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/wangguanglin/nas_test_dir/cus_6_1_0_23
create_file_path = os.path.join(nas_common.ROOT_DIR, FILE_NAME)         # wangguanglin:/nas_test_dir/cus_6_1_0_23


def mpi_create_file(machines_path, file, exe_ip):
    cmd = 'mpirun -hostfile %s -np 10 --allow-run-as-root touch %s'\
          % (machines_path, file)
    rc, stdout = common.run_command(exe_ip, cmd)
    common.judge_rc(rc, 0, 'mpi create file')
    return


def case():
    """若访问分区已经创建好，该步骤需要注释掉"""
    """创建访问分区"""
    access_zone_name = FILE_NAME+"_access_zone_name1"
    ob_node = common.Node()
    node_ids = []
    node_ids = ob_node.get_nodes_id()
    print node_ids
    access_zone_node_id_6_1_0_23 = ','.join(str(p) for p in node_ids)
    check_result1 = nas_common.create_access_zone(node_ids=access_zone_node_id_6_1_0_23, name=access_zone_name)
    if check_result1["err_msg"] != "" or check_result1["detail_err_msg"] != "":
        log.error('%s Failed ' % FILE_NAME)
        raise Exception('%s create_access_zone failed!!!' % FILE_NAME)
    id_6_1_0_23 = check_result1["result"]

    """配置共享目录、授权协议、对外IP地址、授权客户端IP"""
    """enable nas"""
    check_result2 = nas_common.enable_nas(access_zone_id=id_6_1_0_23)
    wait_time1 = random.randint(10, 15)
    time.sleep(wait_time1)
    if check_result2["err_msg"] != "" or check_result2["detail_err_msg"] != "":
        log.error('check_result = %s Failed' % (FILE_NAME))
        raise Exception('%s enable_nas failed!!!' % FILE_NAME)

    """查看NAS是否按配置启动"""
    check_result3 = nas_common.get_access_zones(ids=id_6_1_0_23)
    name = check_result3["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        raise Exception('%s enable_nas failed!!!' % FILE_NAME)
    auth_provider_id_6_1_0_23 = check_result3["result"]["access_zones"][0]["auth_provider_id"]

    """创建目录"""
    check_result4 = nas_common.create_file(path=create_file_path)
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s create_file Failed") % FILE_NAME)

    """添加本地用户组/用户"""
    check_result5 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_6_1_0_23,
                                                 name="group_6_1_0_23")

    if check_result5["err_msg"] != "" or check_result4["detail_err_msg"] != "":
        log.error('%s Failed' % (FILE_NAME))
        raise Exception('%s create_auth_group Failed!!!' % FILE_NAME)
    primary_group_id_6_1_0_23 = check_result5["result"]
    """添加本地用户"""
    check_result6 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_6_1_0_23,
                                                name='user_6_1_0_23', password='111111',
                                                primary_group_id=primary_group_id_6_1_0_23)
    if check_result6["err_msg"] != "" or check_result5["detail_err_msg"] != "":
        log.error('%s Failed' % FILE_NAME)
        raise Exception('%s create_auth_user Failed!!!' % FILE_NAME)

    # 导出目录
    nfs_export_name = "nfs_export"+FILE_NAME
    check_result7 = nas_common.create_nfs_export(access_zone_id=id_6_1_0_23,
                                                 export_name=nfs_export_name,
                                                 export_path=create_file_path)
    if check_result7["err_msg"] != "" or check_result7["detail_err_msg"] != "":
        log.error(' %s failed' % FILE_NAME)
        raise Exception('%s create_nfs_export failed!!!' % FILE_NAME)
    nfs_export_id_6_1_0_23 = check_result7["result"]

    """添加nfs nas 用户"""
    """添加nfs客户端1"""
    auth_clients_name1 = nas_common.NFS_1_CLIENT_IP
    auth_clients_permission_level = 'rw'
    auth_permission_constraint = 'no_root_squash'
    check_result8 = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id_6_1_0_23,
                                                           name=auth_clients_name1,
                                                           permission_level=auth_clients_permission_level,
                                                           permission_constraint=auth_permission_constraint)
    if check_result8["err_msg"] != "" or check_result8["detail_err_msg"] != "":
        log.error(' %s failed' % FILE_NAME)
        raise Exception('%s add_nfs_export_auth_clients failed!!!' % FILE_NAME)

    """添加nfs客户端2"""
    auth_clients_name2 = nas_common.NFS_2_CLIENT_IP
    auth_clients_permission_level = 'rw'
    auth_permission_constraint = 'no_root_squash'
    check_result8 = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id_6_1_0_23,
                                                           name=auth_clients_name2,
                                                           permission_level=auth_clients_permission_level,
                                                           permission_constraint=auth_permission_constraint)
    if check_result8["err_msg"] != "" or check_result8["detail_err_msg"] != "":
        log.error(' %s failed' % FILE_NAME)
        raise Exception('%s add_nfs_export_auth_clients failed!!!' % FILE_NAME)

    """添加nfs客户端3"""
    auth_clients_name3 = nas_common.NFS_3_CLIENT_IP
    auth_clients_permission_level = 'rw'
    auth_permission_constraint = 'no_root_squash'
    check_result8 = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id_6_1_0_23,
                                                           name=auth_clients_name3,
                                                           permission_level=auth_clients_permission_level,
                                                           permission_constraint=auth_permission_constraint)
    if check_result8["err_msg"] != "" or check_result8["detail_err_msg"] != "":
        log.error(' %s failed' % FILE_NAME)
        raise Exception('%s add_nfs_export_auth_clients failed!!!' % FILE_NAME)

    """客户端mount"""
    global auth_clients_mount_dir
    auth_clients_mount_dir = os.path.join('/mnt/', FILE_NAME)
    cmd1 = "ssh %s mkdir %s" % (auth_clients_name1, auth_clients_mount_dir)
    common.run_command(snap_common.CLIENT_IP_1, cmd1)#todo nas.common client
    cmd2 = "ssh %s mkdir %s" % (auth_clients_name2, auth_clients_mount_dir)
    common.run_command(snap_common.CLIENT_IP_1, cmd2)
    cmd3 = "ssh %s mkdir %s" % (auth_clients_name3, auth_clients_mount_dir)
    common.run_command(snap_common.CLIENT_IP_1, cmd3)

    """客户端mount共享路径"""
    wait_time1 = random.randint(8, 10)
    time.sleep(wait_time1)
    cmd1 = "ssh %s mount -t nfs %s:%s %s " \
           % (auth_clients_name1, snap_common.SYSTEM_IP, nfs_path, auth_clients_mount_dir)
    common.run_command(snap_common.CLIENT_IP_1, cmd1)
    cmd2 = "ssh %s mount -t nfs %s:%s %s " \
           % (auth_clients_name2, snap_common.SYSTEM_IP, nfs_path, auth_clients_mount_dir)
    common.run_command(snap_common.CLIENT_IP_1, cmd2)
    cmd3 = "ssh %s mount -t nfs %s:%s %s " \
           % (auth_clients_name3, snap_common.SYSTEM_IP, nfs_path, auth_clients_mount_dir)
    common.run_command(snap_common.CLIENT_IP_1, cmd3)

    test_file1 = os.path.join(auth_clients_mount_dir, 'test_file1')
    test_dir1 = os.path.join(auth_clients_mount_dir, 'test_dir1')

    """"在3个客户端10线程使用mpi并发重复创建同一个文件"""
    log.info('在3个客户端10线程使用mpi并发重复创建同一个文件')
    machines_path = '/tmp/machines'
    cmd = 'echo "%s slots=4\n%s slots=3\n%s slots=3" > %s' \
          % (auth_clients_name1, auth_clients_name2, auth_clients_name3, machines_path)
    common.run_command(snap_common.CLIENT_IP_1, cmd)
    p1 = Process(target=mpi_create_file, args=(machines_path, test_file1,  snap_common.CLIENT_IP_1))
    p1.start()
    p1.join()

    """ 清理环境"""
    cmd = "ssh %s umount %s " %(auth_clients_name1, auth_clients_mount_dir)
    common.run_command(auth_clients_name1, cmd)
    cmd = "ssh %s umount %s " %(auth_clients_name2, auth_clients_mount_dir)
    common.run_command(auth_clients_name2, cmd)
    cmd = "ssh %s umount %s " %(auth_clients_name3, auth_clients_mount_dir)
    common.run_command(auth_clients_name3, cmd)
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info('succeed!')

if __name__ == '__main__':
    common.case_main(main)

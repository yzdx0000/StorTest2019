#-*-coding:utf-8 -*
#!/usr/bin/python

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


#=================================================================================
#  latest update:2018-05-31                                                    =
#  author:wangguanglin                                                           =
#=================================================================================
# 2018-05-31:
# 修改者：wangguanglin
#@summary：
#   读写过程中快照的创建
#@steps:
#   1、创建3节点访问区，确定nas服务；
#   2、配置共享目录、授权协议、对外IP地址、授权客户端IP；
#   3、linux客户端通过授权的用户挂载目录；
#   4、通过linux对共享目录100个1M文件；
#   5、主动对共享目录手工执行快照；
# （pscli --command=create_snapshot --name=nas_test --path=volume:/nas/nas_snap --expire_time=xxxxx）
#   6、删除50个文件，重新创建50个2M文件，进入私有客户端目录./snapshut/nas_test/，观察快照文件；
#


#changelog:
######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                # 本脚本名字
vdb_path = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/wangguanglin/nas_test_dir/nas_16_6_1_7
create_file_path = os.path.join(nas_common.ROOT_DIR, FILE_NAME)         # wangguanglin:/nas_test_dir/nas_16_6_1_7
SYSTEM_IP = get_config.get_parastor_ip()


def case():

    """创建访问分区"""
    access_zone_name = "nas_16_6_1_7_access_zone_name1"
    ob_node = common.Node()
    node_ids = []
    node_ids = ob_node.get_nodes_id()
    access_zone_node_id_16_6_1_7 = ','.join(str(p) for p in node_ids)
    check_result1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_6_1_7, name=access_zone_name)
    if check_result1["err_msg"] != "" or check_result1["detail_err_msg"] != "":
        log.error('%s Failed ' % FILE_NAME)
        raise Exception('%s create_access_zone failed!!!' % FILE_NAME)
    id_16_6_1_7 = check_result1["result"]

    """配置共享目录、授权协议、对外IP地址、授权客户端IP"""
    """enable nas """
    check_result2 = nas_common.enable_nas(access_zone_id=id_16_6_1_7)
    wait_time1 = random.randint(10, 15)
    time.sleep(wait_time1)
    if check_result2["err_msg"] != "" or check_result2["detail_err_msg"] != "":
        log.error('check_result = %s Failed' % (FILE_NAME))
        raise Exception('%s enable_nas failed!!!' % FILE_NAME)

    """查看NAS是否按配置启动"""
    check_result3 = nas_common.get_access_zones(ids=id_16_6_1_7)
    name = check_result3["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        raise Exception('%s enable_nas failed!!!' % FILE_NAME)
    auth_provider_id_16_6_1_7 = check_result3["result"]["access_zones"][0]["auth_provider_id"]

    """创建目录"""
    check_result4 = nas_common.create_file(path=create_file_path, posix_permission="rwxr-xr-x")
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s create_file Failed") % FILE_NAME)

    """添加本地用户组/用户"""
    check_result5 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_6_1_7,
                                                 name="group_16_6_1_7")

    if check_result5["err_msg"] != "" or check_result4["detail_err_msg"] != "":
        log.error('%s Failed' % (FILE_NAME))
        raise Exception('%s create_auth_group Failed!!!' % FILE_NAME)
    primary_group_id_16_6_1_7 = check_result5["result"]
    """添加本地用户"""
    check_result6 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_16_6_1_7,
                                                name='user_16_6_1_7', password='111111',
                                                primary_group_id=primary_group_id_16_6_1_7)
    if check_result6["err_msg"] != "" or check_result5["detail_err_msg"] != "":
        log.error('%s Failed' % FILE_NAME)
        raise Exception('%s create_auth_user Failed!!!' % FILE_NAME)

    # 导出目录
    nfs_export_name = "nfs_export"+FILE_NAME
    check_result7 = nas_common.create_nfs_export(access_zone_id=id_16_6_1_7,
                                                 export_name=nfs_export_name,
                                                 export_path=create_file_path)
    if check_result7["err_msg"] != "" or check_result7["detail_err_msg"] != "":
        log.error(' %s failed' % FILE_NAME)
        raise Exception('%s create_nfs_export failed!!!' % FILE_NAME)
    nfs_export_id_16_6_1_7 = check_result7["result"]

    """添加nfs nas 用户"""
    """添加nfs客户端1"""
    auth_clients_name1 = nas_common.NFS_1_CLIENT_IP
    auth_clients_permission_level = 'rw'
    auth_permission_constraint = 'no_root_squash'
    check_result8 = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id_16_6_1_7,
                                                           name=auth_clients_name1,
                                                           permission_level=auth_clients_permission_level,
                                                           permission_constraint=auth_permission_constraint)
    if check_result8["err_msg"] != "" or check_result8["detail_err_msg"] != "":
        log.error(' %s failed' % FILE_NAME)
        raise Exception('%s add_nfs_export_auth_clients failed!!!' % FILE_NAME)

    """添加nfs客户端2"""
    auth_clients_name2 =nas_common.NFS_2_CLIENT_IP
    auth_clients_permission_level = 'rw'
    auth_permission_constraint = 'no_root_squash'
    check_result8 = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id_16_6_1_7,
                                                           name=auth_clients_name2,
                                                           permission_level=auth_clients_permission_level,
                                                           permission_constraint=auth_permission_constraint)
    if check_result8["err_msg"] != "" or check_result8["detail_err_msg"] != "":
        log.error(' %s failed' % FILE_NAME)
        raise Exception('%s add_nfs_export_auth_clients failed!!!' % FILE_NAME)

    """客户端mount"""
    global auth_clients_mount_dir
    auth_clients_mount_dir = os.path.join('/mnt/', FILE_NAME)
    common.mkdir_path(auth_clients_name1, auth_clients_mount_dir)
    cmd2 = "ssh %s mkdir %s" % (auth_clients_name2, auth_clients_mount_dir)
    common.run_command(auth_clients_name2, cmd2)

    """客户端mount共享路径"""
    wait_time1 = random.randint(8, 10)
    time.sleep(wait_time1)
    cmd1 = "ssh %s mount -t nfs %s:%s %s " \
           % (auth_clients_name1, SYSTEM_IP, vdb_path, auth_clients_mount_dir)
    common.run_command(auth_clients_name1, cmd1)
    cmd2 = "ssh %s mount -t nfs %s:%s %s " \
           % (auth_clients_name2, SYSTEM_IP, vdb_path, auth_clients_mount_dir)
    common.run_command(auth_clients_name2, cmd2)

    log.info('4> 通过linux对共享目录100个1M文件')
    """创建100个1m小文件"""
    path1 = os.path.join(auth_clients_mount_dir, 'snap')
    common.mkdir_path(auth_clients_name1, path1)
    cmd = "cd %s && for i in {1..100}; do dd if=/dev/zero of=file_$i bs=1M count=1; done" % path1
    rc, stdout = common.run_command( auth_clients_name1, cmd)
    common.judge_rc(rc, 0, 'create file')

    log.info('5> 主动对共享目录手工执行快照')
    """对目录/mnt/wangguanglin/nas_16_6_1_7/snap/创建快照1"""
    snap_path = os.path.join(create_file_path, 'snap')
    snap_name1 = FILE_NAME + '_snapshot1'
    rc, stdout = snap_common.create_snapshot(snap_name1, snap_path)
    common.judge_rc(rc, 0, 'create_snapshot %s'% snap_name1)

    log.info('6> 删除50个文件，重新创建50个2M文件，进入私有客户端目录./sna/nas_test/，观察快照文件')
    """对目录/mnt/wangguanglin/nas_16_6_1_7/snap/前50个文件删除"""
    cmd = "cd %s && for i in {1..50}; do rm -rf file_$i; done" % path1
    rc, stdout = common.run_command( auth_clients_name1, cmd)
    common.judge_rc(rc, 0, 'delete file')
    """对目录/mnt/wangguanglin/nas_16_6_1_7/snap/重新创建2M的前50个文件"""
    cmd = "cd %s && for i in {1..50}; do dd if=/dev/zero of=file_$i bs=2M count=1; done" % path1
    rc, stdout = common.run_command( auth_clients_name1, cmd)
    common.judge_rc(rc, 0, 'create file')

    """进入私有客户端目录，观察快照文件"""
    test_dir1=os.path.join(snap_common.SNAPSHOT_PAHT,snap_name1)
    cmd='ls -alF -h %s|grep file'%test_dir1
    rc,stdout=common.run_command(snap_common.CLIENT_IP_1, cmd)
    for i in stdout.split('\n')[:-1]:
        if i.strip().split()[4] != '1.0M':
            log.error('%s item failed!!!' % snap_name1)
            raise Exception('%s item failed!!!' % snap_name1)

    """ 清理环境"""
    cmd = "ssh %s umount %s " %(auth_clients_name1, auth_clients_mount_dir)
    common.run_command(auth_clients_name1, cmd)
    cmd = "ssh %s umount %s " %(auth_clients_name2, auth_clients_mount_dir)
    common.run_command(auth_clients_name2, cmd)
    rc, stdout = snap_common.delete_snapshot_by_name(snap_name1)
    common.judge_rc(rc, 0, 'delete snapshot')

    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info('succeed!')


if __name__ == '__main__':
    common.case_main(main)







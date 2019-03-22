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
#  latest update:2018-08-06                                                    =
#  Author:wanggl                                                           =
# =================================================================================
# 2018-08-06:
# Author：wanggl
# @summary：
#   paradigm业务不能正常退出
# @steps:
#   1、创建3节点访问区，确定nas服务；
#   2、配置共享目录、授权协议、对外IP地址、授权客户端IP；
#   3、linux客户端通过授权的用户挂载目录；
#   4、客户端A通过私有或nas 读写一个文件；
#   5、客户端B通过私有或nas删除该文件，观察客户端A读写情况；
#
#

# changelog:


######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
nfs_path = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/wangguanglin/nas_test_dir/cus_6_1_0_24
create_file_path = os.path.join(nas_common.ROOT_DIR, FILE_NAME)         # wangguanglin:/nas_test_dir/cus_6_1_0_24


def verify_md5(offset1, block_size, r_w, test_file, nfs_file, exe_ip):
    """
    :author:            wanggl
    :date  :            2018.08.7
    :description:       比较nfs客户端上数据与POSIX数据的MD5值，判断一致性
    :param offset1:    偏移量，从哪个位置开始进行操作
    :param block_size: 块大小
    :param r_w:         读写方式选择
    :param test_file:    POSIX客户端文件
    :param nfs_file:    nfs客户端文件
     :param exe_ip:     外部客户端
    :return: 
    """
    """校验工具"""
    tools_path = get_config.get_tools_path()
    verify_tool = os.path.join(tools_path, 'verify')
    verify_file = os.path.join(verify_tool, 'verify_common.py')

    log.info('客户端A通过私有或nas 读写一个文件')
    '''nfs客户端创建10T文件'''
    cmd = 'ssh %s chmod 766 %s ' % (exe_ip, nfs_file)
    common.run_command(exe_ip, cmd)

    cmd = "ssh %s truncate -s 10T %s" % (exe_ip, nfs_file)
    rc, stdout = common.run_command(exe_ip, cmd)
    common.judge_rc(rc, 0, 'truncate 10T file ')

    """获取nfs客户端上文件的md5值"""
    cmd21 = "ssh %s python %s %s %s %s %s" \
            % (exe_ip, verify_file, nfs_file, offset1, block_size, r_w)
    rc, stdout = common.run_command(exe_ip, cmd21)
    common.judge_rc(rc, 0, 'get nfs client offset data')
    file21_md5 = str(stdout.strip().split()[0])
    print("The %s md5 value of nfs client %s " % (offset1, file21_md5))

    """获取集群客户端上文件的md5值"""
    cmd1 = "python %s %s %s %s %s" \
           % (verify_file, test_file, offset1, block_size, r_w)
    rc, stdout = common.run_command(exe_ip, cmd1)
    common.judge_rc(rc, 0, 'get POSIX client offset data ')
    file1_md5 = str(stdout.strip().split()[0])
    print("The %s md5 value of nfs client %s " % (offset1, file1_md5))
    if file21_md5 != file1_md5:
        log.error('The file was read successfully but the data of %s offset was not correct!!!' % offset1)
        raise Exception('The file was read successfully but the data of %s offset was not correct!!!' % offset1)
    return


def delete_file(file, exe_ip):
    """
        :author:            wanggl
    :date  :            2018.08.7
    :description:       删除文件
    :param file:  所有删除的文件
    :param exe_ip: 外部客户端
    :return: 
    """
    log.info('客户端B通过私有或nas删除该文件')
    rc, stdout = common.rm_exe(exe_ip, file)
    common.judge_rc(rc, 0, 'delete test_file1 ')
    return


def case():
    """若访问分区已经创建好，该步骤需要注释掉"""
    """创建访问分区"""
    access_zone_name = FILE_NAME+"_access_zone_name1"
    ob_node = common.Node()
    node_ids = []
    node_ids = ob_node.get_nodes_id()
    access_zone_node_id_6_1_0_24 = ','.join(str(p) for p in node_ids)
    check_result1 = nas_common.create_access_zone(node_ids=access_zone_node_id_6_1_0_24, name=access_zone_name)
    if check_result1["err_msg"] != "" or check_result1["detail_err_msg"] != "":
        log.error('%s Failed ' % FILE_NAME)
        raise Exception('%s create_access_zone failed!!!' % FILE_NAME)
    id_6_1_0_24 = check_result1["result"]

    """配置共享目录、授权协议、对外IP地址、授权客户端IP"""
    """enable nas"""
    check_result2 = nas_common.enable_nas(access_zone_id=id_6_1_0_24)
    wait_time1 = random.randint(10, 15)
    time.sleep(wait_time1)
    if check_result2["err_msg"] != "" or check_result2["detail_err_msg"] != "":
        log.error('check_result = %s Failed' % (FILE_NAME))
        raise Exception('%s enable_nas failed!!!' % FILE_NAME)

    """查看NAS是否按配置启动"""
    check_result3 = nas_common.get_access_zones(ids=id_6_1_0_24)
    name = check_result3["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        raise Exception('%s enable_nas failed!!!' % FILE_NAME)
    auth_provider_id_6_1_0_24 = check_result3["result"]["access_zones"][0]["auth_provider_id"]

    """创建目录"""
    check_result4 = nas_common.create_file(path=create_file_path)
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s create_file Failed") % FILE_NAME)

    """添加本地用户组/用户"""
    check_result5 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_6_1_0_24,
                                                 name="group_6_1_0_24")

    if check_result5["err_msg"] != "" or check_result4["detail_err_msg"] != "":
        log.error('%s Failed' % (FILE_NAME))
        raise Exception('%s create_auth_group Failed!!!' % FILE_NAME)
    primary_group_id_6_1_0_24 = check_result5["result"]
    """添加本地用户"""
    check_result6 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_6_1_0_24,
                                                name='user_6_1_0_24', password='111111',
                                                primary_group_id=primary_group_id_6_1_0_24)
    if check_result6["err_msg"] != "" or check_result5["detail_err_msg"] != "":
        log.error('%s Failed' % FILE_NAME)
        raise Exception('%s create_auth_user Failed!!!' % FILE_NAME)

    # 导出目录
    nfs_export_name = "nfs_export"+FILE_NAME
    check_result7 = nas_common.create_nfs_export(access_zone_id=id_6_1_0_24,
                                                 export_name=nfs_export_name,
                                                 export_path=create_file_path)
    if check_result7["err_msg"] != "" or check_result7["detail_err_msg"] != "":
        log.error(' %s failed' % FILE_NAME)
        raise Exception('%s create_nfs_export failed!!!' % FILE_NAME)
    nfs_export_id_6_1_0_24 = check_result7["result"]

    """添加nfs nas 用户"""
    """添加nfs客户端1"""
    auth_clients_name1 = nas_common.NFS_1_CLIENT_IP
    auth_clients_permission_level = 'rw'
    auth_permission_constraint = 'no_root_squash'
    check_result8 = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id_6_1_0_24,
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
    check_result8 = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id_6_1_0_24,
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
    common.mkdir_path(auth_clients_name2, auth_clients_mount_dir)
    nfs_file1 = os.path.join(auth_clients_mount_dir, 'test_file1')

    """客户端mount共享路径"""
    wait_time1 = random.randint(8, 10)
    time.sleep(wait_time1)
    cmd1 = "ssh %s mount -t nfs %s:%s %s " \
           % (auth_clients_name1, snap_common.SYSTEM_IP, nfs_path, auth_clients_mount_dir)
    common.run_command(snap_common.CLIENT_IP_1, cmd1)
    cmd2 = "ssh %s mount -t nfs %s:%s %s " \
           % (auth_clients_name2, snap_common.SYSTEM_IP, nfs_path, auth_clients_mount_dir)
    common.run_command(snap_common.CLIENT_IP_1, cmd2)

    test_file1 = os.path.join(nfs_path, 'test_file1')
    cmd = 'touch %s' % test_file1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """"客户端A通过私有或nas 读写一个文件"""
    p1 = Process(target=verify_md5, args=(0, 4194304, 'w', test_file1, nfs_file1, auth_clients_name1))
    p2 = Process(target=delete_file, args=(test_file1, auth_clients_name2))
    p1.start()
    time.sleep(1)
    p2.start()  # 第一个进程开始一段时后开始第二个线程
    p2.join()  # 等待第二个线程执行完成
    p1.join()
    common.judge_rc(p2.exitcode, 0, 'delete file ')
    common.judge_rc(p1.exitcode, 0, 'write/read file ')

    """ 清理环境"""
    cmd = "ssh %s umount %s " %(auth_clients_name1, auth_clients_mount_dir)
    common.run_command(auth_clients_name1, cmd)
    cmd = "ssh %s umount %s " %(auth_clients_name2, auth_clients_mount_dir)
    common.run_command(auth_clients_name2, cmd)

    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info('succeed!')

if __name__ == '__main__':
    common.case_main(main)

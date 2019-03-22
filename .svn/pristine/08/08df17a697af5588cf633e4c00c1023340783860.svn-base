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
import prepare_clean
#=================================================================================
#  latest update:2018-06-22                                                    =
#  Author:wangguanglin                                                           =
#=================================================================================
# 2018-06-22:
# Author：wangguanglin
#@summary：
#   读写过程中快照的创建
#@steps:
#   1、创建3节点访问区，确定nas服务；
#   2、配置共享目录、授权协议、对外IP地址、授权客户端IP；
#   3、linux客户端通过授权的用户挂载目录；
#   4、nfs客户端写入4K文件；
#
#
#   该用例覆盖了nas用例业务类型16-4-1-1 nfs读4k小文件
#   还覆盖了nas用例业务类型16-4-1-5 nfs写4k 小文件
#   还覆盖了nas用例业务类型16-4-1-9 nfs打开4k文件
#   还覆盖了nas用例业务类型16-4-1-11 nfs关闭4k文件
#   还覆盖了nas用例业务类型16-4-1-17 nfs客户端stat4k文件
#   共覆盖了5个用例

#changelog:
######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 #本脚本名字
nfs_path = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/wangguanglin/nas_test_dir/nas_16_4_1_5
create_file_path = os.path.join(nas_common.ROOT_DIR, FILE_NAME)         # wangguanglin:/nas_test_dir/nas_16_4_1_5

def case():
    """若访问分区已经创建好，该步骤需要注释掉"""
    """创建访问分区"""
    access_zone_name = "nas_16_4_1_5_access_zone_name1"
    ob_node = common.Node()
    node_ids = []
    node_ids = ob_node.get_nodes_id()
    print node_ids
    access_zone_node_id_16_4_1_5 = ','.join(str(p) for p in node_ids)
    check_result1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_4_1_5, name=access_zone_name)
    if check_result1["err_msg"] != "" or check_result1["detail_err_msg"] != "":
        log.error('%s Failed ' % FILE_NAME)
        raise Exception('%s create_access_zone failed!!!' % FILE_NAME)
    id_16_4_1_5 = check_result1["result"]

    """配置共享目录、授权协议、对外IP地址、授权客户端IP"""
    """enable nas"""
    check_result2 = nas_common.enable_nas(access_zone_id=id_16_4_1_5)
    wait_time1 = random.randint(10, 15)
    time.sleep(wait_time1)
    if check_result2["err_msg"] != "" or check_result2["detail_err_msg"] != "":
        log.error('check_result = %s Failed' % (FILE_NAME))
        raise Exception('%s enable_nas failed!!!' % FILE_NAME)

    """查看NAS是否按配置启动"""
    check_result3 = nas_common.get_access_zones(ids=id_16_4_1_5)
    name = check_result3["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        raise Exception('%s enable_nas failed!!!' % FILE_NAME)
    auth_provider_id_16_4_1_5 = check_result3["result"]["access_zones"][0]["auth_provider_id"]

    """创建目录"""
    check_result4 = nas_common.create_file(path=create_file_path)
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s create_file Failed") % FILE_NAME)

    """添加本地用户组/用户"""
    check_result5 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_4_1_5,
                                                 name="group_16_4_1_5")
    if check_result5["err_msg"] != "" or check_result4["detail_err_msg"] != "":
        log.error('%s Failed' % (FILE_NAME))
        raise Exception('%s create_auth_group Failed!!!' % FILE_NAME)
    primary_group_id_16_4_1_5 = check_result5["result"]
    """添加本地用户"""
    check_result6 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_16_4_1_5,
                                                name='user_16_4_1_5', password='111111',
                                                primary_group_id=primary_group_id_16_4_1_5)
    if check_result6["err_msg"] != "" or check_result5["detail_err_msg"] != "":
        log.error('%s Failed' % FILE_NAME)
        raise Exception('%s create_auth_user Failed!!!' % FILE_NAME)

    """导出目录"""
    nfs_export_name = "nfs_export"+FILE_NAME
    check_result7 = nas_common.create_nfs_export(access_zone_id=id_16_4_1_5,
                                                 export_name=nfs_export_name,
                                                 export_path=create_file_path)
    if check_result7["err_msg"] != "" or check_result7["detail_err_msg"] != "":
        log.error(' %s failed' % FILE_NAME)
        raise Exception('%s create_nfs_export failed!!!' % FILE_NAME)
    nfs_export_id_16_4_1_5 = check_result7["result"]

    """添加nfs nas 用户"""
    """添加nfs客户端1"""
    auth_clients_name1 = nas_common.NFS_1_CLIENT_IP
    auth_clients_permission_level = 'rw'
    auth_permission_constraint = 'no_root_squash'
    check_result8 = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id_16_4_1_5,
                                                           name=auth_clients_name1,
                                                           permission_level=auth_clients_permission_level,
                                                           permission_constraint=auth_permission_constraint)
    if check_result8["err_msg"] != "" or check_result8["detail_err_msg"] != "":
        log.error(' %s failed' % FILE_NAME)
        raise Exception('%s add_nfs_export_auth_clients failed!!!' % FILE_NAME)

    """客户端mount"""
    global auth_clients_mount_dir
    auth_clients_mount_dir = os.path.join('/mnt/', FILE_NAME)
    cmd1 = "ssh %s mkdir %s" % (auth_clients_name1, auth_clients_mount_dir)
    rc, stdout = common.run_command(auth_clients_name1, cmd1)
    common.judge_rc(rc, 0,'create %s!!!'% auth_clients_mount_dir )

    """客户端mount共享路径"""
    wait_time1 = random.randint(8, 10)
    time.sleep(wait_time1)
    cmd1 = "ssh %s mount -t nfs %s:%s %s " \
           % (auth_clients_name1, snap_common.SYSTEM_IP, nfs_path, auth_clients_mount_dir)
    rc, stdout = common.run_command(auth_clients_name1, cmd1)
    common.judge_rc(rc, 0,'mount nfs  %s!!!'% auth_clients_name1 )

    log.info('nfs客户端写入4K文件，并验证写入文件的正确性')
    offset1=0
    block_size=4096 #块大小为4k
    r_w='w'

    """获取nfs客户端上文件的md5值"""
    '''校验工具'''
    tools_path = get_config.get_tools_path()
    VERIFY_TOOL = os.path.join(tools_path,'verify')
    nfs_file1=os.path.join(auth_clients_mount_dir,'test_file1')
    verify_file=os.path.join(VERIFY_TOOL,'verify_common.py')

    '''nfs客户端创建4k文件'''
    cmd='ssh %s chmod 766 %s '% (auth_clients_name1,nfs_file1)
    common.run_command(auth_clients_name1, cmd)

    cmd = "ssh %s truncate -s 4k %s" %(auth_clients_name1,nfs_file1)
    rc, stdout = common.run_command(auth_clients_name1, cmd)
    common.judge_rc(rc, 0,'nfs client  %s write  %s !!!' % (auth_clients_name1, nfs_file1))

    cmd21 = "ssh %s python %s %s %s %s %s" \
           % (auth_clients_name1,verify_file, nfs_file1,offset1,block_size,r_w)
    rc, stdout = common.run_command(auth_clients_name1, cmd21)
    common.judge_rc(rc, 0,'nfs client  %s gets offset %s data !!!' % (auth_clients_name1, offset1))
    file21_md5=str(stdout.strip().split()[0])
    print("The %s md5 value of nfs client %s " %(offset1, file21_md5))

    """获取集群客户端上文件的md5值"""
    cmd1 = "python %s %s %s %s %s" \
           % (verify_file, nfs_file1,offset1,block_size,r_w)
    rc, stdout = common.run_command(auth_clients_name1, cmd1)
    common.judge_rc(rc, 0,'nfs client  %s gets offset %s data !!!' % (auth_clients_name1, offset1))
    file1_md5=str(stdout.strip().split()[0])
    print("The %s md5 value of nfs client %s " %(offset1, file1_md5))
    common.judge_rc(file21_md5, file1_md5,
                    'The file was read successfully but the data of %s offset was not correct!!!'% offset1)

    """ 清理环境"""
    cmd = "ssh %s umount %s " %(auth_clients_name1, auth_clients_mount_dir)
    common.run_command(auth_clients_name1, cmd)

    return

def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info('succeed!')

if __name__ == '__main__':
    common.case_main(main)





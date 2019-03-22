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
#  latest update:2018-08-22                                                    =
#  author:wangguanglin                                                           =
#=================================================================================
# 2018-08-22:
# 修改者：wangguanglin
#@summary：
#   nfs大文件的访问控制
#@steps:
#   1、部署大容量存储集群；
#   2、挂载2个nfs客户端；
#   3、通过私有客户端创建256T的大文件（可通过python语言或c语言中的truncate函数进行创建）；
#   4、第一个客户端从offset:0的位置每次间隔50T对文件写入4M的数据；
#   5、第二个客户端读写所有写入的4M数据是否正确；
#   6、第二个客户端删除该大文件。
#
   #changelog:
######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
vdb_path = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/wangguanglin/nas_test_dir/cus_6_1_0_28
create_file_path = os.path.join(nas_common.ROOT_DIR, FILE_NAME)         # wangguanglin:/nas_test_dir/cus_6_1_0_28
PRIVATE_CLIENT_IP1 = get_config.get_client_ip(0)
PRIVATE_CLIENT_IP2 = get_config.get_client_ip(1)
PRIVATE_CLIENT_IP3 = get_config.get_client_ip(2)
SYSTEM_IP = get_config.get_parastor_ip()


def case():

    log.info('2> 挂载2个nfs客户端')
    """创建访问分区"""
    access_zone_name = FILE_NAME+"_access_zone_name1"
    ob_node = common.Node()
    node_ids = []
    node_ids = ob_node.get_nodes_id()
    access_zone_node_id_6_1_0_28 = ','.join(str(p) for p in node_ids)
    check_result1 = nas_common.create_access_zone(node_ids=access_zone_node_id_6_1_0_28, name=access_zone_name)
    if check_result1["err_msg"] != "" or check_result1["detail_err_msg"] != "":
        log.error('%s Failed ' % FILE_NAME)
        raise Exception('%s create_access_zone failed!!!' % FILE_NAME)
    id_6_1_0_28 = check_result1["result"]

    """配置共享目录、授权协议、对外IP地址、授权客户端IP"""
    """enable nas"""
    check_result2 = nas_common.enable_nas(access_zone_id=id_6_1_0_28)
    wait_time1 = random.randint(10, 15)
    time.sleep(wait_time1)
    if check_result2["err_msg"] != "" or check_result2["detail_err_msg"] != "":
        log.error('check_result = %s Failed' % (FILE_NAME))
        raise Exception('%s enable_nas failed!!!' % FILE_NAME)

    """查看NAS是否按配置启动"""
    check_result3 = nas_common.get_access_zones(ids=id_6_1_0_28)
    name = check_result3["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        raise Exception('%s enable_nas failed!!!' % FILE_NAME)
    auth_provider_id_6_1_0_28 = check_result3["result"]["access_zones"][0]["auth_provider_id"]

    """创建目录"""
    check_result4 = nas_common.create_file(path=create_file_path)
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s create_file Failed") % FILE_NAME)

    """添加本地用户组/用户"""
    check_result5 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_6_1_0_28,
                                                 name="group_6_1_0_28")

    if check_result5["err_msg"] != "" or check_result4["detail_err_msg"] != "":
        log.error('%s Failed' % (FILE_NAME))
        raise Exception('%s create_auth_group Failed!!!' % FILE_NAME)
    primary_group_id_6_1_0_28 = check_result5["result"]
    """添加本地用户"""
    check_result6 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_6_1_0_28,
                                                name='user_6_1_0_28', password='111111',
                                                primary_group_id=primary_group_id_6_1_0_28)
    if check_result6["err_msg"] != "" or check_result5["detail_err_msg"] != "":
        log.error('%s Failed' % FILE_NAME)
        raise Exception('%s create_auth_user Failed!!!' % FILE_NAME)

    # 导出目录
    nfs_export_name = "nfs_export"+FILE_NAME
    check_result7 = nas_common.create_nfs_export(access_zone_id=id_6_1_0_28,
                                                 export_name=nfs_export_name,
                                                 export_path=create_file_path)
    if check_result7["err_msg"] != "" or check_result7["detail_err_msg"] != "":
        log.error(' %s failed' % FILE_NAME)
        raise Exception('%s create_nfs_export failed!!!' % FILE_NAME)
    nfs_export_id_6_1_0_28 = check_result7["result"]

    """添加nfs nas 用户"""
    """添加nfs客户端1"""
    auth_clients_name1 = get_config.get_client_ip(3)
    auth_clients_permission_level = 'rw'
    auth_permission_constraint = 'no_root_squash'
    check_result8 = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id_6_1_0_28,
                                                           name=auth_clients_name1,
                                                           permission_level=auth_clients_permission_level,
                                                           permission_constraint=auth_permission_constraint)
    if check_result8["err_msg"] != "" or check_result8["detail_err_msg"] != "":
        log.error(' %s failed' % FILE_NAME)
        raise Exception('%s add_nfs_export_auth_clients failed!!!' % FILE_NAME)

    """添加nfs客户端2"""
    auth_clients_name2 = get_config.get_client_ip(4)
    auth_clients_permission_level = 'rw'
    auth_permission_constraint = 'no_root_squash'
    check_result8 = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id_6_1_0_28,
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

    log.info('3> 通过私有客户端创建256T的大文件（可通过python语言或c语言中的truncate函数进行创建）')
    common.mkdir_path(PRIVATE_CLIENT_IP1, vdb_path)
    test_file1=os.path.join(vdb_path,'test_file1')
    cmd = "ssh %s truncate -s 256T %s" %(PRIVATE_CLIENT_IP1,test_file1)
    rc, stdout = common.run_command(PRIVATE_CLIENT_IP1, cmd)
    common.judge_rc(rc, 0, 'truncate 256T file')

    log.info('4> 第一个客户端从offset:0的位置每次间隔50T对文件写入4M的数据')
    offset1 = 54975581388800 #50T=50*1024*1024*1024*1024
    block_size = 4194304 #块大小为4M
    r_w = 'w'

    '''校验工具'''
    tools_path = get_config.get_tools_path()
    VERIFY_TOOL = os.path.join(tools_path,'verify')
    verify_file=os.path.join(VERIFY_TOOL,'verify_common.py')

    log.info(' 第一个客户端读写所有写入的4M数据是否正确')
    cmd21 = "ssh %s python %s %s %s %s %s" \
           % (PRIVATE_CLIENT_IP1,verify_file, test_file1,offset1,block_size,r_w)
    rc, stdout = common.run_command(PRIVATE_CLIENT_IP1, cmd21)
    common.judge_rc(rc, 0, 'the first private client %s get offset %s data '%(PRIVATE_CLIENT_IP1,offset1))
    file21_md5=str(stdout.strip().split()[0])
    print("The %s md5 value of the first private client %s " %(offset1, file21_md5))

    log.info('5> 第二个客户端读写所有写入的4M数据是否正确')
    cmd1 = "ssh %s python %s %s %s %s %s" \
           % (PRIVATE_CLIENT_IP2,verify_file, test_file1,offset1,block_size,r_w)
    rc, stdout = common.run_command(PRIVATE_CLIENT_IP2, cmd1)
    common.judge_rc(rc, 0, 'the second private client %s get offset %s data '%(PRIVATE_CLIENT_IP2,offset1))
    file1_md5=str(stdout.strip().split()[0])
    print("The %s md5 value of nfs client %s " %(offset1, file1_md5))
    common.judge_rc(file21_md5, file1_md5,
                    'The file was read successfully but the data of %s offset was not correct!!!'% offset1)

    log.info('6> 第二个客户端删除该大文件')
    cmd = "rm -rf %s"% test_file1
    rc, stdout = common.run_command(PRIVATE_CLIENT_IP2, cmd1)
    common.judge_rc(rc, 0, 'the second private client %s remove %s '%(PRIVATE_CLIENT_IP2,test_file1))

    """ 清理环境"""
    cmd = "ssh %s umount %s " %(auth_clients_name1, auth_clients_mount_dir)
    common.run_command(auth_clients_name1, cmd)
    cmd = "ssh %s umount %s " %(auth_clients_name2, auth_clients_mount_dir)
    common.run_command(auth_clients_name2, cmd)

def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info('succeed!')

if __name__ == '__main__':
    common.case_main(main)







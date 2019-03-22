# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random
import re

import utils_path
import common
import log
import prepare_clean
import get_config
import nas_common
import make_fault
import snap_common
import tool_use

#########################################################
# author: liyao
# 概述：创建任意宽度和深度的目录，各目录随机作为任一协议的导出目录；nfs和smb的导出目录包含客户端授权
#########################################################


VOLUME_NAME = get_config.get_one_volume_name()
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字
NAS_PATH = get_config.get_one_nas_test_path()                            # /mnt/volume/nas_test_dir
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/volume/nas_test_dir/nas_16_6_0_16
BASE_NAS_PATH = os.path.dirname(NAS_PATH)                                # /mnt/volume
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)                           # nas_test_dir
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


def nfs_export_auth(access_zone_id, order_num, export_path):
    nfs_name_base = 'nfs_export'
    nfs_name = nfs_name_base + '_%s' % order_num
    exe_info = nas_common.create_nfs_export(access_zone_id, nfs_name, export_path)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('create nfs export failed !!!')
    nfs_export_id = exe_info['result']

    client_ip_list = ['20.2.42.128', '*', '20.2.42.201/22']   # 为了测试客户端授权格式，ip可任意指定
    for mem in client_ip_list:
        permission_level = random.choice(['rw', 'ro', 'rw_nodelsacl'])
        write_mode = random.choice(['sync', 'async'])
        exe_info = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id, name=mem,
                                                          permission_level=permission_level, write_mode=write_mode)
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('add nfs auth client failed !!!')


def smb_export_auth(access_zone_id, order_num, export_path, local_user_list):
    smb_name_base = 'smb_export'
    smb_name = smb_name_base + '_%s' % order_num
    enable_ntfs_acl = random.choice(['true', 'false'])
    allow_create_ntfs_acl = random.choice(['true', 'false'])
    enable_alternative_datasource = random.choice(['true', 'false'])
    enable_dos_attributes = random.choice(['true', 'false'])
    enable_os2style_ex_attrs = random.choice(['true', 'false'])
    enable_guest = random.choice(['true', 'false'])
    enable_oplocks = random.choice(['true', 'false'])
    exe_info = nas_common.create_smb_export(access_zone_id, smb_name, export_path, enable_ntfs_acl=enable_ntfs_acl,
                                            allow_create_ntfs_acl=allow_create_ntfs_acl,
                                            enable_alternative_datasource=enable_alternative_datasource,
                                            enable_dos_attributes=enable_dos_attributes,
                                            enable_os2style_ex_attrs=enable_os2style_ex_attrs,
                                            enable_guest=enable_guest, enable_oplocks=enable_oplocks)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('create smb export failed !!!')
    smb_export_id = exe_info['result']
    for mem in local_user_list:
        run_as_root = random.choice(['true', 'false'])
        if run_as_root == 'false':
            permission_level = random.choice(['ro', 'rw', 'full_control'])
            exe_info = nas_common.add_smb_export_auth_clients(smb_export_id, name=mem,
                                                              user_type='USER', run_as_root=run_as_root,
                                                              permission_level=permission_level)
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                common.except_exit('add smb auth client failed !!!')
        else:
            exe_info = nas_common.add_smb_export_auth_clients(smb_export_id, name=mem, user_type='USER', run_as_root=run_as_root)
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                common.except_exit('add smb auth client failed !!!')


def ftp_export(access_zone_id, export_path, local_user_list):
    for mem in local_user_list:
        enable_dirlist = random.choice(['true', 'false'])
        enable_create_folder = random.choice(['true', 'false'])
        enable_delete_and_rename = random.choice(['true', 'false'])
        enable_upload = random.choice(['true', 'false'])
        if enable_upload == 'true':
            upload_local_max_rate = random.randint(0, 1000)
        else:
            upload_local_max_rate = None
        enable_download = random.choice(['true', 'false'])
        if enable_download == 'true':
            download_local_max_rate = random.randint(0, 1000)
        else:
            download_local_max_rate = None
        exe_info = nas_common.create_ftp_export(access_zone_id, mem, export_path, enable_dirlist=enable_dirlist,
                                                enable_create_folder=enable_create_folder,
                                                enable_delete_and_rename=enable_delete_and_rename,
                                                enable_upload=enable_upload, upload_local_max_rate=upload_local_max_rate,
                                                enable_download=enable_download, download_local_max_rate=download_local_max_rate)
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('create ftp export failed !!!')


def case():
    """1> 获取基本信息"""
    '''获取访问分区id'''
    node = common.Node()
    ids = node.get_nodes_id()
    node_ids = ','.join(str(p) for p in ids)
    name = 'access_zone_name'
    msg = nas_common.create_access_zone(node_ids=node_ids, name=name)
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        common.except_exit('create_access_zone failed!!!')
    access_zone_id = msg["result"]

    '''启动nas服务'''
    exe_info = nas_common.enable_nas(access_zone_id=access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('enable nas failed!!!')

    '''获取local认证服务器id'''
    exe_info = nas_common.get_auth_providers_local()
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('get auth provider ad failed !!!')
    local_provider_id = exe_info['result']['auth_providers'][0]['id']

    """2> 创建多用户组和多用户"""
    group_name_base = 'a_group_local'
    user_name_base = 'user_local'
    group_id_list = []
    user_id_list = []
    user_name_list = []   # 保存本地用户名
    group_name_list = []  # 保存本地用户组名
    group_num = 2
    user_num = 5
    for i in range(group_num):
        group_name = group_name_base + '_%s' % i
        exe_info = nas_common.create_auth_group(local_provider_id, group_name)
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('create auth group failed !!!')
        group_id = exe_info['result']
        group_id_list.append(group_id)
        group_name_list.append(group_name)
        for j in range(user_num):
            user_name = user_name_base + '_g%s' % i + '_%s' % j
            exe_info = nas_common.create_auth_user(local_provider_id, user_name, '111111', group_id)
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                common.except_exit('create auth user failed !!!')
            user_id = exe_info['result']
            user_id_list.append(user_id)
            user_name_list.append(user_name)

    """3> 创建嵌套目录，各层目录作为不同协议的导出路径"""
    path_base = VOLUME_NAME + ':/' + os.path.join(NAS_PATH_BASENAME, FILE_NAME)
    abs_path_base = NAS_TRUE_PATH
    dir_name_base = 'trunk'
    export_path = path_base

    export_path_list = []

    width_dir_num_init = 4   # 目录初始宽度
    for k in range(width_dir_num_init):
        width_path_base = abs_path_base + '/' + dir_name_base + '_%s' % k
        export_width_path_base = export_path + '/' + dir_name_base + '_%s' % k
        cmd = 'mkdir -p %s' % width_path_base
        common.run_command(SYSTEM_IP_0, cmd)
        export_path_list.append(export_width_path_base)

        width_dir_num = random.randint(2, 5)  # 子目录深度随机选定
        for i in range(width_dir_num):
            width_path_base = width_path_base + '/' + dir_name_base + '_%s' % i
            export_width_path_base = export_width_path_base + '/' + dir_name_base + '_%s' % i
            cmd = 'mkdir -p %s' % width_path_base
            common.run_command(SYSTEM_IP_2, cmd)
            export_path_list.append(export_width_path_base)

            depth_dir_num = random.randint(2, 5)   # 子目录宽度随机选定
            for j in range(depth_dir_num):
                abs_path = width_path_base + '/' + dir_name_base + '_%s' % j
                dir_path = export_width_path_base + '/' + dir_name_base + '_%s' % j
                cmd = 'mkdir -p %s' % abs_path
                common.run_command(SYSTEM_IP_1, cmd)
                export_path_list.append(dir_path)

    export_path_list = list(set(export_path_list))   # 去除重复元素
    export_num = len(export_path_list)
    for i in range(export_num):
        protocol_type = random.choice(['nfs', 'smb', 'ftp'])
        if protocol_type == 'nfs':
            nfs_export_auth(access_zone_id, i, export_path_list[i])
        elif protocol_type == 'smb':
            smb_export_auth(access_zone_id, i, export_path_list[i], user_name_list)
        else:
            ftp_export(access_zone_id, export_path_list[i], user_name_list)

    """启动nas服务"""
    exe_info = nas_common.enable_nas(access_zone_id=access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('enable nas failed !!!')

    return


def nas_main():
    log_file_path = log.get_log_path(FILE_NAME)
    log.init(log_file_path, True)
    case()
    # prepare_clean.nas_test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    nas_main()

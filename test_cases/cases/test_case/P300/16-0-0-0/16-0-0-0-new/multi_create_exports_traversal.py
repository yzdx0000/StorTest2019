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
# 概述：遍历多种协议的所有参数（包含主要参数及次要参数）
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


def create_nfs_export_auth(access_zone_id, export_path_list, local_user_id, local_group_id):
    order_num = 0
    nfs_name_base = 'nfs_export'
    nfs_export_list = []   # nfs导出id列表
    description_list = ['', 'parastor nfs protocol']
    export_path_part_list = export_path_list[:300]
    for mem in export_path_part_list:
        nfs_name = nfs_name_base + '_%s' % order_num
        order_num = order_num + 1
        description = random.choice(description_list)
        exe_info = nas_common.create_nfs_export(access_zone_id, nfs_name, mem, "'%s'" % description)
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('create nfs export failed !!!')
        nfs_export_list.append(exe_info['result'])

    '''nfs客户端授权，各种参数进行遍历'''
    nfs_auth_list = []   # nfs授权id列表
    nfs_export_check_list = nfs_export_list   # 遍历授权参数时，每种情况对应一个导出目录，每次将用过的导出目录从check_list中剔除
    client_ip_list = ['20.2.42.128', '*', '20.2.42.201/22']  # 为了测试客户端授权格式，ip可任意指定;每个导出中包含列表中三种形式的客户端授权
    permission_level = ['rw', 'ro', 'rw_nodelsacl']
    write_mode = ['sync', 'async']
    port_constraint = ['secure', 'insecure']
    permission_constraint = ['all_squash', 'root_squash', 'no_root_squash']
    for mem1 in permission_level:
        for mem2 in write_mode:
            for mem3 in port_constraint:
                for mem4 in permission_constraint:
                    if mem4 == 'all_squash' or mem4 == 'root_squash':
                        anonuid = random.randint(1, 65536)
                        anongid = random.randint(1, 65536)
                        for name in client_ip_list:
                            exe_info = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_check_list[0], name=name,
                                                                              permission_level=mem1, write_mode=mem2,
                                                                              port_constraint=mem3, permission_constraint=mem4,
                                                                              anonuid=anonuid, anongid=anongid)
                            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                                common.except_exit('add nfs auth client failed !!!')
                            nfs_auth_list.append(exe_info['result'][0])
                        nfs_export_check_list.remove(nfs_export_check_list[0])
                    else:
                        for name in client_ip_list:
                            exe_info = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_check_list[0],
                                                                              name=name,
                                                                              permission_level=mem1, write_mode=mem2,
                                                                              port_constraint=mem3,
                                                                              permission_constraint=mem4)
                            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                                common.except_exit('add nfs auth client failed !!!')
                            nfs_auth_list.append(exe_info['result'][0])
                        nfs_export_check_list.remove(nfs_export_check_list[0])
    return nfs_export_list, nfs_auth_list



def create_smb_export_auth(access_zone_id, export_path_list, local_user_list, local_group_list):
    order_num = 0
    smb_name_base = 'smb_export'
    smb_export_list = []  # smb导出id列表
    export_path_list = export_path_list[20:]   # 取列表切片，使得前n个路径为nfs导出独有，后面的路径存在复用情况
    description_list = ['', 'parastor smb export']
    export_path_check_list = export_path_list   # 遍历授权参数时，每种情况对应一个导出目录，每次将用过的导出目录从check_list中剔除;
                                                # 目录数目不足时进行补充创建extra_smb_export_path
    enable_ntfs_acl = ['true', 'false']
    allow_create_ntfs_acl = ['true', 'false']
    enable_alternative_datasource = ['true', 'false']
    enable_dos_attributes = ['true', 'false']
    enable_os2style_ex_attrs = ['true', 'false']
    enable_guest = ['true', 'false']
    enable_oplocks = ['true', 'false']
    authorization_ip = [None, '20.2.42.128,20.2.42.129', '20.2.42.121', '20.2.42.1/22', "'20.2.1. EXCEPT 20.2.1.2 20.2.1.3'"]
                                                                                        # 授权ip的各种形式，具体ip可任意指定
    for mem1 in enable_ntfs_acl:
        for mem2 in allow_create_ntfs_acl:
            for mem3 in enable_alternative_datasource:
                for mem4 in enable_dos_attributes:
                    for mem5 in enable_os2style_ex_attrs:
                        for mem6 in enable_guest:
                            for mem7 in enable_oplocks:
                                for ip in authorization_ip:
                                    smb_name = smb_name_base + '_%s' % order_num
                                    order_num = order_num + 1
                                    description = random.choice(description_list)
                                    exe_info = nas_common.create_smb_export(access_zone_id, smb_name, export_path_check_list[0],
                                                                            enable_ntfs_acl=mem1, description="'%s'" % description,
                                                                            allow_create_ntfs_acl=mem2,
                                                                            enable_alternative_datasource=mem3,
                                                                            enable_dos_attributes=mem4,
                                                                            enable_os2style_ex_attrs=mem5,
                                                                            enable_guest=mem6,
                                                                            enable_oplocks=mem7, authorization_ip=ip)
                                    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                                        common.except_exit('create smb export failed !!!')
                                    smb_export_list.append(exe_info['result'])
                                    export_path_check_list.remove(export_path_check_list[0])

    '''smb客户端授权，各种参数进行遍历'''
    smb_auth_list = []   # smb授权列表
    run_as_root = ['true', 'false']
    permission_level = ['ro', 'rw', 'full_control']
    for mem1 in run_as_root:
        if mem1 == 'false':
            for mem2 in permission_level:   # 由于用户组无法批量删除，不方便使用，故此处授权均为用户；添加用户组可单独设置
                user = local_user_list[0]
                for smb_id in smb_export_list:
                    exe_info = nas_common.add_smb_export_auth_clients(smb_id, name=user,
                                                                      user_type='USER', run_as_root='false',
                                                                      permission_level=mem2)
                    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                        common.except_exit('add smb auth client failed !!!')
                    smb_auth_list.append(exe_info['result'][0])
                local_user_list.remove(local_user_list[0])

                group = local_group_list[0]
                for smb_id in smb_export_list:
                    exe_info = nas_common.add_smb_export_auth_clients(smb_id, name=group,
                                                                      user_type='GROUP', run_as_root='false',
                                                                      permission_level=mem2)
                    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                        common.except_exit('add smb auth client failed !!!')
                    smb_auth_list.append(exe_info['result'][0])
                local_group_list.remove(local_group_list[0])
        else:
            user = local_user_list[0]
            for smb_id in smb_export_list:
                exe_info = nas_common.add_smb_export_auth_clients(smb_id, name=user, user_type='USER',
                                                                  run_as_root='true')
                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                    common.except_exit('add smb auth client failed !!!')
                smb_auth_list.append(exe_info['result'][0])
            local_user_list.remove(local_user_list[0])

            group = local_group_list[0]
            for smb_id in smb_export_list:
                exe_info = nas_common.add_smb_export_auth_clients(smb_id, name=group, user_type='GROUP',
                                                                  run_as_root='true')
                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                    common.except_exit('add smb auth client failed !!!')
                smb_auth_list.append(exe_info['result'][0])
            local_group_list.remove(local_group_list[0])

    return smb_export_list, smb_auth_list


def create_ftp_export(access_zone_id, export_path_list, local_user_list):
    ftp_export_list = []  # ftp导出id列表
    export_path_list = export_path_list[15:]   # 取列表切片，使得部分路径存在复用情况
    export_path_check_list = export_path_list   # 遍历授权参数时，每种情况对应一个导出目录，每次将用过的导出目录从check_list中剔除;
                                                # 目录数目不足时进行补充创建extra_ftp_export_path
    local_user_check_list = local_user_list
    enable_dirlist = ['true', 'false']
    enable_create_folder = ['true', 'false']
    enable_delete_and_rename = ['true', 'false']
    enable_upload = ['true', 'false']
    enable_download = ['true', 'false']
    for mem1 in enable_dirlist:
        for mem2 in enable_create_folder:
            for mem3 in enable_delete_and_rename:
                for mem4 in enable_upload:
                    if mem4 == 'true':
                        upload_local_max_rate = random.randint(0, 1000)
                        for mem5 in enable_download:
                            if mem5 == 'true':
                                download_local_max_rate = random.randint(0, 1000)
                                exe_info = nas_common.create_ftp_export(access_zone_id, local_user_check_list[0], export_path_check_list[0],
                                                                        enable_dirlist=mem1,
                                                                        enable_create_folder=mem2,
                                                                        enable_delete_and_rename=mem3,
                                                                        enable_upload=mem4,
                                                                        upload_local_max_rate=upload_local_max_rate,
                                                                        enable_download=mem5,
                                                                        download_local_max_rate=download_local_max_rate)
                                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                                    common.except_exit('create ftp export failed !!!')
                                ftp_export_list.append(exe_info['result'])
                                local_user_check_list.remove(local_user_check_list[0])
                                export_path_check_list.remove(export_path_check_list[0])
                            else:
                                exe_info = nas_common.create_ftp_export(access_zone_id, local_user_check_list[0], export_path_check_list[0],
                                                                        enable_dirlist=mem1,
                                                                        enable_create_folder=mem2,
                                                                        enable_delete_and_rename=mem3,
                                                                        enable_upload=mem4,
                                                                        upload_local_max_rate=upload_local_max_rate,
                                                                        enable_download=mem5)
                                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                                    common.except_exit('create ftp export failed !!!')
                                ftp_export_list.append(exe_info['result'])
                                local_user_check_list.remove(local_user_check_list[0])
                                export_path_check_list.remove(export_path_check_list[0])
                    else:
                        for mem5 in enable_download:
                            if mem5 == 'true':
                                download_local_max_rate = random.randint(0, 1000)
                                exe_info = nas_common.create_ftp_export(access_zone_id, local_user_check_list[0], export_path_check_list[0],
                                                                        enable_dirlist=mem1,
                                                                        enable_create_folder=mem2,
                                                                        enable_delete_and_rename=mem3,
                                                                        enable_upload=mem4,
                                                                        enable_download=mem5,
                                                                        download_local_max_rate=download_local_max_rate)
                                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                                    common.except_exit('create ftp export failed !!!')
                                ftp_export_list.append(exe_info['result'])
                                local_user_check_list.remove(local_user_check_list[0])
                                export_path_check_list.remove(export_path_check_list[0])
                            else:
                                exe_info = nas_common.create_ftp_export(access_zone_id, local_user_check_list[0], export_path_check_list[0],
                                                                        enable_dirlist=mem1,
                                                                        enable_create_folder=mem2,
                                                                        enable_delete_and_rename=mem3,
                                                                        enable_upload=mem4, enable_download=mem5)
                                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                                    common.except_exit('create ftp export failed !!!')
                                ftp_export_list.append(exe_info['result'])
                                local_user_check_list.remove(local_user_check_list[0])
                                export_path_check_list.remove(export_path_check_list[0])
    return ftp_export_list


def case():
    """1> 获取基本信息"""
    """创建访问分区"""
    obj_node = common.Node()
    nodes_id_list = obj_node.get_nodes_id()
    nodes_id_str = ','.join(str(p) for p in nodes_id_list)
    access_zone_name = 'az_local'
    exe_info = nas_common.create_access_zone(nodes_id_str, access_zone_name)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create access zone %s failed !!!' % access_zone_name)
        raise Exception('create access zone %s failed !!!' % access_zone_name)
    access_zone_id = exe_info['result']

    '''启动nas服务'''
    exe_info = nas_common.enable_nas(access_zone_id=access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('enable nas failed !!!')

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
    group_num = 5
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

    '''创建ftp单独使用的用户组和用户（每个ftp导出需要对应一个用户，所需用户数目过多，不适于放入nfs和smb的循环中）'''
    ftp_group_name_base = 'ftp_group_local'
    ftp_user_name_base = 'ftp_user_local'
    ftp_group_id_list = []
    ftp_user_id_list = []
    ftp_user_name_list = []  # 保存本地用户名
    ftp_group_name_list = []  # 保存本地用户组名
    ftp_group_num = 5
    ftp_user_num = 100
    for i in range(ftp_group_num):
        ftp_group_name = ftp_group_name_base + '_%s' % i
        exe_info = nas_common.create_auth_group(local_provider_id, ftp_group_name)
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('create ftp auth group failed !!!')
        ftp_group_id = exe_info['result']
        ftp_group_id_list.append(ftp_group_id)
        ftp_group_name_list.append(ftp_group_name)
        for j in range(ftp_user_num):
            ftp_user_name = ftp_user_name_base + '_g%s' % i + '_%s' % j
            exe_info = nas_common.create_auth_user(local_provider_id, ftp_user_name, '111111', ftp_group_id)
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                common.except_exit('create ftp auth user failed !!!')
            ftp_user_id = exe_info['result']
            ftp_user_id_list.append(ftp_user_id)
            ftp_user_name_list.append(ftp_user_name)

    """3> 创建嵌套目录，各层目录作为不同协议的导出路径"""
    path_base = VOLUME_NAME + ':/' + os.path.join(NAS_PATH_BASENAME, FILE_NAME)
    abs_path_base = NAS_TRUE_PATH
    dir_name_base = 'trunk'
    export_path = path_base

    export_path_list = []

    width_dir_num_init = 10   # 目录初始宽度
    for k in range(width_dir_num_init):
        width_path_base = abs_path_base + '/' + dir_name_base + '_%s' % k
        export_width_path_base = export_path + '/' + dir_name_base + '_%s' % k
        cmd = 'mkdir -p %s' % width_path_base
        common.run_command(SYSTEM_IP_0, cmd)
        export_path_list.append(export_width_path_base)

        width_dir_num = random.randint(6, 15)  # 子目录深度随机选定
        for i in range(width_dir_num):
            width_path_base = width_path_base + '/' + dir_name_base + '_%s' % i
            export_width_path_base = export_width_path_base + '/' + dir_name_base + '_%s' % i
            cmd = 'mkdir -p %s' % width_path_base
            common.run_command(SYSTEM_IP_2, cmd)
            export_path_list.append(export_width_path_base)

            depth_dir_num = random.randint(6, 15)   # 子目录宽度随机选定
            for j in range(depth_dir_num):
                abs_path = width_path_base + '/' + dir_name_base + '_%s' % j
                dir_path = export_width_path_base + '/' + dir_name_base + '_%s' % j
                cmd = 'mkdir -p %s' % abs_path
                common.run_command(SYSTEM_IP_1, cmd)
                export_path_list.append(dir_path)

    export_path_list = list(set(export_path_list))   # 去除重复元素

    """4> 多种协议，多种授权形式"""

    create_nfs_export_auth(access_zone_id, export_path_list, user_id_list, group_id_list)
    create_smb_export_auth(access_zone_id, export_path_list, user_name_list, group_name_list)
    create_ftp_export(access_zone_id, export_path_list, ftp_user_name_list)

    return


def nas_main():
    # log_file_path = log.get_log_path(FILE_NAME)
    # log.init(log_file_path, True)
    prepare_clean.nas_test_prepare(FILE_NAME)
    prepare_clean.nas_test_clean()
    case()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    nas_main()

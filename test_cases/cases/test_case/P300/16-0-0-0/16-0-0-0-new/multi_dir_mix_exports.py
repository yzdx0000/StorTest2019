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
# 概述：3种协议，各协议对应多层嵌套目录（纵向延申），各层目录分别导出（不同协议之前无公用的共享目录）
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
    group_name_base = 'local_group'
    user_name_base = 'local_user'
    group_id_list = []
    user_id_list = []
    user_name_list = []   # 保存本地用户名
    group_name_list = []  # 保存本地用户组名
    group_num = 5
    user_num = 50
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

    '''3> 列表保存待授权IP, nfs导出, 各导出目录添加指定数目的用户'''
    client_ip_list = ['20.2.42.201/22', '*']
    client_ip_num = 100
    for i in range(client_ip_num):
        tmp_ip = '20.2.42.' + str(i + 1)
        client_ip_list.append(tmp_ip)

    nfs_auth_client_list = []   # 存放授权客户端结果的列表
    nfs_export_num = 50
    nfs_name_base = 'nfs_export'
    nfs_path_base = VOLUME_NAME + ':/' + os.path.join(NAS_PATH_BASENAME, FILE_NAME)
    abs_nfs_path_base = NAS_TRUE_PATH
    nfs_export_id_list = []

    for i in range(nfs_export_num):
        nfs_name = nfs_name_base + '_%s' % i
        nfs_path = nfs_path_base + '/nfs_export_%s' % i
        abs_nfs_path = abs_nfs_path_base + '/nfs_export_%s' % i
        cmd = 'mkdir -p %s' % abs_nfs_path
        common.run_command(SYSTEM_IP_2, cmd)

        exe_info = nas_common.create_nfs_export(access_zone_id, nfs_name, nfs_path)
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('create nfs export %s failed !!!' % str(i))
        nfs_export_id_list.append(exe_info['result'])

    for mem in nfs_export_id_list:
        nfs_auth_client_num = random.randint(50, 100)   # 各导出目录下添加随机数量的用户
        for i in range(nfs_auth_client_num):
            auth_name_ip = client_ip_list[i]
            permission_level = random.choice(['rw', 'ro', 'rw_nodelsacl'])
            write_mode = random.choice(['sync', 'async'])
            exe_info = nas_common.add_nfs_export_auth_clients(export_id=mem, name=auth_name_ip,
                                                              permission_level=permission_level, write_mode=write_mode)
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                common.except_exit('add nfs auth client %s failed !!!' % str(i))
            nfs_auth_client_list.append(exe_info['result'][0])

    '''4> 创建smb导出，各导出路径中添加用户'''
    smb_name_base = 'smb_export'
    smb_export_id_list = []
    smb_export_num = 50   # smb导出的数目
    smb_path_base = VOLUME_NAME + ':/' + os.path.join(NAS_PATH_BASENAME, FILE_NAME)
    abs_smb_path_base = NAS_TRUE_PATH
    various_ip_type = ['20.2.42.1,20.2.41.2,20.2.41.3', '20.2.42.2/24', "'20.2.43. EXCEPT 20.2.43.1 20.2.43.100'", None]

    for i in range(smb_export_num):
        smb_name = smb_name_base + '_%s' % i
        smb_path = smb_path_base + '/smb_export_%s' % i
        abs_smb_path = abs_smb_path_base + '/smb_export_%s' % i
        cmd = 'mkdir -p %s' % abs_smb_path
        common.run_command(SYSTEM_IP_0, cmd)
        enable_ntfs_acl = random.choice(['true', 'false'])
        allow_create_ntfs_acl = random.choice(['true', 'false'])
        enable_alternative_datasource =random.choice(['true', 'false'])
        enable_dos_attributes = random.choice(['true', 'false'])
        enable_os2style_ex_attrs = random.choice(['true', 'false'])
        enable_guest = random.choice(['true', 'false'])
        enable_oplocks = random.choice(['true', 'false'])
        authorization_ip = random.choice(various_ip_type)
        exe_info = nas_common.create_smb_export(access_zone_id, smb_name, smb_path, enable_ntfs_acl=enable_ntfs_acl,
                                                allow_create_ntfs_acl=allow_create_ntfs_acl,
                                                enable_alternative_datasource=enable_alternative_datasource,
                                                enable_dos_attributes=enable_dos_attributes,
                                                enable_os2style_ex_attrs=enable_os2style_ex_attrs,
                                                enable_guest=enable_guest, enable_oplocks=enable_oplocks,
                                                authorization_ip=authorization_ip)
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('create smb export failed !!!')
        smb_export_id_list.append(exe_info['result'])

    for mem in smb_export_id_list:
        smb_client_num = random.randint(50, 100)   # 各smb导出目录中添加的用户数目,为了方便后续添加授权用户，此数目应小于本地用户总数目(user_num * group_num)
        for j in range(smb_client_num):
            '''任选授权对象为用户/用户组, 选择对应的用户/用户组名称'''
            type = random.choice(['USER', 'GROUP'])
            if type == 'USER':
                name = user_name_list[j]
            else:
                extra_group_name = 'extra_group_g%s' % mem + '_%s' % j    # 如果type选择为group，额外创建用户组来满足添加授权的需要
                name = extra_group_name
                exe_info = nas_common.create_auth_group(local_provider_id, name)
                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                    common.except_exit('create auth group %s failed !!!' % extra_group_name)

            run_as_root = random.choice(['true', 'false'])
            if run_as_root == 'false':
                permission_level = random.choice(['ro', 'rw', 'full_control'])
                exe_info = nas_common.add_smb_export_auth_clients(mem, name=name, user_type=type,
                                                                  run_as_root=run_as_root,
                                                                  permission_level=permission_level)
                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                    common.except_exit('add smb auth client failed !!!')
            else:
                exe_info = nas_common.add_smb_export_auth_clients(mem, name=name, user_type=type,
                                                                  run_as_root=run_as_root)
                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                    common.except_exit('add smb auth client failed !!!')

    '''5> 创建ftp导出，各导出目录添加用户'''
    ftp_path_base = VOLUME_NAME + ':/' + os.path.join(NAS_PATH_BASENAME, FILE_NAME)
    abs_ftp_path_base = NAS_TRUE_PATH
    ftp_export_num = 50
    for i in range(ftp_export_num):
        ftp_path = ftp_path_base + '/ftp_export_%s' % i
        abs_ftp_path = abs_ftp_path_base + '/ftp_export_%s' % i
        cmd = 'mkdir -p %s' % abs_ftp_path
        common.run_command(SYSTEM_IP_1, cmd)
        exe_info = nas_common.create_ftp_export(access_zone_id, user_name_list[i], ftp_path)
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('create ftp export failed !!!')

    return


def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    # log_file_path = log.get_log_path(FILE_NAME)
    # log.init(log_file_path, True)
    case()
    # prepare_clean.nas_test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    nas_main()

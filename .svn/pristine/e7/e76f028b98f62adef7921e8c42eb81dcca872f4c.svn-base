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
# 概述：创建任意宽度和深度的目录；测试各种协议导出及授权的多种删除方法
# 过程：1、创建3种协议并添加客户端授权（主要参数遍历，次要参数随机选择）
#      2、对于nfs/smb，分别保存无授权的导出id和有授权的导出id；保存所有授权客户端id（方便选择性删除）
#      3、对于ftp，保存所有导出id
#      4、设置客户端授权删除开关，用来控制是否先删除授权再删除协议导出
#      5、循环进行3种协议的单个/批量删除（直到不再满足删除条件）
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


def ntime_mix_export(ntime):
    '''n层嵌套目录，各层目录协议类型任选'''
    abs_dir_lst = []
    export_dir_lst = []
    abs_dir = NAS_TRUE_PATH
    export_dir = VOLUME_NAME + ':/' + os.path.join(NAS_PATH_BASENAME, FILE_NAME)
    for i in range(ntime):
        abs_dir = os.path.join(abs_dir, 'dir_%s' % i)
        cmd = 'mkdir -p %s'% abs_dir
        common.run_command(SYSTEM_IP_0, cmd)
        abs_dir_lst.append(abs_dir)

        export_dir = os.path.join(export_dir, 'dir_%s' % i)
        export_dir_lst.append(export_dir)

    return export_dir_lst


def create_nfs_export_auth(access_zone_id, export_path_list):
    order_num = 0
    nfs_name_base = 'nfs_export'
    nfs_export_list = []   # nfs导出id列表
    description_list = ['', 'parastor nfs protocol']
    export_path_part_list = export_path_list[:50]
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
    auth_num = random.randint(10, len(nfs_export_list)-3)   # 进行客户端授权的导出目录数（‘-3’是为了防止auth_num = len(nfs_export_list)）
    without_auth_lst = nfs_export_list[auth_num:]   # 只导出，无授权的nfs共享策略列表
    with_auth_lst = nfs_export_list[:auth_num]
    auth_num_left = len(without_auth_lst)   # 不进行客户端授权的导出目录数
    nfs_export_check_list = with_auth_lst[:]   # 遍历授权参数时，每种情况对应一个导出目录，每次将用过的导出目录从check_list中剔除

    client_ip_list = ['20.2.42.128', '*', '20.2.42.201/22']  # 为了测试客户端授权格式，ip可任意指定;每个导出中包含列表中三种形式的客户端授权
    permission_level = ['rw', 'ro', 'rw_nodelsacl']
    write_mode = random.choice(['sync', 'async'])
    port_constraint = random.choice(['secure', 'insecure'])
    permission_constraint = ['all_squash', 'root_squash', 'no_root_squash']
    for mem1 in permission_level:
        for mem2 in permission_constraint:
            if mem2 == 'all_squash' or mem2 == 'root_squash':
                for name in client_ip_list:
                    anonuid = random.randint(1, 65536)
                    anongid = random.randint(1, 65536)
                    exe_info = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_check_list[0], name=name,
                                                                      permission_level=mem1, write_mode=write_mode,
                                                                      port_constraint=port_constraint,
                                                                      permission_constraint=mem2,
                                                                      anonuid=anonuid, anongid=anongid)
                    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                        common.except_exit('add nfs auth client failed !!!')
                    nfs_auth_list.append(exe_info['result'][0])
                nfs_export_check_list.remove(nfs_export_check_list[0])
            else:
                for name in client_ip_list:
                    exe_info = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_check_list[0],
                                                                      name=name,
                                                                      permission_level=mem1, write_mode=write_mode,
                                                                      port_constraint=port_constraint,
                                                                      permission_constraint=mem2)
                    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                        common.except_exit('add nfs auth client failed !!!')
                    nfs_auth_list.append(exe_info['result'][0])
                nfs_export_check_list.remove(nfs_export_check_list[0])

    return without_auth_lst, with_auth_lst, nfs_auth_list, auth_num_left, auth_num


def create_smb_export_auth(access_zone_id, export_path_list, local_user_list, local_group_list):
    order_num = 0
    smb_name_base = 'smb_export'
    smb_export_list = []  # smb导出id列表
    export_path_list = export_path_list[:60]   # 取列表切片，使得前n个路径为nfs导出独有，后面的路径存在复用情况
    description_list = ['', 'parastor smb export']
    # 遍历授权参数时，每种情况对应一个导出目录，每次将用过的导出目录从check_list中剔除;目录数目不足时进行补充创建extra_smb_export_path
    export_path_check_list = export_path_list
    enable_ntfs_acl = ['true', 'false']
    allow_create_ntfs_acl = ['true', 'false']
    enable_alternative_datasource = random.choice(['true', 'false'])
    enable_dos_attributes = random.choice(['true', 'false'])
    enable_os2style_ex_attrs = random.choice(['true', 'false'])
    enable_guest = ['true', 'false']
    enable_oplocks = random.choice(['true', 'false'])
    authorization_ip = [None, '20.2.42.128,20.2.42.129', '20.2.42.121', '20.2.42.1/22',
                        "'20.2.1. EXCEPT 20.2.1.2 20.2.1.3'"]    # 授权ip的各种形式，具体ip可任意指定

    for mem1 in enable_ntfs_acl:
        for mem2 in allow_create_ntfs_acl:
            for mem3 in enable_guest:
                for ip in authorization_ip:
                    smb_name = smb_name_base + '_%s' % order_num
                    order_num = order_num + 1
                    description = random.choice(description_list)
                    exe_info = nas_common.create_smb_export(access_zone_id, smb_name, export_path_check_list[0],
                                                            enable_ntfs_acl=mem1, description="'%s'" % description,
                                                            allow_create_ntfs_acl=mem2,
                                                            enable_alternative_datasource=enable_alternative_datasource,
                                                            enable_dos_attributes=enable_dos_attributes,
                                                            enable_os2style_ex_attrs=enable_os2style_ex_attrs,
                                                            enable_guest=mem3,
                                                            enable_oplocks=enable_oplocks, authorization_ip=ip)
                    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                        common.except_exit('create smb export failed !!!')
                    smb_export_list.append(exe_info['result'])
                    export_path_check_list.remove(export_path_check_list[0])

    '''smb客户端授权，各种参数进行遍历'''
    smb_auth_list = []   # smb授权列表
    auth_num = random.randint(10, len(smb_export_list)-3)
    without_auth_lst = smb_export_list[auth_num:]   # 只导出，不进行授权的smb导出
    with_auth_lst = smb_export_list[:auth_num]
    auth_num_left = len(without_auth_lst)   # 不进行授权的smb导出目录数

    run_as_root = ['true', 'false']
    permission_level = ['ro', 'rw', 'full_control']
    for mem1 in run_as_root:
        if mem1 == 'false':
            for mem2 in permission_level:   # 由于用户组无法批量删除，不方便使用，故此处授权均为用户；添加用户组可单独设置
                user = local_user_list[0]
                for smb_id in with_auth_lst:
                    exe_info = nas_common.add_smb_export_auth_clients(smb_id, name=user,
                                                                      user_type='USER', run_as_root='false',
                                                                      permission_level=mem2)
                    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                        common.except_exit('add smb auth client failed !!!')
                    smb_auth_list.append(exe_info['result'][0])

                local_user_list.remove(local_user_list[0])

                group = local_group_list[0]
                for smb_id in with_auth_lst:
                    exe_info = nas_common.add_smb_export_auth_clients(smb_id, name=group,
                                                                      user_type='GROUP', run_as_root='false',
                                                                      permission_level=mem2)
                    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                        common.except_exit('add smb auth client failed !!!')
                    smb_auth_list.append(exe_info['result'][0])

                local_group_list.remove(local_group_list[0])

        else:
            user = local_user_list[0]
            for smb_id in with_auth_lst:
                exe_info = nas_common.add_smb_export_auth_clients(smb_id, name=user, user_type='USER',
                                                                  run_as_root='true')
                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                    common.except_exit('add smb auth client failed !!!')
                smb_auth_list.append(exe_info['result'][0])
            local_user_list.remove(local_user_list[0])

            group = local_group_list[0]
            for smb_id in with_auth_lst:
                exe_info = nas_common.add_smb_export_auth_clients(smb_id, name=group, user_type='GROUP',
                                                                  run_as_root='true')
                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                    common.except_exit('add smb auth client failed !!!')
                smb_auth_list.append(exe_info['result'][0])
            local_group_list.remove(local_group_list[0])

    return without_auth_lst, with_auth_lst, smb_auth_list, auth_num_left, auth_num


def create_ftp_export(access_zone_id, export_path_list, local_user_list):
    ftp_export_list = []  # ftp导出id列表
    export_path_list = export_path_list[:70]   # 取列表切片，使得部分路径存在复用情况
    # 遍历授权参数时，每种情况对应一个导出目录，每次将用过的导出目录从check_list中剔除;目录数目不足时进行补充创建extra_ftp_export_path
    export_path_check_list = export_path_list
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
                                exe_info = nas_common.create_ftp_export(access_zone_id, local_user_check_list[0],
                                                                        export_path_check_list[0],
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
                                exe_info = nas_common.create_ftp_export(access_zone_id, local_user_check_list[0],
                                                                        export_path_check_list[0],
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
                                exe_info = nas_common.create_ftp_export(access_zone_id, local_user_check_list[0],
                                                                        export_path_check_list[0],
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
                                exe_info = nas_common.create_ftp_export(access_zone_id, local_user_check_list[0],
                                                                        export_path_check_list[0],
                                                                        enable_dirlist=mem1,
                                                                        enable_create_folder=mem2,
                                                                        enable_delete_and_rename=mem3,
                                                                        enable_upload=mem4, enable_download=mem5)
                                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                                    common.except_exit('create ftp export failed !!!')
                                ftp_export_list.append(exe_info['result'])
                                local_user_check_list.remove(local_user_check_list[0])
                                export_path_check_list.remove(export_path_check_list[0])
    export_num = len(ftp_export_list)   # ftp导出数目

    return ftp_export_list, export_num


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
    group_name_base = 'group_local'
    user_name_base = 'user_local'
    group_id_list = []
    user_id_list = []
    user_name_list = []   # 保存本地用户名
    group_name_list = []  # 保存本地用户组名
    group_num = 5
    user_num = 2
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
    ftp_group_num = 2
    ftp_user_num = 20
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

    root_dir = VOLUME_NAME + ':/'
    nfs_export_path_lst = [root_dir]
    smb_export_path_lst = [root_dir]
    ftp_export_path_lst = [root_dir]

    '''指定n层嵌套目录，各层目录对应的导出协议任选，将不同目录加入到不同协议所需export_path_list中'''
    ntime = 3
    ntime_nest_dir = ntime_mix_export(ntime)
    for mem in ntime_nest_dir:
        protocol_type = random.choice(['nfs', 'smb', 'ftp'])
        if protocol_type == 'nfs':
            nfs_export_path_lst.append(mem)
        elif protocol_type == 'smb':
            smb_export_path_lst.append(mem)
        else:
            ftp_export_path_lst.append(mem)

    '''创建大量随即嵌套目录'''
    width_dir_num_init = 5   # 目录初始宽度
    for k in range(width_dir_num_init):
        width_path_base = abs_path_base + '/' + dir_name_base + '_%s' % k
        export_width_path_base = export_path + '/' + dir_name_base + '_%s' % k
        cmd = 'mkdir -p %s' % width_path_base
        common.run_command(SYSTEM_IP_0, cmd)
        nfs_export_path_lst.append(export_width_path_base)
        smb_export_path_lst.append(export_width_path_base)
        ftp_export_path_lst.append(export_width_path_base)

        width_dir_num = random.randint(4, 6)  # 子目录深度随机选定
        for i in range(width_dir_num):
            width_path_base = width_path_base + '/' + dir_name_base + '_w_%s' % i
            export_width_path_base = export_width_path_base + '/' + dir_name_base + '_w_%s' % i
            cmd = 'mkdir -p %s' % width_path_base
            common.run_command(SYSTEM_IP_2, cmd)
            nfs_export_path_lst.append(export_width_path_base)
            smb_export_path_lst.append(export_width_path_base)
            ftp_export_path_lst.append(export_width_path_base)

            depth_dir_num = random.randint(4, 6)   # 子目录宽度随机选定
            for j in range(depth_dir_num):
                abs_path = width_path_base + '/' + dir_name_base + '_d_%s' % j
                dir_path = export_width_path_base + '/' + dir_name_base + '_d_%s' % j
                cmd = 'mkdir -p %s' % abs_path
                common.run_command(SYSTEM_IP_1, cmd)
                nfs_export_path_lst.append(dir_path)
                smb_export_path_lst.append(dir_path)
                ftp_export_path_lst.append(dir_path)

    """4> 各种返回值"""
    nfs_export_without_auth_lst, nfs_export_with_auth_lst, nfs_auth_lst, nfs_without_auth_num, nfs_with_auth_num = \
        create_nfs_export_auth(access_zone_id, nfs_export_path_lst)
    smb_export_without_auth_lst, smb_export_with_auth_lst, smb_auth_lst, smb_without_auth_num, smb_with_auth_num = \
        create_smb_export_auth(access_zone_id, smb_export_path_lst, user_name_list, group_name_list)
    ftp_export_lst, ftp_export_num = create_ftp_export(access_zone_id, ftp_export_path_lst, ftp_user_name_list)

    print ('******** %s %s %s %s %s*********' % (len(nfs_export_without_auth_lst), len(nfs_export_with_auth_lst),
                                                 len(nfs_auth_lst), nfs_without_auth_num, nfs_with_auth_num))
    print ('******** %s %s %s %s %s*********' % (len(smb_export_without_auth_lst), len(smb_export_with_auth_lst),
                                                 len(smb_auth_lst), smb_without_auth_num, smb_with_auth_num))
    print ('******** %s *********' % len(ftp_export_lst))

    """5> 删除授权及协议，或只删除协议"""
    nfs_delete_auth_switch = True  # 用来指定是否要先测试删除客户端授权
    while nfs_delete_auth_switch:
        nfs_single_auth = random.choice(nfs_auth_lst)
        exe_info = nas_common.remove_nfs_export_auth_clients(str(nfs_single_auth))
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('remove nfs auth clients failed !!!')
        nfs_auth_lst.remove(nfs_single_auth)

        if len(nfs_auth_lst) <= 2:
            break
        else:
            nfs_multi_auth_lst = random.sample(nfs_auth_lst, random.randint(2, len(nfs_auth_lst)))
            nfs_multi_auth_str = ','.join(str(p) for p in nfs_multi_auth_lst)
            exe_info = nas_common.remove_nfs_export_auth_clients(nfs_multi_auth_str)
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                common.except_exit('remove nfs auth clients failed !!!')
            for mem in nfs_multi_auth_lst:
                nfs_auth_lst.remove(mem)

            if len(nfs_auth_lst):
                continue
            else:
                break

    smb_delete_auth_switch = True  # 用来指定是否要先测试删除客户端授权
    while smb_delete_auth_switch:
        smb_single_auth = random.choice(smb_auth_lst)
        exe_info = nas_common.remove_smb_export_auth_clients(str(smb_single_auth))
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('remove smb auth clients failed !!!')
        smb_auth_lst.remove(smb_single_auth)

        if len(smb_auth_lst) <= 2:
            break
        else:
            smb_multi_auth_lst = random.sample(smb_auth_lst, random.randint(2, len(smb_auth_lst)))
            smb_multi_auth_str = ','.join(str(p) for p in smb_multi_auth_lst)
            exe_info = nas_common.remove_smb_export_auth_clients(smb_multi_auth_str)
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                common.except_exit('remove smb auth clients failed !!!')
            for mem in smb_multi_auth_lst:
                smb_auth_lst.remove(mem)

            if len(smb_auth_lst):
                continue
            else:
                break

    '''nfs未被授权导出的单个/批量删除'''
    flag = True   # 循环进行单个/批量删除，直到列表为空或批量删除前剩余数量不大于2
    while flag:
        nfs_single_export = random.choice(nfs_export_without_auth_lst)   # 选择单个export_id，进行删除操作
        exe_info = nas_common.delete_nfs_exports(str(nfs_single_export))
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('delete nfs export failed !!!')
        nfs_export_without_auth_lst.remove(nfs_single_export)   # 去掉已被选择过的id，防止重复删除

        if len(nfs_export_without_auth_lst) <= 2:
            break
        else:
            nfs_multi_export_lst = random.sample(nfs_export_without_auth_lst,
                                                 random.randint(2, len(nfs_export_without_auth_lst)))  # 任选导出id进行批量删除
            nfs_multi_export_str = ','.join(str(p) for p in nfs_multi_export_lst)
            exe_info = nas_common.delete_nfs_exports(nfs_multi_export_str)
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                common.except_exit('delete nfs export failed !!!')
            for mem in nfs_multi_export_lst:
                nfs_export_without_auth_lst.remove(mem)

            if len(nfs_export_without_auth_lst):
                flag = True
            else:
                flag = False

    '''nfs被授权导出的单个/批量删除'''
    flag = True
    while flag:
        nfs_single_export = random.choice(nfs_export_with_auth_lst)
        exe_info = nas_common.delete_nfs_exports(str(nfs_single_export))
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('delete nfs export failed !!!')
        nfs_export_with_auth_lst.remove(nfs_single_export)

        if len(nfs_export_with_auth_lst) <= 2:
            break
        else:
            nfs_multi_export_lst = random.sample(nfs_export_with_auth_lst, random.randint(2, len(nfs_export_with_auth_lst)))
            nfs_multi_export_str = ','.join(str(p) for p in nfs_multi_export_lst)
            exe_info = nas_common.delete_nfs_exports(nfs_multi_export_str)
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                common.except_exit('delete nfs export failed !!!')
            for mem in nfs_multi_export_lst:
                nfs_export_with_auth_lst.remove(mem)

            if len(nfs_export_with_auth_lst):
                flag = True
            else:
                flag = False

    '''smb未授权导出的单个/批量删除'''
    flag = True
    while flag:
        smb_single_export = random.choice(smb_export_without_auth_lst)
        exe_info = nas_common.delete_smb_exports(str(smb_single_export))
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('delete smb export failed !!!')
        smb_export_without_auth_lst.remove(smb_single_export)

        if len(smb_export_without_auth_lst) <= 2:
            break
        else:
            smb_multi_export_lst = random.sample(smb_export_without_auth_lst, random.randint(2, len(smb_export_without_auth_lst)))
            smb_multi_export_str = ','.join(str(p) for p in smb_multi_export_lst)
            exe_info = nas_common.delete_smb_exports(smb_multi_export_str)
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                common.except_exit('delete smb export failed !!!')
            for mem in smb_multi_export_lst:
                smb_export_without_auth_lst.remove(mem)

            if len(smb_export_without_auth_lst):
                flag = True
            else:
                flag = False

    '''smb授权导出的单个/批量删除'''
    flag = True
    while flag:
        smb_single_export = random.choice(smb_export_with_auth_lst)
        exe_info = nas_common.delete_smb_exports(str(smb_single_export))
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('delete smb export failed !!!')
        smb_export_with_auth_lst.remove(smb_single_export)

        if len(smb_export_with_auth_lst) <= 2:
            break
        else:
            smb_multi_export_lst = random.sample(smb_export_with_auth_lst, random.randint(2, len(smb_export_with_auth_lst)))
            smb_multi_export_str = ','.join(str(p) for p in smb_multi_export_lst)
            exe_info = nas_common.delete_smb_exports(smb_multi_export_str)
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                common.except_exit('delete smb export failed !!!')
            for mem in smb_multi_export_lst:
                smb_export_with_auth_lst.remove(mem)

            if len(smb_export_with_auth_lst):
                flag = True
            else:
                flag = False

    '''ftp导出的单个/批量删除'''
    flag = True
    while flag:
        ftp_single_export = random.choice(ftp_export_lst)
        exe_info = nas_common.delete_ftp_exports(str(ftp_single_export))
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('delete ftp export failed !!!')
        ftp_export_lst.remove(ftp_single_export)

        if len(ftp_export_lst) <= 2:
            break
        else:
            ftp_multi_export_lst = random.sample(ftp_export_lst, random.randint(2, len(ftp_export_lst)))
            ftp_multi_export_str = ','.join(str(p) for p in ftp_multi_export_lst)
            exe_info = nas_common.delete_ftp_exports(ftp_multi_export_str)
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                common.except_exit('delete ftp export failed !!!')
            for mem in ftp_multi_export_lst:
                ftp_export_lst.remove(mem)

            if len(ftp_export_lst):
                flag = True
            else:
                flag = False

    return


def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    prepare_clean.nas_test_clean()
    case()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    nas_main()

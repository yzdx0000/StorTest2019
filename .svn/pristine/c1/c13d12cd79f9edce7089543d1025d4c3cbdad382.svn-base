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
# 概述：创建并修改多种协议导出及客户端授权
# （导出配置、授权配置不同，授权用户操作限制进行手动验证）
# 过程：1、创建3种协议的导出并添加授权客户端（主要参数遍历，次要参数随机）
#      2、保存nfs/smb各个客户端授权的待修改参数（字典形式，键为auth_id，值是与初始参数不同的、修改目标参数值）；保存smb/ftp各个导出的待修改参数
#      3、对上述修改过程指定循环次数（尽量保证各个参数修改项均被覆盖）
#########################################################


VOLUME_NAME = get_config.get_one_volume_name()
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字
NAS_PATH = get_config.get_one_nas_test_path()                            # /mnt/volume/nas_test
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/volume/nas_test/nas_16_6_0_16
BASE_NAS_PATH = os.path.dirname(NAS_PATH)                                # /mnt/volume
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)                           # /nas_test
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
    update_client_dict = {}   # 存放不同授权客户端对应参数的字典
    nfs_export_check_list = nfs_export_list   # 遍历授权参数时，每种情况对应一个导出目录，每次将用过的导出目录从check_list中剔除
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

                    '''在字典中添加项，键为客户端id，值为各参数（修改后的参数值，避免无效修改）'''
                    port_constraint = random.choice(['secure', 'insecure'])
                    tmp_permission_constraint = 'no_root_squash'  # 每次必然从需要输入匿名用户（组）id修改为不需输入id
                    tmp_permission_level_lst = permission_level[:]
                    tmp_permission_level_lst.remove(mem1)
                    tmp_permission_level = random.choice(tmp_permission_level_lst)
                    tmp_write_mode = random.choice(['sync', 'async'])
                    tmp_value_list = [tmp_permission_level, tmp_write_mode, port_constraint, tmp_permission_constraint]
                    # 每次创建后添加一个键值对，用于之后的客户端授权修改
                    update_client_dict.setdefault(exe_info['result'][0], tmp_value_list)

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

                    port_constraint = random.choice(['secure', 'insecure'])
                    # 每次必然从不需要输入匿名用户（组）id修改为需要输入id
                    tmp_permission_constraint = random.choice(['all_squash', 'root_squash'])
                    tmp_permission_level_lst = permission_level[:]
                    tmp_permission_level_lst.remove(mem1)
                    tmp_permission_level = random.choice(tmp_permission_level_lst)
                    tmp_write_mode = random.choice(['sync', 'async'])
                    tmp_anonuid = random.randint(1, 65536)
                    tmp_anongid = random.randint(1, 65536)
                    tmp_value_list = [tmp_permission_level, tmp_write_mode, port_constraint, tmp_permission_constraint,
                                      tmp_anonuid, tmp_anongid]
                    # 每次创建后添加一个键值对，用于之后的客户端授权修改
                    update_client_dict.setdefault(exe_info['result'][0], tmp_value_list)

                nfs_export_check_list.remove(nfs_export_check_list[0])
    return update_client_dict


def create_smb_export_auth(access_zone_id, export_path_list, local_user_list, local_group_list):
    order_num = 0
    smb_name_base = 'smb_export'
    smb_export_list = []  # smb导出id列表
    update_smb_export_dict = {}   # smb导出修改字典
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

                    '''将smb导出id作为键，待修改后对应的参数值列表作为值，添加到update_smb_export_dict字典中'''
                    tmp_enable_ntfs_acl_lst = enable_ntfs_acl[:]
                    tmp_enable_ntfs_acl_lst.remove(mem1)
                    tmp_allow_create_ntfs_acl_lst = allow_create_ntfs_acl[:]
                    tmp_allow_create_ntfs_acl_lst.remove(mem2)
                    tmp_enable_guest_lst = enable_guest[:]
                    tmp_enable_guest_lst.remove(mem3)
                    tmp_authorization_ip = authorization_ip[:]
                    tmp_authorization_ip.remove(ip)
                    tmp_value_list = [tmp_enable_ntfs_acl_lst[0], tmp_allow_create_ntfs_acl_lst[0],
                                      random.choice(['true', 'false']), random.choice(['true', 'false']),
                                      random.choice(['true', 'false']),
                                      tmp_enable_guest_lst[0], random.choice(['true', 'false']),
                                      random.choice(tmp_authorization_ip)]
                    # 每次创建后添加一个键值对，用于之后的smb导出的修改
                    update_smb_export_dict.setdefault(exe_info['result'], tmp_value_list)

    '''smb客户端授权，各种参数进行遍历'''
    smb_auth_list = []   # smb授权列表
    update_client_dict = {}
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

                    tmp_permission_level_lst = permission_level[:]
                    option_1 = ['true']
                    tmp_permission_level_lst.remove(mem2)
                    option_2 = ['false', random.choice(tmp_permission_level_lst)]
                    options = [option_1, option_2]
            # 待修改后的参数值从两种可能性中任选一个：run_as_root；为true或者run_as_root为false，但permission_level与之前不同
                    tmp_value_list = random.choice(options)
                    update_client_dict.setdefault(exe_info['result'][0], tmp_value_list)

                local_user_list.remove(local_user_list[0])

                group = local_group_list[0]
                for smb_id in smb_export_list:
                    exe_info = nas_common.add_smb_export_auth_clients(smb_id, name=group,
                                                                      user_type='GROUP', run_as_root='false',
                                                                      permission_level=mem2)
                    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                        common.except_exit('add smb auth client failed !!!')
                    smb_auth_list.append(exe_info['result'][0])

                    tmp_permission_level_lst = permission_level[:]
                    option_1 = ['true']
                    tmp_permission_level_lst.remove(mem2)
                    option_2 = ['false', random.choice(tmp_permission_level_lst)]
                    options = [option_1, option_2]
                # 待修改后的参数值从两种可能性中任选一个：run_as_root；为true或者run_as_root为false，但permission_level与之前不同
                    tmp_value_list = random.choice(options)
                    update_client_dict.setdefault(exe_info['result'][0], tmp_value_list)

                local_group_list.remove(local_group_list[0])

        else:
            user = local_user_list[0]
            for smb_id in smb_export_list:
                exe_info = nas_common.add_smb_export_auth_clients(smb_id, name=user, user_type='USER',
                                                                  run_as_root='true')
                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                    common.except_exit('add smb auth client failed !!!')
                smb_auth_list.append(exe_info['result'][0])

                tmp_value_list = ['false', random.choice(permission_level)]  # run_as_root为false，permission_level任选
                update_client_dict.setdefault(exe_info['result'][0], tmp_value_list)

            local_user_list.remove(local_user_list[0])

            group = local_group_list[0]
            for smb_id in smb_export_list:
                exe_info = nas_common.add_smb_export_auth_clients(smb_id, name=group, user_type='GROUP',
                                                                  run_as_root='true')
                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                    common.except_exit('add smb auth client failed !!!')
                smb_auth_list.append(exe_info['result'][0])
                tmp_value_list = ['false', random.choice(permission_level)]  # run_as_root为false，permission_level任选
                update_client_dict.setdefault(exe_info['result'][0], tmp_value_list)

            local_group_list.remove(local_group_list[0])

    return update_smb_export_dict, update_client_dict


def create_ftp_export(access_zone_id, export_path_list, local_user_list):
    ftp_export_list = []  # ftp导出id列表
    update_ftp_export_dict = {}
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

                                tmp_export_path_check_lst = export_path_check_list[:]
                                tmp_export_path_check_lst.remove(export_path_check_list[0])
                                tmp_enable_dirlist_lst = enable_dirlist[:]
                                tmp_enable_dirlist_lst.remove(mem1)
                                tmp_enable_create_folder_lst = enable_create_folder[:]
                                tmp_enable_create_folder_lst.remove(mem2)
                                tmp_delete_and_rename_lst = enable_delete_and_rename[:]
                                tmp_delete_and_rename_lst.remove(mem3)
                                tmp_enable_upload = mem4
                                tmp_upload_local_max_rate = random.randint(0, 1000)
                                tmp_enable_download = 'false'
                                tmp_value_list = [access_zone_id, local_user_check_list[0],
                                                  random.choice(tmp_export_path_check_lst), tmp_enable_dirlist_lst[0],
                                                  tmp_enable_create_folder_lst[0], tmp_delete_and_rename_lst[0],
                                                  tmp_enable_upload, tmp_upload_local_max_rate, tmp_enable_download]
                                update_ftp_export_dict.setdefault(exe_info['result'], tmp_value_list)

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

                                tmp_export_path_check_lst = export_path_check_list[:]
                                tmp_export_path_check_lst.remove(export_path_check_list[0])
                                tmp_enable_dirlist_lst = enable_dirlist[:]
                                tmp_enable_dirlist_lst.remove(mem1)
                                tmp_enable_create_folder_lst = enable_create_folder[:]
                                tmp_enable_create_folder_lst.remove(mem2)
                                tmp_delete_and_rename_lst = enable_delete_and_rename[:]
                                tmp_delete_and_rename_lst.remove(mem3)
                                tmp_enable_upload = mem4
                                tmp_upload_local_max_rate = random.randint(0, 1000)
                                tmp_enable_download = 'true'
                                tmp_download_local_max_rate = random.randint(0, 1000)
                                tmp_value_list = [access_zone_id, local_user_check_list[0],
                                                  random.choice(tmp_export_path_check_lst),
                                                  tmp_enable_dirlist_lst[0], tmp_enable_create_folder_lst[0],
                                                  tmp_delete_and_rename_lst[0], tmp_enable_upload,
                                                  tmp_upload_local_max_rate, tmp_enable_download,
                                                  tmp_download_local_max_rate]
                                update_ftp_export_dict.setdefault(exe_info['result'], tmp_value_list)

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

                                tmp_export_path_check_lst = export_path_check_list[:]
                                tmp_export_path_check_lst.remove(export_path_check_list[0])
                                tmp_enable_dirlist_lst = enable_dirlist[:]
                                tmp_enable_dirlist_lst.remove(mem1)
                                tmp_enable_create_folder_lst = enable_create_folder[:]
                                tmp_enable_create_folder_lst.remove(mem2)
                                tmp_delete_and_rename_lst = enable_delete_and_rename[:]
                                tmp_delete_and_rename_lst.remove(mem3)
                                tmp_enable_upload = mem4
                                tmp_enable_download = 'false'
                                tmp_value_list = [access_zone_id, local_user_check_list[0],
                                                  random.choice(tmp_export_path_check_lst), tmp_enable_dirlist_lst[0],
                                                  tmp_enable_create_folder_lst[0], tmp_delete_and_rename_lst[0],
                                                  tmp_enable_upload, tmp_enable_download]
                                update_ftp_export_dict.setdefault(exe_info['result'], tmp_value_list)

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

                                tmp_export_path_check_lst = export_path_check_list[:]
                                tmp_export_path_check_lst.remove(export_path_check_list[0])
                                tmp_enable_dirlist_lst = enable_dirlist[:]
                                tmp_enable_dirlist_lst.remove(mem1)
                                tmp_enable_create_folder_lst = enable_create_folder[:]
                                tmp_enable_create_folder_lst.remove(mem2)
                                tmp_delete_and_rename_lst = enable_delete_and_rename[:]
                                tmp_delete_and_rename_lst.remove(mem3)
                                tmp_enable_upload = mem4
                                tmp_enable_download = 'true'
                                tmp_download_local_max_rate = random.randint(0, 1000)
                                tmp_value_list = [access_zone_id, local_user_check_list[0],
                                                  random.choice(tmp_export_path_check_lst), tmp_enable_dirlist_lst[0],
                                                  tmp_enable_create_folder_lst[0], tmp_delete_and_rename_lst[0],
                                                  tmp_enable_upload, tmp_enable_download, tmp_download_local_max_rate]
                                update_ftp_export_dict.setdefault(exe_info['result'], tmp_value_list)

                                local_user_check_list.remove(local_user_check_list[0])
                                export_path_check_list.remove(export_path_check_list[0])
    return update_ftp_export_dict


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

    # nfs_export_path_lst = list(set(nfs_export_path_lst))   # 去除重复元素
    # smb_export_path_lst = list(set(smb_export_path_lst))
    # ftp_export_path_lst = list(set(ftp_export_path_lst))

    """4> 修改多种协议，多种授权形式"""
    update_nfs_client_dict = create_nfs_export_auth(access_zone_id, nfs_export_path_lst)
    update_smb_export_dict, update_smb_client_dict = create_smb_export_auth(access_zone_id, smb_export_path_lst,
                                                                            user_name_list, group_name_list)
    update_ftp_export_dict = create_ftp_export(access_zone_id, ftp_export_path_lst, ftp_user_name_list)

    print ('******** %s *********' % len(update_nfs_client_dict))
    print ('******** %s %s *********' % (len(update_smb_export_dict), len(update_smb_client_dict)))
    print ('******** %s *********' % len(update_ftp_export_dict))

    loop_num = 3  # 修改的循环次数
    for i in range(loop_num):
        '''修改nfs客户端授权'''
        update_client_num = random.randint(1, len(update_nfs_client_dict))  # 修改项的数目
        nfs_client_dict_lst = random.sample(update_nfs_client_dict, update_client_num)
        for mem in nfs_client_dict_lst:
            key = mem
            tmp_value_lst = update_nfs_client_dict[key]
            if len(tmp_value_lst) == 4:
                exe_info = nas_common.update_nfs_export_auth_client(auth_client_id=key, permission_level=tmp_value_lst[0],
                                                                    write_mode=tmp_value_lst[1],
                                                                    port_constraint=tmp_value_lst[2],
                                                                    permission_constraint=tmp_value_lst[3])
                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                    common.except_exit('update nfs export auth client failed !!!')
            else:
                exe_info = nas_common.update_nfs_export_auth_client(auth_client_id=key, permission_level=tmp_value_lst[0],
                                                                    write_mode=tmp_value_lst[1],
                                                                    port_constraint=tmp_value_lst[2],
                                                                    permission_constraint=tmp_value_lst[3],
                                                                    anonuid=tmp_value_lst[4],
                                                                    anongid=tmp_value_lst[5])
                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                    common.except_exit('update nfs export auth client failed !!!')

        '''修改smb导出'''
        update_export_num = random.randint(1, len(update_smb_export_dict))
        smb_export_dict_lst = random.sample(update_smb_export_dict, update_export_num)
        for mem in smb_export_dict_lst:
            key = mem
            tmp_value_lst = update_smb_export_dict[key]
            exe_info = nas_common.update_smb_export(export_id=key, description="'update smb export'",
                                                    enable_ntfs_acl=tmp_value_lst[0],
                                                    allow_create_ntfs_acl=tmp_value_lst[1],
                                                    enable_alternative_datasource=tmp_value_lst[2],
                                                    enable_dos_attributes=tmp_value_lst[3],
                                                    enable_os2style_ex_attrs=tmp_value_lst[4],
                                                    enable_guest=tmp_value_lst[5], enable_oplocks=tmp_value_lst[6],
                                                    authorization_ip=tmp_value_lst[7])
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                common.except_exit('update smb export failed !!!')

        '''修改smb客户端授权'''
        update_client_num = random.randint(1, len(update_smb_client_dict))
        smb_client_dict_lst = random.sample(update_smb_client_dict, update_client_num)
        for mem in smb_client_dict_lst:
            key = mem
            tmp_value_lst = update_smb_client_dict[key]
            if len(tmp_value_lst) == 1:
                exe_info = nas_common.update_smb_export_auth_client(auth_client_id=key, run_as_root=tmp_value_lst[0])
                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                    common.except_exit('update smb export auth client failed !!!')
            else:
                exe_info = nas_common.update_smb_export_auth_client(auth_client_id=key, run_as_root=tmp_value_lst[0],
                                                                    permission_level=tmp_value_lst[1])
                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                    common.except_exit('update smb export auth client failed !!!')

        '''修改ftp导出'''
        update_export_num = random.randint(1, len(update_ftp_export_dict))
        ftp_export_dict_lst = random.sample(update_ftp_export_dict, update_export_num)
        for mem in ftp_export_dict_lst:
            key = mem
            tmp_value_lst = update_ftp_export_dict[key]
            if len(tmp_value_lst) == 8:
                exe_info = nas_common.update_ftp_export(export_id=key,
                                                        export_path=tmp_value_lst[2], enable_dirlist=tmp_value_lst[3],
                                                        enable_create_folder=tmp_value_lst[4],
                                                        enable_delete_and_rename=tmp_value_lst[5],
                                                        enable_upload=tmp_value_lst[6], enable_download=tmp_value_lst[7])
                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                    common.except_exit('update ftp export failed !!!')
            if len(tmp_value_lst) == 9:
                if tmp_value_lst[6] == 'true':
                    exe_info = nas_common.update_ftp_export(export_id=key,
                                                            export_path=tmp_value_lst[2], enable_dirlist=tmp_value_lst[3],
                                                            enable_create_folder=tmp_value_lst[4],
                                                            enable_delete_and_rename=tmp_value_lst[5],
                                                            enable_upload=tmp_value_lst[6],
                                                            upload_local_max_rate=tmp_value_lst[7],
                                                            enable_download=tmp_value_lst[8])
                    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                        common.except_exit('update ftp export failed !!!')
                else:
                    exe_info = nas_common.update_ftp_export(export_id=key,
                                                            export_path=tmp_value_lst[2], enable_dirlist=tmp_value_lst[3],
                                                            enable_create_folder=tmp_value_lst[4],
                                                            enable_delete_and_rename=tmp_value_lst[5],
                                                            enable_upload=tmp_value_lst[6],
                                                            enable_download=tmp_value_lst[7],
                                                            download_local_max_rate=tmp_value_lst[8])
                    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                        common.except_exit('update ftp export failed !!!')
            if len(tmp_value_lst) == 10:
                exe_info = nas_common.update_ftp_export(export_id=key,
                                                        export_path=tmp_value_lst[2], enable_dirlist=tmp_value_lst[3],
                                                        enable_create_folder=tmp_value_lst[4],
                                                        enable_delete_and_rename=tmp_value_lst[5],
                                                        enable_upload=tmp_value_lst[6],
                                                        upload_local_max_rate=tmp_value_lst[7],
                                                        enable_download=tmp_value_lst[8],
                                                        download_local_max_rate=tmp_value_lst[9])
                if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                    common.except_exit('update ftp export failed !!!')

    return


def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    prepare_clean.nas_test_clean()
    case()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    nas_main()

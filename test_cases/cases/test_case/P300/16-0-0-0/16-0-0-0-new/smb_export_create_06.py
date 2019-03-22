# -*-coding:utf-8 -*
import multiprocessing
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
import remote

#########################################################
# author: liyao
# 概述：本地认证，2个访问分区，创建2个smb导出，授权IP不做限制（对用户授权）
# 过程：1、创建3节点访问分区，启动服务
#      2、创建本地用户组/用户
#      3、分别使用父目录和子目录创建smb导出，父目录导出使用默认参数，子目录导出使用非默认参数
#      4、分别对同一个用户授权：父目录导出为只读权限，子目录导出为root权限
#      5、创建业务子网、添加vip
#      6、客户端挂载验证
#########################################################


VOLUME_NAME = get_config.get_one_volume_name()
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字
NAS_PATH = get_config.get_one_nas_test_path()                            # /mnt/volume/nas_test_dir
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/volume/nas_test_dir/nas_16_6_0_16
BASE_NAS_PATH = os.path.dirname(NAS_PATH)                                # /mnt/volume
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)                           # nas_test_dir
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
WIN_HOST = get_config.get_win_client_ips()[0]
DISK_SYMBOL = get_config.get_win_disk_symbols()[1]


def create_access_zone():
    '''创建2个本地认证的访问分区'''
    obj_node = common.Node()
    nodes_id_list = obj_node.get_nodes_id()
    access_zone_name = 'az_local_1'
    node_id = nodes_id_list[0]
    access_zone_id_lst = []
    exe_info = nas_common.create_access_zone(node_ids=node_id, name=access_zone_name)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create access zone %s failed !!!' % access_zone_name)
        raise Exception('create access zone %s failed !!!' % access_zone_name)
    access_zone_id_lst.append(exe_info['result'])
    nodes_id_list.remove(node_id)

    nodes_id_str = ','.join(str(p) for p in nodes_id_list)  # 包含2个节点的访问分区
    access_zone_name = 'az_local_2'
    exe_info = nas_common.create_access_zone(node_ids=nodes_id_str, name=access_zone_name)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('create access zone failed !!!')
    access_zone_id_lst.append(exe_info['result'])

    '''获取local认证服务器id和访问分区id'''
    zone_provider_ids_dic = {}
    exe_info = nas_common.get_access_zones()
    access_zones_lst = exe_info['result']['access_zones']
    for mem in access_zones_lst:
        zone_provider_ids_dic.setdefault(mem['auth_provider_id'], mem['id'])

    return zone_provider_ids_dic, access_zone_id_lst


def create_group_user(group_num, user_num, local_provider_id):
    '''创建本地用户组/用户'''
    group_name_base = 'group_local'
    user_name_base = 'user_local'
    group_id_list = []
    user_id_list = []
    user_name_list = []  # 保存本地用户名
    group_name_list = []  # 保存本地用户组名
    group_num = group_num
    user_num = user_num
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
    return group_name_list, user_name_list


def create_subnet(access_zone_id):
    subnet_name = 'subnet_' + FILE_NAME
    ip_family = 'IPv4'
    exe_info = nas_common.create_subnet(access_zone_id=access_zone_id, name=subnet_name, ip_family=ip_family,
                                        svip=nas_common.SUBNET_SVIP, subnet_mask=nas_common.SUBNET_MASK,
                                        subnet_gateway=nas_common.SUBNET_GATEWAY,
                                        network_interfaces=nas_common.SUBNET_NETWORK_INTERFACES)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create subnet %s failed !!!' % subnet_name)
        raise Exception('create subnet %s failed !!!' % subnet_name)
    subnet_id = exe_info['result']

    '''查看业务子网信息'''
    exe_info = nas_common.get_subnets(subnet_id)
    subnet = exe_info['result']['subnets'][0]
    if subnet['id'] == subnet_id and subnet['name'] == subnet_name and subnet['svip'] == nas_common.SUBNET_SVIP and \
            subnet['subnet_mask'] == int(nas_common.SUBNET_MASK) and subnet[
        'subnet_gateway'] == nas_common.SUBNET_GATEWAY \
            and subnet['network_interfaces'][0] == nas_common.SUBNET_NETWORK_INTERFACES:
        log.info('subnet params are correct !')
    else:
        log.error('subnet params are wrong !!! ')
        raise Exception('subnet params are wrong !!!')
    return subnet_id


def create_vip_pool(subnet_id, access_zone_id):
    '''添加vip池，并将IP段切分成IP放入列表'''
    vip_pool_name = 'www.vip-pool'
    used_protocol = 'NAS'

    exe_info = nas_common.get_access_zones(ids=access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('get access zone failed !!!')
    az_nodes_lst = exe_info['result']['access_zones'][0]['node_ids']
    az_nodes_num = len(az_nodes_lst)

    origin_vip_addresses_str = nas_common.VIP_ADDRESSES   # 根据分区中的节点数，确定vip池中的ip数
    parted_vip_lst = re.split('[.-]', origin_vip_addresses_str)
    start_ip_section = parted_vip_lst[3]
    end_ip_section = int(start_ip_section) + int(az_nodes_num) * 4 - 1
    vip_addressed = parted_vip_lst[0] + '.' + parted_vip_lst[1] + '.' + parted_vip_lst[2] + '.' + parted_vip_lst[3] \
                    + '-' + str(end_ip_section)

    exe_info = nas_common.add_vip_address_pool(subnet_id=subnet_id, domain_name=vip_pool_name,
                                               vip_addresses=vip_addressed, supported_protocol=used_protocol,
                                               allocation_method='DYNAMIC')
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('add vip pool failed !!!')

    log.info('waiting for 5s')
    time.sleep(5)

    '''观察VIP是否绑定到3个节点到对应的网卡上（相同网段的网卡）'''
    # ip_dict, xml_ip_list, eth_ip_list = nas_common.get_vip_from_eth()
    # rc = nas_common.judge_vip_layinfo(ip_dict, xml_ip_list, eth_ip_list)
    # common.judge_rc(rc, 0, 'there is something wrong with vip layout !!!')

    '''将vip池中的ip放入列表'''
    exe_info = nas_common.get_vip_address_pools()
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('get vip addresses pool failed !!!')
    vip_str = exe_info['result']['ip_address_pools'][0]['vip_addresses'][0]

    if '-' in vip_str:
        vip_part_lst = re.split('[.-]', vip_str)  # 将如20.2.43.51-62的字符串，切分成['20', '2', '43', '51', '62']列表
        vip_lst_len = int(vip_part_lst[4]) - int(vip_part_lst[3]) + 1
        vip_lst = []
        for i in range(vip_lst_len):
            tmp_ip = vip_part_lst[0] + '.' + vip_part_lst[1] + '.' + vip_part_lst[2] + '.' + \
                     str(int(vip_part_lst[3]) + i)
            vip_lst.append(tmp_ip)
    else:
        vip_lst = vip_str.split(',')  # 离散型ip
        vip_part_lst = vip_lst[0].split('.')

    return vip_lst, vip_part_lst


def smb_mount_create(mount_vip, mount_export_name, mount_passwd, mount_user):
    print WIN_HOST
    rs = remote.Remote(uri='%s:8270' % WIN_HOST)
    rc, stdout = rs.run_keyword(name='smb_mount', args=(DISK_SYMBOL, '\\\\%s\%s' % (mount_vip, mount_export_name),
                                                        mount_passwd, mount_user))
    print rc
    print stdout.decode("gb2312")
    log.info('waiting for 5s')
    time.sleep(5)
    rc = rs.run_keyword(name='create_dir_file', args=(DISK_SYMBOL, ))
    return rc


def smb_clean_umount(dir_lst, file_lst):
    rs = remote.Remote(uri='%s:8270' % WIN_HOST)
    print rs.run_keyword(name='delete_dir_file', args=(dir_lst, file_lst))

    log.info('waiting for 5s')
    time.sleep(5)
    rs.run_keyword(name='smb_umount', args=(DISK_SYMBOL,))


def case():
    '''函数执行主体，包含本脚本的主要测试点：smb的导出与授权'''
    """1> 创建访问分区"""
    zone_provider_ids_dic, access_zone_id_lst = create_access_zone()
    log.info('waiting for 5s')
    time.sleep(5)

    for mem in access_zone_id_lst:
        exe_info = nas_common.enable_nas(access_zone_id=mem)
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('enable nas failed !!!')

    """2> 创建用户组与用户"""
    log.info('waiting for 5s')
    time.sleep(5)
    group_num = 2
    user_num = 3
    local_provider_id = random.choice(zone_provider_ids_dic.keys())   # 从两个分区（认证服务器）中任选一个进行后续的导出及授权
    group_name_lst, user_name_lst = create_group_user(group_num, user_num, local_provider_id)

    """3> 创建子网与vip池"""
    log.info('waiting for 5s')
    time.sleep(5)
    access_zone_id = zone_provider_ids_dic[local_provider_id]
    subnet_id = create_subnet(access_zone_id)
    vip_lst, vip_part_lst = create_vip_pool(subnet_id, access_zone_id)

    """4> 创建2个smb导出，并对同一个用户授权（IP不做限制）"""
    path_num = 2
    abs_path = NAS_TRUE_PATH
    export_path = VOLUME_NAME + ':/' + os.path.join(NAS_PATH_BASENAME, FILE_NAME) + '/'
    export_path_lst = []
    for i in range(path_num):
        abs_path = os.path.join(abs_path, 'smb_%s' % str(i))
        cmd = 'mkdir -p %s' % abs_path
        common.run_command(SYSTEM_IP_0, cmd)
        export_path = os.path.join(export_path, os.path.basename(abs_path))
        export_path_lst.append(export_path)

    '''创建第一个smb导出，使用父目录，非必填项均为默认值；授权为只读权限'''
    export_name_1 = 'smb_export_1'
    export_path_1 = export_path_lst[0]
    exe_info = nas_common.create_smb_export(access_zone_id=access_zone_id, export_name=export_name_1,
                                            export_path=export_path_1)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create smb export failed !!!')
    export_id_1 = exe_info['result']
    auth_client_name = random.choice(user_name_lst)
    exe_info = nas_common.add_smb_export_auth_clients(export_id=export_id_1, name=auth_client_name, user_type='USER',
                                                      run_as_root='false', permission_level='ro')
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('add smb export auth client failed !!!')

    '''创建第二个smb导出，使用子目录，非必填项均为非默认值；授权为root权限'''
    export_name_2 = 'smb_export_2'
    export_path_2 = export_path_lst[1]
    description = 'this is a smb export'
    enable_ntfs_acl = 'false'
    enable_alternative_datasource = 'true'
    enable_dos_attributes = 'false'
    enable_os2style_ex_attrs = 'true'
    enable_guest = 'true'
    enable_oplocks = 'false'
    exe_info = nas_common.create_smb_export(access_zone_id=access_zone_id, export_name=export_name_2,
                                            export_path=export_path_lst[1], description="'%s'" % description,
                                            enable_ntfs_acl=enable_ntfs_acl,
                                            enable_alternative_datasource=enable_alternative_datasource,
                                            enable_dos_attributes=enable_dos_attributes,
                                            enable_os2style_ex_attrs=enable_os2style_ex_attrs,
                                            enable_guest=enable_guest, enable_oplocks=enable_oplocks)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('create smb export failed !!!')
    export_id_2 = exe_info['result']
    exe_info = nas_common.add_smb_export_auth_clients(export_id=export_id_2, name=auth_client_name, user_type='USER',
                                                      run_as_root='true')
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('add smb export auth client failed !!!')

    """5> windows客户端挂载验证"""
    mount_export_name = export_name_2
    mount_user = auth_client_name
    mount_vip = random.choice(vip_lst)
    mount_passwd = '111111'
    rc = smb_mount_create(mount_vip, mount_export_name, mount_passwd, mount_user)  # windows端执行挂载、创建文件
    dir_lst = rc[0]
    file_lst = rc[1]
    client_total_num = int(len(dir_lst) + len(file_lst))
    print ('**********%s %s**************' % (len(dir_lst), len(file_lst)))

    '''linux端导出目录下检查文件是否正确'''
    export_path = export_path_lst[1]
    check_export_path = '/mnt/' + VOLUME_NAME + '/' + export_path.split(':')[1]
    cmd = "cd %s; ls -lR |grep '^-'|wc -l" % check_export_path
    rc, check_file_num = common.run_command(SYSTEM_IP_0, cmd)
    common.judge_rc(rc, 0, 'get files failed !!!')
    cmd = "cd %s; ls -lR |grep '^d'|wc -l" % check_export_path
    rc, check_dir_num = common.run_command(SYSTEM_IP_0, cmd)
    common.judge_rc(rc, 0, 'get directories failed !!!')
    check_total_num = int(check_file_num) + int(check_dir_num)  # 导出目录下文件及目录数检查
    if check_total_num != client_total_num:
        common.except_exit('server file&dir check failed !!!')

    '''windows客户端删除文件并umount'''
    log.info('waiting for 30s')
    time.sleep(30)
    smb_clean_umount(dir_lst, file_lst)


def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    # log_file_path = log.get_log_path(FILE_NAME)
    # log.init(log_file_path, True)
    case()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    nas_main()















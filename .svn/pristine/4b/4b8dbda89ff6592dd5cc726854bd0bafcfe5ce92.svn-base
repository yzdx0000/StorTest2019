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
import remote

#########################################################
# author: liyao
# 概述：验证smb公共属性中的家目录是否生效
# 过程：1、使用默认公共属性，创建smb导出及授权
#      2、使用smb导出进行挂载，并写入数据验证；完成后umount
#      3、修改所有公共属性的参数
#      4、新创建smb导出，使用用户身份登陆
#      5、写入数据，并进入home_dir进行验证
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
WIN_HOST = get_config.get_win_client_ips()[0]
DISK_SYMBOL = get_config.get_win_disk_symbols()[1]


def smb_export_auth(access_zone_id, local_user_list, local_group_list):
    '''创建smb导出'''
    export_id_lst = []
    export_name_lst = []
    order = len(local_user_list) + len(local_group_list)
    for i in range(order):
        abs_export_path = os.path.join(NAS_TRUE_PATH, 'smb_%s' % i)
        cmd = 'mkdir -p %s' % abs_export_path
        common.run_command(SYSTEM_IP_0, cmd)
        export_name = 'export_%s' % i
        export_path = VOLUME_NAME + ':/' + os.path.join(NAS_PATH_BASENAME, FILE_NAME) + '/smb_%s' % i
        exe_info = nas_common.create_smb_export(access_zone_id=access_zone_id, export_name=export_name,
                                                export_path=export_path)
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            log.error('create smb export %s failed !!!' % export_name)
        export_id_lst.append(exe_info['result'])
        export_name_lst.append(export_name)

    '''添加授权客户端'''
    export_id_check_lst = export_id_lst[:]
    auth_client_id = []
    root_right_name = random.choice(local_user_list)   # 保证至少有一个root权限的授权用户，进行windows断的验证
    exe_info = nas_common.add_smb_export_auth_clients(export_id=export_id_check_lst[0], name=root_right_name,
                                                      user_type='USER', run_as_root='true')
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            log.error('add smb export auth client failed !!!')
    export_id_check_lst.remove(export_id_check_lst[0])
    local_user_list.remove(root_right_name)

    for mem in local_user_list:
        run_as_root = random.choice(['true', 'false'])
        if run_as_root == 'true':
            exe_info = nas_common.add_smb_export_auth_clients(export_id=export_id_check_lst[0], name=mem,
                                                              user_type='USER', run_as_root=run_as_root)
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                log.error('add smb export auth client failed !!!')
            auth_client_id.append(exe_info['result'][0])
            export_id_check_lst.remove(export_id_check_lst[0])
        else:
            permission_level = random.choice(['ro', 'rw', 'full_control'])
            exe_info = nas_common.add_smb_export_auth_clients(export_id=export_id_check_lst[0], name=mem,
                                                              user_type='USER', run_as_root=run_as_root,
                                                              permission_level=permission_level)
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                log.error('add smb export auth client failed !!!')
            auth_client_id.append(exe_info['result'][0])
            export_id_check_lst.remove(export_id_check_lst[0])

    for mem in local_group_list:
        run_as_root = random.choice(['true', 'false'])
        if run_as_root == 'true':
            exe_info = nas_common.add_smb_export_auth_clients(export_id=export_id_check_lst[0], name=mem,
                                                              user_type='GROUP', run_as_root=run_as_root)
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                log.error('add smb export auth client failed !!!')
            auth_client_id.append(exe_info['result'][0])
            export_id_check_lst.remove(export_id_check_lst[0])
        else:
            permission_level = random.choice(['ro', 'rw', 'full_control'])
            exe_info = nas_common.add_smb_export_auth_clients(export_id=export_id_check_lst[0], name=mem,
                                                              user_type='GROUP', run_as_root=run_as_root,
                                                              permission_level=permission_level)
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                log.error('add smb export auth client failed !!!')
            auth_client_id.append(exe_info['result'][0])
            export_id_check_lst.remove(export_id_check_lst[0])

    return export_name_lst, export_id_lst


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
    """1> 获取基本信息"""
    obj_node = common.Node()
    nodes_id_list = obj_node.get_nodes_id()
    nodes_id_str = ','.join(str(p) for p in nodes_id_list)
    access_zone_name = 'az_local'
    exe_info = nas_common.create_access_zone(nodes_id_str, access_zone_name)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create access zone %s failed !!!' % access_zone_name)
        raise Exception('create access zone %s failed !!!' % access_zone_name)
    access_zone_id = exe_info['result']

    '''获取local认证服务器id'''
    exe_info = nas_common.get_auth_providers_local()
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('get auth provider ad failed !!!')
    local_provider_id = exe_info['result']['auth_providers'][0]['id']

    '''启动nas服务'''
    exe_info = nas_common.enable_nas(access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('enable nas failed !!!')
        raise Exception('enable nas failed !!!')

    """2> 创建多用户组和多用户"""
    group_name_base = 'group_local'
    user_name_base = 'user_local'
    group_id_list = []
    user_id_list = []
    user_name_list = []   # 保存本地用户名
    group_name_list = []  # 保存本地用户组名
    group_num = 2
    user_num = 3
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

    """3> 创建业务子网"""
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

    log.info('waiting for 10s')
    time.sleep(10)

    '''添加vip池'''
    vip_pool_name = 'www.vip-pool'
    used_protocol = 'NAS'
    exe_info = nas_common.add_vip_address_pool(subnet_id=subnet_id, domain_name=vip_pool_name,
                                               vip_addresses=nas_common.VIP_ADDRESSES, supported_protocol=used_protocol,
                                               allocation_method='DYNAMIC')
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('add vip pool failed !!!')

    '''观察VIP是否绑定到3个节点到对应的网卡上（相同网段的网卡）'''
    ip_dict, xml_ip_list, eth_ip_list = nas_common.get_vip_from_eth()
    rc = nas_common.judge_vip_layinfo(ip_dict, xml_ip_list, eth_ip_list)
    common.judge_rc(rc, 0, 'there is something wrong with vip layout !!!')

    '''将vip池中的ip放入列表'''
    exe_info = nas_common.get_vip_address_pools()
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('get vip addresses pool failed !!!')
    vip_str = exe_info['result']['ip_address_pools'][0]['vip_addresses'][0]
    vip_part_lst = re.split('[.-]', vip_str)  # 将如20.2.43.51-62的字符串，切分成['20', '2', '43', '51', '62']列表
    vip_lst_len = int(vip_part_lst[4]) - int(vip_part_lst[3]) + 1
    vip_lst = []
    for i in range(vip_lst_len):
        tmp_ip = vip_part_lst[0] + '.' + vip_part_lst[1] + '.' + vip_part_lst[2] + '.' + str(int(vip_part_lst[3]) + i)
        vip_lst.append(tmp_ip)

    """4> 创建smb导出及授权，在windows端挂载"""
    smb_export_auth(access_zone_id, user_name_list, group_name_list)
    exe_info = nas_common.get_smb_export_auth_clients()
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('get smb export auth clients failed !!!')
    export_auth_clients_lst = exe_info['result']['smb_export_auth_clients']
    root_ctrl_client_dic = {}  # 字典的键是权限为“root”的授权id，值为该授权对应的export_id和用户/用户组名字
    for mem in export_auth_clients_lst:
        if mem['run_as_root'] is True and mem['type'] == 'USER':
            root_ctrl_client_dic.setdefault(mem['id'], [mem['export_id'], mem['name']])

    '''windows端挂载'''
    mount_vip = random.choice(vip_lst)
    export_user_cp = random.choice(root_ctrl_client_dic.values())  # 获取具有完全控制权限的用户及其对应的导出
    exe_info = nas_common.get_smb_exports(ids=export_user_cp[0])
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('get smb export failed !!!')
    check_export_path = exe_info['result']['exports'][0]['export_path']  # windows端写入文件后，在此路径下进行检查
    mount_export_name = exe_info['result']['exports'][0]['export_name']
    mount_user = export_user_cp[1]  # 挂载所需的本地用户名
    mount_passwd = '111111'

    rc = smb_mount_create(mount_vip, mount_export_name, mount_passwd, mount_user)  # windows端执行挂载、创建文件
    dir_lst = rc[0]
    file_lst = rc[1]
    client_total_num = int(len(dir_lst) + len(file_lst))
    print ('**********%s %s**************' % (len(dir_lst), len(file_lst)))

    '''linux端导出目录下检查文件是否正确'''
    check_export_path = '/mnt/' + VOLUME_NAME + '/' + check_export_path.split(':')[1]
    cmd = "cd %s; ls -lR |grep '^-'|wc -l" % check_export_path
    rc, check_file_num = common.run_command(SYSTEM_IP_1, cmd)
    common.judge_rc(rc, 0, 'get files failed !!!')
    cmd = "cd %s; ls -lR |grep '^d'|wc -l" % check_export_path
    rc, check_dir_num = common.run_command(SYSTEM_IP_0, cmd)
    common.judge_rc(rc, 0, 'get directories failed !!!')
    check_total_num = int(check_file_num) + int(check_dir_num)  # 导出目录下文件及目录数检查
    if check_total_num != client_total_num:
        common.except_exit('server file&dir check failed !!!')

    log.info('waiting for 30s')
    time.sleep(30)
    smb_clean_umount(dir_lst, file_lst)

    """5> 修改公共属性后，windows端挂载"""
    mount_vip = random.choice(vip_lst)
    export_user_cp = random.choice(root_ctrl_client_dic.values())  # 获取具有完全控制权限的用户及其对应的导出
    exe_info = nas_common.get_smb_exports(ids=export_user_cp[0])
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('get smb export failed !!!')
    mount_user = export_user_cp[1]   # 挂载所需的本地用户名
    mount_passwd = '111111'

    exe_info = nas_common.get_smb_global_configs()
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('get smb global config failed !!!')
    global_config_id = exe_info['result']['configs'][0]['id']

    abs_home_dir = NAS_TRUE_PATH + '/home_dir'
    home_dir = VOLUME_NAME + ':/' + os.path.join(NAS_PATH_BASENAME, FILE_NAME) + '/home_dir'
    cmd = 'mkdir -p %s' % abs_home_dir
    common.run_command(SYSTEM_IP_1, cmd)

    update_configs_dic = {'enable_change_notify': 'false', 'enable_guest': 'true', 'enable_send_ntlmv2': 'true',
                          'home_dir': home_dir, 'enable_alternative_datasource': 'true',
                          'enable_dos_attributes': 'false', 'enable_os2style_ex_attrs': 'true',
                          'enable_ntfs_acl': 'false', 'allow_create_ntfs_acl': 'false', 'enable_oplocks': 'false'}
    exe_info = nas_common.update_smb_global_config(smb_global_config_id=global_config_id,
                                                   enable_change_notify=update_configs_dic['enable_change_notify'],
                                                   enable_guest=update_configs_dic['enable_guest'],
                                                   enable_send_ntlmv2=update_configs_dic['enable_send_ntlmv2'],
                                                   home_dir=update_configs_dic['home_dir'],
                                                   enable_alternative_datasource=update_configs_dic['enable_alternative_datasource'],
                                                   enable_dos_attributes=update_configs_dic['enable_dos_attributes'],
                                                   enable_os2style_ex_attrs=update_configs_dic['enable_os2style_ex_attrs'],
                                                   enable_ntfs_acl=update_configs_dic['enable_ntfs_acl'],
                                                   allow_create_ntfs_acl=update_configs_dic['allow_create_ntfs_acl'],
                                                   enable_oplocks=update_configs_dic['enable_oplocks'])
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('update smb global config failed !!!')

    rc = smb_mount_create(mount_vip, mount_user, mount_passwd, mount_user)   # 修改公共属性后，再次执行挂载、创建文件
    dir_lst = rc[0]
    file_lst = rc[1]
    client_total_num = len(dir_lst) + len(file_lst)
    check_export_path = os.path.join(abs_home_dir, mount_user)

    '''linux端导出目录下检查文件是否正确'''
    cmd = "cd %s; ls -lR |grep '^-'|wc -l" % check_export_path
    rc, check_file_num = common.run_command(SYSTEM_IP_1, cmd)
    common.judge_rc(rc, 0, 'get files failed !!!')
    cmd = "cd %s; ls -lR |grep '^d'|wc -l" % check_export_path
    rc, check_dir_num = common.run_command(SYSTEM_IP_0, cmd)
    common.judge_rc(rc, 0, 'get directories failed !!!')
    check_total_num = int(check_file_num) + int(check_dir_num)  # 导出目录下文件及目录数检查
    if check_total_num != client_total_num:
        common.except_exit('server file&dir check failed !!!')

    log.info('waiting for 30s')
    time.sleep(30)
    smb_clean_umount(dir_lst, file_lst)

    return


def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    # log_file_path = log.get_log_path(FILE_NAME)
    # log.init(log_file_path, True)
    case()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    nas_main()
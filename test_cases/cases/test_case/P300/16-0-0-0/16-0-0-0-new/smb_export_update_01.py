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
# 概述：访问分区的修改，认证服务器的修改，smb导出创建（创建时为默认值，授权IP不限制）+ 导出修改（授权IP修改为IP段）
# 过程：1、创建ad认证服务器
#      2、创建2个本地访问分区（node1 & node2+node3），启动nas服务
#      3、修改访问分区为（node1+node2 & node3），访问分区1由本地认证修改为ad认证
#      4、创建默认参数的smb导出（authorization_ip 不设限制）并进行授权（用户）
#      5、修改smb导出（authorization_ip 修改为IP段）
#      6、创建业务子网、添加vip，挂载后客户端测试文件读写
#########################################################


VOLUME_NAME = get_config.get_one_volume_name()
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字
NAS_PATH = get_config.get_one_nas_test_path()                            # /mnt/volume/nas_test_dir
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/volume/nas_test_dir/nas_16_6_0_16
BASE_NAS_PATH = os.path.dirname(NAS_PATH)                                # /mnt/volume
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)                           # nas_test_dir
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
WIN_HOST = get_config.get_win_client_ips()[0]
WIN_AUTH_CLIENT = get_config.get_win_client_ips()[1]
DISK_SYMBOL = get_config.get_win_disk_symbols()[0]


def create_provider_access_zones():
    '''创建ad认证，创建本地访问分区'''
    obj_node = common.Node()
    nodes_id_list = obj_node.get_nodes_id()
    ad_name = 'ad_server'
    services_for_unix_lst = ['NONE', 'RFC2307']
    services_for_unix = random.choice(services_for_unix_lst)
    exe_info = nas_common.add_auth_provider_ad(name=ad_name, domain_name=nas_common.AD_DOMAIN_NAME,
                                               dns_addresses=nas_common.AD_DNS_ADDRESSES, username=nas_common.AD_USER_1,
                                               password=nas_common.AD_PASSWORD,
                                               services_for_unix='"%s"' % services_for_unix)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('get auth provider ad failed !!!')
    ad_provider_id = exe_info['result']

    '''创建2个访问分区，分别包含node1和node2 + node3'''
    access_zone_ids_lst = []
    allocation_ids_lst = nodes_id_list[:]   # 存放待分配的集群节点id
    access_zone_name_1 = 'az1_ad'
    exe_info = nas_common.create_access_zone(node_ids=allocation_ids_lst[0], name=access_zone_name_1,
                                             auth_provider_id=ad_provider_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('create access zone failed !!!')
    allocation_ids_lst.remove(allocation_ids_lst[0])
    access_zone_id_1 = exe_info['result']
    access_zone_ids_lst.append(access_zone_id_1)

    access_zone_name_2 = 'az2_ad'
    allocation_ids_str = ','.join(str(p) for p in allocation_ids_lst)
    exe_info = nas_common.create_access_zone(node_ids=allocation_ids_str, name=access_zone_name_2,
                                             auth_provider_id=ad_provider_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('create access zone failed !!!')
    access_zone_id_2 = exe_info['result']
    access_zone_ids_lst.append(access_zone_id_2)

    return access_zone_ids_lst, ad_provider_id


def update_access_zones(single_node_az_id, multi_nodes_az_id):
    '''对多节点分区和单节点分区先后进行修改'''
    exe_info = nas_common.get_access_zones(ids=multi_nodes_az_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('get access zone failed !!!')
    multi_nodes_ids_lst = exe_info['result']['access_zones'][0]['node_ids']

    exe_info = nas_common.update_access_zone(access_zone_id=multi_nodes_az_id, node_ids=multi_nodes_ids_lst[-1])
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('update access zone failed !!!')

    exe_info = nas_common.get_access_zones(ids=single_node_az_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('get access zone failed !!!')
    single_node_id_lst = exe_info['result']['access_zones'][0]['node_ids']
    single_node_id_lst.append(multi_nodes_ids_lst[0])   # 将上一个分区剔除的节点加入单节点分区中

    modified_nodes_str = ','.join(str(p) for p in single_node_id_lst)
    exe_info = nas_common.update_access_zone(access_zone_id=single_node_az_id, node_ids=modified_nodes_str)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('update access zone failed !!!')


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
            tmp_ip = vip_part_lst[0] + '.' + vip_part_lst[1] + '.' + vip_part_lst[2] + '.' + str(int(vip_part_lst[3]) + i)
            vip_lst.append(tmp_ip)
    else:
        vip_lst = vip_str.split(',')  # 离散型ip

    return vip_lst


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
    """1> 创建并修改访问分区"""
    access_zone_id_lst, auth_provider_id = create_provider_access_zones()
    log.info('waiting for 5s')
    time.sleep(5)
    for i in range(len(access_zone_id_lst)):
        exe_info = nas_common.enable_nas(access_zone_id=access_zone_id_lst[i])
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            log.error('enable nas failed !!!')

    single_node_az_id = access_zone_id_lst[0]
    multi_nodes_az_id = access_zone_id_lst[1]
    update_access_zones(single_node_az_id, multi_nodes_az_id)

    """2> 获取用户组与用户"""
    log.info('waiting for 5s')
    time.sleep(5)
    group_name_lst = []
    ad_group_num = 3
    for i in range(ad_group_num):
        group_name_lst.append(get_config.get_ad_groups()[i])

    """3> 创建子网与vip池"""
    log.info('waiting for 5s')
    time.sleep(5)
    access_zone_id = single_node_az_id   # 后续一系列操作使用的访问分区id
    subnet_id = create_subnet(access_zone_id)
    vip_lst = create_vip_pool(subnet_id, access_zone_id)

    """4> 创建smb导出(对授权IP做限制)"""
    '''一个导出，多个用户授权'''
    smb_basename = 'smb_1'
    abs_export_path = os.path.join(NAS_TRUE_PATH, smb_basename)
    cmd = 'mkdir -p %s' % abs_export_path
    common.run_command(SYSTEM_IP_0, cmd)
    export_path = VOLUME_NAME + ':/' + os.path.join(NAS_PATH_BASENAME, FILE_NAME) + '/%s' % smb_basename
    export_name = 'smb_export'
    description = 'this is a smb export'
    enable_ntfs_acl = 'true'
    allow_create_ntfs_acl = 'true'
    enable_alternative_datasource = 'false'
    enable_dos_attributes = 'true'
    enable_os2style_ex_attrs = 'false'
    enable_guest = 'false'
    enable_oplocks = 'true'
    win_auth_client_lst = WIN_AUTH_CLIENT.split('.')
    authorization_ip_part = win_auth_client_lst[0] + '.' + win_auth_client_lst[1] + '.' + win_auth_client_lst[2] + '.'
    authorization_ip = authorization_ip_part + ' EXCEPT ' + authorization_ip_part + '1'  # smb导出中选择IP段去除部分IP
    exe_info = nas_common.create_smb_export(access_zone_id=access_zone_id, export_name=export_name,
                                            export_path=export_path, description="'%s'" % description,
                                            enable_ntfs_acl=enable_ntfs_acl, allow_create_ntfs_acl=allow_create_ntfs_acl,
                                            enable_alternative_datasource=enable_alternative_datasource,
                                            enable_dos_attributes=enable_dos_attributes,
                                            enable_os2style_ex_attrs=enable_os2style_ex_attrs,
                                            enable_guest=enable_guest, enable_oplocks=enable_oplocks,
                                            authorization_ip="'%s'" % authorization_ip)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create smb export failed !!!')
    export_id = exe_info['result']

    """5> 修改smb导出(授权IP不受限制)，添加授权"""
    exe_info = nas_common.update_smb_export(export_id=export_id, authorization_ip=None)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('update smb export failed !!!')

    auth_num = 3
    if auth_num > ad_group_num:   # 控制添加授权的数目不能超过用户总数
        auth_num = ad_group_num
    else:
        pass
    auth_right_lst = ['true', 'ro', 'rw', 'full_control']
    auth_id_lst = []
    for i in range(auth_num):
        exe_info = nas_common.add_smb_export_auth_clients(export_id=export_id, name='"%s"' % group_name_lst[0],
                                                          user_type='GROUP', run_as_root=auth_right_lst[0])
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            log.error('add smb auth client failed !!!')
        auth_id_lst.append(exe_info['result'][0])
        group_name_lst.remove(group_name_lst[0])

    """6> windows客户端挂载验证"""
    exe_info = nas_common.get_smb_export_auth_clients(export_ids=export_id)

    print('**********')
    print type(exe_info)
    print('**********')

    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('get smb export auth client failed !!!')
    write_read_groups_lst = []
    auth_groups_lst = exe_info['result']['smb_export_auth_clients']
    for mem in auth_groups_lst:
        if mem['run_as_root'] is True or mem['permission_level'] == 'full_control':
            write_read_groups_lst.append(mem['name'])

    find_user_by_group = random.choice(write_read_groups_lst)   # 通过用户组，查找到具有root权限或完全控制权限的用户，用户挂载

    rc, exe_info = nas_common.get_auth_users(auth_provider_id=auth_provider_id)

    print('**********')
    print type(exe_info)
    print('**********')

    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('get smb export auth client failed !!!')
    export_auth_clients_lst = exe_info['result']['auth_users']
    write_read_users_lst = []   # 可以在windows客户端验证文件读写的用户名
    for mem in export_auth_clients_lst:
        if 'primary_group_name' in mem.keys():
            if mem['primary_group_name'] == str(find_user_by_group):
                write_read_users_lst.append(mem['name'])

    mount_export_name = export_name
    mount_domain_name = 'adtest'
    mount_user = mount_domain_name + '\\' + random.choice(write_read_users_lst)
    mount_vip = random.choice(vip_lst)
    mount_passwd = '111111'
    rc = smb_mount_create(mount_vip, mount_export_name, mount_passwd, mount_user)  # windows端执行挂载、创建文件
    dir_lst = rc[0]
    file_lst = rc[1]
    client_total_num = int(len(dir_lst) + len(file_lst))
    print ('**********%s %s**************' % (len(dir_lst), len(file_lst)))

    '''linux端导出目录下检查文件是否正确'''
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















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
# 概述：nis认证，1个单节点访问分区（之后修改分区内节点数），创建nfs导出，对各种IP形式授权（权限不同）
# 过程：1、创建2个访问分区，分别启动服务
#      2、修改访问分区
#      3、创建默认参数的nfs导出并对['*', '50.2.42.1/22', '50.2.42.128']分别授与['ro', 'rw_nodelsacl', 'rw']的权限
#      4、创建业务子网、添加vip，挂载后客户端测试文件读写（按照上述授权方法，客户端50.2.42.128应该只具有'ro'的权限）
#########################################################


VOLUME_NAME = get_config.get_one_volume_name()
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字
NAS_PATH = get_config.get_one_nas_test_path()                            # /mnt/volume/nas_test_dir
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/volume/nas_test_dir/nas_16_6_0_16
BASE_NAS_PATH = os.path.dirname(NAS_PATH)                                # /mnt/volume
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)                           # nas_test_dir
SYSTEM_IP_0 = get_config.get_parastor_ip(0)


def create_access_zones():
    '''创建nis认证，并创建1个单节点访问分区'''
    nis_server_name = 'nis_server'
    domain_name = nas_common.NIS_DOMAIN_NAME
    ip_addressed = nas_common.NIS_IP_ADDRESSES
    exe_info = nas_common.add_auth_provider_nis(name=nis_server_name, domain_name=domain_name,
                                                ip_addresses=ip_addressed)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('add nis auth provider failed !!!')
    nis_provider_id = exe_info['result']

    obj_node = common.Node()
    nodes_id_list = obj_node.get_nodes_id()
    access_zone_name = 'az_nis'
    exe_info = nas_common.create_access_zone(node_ids=nodes_id_list[0], name=access_zone_name,
                                             auth_provider_id=nis_provider_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('create access zone failed !!!')
    access_zone_id = exe_info['result']

    return nis_provider_id, access_zone_id


def update_access_zones(access_zone_id, nodes_id_lst):
    '''修改访问分区中的节点数'''
    nodes_id_str = ','.join(str(p) for p in nodes_id_lst)
    exe_info = nas_common.update_access_zone(access_zone_id=access_zone_id, node_ids=nodes_id_str)
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
        common.except_exit('create subnet failed !!!')
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


def case():
    """1> 创建访问分区，启动服务"""
    nis_provider_id, access_zone_id = create_access_zones()
    exe_info = nas_common.enable_nas(access_zone_id=access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('enable nas failed !!!')

    """2> 创建子网，添加vip池"""
    log.info('waiting for 5s')
    time.sleep(5)
    subnet_id = create_subnet(access_zone_id)
    vip_lst, vip_part_lst = create_vip_pool(subnet_id, access_zone_id)   # 存放vip列表和某个被切分的IP地址，如[10,2,40,1]

    """3> 创建nfs导出并授权"""
    export_name = 'nfs_export'
    abs_export_path = os.path.join(NAS_TRUE_PATH, 'nfs_path')
    cmd = 'mkdir -p %s' % abs_export_path
    common.run_command(SYSTEM_IP_0, cmd)
    description = 'this is a nfs export'
    export_path = VOLUME_NAME + ':/' + os.path.join(NAS_PATH_BASENAME, FILE_NAME) + '/nfs_path'
    exe_info = nas_common.create_nfs_export(access_zone_id=access_zone_id, export_name=export_name,
                                            export_path=export_path, description="'%s'" % description)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('create nfs export failed !!!')
    export_id = exe_info['result']

    '''添加授权(在客户端获取将要授权的IP)'''
    cmd = 'ip a |grep inet |grep /%s' % nas_common.SUBNET_MASK
    rc, stdout = common.run_command(nas_common.CLIENT_IP_1, cmd)
    filter_lines_lst = stdout.strip().split()
    for mem in filter_lines_lst:
        if vip_part_lst[0] in mem.split('.') and str(nas_common.SUBNET_MASK) in mem.split('/'):
            auth_client_ip_1 = mem.split('/')[0]  # 两种不同的授权IP形式
            auth_client_ip_2 = mem

    auth_clients_lst = ['*', auth_client_ip_2, auth_client_ip_1]
    permission_level_lst = ['ro', 'rw_nodelsacl', 'rw']
    for i in range(len(auth_clients_lst)):
        exe_info = nas_common.add_nfs_export_auth_clients(export_id=export_id, name=auth_clients_lst[i],
                                                          permission_level=permission_level_lst[i])
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('add nfs export auth clients failed !!!')

    """4> nfs挂载，并在客户端进行验证"""
    server_ip = random.choice(vip_lst)
    server_path = abs_export_path
    client_ip = nas_common.CLIENT_IP_1
    client_path = '/mnt/' + os.path.join(FILE_NAME, 'nfs_mount')
    judge_info = nas_common.mount(server_ip=server_ip, server_path=server_path, client_ip=client_ip,
                                  client_path=client_path)
    if judge_info == 3:
        common.except_exit('nfs mount failed !!!')

    '''客户端进行验证'''
    log.info('waiting for 5s')
    time.sleep(5)
    create_file_num = 10
    file_name_base = 'file_'
    for i in range(create_file_num):
        file_name = file_name_base + str(i)
        cmd = 'cd %s; touch %s' % (client_path, file_name)
        common.run_command(nas_common.CLIENT_IP_1, cmd)

    '''nfs导出目录下检查文件数目是否正确'''
    cmd = "cd %s; ls -lR |grep '^-'|wc -l" % server_path
    rc, check_file_num = common.run_command(SYSTEM_IP_0, cmd)
    if int(check_file_num) != int(create_file_num):
        common.except_exit('check file number failed !!!')

    """5> nfs客户端umount，并删除挂载路径"""
    cmd = 'cd %s; rm -rf *' % client_path
    common.run_command(nas_common.CLIENT_IP_1, cmd)
    rc = nas_common.umount(nas_common.CLIENT_IP_1, client_path)
    common.judge_rc(rc, 0, 'umount nfs failed !!!')


def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    # log_file_path = log.get_log_path(FILE_NAME)
    # log.init(log_file_path, True)
    case()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    nas_main()















# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import re
import utils_path
import common
import nas_common
import log
import get_config
import json
import random
import prepare_clean
import threading

# 此脚本使用时，默认认证服务器及访问区存在

VOLUME_NAME = get_config.get_one_volume_name()
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字
NAS_PATH = get_config.get_one_nas_test_path()                            # /mnt/volume/nas_test_dir
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/volume/nas_test_dir/nas_16_1_1_11
BASE_NAS_PATH = os.path.dirname(NAS_PATH)                                # /mnt/volume
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)                           # nas_test_dir
SYSTEM_IP_0 = '10.2.40.1'
NFS_CLIENT_IP_LST = ['10.2.40.93', '10.2.40.94', '10.2.40.78', '10.2.40.79', '10.2.40.80']


def client_mount(domain_name, export_path_abs, client_path, client_ip):
    try_num = 10
    for i in range(try_num):
        cmd = 'mount -t nfs %s:%s %s' % (domain_name, export_path_abs, client_path)
        rc, stdout = common.run_command(client_ip, cmd)
        if rc == 0:
            break
        elif i == (try_num-1) and rc != 0:
            raise Exception('mount client failed !!!')
        elif rc != 0:
            log.info('the %s time mount failed !!!' % (i + 1))
            log.info('waiting for 10s')
            time.sleep(10)


def umount_client(client_path, client_ip):
    cmd = 'umount -l %s' % client_path
    rc, stdout = common.run_command(client_ip, cmd)
    # common.judge_rc(rc, 0, 'umount client failed !!!')


def file_write(mount_path, client_ip):
    while True:
        for i in range(10):
            of = mount_path + '/file_%s' % i
            cmd = 'dd if=/dev/sda1 of=%s bs=100M count=10' % of
            rc, stdout = common.run_command(client_ip, cmd)
            common.judge_rc(rc, 0, 'create file failed !!!')


def case():
    '''函数执行主体'''
    """(1) 创建访问区，获取访问区id"""
    exe_info = nas_common.create_access_zone(node_ids='1,2,3', name='az1')
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create access zone failed !!!' )
        raise Exception('create access zone failed !!!')

    exe_info = nas_common.get_access_zones()
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('get access zone failed !!!' )
        raise Exception('get access zone failed !!!')
    az_id_lst = []
    for zone in exe_info['result']['access_zones']:
        az_id_lst.append(zone['id'])

    exe_info = nas_common.enable_nas(access_zone_id=az_id_lst[0])
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('get access zone failed !!!' )
        raise Exception('get access zone failed !!!')

    """(2)集群和客户端创建多目录"""
    test_path_base = os.path.join(BASE_NAS_PATH, 'large_scale_test')
    cmd = 'mkdir -p %s' % test_path_base
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    common.judge_rc(rc, 0, 'create large_scale_path failed !!!')
    '''集群创建nfs导出目录'''
    dir_num = 300
    export_path_abs_lst = []
    export_base_path = VOLUME_NAME + ':/' + 'large_scale_test/'
    export_path_lst = []
    for i in range(dir_num):
        tmp_path_abs = os.path.join(test_path_base, 'test_%s' % i)
        tmp_path = export_base_path + os.path.basename(tmp_path_abs)
        cmd = 'mkdir -p %s' % tmp_path_abs
        rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
        # common.judge_rc(rc, 0, 'create nfs export path failed !!!')
        export_path_abs_lst.append(tmp_path_abs)
        export_path_lst.append(tmp_path)

    '''客户端创建挂载目录'''
    mount_path_base = os.path.join('/mnt/', 'large_scale_test/')
    umount_path = mount_path_base + 'test_*'
    for mem in NFS_CLIENT_IP_LST:
        umount_client(umount_path, mem)
    log.info('waiting for 5s')
    time.sleep(5)

    client_mount_path_lst = []
    client_dir_num = 60
    for mem in NFS_CLIENT_IP_LST:
        cmd = 'mkdir -p %s' % mount_path_base
        rc, stdout = common.run_command(mem, cmd)
        # common.judge_rc(rc, 0, 'create client mount failed !!!')
        for i in range(client_dir_num):
            tmp_path = os.path.join(mount_path_base, 'test_%s' % i)
            cmd = 'mkdir -p %s' % tmp_path
            rc, stdout = common.run_command(mem, cmd)
            # common.judge_rc(rc, 0, 'create client mount dir failed !!!')
            client_mount_path_lst.append(tmp_path)
    '''分割集群导出目录列表和客户端挂载目录列表'''
    parted_client_path_lst = []    # 分别存储各客户端挂载使用的路径
    client_num = 5
    for i in range(client_num):
        parted_client_path_lst.append(client_mount_path_lst[client_dir_num*i:client_dir_num*i+dir_num])

    parted_export_lst = []
    for i in range(client_num):
        parted_export_lst.append(export_path_abs_lst[client_dir_num*i:client_dir_num*i+dir_num])

    """(3)创建nfs导出并授权"""
    export_name_base = 'nfs_export'
    export_id_lst = []
    client_auth_lst = []
    for i in range(dir_num):
        export_name = export_name_base + '_%s' % i
        exe_info = nas_common.create_nfs_export(access_zone_id=az_id_lst[0], export_path=export_path_lst[i], export_name=export_name)
        tmp_id = exe_info['result']
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            log.error('create nfs export failed !!!' )
            raise Exception('create nfs export failed !!!')
        export_id_lst.append(tmp_id)

        exe_info = nas_common.add_nfs_export_auth_clients(export_id=tmp_id, name='*', permission_level='rw')
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            log.error('add nfs auth client failed !!!' )
            raise Exception('add nfs auth client failed !!!')
        client_auth_lst.append(exe_info['result'][0])

    """(4)创建业务子网，VIP池"""
    exe_info = nas_common.create_subnet(access_zone_id=az_id_lst[0], name='subnet1', ip_family='IPv4', svip='50.10.11.112',
                                        subnet_mask='16', subnet_gateway='50.10.11.254', network_interfaces='ens7f0')
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create subnet failed !!!')
        raise Exception('create subnet failed !!!')
    subnet_id = exe_info['result']

    exe_info = nas_common.add_vip_address_pool(subnet_id=subnet_id, domain_name='www.nastest', vip_addresses='50.10.1.1-200,50.10.5.1-100',
                                               supported_protocol='NAS', allocation_method='DYNAMIC', rebalance_policy='RB_AUTOMATIC')
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('add vip address pool failed !!!')
        raise Exception('add vip address pool failed !!!')

    """(5)客户端挂载"""
    each_client_auth_num = client_dir_num
    for i in range(client_num):
        for j in range(each_client_auth_num):
            client_mount('www.nastest', parted_export_lst[i][j], parted_client_path_lst[i][j], NFS_CLIENT_IP_LST[i])
            log.info('waiting for 1s')
            time.sleep(1)

    """(6)各个挂载路径中文件读写"""
    threads_lst = []
    for j in range(client_num):
        threads_lst.append([])

    for j in range(client_num):
        for i in range(each_client_auth_num):
            t = threading.Thread(target=file_write,args=(parted_client_path_lst[j][i],NFS_CLIENT_IP_LST[j]))
            t.setDaemon(True)
            threads_lst[j].append(t)
        for i in range(each_client_auth_num):
            threads_lst[j][i].start()

    for j in range(client_num):
        for i in range(each_client_auth_num):
            threads_lst[j][i].join()

    """(7)客户端去挂载"""
    for i in range(client_num):
        for j in range(each_client_auth_num):
            umount_client(parted_client_path_lst[i][j], NFS_CLIENT_IP_LST[i])
            log.init('waiting for 3s')
            time.sleep(3)



def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    # log_file_path = log.get_log_path(FILE_NAME)
    # log.init(log_file_path, True)
    case()
    # prepare_clean.nas_test_clean()
    log.info('%s succeed!' % FILE_NAME)

    return

if __name__ == '__main__':
    nas_main()

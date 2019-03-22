# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import shell
import get_config
import prepare_clean
import tool_use
import commands
#################################################################
#
# Author: chenjy1
# Date: 2018-07-14
# @summary：
#        客户端授权后，mount操作 mount失败
# @steps:
#       1、创建一个新卷（卷名qc_40）
#       2、重新授权 不选自动挂载
#       3、mount操作 查看是否能发现挂载卷
#       4、通过后，删除授权，删除卷
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字


def case():
    log.info("case begin")

    ob_volume = common.Volume()
    ob_storagepool = common.Storagepool()

    '''获取存储池的信息'''

    rc, stdout = common.get_storage_pools()
    if 0 != rc:
        raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (rc, stdout))
    storage_pools = common.json_loads(stdout)
    storage_name = ''
    for storage_pool in storage_pools['result']['storage_pools']:
        if storage_pool['name'] != 'shared_storage_pool':
            storage_name = storage_pool['name']
            break

    rc, storagepool_id = ob_storagepool.get_storagepool_id(storage_name)  # 获取此存储池的ID
    log.info("log.info(storagepool_id)")
    log.info(storagepool_id)
    '''获取该存储池上一个已有的卷的信息'''
    one_volume = {}

    rc, stdout = common.get_volumes()
    if 0 != rc:
        raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (rc, stdout))
    volume_num = common.json_loads(stdout)['result']['total']
    if volume_num == 0:
        raise Exception('your storage_pool need a volume!')
    for volume in common.json_loads(stdout)['result']['volumes']:
        if volume['storage_pool_name'] == storage_name:
            one_volume = volume

    log.info("1> 创建一个新卷（卷名qc_40）")
    rc, json_info = ob_volume.create_volume(FILE_NAME, storagepool_id, one_volume['layout']['stripe_width'],
                            one_volume['layout']['disk_parity_num'], one_volume['layout']['node_parity_num'],
                            one_volume['layout']['replica_num'])
    common.judge_rc(rc, 0, "create volume failed")
    log.info("创建一个新卷名为qc_40 ...  ")
    time.sleep(30)

    """获取此卷所有信息"""
    old_volume = {}
    rc, stdout = common.get_volumes()
    if 0 != rc:
        raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (rc, stdout))
    for volume in common.json_loads(stdout)['result']['volumes']:
        if volume['name'] == FILE_NAME:
            old_volume = volume

    client_ip_lst = get_config.get_allclient_ip()
    auth_info = {}
    auth_info['auto_mount'] = 'false'

    log.info("2> 重新授权 不选自动挂载")
    for client_ip in client_ip_lst:
        rc, stdout = common.create_client_auth(client_ip, old_volume['id'], auth_info['auto_mount'])
        if 0 != rc:
            raise Exception("client_ip : %s Execute command: \"%s\" failed. \nstdout: %s" % (client_ip, rc, stdout))

    '''获取集群名称'''
    rc, stdout = common.get_cluster_overview()
    if 0 != rc:
        raise Exception("client_ip : %s Execute command: \"%s\" failed. \nstdout: %s" % (client_ip, rc, stdout))
    system_name = common.json_loads(stdout)['result']['name']

    '''每个客户端挂载'''
    log.info("3> mount操作 查看是否能发现挂载卷")
    for client_ip in client_ip_lst:
        cmd = "mkdir -p /mnt/%s ; mount -t parastor nodev /mnt/%s -o sysname=%s -o fsname=%s " \
              % (FILE_NAME, FILE_NAME, system_name, FILE_NAME)
        rc, stdout = common.run_command(client_ip, cmd)
        if 0 != rc:
            raise Exception("client_ip : %s Execute command: \"%s\" failed. \nstdout: %s" % (client_ip, rc, stdout))

    '''检查是否能发现挂载卷'''
    node = common.Node()
    all_ip = client_ip_lst
    flag_ip_volume = 1
    for i in range(len(all_ip) - 1):
        flag_ip_volume = (flag_ip_volume << 1) + 1  # 111111
    res_ip_volume = flag_ip_volume  # 111111
    start_time = time.time()
    while True:
        for i, ip in enumerate(all_ip):
            if (flag_ip_volume & (1 << i)) != 0:  # 仅看还未发现卷的节点
                res = common.check_client_state(ip, FILE_NAME)  # 使用判断客户端超时的函数
                if 0 == res:
                    flag_ip_volume &= (res_ip_volume ^ (1 << i))  # 将i对应的标志位置0
                elif -1 == res:
                    raise Exception('ssh failed !!!  please check node!!!')
                elif -2 == res:
                    raise Exception('client is blockup !!!')
                else:
                    log.info('still waiting %s' % ip)
        if flag_ip_volume & res_ip_volume == 0:  # 全0则通过
            break
        time.sleep(10)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('not found volume exist %dh:%dm:%ds' % (h, m, s))

    """删除授权"""
    log.info("4> 通过后，删除授权，删除卷")
    volume_id_list = [old_volume['id']]
    ob_auth_clinet = common.Clientauth()
    for client_ip in client_ip_lst:
        client_auth_id = ob_auth_clinet.get_client_auth_id(client_ip, volume_id_list)
        ob_auth_clinet.delete_client_auth(client_auth_id)

    """删除卷"""
    rc = ob_volume.delete_volume(old_volume['id'])
    common.judge_rc(rc, 0, 'delete_volume failed')

    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)

# -*-coding:utf-8 -*
# !/usr/bin/python

import os
import time
import commands
import json
import hashlib
from multiprocessing import Process

import utils_path
import common
import snap_common
import nas_common
import quota_common
import random
import log
import shell
import get_config
import tool_use
import prepare_clean
import upgrade_common
import make_fault

# =================================================================================
#  latest update:2018-08-13                                                   =
#  Author:wanggl                                                           =
# =================================================================================
# 2018-08-13:
# Author：wanggl
# @summary：
#   升级前后rcvr_dblksize_kb不同导致oStor的core
# @steps:
#   1、升级版本；
#   2、升级后，故障两块磁盘触发修复，观察修复任务；
#
#

# changelog:


######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
Private_clientIP1 = get_config.get_client_ip(0)
Private_clientIP2 = get_config.get_client_ip(1)
Private_clientIP3 = get_config.get_client_ip(2)

def pullout_disks(node_ip, disk_id_lst):
    """
    随机拔出插入一块数据盘
    :param node_ip:
    :param disk_id_lst:
    :return:
    """
    log.info('waiting for 10s')
    time.sleep(10)
    for disk_id in disk_id_lst:
        make_fault.pullout_disk(node_ip, disk_id, 'DATA')
    log.info('waiting for 10s')
    time.sleep(10)
    return


def insert_disks(node_ip, disk_id_lst):
    log.info('waiting for 10s')
    time.sleep(10)
    for disk_id in disk_id_lst:
        make_fault.insert_disk(node_ip, disk_id, 'DATA')
    log.info('waiting for 10s')
    time.sleep(10)
    return


def case():

    log.info('1> 升级版本')
    rc = upgrade_common.online_upgrade()
    common.judge_rc(rc, 0, 'upgrade version')

    log.info('2> 升级后，故障两块磁盘触发修复，观察修复任务')
    '''获取集群内所有节点的id'''
    ob_node = common.Node()
    ob_disk = common.Disk()
    ob_storage_pool = common.Storagepool()
    node_id_lst = ob_node.get_nodes_id()

    '''随机选一个节点'''
    fault_node_id = random.choice(node_id_lst)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    '''获取故障节点内所有的共享硬盘和数据硬盘'''
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)
    """随机选择两个数据盘"""
    fault_disk_name_lst = random.sample(monopoly_disk_names, 2)
    """获取故障盘的scsi id, id, uuid, 盘类型, 存储池id"""
    fault_disk_physicalid_lst = []
    fault_disk_id_lst = []
    fault_disk_uuid_lst = []
    fault_disk_usage_lst = []
    storage_pool_id_lst = []
    for fault_disk_name in fault_disk_name_lst:
        """物理id"""
        fault_disk_physicalid = ob_disk.get_physicalid_by_name(fault_node_ip, fault_disk_name)
        fault_disk_physicalid_lst.append(fault_disk_physicalid)
        """id"""
        fault_disk_id = ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name)
        fault_disk_id_lst.append(fault_disk_id)
        """uuid"""
        fault_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_disk_name)
        fault_disk_uuid_lst.append(fault_disk_uuid)
        """usage"""
        fault_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_disk_name)
        fault_disk_usage_lst.append(fault_disk_usage)
        """存储池id"""
        storage_pool_id = ob_disk.get_storage_pool_id_by_diskid(fault_node_id, fault_disk_id)
        storage_pool_id_lst.append(storage_pool_id)

        log.info("fault_node_id : %s"
                 "\nfault_disk_name : %s"
                 "\nfault_disk_physicalid : %s"
                 "\nfault_disk_uuid : %s"
                 "\nfault_disk_usage : %s"
                 "\nfault_disk_id : %s"
                 "\nstorage_pool_id : %s"
                 % (str(fault_node_id),
                    fault_disk_name,
                    fault_disk_physicalid,
                    fault_disk_uuid,
                    fault_disk_usage,
                    str(fault_disk_id),
                    str(storage_pool_id)))

    '''随机拔除一个节点的两个数据盘 '''
    pullout_disks(fault_node_ip, fault_disk_physicalid_lst)

    """被动重建完成后，将磁盘插回；删除僵尸状态的磁盘，并再次添加"""
    log.info('wait 60s')
    time.sleep(60)

    """不断检查重建任务是否存在"""
    start_time = time.time()
    while True:
        if not common.check_rebuild_job():
            log.info('rebuild job finish!!!')
            break
        time.sleep(20)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('rebuild job exist %dh:%dm:%ds' % (h, m, s))

    """将磁盘重新插入"""
    insert_disks(fault_node_ip, fault_disk_physicalid_lst)

    """删除磁盘"""
    for fault_disk_id in fault_disk_id_lst:
        ob_disk.remove_disks(fault_disk_id)

    log.info('wait 180s')
    time.sleep(180)

    """加入磁盘,并且加入存储池"""
    for i in range(len(fault_disk_id_lst)):
        ob_disk.add_disks(fault_node_id, fault_disk_uuid_lst[i], fault_disk_usage_lst[i])
        fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid_lst[i])
        ob_storage_pool.expand_storage_pool(storage_pool_id_lst[i], fault_disk_id_new)

    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean(FILE_NAME)
    log.info('succeed!')

if __name__ == '__main__':
    common.case_main(main)
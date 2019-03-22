#-*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean

####################################################################################
#
# author 刘俊鑫
# date 2018-07-13
# @summary：
#   qc_499,删除磁盘后取消删除，再删除时磁盘状态没有变化
# @steps:
#   step1:删除磁盘并取消删除磁盘
#   step2：再次删除磁盘，并查看磁盘状态
#   step3：十分钟后恢复磁盘
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]               # 本脚本名字
'''获取节点的所有数据盘id'''


def get_node_monopoly_disks_id(node_id, node_ip):
    ob_disk = common.Disk()

    '''获取一个节点内所有的共享硬盘和数据硬盘'''
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(node_id)

    '''根据数据盘的名字查到其id'''
    disk_id_list = []
    rc, stdout = common.get_disks(node_id)
    if rc != 0:
        raise Exception("get disks failed")
    else:
        result = common.json_loads(stdout)
        disk_list = result['result']['disks']
        for disk in disk_list:
            if disk['devname'] in monopoly_disk_names:
                disk_id_list.append(disk['id'])
    print disk_id_list
    return disk_id_list


def case():

    log.info("----------case----------")
    '''随机选取集群内的一个节点，获取节点的数据盘的物理id'''
    '''获取集群内所有节点的id'''
    ob_node = common.Node()

    nodeid_list = ob_node.get_nodes_id()

    '''随机选一个节点'''
    node_id = random.choice(nodeid_list)
    node_ip = ob_node.get_node_ip_by_id(node_id)

    '''根据节点ip和id随机选出将要删除的数据盘id'''
    disk_id_list = get_node_monopoly_disks_id(node_id, node_ip)
    disk_id_to_remove = random.choice(disk_id_list)
    log.info('node_id:%s, disk_id_to_remove:%s' % (node_id, disk_id_to_remove))
    for i in range(1, 10):
        '''删除磁盘并取消删除磁盘'''
        rc, stdout = common.remove_disks(disk_id_to_remove, auto_query='false')
        common.judge_rc(rc, 0, 'remove_disks failed')
        time.sleep(5)
        rc, stdout = common.cancel_remove_disks(disk_id_to_remove)
        common.judge_rc(rc, 0, 'remove_disks failed')
        time.sleep(5)

    '''再次删除磁盘并查询磁盘状态'''
    rc, stdout = common.remove_disks(disk_id_to_remove, auto_query='false')
    common.judge_rc(rc, 0, "remove_disks failed")
    time.sleep(20)

    disk = common.Disk()
    disk_state = disk.get_disk_state_by_id(node_id, disk_id_to_remove)
    if disk_state == 'DISK_STATE_HEALTH':
        log.info('disk_to_remove state is still DISK_STATE_HEALTH, it should has been changed to %s' % disk_state)
    else:
        log.info('disk_to_remove state is %s' % disk_state)

    '''取消删除磁盘'''
    rc, stdout = common.cancel_remove_disks(disk_id_to_remove)
    common.judge_rc(rc, 0, 'cancel_remove_disks failed')


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
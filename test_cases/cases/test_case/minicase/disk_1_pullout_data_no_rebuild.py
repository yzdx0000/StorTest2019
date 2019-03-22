# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import tool_use
import make_fault
import get_config
import prepare_clean

#################################################################
#
# Author: baorb
# date 2017-08-21
# @summary：
#    本用例测试磁盘故障，不等重建。
# @steps:
#    1，使用vdbench创建文件和数据校验
#    2，同时在一个节点上每隔30秒随机拔出插入一块数据盘
#
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]               # 本脚本名字
MINI_TRUE_PATH = os.path.join(prepare_clean.MINICASE_PATH, FILE_NAME)     # /mnt/volume1/mini_case/3_0015_truncate_test


def get_random_node_monopoly_disks(node_id, node_ip):
    """
    :author:         baoruobing
    :date  :         2018.06.07
    :description:    获取一个节点的所有数据盘
    :param node_id:  节点id
    :param node_ip:  节点ip
    :return:
    """
    ob_disk = common.Disk()

    '''获取一个节点内所有的共享硬盘和数据硬盘'''
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(node_id)
    '''获取节点内数据盘的物理id, 2:0:0:1'''
    monopoly_disk_id_list = []
    for disk_name in monopoly_disk_names:
        id = ob_disk.get_physicalid_by_name(node_ip, disk_name)
        monopoly_disk_id_list.append(id)

    return monopoly_disk_id_list


def random_disk_fault(node_ip, monopoly_disk_id_list):
    """
    :author:         baoruobing
    :date  :         2018.06.07
    :description:    随机拔出插入一块数据盘
    :param node_ip:
    :param monopoly_disk_id_list:
    :return:
    """
    time.sleep(10)

    disk_scsi_id = random.choice(monopoly_disk_id_list)
    for i in range(5):
        make_fault.pullout_disk(node_ip, disk_scsi_id, 'DATA')
        time.sleep(30)
        make_fault.insert_disk(node_ip, disk_scsi_id, 'DATA')
        time.sleep(30)


def case():
    log.info("----------case----------")
    '''随机选取集群内的一个节点，获取节点的数据盘的物理id'''
    '''获取集群内所有节点的id'''
    ob_node = common.Node()
    nodeid_list = ob_node.get_nodes_id()

    '''随机选一个节点'''
    node_id = random.choice(nodeid_list)
    node_ip = ob_node.get_node_ip_by_id(node_id)

    '''获取节点内的所有数据盘的物理id'''
    monopoly_disk_id_list1 = get_random_node_monopoly_disks(node_id, node_ip)

    client_ip_lst = get_config.get_allclient_ip()

    """恢复重建时间为默认值"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '3600000')

    p1 = Process(target=tool_use.vdbench_run, args=(MINI_TRUE_PATH, client_ip_lst[0], client_ip_lst[1]),
                 kwargs={'run_create': True, 'run_check_write': True})
    p2 = Process(target=random_disk_fault, args=(node_ip, monopoly_disk_id_list1))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    time.sleep(10)
    common.judge_rc(p1.exitcode, 0, 'vdbench_run')

    '''不断检查坏对象是否修复'''
    count = 0
    log.info("wait 60 seconds")
    time.sleep(60)
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 10 seconds")
        time.sleep(10)
        if common.check_badjobnr():
            break

    '''再跑检查数据的正确性'''
    tool_use.vdbench_run(MINI_TRUE_PATH, client_ip_lst[0], client_ip_lst[1], run_check=True)
    '''检查系统'''
    common.ckeck_system()
    log.info("case succeed!")


def main():
    prepare_clean.minicase_test_prepare(FILE_NAME)
    case()
    prepare_clean.minicase_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)
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
#################################################################
#
# Author: chenjy1
# Date: 2018-07-14
# @summary：
#    5节点虚拟机，vdbench跑64k文件，拔出一块共享硬盘池中的硬盘，数据读写断掉，插入也无法恢复
# @steps:
#    1，随机选取一个节点
#    2，同时进行1.跑vdbench 2.在一个节点上每隔5分钟随机拔出插入一块共享盘
#    3，确保全部共享盘都插入
#    4，检查环境磁盘状态和vdbench
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字


def vdbench_run(anchor_path, journal_path, *args):
    """
    :author :             chenjy1
    :date:                2018.07.30
    :description:         跑vdbench64k文件
    :param anchor_path:  vdbench anchor目录
    :param journal_path: journal目录
    :param args:         跑vdbench节点IP
    :return:
    """
    vdb = tool_use.Vdbenchrun(size='64k')

    rc = vdb.run_create(anchor_path, journal_path, *args)
    common.judge_rc(rc, 0, "vdbench run_create failed")

    rc = vdb.run_check_write(anchor_path, journal_path, *args)
    common.judge_rc(rc, 0, "vdbench run_check_write failed")

    return


def get_random_node_share_disks(node_id, node_ip):
    """
    :author :             chenjy1
    :date:                2018.07.30
    :description:         获取一个节点的所有共享盘的物理id
    :param node_id:      节点id
    :param node_ip:      节点IP
    :return:
    """
    ob_disk = common.Disk()

    """获取一个节点内所有的共享硬盘和数据硬盘"""
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(node_id)
    """获取节点内共享盘的物理id, 2:0:0:1"""
    share_disk_id_list = []
    for disk_name in share_disk_names:
        id = ob_disk.get_physicalid_by_name(node_ip, disk_name)
        share_disk_id_list.append(id)

    return share_disk_id_list


def random_disk_fault(node_ip, disk_id):
    """
    :author :                    chenjy1
    :date:                       2018.07.30
    :description:                随机拔出插入一块共享盘
    :param node_ip:             node_ip
    :param share_disk_id_list:  共享盘列表
    :return:
    """
    time.sleep(10)
    while True:
        cmd2 = ('ssh %s \"echo scsi remove-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id))
        cmd3 = ('ssh %s \"echo scsi add-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id))
        common.command(cmd2)
        time.sleep(150)
        common.command(cmd3)
        time.sleep(150)


def case():
    log.info("case begin")
    '''随机选取集群内的一个节点，获取节点的共享盘的物理id'''
    '''获取集群内所有节点的id'''
    ob_node = common.Node()
    ob_disk = common.Disk()
    nodeid_list = ob_node.get_nodes_id()

    '''随机选一个节点'''
    fault_node_id = random.choice(nodeid_list)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    share_disk_id_list1 = get_random_node_share_disks(fault_node_id, fault_node_ip)

    '''获取节点内的所有数据盘的物理id'''
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)
    """随机获取一个共享盘"""
    fault_disk_name = random.choice(share_disk_names)
    fault_disk_physical_id = ob_disk.get_physicalid_by_name(fault_node_ip, fault_disk_name)
    fault_disk_id = ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name)
    fault_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_disk_name)
    fault_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_disk_name)

    client_ip_lst = get_config.get_allclient_ip()

    """确定磁盘重建的等待时间为默认值"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '3600000')

    vdbench_run_path = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)

    log.info("2> 同时进行1.跑vdbench 2.在一个节点上每隔5分钟随机拔出插入一块共享盘")
    p1 = Process(target=vdbench_run, args=(vdbench_run_path, vdbench_run_path, client_ip_lst[0],))
    p2 = Process(target=random_disk_fault, args=(fault_node_ip, fault_disk_physical_id,))

    p1.start()
    p2.start()

    p1.join()
    p2.terminate()
    p2.join()

    """再获取一遍节点内的共享盘,防止进程停止的时候拔出了盘没有插入"""
    log.info("3> 确保全部共享盘都插入")
    share_disk_id_list2 = get_random_node_share_disks(fault_node_id, fault_node_ip)
    disk_list = []
    for disk_id in share_disk_id_list1:
        if disk_id not in share_disk_id_list2:
            disk_list.append(disk_id)
    for disk in disk_list:
        cmd = ('ssh %s \"echo scsi add-single-device %s > /proc/scsi/scsi\"' % (fault_node_ip, disk))
        common.command(cmd)

    log.info('wait 60s')
    time.sleep(60)

    """删除磁盘"""
    ob_disk.remove_disks(fault_disk_id)

    log.info('wait 180s')
    time.sleep(180)

    """加入磁盘"""
    ob_disk.add_disks(fault_node_id, fault_disk_uuid, fault_disk_usage)

    '''不断检查坏对象是否修复'''
    count = 0
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 60 seconds")
        time.sleep(60)
        if common.check_badjobnr():
            break
    log.info("4> 检查环境磁盘状态和vdbench")
    if True != common.check_alldisks_health():
        raise Exception("some disks is not health")

    if p1.exitcode != 0:
        raise Exception("vdbench is failed!!!!!!")

    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean
import tool_use
from multiprocessing import Process
import random

####################################################################################
#
# Author: chenjy1
# Date: 2018-07-12
# @summary：
#    5节点虚拟机，手动拔出硬盘再插入，磁盘的uuid变化
# @steps:
#    1、随机选一块盘，不论共享盘和数据盘
#    2、同时跑vdbench和拔盘插盘
#    3、检查磁盘uuid是否变化
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字


def pullout_one_disk(node_ip, disk_id):
    """
    :author :             chenjy1
    :date:                2018.07.30
    :description:         拔出一块盘
    :param node_ip:      节点IP
    :param disk_id:       盘的物理id
    :return:
    """
    time.sleep(10)
    cmd = ('ssh %s \"echo scsi remove-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id))
    common.command(cmd)
    time.sleep(10)
    return


def insert_one_disk(node_ip, disk_id):
    """
    :author :             chenjy1
    :date:                2018.07.30
    :description:         插入一块盘
    :param node_ip:      节点IP
    :param disk_id:      盘的物理id
    :return:
    """
    time.sleep(10)
    cmd = ('ssh %s \"echo scsi add-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id))
    common.command(cmd)
    time.sleep(10)
    return


def random_disk_fault(node_ip, disk_id):
    """
    :author :             chenjy1
    :date:                2018.07.30
    :description:         拔盘再插入
    :param node_ip:      节点IP
    :param disk_id:      盘的物理id
    :return:
    """
    pullout_one_disk(node_ip, disk_id)
    time.sleep(10)
    insert_one_disk(node_ip, disk_id)


def vdbench_run(anchor_path, journal_path, *args):
    """
    :author :             chenjy1
    :date:                2018.07.30
    :description:         跑vdbench读写
    :param anchor_path:  vdbench anchor目录
    :param journal_path: journal目录
    :param args:         跑vdbench节点IP
    :return:
    """
    vdb = tool_use.Vdbenchrun()
    rc = vdb.run_create(anchor_path, journal_path, *args)
    common.judge_rc(rc, 0, "vdbench run_create failed")
    rc = vdb.run_check_write(anchor_path, journal_path, *args)
    common.judge_rc(rc, 0, "vdbench run_create failed")


def case():
    log.info("case begin")

    log.info("1> 随机选一块盘，不论共享盘和数据盘")
    """随机选取集群内的一个节点，获取节点的共享盘的物理id"""
    """获取集群内所有节点的id"""
    ob_node = common.Node()
    ob_disk = common.Disk()

    node_id_lst = ob_node.get_nodes_id()

    """随机选一个节点"""
    fault_node_id = random.choice(node_id_lst)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    """获取一个节点内所有的共享硬盘和数据硬盘"""
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)

    all_disk_names = monopoly_disk_names[:]
    all_disk_names.extend(share_disk_names)

    """随机获取一个盘"""
    fault_disk_name = random.choice(all_disk_names)
    """故障盘的scsi id, id, uuid, 盘类型"""
    fault_disk_physicalid = ob_disk.get_physicalid_by_name(fault_node_ip, fault_disk_name)
    fault_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_disk_name)
    fault_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_disk_name)
    fault_disk_id = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)

    log.info("fault_node_id : %s"
             "\nfault_disk_name : %s"
             "\nfault_disk_physicalid : %s"
             "\nfault_disk_uuid : %s"
             "\nfault_disk_usage : %s"
             "\nfault_disk_id : %s"
             % (str(fault_node_id),
                fault_disk_name,
                fault_disk_physicalid,
                fault_disk_uuid,
                fault_disk_usage,
                str(fault_disk_id)))

    """确定磁盘重建的等待时间为默认值"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '3600000')

    log.info("2> 同时跑vdbench和拔盘插盘")
    client_ip_lst = get_config.get_allclient_ip()
    vdbench_run_path = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)
    p1 = Process(target=vdbench_run, args=(vdbench_run_path, vdbench_run_path, client_ip_lst[0],))
    p2 = Process(target=random_disk_fault, args=(fault_node_ip, fault_disk_physicalid,))

    p1.start()
    p2.start()

    time.sleep(80)

    p1.join()
    p2.terminate()
    p2.join()

    """再执行一遍插盘,防止进程停止的时候拔出了盘没有插入"""
    cmd = ('ssh %s \"echo scsi add-single-device %s > /proc/scsi/scsi\"' % (fault_node_ip, fault_disk_physicalid))
    common.command(cmd)

    if fault_disk_usage == "SHARED":
        rc, stdout = ob_disk.remove_disks(fault_disk_id)
        common.judge_rc(rc, 0, 'remove_disks failed')
        log.info('wait 180s')
        time.sleep(180)
        """磁盘加入到系统"""
        rc, stdout = ob_disk.add_disks(fault_node_id, fault_disk_uuid, fault_disk_usage)
        common.judge_rc(rc, 0, 'add_disks failed')

    cnt = 0
    while True:
        cnt += 1
        log.info('wait 15s')
        time.sleep(15)
        rc, stdout = common.get_disks(fault_node_id, print_flag=True)
        common.judge_rc(rc, 0, 'get_disks failed')
        pscli_info = common.json_loads(stdout)
        used_flag = False
        find_disk_flag = False
        for disk in pscli_info['result']['disks']:
            if disk['uuid'] == fault_disk_uuid:
                find_disk_flag = True
                if disk['usedState'] == 'IN_USE':
                    used_flag = True
                    break
        if used_flag is True:
            break
        if find_disk_flag == False:
            if cnt == 3:   # 有三次还没发现此磁盘uuid的话就先退出循环，等后面的判断
                break

    current_disk_uuid_list = ob_disk.get_disks_uuids(fault_node_id)

    """检查所有的磁盘状态是否正确"""
    if True != common.check_alldisks_health():
        raise Exception("some disks is not health")

    log.info("3> 检查磁盘uuid是否变化")
    """检查磁盘uuid是否变化"""
    log.info('fault_disk_uuid:')
    log.info(fault_disk_uuid)
    log.info('current_disk_uuid_list:')
    log.info(current_disk_uuid_list)
    if fault_disk_uuid not in current_disk_uuid_list:
        raise Exception("qc_123 is failed!!!!!!")
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

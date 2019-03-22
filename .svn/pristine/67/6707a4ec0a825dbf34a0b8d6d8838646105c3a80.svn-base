# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import get_config
import prepare_clean
import tool_use
#################################################################
#
# author 陈津宇
# date 2018-07-14
# @summary：
#    拔盘故障：单节点一个共享盘一个数据盘，不等待重建
# @steps:
#    1，随机选节点和两个盘
#    2，同时执行：1.跑vdbench 2、拔出插入两块盘，周期5分钟
#    3，共享盘需要手动删除添加
#    4，检查所有的磁盘状态和vdbench
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
MINI_TRUE_PATH = os.path.join(prepare_clean.MINICASE_PATH, FILE_NAME)      # /mnt/volume1/mini_case/3_0015_truncate_test


def vdbench_run(anchor_path, journal_path, *args):
    """
    运行vdbench，先创建，再读写
    :param anchor_path:
    :param journal_path:
    :param args:
    :return:
    """
    vdb = tool_use.Vdbenchrun()
    vdb.run_create(anchor_path, journal_path, *args)
    vdb.run_check_write(anchor_path, journal_path, *args)
    return


# 获取集群内的一个节点的所有共享盘的物理id
def get_random_node_share_disks_data_disks(node_id, node_ip):
    ob_disk = common.Disk()
    # 获取一个节点内所有的共享硬盘和数据硬盘
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(node_id)
    # 获取节点内磁盘的物理id, 2:0:0:1
    share_disk_id_list = []
    data_disk_id_list = []
    for disk_name in share_disk_names:
        id = ob_disk.get_physicalid_by_name(node_ip, disk_name)
        share_disk_id_list.append(id)
    for disk_name in monopoly_disk_names:
        id = ob_disk.get_physicalid_by_name(node_ip, disk_name)
        data_disk_id_list.append(id)

    return share_disk_id_list, data_disk_id_list


# 拔出插入一块盘，周期30s
def disk_fault_one_share_one_date(node_ip, share_disk_phyid, data_disk_phyid):
    time.sleep(10)
    for i in range(5):
        cmd_pullout_share_disk = ("echo scsi remove-single-device %s > /proc/scsi/scsi" % share_disk_phyid)
        cmd_insert_share_disk = ("echo scsi add-single-device %s > /proc/scsi/scsi" % share_disk_phyid)
        cmd_pullout_data_disk = ("echo scsi remove-single-device %s > /proc/scsi/scsi" % data_disk_phyid)
        cmd_insert_data_disk = ("echo scsi add-single-device %s > /proc/scsi/scsi" % data_disk_phyid)
        common.run_command(node_ip, cmd_pullout_share_disk)
        common.run_command(node_ip, cmd_pullout_data_disk)
        time.sleep(30)
        common.run_command(node_ip, cmd_insert_share_disk)
        common.run_command(node_ip, cmd_insert_data_disk)
        time.sleep(30)


def case():
    log.info("case begin")
    # 随机选取集群内的一个节点，获取节点的共享盘的物理id
    # 获取集群内所有节点的id
    ob_node = common.Node()
    ob_disk = common.Disk()
    node_id_lst = ob_node.get_nodes_id()
    # 随机选一个节点
    fault_node_id = random.choice(node_id_lst)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    # 获取一个节点内所有的共享硬盘和数据硬盘
    share_disk_name_list, data_disk_name_list = ob_disk.get_share_monopoly_disk_names(fault_node_id)
    share_disk_phyid_list1, data_disk_phyid_list1 = get_random_node_share_disks_data_disks(fault_node_id, fault_node_ip)

    fault_share_disk_name = random.choice(share_disk_name_list)
    fault_data_disk_name = random.choice(data_disk_name_list)

    # 两块故障盘的scsi id, id, uuid, 盘类型
    fault_share_disk_physicalid = ob_disk.get_physicalid_by_name(fault_node_ip, fault_share_disk_name)
    fault_share_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_share_disk_name)
    fault_share_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_share_disk_name)
    fault_share_disk_id = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_share_disk_uuid)

    fault_data_disk_physicalid = ob_disk.get_physicalid_by_name(fault_node_ip, fault_data_disk_name)
    fault_data_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_data_disk_name)
    fault_data_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_data_disk_name)
    fault_data_disk_id = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_data_disk_uuid)

    log.info("fault_node_id : %s"
             "\nfault_share_disk_name : %s"
             "\nfault_share_disk_physicalid : %s"
             "\nfault_share_disk_uuid : %s"
             "\nfault_share_disk_usage : %s"
             "\nfault_share_disk_id : %s"
             "\nfault_data_disk_name : %s"
             "\nfault_data_disk_physicalid : %s"
             "\nfault_data_disk_uuid : %s"
             "\nfault_data_disk_usage : %s"
             "\nfault_data_disk_id : %s"
             % (str(fault_node_id),
                fault_share_disk_name,
                fault_share_disk_physicalid,
                fault_share_disk_uuid,
                fault_share_disk_usage,
                str(fault_share_disk_id),
                fault_data_disk_name,
                fault_data_disk_physicalid,
                fault_data_disk_uuid,
                fault_data_disk_usage,
                str(fault_data_disk_id)))

    client_ip_lst = get_config.get_allclient_ip()
    p1 = Process(target=vdbench_run, args=(MINI_TRUE_PATH, MINI_TRUE_PATH, client_ip_lst[0]))
    p2 = Process(target=disk_fault_one_share_one_date,
                 args=(fault_node_ip, fault_share_disk_physicalid, fault_data_disk_physicalid))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    # 共享盘需要添加
    # 删除磁盘
    share_disk_id = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_share_disk_uuid)
    ob_disk.remove_disks(share_disk_id)
    log.info('wait 180s')
    time.sleep(180)

    # 磁盘加入到系统
    ob_disk.add_disks(fault_node_id, fault_share_disk_uuid, "SHARED")

    time.sleep(10)

    # 检查vdbench运行是否出错
    common.judge_rc(p1.exitcode, 0, 'vdbench')
    return


def main():
    prepare_clean.minicase_test_prepare(FILE_NAME, check_share_disk_num=True)
    case()
    prepare_clean.minicase_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
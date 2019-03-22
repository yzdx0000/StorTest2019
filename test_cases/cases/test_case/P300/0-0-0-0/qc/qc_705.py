# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import make_fault
import get_config
import prepare_clean
import tool_use
import prepare_clean

#################################################################
#
# Author: chenjy1
# Date: 2018-08-27
# @summary：
#    删除磁盘作业互斥未生效，并且没有完全删除掉
# @steps:
#    1.创建文件
#    2.创建完成后，删除两块数据盘
#    3.判断两块盘是否同时处于重建状态
#    4.恢复环境
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
VDBENCH_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)          # /mnt/volume1/defect_case/qc_705
get_node_stat_rc = 1


def case():
    log.info("case begin")
    ob_node = common.Node()
    ob_disk = common.Disk()
    ob_storage_pool = common.Storagepool()
    node_id_lst = ob_node.get_nodes_id()
    client_ip_lst = get_config.get_allclient_ip()
    """随机选一个节点"""
    fault_node_id = random.choice(node_id_lst)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)
    """获取故障节点内所有的共享硬盘和数据硬盘"""
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)
    """随机选择一个数据盘"""
    fault_disk_name_lst = random.sample(monopoly_disk_names, 2)
    fault_disk_physicalid_lst = []
    fault_disk_id_lst = []
    fault_disk_uuid_lst = []
    fault_disk_usage_lst = []
    storage_pool_id_lst = []
    for fault_disk_name in fault_disk_name_lst:
        """获取故障盘的scsi id, id, uuid, 盘类型, 存储池id"""
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
    log.info("1> 创建文件")
    client_ip_lst = get_config.get_allclient_ip()
    ob_vdb = tool_use.Vdbenchrun(depth=1, width=2, files=20, size='500m', threads=30)
    rc = ob_vdb.run_create(VDBENCH_PATH, VDBENCH_PATH, client_ip_lst[0])
    common.judge_rc(rc, 0, "vdbench create file failed")

    log.info('wait 10s')
    time.sleep(10)

    log.info("2> 创建完成后，删除两块数据盘")
    for disk_id in fault_disk_id_lst:
        ob_disk.remove_disks_asyn(disk_id)

    log.info("3> 判断两块盘是否同时处于重建状态")
    flag_two_act_rebuild = False
    disk_state_lst = ['init', 'init']
    start_time = time.time()
    while True:
        for i, diskid in enumerate(fault_disk_id_lst):
            disk_state = ob_disk.get_disk_state_by_id(fault_node_id, diskid)
            log.info("nodeid : %s  diskid : %s state :%s" % (fault_node_id, diskid, disk_state))
            disk_state_lst[i] = disk_state
        if disk_state_lst[0] == "DISK_STATE_REBUILDING_ACTIVE" \
                and disk_state_lst[1] == 'DISK_STATE_REBUILDING_ACTIVE':
            flag_two_act_rebuild = True
        time.sleep(10)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('wait two disks delete  %dh:%dm:%ds ' % (h, m, s))
        if disk_state_lst[0] == None and disk_state_lst[1] == None:
            log.info("two disks delete success")
            break
    log.info('wait 180s')
    time.sleep(180)

    log.info('4> 恢复环境')
    """加入磁盘,并且加入存储池"""
    for i, disk_uuid in enumerate(fault_disk_uuid_lst):
        ob_disk.add_disks(fault_node_id, disk_uuid, fault_disk_usage_lst[i])
        fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, disk_uuid)
        ob_storage_pool.expand_storage_pool(storage_pool_id_lst[i], fault_disk_id_new)

    rc, stdout = common.get_node_stat()
    common.judge_rc(rc, get_node_stat_rc, "get_node_stat  failed")

    common.judge_rc_unequal(flag_two_act_rebuild, True, "two disks are DISK_STATE_REBUILDING_ACTIVE at the same time")

    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)

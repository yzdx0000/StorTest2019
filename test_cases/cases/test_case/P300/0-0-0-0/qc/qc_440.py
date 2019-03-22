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

#################################################################
#
# Author: chenjy1
# Date: 2018-08-14
# @summary：
#    物理机3节点，2个磁盘插拔过程中出现配置覆盖，导致磁盘状态无法发生变迁
# @steps:
#    1、更改磁盘超时重建参数
#    2、先后拔出磁盘A和B
#    3、插入磁盘B，此时磁盘B的盘符变成A
#    4、观察磁盘A是否正常更改为孤立、重建、僵尸状态
#    5、环境恢复
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
VDBENCH_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)          # /mnt/volume1/defect_case/qc_614


def wait_disk_remove(fault_node_id, fault_disk_id,):
    """
    Author:                      chenjy1
    :date:                       2018.08.14
    :description:                等待盘被删除掉
    :param fault_node_id:       (int)故障节点ID
    :param fault_disk_id:       (int)故障磁盘ID
    :return:                    (bool)是否删除掉
    """
    obj_disk = common.Disk()
    flag_remove_disk = False
    start_time = time.time()
    while True:
        if obj_disk.check_disk_exist(fault_node_id, fault_disk_id):  # 盘存在则继续等，三分钟后仍存在则退出报错
            time.sleep(10)
            exist_time = int(time.time() - start_time)
            if exist_time > 1200:
                break
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            log.info('disk exist %dh:%dm:%ds' % (h, m, s))
        else:
            flag_remove_disk = True
            log.info("disk have been deleted!")
            break
    return flag_remove_disk


def case():
    ob_node = common.Node()
    ob_disk = common.Disk()
    ob_storage_pool = common.Storagepool()
    node_id_lst = ob_node.get_nodes_id()

    """随机选一个节点"""
    fault_node_id = random.choice(node_id_lst)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    """获取故障节点内所有的共享硬盘和数据硬盘"""
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)
    """随机选择一个数据盘"""
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

    log.info("1> 修改磁盘超时重建参数为60秒")
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')

    log.info("2> 先后拔出磁盘A和B")
    flag_up = True  # 是否与列表索引顺序一致
    make_fault.pullout_disk(fault_node_ip, fault_disk_physicalid_lst[0], fault_disk_usage_lst[0])
    make_fault.pullout_disk(fault_node_ip, fault_disk_physicalid_lst[1], fault_disk_usage_lst[1])

    if len(fault_disk_name_lst[0]) > len(fault_disk_name_lst[1]):
        flag_up = False
        log.info("%s > %s" % (fault_disk_name_lst[0], fault_disk_name_lst[1]))
    elif len(fault_disk_name_lst[0]) == len(fault_disk_name_lst[1]):
        if fault_disk_name_lst[0] > fault_disk_name_lst[1]:
            flag_up = False
            log.info("%s > %s" % (fault_disk_name_lst[0], fault_disk_name_lst[1]))
        else:
            log.info("%s < %s" % (fault_disk_name_lst[0], fault_disk_name_lst[1]))
    else:
        log.info("%s < %s" % (fault_disk_name_lst[0], fault_disk_name_lst[1]))
    log.info('wait 10s')
    time.sleep(10)
    log.info("3> 插入磁盘B，此时磁盘B的盘符变成A")
    if not flag_up:
        fault_disk_physicalid_lst = fault_disk_physicalid_lst[::-1]
        fault_disk_id_lst = fault_disk_id_lst[::-1]
        fault_disk_uuid_lst = fault_disk_uuid_lst[::-1]
        fault_disk_usage_lst = fault_disk_usage_lst[::-1]
        storage_pool_id_lst = storage_pool_id_lst[::-1]
        fault_disk_name_lst = fault_disk_name_lst[::-1]

    make_fault.insert_disk(fault_node_ip, fault_disk_physicalid_lst[1], fault_disk_usage_lst[1])
    log.info('wait 60s')
    time.sleep(60)
    """通过disk uuid 找到盘名"""
    rc, stdout = ob_disk.get_disk_info(fault_node_id)
    common.judge_rc(rc, 0, "get get_disk_info failed")
    disk_info = common.json_loads(stdout)
    for disk in disk_info['result']['disks']:
        if disk['uuid'] == fault_disk_uuid_lst[1]:  # 盘B的UUID
            log.info(disk['devname'])
            log.info(disk['uuid'])
            log.info(fault_disk_name_lst[1])
            if fault_disk_name_lst[1] == disk['devname']:
                log.info("disk B devname ")

    log.info("4> 观察磁盘A是否正常改变状态")
    start_time = time.time()
    while True:
        disk_state = ob_disk.get_disk_state_by_id(fault_node_id, fault_disk_id_lst[0])
        if disk_state == "DISK_STATE_ZOMBIE":  # 由于没有数据的话很快变僵尸，故判断僵尸状态，每个循环写明当前状态
            log.info('disk state is DISK_STATE_ZOMBIE')
            break
        time.sleep(5)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('wait DISK_STATE_ZOMBIE exist %dh:%dm:%ds now is %s uuid:%s' % (h, m, s, disk_state, fault_disk_uuid_lst[0]))

    log.info("5> 恢复环境")
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
    make_fault.insert_disk(fault_node_ip, fault_disk_physicalid_lst[0], fault_disk_usage_lst[0])
    """删除磁盘"""
    for i in range(len(fault_disk_id_lst)):
        ob_disk.remove_disks_asyn(fault_disk_id_lst[i])  # 删除磁盘都用异步，然后检查
        flag_remove_disk = wait_disk_remove(fault_node_id, fault_disk_id_lst[i])
        common.judge_rc(flag_remove_disk, True, "fault_disk_name: %s remove failed" % fault_disk_name_lst[i])
    log.info('wait 180s')
    time.sleep(180)
    """加入磁盘,并且加入存储池"""
    for i in range(len(fault_disk_id_lst)):
        ob_disk.add_disks(fault_node_id, fault_disk_uuid_lst[i], fault_disk_usage_lst[i])
        fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid_lst[i])
        ob_storage_pool.expand_storage_pool(storage_pool_id_lst[i], fault_disk_id_new)

    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '3600000')


    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)

# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import snap_common
import log
import prepare_clean
import get_config
import tool_use
import commands
import logging
import event_common

####################################################################################
#
# author liyao
# date 2018-08-09
# @summary：
#    修改硬盘速率等级成功
# @steps:
#   1、部署3节点集群环境
#   2、执行get_disks，获取任一集群节点的某块磁盘信息
#   3、删除上述磁盘
#   4、重新添加磁盘，获取该磁盘的新id
#   5、执行change_disk_speed_level，输入参数正确，预期执行成功(由于各节点需要有相同速率等级的磁盘，故需要获取IN_USE状态的磁盘速率)
#   6、执行get_events，检查结果显示是否正确
#   7、将上述磁盘加入存储池
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
EVENT_TRUE_PATH = os.path.join(event_common.EVENT_TEST_PATH, FILE_NAME)
DATA_DIR = os.path.join(EVENT_TRUE_PATH, 'data_dir')                  # /mnt/volume1/event/events_5_3_1_11/data_dir/
CREATE_EVENT_PATH = os.path.join('event', FILE_NAME)                   # /event/events_5_3_6_21
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


def case():
    ''''函数执行主体'''
    '''获取当前时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_1, cmd)
    script_start_time = int(stdout)  # 获取操作事件信息的起始时间

    '''2> 执行get_disks，获取任一集群节点的某块状态为"usedState": "IN_USE"的磁盘'''
    """获取集群内所有节点的id"""
    ob_node = common.Node()
    ob_disk = common.Disk()
    ob_storage_pool = common.Storagepool()
    nodeid_list = ob_node.get_nodes_id()

    """随机选一个节点"""
    fault_node_id = random.choice(nodeid_list)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    """获取节点内的所有数据盘的物理id"""
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)

    """随机获取一个数据盘"""
    fault_disk_name = random.choice(monopoly_disk_names)
    fault_disk_id = ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name)
    fault_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_disk_name)
    fault_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_disk_name)
    storage_pool_id = ob_disk.get_storage_pool_id_by_diskid(fault_node_id, fault_disk_id)

    '''3> 删除上述磁盘'''
    ob_disk.remove_disks(fault_disk_id)
    # todo 使用后台删除函数

    log.info('waiting for 180s')
    time.sleep(180)

    """检查磁盘是否删除"""
    start_time = time.time()
    while True:
        if 0 == ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name):
            log.info('node %s disk %s delete success!!!' % (fault_node_ip, fault_disk_name))
            break
        time.sleep(20)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('node %s disk %s delete %dh:%dm:%ds' % (fault_node_ip, fault_disk_name, h, m, s))

    '''4> 重新添加磁盘，并获取该磁盘的新id，只有未添加到存储池的磁盘才能修改硬盘速率'''
    ob_disk.add_disks(fault_node_id, fault_disk_uuid, fault_disk_usage)
    fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)

    '''5> 执行change_disk_speed_level，输入参数正确，预期执行成功'''
    rc, stdout = ob_disk.get_disk_info(fault_node_id)
    common.judge_rc(rc, 0, 'get disk failed!!!')
    stdout = common.json_loads(stdout)
    all_disks_info = stdout['result']['disks']
    for disk in all_disks_info:
        if disk['usedState'] == 'IN_USE':
            default_speed_level = disk['speed_level']
            break
    else:
        log.error('There is something wrong with storage_pool !!!')
        raise Exception('There is something wrong with storage_pool !!!')
    # todo 添加common函数
    rc, stdout = ob_disk.change_disk_speed_level(fault_disk_id_new, "MID")
    common.judge_rc(rc, 0, 'change disk speed level')

    '''6> 执行get_events，检查结果显示是否正确'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)

    code = '0x02060055'
    description = 'change disk speed level'
    event_common.check_events_result(script_start_time, code, description)

    '''7> 将上述磁盘加入存储池'''
    rc, stdout = ob_disk.change_disk_speed_level(fault_disk_id_new, default_speed_level)
    common.judge_rc(rc, 0, 'change disk speed level')
    ob_storage_pool.expand_storage_pool(storage_pool_id, fault_disk_id_new)
    log.info('waiting for 30s')
    time.sleep(30)

    """检查磁盘状态是否变为IN_USE"""
    rc, stdout = ob_disk.get_disk_info(fault_node_id)
    common.judge_rc(rc, 0, 'get disk failed!!!')
    stdout = common.json_loads(stdout)
    disks_info_new = stdout['result']['disks']
    for disk in disks_info_new:
        if disk['id'] == fault_disk_id_new:
            if disk['usedState'] != 'IN_USE':
                log.error('There is something wrong with expanding storage_pool !!!')
                raise Exception('There is something wrong with expanding storage_pool !!!')

    return


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=True)
    case()
    prepare_clean.test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

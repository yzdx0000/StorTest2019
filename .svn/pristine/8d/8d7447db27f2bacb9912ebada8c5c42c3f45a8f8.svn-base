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
# date 2018-08-13
# @summary：
#    扩容存储池失败
# @steps:
#   1、部署3节点集群环境
#   2、执行扩容存储池的命令，输入参数错误，预期扩容失败
#   3、执行get_events，检查结果显示是否正确
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
EVENT_TRUE_PATH = os.path.join(event_common.EVENT_TEST_PATH, FILE_NAME)
DATA_DIR = os.path.join(EVENT_TRUE_PATH, 'data_dir')                  # /mnt/volume1/event/events_5_3_1_11/data_dir/
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


def case():
    ''''函数执行主体'''
    '''获取当前时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_1, cmd)
    script_start_time = int(stdout)  # 获取操作事件信息的起始时间

    '''2> 执行扩容存储池的命令，输入参数错误，预期扩容失败'''
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
    storage_pool_id = ob_disk.get_storage_pool_id_by_diskid(fault_node_id, fault_disk_id)

    """扩容存储池，输入参数错误，预期失败"""
    incorrect_id = 0
    ob_storage_pool.expand_storage_pool(storage_pool_id, incorrect_id)
    log.info('waiting for 30s')
    time.sleep(30)

    '''3> 执行get_events，检查结果显示是否正确'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)

    code = '0x02040012'
    description = 'expand storage pool'
    event_common.check_events_result(script_start_time, code, description)

    return


def main():
    prepare_clean.event_test_prepare(FILE_NAME)
    case()
    prepare_clean.event_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
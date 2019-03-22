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
#    修改硬盘速率等级失败
# @steps:
#   1、部署3节点集群环境
#   2、执行get_disks，获取任一集群节点的某块状态为"usedState": "IN_USE"的磁盘
#   3、执行change_disk_speed_level，输入参数正确，但（由于磁盘状态不是free）预期执行失败
#   4、执行get_events，检查结果显示是否正确
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
    start_time = int(stdout)  # 获取操作事件信息的起始时间

    '''2> 执行get_disks，获取任一集群节点的某块状态为"usedState": "IN_USE"的磁盘'''
    obj_disk = common.Disk()
    obj_node = common.Node()
    node_ids = obj_node.get_nodes_id()
    select_node_id = random.choice(node_ids)
    rc, stdout = obj_disk.get_disk_info(select_node_id)
    common.judge_rc(rc, 0, 'get disk failed!!!')
    stdout = common.json_loads(stdout)
    disks_info = stdout['result']['disks']

    for disk in disks_info:
        if disk['usedState'] == 'IN_USE':
            select_disk_id = disk['id']
            break
    else:
        log.warn('There is something wrong with the system !!!')
        raise Exception('There is something wrong with the system !!!')

    '''3> 执行change_disk_speed_level，输入参数正确，但（由于磁盘状态不是free）预期执行失败'''
    speed_level_list = ['LOW', 'MID', 'HIGH']
    select_speed_level = random.choice(speed_level_list)
    rc, stdout = obj_disk.change_disk_speed_level(select_disk_id, select_speed_level)
    if 0 != rc:
        log.warn('change disk speed level failed !!!')

    '''4> 执行get_events，检查结果显示是否正确'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)

    code = '0x02060056'
    description = 'change disk speed level'
    event_common.check_events_result(start_time, code, description)

    return


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=True)
    case()
    prepare_clean.test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

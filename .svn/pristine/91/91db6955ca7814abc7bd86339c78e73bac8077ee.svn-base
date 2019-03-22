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
# Author: liyao
# date 2018-08-03
# @summary：
#    删除事件成功
# @steps:
#   1、部署3节点集群环境
#   2、获取所有事件的id，获取‘创建节点池、存储池’等事件的id
#   3、在除去创建类事件之外的内容中，选择一个待删除事件，执行delete_events操作
#   4、执行get_events，查看告警信息显示是否正确
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
    '''函数执行主体'''
    '''获取当前时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_1, cmd)
    start_time = int(stdout)   # 获取操作事件信息的起始时间

    '''2> 获取所有事件的id，获取‘创建节点池、存储池’等事件的id'''
    total_event_ids = []
    rc, events_info = event_common.get_events()
    common.judge_rc(rc, 0, 'get_events failed')
    for event in events_info:
        total_event_ids.append(event['id'])

    creating_type_codes = ['0x02040001', '0x02040007']
    creating_type_ids = []   # 创建类事件的id（节点池，存储池）
    for code in creating_type_codes:
        event_id = event_common.get_event_ids_by_code(code, 1)
        creating_type_ids.append(event_id)

    '''3> 在除去创建类事件之外的内容中，选择一个待删除事件，执行delete_events操作'''
    while True:
        delete_event_id = random.choice(total_event_ids)
        if delete_event_id not in creating_type_ids:
            break

    rc, stdout = event_common.delete_events(delete_event_id)
    if 0 != rc:
        log.error('deleting event failed !!!')
        raise Exception('deleting event failed !!!')

    '''4> 执行get_events，查看告警信息显示是否正确'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)

    code = '0x02020001'
    description = 'quota warning'
    event_common.check_events_result(start_time, code, description)

    return


def main():
    prepare_clean.event_test_prepare(FILE_NAME)
    case()
    prepare_clean.event_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
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
# date 2018-08-13
# @summary：
#    创建节点池成功（等待get_events接口完成）
# @steps:
#   1、部署3节点集群环境
#   2、执行get_events，查看创建节点池结果显示
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
    ''' 查看创建节点池结果显示'''
    rc, all_events_info = event_common.get_events()
    if 0 != rc:
        log.error('get events failed !!!')
        raise Exception('get events failed !!!')

    event_codes = []
    for event in all_events_info:
        event_codes.append(event['code'])
    typical_event_code = '0x02040007'   # 创建存储池成功对应的编号
    if typical_event_code in event_codes:
        log.info('creating storage_pool displayed correct !!!')
    else:
        log.error('creating storage_pool displayed wrong !!!')
        raise Exception('creating storage_pool displayed wrong !!!')

    return


def main():
    prepare_clean.event_test_prepare(FILE_NAME)
    case()
    prepare_clean.event_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
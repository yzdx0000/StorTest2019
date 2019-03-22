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
# date 2018-07-25
# @summary：
#    系统服务启动成功（等待get_events接口完成）
# @steps:
#   1、部署3节点集群环境
#   2、执行get_events，查看系统服务启动结果显示
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
    '''获取所有的操作信息'''
    rc, events_info = event_common.get_events()
    all_event_codes = []
    for event in events_info:
        all_event_codes.append(event['code'])
    typical_event_code = '0x02050001'   # 系统服务启动成功对应的编号
    if typical_event_code in all_event_codes:
        log.info('system service start-up displayed correct !!!')
    else:
        log.error('system service start-up displayed wrong !!!')
        raise Exception('system service start-up displayed wrong !!!')

    return


def main():
    prepare_clean.event_test_prepare(FILE_NAME)
    case()
    prepare_clean.event_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
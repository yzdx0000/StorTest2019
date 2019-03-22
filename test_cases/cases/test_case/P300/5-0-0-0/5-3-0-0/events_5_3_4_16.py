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
# date 2018-07-30
# @summary：
#    删除存储卷失败
# @steps:
#   1、部署3节点集群环境
#   2、执行delete_volume命令，输入参数错误，预期删除失败
#   3、执行get_events查看操作信息显示是否正确
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

    '''2> 执行delete_volume命令，输入参数错误，预期删除失败'''
    ob_volume = common.Volume()
    rc = ob_volume.delete_volume(0)  # 输入错误volume_id，预期删除失败
    if 0 != rc:
        log.error('deleting volume failed !!!')

    '''4> 执行get_events查看操作信息显示是否正确'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)

    '''获取最新的删除存储卷的操作信息'''
    code = '0x02040024'
    description = 'deleting volume'
    event_common.check_events_result(start_time, code, description)

    return


def main():
    prepare_clean.event_test_prepare(FILE_NAME)
    case()
    prepare_clean.event_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
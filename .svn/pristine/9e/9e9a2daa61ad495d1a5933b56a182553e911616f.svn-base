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
import quota_common

####################################################################################
#
# Author: liyao
# date 2018-07-25
# @summary：
#    添加配额失败（等待get_events接口完成）
# @steps:
#   1、部署3节点集群环境
#   2、对/mnt/volume1/snap/data_dir创建配额（参数输入错误，预期创建失败）
#   3、执行get_events，查看配额创建结果
#   4、删除配额，清理环境
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
    '''函数执行主体'''
    '''获取当前时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_1, cmd)
    start_time = int(stdout)   # 获取操作事件信息的起始时间

    '''2> 对/mnt/volume1/snap/data_dir创建配额（参数输入失败，预期创建失败）'''
    test_file = os.path.join(EVENT_TRUE_PATH, 'test_file')
    quota_common.creating_dir(SYSTEM_IP_0, EVENT_TRUE_PATH)
    cmd = 'dd if=/dev/zero of=%s bs=1M count=100' % test_file
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    if rc != 0:
        log.error('data directory create failed !!!')
        raise Exception('data directory create failed !!!')
    log.info('waiting for 10s')
    time.sleep(10)

    ''' 创建文件数配额'''
    quota_path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_EVENT_PATH, 'test_file')   # 使用错误的配额路径
    rc, json_info = quota_common.create_one_quota(quota_path, filenr_quota_cal_type='QUOTA_LIMIT',
                                                  filenr_hard_threshold=10)
    if rc != 0:
        log.info('quota create failed !!!')

    log.info('waiting for 10s')
    time.sleep(10)

    ''' 3> 执行get_events，查看配额创建结果'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)

    '''获取最新的创建配额的操作信息'''
    code = '0x02060030'
    description = 'creating quota'
    event_common.check_events_result(start_time, code, description)

    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean(FILE_NAME)
    common.rm_exe(SYSTEM_IP_0, os.path.join(quota_common.BASE_QUOTA_PATH, 'event'))
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
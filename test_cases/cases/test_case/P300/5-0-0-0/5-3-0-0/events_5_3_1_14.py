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
# date 2018-08-1
# @summary：
#    更新配置参数失败
# @steps:
#   1、部署3节点集群环境
#   2、执行update_param，输入参数错误（预期添加失败）
#   3、执行get_events查看配额更新结果显示
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
EVENT_TRUE_PATH = os.path.join(event_common.EVENT_TEST_PATH, FILE_NAME)
DATA_DIR = os.path.join(EVENT_TRUE_PATH, 'data_dir')                  # /mnt/volume1/event/events_5_3_1_11/data_dir/
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


def get_params(section, name):
    rc, stdout = common.get_params(section=section, name=name)
    if 0 != rc:
        log.error('get params failed !!!')
    stdout = common.json_loads(stdout)
    param_info = stdout['result']['parameters']
    return rc, param_info


def update_param(section, name, current):
    rc, stdout = common.update_param(section, name, current)
    if 0 != rc:
        log.error('update param failed !!!')
    return rc


def case():
    '''函数执行主体'''
    '''获取当前时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_1, cmd)
    start_time = int(stdout)   # 获取操作事件信息的起始时间

    '''2> 执行update_param，输入参数错误（预期添加失败）'''
    section = 'oPara'
    param_name = 'filmeta_ratio'

    rc, param_info = get_params(section, param_name)
    default_value = param_info[0]['default']
    min_value = param_info[0]['min_value']
    max_value = param_info[0]['max_value']
    select_value = random.randint(min_value, max_value)

    fault_section = 'opara'
    rc = update_param(fault_section, param_name, select_value)
    if 0 != rc:
        log.error('update param failed !!!')

    '''3> 执行get_events查看结果显示'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)

    code = '0x02010034'
    description = 'updating param'
    event_common.check_events_result(start_time, code, description)

    return


def main():
    prepare_clean.event_test_prepare(FILE_NAME)
    case()
    prepare_clean.event_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
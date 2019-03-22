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
#    删除机柜失败
# @steps:
#   1、部署3节点集群环境
#   2、执行add_cabinets命令，输入参数正确，预期成功
#   3、执行remove_cabinet命令，输入参数错误，预计删除失败
#   4、执行get_events，检查结果显示是否正确
#   5、删除上述机柜，清理环境
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
    start_time = int(stdout)  # 获取操作事件信息的起始时间

    '''2> 执行add_cabinets命令，输入参数正确，预期成功'''
    new_cabinet_name = FILE_NAME + '_cabinet1'
    height = random.choice(['36', '42'])
    rc, stdout = common.add_cabinets(new_cabinet_name, height)
    common.judge_rc(rc, 0, 'add cabinets failed !!!')

    log.info('waiting for 10s')
    time.sleep(10)

    '''3> 执行remove_cabinet命令，输入参数错误，预计删除失败'''
    rc, stdout = common.remove_cabinet(0)
    common.judge_rc_unequal(rc, 0, 'execution result is wrong !!!')

    '''4> 执行get_events，检查结果显示是否正确'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)

    code = '0x02060022'
    description = 'deleting cabinets'
    event_common.check_events_result(start_time, code, description)

    '''5> 删除上述机柜，清理环境'''
    """获取机柜信息"""
    rc, stdout = common.get_cabinets()
    stdout = common.json_loads(stdout)
    cabinets_info = stdout['result']['cabinets']
    for cabinet in cabinets_info:
        if cabinet['name'] == new_cabinet_name:
            new_cabinet_id = cabinet['id']
            break
    else:
        raise Exception('get cabinets failed !!!')

    rc, stdout = common.remove_cabinet(new_cabinet_id)
    common.judge_rc(rc, 0, 'remove cabinet failed !!!')

    return


def main():
    prepare_clean.event_test_prepare(FILE_NAME)
    case()
    prepare_clean.event_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
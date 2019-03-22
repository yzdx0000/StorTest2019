# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random
import json

import utils_path
import common
import snap_common
import log
import prepare_clean
import get_config
import tool_use
import logging
import event_common

####################################################################################
#
# Author: liyao
# date 2018-08-07
# @summary：
#    暂停任务成功
# @steps:
#   1、部署3节点集群环境
#   2、执行start_jobengine，输入参数正确，预期下发成功
#   3、执行pause_jobengine，输入参数正确，预期下发成功
#   4、执行get_events进行结果显示检查
#   5、取消上述任务
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
    '''获取当前时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_1, cmd)
    start_time = int(stdout)   # 获取操作事件信息的起始时间

    '''2> 执行start_jobengine，输入参数正确，预期创建成功'''
    jobengine_types = ['DIRQUOTA', 'CONCHK', 'BBS', 'RMFS']   # 支持手动暂停的后台任务列表（未包含BALANCE）
    # select_type = random.choice(jobengine_types)
    select_type = jobengine_types[3]   # 仅RMFS支持start和cancel

    rc, stdout = common.start_jobengine(select_type)
    common.judge_rc(rc, 0, 'start jobengine')

    '''3> 执行pause_jobengine，输入参数正确，预期下发成功'''
    log.info('waiting for 10s')
    time.sleep(10)
    rc, stdout = common.get_jobengines(select_type)
    stdout = common.json_loads(stdout)
    select_jobengine_info = stdout['result']['job_engines'][0]
    backend_id = select_jobengine_info['backend_id']

    rc, stdout = common.pause_jobengine(select_type, backend_id)
    common.judge_rc(rc, 0, 'pause jobengine failed')

    '''4> 执行get_events，查看告警信息显示是否正确'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)

    code = '0x02050015'
    description = 'pause jobengine'
    event_common.check_events_result(start_time, code, description)

    '''5> 取消上述任务'''
    rc, stdout = common.cancel_jobengine(select_type, backend_id)
    common.judge_rc(rc, 0, 'cancel jobengine failec')

    return


def main():
    prepare_clean.event_test_prepare(FILE_NAME)
    case()
    prepare_clean.event_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
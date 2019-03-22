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
import commands
import logging
import event_common

####################################################################################
#
# Author: liyao
# date 2018-08-06
# @summary：
#    添加影响策略成功
# @steps:
#   1、部署3节点集群环境
#   2、执行create_jobengine_impact，输入参数正确，预期创建成功
#   3、执行get_events，查看告警信息显示是否正确
#   4、删除上述影响策略
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

    '''2> 执行create_jobengine_impact，输入参数正确，预期创建成功'''
    add_impact_name = "test"
    impact_info = "'{\\\"intervals\\\":[{\\\"end_time\\\":{\\\"hour\\\":\\\"0\\\",\\\"minute\\\":\\\"0\\\"," \
                  "\\\"week_day\\\":\\\"1\\\"},\\\"link_id\\\":\\\"1\\\",\\\"start_time\\\":{\\\"hour\\\":\\\"0\\\"," \
                  "\\\"minute\\\":\\\"0\\\",\\\"week_day\\\":\\\"1\\\"}}],\\\"name\\\":\\\"test\\\"}'"
    rc, stdout = common.create_jobengine_impact(impact_info)
    common.judge_rc(rc, 0, 'create jobengine impact')

    '''3> 执行get_events，查看告警信息显示是否正确'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)

    code = '0x02050011'
    description = 'creating jobengine impact'
    event_common.check_events_result(start_time, code, description)

    '''4> 删除上述影响策略'''
    rc, stdout = common.get_jobengine_impact()
    stdout = common.json_loads(stdout)
    total_impacts = stdout['result']['impacts']
    add_impact_id = -1
    for impact in total_impacts:
        if impact['name'] == add_impact_name:
            add_impact_id = impact['id']

    rc, stdout = common.delete_jobengine_impact(add_impact_id)
    common.judge_rc(rc, 0, "delete jobengine impact failed")

    return


def main():
    prepare_clean.event_test_prepare(FILE_NAME)
    case()
    prepare_clean.event_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
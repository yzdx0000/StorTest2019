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
# date 2018-07-24
# @summary：
#    节点CPU利用率过高检测
# @steps:
#   1、部署3节点集群环境
#   2、执行pscli --command=clean_alarms清除现有告警信息
#   3、在一个节点上执行vdbench数据读写,过程中执行get_alarms查看告警信息是否正确
#   4、清除数据
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
    # 2> 执行pscli --command=clean_alarms清除现有告警信息
    rc, pscli_info = event_common.clean_alarms()
    common.judge_rc(rc, 0, 'clean_alarms falied')

    log.info('waiting for 10s')
    time.sleep(10)

    # 3> 在一个节点上执行vdbench数据读写,过程中执行get_alarms查看告警信息是否正确
    data_dir = EVENT_TRUE_PATH
    obj_create = tool_use.Vdbenchrun(size='(64k,30,128k,35,1m,30,5m,5)')
    obj_create.run_create(data_dir, '/tmp', SYSTEM_IP_0)
    time.sleep(20)
    p1 = Process(target=obj_create.run_check_write, args=(data_dir, '/tmp', SYSTEM_IP_0))
    p1.daemon = True
    p1.start()

    # 查看告警信息是否正确
    code = '0x01020013'
    description = 'Node CPU usage is too high !!'
    event_common.check_alarms_result(code, description)

    return


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=True)
    quota_common.creating_dir(SYSTEM_IP_0, EVENT_TRUE_PATH)
    case()
    prepare_clean.test_clean()
    common.rm_exe(SYSTEM_IP_0, os.path.join(quota_common.BASE_QUOTA_PATH, 'event'))
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import shell
import get_config
import prepare_clean
import tool_use
import commands
#################################################################
#
# Author: chenjy1
# Date: 2018-08-09
# @summary：
#    qc_56 系统关闭失败
# @steps:
#    1.关闭系统
#    2.检查系统状态是否是fault
#    3.启动系统
#    4.检查系统状态是否是SYSTEM_RUNNING
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字


def case():
    log.info("case begin")
    node_ip = common.SYSTEM_IP

    log.info("1> 关闭系统")
    rc, stdout = common.shutdown()
    common.judge_rc(rc, 0, "shutdown failed")
    log.info('wait 60s')
    time.sleep(60)

    log.info("2> 检查系统状态是否是fault")
    log.info("check SYSTEM_FAULT")
    rc, stdout = common.get_system_state()
    common.judge_rc(rc, 0, "get_system_state failed")
    if common.json_loads(stdout)['result']['storage_system_running_state'] != 'SYSTEM_SHUTDOWN':
        common.except_exit(info="state not SYSTEM_SHUTDOWN")

    log.info("3> 启动系统")
    rc, stout = common.startup()
    common.judge_rc(rc, 0, "startup failed")
    log.info('wait 60s')
    time.sleep(60)

    log.info("4> 检查系统状态是否是SYSTEM_RUNNING")
    log.info("check SYSTEM_RUNNING")
    rc, stdout = common.get_system_state()
    common.judge_rc(rc, 0, "get_system_state failed")
    if common.json_loads(stdout)['result']['storage_system_running_state'] != 'SYSTEM_RUNNING':
        common.except_exit(info="state not SYSTEM_RUNNING")

    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)

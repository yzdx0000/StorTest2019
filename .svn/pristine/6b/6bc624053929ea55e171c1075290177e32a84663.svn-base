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
# Date: 2018-08-16
# @summary：
#    跑vdbench同时启动/关闭系统
# @steps:
#    1.子进程跑vdbench
#    2.关闭系统、启动系统循环三次
#
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]         # 本脚本名字
VDBENCH_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)   # /mnt/parastor/defect_path/vdb_shutdown_startup


def vdbench_run(anchor_path, journal_path, *args):
    """
    :author :             chenjy1
    :date:                2018.07.30
    :description:         跑vdbench64k文件
    :param anchor_path:  vdbench anchor目录
    :param journal_path: journal目录
    :param args:         跑vdbench节点IP
    :return:
    """
    vdb = tool_use.Vdbenchrun(elapsed=4000)

    rc = vdb.run_create(anchor_path, journal_path, *args)
    common.judge_rc(rc, 0, "vdbench run_create failed")

    rc = vdb.run_write(anchor_path, *args)
    common.judge_rc(rc, 0, "vdbench run_check_write failed")

    return



def case():
    log.info("case begin")
    log.info("1> 子进程跑vdbench")
    node_ip = common.SYSTEM_IP
    client_ip_lst = get_config.get_allclient_ip()
    vdbench_run_path = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)
    p1 = Process(target=vdbench_run, args=(vdbench_run_path, vdbench_run_path, client_ip_lst[0],))
    p1.daemon = True

    p1.start()
    log.info('wait 60s')
    time.sleep(60)

    log.info("2> 启动关闭系统循环三次")
    for i in range(3):
        log.info("a.shutdown")
        rc, stdout = common.shutdown()
        common.judge_rc(rc, 0, "shutdown failed")
        log.info('wait 20s')
        time.sleep(20)

        log.info("b.check SYSTEM_FAULT")
        rc, stdout = common.get_system_state()
        common.judge_rc(rc, 0, "get_system_state failed")
        if common.json_loads(stdout)['result']['storage_system_running_state'] != 'SYSTEM_SHUTDOWN':
            common.except_exit(info="state not SYSTEM_SHUTDOWN")

        log.info("c.startup")
        rc, stdout = common.startup()
        common.judge_rc(rc, 0, "startup failed")
        log.info('wait 20s')
        time.sleep(20)

        log.info("d.check SYSTEM_RUNNING")
        rc, stdout = common.get_system_state()
        common.judge_rc(rc, 0, "get_system_state failed")
        if common.json_loads(stdout)['result']['storage_system_running_state'] != 'SYSTEM_RUNNING':
            common.except_exit(info="state not SYSTEM_RUNNING")

    p1.join()

    common.judge_rc(p1.exitcode, 0, "vdbench failed ")
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)

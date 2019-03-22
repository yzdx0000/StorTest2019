# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import make_fault
import get_config
import prepare_clean

#################################################################
#
# Author: baorb
# Date: 2018-08-07
# @summary：
#    本测试主要测试关闭启动系统。
# @steps:
#    1, 关闭系统
#    2，启动系统
#    3，检查系统正常
#
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字


def case():
    log.info("1> 关闭系统")
    rc, stdout = common.shutdown()
    common.judge_rc(rc, 0, "shutdown failed. \nstdout: %s" % (stdout))

    time.sleep(20)

    log.info("2> 启动系统")
    rc, stdout = common.startup()
    common.judge_rc(rc, 0, "startup failed. \nstdout: %s" % (stdout))

    log.info("3> 检查服务状态")
    start_time = time.time()
    while True:
        time.sleep(10)
        if common.check_service_state():
            break
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info("service not OK %dh:%dm:%ds!!!" % (h, m, s))


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)
#!/usr/bin/python
# -*- encoding:utf8 -*-

import sys
import utils_path
import log
import common
import fence_common
#
# Author: liuyzhb
# date 2019/03/15
# @summary：
#           开启fence命令执行
# @steps:
#           1、执行开启fence操作，能够成功
def main():
    log_file_path = log.get_log_path(sys.argv[0])
    log.init(log_file_path, True)
    fence = fence_common.Fence()

    log.info("0> 进行环境准备")
    fence.fence_prepare()
    log.info("1> 开启fence")
    rc,stdout = fence.fence_enable()
    common.judge_rc(rc, 0, "fence_enable failed!!! \nstdout: %s" % stdout)
    log.info('fence_enable case %s finish success!!!!!' %sys.argv[0] )

if __name__=="__main__":
    common.case_main(main)

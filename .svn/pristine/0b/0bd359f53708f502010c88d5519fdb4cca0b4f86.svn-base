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
#           判断zk、oJmgs、oRole的主在同一个节点上
# @steps:
#           1、判断三个进程的主是否在同一个节点上
def main():
    log_file_path = log.get_log_path(sys.argv[0])
    log.init(log_file_path, True)
    fence = fence_common.Fence()

    log.info("0> 进行环境准备")
    fence.fence_prepare()
    log.info("1> 判断三个进程的主是否在同一个节点上")
    rc= fence.if_master_unified()
    common.judge_rc(rc, 0, "master of zk、oJmgs、oRole is not one node!!!")
    log.info('master of zk、oJmgs、oRole is on the same node!!!!!')
    log.info('case %s finish success!!!!!' %sys.argv[0] )

if __name__=="__main__":
    common.case_main(main)

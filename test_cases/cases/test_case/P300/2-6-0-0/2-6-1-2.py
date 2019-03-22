#!/usr/bin/python
# -*- encoding=utf8 -*-
import sys
import time
import utils_path
import log
import common
import fence_common
#
# Author: liuyzhb
# date 2019/03/15
# @summary：
#           关闭fence功能且证明fence确实关闭成功了
# @steps:
#           1、关闭fence
#           2、等待60s
#           3、查询fence参数确实为0
#           4、主动将oPara进程fence掉,执行fence失败即为成功
# @changelog：
#

def main():
    fence = fence_common.Fence()
    log_file_path = log.get_log_path(sys.argv[0])
    log.init(log_file_path, True)
    fence = fence_common.Fence()

    log.info("0> 进行环境准备")
    fence.fence_prepare()

    log.info("1> 关闭fence")
    rc, stdout = fence.fence_disable()
    common.judge_rc(rc, 0, "run fence_disable failed!!!!! \nstdout: %s" % stdout)

    log.info("2 > 等待 60s")
    time.sleep(60)

    log.info("3 > 查询fence参数确实为0")
    current = fence.get_fence_current()
    log.info("current is %s" %current)
    common.judge_rc(int(current), 0, "disable fence but current is not 0")

    log.info("4 > 主动将oPara进程fence掉")
    fence_time = int(time.time())
    rc, stdout = fence.add_fence_service(sender_type = "oRole", node_id = 1, service_type = "oPara", force = "true")
    common.judge_rc(rc, -1, "add_fence_service success when fence_disabled,that is wrong,case failed!!!")
    log.info("case %s finish success!!!!!" %sys.argv[0] )

if __name__ == "__main__":
    common.case_main(main)






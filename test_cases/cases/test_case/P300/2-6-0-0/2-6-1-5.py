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
#           开启fence功能且证明fence确实关闭成功了
# @steps:
#           1、开启fence
#           2、等待60s
#           3、查询fence参数确实为1
#           4、主动将oPara进程fence掉
#           5、查询fence记录，查询到即为成功
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
    rc, stdout = fence.fence_enable()
    common.judge_rc(rc, 0, "run fence_enable failed!!!!! \nstdout: %s" % stdout)

    log.info("2 > 等待 60s")
    time.sleep(60)

    log.info("3 > 查询fence参数确实为1")
    current = fence.get_fence_current()
    log.info("current is %s" %current)
    common.judge_rc(int(current), 1, "enable fence but current is not 1")

    log.info("4 > 主动将oPara进程fence掉")
    rc,fence_time = common.get_time_of_parastor()
    log.info('fence_time is %s' % fence_time)
    common.judge_rc(rc, 0, "get time on all nodes failed", exit_flag=False)
    real_fence_time = time.strftime('%Y.%m.%d:%H.%M.%S',time.localtime(float(fence_time)))
    log.info('real_fence_time is %s' % real_fence_time)

    rc, stdout = fence.add_fence_service(sender_type = "oRole", node_id = 1, service_type = "oPara", force = "true")
    common.judge_rc(rc, 0, "add_fence_service failed!!!\n stdout is %s" %stdout)

    time.sleep(60)

    log.info("5 > 查询fence记录，查询到即为成功")
    rc= fence.check_fence_event(fence_time,fence_node_id = "1", fence_process =  "oPara")
    #rc, stdout = fence.check_fence_event(fence_time)
    if rc == 0:
        log.info('check_fence_event result is not empty,case finish success!!!!!')
    elif rc ==-2:
        log.info('check_fence_event result is empty, that is ,after disable fence 60s,fence_event alse have new event,case failed!!!')
    else:
        log.info( 'check_fence_eventfailed,case failed!!!')
    common.judge_rc(rc, 0, "check_fence_event failed,case failed!!! stdout is %s\n" %stdout)
if __name__ == "__main__":
    common.case_main(main)






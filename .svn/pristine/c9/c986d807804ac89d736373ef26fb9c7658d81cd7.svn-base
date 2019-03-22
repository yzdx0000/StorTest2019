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
import make_fault
import logging
import event_common
import quota_common
####################################################################################
#
# Author: liyao
# date 2018-08-2
# @summary：
#    节点管理服务异常（oJmgs）
# @steps:
#   1、部署3节点集群环境
#   2、vdbench数据读写过程中，kill oJmgs进程
#   3、执行get_events查看结果显示
#   4、查看oJmgs进程是否恢复
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


def check_process(process_name):
    cmd = 'ps axf |grep %s' % process_name
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    grep_info = stdout.split()
    check_dir = '/home/parastor/bin/' + process_name + '-1.0.jar'

    limit_time = 120
    used_time = 20
    while True:
        if used_time < limit_time:
            log.info('waiting for 20s')
            time.sleep(20)
            if check_dir in grep_info:
                log.info('process %s recovered successfully' % process_name)
                break
            else:
                used_time = used_time + 20
        else:
            log.error('%s recovery time out !!!' % process_name)
            raise Exception('%s recovery time out !!!' % process_name)
    return


def case():
    '''函数执行主体'''
    '''获取当前时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_1, cmd)
    start_time = int(stdout) - 30   # 获取操作事件信息的起始时间

    '''2> vdbench数据读写过程中，kill oJmgs进程'''
    '''随机获取集群内的一个节点，对其进行故障'''
    process_name = 'oJmgs'
    ob_node = common.Node()
    node_ip_list = ob_node.get_nodes_ip()
    node_ip = random.choice(node_ip_list)
    obj_vdb = tool_use.Vdbenchrun(size="(16k,30,64k,35,2m,30,8m,5)")
    p1 = Process(target=obj_vdb.run_create, args=(EVENT_TRUE_PATH, '/tmp', SYSTEM_IP_0))
    p2 = Process(target=make_fault.kill_process, args=(node_ip, process_name))

    p1.start()
    p2.start()

    p1.join()
    p2.terminate()
    p2.join()

    if p1.exitcode != 0:
        raise Exception("vdbench is failed!!!!!!")

    '''3> 执行get_events查看结果显示'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    # time.sleep(delay_time)

    code = '0x01030010'
    description = 'check oJmgs alarm right'

    cmd = "mv /home/parastor/bin/oJmgs /home/parastor/bin/oJmgs_bk"
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "mv oPara wrong")
    make_fault.kill_process(node_ip, process_name)

    event_common.check_alarms_result(code, description)
    # 恢复环境
    cmd1 = "mv /home/parastor/bin/oJmgs_bk /home/parastor/bin/oJmgs"
    rc, stdout = common.run_command(node_ip, cmd1)
    common.judge_rc(rc, 0, "mv oPara wrong")

    '''4> 查看oJmgs进程是否恢复'''
    '''不断检查坏对象是否修复'''
    count = 0
    log.info("wait 60 seconds")
    time.sleep(60)
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 10 seconds")
        time.sleep(10)
        if common.check_badjobnr():
            break

    check_process(process_name)
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

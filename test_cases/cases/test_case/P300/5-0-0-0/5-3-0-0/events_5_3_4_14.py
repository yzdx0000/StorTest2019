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

####################################################################################
#
# Author: liyao
# date 2018-07-30
# @summary：
#    创建存储卷失败
# @steps:
#   1、部署3节点集群环境
#   2、执行create_volume命令，创建名称为FILE_NAME的存储卷（参数错误，预期失败）
#   3、执行get_events查看操作信息显示是否正确
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

    ''' 2> 执行create_volume命令，创建名称为FILE_NAME的存储卷（参数错误，预期失败）'''
    '''输入错误参数id = 0'''
    volume_name = 'liliyao_' + FILE_NAME
    ob_volume = common.Volume()
    rc, stdout = common.get_node_pools()
    node_pool_info = common.json_loads(stdout)["result"]["node_pools"][0]
    ob_volume.create_volume(volume_name, 0, node_pool_info["stripe_width"],
                            node_pool_info["disk_parity_num"], node_pool_info["node_parity_num"],
                            node_pool_info["replica_num"])

    '''3> 执行get_events查看操作信息显示是否正确'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)

    '''获取最新的创建存储卷失败的操作信息'''
    code = '0x02040022'
    description = 'creating volume'
    event_common.check_events_result(start_time, code, description)

    return


def main():
    prepare_clean.event_test_prepare(FILE_NAME)
    case()
    prepare_clean.event_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
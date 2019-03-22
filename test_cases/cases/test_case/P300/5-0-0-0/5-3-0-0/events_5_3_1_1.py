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
import nas_common

####################################################################################
#
# author liyao
# date 2018-08-13
# @summary：
#    配置NTP时间服务器成功
# @steps:
#   1、部署3节点集群环境
#   2、执行set_ntp，输入参数正确，预期执行成功
#   3、执行get_events，检查结果显示是否正确
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
    ''''函数执行主体'''
    '''获取当前时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_1, cmd)
    start_time = int(stdout)  # 获取操作事件信息的起始时间

    '''2> 执行set_ntp，输入参数正确，预期执行成功'''
    ob_node = common.Node()
    nodeid_list = ob_node.get_nodes_id()
    """选择一个启动了ntp服务的节点ip，这里直接取ad服务器的ip"""
    ntp_node_ip = nas_common.AD_DNS_ADDRESSES
    pscli_info = nas_common.set_ntp(is_enabled='true', ntp_servers=ntp_node_ip)
    common.judge_rc(pscli_info['err_no'], 0, 'set ntp failed !!!')

    '''3> 执行get_events查看操作信息显示是否正确'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)

    code = '0x02010021'
    description = 'set ntp'
    event_common.check_events_result(start_time, code, description)

    return


def main():
    prepare_clean.event_test_prepare(FILE_NAME)
    case()
    prepare_clean.event_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
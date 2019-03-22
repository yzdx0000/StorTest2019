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
# author liyao
# date 2018-08-13
# @summary：
#    节点下线命令成功
# @steps:
#   1、部署3节点集群环境
#   2、执行make_node_offline，输入参数正确，预期执行成功
#   3、执行get_events，检查结果显示是否正确
#   4、执行节点上线命令，恢复环境
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
    script_start_time = int(stdout)  # 获取操作事件信息的起始时间

    '''2> 执行make_node_offline，输入参数正确，预期执行成功'''
    """获取集群内所有节点的id"""
    ob_node = common.Node()
    nodeid_list = ob_node.get_nodes_id()

    """随机选一个节点"""
    fault_node_id = random.choice(nodeid_list)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    """执行节点下线命令"""
    rc, stdout = common.make_node_offline(fault_node_id)
    common.judge_rc(rc, 0, 'make node offline failed !!!')

    """不断检查节点下线是否完成"""
    # todo 更换版本之前，执行下线操作；get_nodes，查看节点状态

    '''3> 执行get_events，检查结果显示是否正确'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)

    code = '0x02060013'
    description = 'make node offline'
    event_common.check_events_result(script_start_time, code, description)

    '''4> 执行节点上线命令，恢复环境'''
    rc, stdout = common.make_nodes_online(fault_node_id)
    common.judge_rc(rc, 0, 'make nodes online failed !!!')
    # todo 加入节点上线执行结果的检查

    return


def main():
    prepare_clean.event_test_prepare(FILE_NAME)
    case()
    prepare_clean.event_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
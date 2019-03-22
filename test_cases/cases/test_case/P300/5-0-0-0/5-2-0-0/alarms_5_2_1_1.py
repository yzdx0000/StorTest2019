# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import log
import common
import tool_use
import get_config
import make_fault
import event_common
import quota_common
import prepare_clean


####################################################################################
#
# Author: liyao
# date 2018-07-24
# @summary：
#    集群CPU利用率过高检测
# @steps:
#   1、部署3节点集群环境
#   2、执行pscli --command=clean_alarms清除现有告警信息
#   3、在一个节点上执行vdbench数据读写,另一个节点做断部分数据网随后恢复的操作
#   4、执行get_alarms查看告警信息是否正确
#   5、恢复节点数据网
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
EVENT_TRUE_PATH = os.path.join(event_common.EVENT_TEST_PATH, FILE_NAME)
DATA_DIR = os.path.join(EVENT_TRUE_PATH, 'data_dir')                  # /mnt/volume1/event/events_5_3_1_11/data_dir/
CREATE_EVENT_PATH = os.path.join('event', FILE_NAME)                   # /event/events_5_3_6_21
SYSTEM_IP_0 = get_config.get_parastor_ip(0)


def down_part_eth(ip):
    # 获取集群节点数据网,断掉随后恢复部分数据网
    obj_node = common.Node()
    node_id = obj_node.get_node_id_by_ip(ip)
    eth_list, data_ip_list, ip_mask_lst = obj_node.get_node_eth(node_id)
    eth_fault = random.choice(eth_list)
    make_fault.down_eth(ip, eth_fault)

    log.info('waiting for 10s')
    time.sleep(10)

    make_fault.up_eth(ip, eth_fault, ip_mask_lst)
    log.info('waiting for 10s')
    time.sleep(10)

    return


def case():
    # 2> 执行pscli --command=clean_alarms清除现有告警信息
    rc, pscli_info = event_common.clean_alarms()
    common.judge_rc(rc, 0, "clean_alarms failed")

    log.info('waiting for 10s')
    time.sleep(10)

    # 3> 在一个节点上执行vdbench数据读写,过程中断掉另一个节点的部分数据网并恢复
    data_dir = EVENT_TRUE_PATH
    obj_create = tool_use.Vdbenchrun(size='(64k,30,128k,35,5m,30,10m,5)')
    obj_create.run_create(data_dir, '/tmp', SYSTEM_IP_0, SYSTEM_IP_1, SYSTEM_IP_2)
    p1 = Process(target=obj_create.run_check_write, args=(data_dir, '/tmp', SYSTEM_IP_0, SYSTEM_IP_1, SYSTEM_IP_2))
    p2 = Process(target=down_part_eth, args=(SYSTEM_IP_2,))

    p1.daemon = True  # 主进程检测到告警事件，就结束
    p1.daemon = True
    p1.start()
    p2.start()
    time.sleep(60)

    # 4> 反复获取告警信息,查看告警信息是否正确
    code = '0x01010001'   # 集群CPU利用率过高告警对应的编号
    description = 'Cluster CPU usage is too high'
    event_common.check_alarms_result(code, description)
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
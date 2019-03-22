# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time

import utils_path
import common
import snap_common
import log
import prepare_clean
import get_config
import make_fault
import event_common
import quota_common

####################################################################################
#
# Author: liyao
# date 2018-07-23
# @summary：
#    节点管理服务异常检测
# @steps:
#   1、部署3节点集群环境
#   2、执行pscli --command=clean_alarms清除现有告警信息
#   3、断掉一个节点的数据网
#   4、get_alarms查看告警信息是否正确
#   5、恢复节点数据网
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


def case():
    # 2> 执行pscli --command=clean_alarms清除现有告警信息
    rc, pscli_info = event_common.clean_alarms()
    common.judge_rc(rc, 0, 'clean_alarms failed')

    log.info('waiting for 10s')
    time.sleep(10)

    # 3> 断掉一个节点的数据网
    obj_node = common.Node()
    node_id = obj_node.get_node_id_by_ip(SYSTEM_IP_1)
    eth_list, data_ip_list, ip_mask_lst = obj_node.get_node_eth(node_id)
    make_fault.down_eth(SYSTEM_IP_1, eth_list)

    log.info('waiting for 60s')
    time.sleep(60)

    # 4> get_alarms查看告警信息是否正确
    rc, pscli_info = event_common.get_alarms(fault_node_ip=SYSTEM_IP_1)

    time_waiting = 10
    sleep_mark = True
    while sleep_mark:
        log.info('waiting for %s' % time_waiting)
        time.sleep(time_waiting)
        rc, pscli_info = event_common.get_alarms(fault_node_ip=SYSTEM_IP_1)
        if rc != 0:
            log.info('system has not prepared well !!!')
            sleep_mark = True
        else:
            sleep_mark = False

    code = '0x01030010'
    description = 'Node management service is abnormal !!'
    event_common.check_alarms_result(code, description, fault_node_ip=SYSTEM_IP_1)
    start_time = time.time()
    while True:
        time.sleep(20)
        if common.check_ping(SYSTEM_IP_1):
            break
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('node %s cannot ping pass %dh:%dm:%ds' % (SYSTEM_IP_1, h, m, s))
    log.info('wait 20s')
    # 5> 恢复节点数据网
    make_fault.up_eth(SYSTEM_IP_1, eth_list, ip_mask_lst)
    log.info('waiting for 10s')
    time.sleep(10)

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
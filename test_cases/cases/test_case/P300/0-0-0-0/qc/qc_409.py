# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import make_fault
import get_config
import prepare_clean
import tool_use
#################################################################
#
# Author: chenjy1
# Date: 2018-07-14
# @summary：
#        down掉集群的数据网后，再up后，一个节点的节点状态和oMgcd的状态不正常
# @steps:
#       1、判断管理网和数据网是否复用
#       2、直接down集群数据网
#       3、进行检查
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
VDBENCH_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)          # /mnt/volume1/defect_case/qc_614


def waitnode_up(fault_node_ip):
    start_time = time.time()
    while True:
        time.sleep(20)
        if common.check_ping(fault_node_ip):
            break
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('node %s cannot ping pass %dh:%dm:%ds' % (fault_node_ip, h, m, s))
    log.info('wait 20s')


def case():
    log.info("1> 判断管理网和数据网是否复用")
    obj_node = common.Node()
    node_id_lst = obj_node.get_nodes_id()
    fault_node_id = random.choice(node_id_lst)
    node_ctrl_ip = obj_node.get_node_ip_by_id(fault_node_id)
    node_eth_lst, node_data_ip_lst, node_ip_mask_lst = obj_node.get_node_eth(fault_node_id)
    if node_ctrl_ip in node_data_ip_lst:
        common.except_exit(info="ctrl ip in data ip, this case can't run!!!")

    node_ip_eth_dict = {}
    log.info("2> 直接down/up集群所有节点数据网")
    for nodeid in node_id_lst:
        node_ip = obj_node.get_node_ip_by_id(nodeid)  # 节点一断网后下一个节点
        node_eth_lst, node_data_ip_lst, node_ip_mask_lst = obj_node.get_node_eth(nodeid)
        node_ip_eth_dict[node_ip] = node_eth_lst

    for node_ip in node_ip_eth_dict:
        make_fault.down_eth(node_ip, node_ip_eth_dict[node_ip])

    log.info("wait 30s")
    time.sleep(30)

    for node_ip in node_ip_eth_dict:
        waitnode_up(node_ip)

    log.info("wait 20s")
    time.sleep(20)
    # for node_ip in node_ip_eth_dict:
    #     make_fault.up_eth(node_ip, node_ip_eth_dict[node_ip])

    """获取集群所有节点的状态"""
    flag_node_state = 1
    for i in range(len(node_id_lst) - 1):
        flag_node_state = (flag_node_state << 1) + 1  # 111
    res_node_state = flag_node_state  # 111
    start_time = time.time()
    while True:
        for i, nodeid in enumerate(node_id_lst):
            if (flag_node_state & (1 << i)) != 0:
                if "NODE_STATE_HEALTHY" == obj_node.get_node_state(nodeid):
                    flag_node_state &= (res_node_state ^ (1 << i))  # 将i对应的标志位置0
        if flag_node_state & res_node_state == 0:  # 全0则通过
            break
        time.sleep(10)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('get_node_state not NODE_STATE_HEALTHY exist %dh:%dm:%ds' % (h, m, s))

    """获取集群节点的服务状态"""
    start_time = time.time()
    while True:
        rc = common.check_service_state()
        if rc:
            break
        time.sleep(10)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('wait check_service_state %dh:%dm:%ds' % (h, m, s))
    log.info("check_service_state ok ")
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

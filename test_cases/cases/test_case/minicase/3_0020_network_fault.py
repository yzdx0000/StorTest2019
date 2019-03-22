# -*-coding:utf-8 -*
import os
import time
from multiprocessing import Process

import utils_path
import log
import common
import tool_use
import make_fault
import get_config
import prepare_clean

#################################################################
#
# Author: baorb
# date 2017-08-21
# @summary：
#    本测试主要测试3节点P300的网络故障(本脚本前提:节点的管理网和数据网不能重复！！！)。
# @steps:
#    1，使用vdbench创建文件和数据校验
#    2，同时在一个节点上每隔5分钟随机拔出插入一块数据盘
#
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]             # 本脚本名字
MINI_TRUE_PATH = os.path.join(prepare_clean.MINICASE_PATH, FILE_NAME)   # /mnt/volume1/mini_case/3_0015_truncate_test

eth_list = []


def network_fault(node_ip, eth_list, ip_mask_lst):
    time.sleep(10)
    while True:
        make_fault.down_eth(node_ip, eth_list)
        time.sleep(120)
        make_fault.up_eth(node_ip, eth_list, ip_mask_lst)
        time.sleep(120)


def case():
    log.info("----------case----------")
    '''获取集群内所有节点的id'''
    client_ip_lst = get_config.get_allclient_ip()
    ob_node = common.Node()
    node_ip_list = ob_node.get_nodes_ip()

    '''获取节点id和ip对应关系'''
    fault_node_ip = None
    for node_ip in node_ip_list:
        if node_ip != client_ip_lst[0] and node_ip != client_ip_lst[1]:
            fault_node_ip = node_ip

    if fault_node_ip is None:
        log.error('Because this system does not meet the configuration requirements, this use case cannot run')
        raise Exception("Because this system does not meet the configuration requirements, this use case cannot run")

    node_id = ob_node.get_node_id_by_ip(fault_node_ip)
    '''获取节点3的数据网的eth名字'''
    obj_node = common.Node()
    eth_list, data_ip_list, ip_mask_lst = obj_node.get_node_eth(node_id)

    p1 = Process(target=tool_use.vdbench_run, args=(MINI_TRUE_PATH, client_ip_lst[0], client_ip_lst[1]),
                 kwargs={'run_create': True, 'run_check_write': True})
    p2 = Process(target=network_fault, args=(fault_node_ip, eth_list, ip_mask_lst))

    p1.start()
    p2.start()

    p1.join()
    p2.terminate()
    p2.join()

    '''恢复网络'''
    make_fault.up_eth(fault_node_ip, eth_list, ip_mask_lst)

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

    '''再跑检查数据的正确性'''
    tool_use.vdbench_run(MINI_TRUE_PATH, client_ip_lst[0], client_ip_lst[1], run_check=True)

    '''检查系统'''
    common.ckeck_system()
    log.info("case succeed!")


def main():
    prepare_clean.minicase_test_prepare(FILE_NAME)
    case()
    prepare_clean.minicase_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)
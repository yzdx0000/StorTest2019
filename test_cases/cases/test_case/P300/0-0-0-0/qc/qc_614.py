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
# Date: 2018-08-14
# @summary：
#    物理机5节点，删除文件过程中断网。
# @steps:
#    1、vdbench创建文件
#    2、vdbench删除文件同时故障网络
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
VDBENCH_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)          # /mnt/volume1/defect_case/qc_614


def net_fault(node_ip, eth_list, node_ip_mask_lst):
    """
    :author :           chenjy1
    :date:              2018.08.14
    :description:       每隔30秒down/up网
    :param node_ip:    (str)节点IP
    :param eth_lst:    (list)网卡列表
    :return:
    """
    while True:
        make_fault.down_eth(node_ip, eth_list)
        log.info("wait 30s")
        time.sleep(30)

        start_time = time.time()
        while True:
            time.sleep(20)
            if common.check_ping(node_ip):
                break
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            log.info('node %s cannot ping pass %dh:%dm:%ds' % (node_ip, h, m, s))
        log.info('wait 20s')

        make_fault.up_eth(node_ip, eth_list, node_ip_mask_lst)
        log.info("wait 30s")
        time.sleep(30)
    return


def case():
    obj_node = common.Node()
    node_id_lst = obj_node.get_nodes_id()
    fault_node_id = random.choice(node_id_lst)
    node_ctrl_ip = obj_node.get_node_ip_by_id(fault_node_id)
    node_eth_lst, node_data_ip_lst, node_ip_mask_lst = obj_node.get_node_eth(fault_node_id)
    if node_ctrl_ip in node_data_ip_lst:
        common.except_exit(info="ctrl ip in data ip, this case can't run!!!")

    log.info("1> vdbench创建文件")
    client_ip_lst = get_config.get_allclient_ip()
    ob_vdb = tool_use.Vdbenchrun(depth=3, width=4, files=100, size="4k")  # 删除的时间为5分钟左右
    rc = ob_vdb.run_create(VDBENCH_PATH, VDBENCH_PATH, client_ip_lst[0])
    common.judge_rc(rc, 0,  "vdbench run_create failed")

    log.info("2> vdbench删除文件同时故障网络")
    p1 = Process(target=ob_vdb.run_clean, args=(VDBENCH_PATH, client_ip_lst[0]))
    p2 = Process(target=net_fault, args=(node_ctrl_ip, node_eth_lst, node_ip_mask_lst))
    p1.daemon = True
    p2.daemon = True
    p1.start()
    p2.start()

    p1.join()
    p2.terminate()
    p2.join()

    """再up一遍故障节点的所有数据网"""
    make_fault.up_eth(node_ctrl_ip, node_eth_lst, node_ip_mask_lst)
    common.judge_rc(p1.exitcode, 0, 'vdbench clean file failed')
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
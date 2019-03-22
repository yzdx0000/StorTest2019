# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import log
import common
import tool_use
import make_fault
import get_config
import prepare_clean


#################################################################
#
# Author: chenjy1
# Date: 2018-08-14
# @summary：
#    物理机3节点集群，运行vdbench压力过程中，单根网络故障，出现oStor的core
# @steps:
#    1、子进程跑vdbench
#    2、单节点单个数据网循环故障
#    3、检查客户端挂载情况
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
VDBENCH_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)          # /mnt/volume1/defect_case/qc_614
N = 5


def case():
    obj_node = common.Node()
    node_id_lst = obj_node.get_nodes_id()
    fault_node_id = random.choice(node_id_lst)
    node_ctrl_ip = obj_node.get_node_ip_by_id(fault_node_id)
    node_eth_lst, node_data_ip_lst, ip_mask_lst = obj_node.get_node_eth(fault_node_id)
    if node_ctrl_ip in node_data_ip_lst:
        common.except_exit(info="ctrl ip in data ip, this case can't run!!!")

    fault_eth = random.choice(node_eth_lst)
    ip_mask = ip_mask_lst[node_eth_lst.index(fault_eth)]

    log.info("1> 跑vdbench")
    client_ip_lst = get_config.get_allclient_ip()
    p1 = Process(target=tool_use.vdbench_run, args=(VDBENCH_PATH, client_ip_lst[0], client_ip_lst[1]),
                 kwargs={'run_create': True, 'run_check_write': True})
    p1.daemon = True
    p1.start()

    log.info("2> 网络故障")
    for i in range(N):
        rc = make_fault.down_eth(node_ctrl_ip, fault_eth)
        common.judge_rc(rc, 0, "IP : %s  ifdown %s failed" % (node_ctrl_ip, fault_eth))
        log.info("wait 20s")
        time.sleep(20)

        rc = make_fault.up_eth(node_ctrl_ip, fault_eth, ip_mask)
        common.judge_rc(rc, 0, "IP : %s  ifup %s failed" % (node_ctrl_ip, fault_eth))
        log.info("wait 20s")
        time.sleep(20)

    tools_run_volume = os.path.basename(os.path.dirname(prepare_clean.DEFECT_PATH))

    """循环：1.判断所有独立客户端节点是否卡住或者掉了，2.判断俩进程是否全跑完了"""
    """如1出现，则脚本失败，如2出现，则往下走。"""
    log.info("3> 检查客户端挂载情况")
    all_client_list = get_config.get_allclient_ip()
    flag = 1
    while True:
        for clientip in all_client_list:
            res = common.check_client_state(clientip, tools_run_volume, timeout=1800)
            if -1 == res:
                common.except_exit('ssh failed !!!  please check node!!!')
            elif -2 == res:
                p1.terminate()
                p1.join()
                common.except_exit('client is blockup !!!')
            elif -3 == res:
                p1.terminate()
                p1.join()
                common.except_exit('not found volume !!!')
            if not p1.is_alive():
                flag = 0
                break
        if flag == 0:
            break
    p1.join()
    common.judge_rc(p1.exitcode, 0, 'vdbench failed')
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME, fault=False)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
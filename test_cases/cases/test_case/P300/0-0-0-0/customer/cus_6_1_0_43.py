# -*-coding:utf-8 -*
# !/usr/bin/python

import os
import time
import random
from multiprocessing import Process

import utils_path
import log
import common
import tool_use
import nas_common
import get_config
import make_fault
import quota_common
import prepare_clean

# =================================================================================
#  latest update:2018-08-17                                                    =
#  Author:wanggl                                                           =
# =================================================================================
# 2018-08-17:
# Author：wanggl
# @summary：
#   网络闪断
# @steps:
#   1、3节点集群，4+2:1配比，私有客户端挂载，通过vdbench写入数据；
#   2、循环闪断某个节点网络，闪断时间在0.1s-2s之间，执行1000次；
#
#

# changelog:


######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
volume_path = os.path.join(nas_common.BASE_NAS_PATH, FILE_NAME)          # /mnt/wangguanglin/cus_6_1_0_43
SYSTEM_IP = get_config.get_parastor_ip()
Private_clientIP1 = get_config.get_client_ip(0)
Private_clientIP2 = get_config.get_client_ip(1)
Private_clientIP3 = get_config.get_client_ip(2)


def vdbench_run(anchor_path, journal_path, *args):
    """
    :Author:            wanggl
    :date  :            2018.08.17
    :description:       运行vdbench,先创建，再读写
    :param anchor_path:  数据读写的路径
    :param journal_path:  校验文件创建的路径
    :param args:       运行vdbench的ip
    :return:
    """
    vdb = tool_use.Vdbenchrun(depth=2, width=3, files=40, xfersize='4k', elapsed=1200)
    rc = vdb.run_create(anchor_path, journal_path, *args)
    common.judge_rc(rc, 0, "vdb create file failed")
    rc = vdb.run_check_write(anchor_path, journal_path, *args)
    common.judge_rc(rc, 0, 'vdbench run ')
    return


def down_up_network(netcard, exe_ip, ip_mask_lst):
    for i in range(1, 10):
        for eth_name in netcard:
            make_fault.down_eth(exe_ip, eth_name)
        random_choice = random.uniform(0.1, 2)
        log.info(random_choice)
        time.sleep(random_choice)
        for eth_name in netcard:
            rc = make_fault.up_eth(exe_ip, eth_name, ip_mask_lst)
            while rc != 0:
                time.sleep(10)
                rc = make_fault.up_eth(exe_ip, eth_name, ip_mask_lst)
        time.sleep(120)   # 等待系统恢复


def case():
    log.info('1> 3节点集群，私有客户端挂载，通过vdbench写入数据')
    ob_node = common.Node()
    node_ids = ob_node.get_nodes_id()
    node_id = random.choice(node_ids)
    eth_lst, data_ip_lst, ip_mask_lst = ob_node.get_node_eth(node_id)
    quota_common.creating_dir(Private_clientIP1, volume_path)
    p1 = Process(target=vdbench_run, args=(volume_path, '/tmp', Private_clientIP1, Private_clientIP2,
                                           Private_clientIP3))
    p2 = Process(target=down_up_network, args=(eth_lst, SYSTEM_IP, ip_mask_lst))
    p1.start()
    time.sleep(60)
    p2.start()
    p1.join()
    common.judge_rc(p1.exitcode, 0, 'p1 process')
    p2.join()
    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    common.rm_exe(Private_clientIP1, volume_path)
    prepare_clean.test_clean(FILE_NAME)
    log.info('succeed!')


if __name__ == '__main__':
    common.case_main(main)

# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import sys

import utils_path
import common
import snap_common
import log
import prepare_clean
import rep_common
import random

####################################################################################
#
# Author: chenjy1
# Date 20181218
# @summary：
#    多条enable_rep命令并发执行， 预期一个成功
# @steps:
#    1、多个子进程，同时enable_rep所有节点
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
NEED_CLUSTER_LIST = [rep_common.MASTER]
THREADS = 10


def enable_rep_server(node_ids=None, print_flag=True, fault_node_ip=None, run_cluster=rep_common.MASTER):
    rc, pscli_info = rep_common.enable_rep_server(node_ids=node_ids, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                                  run_cluster=run_cluster)
    common.judge_rc(rc, 0, 'enable_rep_server failed')
    return


def case():
    rc, nodeid_lst = rep_common.get_node_id_lst()
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    nodeid_str = rep_common.convert_lst_to_str(nodeid_lst)

    log.info('1> [主]多个子进程并行enable_rep所有节点')
    pro_lst = []
    for pro in range(THREADS):
        pro_lst.append(Process(target=enable_rep_server, args=(nodeid_str,)))
    for pro in pro_lst:
        pro.daemon = True
    for pro in pro_lst:
        pro.start()
    for pro in pro_lst:
        pro.join()
    ret_lst = []
    for pro in pro_lst:
        ret_lst.append(pro.exitcode)
    if ret_lst.count(0) != 1:
        common.except_exit('Not only one thread succeeded')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

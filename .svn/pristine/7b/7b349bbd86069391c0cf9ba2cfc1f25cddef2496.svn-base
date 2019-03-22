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
#    测试节点加入复制域功能
# @steps:
#    1、复制域扩容节点
#    2、复制域缩容节点
#    3、[主]enable_rep另外一节点的的同时，disable_rep
#    4、[主]disable_rep 某节点的同时enable_rep
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
NEED_CLUSTER_LIST = [rep_common.MASTER]


def enable_rep_server(node_ids=None, print_flag=True, fault_node_ip=None, run_cluster=rep_common.MASTER):
    rc, pscli_info = rep_common.enable_rep_server(node_ids=node_ids, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                                  run_cluster=run_cluster)
    common.judge_rc(rc, 0, 'enable_rep_server failed')
    return


def disable_rep_server(node_ids=None, print_flag=True, fault_node_ip=None, run_cluster=rep_common.MASTER):
    rc, pscli_info = rep_common.disable_rep_server(node_ids=node_ids, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                           run_cluster=run_cluster)
    common.judge_rc(rc, 0, 'disable_rep_server failed')
    return


def case():
    log.info('1>复制域扩容')
    rc, master_all_id_lst = rep_common.get_node_id_lst()
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    if len(master_all_id_lst) <= 3:
        log.warn('节点数不大于3个，未满足此脚本运行条件')
        sys.exit(-1)
    master_id_lst = random.sample(master_all_id_lst, 3)
    log.info(master_all_id_lst)
    master_left_id_lst = master_all_id_lst
    for i in master_id_lst:
        master_left_id_lst.remove(i)
    three_node_str = rep_common.convert_lst_to_str(master_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=three_node_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    rc, pscli_info = rep_common.enable_rep_server(node_ids=master_left_id_lst[0])
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    log.info('2> 复制域缩容节点')
    rc, pscli_info = rep_common.disable_rep_server(node_ids=str(master_left_id_lst[0]))
    common.judge_rc(rc, 0, 'disable_rep_server failed')
    rc, pscli_info = rep_common.disable_rep_server(node_ids=rep_common.convert_lst_to_str(master_id_lst))
    common.judge_rc(rc, 0, 'disable_rep_server failed')

    log.info('3> [主]enable_rep另外一节点的同时，disable_rep')
    rc, pscli_info = rep_common.enable_rep_server(node_ids=three_node_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    p1 = Process(target=enable_rep_server, args=(master_left_id_lst[0], ))
    p1.daemon = True
    p1.start()
    time.sleep(1)
    rc, pscli_info = rep_common.disable_rep_server(node_ids=master_left_id_lst[0])
    common.judge_rc_unequal(rc, 0, 'disable_rep_server successful')

    p1.join()
    common.judge_rc(p1.exitcode, 0, 'enable_rep_server failed')

    log.info('6> [主]disable_rep 某节点的同时enable_rep')
    p1 = Process(target=disable_rep_server, args=(master_left_id_lst[0],))
    p1.daemon = True
    p1.start()
    time.sleep(1)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=master_left_id_lst[0])
    common.judge_rc_unequal(rc, 0, 'disable_rep_server successful')

    p1.join()
    common.judge_rc(p1.exitcode, 0, 'disable_rep_server failed')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

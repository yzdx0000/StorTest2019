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
#    多个删除同一个通道命令并行执行
# @steps:
#    1、[主从]创建复制域(节点数>=3随机)
#    2、[主]正常创建通道
#    3、[主]多个删除同一通道命令并行执行
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]
THREADS = 5


def delete_rep_channel(channel_id=None, print_flag=True, fault_node_ip=None, run_cluster=rep_common.MASTER):
    rc, stdout = rep_common.delete_rep_channel(channel_id=channel_id, print_flag=print_flag,
                                               fault_node_ip=fault_node_ip, run_cluster=run_cluster)
    common.judge_rc(rc, 0, 'delete_rep_channel failed')
    return


def case():
    log.info('case begin')
    rc, master_all_id_lst = rep_common.get_node_id_lst()
    common.judge_rc(rc, 0, 'get_node_id_lst failed')

    rc, slave_all_id_lst = rep_common.get_node_id_lst(run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'get_node_id_lst failed')

    master_id_lst = random.sample(master_all_id_lst, 3)
    slave_id_lst = random.sample(slave_all_id_lst, 3)

    log.info('1>[主从]创建3节点复制域')
    master_nodeid_str = rep_common.convert_lst_to_str(master_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=master_nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    slave_nodeid_str = rep_common.convert_lst_to_str(slave_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=slave_nodeid_str, run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    log.info('2> [主]创建通道')
    rc, channelip = rep_common.ip_for_create_channel(slave_id_lst)
    common.judge_rc(rc, 0, 'ip_for_create_channel failed')
    rc, pscli_info = rep_common.create_rep_channel(name=FILE_NAME, ip=channelip)
    common.judge_rc(rc, 0, 'create_rep_channel failed')

    rc, channelid = rep_common.get_channel_id_by_ip(channelip)
    common.judge_rc(rc, 0, 'get_channel_id_by_ip failed')

    log.info('3> [主]多个删除同一通道命令并行执行')
    pro_lst = []
    for pro in range(THREADS):
        pro_lst.append(Process(target=delete_rep_channel, args=(channelid,)))
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
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST, node_num=3)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

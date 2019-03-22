# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time

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
#    多个删除同一策略命令并行执行
# @steps:
#    1、[主从]创建复制域和通道
#    2、[主]创建pair
#    3、[主]创建策略
#    4、[主]多个子进程并行删除同一策略
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(slave)parastor/(slave)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]
THREADS = 5


def delete_rep_policies(ids=None, print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    rc, pscli_info = rep_common.delete_rep_policies(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                                    run_cluster=run_cluster)
    common.judge_rc(rc, 0, 'delete_rep_policies failed')
    return


def case():
    log.info('case begin')
    log.info('1>[主从]准备复制域和通道')
    rc, ready_info = rep_common.format_area_channel()
    common.judge_rc(rc, 0, 'format_area_channel failed')
    channelid = ready_info['channel']
    m_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir', 20)
    s_dir_lst = rep_common.create_dir(rep_common.SLAVE_NODE_LST[0], FILE_SLAVE_PATH, 'dir', 20)

    log.info('2> [主]正常创建pair')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[0],
                                        destination_directory=s_dir_lst[0])
    common.judge_rc(rc, 0, 'create_rep_pair faled')
    rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[0],
                                            destination_directory=s_dir_lst[0])
    common.judge_rc(rc, 0, 'get_one_pair_id failed')

    log.info('3>[主]创建策略')
    name = FILE_NAME
    rc, stdout = common.create_rep_policy(name=name, rep_pair_id=pairid, period_type=rep_common.BY_YEAR,
                                          months=1, days=1, hours=1, minute=1, expire_time=0)
    common.judge_rc(rc, 0, 'create_rep_policy failed')

    rc, policyid =  rep_common.get_rep_policy_id(name)
    common.judge_rc(rc, 0, 'get_rep_policy_id failed')

    log.info('4> [主]多个子进程并行删除同一策略')
    pro_lst = []
    for pro in range(THREADS):
        pro_lst.append(Process(target=delete_rep_policies, args=(policyid,)))
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

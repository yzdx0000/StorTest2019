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
#    创建策略测试
# @steps:
#    1、[主]准备复制域和通道
#    2、[主]创建pair
#    3、[主]串行创建多个策略
#    4、[主]并行创建多个策略
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(slave)parastor/(slave)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]
THREADS_NUMBER = 10

def create_rep_policy(name=None, rep_pair_id=None, period_type=None, months=False, week_days=None, days=None,
                      hours=None, minute=None, expire_time=None, print_flag=True, fault_node_ip=None,
                      run_cluster=rep_common.MASTER):
    rc, pscli_info = rep_common.create_rep_policy(name=name, rep_pair_id=rep_pair_id, period_type=period_type,
                                                  months=months, week_days=week_days, days=days, hours=hours,
                                                  minute=minute, expire_time=expire_time, print_flag=print_flag,
                                                  fault_node_ip=fault_node_ip, run_cluster=run_cluster)
    common.judge_rc(rc, 0, 'create_rep_policy failed')

    return


def delete_rep_pair(id=None, print_flag=True, fault_node_ip=None, run_cluster=rep_common.MASTER):
    rc, pscli_info = rep_common.delete_rep_pair(id=id, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                                run_cluster=run_cluster)
    common.judge_rc(rc, 0, 'create_rep_pair failed')


def case():
    log.info('case begin')
    log.info('1>[主从]准备复制域和通道')
    rc, ready_info = rep_common.format_area_channel()
    common.judge_rc(rc, 0, 'format_area_channel failed')
    channelid = ready_info['channel']
    m_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir', 20)
    s_dir_lst = rep_common.create_dir(rep_common.SLAVE_NODE_LST[0], FILE_SLAVE_PATH, 'dir', 20)

    pair_lst = []
    log.info('2> [主]正常创建pair')
    for i in range(20):
        rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[i],
                                            destination_directory=s_dir_lst[i])
        common.judge_rc(rc, 0, 'create_rep_pair faled')
        rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[i],
                                     destination_directory=s_dir_lst[i])
        common.judge_rc(rc, 0, 'get_one_pair_id failed')
        pair_lst.append(pairid)

    log.info('3>[主]创建多个策略')
    for i in range(10):
        name = FILE_NAME + str(i)
        rc, stdout = common.create_rep_policy(name=name,rep_pair_id=pair_lst[i], period_type='BY_YEAR',
                                                 months=1, days=1, hours=1, minute=1, expire_time=0)
        common.judge_rc(rc, 0, 'create_rep_policy failed')

    log.info('4>[主]子进程N，同时创建N个策略')
    pro_lst = []
    for i in range(10, 10+THREADS_NUMBER):
        name = FILE_NAME + str(i)
        pro_lst.append(Process(target=create_rep_policy, args=(name, pair_lst[i], 'BY_YEAR', 1, 1, 1, 1, 0)))
    for i in range(THREADS_NUMBER):
        pro_lst[i].start()
    for i in range(THREADS_NUMBER):
        pro_lst[i].join()
        common.judge_rc(0, pro_lst[i].exitcode, 'create_rep_policy failed pairid = %s' % pair_lst[i+10])


    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

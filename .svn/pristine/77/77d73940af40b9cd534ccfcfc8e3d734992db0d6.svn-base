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
#    删除pair相关
# @steps:
#    1、主从端创建3节点复制域，主端创建通道
#    2、创建N个pair
#    3、逐个删除
#    4、创建N个，子线程并行删除
#    5、先创建pair，后创建策略，删除pair，查看策略是否在
#    6、清除环境
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(slave)parastor/(slave)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]
THREADS_NUMBER = 20


def delete_rep_pair(id=None, print_flag=True, fault_node_ip=None, run_cluster=rep_common.MASTER):
    rc, pscli_info = rep_common.delete_rep_pair(id=id, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                                run_cluster=run_cluster)
    common.judge_rc(rc, 0, 'create_rep_pair failed')


def case():
    log.info('case begin')
    log.info('1> [主从]准备复制域和通道')
    rc, ready_info = rep_common.format_area_channel()
    common.judge_rc(rc, 0, 'format_area_channel failed')
    channelid = ready_info['channel']

    log.info('2>[主]创建N个pair')
    '''先创建目录，形式：/mnt/parastor/rep_test_dir/filename/filename0-->filename20'''
    m_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir', THREADS_NUMBER+1)
    s_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir', THREADS_NUMBER+1)
    pair_id_lst = []
    for i in range(THREADS_NUMBER):
        rc, pscli_info = rep_common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[i],
                                                    destination_directory=s_dir_lst[-1])
        common.judge_rc(rc, 0, 'create_rep_pair failed')
        rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[i],
                                                destination_directory=s_dir_lst[-1])
        common.judge_rc(rc, 0, 'get_one_pair_id failed')
        pair_id_lst.append(pairid)

    log.info('3>[主]逐个删除N个pair')
    for i in range(THREADS_NUMBER):
        rc, pscli_info = rep_common.delete_rep_pair(id=pair_id_lst[i])
        common.judge_rc(rc, 0, 'create_rep_pair failed')

    log.info('4> [主]再次创建N个pair 并行删除')
    '''先创建目录，形式：/mnt/parastor/rep_test_dir/filename/filename0-->filename20'''
    pair_id_lst = []
    for i in range(THREADS_NUMBER):
        rc, pscli_info = rep_common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[i],
                                                    destination_directory=s_dir_lst[-1])
        common.judge_rc(rc, 0, 'create_rep_pair failed')
        rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[i],
                                                destination_directory=s_dir_lst[-1])
        common.judge_rc(rc, 0, 'get_one_pair_id failed')
        pair_id_lst.append(pairid)

    pro_lst = []
    for i in range(THREADS_NUMBER):
        pro_lst.append(Process(target=delete_rep_pair, args=(pair_id_lst[i])))
    for i in range(THREADS_NUMBER):
        pro_lst[i].start()
    for i in range(THREADS_NUMBER):
        pro_lst[i].join()
        common.judge_rc(0, pro_lst[i].exitcode,
                        'create_rep_pair failed  s_dir:%s ,d_dir:%s' % (m_dir_lst[i], s_dir_lst[i]))

    log.info('5> 先创建pair，后创建策略，删除pair，查看策略是否在')
    rc, pscli_info = rep_common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[THREADS_NUMBER],
                                                destination_directory=s_dir_lst[THREADS_NUMBER])
    common.judge_rc(rc, 0, 'create_rep_pair failed')
    rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[THREADS_NUMBER],
                                            destination_directory=s_dir_lst[THREADS_NUMBER])
    common.judge_rc(rc, 0, 'get_one_pair_id failed')

    rc, pscli_info = rep_common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type=rep_common.BY_YEAR, months=1,
                                 days=1, hours=1, minute=1, expire_time=0)
    common.judge_rc(rc, 0, 'create_rep_policy failed')

    rc, policyid = rep_common.get_rep_policy_id(name=FILE_NAME)
    common.judge_rc(rc, 0, 'get_rep_policy_id failed')

    rc, pscli_info = rep_common.delete_rep_pair(id=pairid)
    common.judge_rc(rc, 0, 'create_rep_pair failed')

    rc, stdout = common.get_rep_policies(ids=policyid)
    common.judge_rc_unequal(rc, 0, 'get_rep_policies successful')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

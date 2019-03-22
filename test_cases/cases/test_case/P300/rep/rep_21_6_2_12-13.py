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
#   支持根目录->非根目录    支持非根目录->根目录
# @steps:
#   1、[主从]创建复制域和通道
#   2、[主从]创建新卷
#   3、[主]创建一个pair(主端根目录，从端非根目录)
#   4、[主]主目录创建目录+文件后起pair任务
#   5、[主]创建一个pair(主端非根目录，从端根目录)
#   6、[主]主目录创建目录+文件后起pair任务

# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(slave)parastor/(slave)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]
THREADS_NUMBER = 10


def case():
    log.info('case begin')
    log.info('1>[主从]准备复制域和通道')
    rc, ready_info = rep_common.format_area_channel()
    common.judge_rc(rc, 0, 'format_area_channel failed')
    channelid = ready_info['channel']
    m_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir', 20)
    s_dir_lst = rep_common.create_dir(rep_common.SLAVE_NODE_LST[0], FILE_SLAVE_PATH, 'dir', 20)

    log.info('2> [主从]创建新卷')
    m_volumeinfo_lst = []
    s_volumeinfo_lst = []
    for i in range(1):
        rc, volumeid = rep_common.create_one_volume(FILE_NAME + '_%s' % i, run_cluster=rep_common.MASTER)
        common.judge_rc(rc, 0, 'create_one_volume failed')
        m_volumeinfo_lst.append([FILE_NAME + '_%s' % i, volumeid])
        rc, volumeid = rep_common.create_one_volume(FILE_NAME + '_%s' % i, run_cluster=rep_common.SLAVE)
        common.judge_rc(rc, 0, 'create_one_volume failed')
        s_volumeinfo_lst.append([FILE_NAME + '_%s' % i, volumeid])

    log.info('3> [主]创建一个pair(主端根目录，从端非根目录)')
    pairid_lst = []
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_volumeinfo_lst[0][0],
                                        destination_directory=s_dir_lst[0])
    common.judge_rc(rc, 0, 'create_rep_pair faled')
    rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[0],
                                            destination_directory=s_dir_lst[0])
    common.judge_rc(rc, 0, 'get_one_pair_id failed')

    pairid_lst.append(pairid)

    log.info('4> [主]主目录创建目录+文件后起pair任务')
    rc = rep_common.vdb_create(m_volumeinfo_lst[0][0], '/tmp', rep_common.MASTER_RANDOM_NODE)
    common.judge_rc(rc, 0, 'vdb_create failed ')
    rc, pscli_info = rep_common.start_rep_task_scp(pairid)
    common.judge_rc(rc, 0, 'start_rep_task failed')
    '''检验一致性'''
    rc = rep_common.check_data_consistency(s_dir_lst[0], '/tmp', [rep_common.MASTER_RANDOM_NODE],
                                           [rep_common.SLAVE_RANDOM_NODE])
    common.judge_rc(rc, 0, 'check_data_consistency failed')

    log.info('5> [主]创建一个pair(主端非根目录，从端根目录)')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[0],
                                        destination_directory=s_volumeinfo_lst[0][0])
    common.judge_rc(rc, 0, 'create_rep_pair faled')
    rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[0],
                                            destination_directory=s_volumeinfo_lst[0][0])
    common.judge_rc(rc, 0, 'get_one_pair_id failed')
    pairid_lst.append(pairid)

    log.info('6> [主]主目录创建目录+文件后起pair任务')
    rc = rep_common.vdb_create(m_dir_lst[0], '/tmp', rep_common.MASTER_RANDOM_NODE)
    common.judge_rc(rc, 0, 'vdb_create failed ')
    rc, pscli_info = rep_common.start_rep_task_scp(pairid)
    common.judge_rc(rc, 0, 'start_rep_task failed')
    '''检验一致性'''
    rc = rep_common.check_data_consistency(s_volumeinfo_lst[0][0], '/tmp', [rep_common.MASTER_RANDOM_NODE],
                                           [rep_common.SLAVE_RANDOM_NODE])
    common.judge_rc(rc, 0, 'check_data_consistency failed')



    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

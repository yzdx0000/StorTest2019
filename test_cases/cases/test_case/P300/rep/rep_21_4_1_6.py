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
#    多pair创建相同时间的策略，定时起任务
# @steps:
#    1、[主从]创建复制域和通道
#    2、[主]创建9个pair
#    3、[主]9个pair创建同一时间起任务的策略
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(slave)parastor/(slave)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]
PAIR_NUMBER = 9


def case():
    log.info('case begin')
    log.info('1>[主从]准备复制域和通道')
    rc, ready_info = rep_common.format_area_channel()
    common.judge_rc(rc, 0, 'format_area_channel failed')
    channelid = ready_info['channel']
    m_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir', 20)
    s_dir_lst = rep_common.create_dir(rep_common.SLAVE_NODE_LST[0], FILE_SLAVE_PATH, 'dir', 20)

    pair_lst = []
    log.info('2> [主]创建9个pair')
    for i in range(PAIR_NUMBER):
        rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[i],
                                            destination_directory=s_dir_lst[i])
        common.judge_rc(rc, 0, 'create_rep_pair faled')
        rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[i],
                                                destination_directory=s_dir_lst[i])
        common.judge_rc(rc, 0, 'get_one_pair_id failed')
        pair_lst.append(pairid)

    log.info('3> [主]9个pair创建同一时间起任务的策略')
    nodeip = rep_common.MASTER_RANDOM_NODE
    left_second = 0
    hour = 0
    minute = 0
    second = 0
    cmd = 'date -d "2 minute" +%T'
    rc, stdout = common.run_command(nodeip, cmd)
    if rc != 0:
        return rc, 0, {}
    moment_str = stdout.strip()
    second = int(moment_str.split(':')[2])
    if (60 - second) <= 30:
        left_second = (120 - second) + 60
        hour = int(moment_str.split(':')[0])
        minute = int(moment_str.split(':')[1]) + 1
        if minute >= 60:
            minute -= 60
            hour += 1
            if hour >= 24:
                hour -= 24
    else:
        left_second = 60 - second + 60
        hour = int(moment_str.split(':')[0])
        minute = int(moment_str.split(':')[1])

    for i in range(PAIR_NUMBER):
        rc, pscli_info = rep_common.create_rep_policy(name=FILE_NAME + str(i), rep_pair_id=pair_lst[i],
                                                      period_type='BY_DAY', hours=hour, minute=minute)
        common.judge_rc(rc, 0, 'create_rep_policy failed')

    #todo 待开发提供查询任务起没起的方法  预计在left_second秒后起8个任务，第9个排队


    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

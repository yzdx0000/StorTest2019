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
#    策略修改后再修回
# @steps:
#    1、[主从]创建复制域和通道
#    2、[主]创建pair
#    3、[主]创建策略，时间为2分钟后
#    4、[主]修改策略，时间为1天后
#    5、[主]修改策略，时间仍为2分钟后，等2分钟策略运行
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(slave)parastor/(slave)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]


def case():
    log.info('case begin')
    log.info('1>[主从]准备复制域和通道')
    rc, ready_info = rep_common.format_area_channel()
    common.judge_rc(rc, 0, 'format_area_channel failed')
    channelid = ready_info['channel']
    m_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir', 20)
    s_dir_lst = rep_common.create_dir(rep_common.SLAVE_NODE_LST[0], FILE_SLAVE_PATH, 'dir', 20)

    log.info('2> [主]创建9个pair')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[0],
                                        destination_directory=s_dir_lst[0])
    common.judge_rc(rc, 0, 'create_rep_pair faled')
    rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[0],
                                            destination_directory=s_dir_lst[0])
    common.judge_rc(rc, 0, 'get_one_pair_id failed')

    log.info('3> [主]创建策略，时间为2分钟后')
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

    rc, pscli_info = rep_common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid,
                                                  period_type='BY_DAY', hours=hour, minute=minute)
    common.judge_rc(rc, 0, 'create_rep_policy failed')
    rc, policyid = rep_common.get_rep_policy_id(name=FILE_NAME)
    common.judge_rc(rc, 0, 'get_rep_policy_id failed')

    cmd = 'date  +%F-%T'
    rc, stdout = common.run_command(rep_common.MASTER_RANDOM_NODE, cmd)
    common.judge_rc(rc, 0, cmd + 'failed')
    mounth = stdout.split('-')[1] + 1
    if mounth > 12:
        mounth = 1
    day = stdout.split('-')[2]
    hour = stdout.split('-')[3].split(':')[0]
    minute = stdout.split('-')[3].split(':')[1]

    rc, pscli_info = rep_common.update_rep_policy(id=policyid, rep_pair_id=rep_common.BY_YEAR, months=mounth, days=day,
                                                  hours=hour, minute=minute, expire_time=0)
    common.judge_rc(rc, 0, 'update_rep_policy failed')

    rc, pscli_info = rep_common.update_rep_policy(id=policyid, period_type='BY_DAY', hours=hour, minute=minute)
    common.judge_rc(rc, 0, 'update_rep_policy failed')

    #todo 待开发提供查询任务起没起的方法  预计在left_second秒后起任务


    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

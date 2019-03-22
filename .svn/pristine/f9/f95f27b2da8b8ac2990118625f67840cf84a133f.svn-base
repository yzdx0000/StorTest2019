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
#    多个创建同一策略命令并行执行
# @steps:
#    1、[主从]创建复制域和通道
#    2、[主]创建1个pair
#    3、[主]子线程并行创建10个相同策略
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(slave)parastor/(slave)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]
THREADS = 10


def create_rep_policy(name=None, rep_pair_id=None, period_type=None, months=False, days=None,
                      hours=None, minute=None, expire_time=None, print_flag=True, fault_node_ip=None,
                      run_cluster=rep_common.MASTER):
    rc, pscli_info = rep_common.create_rep_policy(name=name, rep_pair_id=rep_pair_id, period_type=period_type,
                                                  months=months, days=days, hours=hours,
                                                  minute=minute, expire_time=expire_time, print_flag=print_flag,
                                                  fault_node_ip=fault_node_ip, run_cluster=run_cluster)
    common.judge_rc(rc, 0, 'create_rep_policy failed')

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

    cmd = 'date  +%F-%T'
    rc, stdout = common.run_command(rep_common.MASTER_RANDOM_NODE, cmd)
    common.judge_rc(rc, 0, cmd + 'failed')
    mounth = stdout.split('-')[1] + 1
    if mounth > 12:
        mounth = 1
    day = stdout.split('-')[2]
    hour = stdout.split('-')[3].split(':')[0]
    minute = stdout.split('-')[3].split(':')[1]

    log.info('3> [主]子线程并行创建10个相同策略')
    pro_lst = []
    for pro in range(THREADS):
        pro_lst.append(Process(target=create_rep_policy, args=(FILE_NAME, pairid, rep_common.BY_YEAR, mounth,
                                                               day, hour, minute, 0)))
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

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
#
# @steps:
#   1、[主从]创建复制域和通道
#   2、[主]创建pair(主端文件，从端目录)
#   3、[主]创建pair(从端文件，主端目录)
#   4、[主]创建A:/a -->B:/b的pair 和 A:/a -->B:/c的pair
#   5、[主]创建A:/a -->B:/b的pair 和 A:/a/a1 -->B:/c的pair
#   6、[主]创建A:/-->B:/的pair 和 A:/a -->B:不同卷/的pair
#   7、[主]创建A:/a -->B:/b的pair 和 A:/a -->B:/b/b1的pair
#   8、[主]创建A:/ -->B:/的pair 和 A:/ -->B:/b的pair
#   9、[主]创建A:/a/a1 -->B:/b的pair 和 A:/a -->B:/c的pair
#   10、[主]创建A:/a -->B:/b/b1的pair 和 A:/a -->B:/b的pair
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
    channelid = ready_info['channel']['result'][0]['id']
    m_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir', 20)
    s_dir_lst = rep_common.create_dir(rep_common.SLAVE_NODE_LST[0], FILE_SLAVE_PATH, 'dir', 20)
    '''准备文件'''
    rc = rep_common.create_file(rep_common.MASTER_RANDOM_NODE, m_dir_lst[0], 'file', 1, 1)
    common.judge_rc(rc, 0, 'create_file failed')
    rc = rep_common.create_file(rep_common.SLAVE_RANDOM_NODE, s_dir_lst[0], 'file', 1, 1)
    common.judge_rc(rc, 0, 'create_file failed')

    '''使用序号0的目录'''
    log.info('2> [主]创建pair(主端文件，从端目录)')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid,
                                        source_directory=os.path.join(os.path.join(m_dir_lst[0], 'file1')),
                                        destination_directory=s_dir_lst[0])
    common.judge_rc_unequal(rc, 0, 'create_rep_pair failed')

    log.info('3> [主]创建pair(从端文件，主端目录)')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid,source_directory=m_dir_lst[0],
                                        destination_directory=os.path.join(os.path.join(s_dir_lst[0], 'file1')))
    common.judge_rc_unequal(rc, 0, 'create_rep_pair failed')

    '''使用序号1、2的目录'''
    log.info('4>[主]创建A:/a -->B:/b的pair 和 A:/a -->B:/c的pair')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[1],
                                        destination_directory=s_dir_lst[1])
    common.judge_rc(rc, 0, 'create_rep_pair failed')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[1],
                                        destination_directory=s_dir_lst[2])
    common.judge_rc(rc, 0, 'create_rep_pair failed')

    '''使用序号3、4的目录'''
    log.info('5> [主]创建A:/a -->B:/b的pair 和 A:/a/a1 -->B:/c的pair')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[3],
                                        destination_directory=s_dir_lst[3])
    common.judge_rc(rc, 0, 'create_rep_pair failed')
    dir_lst = rep_common.create_dir(rep_common.MASTER_RANDOM_NODE, m_dir_lst[3], 'dir', 1)
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=dir_lst[0],
                                        destination_directory=s_dir_lst[4])
    common.judge_rc_unequal(rc, 0, 'create_rep_pair successful')

    log.info('6> [主]创建A:/-->B:/的pair 和 A:/a -->B:不同卷/的pair')

    m_volumeinfo_lst = []
    s_volumeinfo_lst = []
    for i in range(2):
        rc, volumeid = rep_common.create_one_volume(FILE_NAME + '_%s' % i, run_cluster=rep_common.MASTER)
        common.judge_rc(rc, 0, 'create_one_volume failed')
        m_volumeinfo_lst.append([FILE_NAME + '_%s' % i, volumeid])
        rc, volumeid = rep_common.create_one_volume(FILE_NAME + '_%s' % i, run_cluster=rep_common.SLAVE)
        common.judge_rc(rc, 0, 'create_one_volume failed')
        s_volumeinfo_lst.append([FILE_NAME + '_%s' % i, volumeid])

    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_volumeinfo_lst[0][0],
                                        destination_directory=s_volumeinfo_lst[0][0])
    common.judge_rc(rc, 0, 'create_rep_pair failed')

    dir_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, m_volumeinfo_lst[0][0], 'dir', 1)
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=dir_lst[0],
                                        destination_directory=s_volumeinfo_lst[1][0])
    common.judge_rc_unequal(rc, 0, 'nesting create_rep_pair failed')

    '''使用序号5的目录'''
    log.info('7> [主]创建A:/a -->B:/b的pair 和 A:/a -->B:/b/b1的pair')
    dir_5_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, m_dir_lst[5], 'dir', 1)
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[5],
                                        destination_directory=s_dir_lst[5])
    common.judge_rc(rc, 0, 'nesting create_rep_pair failed')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[5],
                                        destination_directory=dir_5_lst[0])
    common.judge_rc_unequal(rc, 0, 'nesting create_rep_pair successful')

    log.info('8、[主]创建A:/ -->B:/的pair 和 A:/ -->B:/b的pair')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_volumeinfo_lst[1][0],
                                        destination_directory=s_volumeinfo_lst[1][0])
    common.judge_rc(rc, 0, 'create_rep_pair failed')

    volume_dir_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, s_volumeinfo_lst[1][0], 1)
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_volumeinfo_lst[1][0],
                                        destination_directory=volume_dir_lst[0])
    common.judge_rc_unequal(rc, 0, 'create_rep_pair failed')

    log.info('9> [主]创建A:/a/a1 -->B:/b的pair 和 A:/a -->B:/c的pair')
    '''使用序号6、7的目录'''
    dir_6_lst = rep_common.create_dir(rep_common.MASTER_RANDOM_NODE, m_dir_lst[6],'dir', 1)
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=dir_6_lst[0],
                                        destination_directory=s_dir_lst[6])
    common.judge_rc(rc, 0, 'nesting create_rep_pair failed')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[6],
                                        destination_directory=s_dir_lst[7])
    common.judge_rc_unequal(rc, 0, 'nesting create_rep_pair successful')

    log.info('10> [主]创建A:/a -->B:/b/b1的pair 和 A:/a -->B:/b的pair')
    dir_8_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, s_dir_lst[8], 'dir', 1)
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[8],
                                        destination_directory=dir_8_lst[0])
    common.judge_rc(rc, 0, 'nesting create_rep_pair failed')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[8],
                                        destination_directory=s_dir_lst[9])
    common.judge_rc_unequal(rc, 0, 'nesting create_rep_pair successful')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

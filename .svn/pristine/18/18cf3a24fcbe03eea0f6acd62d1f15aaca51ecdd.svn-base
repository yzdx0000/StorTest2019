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
#   软/硬链接的复制   注：19年6月的版本不支持软硬链接，处理方式是：软连接直接不管，硬链接复制过去后变为俩文件
# @steps:
#   1、[主从]创建复制域和通道
#   2、[主]创建一个pair
#   3、[主]创建主目录内对目录和文件的软连接，起pair任务
#   4、[主]创建到主目录外对目录和文件的软连接，起pair任务
#   5、[主]创建主目录内硬连接，起pair任务
#   6、[主]创建到主目录外的硬连接，起pair任务
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

    log.info('2> [主]正常创建pair')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[0],
                                        destination_directory=s_dir_lst[0])
    common.judge_rc(rc, 0, 'create_rep_pair faled')
    rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[0],
                                            destination_directory=s_dir_lst[0])
    common.judge_rc(rc, 0, 'get_one_pair_id failed')

    log.info('3> [主]创建主目录内对目录和文件的软连接，起pair任务')
    rc = rep_common.create_file(rep_common.MASTER_RANDOM_NODE, m_dir_lst[0], 'file', 2, 1)
    common.judge_rc(rc, 0, 'create_file failed')
    dir_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, m_dir_lst[0], 'dir', 1)
    rc = rep_common.create_file(rep_common.MASTER_RANDOM_NODE, FILE_MASTER_PATH, 'file', 2, 1)
    common.judge_rc(rc, 0, 'create_file failed')
    dir_out_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, FILE_MASTER_PATH, 'dir', 1)

    '''文件'''
    cmd = 'ln -s %s %s ' % (os.path.join(m_dir_lst[0], 'soft_file'), os.path.join(m_dir_lst[0], 'file_1'))
    rc, stdout = common.run_command(rep_common.MASTER_RANDOM_NODE, cmd)
    common.judge_rc(rc, 0, cmd + 'failed')
    rc, pscli_info = rep_common.start_rep_task_scp(pair_id=pairid)
    common.judge_rc(rc, 0, 'start_rep_task_scp failed')
    cmd = 'ls %s' % (os.path.join(s_dir_lst[0], 'soft_file')) # 预期不能存在软连接
    rc, stdout = common.run_command(rep_common.SLAVE_RANDOM_NODE, cmd)
    common.judge_rc_unequal(rc, 0, 'can find soft_file')
    cmd = 'ls %s' % (os.path.join(s_dir_lst[0], 'file_1'))   # 预期存在file_1文件
    rc, stdout = common.run_command(rep_common.SLAVE_RANDOM_NODE, cmd)
    common.judge_rc(rc, 0, 'cannot find file_1')

    '''目录'''
    cmd = 'ln -s %s %s ' % (os.path.join(m_dir_lst[0], 'soft_dir'), os.path.join(m_dir_lst[0], 'dir0'))
    rc, stdout = common.run_command(rep_common.MASTER_RANDOM_NODE, cmd)
    common.judge_rc(rc, 0, cmd + 'failed')
    rc, pscli_info = rep_common.start_rep_task_scp(pair_id=pairid)
    common.judge_rc(rc, 0, 'start_rep_task_scp failed')
    cmd = 'ls %s' % (os.path.join(s_dir_lst[0], 'soft_dir'))  # 预期不能存在软连接
    rc, stdout = common.run_command(rep_common.SLAVE_RANDOM_NODE, cmd)
    common.judge_rc_unequal(rc, 0, 'can find soft_dir')
    cmd = 'ls %s' % (os.path.join(s_dir_lst[0], 'dir0'))  # 预期存在file_1文件
    rc, stdout = common.run_command(rep_common.SLAVE_RANDOM_NODE, cmd)
    common.judge_rc(rc, 0, 'cannot find dir0')

    log.info('4> [主]创建到主目录外对目录和文件的软连接，起pair任务')
    '''文件'''
    cmd = 'ln -s %s %s ' % (os.path.join(m_dir_lst[0], 'soft_file_out'), os.path.join(FILE_MASTER_PATH, 'file_1'))
    rc, stdout = common.run_command(rep_common.MASTER_RANDOM_NODE, cmd)
    common.judge_rc(rc, 0, cmd + 'failed')
    rc, pscli_info = rep_common.start_rep_task_scp(pair_id=pairid)
    common.judge_rc(rc, 0, 'start_rep_task_scp failed')
    cmd = 'ls %s' % (os.path.join(s_dir_lst[0], 'soft_file_out'))  # 预期不能存在软连接
    rc, stdout = common.run_command(rep_common.SLAVE_RANDOM_NODE, cmd)
    common.judge_rc_unequal(rc, 0, 'can find soft_file_out')

    '''目录'''
    cmd = 'ln -s %s %s ' % (os.path.join(m_dir_lst[0], 'soft_dir_out'), os.path.join(FILE_MASTER_PATH, 'dir0'))
    rc, stdout = common.run_command(rep_common.MASTER_RANDOM_NODE, cmd)
    common.judge_rc(rc, 0, cmd + 'failed')
    rc, pscli_info = rep_common.start_rep_task_scp(pair_id=pairid)
    common.judge_rc(rc, 0, 'start_rep_task_scp failed')
    cmd = 'ls %s' % (os.path.join(s_dir_lst[0], 'soft_dir_out'))  # 预期不能存在软连接
    rc, stdout = common.run_command(rep_common.SLAVE_RANDOM_NODE, cmd)
    common.judge_rc_unequal(rc, 0, 'can find soft_dir_out')

    log.info('5> [主]创建主目录内硬连接，起pair任务')
    cmd = 'ln %s %s ' % (os.path.join(m_dir_lst[0], 'hard_file'), os.path.join(m_dir_lst[0], 'file_2'))
    rc, stdout = common.run_command(rep_common.MASTER_RANDOM_NODE, cmd)
    common.judge_rc(rc, 0, cmd + 'failed')
    rc, pscli_info = rep_common.start_rep_task_scp(pair_id=pairid)
    common.judge_rc(rc, 0, 'start_rep_task_scp failed')
    cmd = 'ls %s' % (os.path.join(s_dir_lst[0], 'hard_file'))  # 预期不能存在软连接
    rc, stdout = common.run_command(rep_common.SLAVE_RANDOM_NODE, cmd)
    common.judge_rc_unequal(rc, 0, 'can find hard_file')
    cmd = 'ls %s' % (os.path.join(s_dir_lst[0], 'file_2'))  # 预期存在file_2文件
    rc, stdout = common.run_command(rep_common.SLAVE_RANDOM_NODE, cmd)
    common.judge_rc(rc, 0, 'cannot find file_2')


    log.info('6> [主]创建到主目录外的硬连接，起pair任务')
    '''文件'''
    cmd = 'ln -s %s %s ' % (os.path.join(m_dir_lst[0], 'hard_file_out'), os.path.join(FILE_MASTER_PATH, 'file_2'))
    rc, stdout = common.run_command(rep_common.MASTER_RANDOM_NODE, cmd)
    common.judge_rc(rc, 0, cmd + 'failed')
    rc, pscli_info = rep_common.start_rep_task_scp(pair_id=pairid)
    common.judge_rc(rc, 0, 'start_rep_task_scp failed')
    cmd = 'ls %s' % (os.path.join(s_dir_lst[0], 'hard_file_out'))  # 预期不能存在软连接
    rc, stdout = common.run_command(rep_common.SLAVE_RANDOM_NODE, cmd)
    common.judge_rc_unequal(rc, 0, 'can find hard_file_out')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

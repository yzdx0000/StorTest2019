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
#   目录类复制
# @steps:
#   1、[主从]创建复制域和通道
#   2、[主]创建一个pair
#   3、[主]主目录创建目录文件后起pair任务
#   4、[主]创建文件，起复制任务
#   5、[主]rename某文件，起复制任务,此文件全复制
#   6、[主]删除文件，起复制任务
#   7、[主]删除再创建同名文件，起复制任务
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

    log.info('3> [主]主目录创建目录文件后起pair任务')
    rc = rep_common.vdb_create(m_dir_lst[0], '/tmp', rep_common.MASTER_RANDOM_NODE)
    common.judge_rc(rc, 0, 'vdb_create failed ')
    rc, pscli_info = rep_common.start_rep_task_scp(pairid)
    common.judge_rc(rc, 0, 'start_rep_task failed')
    '''检验一致性'''
    rc = rep_common.check_data_consistency(s_dir_lst[0], '/tmp', [rep_common.MASTER_RANDOM_NODE],
                                           [rep_common.SLAVE_RANDOM_NODE])
    common.judge_rc(rc, 0, 'check_data_consistency failed')

    log.info('4> [主]创建文件，起复制任务')
    rc = rep_common.create_file(rep_common.MASTER_RANDOM_NODE, m_dir_lst[0], 'file', 3, 1)
    common.judge_rc(rc, 0, 'create_file failed')
    rc, md5_1 = rep_common.md5sum(rep_common.MASTER_RANDOM_NODE, os.path.join(m_dir_lst[0],"file_1"))
    common.judge_rc(rc, 0, 'md5sum failed')

    rc, pscli_info = rep_common.start_rep_task_scp(pairid)
    common.judge_rc(rc, 0, 'start_rep_task failed')

    '''检查'''
    rc, md5_2 = rep_common.md5sum(rep_common.SLAVE_RANDOM_NODE, os.path.join(s_dir_lst[0], "file_1"))
    common.judge_rc(rc, 0, 'md5sum failed')
    if md5_1 != md5_2:
        common.except_exit('md5check failed')

    rc, inode = rep_common.get_inode(rep_common.SLAVE_RANDOM_NODE, os.path.join(s_dir_lst[0], 'file_1'))
    common.judge_rc(rc, 0, 'get_inode failed')

    log.info('5> [主]rename某文件，起复制任务')
    cmd = 'mv %s %s' % (os.path.join(m_dir_lst[0], 'file_1'), os.path.join(m_dir_lst[0], 'file_1_new'))
    rc, stdout = common.run_command(rep_common.MASTER_RANDOM_NODE, cmd)
    common.judge_rc(rc, 0, 'cmd %s failed' % cmd)

    rc, pscli_info = rep_common.start_rep_task_scp(pairid)
    common.judge_rc(rc, 0, 'start_rep_task failed')

    '''检查'''
    cmd = 'ls %s' % os.path.join(s_dir_lst[0], 'file_1')
    rc, stdout = common.run_command(rep_common.SLAVE_RANDOM_NODE, cmd)
    common.judge_rc_unequal(rc, 0, 'find file_1')


    cmd = 'ls %s' % os.path.join(s_dir_lst[0], 'file_1_new')
    rc, stdout = common.run_command(rep_common.SLAVE_RANDOM_NODE, cmd)
    common.judge_rc(rc, 0, 'not find file_1_new')
    rc, inode_tmp = rep_common.get_inode(rep_common.SLAVE_RANDOM_NODE, os.path.join(s_dir_lst[0], 'file_1_new'))
    common.judge_rc(rc, 0, 'get_inode failed')
    common.judge_rc(inode_tmp, inode, 'inode not equal')

    log.info('6> [主]删除文件，起复制任务')
    rc, stdout = common.rm_exe(rep_common.MASTER_RANDOM_NODE, os.path.join(m_dir_lst[0], 'file_2'))
    common.judge_rc(rc, 0, 'rm_exe failed')

    rc, pscli_info = rep_common.start_rep_task_scp(pairid)
    common.judge_rc(rc, 0, 'start_rep_task failed')

    '''检查'''
    cmd = 'ls %s' % os.path.join(s_dir_lst[0], 'file_2')
    rc, stdout = common.run_command(rep_common.SLAVE_RANDOM_NODE, cmd)
    common.judge_rc_unequal(rc, 0, 'file still exist ,failed')

    log.info('7> [主]删除再创建同名文件，起复制任务')
    '''先创建同名文件，复制'''
    cmd = 'echo > aaa %s' % (os.path.join(s_dir_lst[0], 'file_2'))
    rc, stdout = common.run_command(rep_common.MASTER_RANDOM_NODE, cmd)
    common.judge_rc(rc, 0, cmd + 'failed')

    rc, md5 = rep_common.md5sum(rep_common.MASTER_RANDOM_NODE, os.path.join(s_dir_lst[0], 'file_2'))
    common.judge_rc(rc, 0, 'md5sum failed')

    rc, pscli_info = rep_common.start_rep_task_scp(pairid)
    common.judge_rc(rc, 0, 'start_rep_task failed')

    rc, md5_2 = rep_common.md5sum(rep_common.MASTER_RANDOM_NODE, os.path.join(s_dir_lst[0], 'file_2'))
    common.judge_rc(rc, 0, 'md5sum failed')
    common.judge_rc(md5. md5_2, 'md5 not equal')

    '''删除并创建同名文件，复制'''
    rc, stdout = common.rm_exe(rep_common.MASTER_RANDOM_NODE, os.path.join(m_dir_lst[0], 'file_3'))
    common.judge_rc(rc, 0, 'rm_exe failed')

    cmd = 'echo > bbb %s' % (os.path.join(s_dir_lst[0], 'file_3'))
    rc, stdout = common.run_command(rep_common.MASTER_RANDOM_NODE, cmd)
    common.judge_rc(rc, 0, cmd + 'failed')

    rc, md5 = rep_common.md5sum(rep_common.MASTER_RANDOM_NODE, os.path.join(s_dir_lst[0], 'file_3'))
    common.judge_rc(rc, 0, 'md5sum failed')

    rc, pscli_info = rep_common.start_rep_task_scp(pairid)
    common.judge_rc(rc, 0, 'start_rep_task failed')

    rc, md5_2 = rep_common.md5sum(rep_common.MASTER_RANDOM_NODE, os.path.join(s_dir_lst[0], 'file_3'))
    common.judge_rc(rc, 0, 'md5sum failed')
    common.judge_rc(md5, md5_2, 'md5 not equal')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

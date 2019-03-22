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
#   支持应用程序的远程复制，且功能可用
# @steps:
#   1、[主从]创建复制域和通道
#   2、[主]创建一个pair
#   3、[主]主目录创建可支持程序文件后起pair任务
#   4、[从]从端执行程序
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

    log.info('3> [主]主目录创建可执行文件后起pair任务')
    file_name1 = os.path.join(m_dir_lst[0], 'test_file.c')
    cmd = 'echo -e "#include<stdio.h>\nvoid main(){printf(\\"Hello world\\");}" > %s' % (file_name1)
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    common.judge_rc(rc, 0, cmd + ' failed')
    file_name2 = os.path.join(m_dir_lst[0], 'test_file.out')
    cmd = 'gcc %s -o %s' % (file_name1, file_name2)
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    common.judge_rc(rc, 0, cmd + 'failed')

    rc, pscli_info = rep_common.start_rep_task_scp(pairid)
    common.judge_rc(rc, 0, 'start_rep_task failed')
    '''检验一致性'''
    rc, stdout = common.run_command(rep_common.SLAVE_RANDOM_NODE, file_name2.replace(m_dir_lst[0], s_dir_lst[0]))
    common.judge_rc(stdout.strip(), 'Hello world', 'exe failed')


    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

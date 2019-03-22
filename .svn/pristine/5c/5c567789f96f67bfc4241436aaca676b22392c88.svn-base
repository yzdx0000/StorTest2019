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
#   手动起pair任务
# @steps:
#   1、[主从]创建复制域和通道
#   2、[主]创建pair
#   3、[主]手动起复制任务，参数id非法
#   4、[主]手动暂停复制任务，参数id非法
#   5、[主]手动恢复复制任务，参数id非法
#   6、[主]手动删除复制任务，参数id非法
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(slave)parastor/(slave)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]
THREADS_NUMBER = 10
CHAR_LEN = random.randint(0, 10)  # todo 找开发确认参数长度是多少



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

    log.info('3> [主]手动起复制任务')
    special_char = common.get_special_character(CHAR_LEN)
    rc, stdout = common.start_rep_task(id=special_char)
    common.judge_rc_unequal(rc, 0, 'start_rep_task successful')

    log.info('4> [主]手动暂停复制任务，参数id非法')
    rc, stdout = common.pause_rep_task(id=special_char)
    common.judge_rc_unequal(rc, 0, 'pause_rep_task successful')

    log.info('5> [主]手动恢复复制任务，参数id非法')
    rc, stdout = common.resume_rep_task(id=special_char)
    common.judge_rc_unequal(rc, 0, 'resume_rep_task successful')

    log.info('6> [主]手动删除复制任务，参数id非法')
    rc, stdout = common.delete_abnormal_rep_task(id=special_char)
    common.judge_rc_unequal(rc, 0, 'resume_rep_task successful')

    return



def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

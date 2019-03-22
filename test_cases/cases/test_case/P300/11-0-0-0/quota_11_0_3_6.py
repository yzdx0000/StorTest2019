#-*-coding:utf-8 -*
import os
import time
import random
import commands

import utils_path
import common
import quota_common
import log
import shell
import get_config
import prepare_clean
import sys
#################################################################
#
# Author: chenjy1
# Date: 2018-09-03
# @summary：
#    父目录软阈值1000，宽限时间60秒，三个子目录软阈值300，宽限时间60秒，3个子目录分别创建400文件，
#    过期后所有目录无法创建文件
# @steps:
#    1.创建目录FILENAME/nesting1_1  nesting1_2  nesting1_3
#    2.创建目录FILENAME配额,软阈值1000 宽限时间60秒 等待配额状态为work
#    3.创建子目录FILENAME/nesting1_x/配额,子目录软阈值300，宽限时间60秒 等待配额状态为work
#    4.3子目录创建400文件开始计时，过期后3目录无法创建文件
# @changelog：
#################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
SCRIPT_PATH = os.path.join(quota_common.QUOTA_PATH, FILE_NAME)           # /mnt/volume1/qouta_test_dir/quota_11_0_3_1


def case():
    log.info("case begin ")
    rc_lst = {}
    ob_node = common.Node()
    log.info("1.创建目录FILENAME/nesting1_1")
    quota_id_lst = []
    dir0 = SCRIPT_PATH
    dir1_ = []
    for i in range(3):
        dir1_.append(os.path.join(dir0, 'nesting1_%s') % (i+1))
        quota_common.creating_dir(quota_common.NOTE_IP_1, dir1_[i])

    create_quota_dir0 = os.path.join(get_config.get_one_volume_name() + ':', quota_common.QUOTA_PATH_BASENAME, os.path.basename(dir0))
    log.info(create_quota_dir0)

    create_quota_dir1_ = []
    for i in range(3):
        create_quota_dir1_.append(os.path.join(create_quota_dir0, os.path.basename(dir1_[i])))

    log.info("2> 创建父目录配额,软阈值1000 宽限时间60秒 等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir0,
                                                   filenr_soft_threshold=1000, filenr_grace_time=60,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("3> 创建子目录FILENAME/nesting1_x配额,子目录软阈值300，宽限时间60秒 等待配额状态为work")
    for i in range(3):
        rc, pscli_info = quota_common.create_one_quota(create_quota_dir1_[i],
                                                       filenr_soft_threshold=300, filenr_grace_time=60,
                                                       filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
        common.judge_rc(rc, 0, "create  quota failed")
        rc, quota_id = quota_common.get_one_quota_id(create_quota_dir1_[i], quota_common.TYPE_CATALOG)
        common.judge_rc(rc, 0, "get_one_quota_id failed")
        quota_id_lst.append(quota_id)
        rc = quota_common.wait_quota_work(quota_id)
        common.judge_rc(rc, 0, "get quota info failed")

    rc = quota_common.chkmult_client_one_dir_on_path(dir0)
    common.judge_rc(rc, 0, "chkmult_client_all_dir_on_path failed")
    log.info("4> 3子目录创建400文件开始计时，过期后3目录无法创建文件")
    for i in range(3):
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir1_[i], 400, 1, 'a', quota_id=quota_id_lst[i+1])

    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir1_[0])
    if dir_inode != 400:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_[0], dir_inode)
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_2, dir1_[1])
    if dir_inode != 400:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_[1], dir_inode)
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_3, dir1_[2])
    if dir_inode != 400:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_[2], dir_inode)

    rc, qmgrid = quota_common.get_qmgr_id(quota_id_lst[0])
    common.judge_rc(rc, 0, "get_qmgr_id failed")
    qmgr_ip = ob_node.get_node_ip_by_id(qmgrid)
    '''等待超过超期时间'''
    log.info('wait 75s')
    time.sleep(75)

    for i in range(4):
        quota_common.wait_soft_threshold_over_time(qmgr_ip, quota_id_lst[i], quota_common.SOFT_TIME_FILENR)

    quota_common.creating_files(quota_common.CLIENT_IP_2, dir1_[0], 1, 1, 'b', quota_id=quota_id_lst[1])
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir1_[0])
    if dir_inode != 400:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_[0], dir_inode)
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_2, dir1_[1])
    if dir_inode != 400:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_[1], dir_inode)
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_3, dir1_[2])
    if dir_inode != 400:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_[2], dir_inode)
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir0)
    if dir_inode != 1203:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir0, dir_inode)

    """判断rc_lst"""
    if rc_lst != {}:
        log.info(rc_lst)
        for i in rc_lst:
            log.info("check point in line : %s is about :%s " % (i, rc_lst[i]))
        log.info('If there are many lines, you may only need to look at the first line.')
        common.except_exit("some check point failed")

    return


def main():
    prepare_clean.quota_test_prepare(FILE_NAME)
    case()
    prepare_clean.quota_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return

if __name__ == '__main__':
    common.case_main(main)

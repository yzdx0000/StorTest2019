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
#    对父目录a创建硬阈值配额1G，创建子目录b硬阈值为1G，在父目录下创建文件，
#    创建1G多 再创建失败，在子目录创建文件失败，删除父目录配额，在子目录创建文件成功
# @steps:
#    1.创建目录FILENAME/nesting1_1
#    2.创建目录FILENAME配额,硬阈值1G 等待配额状态为work
#    3.创建子目录FILENAME/nesting1_1配额,硬阈值1G,等待配额状态为work
#    4.父目录创建1G多文件，预期total_size=1G
#    5.子目录创建文件，预期失败
#    6.父目录删除配额，子目录创建文件成功，创建1G多，预期1G
# @changelog：
#################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
SCRIPT_PATH = os.path.join(quota_common.QUOTA_PATH, FILE_NAME)           # /mnt/volume1/qouta_test_dir/quota_11_0_3_1
LARGE_BS = random.choice([True, False])   # True大文件，False:小文件


def case():
    log.info("case begin ")
    rc_lst = {}
    log.info("1.创建目录FILENAME/nesting1_1")
    quota_id_lst = []
    dir0 = SCRIPT_PATH
    dir1_1 = os.path.join(dir0, 'nesting1_1')
    quota_common.creating_dir(quota_common.NOTE_IP_1, dir1_1)

    create_quota_dir0 = os.path.join(get_config.get_one_volume_name() + ':', quota_common.QUOTA_PATH_BASENAME, os.path.basename(dir0))
    log.info(create_quota_dir0)
    create_quota_dir1_1 = os.path.join(create_quota_dir0, os.path.basename(dir1_1))

    log.info("2> 创建父目录配额,硬阈值1G  等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir0,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_1G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("3> 创建子目录FILENAME/nesting1_1配额,硬阈值1G,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir1_1,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_1G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir1_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed") 

    log.info("4> 父目录创建1G多文件，预期total_size=1G")
    if LARGE_BS:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir0, 1, 1500, 'a', quota_id=quota_id_lst[0])
    else:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir0, 1500, 1, 'a', quota_id=quota_id_lst[0])
    dir0_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, dir0)
    if dir0_size != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir0, dir0_size)

    log.info("5> 子目录创建文件，预期失败")
    quota_common.creating_files(quota_common.CLIENT_IP_2, dir1_1, 1, 1, 'b', quota_id=quota_id_lst[1])
    dir1_1_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_2, dir1_1)
    if dir1_1_size != 0:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_1, dir1_1_size)

    log.info("6.父目录删除配额，子目录创建文件成功，创建1G多，预期1G")
    rc, pscli_info = quota_common.delete_one_quota(quota_id_lst[0])
    if rc != 0:
        quota_common.get_one_quota_info(quota_id_lst[0])
    common.judge_rc(rc, 0, "delete_one_quota failed, quota_id : %s " % quota_id_lst[0])
    if LARGE_BS:
        quota_common.creating_files(quota_common.CLIENT_IP_3, dir1_1, 1, 1500, 'c')
    else:
        quota_common.creating_files(quota_common.CLIENT_IP_3, dir1_1, 1500, 1, 'c')
    dir1_1_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_3, dir1_1)
    if dir1_1_size != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (dir1_1, dir1_1_size)

    """判断rc_lst"""
    if rc_lst != {}:
        log.info(rc_lst)
        for i in rc_lst:
            log.info("check point in line : %s is about :%s " % (i, rc_lst[i]))
        log.info('If there are many lines, you may only need to look at the first line.')
        common.except_exit("some check point failed")


def main():
    prepare_clean.quota_test_prepare(FILE_NAME)
    case()
    prepare_clean.quota_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return

if __name__ == '__main__':
    common.case_main(main)

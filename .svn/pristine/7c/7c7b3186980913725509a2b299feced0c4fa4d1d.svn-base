#-*-coding:utf-8 -*
import os
import time
import random
import commands

import utils_path
import common
import quota_common
import log
import get_config
import prepare_clean
import sys
#################################################################
# Author: liyi
# Date: 2018-11-1
# @summary：
#   测试inode硬阈值配额在升级前后是否生效
#   升级前后配额操作：
#           升级前：volume_11: 硬阈值1000,先写1000；升级后：写数据，查看规则是否生效
#           升级前：volume_12：硬阈值100，先写50个文件；升级后：继续写，查看规则是否生效
#           升级前：volume_13：硬阈值1000，写1000；升级后：修改根配额为2g，看是否可以继续写入
# @notice:
#   本脚本执行前提：需要先用quota_11_0_3_66.py创建好N个卷
#   本脚本需要与quota_upgrade_after_4.py配合使用
# @steps:
#    1.volume_11创建配额,硬阈值1000,等待配额状态为work
#    2.volume_12创建50个文件，预期total_inode=50
#    3.volume_13创建1100个文件，预期total_inode=1000
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
ip_list = get_config.get_allclient_ip()
mnt_path = get_config.get_mount_paths()  # /mnt/volume
LARGE_BS = random.choice([True, False])  # True大文件，False:小文件


def case():
    """
    author:liyi
    date:2018-11-1
    description: 升级前操作
    :return:
    """
    log.info("case begin ")
    rc_lst = {}
    obj_storage = common.Storagepool()
    rc, storage_pool_id = obj_storage.get_storagepool_id(storage_pool_name="stor")
    common.judge_rc(rc, 0, "get_storage_pool_id faild!")

    mnt_path_11 = get_config.get_mount_paths()[0] + "_11" #/mnt/volume_11
    mnt_path_12 = get_config.get_mount_paths()[0] + "_12" #/mnt/volume_12
    mnt_path_13 = get_config.get_mount_paths()[0] + "_13" #/mnt/volume_13

    create_quota_dir_11 = quota_common.VOLUME_NAME + "_11" + ":/"
    create_quota_dir_12 = quota_common.VOLUME_NAME + "_12" + ":/"
    create_quota_dir_13 = quota_common.VOLUME_NAME + "_13" + ":/"

    log.info("1.1> volume_11创建配额,硬阈值1000,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir_11,
                                                   filenr_hard_threshold=1000,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_11, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("1.2> volume_11创建1100个文件，预期total_inode=1000")
    quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_11, 1100, 1, 'before')
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, mnt_path_11)
    if dir_inode != 1000:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_11, dir_inode)

    log.info("2.1> volume_12创建配额,硬阈值100,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir_12,
                                                   filenr_hard_threshold=100,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_12, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("2.2> volume_12创建50个文件，预期total_inode=50")
    quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_12, 50, 1, 'before')
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, mnt_path_12)
    if dir_inode != 50:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_12, dir_inode)

    log.info("3.1> volume_13创建配额,硬阈值1000,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir_13,
                                                   filenr_hard_threshold=1000,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_13, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("3.2> volume_13创建1100个文件，预期total_inode=1000")
    quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_13, 1100, 1, 'before')
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, mnt_path_13)
    if dir_inode != 1000:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_13, dir_inode)

    """判断rc_lst"""
    if rc_lst != {}:
        log.info(rc_lst)
        for i in rc_lst:
            log.info("check point in line : %s is about :%s " % (i, rc_lst[i]))
        log.info('If there are many lines, you may only need to look at the first line.')
        common.except_exit("some check point failed")


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
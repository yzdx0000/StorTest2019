#-*-coding:utf-8 -*
import os
import time
import random
import commands

import utils_path
import common
import quota_common
import nas_common
import log
import get_config
import prepare_clean
import sys
#################################################################
# Author: liyi
# Date: 2018-11-1
# @summary：
#   用户：测试inode硬阈值配额在升级前后是否生效
#   升级前后配额操作：
#           升级前：volume_24: 硬阈值1000,先写1000；升级后：写数据，查看规则是否生效
#           升级前：volume_25：硬阈值100，先写50个文件；升级后：继续写，查看规则是否生效
#           升级前：volume_26：硬阈值1000，写1000；升级后：修改根配额为2g，看是否可以继续写入
# @notice:
#   本脚本执行前提：需要先用quota_11_0_3_66.py创建好N个卷
#   本脚本需要与quota_upgrade_after_8.py配合使用
# @steps:
#    1.volume_24创建配额,硬阈值1000,等待配额状态为work
#    2.volume_25创建50个文件，预期total_inode=50
#    3.volume_26创建1100个文件，预期total_inode=1000
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

    mnt_path_24 = get_config.get_mount_paths()[0] + "_24"  # /mnt/volume_24
    mnt_path_25 = get_config.get_mount_paths()[0] + "_25"  # /mnt/volume_25
    mnt_path_26 = get_config.get_mount_paths()[0] + "_26"  # /mnt/volume_26
    create_quota_dir_24 = quota_common.VOLUME_NAME + "_24" + ":/"
    create_quota_dir_25 = quota_common.VOLUME_NAME + "_25" + ":/"
    create_quota_dir_26 = quota_common.VOLUME_NAME + "_26" + ":/"

    auth_providers_id_list = nas_common.get_auth_providers_id_list()
    auth_provider_id = auth_providers_id_list.split(',')[0]
    for i in range(24, 27):
        cmd = "chmod 777 /mnt/volume_%s" % i
        rc, stdout = common.run_command(quota_common.NOTE_IP_1,cmd)
        common.judge_rc(rc, 0, "chmod failed!!")

    log.info("1> volume_24创建配额,硬阈值1000,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir_24,
                                                   auth_provider_id=auth_provider_id, user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   filenr_hard_threshold=1000,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_24, quota_common.TYPE_USER, u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("1.1> volume_24创建1100个文件，预期total_inode=1000")
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_2, mnt_path_24, 1100, 1, 'before',  quota_common.QUOTA_USER)
    dir_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_2, mnt_path_24, quota_common.QUOTA_USER)
    if dir_inode != 1000:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_24, dir_inode)

    log.info("2> volume_25创建配额,硬阈值100,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir_25,
                                                   auth_provider_id=auth_provider_id, user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   filenr_hard_threshold=100,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id( create_quota_dir_25, quota_common.TYPE_USER, u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("2.1> volume_25创建50个文件，预期total_inode=50")
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, mnt_path_25, 50, 1, 'before',  quota_common.QUOTA_USER)
    dir_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, mnt_path_25, quota_common.QUOTA_USER)
    if dir_inode != 50:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_25, dir_inode)

    log.info("3> volume_26创建配额,硬阈值1000,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir_26,
                                                   auth_provider_id=auth_provider_id, user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   filenr_hard_threshold=1000,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_26, quota_common.TYPE_USER, u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work( quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("3.1> volume_26创建1100个文件，预期total_inode=1000")
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_2, mnt_path_26, 1100, 1, 'before',  quota_common.QUOTA_USER)
    dir_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_2, mnt_path_26, quota_common.QUOTA_USER)
    if dir_inode != 1000:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_26, dir_inode)

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
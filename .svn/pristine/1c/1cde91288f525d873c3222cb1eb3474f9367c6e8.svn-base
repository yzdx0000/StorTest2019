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
#   用户：测试inode软配额在升级前后是否生效
#   升级前后配额操作：
#           升级前：volume_27: 软阈值1000,先写1100，触发软；升级后：写数据，查看规则是否生效
#           升级前：volume_28：软阈值1000，先写500个文件；升级后：继续写，查看规则是否生效
# @notice:
#   本脚本执行前提：需要先用quota_14_0_3_66.py创建好N个卷
#   本脚本需要与quota_upgrade_after_9.py配合使用
# @steps:
#    1.volume_27创建配额,硬阈值1000,等待配额状态为work
#    2.volume_28创建配额,硬阈值1000,等待配额状态为work
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
    auth_providers_id_list = nas_common.get_auth_providers_id_list()
    auth_provider_id = auth_providers_id_list.split(',')[0]

    mnt_path_27 = get_config.get_mount_paths()[0] + "_27"  # /mnt/volume_27
    mnt_path_28 = get_config.get_mount_paths()[0] + "_28"  # /mnt/volume_28
    create_quota_dir_27 = quota_common.VOLUME_NAME + "_27" + ":/"
    create_quota_dir_28 = quota_common.VOLUME_NAME + "_28" + ":/"

    for i in range(27, 29):
        cmd = "chmod 777 /mnt/volume_%s" % i
        rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
        common.judge_rc(rc, 0, "chmod failed!!")

    log.info("1> volume_27软阈值1000，宽限时间60s,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir_27,
                                                   auth_provider_id=auth_provider_id,
                                                   user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   filenr_soft_threshold=1000, filenr_grace_time=60,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_27, quota_common.TYPE_USER, u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("1.1> volume_27创建1100个文件，触发软阈值")
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, mnt_path_27, 1100, 1, 'before', quota_common.QUOTA_USER)
    dir_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, mnt_path_27, quota_common.QUOTA_USER)
    if dir_inode != 1100:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_27, dir_inode)

    log.info("2> volume_28软阈值1000，宽限时间60s,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir_28,
                                                   auth_provider_id=auth_provider_id,
                                                   user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   filenr_soft_threshold=1000,
                                                   filenr_grace_time=60,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_28, quota_common.TYPE_USER, u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("2.1> volume_28 创建500个文件，预期total_inode=500")
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, mnt_path_28, 500, 1, 'before', quota_common.QUOTA_USER)
    dir_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, mnt_path_28,quota_common.QUOTA_USER)
    if dir_inode != 500:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_28, dir_inode)

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
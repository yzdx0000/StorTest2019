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
#   用户：测试逻辑硬阈值配额在升级前后是否生效
#   升级前后配额操作：
#           升级前：卷17 容量：2g  根配额1g；升级后：写数据，查看规则是否生效
#           升级前：卷18 容量：2g  根配额4g，写2g多，预计2g；升级后：继续写，查看规则是否生效
#           升级前：卷19 容量：2g  根配额1g，写1g多，预计1g；升级后：修改根配额为2g，看是否可以继续写入
#           升级前：卷20 容量：2g  根配额truncate2g；升级后：删除文件，继续truncate1g，规则是否生效
# @notice:
#   本脚本执行前提：需要先用quota_11_0_3_66.py创建好N个卷
#   本脚本需要与quota_upgrade_after_6.py配合使用
# @steps:
#    1.volume_17创建配额,硬阈值1G,等待配额状态为work
#    2.volume_18创建配额,硬阈值4G,并在其下写入2G多文件
#    3.volume_19创建配额,硬阈值1G,并在其下写入1G多文件，预计1G
#    4.volume_20创建配额,硬阈值1G,并在其下写入1G多文件，预计1G
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

    rc_lst = {}
    obj_storage = common.Storagepool()
    rc, storage_pool_id = obj_storage.get_storagepool_id(storage_pool_name="stor")
    common.judge_rc(rc, 0, "get_storage_pool_id faild!")
    obj_volume = common.Volume()

    mnt_path_18 = get_config.get_mount_paths()[0] + "_18"  # /mnt/volume_18
    mnt_path_19 = get_config.get_mount_paths()[0] + "_19"  # /mnt/volume_19
    mnt_path_20 = get_config.get_mount_paths()[0] + "_20"  # /mnt/volume_20

    create_quota_dir_17 = quota_common.VOLUME_NAME + "_17" + ":/"
    create_quota_dir_18 = quota_common.VOLUME_NAME + "_18" + ":/"
    create_quota_dir_19 = quota_common.VOLUME_NAME + "_19" + ":/"
    create_quota_dir_20 = quota_common.VOLUME_NAME + "_20" + ":/"

    volume_name_18 = quota_common.VOLUME_NAME + "_18"
    volume_id_18 = obj_volume.get_volume_id(volume_name_18)
    auth_providers_id_list = nas_common.get_auth_providers_id_list()
    auth_provider_id = auth_providers_id_list.split(',')[0]

    for i in range(17, 21):
        cmd = "chmod 777 /mnt/volume_%s" % i
        rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
        common.judge_rc(rc, 0, "chmod failed!!")

    log.info("1> volume_17创建配额,硬阈值1G,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir_17,
                                                   auth_provider_id=auth_provider_id,
                                                   user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_1G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_17,
                                                 u_or_g_type=quota_common.TYPE_USER,
                                                 u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("2> volume_18创建配额,硬阈值4G,并在其下写入2G多文件")
    log.info("2.1> volume_18创建配额,硬阈值4G,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir_18,
                                                   auth_provider_id=auth_provider_id,
                                                   user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_4G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_18,
                                                 u_or_g_type=quota_common.TYPE_USER,
                                                 u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("2.2> volume_18下面写2G多文件，预期total_size 2G")
    if LARGE_BS:
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, mnt_path_18, 1, 1100,
                                                                'before_a', quota_common.QUOTA_USER)
        log.info("切客户端写前，对volume_18进行chkmult检测")
        quota_common.chkmult_client_volume(volume_id_18)
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_2, mnt_path_18, 1100, 1,
                                                                'before_b', quota_common.QUOTA_USER)
    else:
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, mnt_path_18, 275, 4,
                                                                'before_a', quota_common.QUOTA_USER)
        log.info("切客户端写前，对volume_18进行chkmult检测")
        quota_common.chkmult_client_volume(volume_id_18)
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, mnt_path_18, 1100, 1,
                                                                'before_b', quota_common.QUOTA_USER)
    dir_size = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, mnt_path_18, quota_common.QUOTA_USER)

    if dir_size != quota_common.FILE_SIZE_2G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (mnt_path_18, dir_size)

    log.info("3> volume_19创建配额,硬阈值1G,并在其下写入1G多文件，预计1G")
    log.info("3.1> volume_19创建配额,硬阈值1G,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir_19,
                                                   auth_provider_id=auth_provider_id,
                                                   user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_1G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_19,
                                                 u_or_g_type=quota_common.TYPE_USER,
                                                 u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("3.2> volume_19下面写1G文件")
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, mnt_path_19, 1100, 1,
                                                                'before_a',quota_common.QUOTA_USER)
    dir_size = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, mnt_path_19,quota_common.QUOTA_USER)
    if dir_size != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (mnt_path_19, dir_size)

    log.info("4> volume_20创建配额,硬阈值1G,并在其下写入1G多文件，预计1G")
    log.info("4.1> volume_20创建配额,硬阈值1G,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir_20,
                                                   auth_provider_id=auth_provider_id,
                                                   user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_1G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_20, quota_common.TYPE_USER,
                                                 u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("4.2> volume_20 truncate到1G；再写入失败")
    cmd = ("cd %s; su quota_user -c \"truncate -s 1G file_1\";") % mnt_path_20
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    common.judge_rc(rc, 0, "truncate failed!")
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, mnt_path_19, 1, 1,
                                                            'before_a', quota_common.QUOTA_USER)
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, mnt_path_20)
    if dir_size != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_20, dir_size)

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
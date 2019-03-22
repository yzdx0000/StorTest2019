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
# Date: 2018-10-31
# @summary：
#   测试逻辑硬阈值配额在升级前后是否生效
#   升级前后配额操作：
#           升级前：卷4 容量：2g  根配额1g；升级后：写数据，查看规则是否生效
#           升级前：卷5 容量：2g  根配额4g，写2g多，预计2g；升级后：继续写，查看规则是否生效
#           升级前：卷6 容量：2g  根配额1g，写1g多，预计1g；升级后：修改根配额为2g，看是否可以继续写入
#           升级前：卷7 容量：2g  根配额truncate2g；升级后：升级后：删除文件，继续truncate1g，规则是否生效
# @notice:
#   本脚本执行前提：需要先用quota_11_0_3_66.py创建好N个卷
#   本脚本需要与quota_upgrade_after_2.py配合使用
# @steps:
#    1.volume_4创建配额,硬阈值1G,等待配额状态为work
#    2.volume_5创建配额,硬阈值4G,并在其下写入2G多文件
#    3.volume_6创建配额,硬阈值1G,并在其下写入1G多文件，预计1G
#    4.volume_7创建配额,硬阈值1G,并在其下写入1G多文件，预计1G
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
ip_list = get_config.get_allclient_ip()
mnt_path = get_config.get_mount_paths()  # /mnt/volume
LARGE_BS = random.choice([True, False])  # True大文件，False:小文件


def case():
    """
    author:liyi
    date:2018-10-31
    description: 升级前操作
    :return:
    """
    log.info("case begin ")
    rc_lst = {}
    obj_storage = common.Storagepool()
    rc, storage_pool_id = obj_storage.get_storagepool_id(storage_pool_name="stor")
    common.judge_rc(rc, 0, "get_storage_pool_id faild!")
    obj_volume = common.Volume()

    mnt_path_5 = get_config.get_mount_paths()[0] + "_5" #/mnt/volume_5
    mnt_path_6 = get_config.get_mount_paths()[0] + "_6" #/mnt/volume_6
    mnt_path_7 = get_config.get_mount_paths()[0] + "_7" #/mnt/volume_7

    create_quota_dir_4 = quota_common.VOLUME_NAME + "_4" + ":/"
    create_quota_dir_5 = quota_common.VOLUME_NAME + "_5" + ":/"
    create_quota_dir_6 = quota_common.VOLUME_NAME + "_6" + ":/"
    create_quota_dir_7 = quota_common.VOLUME_NAME + "_7" + ":/"

    volume_name_5 = quota_common.VOLUME_NAME + "_5"
    volume_name_6 = quota_common.VOLUME_NAME + "_6"
    volume_id_5 = obj_volume.get_volume_id(volume_name_5)
    volume_id_6 = obj_volume.get_volume_id(volume_name_6)

    log.info("1> volume_4创建配额,硬阈值1G,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(path=create_quota_dir_4,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_1G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_4, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("2> volume_5创建配额,硬阈值4G,并在其下写入2G多文件")
    log.info("2.1> volume_5创建配额,硬阈值4G,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir_5,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_4G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_5, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("2.2> volume_5下面写2G文件")
    if LARGE_BS:
        log.info("多客户端写入2g多数据，写入前对卷chkmulti")
        quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_5, 1, 2048, 'before_a')
        quota_common.chkmult_client_volume(volume_id_5)
        quota_common.creating_files(quota_common.CLIENT_IP_2, mnt_path_5, 1, 1, 'before_b')
    else:
        log.info("单客户端写入2g多数据")
        quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_5, 2050, 1, 'before')
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, mnt_path_5)
    if dir_size != quota_common.FILE_SIZE_2G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_5, dir_size)

    log.info("3> volume_6创建配额,硬阈值1G,并在其下写入1G多文件，预计1G")
    log.info("3.1> volume_6创建配额,硬阈值1G,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir_6,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_1G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_6, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("3.2> volume_6下面写1G文件")
    if LARGE_BS:
        log.info("多客户端写入1g多数据")
        quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_6, 1, 1024, 'before_a')
        log.info("对volume_6进行chkmulti检测")
        quota_common.chkmult_client_volume(volume_id_6)
        quota_common.creating_files(quota_common.CLIENT_IP_2, mnt_path_6, 1, 1, 'before_b')
    else:
        log.info("单客户端写入1g多数据")
        quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_6, 1100, 1, 'before')
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, mnt_path_6)
    if dir_size != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_6, dir_size)

    log.info("4> volume_7创建配额,硬阈值1G,并在其下写入1G多文件，预计1G")
    log.info("4.1> volume_7创建配额,硬阈值1G,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir_7,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_1G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_7, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("4.2> volume_7 truncate到1G；再写入失败")
    cmd = ("cd %s; truncate -s 1G file_1") % mnt_path_7
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    common.judge_rc(rc, 0, "truncate failed!")
    quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_7, 1, 1, 'before')
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, mnt_path_7)
    if dir_size != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_7, dir_size)

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
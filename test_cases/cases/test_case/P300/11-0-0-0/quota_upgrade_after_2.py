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
# Date: 2018-11-5
# @summary：
#   测试逻辑硬阈值配额在升级前后是否生效
#   升级前后配额操作：
#           升级前：卷4 容量：2g  根配额1g；升级后：写数据，查看规则是否生效
#           升级前：卷5 容量：2g  根配额4g，写2g多，预计2g；升级后：继续写，查看规则是否生效
#           升级前：卷6 容量：2g  根配额1g，写1g多，预计1g；升级后：修改根配额为2g，看是否可以继续写入
#           升级前：卷7 容量：2g  根配额1g，truncate1g；升级后：删除文件，继续truncate1g，规则是否生效
# @notice:
#   本脚本执行前提：需要先用quota_11_0_3_66.py创建好N个卷
#   本脚本需要与quota_upgrade_after_2.py配合使用
# @steps:
#    1.volume_4 升级后：volume_4下面写1G多文件
#    2.volume_5 升级后：继续写，预计写入失败
#    3.volume_6 升级后：修改根配额为2g，看是否可以继续写入
#    4.volume_7 升级后：删除文件，继续truncate1g，规则是否生效
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
ip_list = get_config.get_allclient_ip()
mnt_path = get_config.get_mount_paths()  # /mnt/volume
LARGE_BS = random.choice([True, False])  # True大文件，False:小文件


def case():
    """
    author:liyi
    date:2018-11-5
    description:升级后操作
    :return:
    """
    obj_storage = common.Storagepool()
    rc, storage_pool_id = obj_storage.get_storagepool_id(storage_pool_name="stor")
    common.judge_rc(rc, 0, "get_storage_pool_id faild!")

    mnt_path_4 = get_config.get_mount_paths()[0] + "_4" #/mnt/volume_4
    mnt_path_5 = get_config.get_mount_paths()[0] + "_5" #/mnt/volume_5
    mnt_path_6 = get_config.get_mount_paths()[0] + "_6" #/mnt/volume_6
    mnt_path_7 = get_config.get_mount_paths()[0] + "_7" #/mnt/volume_7
    create_quota_dir_6 = quota_common.VOLUME_NAME + "_6" + ":/"

    log.info("case begin ")
    rc_lst = {}
    log.info("1> 升级前：卷4容量：2g 根配额1g；升级后：volume_4下面写1G多文件")
    if LARGE_BS:
        log.info("多客户端写入1g多数据")
        quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_4, 1, 1024, 'after_a')
        quota_common.creating_files(quota_common.CLIENT_IP_2, mnt_path_4, 1, 1, 'after_b')
    else:
        log.info("单客户端写入2g多数据")
        quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_4, 1100, 1, 'after')
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, mnt_path_4)
    if dir_size != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_4, dir_size)

    log.info("2> 升级前：卷5 容量：2g 根配额4g，写2g多，预计2g；升级后：继续写，预计写入失败")
    log.info("2.1> volume_5下面写文件，预计写入失败")
    quota_common.creating_files(quota_common.CLIENT_IP_2, mnt_path_5, 10, 1, 'after_a')
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, mnt_path_5)
    if dir_size != quota_common.FILE_SIZE_2G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_5, dir_size)

    log.info("3> 升级前：卷6 容量：2g根配额1g，写1g多，预计1g；升级后：修改根配额为2g，看是否可以继续写入")
    log.info("3.1> volume_6修改根配额为2g，等待配额状态为work")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_6, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc, pscli_info = quota_common.update_one_quota(quota_id,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_2G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "update quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_6, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("3.2> volume_6下面继续写入文件，预计共2G")
    if LARGE_BS:
        log.info("多客户端写入1g多数据")
        quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_6, 1, 1024, 'after_a')
        quota_common.creating_files(quota_common.CLIENT_IP_2, mnt_path_6, 1, 1, 'after_b')
    else:
        log.info("单客户端写入1g多数据")
        quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_6, 1100, 1, 'after')
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, mnt_path_6)
    if dir_size != quota_common.FILE_SIZE_2G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_6, dir_size)

    log.info("4> 升级前：卷7容量：2g 根配额truncate2g；升级后：删除文件，继续truncate1g，规则是否生效")
    log.info("4.1> 删除文件")
    rm_path = os.path.join(mnt_path_7, "file*")
    rc, stdout = common.rm_exe(quota_common.NOTE_IP_1, rm_path)
    common.judge_rc(rc, 0, "rm failed!")

    log.info("4.2> volume_7 truncate到1G，再写入失败")
    cmd = ("cd %s; truncate -s 1G file_1") % mnt_path_7
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    common.judge_rc(rc, 0, "truncate failed!")
    quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_7, 1, 1, 'after')
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
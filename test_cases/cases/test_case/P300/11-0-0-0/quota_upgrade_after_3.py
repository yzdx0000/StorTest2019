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
#   测试逻辑软阈值配额在升级前后是否生效
#   升级前后配额操作：
#           升级前：卷8  容量：2g  根配额1g, 宽限时间60s;升级后：写1g触发软阈值；过60后，看是否可以继续写入
#           升级前：卷9  容量：2g  根配额1g，宽限时间60s;写1100M；升级后：删除文件到小于1g，测试规则是否生效
#           升级前：卷10 容量：2g  根配额1g，宽限时间60s;写2g多，预计2g；升级后：删除文件，检测规则是否还有效
# @notice:
#   本脚本执行前提：需要先用quota_11_0_3_66.py创建好N个卷
#   本脚本需要与quota_upgrade_after_3.py配合使用
# @steps:
#    升级前步骤：
#       1.volume_8创建配额,软阈值1G,等待配额状态为work
#       2.volume_9下面写1100文件,触发软配额
#       3.volume_10下面写2G多文件,触发软配额
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
    description: 升级后操作
    :return:
    """
    log.info("case begin ")
    rc_lst = {}
    obj_storage = common.Storagepool()
    rc, storage_pool_id = obj_storage.get_storagepool_id(storage_pool_name="stor")
    common.judge_rc(rc, 0, "get_storage_pool_id faild!")
    obj_volume = common.Volume()

    mnt_path_8 = get_config.get_mount_paths()[0] + "_8" #/mnt/volume_8
    mnt_path_9 = get_config.get_mount_paths()[0] + "_9" #/mnt/volume_9
    mnt_path_10 = get_config.get_mount_paths()[0] + "_10" #/mnt/volume_10

    create_quota_dir_8 = quota_common.VOLUME_NAME + "_8" + ":/"
    create_quota_dir_9 = quota_common.VOLUME_NAME + "_9" + ":/"
    volume_name_10 = quota_common.VOLUME_NAME + "_10"
    volume_id_10 = obj_volume.get_volume_id(volume_name_10)
    ob_node = common.Node()

    log.info("1> 升级前：volume_8软阈值1G,宽限60s;升级后：写1g触发软阈值；过60后，看是否可以继续写入")
    if LARGE_BS:
        quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_8, 1, 1100, 'after_a')
    else:
        quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_8, 1100, 1, 'after_a')
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, mnt_path_8)
    if dir_size != quota_common.FILE_SIZE_1M * 1100:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_8, dir_size)

    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_8, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc, qmgrid = quota_common.get_qmgr_id(quota_id)
    common.judge_rc(rc, 0, "get_qmgr_id failed")
    qmgr_ip = ob_node.get_node_ip_by_id(qmgrid)

    log.info("延时70s，无法再继续写入数据")
    time.sleep(70)
    quota_common.wait_soft_threshold_over_time(qmgr_ip, quota_id, quota_common.SOFT_TIME_FILENR)
    quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_8, 10, 1, 'after_again')
    if dir_size != quota_common.FILE_SIZE_1M * 1100:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_8, dir_size)

    log.info("2> 升级前：volume_9软阈值1G（60s）下面有1100文件；升级后：删除操作后配额规则是否生效")
    log.info("2.1> 删除volume_9下所有文件")
    rm_dir = os.path.join(mnt_path_9, "*")
    rc, stdout = common.rm_exe(quota_common.NOTE_IP_1,rm_dir)
    common.judge_rc(rc, 0, "rm failed!!")

    log.info("2.2> volume_9写1100M文件，触发软阈值")
    if LARGE_BS:
        quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_9, 1, 1100, 'after_a')
    else:
        quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_9, 1100, 1, 'after_a')
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, mnt_path_9)
    if dir_size != quota_common.FILE_SIZE_1M*1100:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_9, dir_size)
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_9, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc, qmgrid = quota_common.get_qmgr_id(quota_id)
    common.judge_rc(rc, 0, "get_qmgr_id failed")
    qmgr_ip = ob_node.get_node_ip_by_id(qmgrid)

    log.info("2.3>延时70s，无法再继续写入数据，预计volume_9文件大小：1100M")
    time.sleep(70)
    quota_common.wait_soft_threshold_over_time(qmgr_ip, quota_id, quota_common.SOFT_TIME_FILENR)
    quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_9, 10, 1, 'after_again')
    if dir_size != quota_common.FILE_SIZE_1M * 1100:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_9, dir_size)

    log.info("3> volume_10软阈值1G(已有2G),删除后，继续写2G，是否会超")
    log.info("3.1> volume_10删除所有文件")
    rm_dir = os.path.join(mnt_path_10, "*")
    rc, stdout = common.rm_exe(quota_common.NOTE_IP_1,rm_dir)
    common.judge_rc(rc, 0, "rm failed!!")

    log.info("3.2> volume_10下面写2G多文件，预计2G")
    if LARGE_BS:
        quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_10, 1, 1100, 'after_a')
        log.info("切客户端写前，对volume_10进行chkmult检测")
        quota_common.chkmult_client_volume(volume_id_10)
        quota_common.creating_files(quota_common.CLIENT_IP_2, mnt_path_10, 1, 1100, 'after_b')
    else:
        quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_10, 1100, 1, 'after_a')
        log.info("切客户端写前，对volume_10进行chkmult检测")
        quota_common.chkmult_client_volume(volume_id_10)
        quota_common.creating_files(quota_common.CLIENT_IP_2, mnt_path_10, 1100, 1, 'after_b')
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, mnt_path_10)
    if dir_size != quota_common.FILE_SIZE_2G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_10, dir_size)

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
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
# Date: 2018-11-6
# @summary：
#   用户：测试逻辑软阈值配额在升级前后是否生效
#   升级前后配额操作：
#           升级前：卷21  容量：2g  根配额1g, 宽限时间60s;升级后：写1g触发软阈值；过60后，看是否可以继续写入
#           升级前：卷22  容量：2g  根配额1g，宽限时间60s;写1100M；升级后：删除文件到小于1g，测试规则是否生效
#           升级前：卷23 容量：2g  根配额1g，宽限时间60s;写2g多，预计2g；升级后：删除文件，检测规则是否还有效
# @notice:
#   本脚本执行前提：需要先用quota_11_0_3_66.py创建好N个卷
#   本脚本需要与quota_upgrade_after_7.py配合使用
# @steps:
#    升级前步骤：
#       1.volume_21创建配额,软阈值1G,等待配额状态为work
#       2.volume_22下面写1100文件,触发软配额
#       3.volume_23下面写2G多文件,触发软配额
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
ip_list = get_config.get_allclient_ip()
mnt_path = get_config.get_mount_paths()  # /mnt/volume
LARGE_BS = random.choice([True, False])  # True大文件，False:小文件


def case():
    """
    author:liyi
    date:2018-11-6
    description: 升级前操作
    :return:
    """
    log.info("case begin ")
    rc_lst = {}
    obj_storage = common.Storagepool()
    rc, storage_pool_id = obj_storage.get_storagepool_id(storage_pool_name="stor")
    common.judge_rc(rc, 0, "get_storage_pool_id faild!")
    obj_volume = common.Volume()
    mnt_path_21 = get_config.get_mount_paths()[0] + "_21"  # /mnt/volume_21
    mnt_path_22 = get_config.get_mount_paths()[0] + "_22"  # /mnt/volume_22
    mnt_path_23 = get_config.get_mount_paths()[0] + "_23"  # /mnt/volume_23

    create_quota_dir_21 = quota_common.VOLUME_NAME + "_21" + ":/"
    create_quota_dir_22 = quota_common.VOLUME_NAME + "_22" + ":/"
    volume_name_23 = quota_common.VOLUME_NAME + "_23"
    volume_id_23 = obj_volume.get_volume_id(volume_name_23)

    log.info("1> volume_21软阈值1G,升级后：写入1G多数据，触发软阈值")
    log.info("1.1> volume_21写入1G多数据，触发软阈值")
    if LARGE_BS:
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, mnt_path_21, 1, 1100,
                                                                'after_a', quota_common.QUOTA_USER)
    else:
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, mnt_path_21, 1100, 1,
                                                                'after_a', quota_common.QUOTA_USER)
    dir_size = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, mnt_path_21,
                                                          quota_common.QUOTA_USER)
    if dir_size != quota_common.FILE_SIZE_1M * 1100:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (mnt_path_21, dir_size)

    log.info("1.2> 延时70s；等待volume_21软阈值超时")
    log.info("time.sleep(70)")
    time.sleep(70)
    ob_node = common.Node()
    rc, quota_id = quota_common.get_one_quota_id(path=create_quota_dir_21,
                                                 u_or_g_type=quota_common.TYPE_USER,
                                                 u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc, qmgrid = quota_common.get_qmgr_id(quota_id)
    common.judge_rc(rc, 0, "get_qmgr_id failed")
    qmgr_ip = ob_node.get_node_ip_by_id(qmgrid)
    quota_common.wait_soft_threshold_over_time(qmgr_ip, quota_id, quota_common.SOFT_TIME_FILENR)

    log.info("1.3> 超时后再写失败，预计1100")
    if LARGE_BS:
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, mnt_path_21, 1, 10,
                                                                'after_s', quota_common.QUOTA_USER)
    else:
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, mnt_path_21, 10, 1,
                                                                'after_s', quota_common.QUOTA_USER)
    dir_size = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, mnt_path_21,
                                                          quota_common.QUOTA_USER)
    if dir_size != quota_common.FILE_SIZE_1M * 1100:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (mnt_path_21, dir_size)

    log.info("2> volume_22软阈值1G(已写1100M)升级后：删除所有文件，测试规则是否生效")
    log.info("2.1> 删除volume_22下面文件")
    rm_dir = os.path.join(mnt_path_22, "*")
    rc,stdout = common.rm_exe(quota_common.NOTE_IP_1, rm_dir)
    common.judge_rc(rc, 0, "rm failed!!")
    log.info("2.2> volume_22下面写1100文件,触发软配额")
    if LARGE_BS:
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, mnt_path_22, 1, 1100, 'after_a',
                                                                quota_common.QUOTA_USER)
    else:
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, mnt_path_22, 1100, 1, 'after_a',
                                                                quota_common.QUOTA_USER)
    dir_size = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, mnt_path_22, quota_common.QUOTA_USER)
    if dir_size != quota_common.FILE_SIZE_1M * 1100:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (mnt_path_22, dir_size)

    log.info("2.3> 等待volume_22软阈值超时")
    time.sleep(70)
    ob_node = common.Node()
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_22, quota_common.TYPE_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc, qmgrid = quota_common.get_qmgr_id(quota_id)
    common.judge_rc(rc, 0, "get_qmgr_id failed")
    qmgr_ip = ob_node.get_node_ip_by_id(qmgrid)
    quota_common.wait_soft_threshold_over_time(qmgr_ip, quota_id, quota_common.SOFT_TIME_FILENR)

    log.info("2.4 超时后再写失败，预计1100")
    if LARGE_BS:
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, mnt_path_22, 1, 10,
                                                                'after_over_time', quota_common.QUOTA_USER)
    else:
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, mnt_path_22, 10, 1,
                                                                'after_overtime', quota_common.QUOTA_USER)
    dir_size = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, mnt_path_22,
                                                          quota_common.QUOTA_USER)
    if dir_size != quota_common.FILE_SIZE_1M * 1100:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (mnt_path_22, dir_size)

    log.info("3> volume_23软阈值1G(已有2G多)升级后：删除再创2G")
    log.info("3.1> 删除volume_23下面文件")
    rm_dir = os.path.join(mnt_path_23, "*")
    rc,stdout = common.rm_exe(quota_common.NOTE_IP_1, rm_dir)
    common.judge_rc(rc, 0, "rm failed!!")
    log.info("3.2> volume_23下面重写2G多文件,触发软配额")
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, mnt_path_23, 1100, 1, 'after_a',
                                                                quota_common.QUOTA_USER)
    log.info("多客户端写入2g多数据，写入前对卷chkmulti")
    quota_common.chkmult_client_volume(volume_id_23)
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_2, mnt_path_23, 1100, 1, 'after_a',
                                                                quota_common.QUOTA_USER)
    dir_size = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, mnt_path_23, quota_common.QUOTA_USER)
    if dir_size != quota_common.FILE_SIZE_1M * 2048:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (mnt_path_23, dir_size)

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
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
# Date: 2018-11-6
# @summary：
#   测试inode软配额在升级前后是否生效
#   升级前后配额操作：
#           升级前：volume_14: 软阈值1000,先写1100，触发软；升级后：写数据，查看规则是否生效
#           升级前：volume_15：软阈值1000，先写500个文件；升级后：继续写，查看规则是否生效
# @notice:
#   本脚本执行前提：需要先用quota_14_0_3_66.py创建好N个卷
#   本脚本需要与quota_upgrade_after_5.py配合使用
# @steps:
#    1.volume_14创建配额,硬阈值1000,等待配额状态为work
#    2.volume_15创建配额,硬阈值1000,等待配额状态为work
# @changelog：
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

    mnt_path_14 = get_config.get_mount_paths()[0] + "_14" #/mnt/volume_14
    mnt_path_15 = get_config.get_mount_paths()[0] + "_15" #/mnt/volume_15
    create_quota_dir_15 = quota_common.VOLUME_NAME + "_15" + ":/"
    ob_node = common.Node()

    log.info("1> volume_14软阈值1000（60s）（已有1100M）升级后：写数据，查看规则是否生效")
    log.info("1.1> volume_14创文件，预计1100M")
    quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_14, 1, 1, 'after')
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, mnt_path_14)
    if dir_inode != 1100:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_14, dir_inode)

    log.info("2> volume_15:inode阈值1000(已有500);升级后：继续写入，规则依然生效")
    log.info("2.1> volume_15继续创建600个文件，触发软阈值，预期total_inode=1100")
    quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_15, 600, 1, 'after')
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, mnt_path_15)
    if dir_inode != 1100:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_15, dir_inode)

    log.info("2.2>等待软阈值超时，无法写入，预计total_inode：1100")
    time.sleep(70)
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_15, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc, qmgrid = quota_common.get_qmgr_id(quota_id)
    common.judge_rc(rc, 0, "get_qmgr_id failed")
    qmgr_ip = ob_node.get_node_ip_by_id(qmgrid)
    quota_common.wait_soft_threshold_over_time(qmgr_ip, quota_id, quota_common.SOFT_TIME_FILENR)
    quota_common.creating_files(quota_common.CLIENT_IP_1, mnt_path_15, 10, 1, 'after_again')
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, mnt_path_15)
    if dir_inode != 1100:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_15, dir_inode)

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
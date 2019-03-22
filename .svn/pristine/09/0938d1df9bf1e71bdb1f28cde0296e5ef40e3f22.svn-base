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
#   用户：测试inode硬阈值配额在升级前后是否生效
#   升级前后配额操作：
#           升级前：volume_24: 硬阈值1000,先写1000；升级后：写数据，查看规则是否生效
#           升级前：volume_25：硬阈值100，先写50个文件；升级后：创建软硬连接规则是否生效
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
    date:2018-11-6
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
    create_quota_dir_25 = quota_common.VOLUME_NAME + "_25" + ":/"
    create_quota_dir_26 = quota_common.VOLUME_NAME + "_26" + ":/"

    log.info("1> volume_24硬阈值1000（已写1000）；升级后：写数据，查看规则是否生效")
    log.info("1.1> volume_24再创文件，预期total_inode=1000")
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_2, mnt_path_24, 1, 1, 'after',  quota_common.QUOTA_USER)
    dir_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_2, mnt_path_24, quota_common.QUOTA_USER)
    if dir_inode != 1000:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_24, dir_inode)

    log.info("2> volume_25硬阈值100(已有50)升级后：创建软硬连接规则是否生效")
    log.info("2.1> 对volume_25下文件创建软连接，创建完后，预期total_inode=100")
    for i in range(50):
        cmd = "cd %s;su quota_user -c \"ln -s file_%s_before_%s soft_%s\";" % (mnt_path_25, quota_common.CLIENT_IP_1, i + 1, i + 1)
        rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
        common.judge_rc(rc, 0, "soft_ln failed!")

    log.info("2.2> volume_25下的文件预计100")
    dir_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, mnt_path_25, quota_common.QUOTA_USER)
    if dir_inode != 100:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_25, dir_inode)

    log.info("2.3> 删除volume_25软文件,预计总inode数变为50")
    rm_path = os.path.join(mnt_path_25, "soft*")
    rc, stdout = common.rm_exe(quota_common.NOTE_IP_1, rm_path)
    common.judge_rc(rc, 0, "rm failed!")
    dir_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, mnt_path_25, quota_common.QUOTA_USER)
    if dir_inode != 50:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_25, dir_inode)

    log.info("2.4>volume_25创建10个硬连接，预计inode数为50")
    for i in range(10):
        cmd = "cd %s;su quota_user -c \"ln file_%s_before_%s hard_%s\";" % (mnt_path_25, quota_common.CLIENT_IP_1, i + 1, i + 1)
        rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
        common.judge_rc(rc, 0, "hard_ln failed!")
    dir_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, mnt_path_25, quota_common.QUOTA_USER)
    if dir_inode != 60:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_25, dir_inode)
    rc, quota_id = quota_common.get_one_quota_id(path=create_quota_dir_25,
                                                 u_or_g_type=quota_common.TYPE_USER,
                                                 u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get quota_id failed!!")
    quota_filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id)
    if 50 != quota_filenr_used_nr:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (mnt_path_25, dir_inode)

    log.info("3> volume_26硬阈值1000(已有1000)升级后：修改配额阈值为1500，查看规则是否生效")
    log.info("3.1> volume_26创建1100个文件，预期total_inode=1000")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir_26, quota_common.TYPE_USER, u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc, pscli_info = quota_common.update_one_quota(id=quota_id,
                                                   filenr_hard_threshold=1500,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("3.2> volume_26创建510文件，预期total_inode=1500")
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_2, mnt_path_26, 510, 1, 'after',  quota_common.QUOTA_USER)
    dir_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_2, mnt_path_26, quota_common.QUOTA_USER)
    if dir_inode != 1500:
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
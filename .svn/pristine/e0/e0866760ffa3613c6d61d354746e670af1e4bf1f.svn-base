#-*-coding:utf-8 -*
import os
import time
import random
import commands

import utils_path
import common
import quota_common
import log
import shell
import get_config
import prepare_clean
import sys
#################################################################
#
# Author: liyi
# Date: 2018-10-13
# @summary：
#    硬inode配额3000，先在父目录下写3000个文件，删除997个文件
#    将剩余的个文件分别移动到子目录下，
#    检测移动操作后，配额规则是否还生效
# @steps:
#    1.创建目录FILENAME/nesting1_1    nesting1_2  nesting1_3
#    2.创建目录FILENAME配额,硬阈值3000 等待配额状态为work
#    3.创建子目录FILENAME/nesting1_x配额,硬阈值1000,等待配额状态为work
#    4.父目录下面写3000个文件,再删除997个含c的文件（写前chkmulti检测）
#    5.移动FILENAME文件到nesting1_1(等待10s，待所有规则都为work状态)
#    6.移动FILENAME文件到nesting1_2(等待10s，待所有规则都为work状态)
#    7.检测文件已使用量在移动后统计是否准确
#    8.查看移动后，配额规则是否还生效（chkmulti检测）
# @changelog：
#################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
SCRIPT_PATH = os.path.join(quota_common.QUOTA_PATH, FILE_NAME)           # /mnt/volume1/qouta_test_dir/quota_11_0_3_1


def case():
    log.info("case begin ")
    rc_lst = {}
    log.info("1> 创建目录FILENAME/nesting1_1    nesting1_2  nesting1_3")
    quota_id_lst = []
    dir0 = SCRIPT_PATH
    dir1_ = []
    for i in range(3):
        dir1_.append(os.path.join(dir0, 'nesting1_%s' % (i)))
    create_quota_dir0 = os.path.join(get_config.get_one_volume_name() + ':', quota_common.QUOTA_PATH_BASENAME, os.path.basename(dir0))
    log.info(create_quota_dir0)

    for dir in dir1_:
        quota_common.creating_dir(quota_common.NOTE_IP_1, dir)
    create_quota_dir1_ = []
    for i in range(3):
        create_quota_dir1_.append(os.path.join(create_quota_dir0, os.path.basename(dir1_[i])))

    log.info("2> 创建父目录配额,硬阈值3000 等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir0,
                                                   filenr_hard_threshold=3000,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("3> 创建三个子目录配额,硬阈值1000 等待配额状态为work")
    for i in range(3):
        rc, pscli_info = quota_common.create_one_quota(create_quota_dir1_[i],
                                                       filenr_hard_threshold=1000,
                                                       filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
        common.judge_rc(rc, 0, "create  quota failed")
        rc, quota_id = quota_common.get_one_quota_id(create_quota_dir1_[i], quota_common.TYPE_CATALOG)
        common.judge_rc(rc, 0, "get_one_quota_id failed")
        quota_id_lst.append(quota_id)
        rc = quota_common.wait_quota_work(quota_id)
        common.judge_rc(rc, 0, "get quota info failed")

    log.info("4> 父目录下面写3000个文件,再删除1000个")
    log.info("写入数据前：对FILENAME nesting1_1 nesting1_2  nesting1_3做chkmulti检测")
    quota_common.chkmult_client_all_dir_on_path(dir0)
    for i in range(3):
        quota_common.chkmult_client_all_dir_on_path(dir1_[i])
    quota_common.creating_files(quota_common.CLIENT_IP_1, dir0, 1000, 1, 'a', quota_id=quota_id_lst[0])
    quota_common.creating_files(quota_common.CLIENT_IP_2, dir0, 1000, 1, 'b', quota_id=quota_id_lst[0])
    quota_common.creating_files(quota_common.CLIENT_IP_3, dir0, 1000, 1, 'c', quota_id=quota_id_lst[0])
    dir0_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir0)
    if dir0_inode != 3000:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir0, dir0_inode)
    log.info("4.1> 删除997个c文件")
    rm_dir = os.path.join(dir0, "*c*")
    rc,stdout = common.rm_exe(quota_common.NOTE_IP_1, rm_dir)
    common.judge_rc(rc, 0, "rm failed!!")

    log.info("5> 移动FILENAME文件a到nesting1_0")
    cmd = "mv %s*a* %s" % (dir0 + "/", dir1_[0])
    rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "mv failed!")
    time.sleep(3)

    log.info("5.1> 等待10s，待所有规则都为work状态")
    time.sleep(10)
    quota_common.wait_quota_work_after_mv(create_quota_dir0, quota_common.TYPE_CATALOG)
    for i in range(3):
        quota_common.wait_quota_work_after_mv(create_quota_dir1_[i], quota_common.TYPE_CATALOG)

    log.info("6> 移动FILENAME含b的文件到nesting1_1")
    cmd = "mv %s*b* %s" % (dir0 + "/", dir1_[1])
    rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "mv failed!")

    log.info("6.1> 等待10s，待所有规则都为work状态")
    time.sleep(10)
    quota_common.wait_quota_work_after_mv(create_quota_dir0, quota_common.TYPE_CATALOG)
    for i in range(3):
        quota_common.wait_quota_work_after_mv(create_quota_dir1_[i], quota_common.TYPE_CATALOG)

    log.info("7> 检测文件已使用量在移动后统计是否准确")
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0,
                                                      quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir0_filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id_dir0)
    if dir0_filenr_used_nr != 2003:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir0, dir0_filenr_used_nr)

    for i in range(2):
        rc, quota_id = quota_common.get_one_quota_id(create_quota_dir1_[i],
                                                            quota_common.TYPE_CATALOG)
        common.judge_rc(rc, 0, "get_one_quota_id failed")
        filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id)
        if filenr_used_nr != 1000:
            rc_lst[sys._getframe().f_lineno] = 'dir_[%s] total_size:%s' % (i, filenr_used_nr)

    log.info('8>查看移动后，配额规则是否还生效')
    log.info("写入数据前：chkmulti检测")
    quota_common.chkmult_client_all_dir_on_path(dir0)
    for i in range(3):
        quota_common.chkmult_client_all_dir_on_path(dir1_[i])
    log.info("在FILENAME写入1000个，预计只能写到3000个")
    quota_common.creating_files(quota_common.CLIENT_IP_1, dir0, 1000, 1, 'mv_a', quota_id=quota_id_lst[0])
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir0)
    if dir_inode != 3000:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir0, dir_inode)
    for i in range(2):
        log.info("%s下再写失败，预期1000" % dir1_[i])
        quota_common.chkmult_client_all_dir_on_path(dir1_[i])
        quota_common.creating_files(quota_common.CLIENT_IP_2, dir1_[i], 1, 1, 'mv_a', quota_id=quota_id_lst[i+1])
        dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir1_[i])
        if dir_inode != 1000:
            rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_[i], dir_inode)

    """判断rc_lst"""
    if rc_lst != {}:
        log.info(rc_lst)
        for i in rc_lst:
            log.info("check point in line : %s is about :%s " % (i, rc_lst[i]))
        log.info('If there are many lines, you may only need to look at the first line.')
        common.except_exit("some check point failed")


def main():
    prepare_clean.quota_test_prepare(FILE_NAME)
    case()
    prepare_clean.quota_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)
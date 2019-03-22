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
# Date: 2018-10-18
# @summary：
#    对父目录a创建硬阈值配额1000，创建子目录b硬阈值为500，子目录写250个文件，
#    对子目录所有文件创建软连接，再写数据失败，预计inode总数为500，移动子目录
#    下的含a的文件(250个)到父目录，检测移动后统计是否准确；父目录下创建含a文件
#    的硬连接，不影响inode数据的变化，创建完毕后，查看规则是否生效。
# @steps:
#    1.创建目录FILENAME/nesting1_1
#    2.创建父目录配额,硬阈值1000 等待配额状态为work
#    3.创建子目录FILENAME/nesting1_1配额,硬阈值500,等待配额状态为work
#    4.子目录创建250文件，预期total_inode=250(chkmulti检测)
#    5.对子目录创建的文件创建软连接，创建完后，预期total_inode=500
#    6.子目录中再写文件失败，预计子目录中inode个数是500
#    7.移动nesting1_1下文件到FILENAME下
#    8.等待10s，待所有规则都为work状态
#    9.检测文件已使用量在移动后统计是否准确
#    10.在父目录下面创建250个硬连接，预计父目录inode：501 子目录：250
#    11.检测创建硬链接后文件已使用量统计是否准确
#    12.查看移动后，配额规则是否还生效
# @changelog：
#################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
SCRIPT_PATH = os.path.join(quota_common.QUOTA_PATH, FILE_NAME)           # /mnt/volume1/qouta_test_dir/quota_11_0_3_1


def case():
    log.info("case begin ")
    rc_lst = {}
    log.info("1> 创建目录FILENAME/nesting1_1")
    quota_id_lst = []
    dir0 = SCRIPT_PATH
    dir1_1 = os.path.join(dir0, 'nesting1_1')
    quota_common.creating_dir(quota_common.NOTE_IP_1, dir1_1)

    create_quota_dir0 = os.path.join(get_config.get_one_volume_name() + ':', quota_common.QUOTA_PATH_BASENAME, os.path.basename(dir0))
    log.info(create_quota_dir0)
    create_quota_dir1_1 = os.path.join(create_quota_dir0, os.path.basename(dir1_1))

    log.info("2> 创建父目录配额,硬阈值1000 等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir0,
                                                   filenr_hard_threshold=1000,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")

    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("3> 创建子目录FILENAME/nesting1_1配额,硬阈值500,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir1_1,
                                                   filenr_hard_threshold=500,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir1_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("4> 子目录创建250文件，预期total_inode=250")
    log.info("写入数据前：做chkmulti检测")
    quota_common.chkmult_client_all_dir_on_path(dir1_1)
    quota_common.creating_files(quota_common.CLIENT_IP_1, dir1_1, 250, 1, 'a', quota_id=quota_id_lst[1])
    dir1_1_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir1_1)
    if dir1_1_inode != 250:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_1, dir1_1_inode)

    log.info("5> 对子目录创建的文件创建软连接，创建完后，预期total_inode=500")
    for i in range(250):
        cmd = "cd %s;ln -s file_%s_a_%s soft_%s" % (dir1_1, quota_common.CLIENT_IP_1, i+1, i+1)
        rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
        common.judge_rc(rc, 0, "soft_ln failed!")

    log.info("6> 子目录中再写文件失败，预计子目录中inode个数是500")
    quota_common.creating_files(quota_common.CLIENT_IP_1, dir1_1, 1, 1, 'after_ln', quota_id=quota_id_lst[1])
    dir1_1_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir1_1)
    if dir1_1_inode != 500:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_1, dir1_1_inode)

    log.info("7> 移动nesting1_1下文件到FILENAME下")
    cmd = "mv %s*a* %s" % (dir1_1 + "/", dir0)
    rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "mv failed!")

    log.info("8> 等待10s，待所有规则都为work状态")
    log.info("延时10s")
    time.sleep(10)
    quota_common.wait_quota_work_after_mv(create_quota_dir0, quota_common.TYPE_CATALOG)
    quota_common.wait_quota_work_after_mv(create_quota_dir1_1, quota_common.TYPE_CATALOG)

    log.info("9> 检测文件已使用量在移动后统计是否准确")
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0,
                                                      quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir0_filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id_dir0)
    if dir0_filenr_used_nr != 501:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir0, dir0_filenr_used_nr)

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1,
                                                        quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir1_1_filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id_dir1_1)
    if dir1_1_filenr_used_nr != 250:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir1_1, dir1_1_filenr_used_nr)
    log.info("9.1>  FILENAME(预期501):%s  nesting1_1(预期250)：%s" % (dir0_filenr_used_nr, dir1_1_filenr_used_nr))

    log.info("10>在父目录下面创建250个硬连接，预计父目录inode：501 子目录：250")
    for i in range(250):
        cmd = "cd %s;ln file_%s_a_%s hard_%s" % (dir0, quota_common.CLIENT_IP_1, i+1, i+1)
        rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
        common.judge_rc(rc, 0, "hard_ln failed!")
    log.info("11> 检测创建硬链接后文件已使用量统计是否准确")
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0,
                                                      quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir0_filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id_dir0)
    if dir0_filenr_used_nr != 501:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir0, dir0_filenr_used_nr)

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1,
                                                        quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir1_1_filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id_dir1_1)
    if dir1_1_filenr_used_nr != 250:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir1_1, dir1_1_filenr_used_nr)
    log.info("11.1>  FILENAME(预期501):%s  nesting1_1(预期250)：%s" % (dir0_filenr_used_nr, dir1_1_filenr_used_nr))

    log.info('12>查看移动后，配额规则是否还生效')
    log.info('12.1> nesting1_1下再写250预期500')
    log.info("写入数据前：chkmulti检测")
    quota_common.chkmult_client_all_dir_on_path(dir1_1)
    quota_common.creating_files(quota_common.CLIENT_IP_2, dir1_1, 250, 1, 'NE_after_mv', quota_id=quota_id_lst[1])
    dir1_1_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_2, dir1_1)
    if dir1_1_inode != 500:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_1, dir1_1_inode)
    log.info('12.2> FILENAME下再写，预计共1000个')
    quota_common.creating_files(quota_common.CLIENT_IP_2, dir0, 250, 1, 'F_mv_a', quota_id=quota_id_lst[0])
    dir0_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir0)
    if dir0_inode != 1250:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir0, dir0_inode)

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

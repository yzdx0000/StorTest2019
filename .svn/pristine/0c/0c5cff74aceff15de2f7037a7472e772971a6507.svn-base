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
#    父目录软阈值2000，宽限时间60秒，子目录软阈值1000，宽限时间60秒，子目录创建1001文件开始计时，
#    过期后子目录无法创建文件，移动子目录下面文件到父目录，检测移动操作后，规则是否生效
#    子目录下面写1001个文件，等待60s后，父和子都无法继续写入了，父预计2002个，子1001个
# @steps:
#    1.创建目录FILENAME/nesting1_1
#    2.创建目录FILENAME配额,软阈值2000 宽限时间60秒 等待配额状态为work
#    3.创建子目录FILENAME/nesting1_1/配额,子目录软阈值1000，宽限时间60秒 等待配额状态为work
#    4.子目录创建1001文件开始计时，过期后子目录无法创建文件（写入数据前：chkmulti检测）
#    5.移动nesting1_1下文件到FILENAME下
#    6.等待10s，待所有规则都为work状态
#    7.检测文件已使用量在移动后统计是否准确
#    8.查看移动后，配额规则是否还生效
# @changelog：
#################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
SCRIPT_PATH = os.path.join(quota_common.QUOTA_PATH, FILE_NAME)           # /mnt/volume1/qouta_test_dir/quota_11_0_3_1


def case():
    log.info("case begin ")
    rc_lst = {}
    ob_node = common.Node()
    log.info("1.创建目录FILENAME/nesting1_1")
    quota_id_lst = []
    dir0 = SCRIPT_PATH
    dir1_1 = os.path.join(dir0, 'nesting1_1')
    quota_common.creating_dir(quota_common.NOTE_IP_1, dir1_1)

    create_quota_dir0 = os.path.join(get_config.get_one_volume_name() + ':', quota_common.QUOTA_PATH_BASENAME, os.path.basename(dir0))
    log.info(create_quota_dir0)
    create_quota_dir1_1 = os.path.join(create_quota_dir0, os.path.basename(dir1_1))

    log.info("2> 创建父目录配额,软阈值2000 宽限时间60秒 等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir0,
                                                   filenr_soft_threshold=2000, filenr_grace_time=60,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("3> 创建子目录FILENAME/nesting1_1配额,子目录软阈值1000，宽限时间60秒 等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir1_1,
                                                   filenr_soft_threshold=1000, filenr_grace_time=60,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir1_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("4> 子目录创建1001个文件，过期后子目录无法创建文件")
    log.info("写入数据前：chkmulti检测")
    quota_common.chkmult_client_all_dir_on_path(dir1_1)
    quota_common.creating_files(quota_common.CLIENT_IP_1, dir1_1, 1001, 1, 'a', quota_id=quota_id_lst[1])
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir1_1)
    if dir_inode != 1001:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_1, dir_inode)
    rc, qmgrid = quota_common.get_qmgr_id(quota_id_lst[0])
    common.judge_rc(rc, 0, "get_qmgr_id failed")
    qmgr_ip = ob_node.get_node_ip_by_id(qmgrid)
    '''等待超过超期时间'''
    log.info('wait 75s')
    time.sleep(75)
    quota_common.wait_soft_threshold_over_time(qmgr_ip, quota_id_lst[1], quota_common.SOFT_TIME_FILENR)
    quota_common.creating_files(quota_common.CLIENT_IP_2, dir1_1, 1, 1, 'b', quota_id=quota_id_lst[1])
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_2, dir1_1)
    if dir_inode != 1001:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_1, dir_inode)

    log.info("5> 移动nesting1_1下文件到FILENAME下")
    cmd = "mv %s*a* %s" % (dir1_1 + "/", dir0)
    rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "mv failed!")

    log.info("6> 等待10s，待所有规则都为work状态")
    log.info("延时10s")
    time.sleep(10)
    quota_common.wait_quota_work_after_mv(create_quota_dir0, quota_common.TYPE_CATALOG)
    quota_common.wait_quota_work_after_mv(create_quota_dir1_1, quota_common.TYPE_CATALOG)

    log.info("7> 检测文件已使用量在移动后统计是否准确")
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0,
                                                      quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir0_filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id_dir0)
    if dir0_filenr_used_nr != 1002:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir0, dir0_filenr_used_nr)

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1,
                                                        quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir1_1_filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id_dir1_1)
    if dir1_1_filenr_used_nr != 0:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir1_1, dir1_1_filenr_used_nr)
    log.info("7>  FILENAME(预期1001):%s  nesting1_1(预期0)：%s" % (dir0_filenr_used_nr, dir1_1_filenr_used_nr))

    log.info('8>查看移动后，配额规则是否还生效')
    log.info("8.1> 子目录创建1001个文件，子目录父目录都超过软阈值")
    log.info("写入数据前：chkmulti检测")
    quota_common.chkmult_client_all_dir_on_path(dir1_1)
    quota_common.creating_files(quota_common.CLIENT_IP_1, dir1_1, 1001, 1, 'a', quota_id=quota_id_lst[1])
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir1_1)
    if dir_inode != 1001:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_1, dir_inode)
    rc, qmgrid = quota_common.get_qmgr_id(quota_id_lst[0])
    common.judge_rc(rc, 0, "get_qmgr_id failed")
    '''等待超过超期时间'''
    log.info('wait 75s')
    time.sleep(75)
    quota_common.wait_soft_threshold_over_time(qmgr_ip, quota_id_lst[1], quota_common.SOFT_TIME_FILENR)
    log.info("子目录写入数据前：chkmulti检测")
    quota_common.chkmult_client_all_dir_on_path(dir1_1)
    quota_common.creating_files(quota_common.CLIENT_IP_2, dir1_1, 1, 1, 'mv_b', quota_id=quota_id_lst[1])
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_2, dir1_1)
    if dir_inode != 1001:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_1, dir_inode)

    log.info("父目录写入数据前：chkmulti检测")
    quota_common.creating_files(quota_common.CLIENT_IP_3, dir0, 1, 1, 'mv_c', quota_id=quota_id_lst[0])
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_3, dir0)
    if dir_inode != 2003:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir0, dir_inode)

    """判断rc_lst"""
    if rc_lst != {}:
        log.info(rc_lst)
        for i in rc_lst:
            log.info("check point in line : %s is about :%s " % (i, rc_lst[i]))
        log.info('If there are many lines, you may only need to look at the first line.')
        common.except_exit("some check point failed")

    return


def main():
    prepare_clean.quota_test_prepare(FILE_NAME)
    case()
    prepare_clean.quota_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)

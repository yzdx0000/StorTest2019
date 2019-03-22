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
#    父目录软阈值2G，宽限时间60秒，子目录软阈值1G，宽限时间60秒，子目录创建1100M文件开始计时，
#    过期后子目录无法创建文件，将子目录下文件移动到父目录下，查看移动后，配额规则是否生效
#    子目录再创建1100M文件，60s后，预计子目录和父目录都无法写入文件
# @steps:
#    1.创建目录FILENAME/nesting1_1
#    2.创建目录FILENAME配额,软阈值2G 宽限时间60秒 等待配额状态为work
#    3.创建子目录FILENAME/nesting1_1/配额,子目录软阈值1G，宽限时间60秒 等待配额状态为work
#    4.子目录创建1100M文件开始计时，过期后子目录无法创建文件
#    5.将子目录下面的部分文件移动到父目录
#    6.等待10s，待父目录、子目录规则都为work状态
#    7.检测配额已使用量在移动后统计是否准确 预期父目录1100M，子目录0
#    8.移动操作后，查看配额规则是否有效,子目录下写入1100M文件，等待60s，预计父目录和子目录都无法写入
# @changelog：
#################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
SCRIPT_PATH = os.path.join(quota_common.QUOTA_PATH, FILE_NAME)           # /mnt/volume1/qouta_test_dir/quota_11_0_3_1
LARGE_BS = random.choice([True, False])   # True大文件，False:小文件

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

    log.info("2> 创建父目录配额,软阈值2G 宽限时间60秒 等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir0,
                                                   logical_soft_threshold=quota_common.FILE_SIZE_2G, logical_grace_time=60,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("3> 创建子目录FILENAME/nesting1_1配额,子目录软阈值1G，宽限时间60秒 等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir1_1,
                                                   logical_soft_threshold=quota_common.FILE_SIZE_1G, logical_grace_time=60,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir1_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("4> 子目录创建1100M文件开始计时，过期后子目录无法创建文件")
    if LARGE_BS:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir1_1, 1, 1100, 'a', quota_id=quota_id_lst[1])
    else:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir1_1, 1100, 1, 'a', quota_id=quota_id_lst[1])
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, dir1_1)
    if dir_size != quota_common.FILE_SIZE_1M * 1100:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (dir1_1, dir_size)
    rc, qmgrid = quota_common.get_qmgr_id(quota_id_lst[0])
    common.judge_rc(rc, 0, "get_qmgr_id failed")
    qmgr_ip = ob_node.get_node_ip_by_id(qmgrid)
    '''等待超过超期时间'''
    log.info('wait 75s')
    time.sleep(75)
    quota_common.wait_soft_threshold_over_time(qmgr_ip, quota_id_lst[1], quota_common.SOFT_TIME_LOGICAL)
    quota_common.creating_files(quota_common.CLIENT_IP_2, dir1_1, 1, 1, 'b', quota_id=quota_id_lst[1])
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_2, dir1_1)
    if dir_size != quota_common.FILE_SIZE_1M * 1100:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (dir1_1, dir_size)

    log.info("5> 将子目录下面的部分文件移动到父目录")
    cmd = "mv %s*a* %s" % (dir1_1 + "/", dir0)
    rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "mv failed!")

    log.info("6> 等待10s，待父目录、子目录规则都为work状态")
    log.info("time.sleep(10s)")
    time.sleep(10)
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0,
                                                      quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir0)

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1,
                                                        quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir1_1)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("7> 检测配额已使用量在移动后统计是否准确 预期父目录1100M，子目录0")
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0,
                                                      quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir0_logical_capacity = quota_common.get_quota_logical_used_capacity(quota_id_dir0)
    if dir0_logical_capacity != quota_common.FILE_SIZE_1M * 1100:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir0, dir0_logical_capacity)

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1,
                                                        quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir1_1_logical_capacity = quota_common.get_quota_logical_used_capacity(quota_id_dir1_1)
    if dir1_1_logical_capacity != 0:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir1_1, dir1_1_logical_capacity)

    log.info("8> 移动操作后，查看配额规则是否有效")
    log.info("8.1> 子目录再创建1100M文件,此时父目录和子目录超过阈值")
    quota_common.creating_files(quota_common.CLIENT_IP_2, dir1_1, 1100, 1, 'after_mv_create_again',
                                quota_id=quota_id_lst[1])
    dir1_1_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_2, dir1_1)
    if dir1_1_size != quota_common.FILE_SIZE_1M * 1100:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s expect:1100M total_size: %s ' % (dir1_1, dir1_1_size)
    log.info("8.2> 等待超过60s，在父目录和子目录中写入，预计失败")
    '''等待超过超期时间'''
    log.info('wait 75s')
    time.sleep(75)
    quota_common.wait_soft_threshold_over_time(qmgr_ip, quota_id_lst[1], quota_common.SOFT_TIME_LOGICAL)
    log.info("8.3> 父目录写入失败，预计共2200M")
    quota_common.creating_files(quota_common.CLIENT_IP_1, dir1_1, 1, 1, 'F_mv_a', quota_id=quota_id_lst[0])
    dir0_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, dir0)
    if dir0_size != quota_common.FILE_SIZE_1M * 2200:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (dir0, dir0_size)
    log.info("8.4> 子目录写入失败，预计共1100M")
    quota_common.creating_files(quota_common.CLIENT_IP_2, dir1_1, 1, 1, 'NE_mv_a', quota_id=quota_id_lst[1])
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_2, dir1_1)
    if dir_size != quota_common.FILE_SIZE_1M * 1100:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (dir1_1, dir_size)

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

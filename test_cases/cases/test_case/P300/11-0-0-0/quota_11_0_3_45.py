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
# Date: 2018-10-11
# @summary：
#    对父目录a创建硬阈值配额3G，在a下创建目录b硬阈值配额2G，在目录b创建目录c硬阈值配额1G，
#    在目录c下创建文件，限制size为1G，在目录b下创建文件，限制size为2G，
#    在目录a下创建文件，限制size为3G
# @steps:
#    1.创建目录FILENAME/nesting1_1/nesting2_1/
#    2.创建目录FILENAME配额,硬阈值3G等待配额状态为work
#    3.创建2个子目录配额,硬阈值2G  1G  等待配额状态为work
#    4.子目录nesting2_1下写1100M文件预期total_size=1G
#    5.移动子目录nesting2_1下的1G到子目录nesting1_1下
#    6.等待10s，待所有规则都为work状态
#    7.检测配额已使用量在移动后统计是否准确 nesting2_1预期0G nesting1_1预期1G
#    8.检测移动后nesting2_1和nesting1_1规则是否生效
#    9.移动子目录nesting1_1和nesting2_1下的1G到FILENAME下
#    10.检测配额已使用量在移动后统计是否准确 FILENAME:2G nesting2_1预期0G，nesting1_1预期0G
#    11.检测移动后规则是否生效
# @changelog：

#################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
SCRIPT_PATH = os.path.join(quota_common.QUOTA_PATH, FILE_NAME)           # /mnt/volume1/qouta_test_dir/quota_11_0_3_1
LARGE_BS = random.choice([True, False])   # True大文件，False:小文件


def get_quota_logical_used_capacity(quota_id):
    """
    author:liyi
    date:2018-10-10
    description:获取逻辑配额使用容量
    :return:
    """
    rc, stdout = quota_common.get_one_quota_info(quota_id)
    common.judge_rc(rc, 0, 'get_one_quota_info')
    list_quotas = stdout["result"]["quotas"]
    for quota in list_quotas:
        logical_used_capacity = quota["logical_used_capacity"]
        return logical_used_capacity


def case():
    log.info("case begin ")
    rc_lst = {}
    log.info("1.创建目录FILENAME/nesting1_1/nesting2_1")
    quota_id_lst = []
    dir0 = SCRIPT_PATH
    dir1_1 = os.path.join(dir0, 'nesting1_1')
    dir2_1 = os.path.join(dir1_1, 'nesting2_1')

    create_quota_dir0 = os.path.join(get_config.get_one_volume_name() + ':', quota_common.QUOTA_PATH_BASENAME, os.path.basename(dir0))
    log.info(create_quota_dir0)
    create_quota_dir1_1 = os.path.join(create_quota_dir0, 'nesting1_1')
    create_quota_dir2_1 = os.path.join(create_quota_dir1_1, 'nesting2_1')

    quota_common.creating_dir(quota_common.NOTE_IP_1, dir0)
    quota_common.creating_dir(quota_common.NOTE_IP_1, dir1_1)
    quota_common.creating_dir(quota_common.NOTE_IP_1, dir2_1)

    log.info("2> 创建父目录配额,硬阈值3G 等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir0,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_3G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("3> 创建2个子目录配额,硬阈值2G  1G  等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir1_1,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_2G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir1_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir2_1,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_1G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir2_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info('4> 子目录nesting2_1下写1100M文件预期total_size=1G')
    if LARGE_BS:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir2_1, 1, 1100, 'a', quota_id=quota_id_lst[2])
    else:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir2_1, 1100, 1, 'a', quota_id=quota_id_lst[2])
    dir2_1_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, dir2_1)
    if dir2_1_size != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (dir2_1, dir2_1_size)

    log.info("5> 移动子目录nesting2_1下的1G到子目录nesting1_1下")
    cmd = "mv %s*a* %s" % (dir2_1+"/", dir1_1)
    rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "mv failed!")

    log.info("6> 等待10s，待所有规则都为work状态")
    log.info("time.sleep(10s)")
    time.sleep(10)
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir0)

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir1_1)
    common.judge_rc(rc, 0, "get quota info failed")

    rc, quota_id_dir2_1 = quota_common.get_one_quota_id(create_quota_dir2_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir2_1)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("7> 检测配额已使用量在移动后统计是否准确 nesting2_1预期0G nesting1_1预期1G")
    rc, quota_id_dir2_1 = quota_common.get_one_quota_id(create_quota_dir2_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir2_1_logical_capacity = get_quota_logical_used_capacity(quota_id_dir2_1)
    if dir2_1_logical_capacity != 0:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir2_1, dir2_1_logical_capacity)

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1,
                                                        quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir1_1_logical_capacity = get_quota_logical_used_capacity(quota_id_dir1_1)
    if dir1_1_logical_capacity != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir1_1, dir1_1_logical_capacity)

    log.info("8> 检测移动后nesting2_1和nesting1_1规则是否生效")
    log.info('8.1> 子目录nesting2_1下写1100M文件预期total_size=1G')
    if LARGE_BS:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir2_1, 1, 1100, 'nes2_a_mv_1', quota_id=quota_id_lst[2])
    else:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir2_1, 1100, 1, 'nes2_a_mv_1', quota_id=quota_id_lst[2])
    dir2_1_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, dir2_1)
    if dir2_1_size != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (dir2_1, dir2_1_size)

    log.info('8.2> 子目录nesting1_1下再写失败1100M文件预期total_size=2G')
    if LARGE_BS:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir1_1, 1, 10, 'nes1_a_mv_1', quota_id=quota_id_lst[1])
    else:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir1_1, 10, 1, 'nes1_a_mv_1', quota_id=quota_id_lst[1])
    dir1_1_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, dir1_1)
    if dir1_1_size != quota_common.FILE_SIZE_2G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (dir1_1, dir1_1_size)

    log.info("9> 移动子目录nesting1_1和nesting2_1下的1G到FILENAME下")
    log.info("9.1> 移动子目录nesting1_1下的1G到FILENAME下")
    cmd = "mv %s*a* %s" % (dir1_1+"/", dir0)
    rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "mv failed!")

    log.info("9.2> 等待10s，待所有规则都为work状态")
    log.info("time.sleep(10s)")
    time.sleep(10)
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir0)

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir1_1)
    common.judge_rc(rc, 0, "get quota info failed")

    rc, quota_id_dir2_1 = quota_common.get_one_quota_id(create_quota_dir2_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir2_1)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("9.3> 移动子目录nesting2_1下的1G到FILENAME下")
    cmd = "mv %s*a* %s" % (dir2_1 + "/", dir0)
    rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "mv failed!")

    log.info("9.4> 等待10s，待所有规则都为work状态")
    log.info("time.sleep(10s)")
    time.sleep(10)
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir0)

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir1_1)
    common.judge_rc(rc, 0, "get quota info failed")

    rc, quota_id_dir2_1 = quota_common.get_one_quota_id(create_quota_dir2_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir2_1)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("10> 检测配额已使用量在移动后统计是否准确 FILENAME:2G nesting2_1预期0G，nesting1_1预期0G")
    dir2_1_logical_capacity = get_quota_logical_used_capacity(quota_id_dir2_1)
    if dir2_1_logical_capacity != 0:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir2_1, dir2_1_logical_capacity)

    dir1_1_logical_capacity = get_quota_logical_used_capacity(quota_id_dir1_1)
    if dir1_1_logical_capacity != 0:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir1_1, dir1_1_logical_capacity)

    dir0_logical_capacity = get_quota_logical_used_capacity(quota_id_dir0)
    if dir0_logical_capacity != quota_common.FILE_SIZE_2G:
        rc_lst[sys._getframe().sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir0, dir0_logical_capacity)

    log.info("11> 检测移动后规则是否生效")
    log.info('11.1> 子目录nesting2_1下写1100M文件预期total_size=1G')
    if LARGE_BS:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir2_1, 1, 1100, 'nes2_a_mv_2', quota_id=quota_id_lst[2])
    else:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir2_1, 1100, 1, 'nes2_a_mv_2', quota_id=quota_id_lst[2])
    dir2_1_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, dir2_1)
    if dir2_1_size != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (dir2_1, dir2_1_size)

    log.info('11.2> FILENAME下再写失败预期total_size=3G')
    if LARGE_BS:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir0, 1, 10, 'nes1_a_mv_2', quota_id=quota_id_lst[1])
    else:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir0, 10, 1, 'nes1_a_mv_2', quota_id=quota_id_lst[1])
    dir0_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, dir0)
    if dir0_size != quota_common.FILE_SIZE_3G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (dir0, dir0_size)

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

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
#    对父目录a创建硬阈值配额2G，创建子目录b硬阈值为1G，移动子目录部分
#    文件到父目录后，检测经过移动操作后的规则，是否生效。
# @steps:
#    1.创建目录FILENAME/nesting1_1
#    2.创建目录FILENAME配额,硬阈值2G 等待配额状态为work
#    3.创建子目录FILENAME/nesting1_1配额,硬阈值1G,等待配额状态为work
#    4.子目录创建1G多文件，预期total_size=1G
#    5.将子目录下面的部分文件(512M)移动到父目录
#    6.等待10s，待父目录、子目录规则都为work状态
#    7.检测配额已使用量在移动后统计是否准确
#    8.子目录写入520M文件，预计只能写512M
#    9.父目录写入520M文件，预计只能写512M
# @changelog：
#################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
SCRIPT_PATH = os.path.join(quota_common.QUOTA_PATH, FILE_NAME)           # /mnt/volume1/qouta_test_dir/quota_11_0_3_1
LARGE_BS = random.choice([True, False])   # True大文件，False:小文件
FILE_SIZE_HALF_1G = 536870912


def get_quota_logical_used_capacity(quota_id):
    """
    author:liyi
    date:2018-10-10
    description:获取逻辑配额使用容量
    :return:
    """
    rc, stdout = quota_common.get_one_quota_info(quota_id)
    common.judge_rc(rc, 0, "get_one_quota_info failed")
    list_quotas = stdout["result"]["quotas"]
    for quota in list_quotas:
        logical_used_capacity = quota["logical_used_capacity"]
        return logical_used_capacity


def case():
    log.info("case begin ")
    rc_lst = {}
    log.info("1.创建目录FILENAME/nesting1_1")
    quota_id_lst = []
    dir0 = SCRIPT_PATH
    dir1_1 = os.path.join(dir0, 'nesting1_1')
    quota_common.creating_dir(quota_common.NOTE_IP_1, dir1_1)

    create_quota_dir0 = os.path.join(get_config.get_one_volume_name() + ':', quota_common.QUOTA_PATH_BASENAME, os.path.basename(dir0))
    log.info(create_quota_dir0)
    create_quota_dir1_1 = os.path.join(create_quota_dir0, os.path.basename(dir1_1))

    log.info("2> 创建父目录配额,硬阈值2G  等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir0,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_2G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("3> 创建子目录FILENAME/nesting1_1配额,硬阈值1G,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir1_1,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_1G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir1_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("4> 子目录创建1G多文件，预期total_size=1G")
    if LARGE_BS:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir1_1, 1, 512, 'a', quota_id=quota_id_lst[0])
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir1_1, 1, 512, 'b', quota_id=quota_id_lst[0])
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir1_1, 1, 512, 'c', quota_id=quota_id_lst[0])
    else:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir1_1, 512, 1, 'a', quota_id=quota_id_lst[0])
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir1_1, 512, 1, 'b', quota_id=quota_id_lst[0])
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir1_1, 1, 1, 'c', quota_id=quota_id_lst[0])
    dir1_1_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, dir1_1)
    if dir1_1_size != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_1, dir1_1_size)

    log.info("5> 将子目录下面的部分文件移动到父目录")
    log.info("5.1> 移动前：子目录文件大小(预计为1G)为：%s" % dir1_1_size)
    cmd = "mv %s*b* %s" % (dir1_1 + "/", dir0)
    rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "mv failed!")
    dir1_1_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, dir1_1)
    log.info("5.2> 移动后：子目录文件大小(预计为0.5G)为：%s" % dir1_1_size)

    log.info("6> 等待10s，待父目录、子目录规则都为work状态")
    log.info("time.sleep(10s)")
    time.sleep(10)
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir0)

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir1_1)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("7> 检测配额已使用量在移动后统计是否准确 预期父目录1G，子目录0.5G")
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir0_logical_capacity = get_quota_logical_used_capacity(quota_id_dir0)
    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1,
                                                        quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir1_1_logical_capacity = get_quota_logical_used_capacity(quota_id_dir1_1)
    if dir0_logical_capacity != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir0, dir0_logical_capacity)
    if dir1_1_logical_capacity != FILE_SIZE_HALF_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir1_1, dir1_1_logical_capacity)

    log.info("8> 子目录写入520M文件，预计只能写512M")
    quota_common.creating_files(quota_common.CLIENT_IP_1, dir1_1, 520, 1, 'd', quota_id=quota_id_lst[0])
    dir1_1_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, dir1_1)
    if dir1_1_size != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (dir1_1, dir1_1_size)

    log.info("9> 父目录写入520M文件，预计只能写512M")
    quota_common.creating_files(quota_common.CLIENT_IP_1, dir0, 520, 1, 'd', quota_id=quota_id_lst[0])
    dir0_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, dir0)
    if dir0_size != quota_common.FILE_SIZE_2G:
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

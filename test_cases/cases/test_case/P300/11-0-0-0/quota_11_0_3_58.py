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
# Date: 2018-10-16
# @summary：
#    对父目录a创建硬阈值配额1G，创建子目录b硬阈值为1G，在父目录下创建文件，
#    创建1G多 再创建失败，移动父目录所有文件到子目录，删除子目录下面的所有文件
#    检测移动和删除操作后，已使用量和规则是否都生效
# @steps:
#    1.创建目录FILENAME/nesting1_1
#    2.创建目录FILENAME配额,硬阈值1G 等待配额状态为work
#    3.创建子目录FILENAME/nesting1_1配额,硬阈值1G,等待配额状态为work
#    4.父目录创建512M文件，预期total_size=512M
#    5.将父目录下面的所有文件移动到子目录
#    6.等待10s，待父目录、子目录规则都为work状态
#    7.检测配额已使用量在移动后统计是否准确 预期父目录512M，子目录512M
#    8.删除子目录下面的文件，等待10s，查看删除操作后的父目录和子目录的已使用量是否准确
# @changelog：
#################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
SCRIPT_PATH = os.path.join(quota_common.QUOTA_PATH, FILE_NAME)           # /mnt/volume1/qouta_test_dir/quota_11_0_3_1
LARGE_BS = random.choice([True, False])   # True大文件，False:小文件
FILE_SIZE_HALF_1G = 536870912


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

    log.info("2> 创建父目录配额,硬阈值1G  等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir0,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_1G,
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

    log.info("4> 父目录创建512M多文件，预期total_size=1G")
    if LARGE_BS:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir0, 1, 512, 'a', quota_id=quota_id_lst[0])
    else:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir0, 512, 1, 'a', quota_id=quota_id_lst[0])
    dir0_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, dir0)
    if dir0_size != FILE_SIZE_HALF_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (dir0, dir0_size)

    log.info("5> 将父目录下面的所有文件移动到子目录")
    cmd = "mv %s*a* %s" % (dir0+"/", dir1_1)
    rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "mv failed!")

    log.info("6> 等待10s，待父目录、子目录规则都为work状态")
    log.info("time.sleep(10s)")
    time.sleep(10)
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir0)
    common.judge_rc(rc, 0, "get quota info failed")

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir1_1)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("7> 检测配额已使用量在移动后统计是否准确 预期父目录512M，子目录512M")
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0,
                                                      quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir0_logical_capacity = get_quota_logical_used_capacity(quota_id_dir0)
    if dir0_logical_capacity != FILE_SIZE_HALF_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir0, dir0_logical_capacity)

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1,
                                                        quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir1_1_logical_capacity = get_quota_logical_used_capacity(quota_id_dir1_1)
    if dir1_1_logical_capacity != FILE_SIZE_HALF_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir1_1, dir1_1_logical_capacity)
    log.info("父目录已使用量(预计512M)：%s 子目录已使用量(预计512M)：%s"
             % (dir0_logical_capacity, dir1_1_logical_capacity))

    log.info("8> 删除子目录下面的文件")
    dir1_1_rm = os.path.join(dir1_1, '*')
    rc, stdout = common.rm_exe(common.SYSTEM_IP, dir1_1_rm)
    common.judge_rc(rc, 0, "rm failed!")
    log.info("8.1> 等待10s，查看删除操作后的父目录和子目录的已使用量是否准确")
    time.sleep(10)
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0,
                                                      quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir0_logical_capacity = get_quota_logical_used_capacity(quota_id_dir0)
    if dir0_logical_capacity != 0:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir0, dir0_logical_capacity)

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1,
                                                        quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir1_1_logical_capacity = get_quota_logical_used_capacity(quota_id_dir1_1)
    if dir1_1_logical_capacity != 0:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir1_1, dir1_1_logical_capacity)
    log.info("8.2> 删除操作后检查：父目录(预计0):%s 子目录(预计0):%s" %
             (dir0_logical_capacity, dir1_1_logical_capacity))

    """判断rc_lst"""
    if rc_lst != {}:
        log.info(rc_lst)
        for i in rc_lst:
            log.info("check point in line : %s is about :%s " % (i, rc_lst[i]))
        log.info('If there are many lines, you may only need to look at the first line.')
        common.except_exit("some check point failed")


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


def main():
    prepare_clean.quota_test_prepare(FILE_NAME)
    case()
    prepare_clean.quota_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)

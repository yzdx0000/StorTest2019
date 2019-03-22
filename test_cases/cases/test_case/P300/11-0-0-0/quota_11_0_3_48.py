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
# Date: 2018-10-15
# @summary：
#    对父目录a创建硬阈值配额1000，修改父目录阈值为2000
#    创建子目录b硬阈值为1000，在父目录下创建文件1000个
#    移动父目录中文件到子目录，查看移动后配额规则是否生效
# @steps:
#    1.创建目录FILENAME/nesting1_1
#    2.创建目录FILENAME配额,硬阈值1000 等待配额状态为work，修改父目录阈值为2000
#    3.创建子目录FILENAME/nesting1_1配额,硬阈值1000,等待配额状态为work
#    4.父目录创建1000个文件，预期total_inode=1001(写入数据前：chkmulti检测)
#    5.移动FILENAME文件到nesting1_1下
#    6.等待10s，待所有规则都为work状态
#    7.检测文件已使用量在移动后统计是否准确 FILENAME预期1001 nesting1_1预期1000
#    8.查看移动后，配额规则是否还生效(写入数据前：chkmulti检测)
# @changelog：
#################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
SCRIPT_PATH = os.path.join(quota_common.QUOTA_PATH, FILE_NAME)           # /mnt/volume1/qouta_test_dir/quota_11_0_3_1


def case():
    log.info("case begin ")
    rc_lst = {}
    log.info("1.创建父目录FILENAME")
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

    log.info("2.1> 修改子目录FILENAME配额,硬阈值2000,等待配额状态为work")
    rc, pscli_info = quota_common.update_one_quota(id=quota_id,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT,
                                                   filenr_hard_threshold=2000)
    common.judge_rc(rc, 0, "update_quota_failed!!")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("3> 创建子目录FILENAME/nesting1_1配额,硬阈值1000,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir1_1,
                                                   filenr_hard_threshold=1000,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir1_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("4> 父目录创建1000个文件，预期total_inode=1001")
    log.info("写入数据前：chkmulti检测")
    quota_common.chkmult_client_all_dir_on_path(dir0)
    quota_common.creating_files(quota_common.CLIENT_IP_1, dir0, 1000, 1, 'a', quota_id=quota_id_lst[0])
    dir0_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir0)
    if dir0_inode != 1001:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir0, dir0_inode)

    log.info("5> 移动FILENAME文件到nesting1_1下")
    cmd = "mv %s*a* %s" % (dir0 + "/", dir1_1)
    rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "mv failed!")

    log.info("6> 等待10s，待所有规则都为work状态")
    log.info("time.sleep(10s)")
    time.sleep(10)
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0,
                                                      quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir0)
    common.judge_rc(rc, 0, "get quota info failed")

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir1_1)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("7> 检测文件已使用量在移动后统计是否准确 FILENAME预期1001 nesting1_1预期1000")
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0,
                                                      quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir0_filenr_used_nr = get_quota_filenr_used_nr(quota_id_dir0)
    if dir0_filenr_used_nr != 1001:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir0, dir0_filenr_used_nr)

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1,
                                                        quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir1_1_filenr_used_nr = get_quota_filenr_used_nr(quota_id_dir1_1)
    if dir1_1_filenr_used_nr != 1000:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir1_1, dir1_1_filenr_used_nr)
    log.info("7>  FILENAME(预期1000):%s  nesting1_1(预期1000)：%s" % (dir0_filenr_used_nr, dir1_1_filenr_used_nr))

    log.info('8>查看移动后，配额规则是否还生效')
    log.info('8.1> FILENAME下再写1100预期2000')
    log.info("写入数据前：chkmulti检测")
    quota_common.chkmult_client_all_dir_on_path(dir0)
    quota_common.creating_files(quota_common.CLIENT_IP_2, dir0, 1100, 1, 'mv_a', quota_id=quota_id_lst[0])
    dir0_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir0)
    if dir0_inode != 2000:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir0, dir0_inode)
    log.info('8.2> nesting1_1下再写失败文件失败预期1000')
    log.info("写入数据前：chkmulti检测")
    quota_common.chkmult_client_all_dir_on_path(dir0)
    quota_common.creating_files(quota_common.CLIENT_IP_2, dir1_1, 10, 1, 'mv_a', quota_id=quota_id_lst[1])
    dir1_1_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_2, dir1_1)
    if dir1_1_inode != 1000:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_1, dir1_1_inode)

    """判断rc_lst"""
    if rc_lst != {}:
        log.info(rc_lst)
        for i in rc_lst:
            log.info("check point in line : %s is about :%s " % (i, rc_lst[i]))
        log.info('If there are many lines, you may only need to look at the first line.')
        common.except_exit("some check point failed")


def get_quota_filenr_used_nr(quota_id):
    """
    author:liyi
    date:2018-10-12
    description:获取文件使用个数
    :return:
    """
    rc, stdout = quota_common.get_one_quota_info(quota_id)
    common.judge_rc(rc, 0, "get_one_quota_info failed")
    list_quotas = stdout["result"]["quotas"]
    for quota in list_quotas:
            filenr_used_nr = quota["filenr_used_nr"]
            return filenr_used_nr


def main():
    prepare_clean.quota_test_prepare(FILE_NAME)
    case()
    prepare_clean.quota_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)
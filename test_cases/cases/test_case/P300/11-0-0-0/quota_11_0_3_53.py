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
import nas_common
#################################################################
#
# Author: liyi
# Date: 2018-10-15
# @summary：
#    用户：硬阈值配额3000，创建3个子目录配额硬阈值为1000，
#    3个子目录下各写1001个文件，删除nesting1_1下的文件，
#    移动nesting1_2下文件到nesting1_1下，查看移动后配额规则是否生效
# @steps:
#    1.创建用户用户组
#    2.创建目录FILENAME/nesting1_1  nesting1_2  nesting1_3
#    3.创建目录FILENAME配额,硬阈值3000 等待配额状态为work
#    4.创建子目录FILENAME/nesting1_x配额,硬阈值1000,等待配额状态为work
#    5.三个子目录下各写1001个文件
#    6.删除nesting1_1下的文件
#    7.移动nesting1_2下文件到nesting1_1下
#    8.等待10s，待所有规则都为work状态
#    9.检测文件已使用量在移动后统计是否准确
#    10.查看移动后，配额规则是否还生效
#    11.检测文件已使用量统计是否准确
# @changelog：
#################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
SCRIPT_PATH = os.path.join(quota_common.QUOTA_PATH, FILE_NAME)           # /mnt/volume1/qouta_test_dir/quota_11_0_3_1


def case():
    log.info("case begin ")
    rc_lst = {}

    log.info("1> 创建用户，用户组")
    node_ids = nas_common.get_node_ids()
    pscli_info = nas_common.create_access_zone(node_ids=node_ids, name=quota_common.QUOTA_ACCESS_ZONE)
    common.judge_rc(pscli_info['err_no'], 0, "create_access_zone failed")
    access_zone_id = pscli_info['result']
    pscli_info = nas_common.enable_nas(access_zone_id=access_zone_id)
    common.judge_rc(pscli_info['err_no'], 0, "enable_nas failed")
    pscli_info = nas_common.get_access_zones(ids=access_zone_id)
    auth_provider_id = pscli_info["result"]["access_zones"][0]["auth_provider_id"]
    pscli_info = nas_common.create_auth_group(auth_provider_id=auth_provider_id, name=quota_common.QUOTA_GROUP)
    primary_group_id = pscli_info['result']
    pscli_info = nas_common.create_auth_user(auth_provider_id, quota_common.QUOTA_USER, '111111', primary_group_id)
    user_id = pscli_info['result']

    log.info("2> 创建目录FILENAME/nesting1_1    nesting1_2  nesting1_3")
    quota_id_lst = []
    dir0 = SCRIPT_PATH
    dir1_ = []
    for i in range(3):
        dir1_.append(os.path.join(dir0, 'nesting1_%s' % (i+1)))

    create_quota_dir0 = os.path.join(get_config.get_one_volume_name() + ':', quota_common.QUOTA_PATH_BASENAME, os.path.basename(dir0))
    log.info(create_quota_dir0)

    for dir in dir1_:
        quota_common.creating_dir(quota_common.NOTE_IP_1, dir)

    create_quota_dir1_ = []
    for i in range(3):
        create_quota_dir1_.append(os.path.join(create_quota_dir0, os.path.basename(dir1_[i])))

    log.info("3> 创建父目录配额,硬阈值3000 等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir0,
                                                   auth_provider_id=auth_provider_id, user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   filenr_hard_threshold=3000,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_USER, u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("4> 创建三个子目录配额,硬阈值1000 等待配额状态为work")
    for i in range(3):
        rc, pscli_info = quota_common.create_one_quota(create_quota_dir1_[i],
                                                       auth_provider_id=auth_provider_id,
                                                       user_type=quota_common.TYPE_USER,
                                                       user_or_group_name=quota_common.QUOTA_USER,
                                                       filenr_hard_threshold=1000,
                                                       filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
        common.judge_rc(rc, 0, "create  quota failed")
        rc, quota_id = quota_common.get_one_quota_id(create_quota_dir1_[i], quota_common.TYPE_USER, u_or_g_name=quota_common.QUOTA_USER)
        common.judge_rc(rc, 0, "get_one_quota_id failed")
        quota_id_lst.append(quota_id)
        rc = quota_common.wait_quota_work(quota_id)
        common.judge_rc(rc, 0, "get quota info failed")

    log.info('5> 三个子目录下各写1001个文件')
    for i in range(3):
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, dir1_[i], 1001, 1,
                                                                '%c' % (i+97), quota_common.QUOTA_USER,
                                                                quota_id=quota_id_lst[i+1])
    log.info("6> 删除nesting1_1下的文件")
    quota_true_path = os.path.join(dir1_[0], "*")  # /mnt/volume1/qouta_test_dir/xxx
    common.rm_exe(common.SYSTEM_IP, quota_true_path)

    log.info("7> 移动nesting1_2下文件到nesting1_1下")
    cmd = "mv %s* %s" % (dir1_[1] + "/", dir1_[0])
    rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "mv failed!")

    log.info("8> 等待10s，待所有规则都为work状态")
    log.info("延时10s")
    time.sleep(10)
    quota_common.wait_quota_work_after_mv(create_quota_dir0, quota_common.TYPE_USER)
    quota_common.wait_quota_work_after_mv(create_quota_dir1_[0], quota_common.TYPE_USER)
    quota_common.wait_quota_work_after_mv(create_quota_dir1_[1], quota_common.TYPE_USER)

    log.info("9> 检测文件已使用量在移动后统计是否准确")
    rc, quota_id_dir1_0 = quota_common.get_one_quota_id(create_quota_dir1_[0],
                                                        quota_common.TYPE_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id_dir1_0)
    if filenr_used_nr != 1000:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir0, filenr_used_nr)

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_[1],
                                                        quota_common.TYPE_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir1_1_filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id_dir1_1)
    if dir1_1_filenr_used_nr != 0:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir1_[1], dir1_1_filenr_used_nr)
    log.info("9>  nesting1_1(预期1000):%s  nesting1_2(预期0)：%s" % (filenr_used_nr, dir1_1_filenr_used_nr))

    log.info('10>查看移动后，配额规则是否还生效')
    log.info('10.1> nesting1_2下再写1000')
    quota_common.chkmult_client_all_dir_on_path(dir1_[1])
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, dir1_[1], 1001, 1, 'a', quota_common.QUOTA_USER,quota_id=quota_id_lst[1])
    dir_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, dir1_[1], quota_common.QUOTA_USER)
    if dir_inode != 1000:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_[1], dir_inode)
    log.info('10.2> FILENAME下再写1个数据，预计共3000个')
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, dir0, 1, 1, 'F_mv_a',  quota_common.QUOTA_USER,quota_id=quota_id_lst[0])
    dir0_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, dir0, quota_common.QUOTA_USER)
    if dir0_inode != 3000:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir0, dir0_inode)

    log.info("11> 检测文件已使用量统计是否准确")
    log.info("11.1> 检测文件FILENAME已使用量预计3000")
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0,
                                                        quota_common.TYPE_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    filenr_used_nr_dir0 = quota_common.get_quota_filenr_used_nr(quota_id_dir0)
    if filenr_used_nr_dir0 != 3000:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir0, filenr_used_nr_dir0)
    log.info("11.2> 检测nesting1_1文件已使用量预计1000")
    rc, quota_id_dir1_0 = quota_common.get_one_quota_id(create_quota_dir1_[0],
                                                        quota_common.TYPE_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id_dir1_0)
    if filenr_used_nr != 1000:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir1_[0], filenr_used_nr)
    log.info("11.3> 检测nesting1_2文件已使用量预计1000")
    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_[1],
                                                        quota_common.TYPE_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir1_1_filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id_dir1_1)
    if dir1_1_filenr_used_nr != 1000:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir1_[1], dir1_1_filenr_used_nr)

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
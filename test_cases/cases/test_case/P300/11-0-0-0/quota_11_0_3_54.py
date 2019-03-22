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
#    用户 :
#    父目录软阈值2000，宽限时间60秒，子目录软阈值1000，宽限时间60秒，子目录创建1001文件开始计时，
#    过期后子目录无法创建文件，移动子目录下面文件到父目录，检测移动操作后，规则是否生效
#    子目录下面写1001个文件，等待60s后，父和子都无法继续写入了，父预计2002个，子1001个
# @steps:
#    1.创建用户用户组
#    2.创建目录FILENAME/nesting1_1
#    3.创建目录FILENAME配额,软阈值2000 宽限时间60秒 等待配额状态为work
#    4.创建子目录FILENAME/nesting1_1/配额,子目录软阈值1000，宽限时间60秒 等待配额状态为work
#    5.子目录创建1001文件开始计时，过期后子目录无法创建文件
#    6.移动nesting1_1下文件到FILENAME下
#    7.等待10s，待所有规则都为work状态
#    8.检测文件已使用量在移动后统计是否准确
#    9.查看移动后，配额规则是否还生效
# @changelog：
#################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
SCRIPT_PATH = os.path.join(quota_common.QUOTA_PATH, FILE_NAME)           # /mnt/volume1/qouta_test_dir/quota_11_0_3_1


def case():
    log.info("case begin" )
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
    ob_node = common.Node()
    log.info("2> 创建目录FILENAME/nesting1_1")
    quota_id_lst = []
    dir0 = SCRIPT_PATH
    dir1_1 = os.path.join(dir0, 'nesting1_1')
    quota_common.creating_dir(quota_common.NOTE_IP_1, dir1_1)

    create_quota_dir0 = os.path.join(get_config.get_one_volume_name() + ':', quota_common.QUOTA_PATH_BASENAME, os.path.basename(dir0))
    log.info(create_quota_dir0)
    create_quota_dir1_1 = os.path.join(create_quota_dir0, os.path.basename(dir1_1))

    log.info("3> 创建父目录配额,软阈值2000 宽限时间60秒 等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir0,
                                                   auth_provider_id=auth_provider_id, user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   filenr_soft_threshold=2000, filenr_grace_time=60,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_USER, u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("4> 创建子目录FILENAME/nesting1_1配额,子目录软阈值1000，宽限时间60秒 等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir1_1,
                                                   auth_provider_id=auth_provider_id, user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   filenr_soft_threshold=1000, filenr_grace_time=60,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir1_1, quota_common.TYPE_USER, u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("5> 子目录创建1001文件开始计时，过期后子目录无法创建文件")
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, dir1_1, 1001, 1, 'a', quota_common.QUOTA_USER,quota_id=quota_id_lst[1])
    dir_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, dir1_1, quota_common.QUOTA_USER)
    if dir_inode != 1001:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_1, dir_inode)
    rc, qmgrid = quota_common.get_qmgr_id(quota_id_lst[0])
    common.judge_rc(rc, 0, "get_qmgr_id failed")
    qmgr_ip = ob_node.get_node_ip_by_id(qmgrid)
    '''等待超过超期时间'''
    log.info('wait 75s')
    time.sleep(75)
    quota_common.wait_soft_threshold_over_time(qmgr_ip, quota_id_lst[1], quota_common.SOFT_TIME_FILENR)
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_2, dir1_1, 1, 1, 'b',quota_common.QUOTA_USER, quota_id=quota_id_lst[1])
    dir_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_2, dir1_1, quota_common.QUOTA_USER)
    if dir_inode != 1001:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_1, dir_inode)

    log.info("6> 移动nesting1_1下文件到FILENAME下")
    cmd = "mv %s*a* %s" % (dir1_1 + "/", dir0)
    rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "mv failed!")

    log.info("7> 等待10s，待所有规则都为work状态")
    log.info("延时10s")
    time.sleep(10)
    quota_common.wait_quota_work_after_mv(create_quota_dir0, quota_common.TYPE_USER)
    quota_common.wait_quota_work_after_mv(create_quota_dir1_1, quota_common.TYPE_USER)

    log.info("8> 检测文件已使用量在移动后统计是否准确")
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0,
                                                      quota_common.TYPE_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir0_filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id_dir0)
    if dir0_filenr_used_nr != 1001:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir0, dir0_filenr_used_nr)

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1,
                                                        quota_common.TYPE_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir1_1_filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id_dir1_1)
    if dir1_1_filenr_used_nr != 0:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir1_1, dir1_1_filenr_used_nr)
    log.info("8>  FILENAME(预期1001):%s  nesting1_1(预期0)：%s" % (dir0_filenr_used_nr, dir1_1_filenr_used_nr))

    log.info('9>查看移动后，配额规则是否还生效')
    log.info("9.1> 子目录创建1001个文件，子目录父目录都超过软阈值")
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, dir1_1, 1001, 1, 'a', quota_common.QUOTA_USER,quota_id=quota_id_lst[1])
    dir_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, dir1_1, quota_common.QUOTA_USER)
    if dir_inode != 1001:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_1, dir_inode)
    rc, qmgrid = quota_common.get_qmgr_id(quota_id_lst[0])
    common.judge_rc(rc, 0, "get_qmgr_id failed")
    '''等待超过超期时间'''
    log.info('wait 75s')
    time.sleep(75)
    log.info("9.2> 60s后，不能继续写入数据，子目录预计1001个，父目录预计2002个")
    quota_common.wait_soft_threshold_over_time(qmgr_ip, quota_id_lst[1], quota_common.SOFT_TIME_FILENR)
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, dir1_1, 1, 1, 'N_mv_a', quota_common.QUOTA_USER,quota_id=quota_id_lst[1])
    dir_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, dir1_1, quota_common.QUOTA_USER)
    if dir_inode != 1001:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_1, dir_inode)

    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, dir0, 1, 1, 'F_mv_a',  quota_common.QUOTA_USER,quota_id=quota_id_lst[0])
    dir0_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, dir0, quota_common.QUOTA_USER)
    if dir0_inode != 2002:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir0, dir0_inode)

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

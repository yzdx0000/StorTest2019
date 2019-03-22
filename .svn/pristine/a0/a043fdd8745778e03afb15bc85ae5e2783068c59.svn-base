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
# Author: chenjy1
# Date: 2018-09-03
# @summary：
#    用户 对父目录a创建硬阈值配额3G，在a下创建目录b硬阈值配额2G，在目录b创建目录c硬阈值配额1G，
#    在目录c下创建文件，限制size为1G，在目录b下创建文件，限制size为2G，
#    在目录a下创建文件，限制size3G
# @steps:
#    1.创建用户用户组
#    2.创建目录FILENAME/nesting1_1/nesting2_1/
#    3.创建目录FILENAME配额,硬阈值3G 等待配额状态为work
#    4.创建子目录FILENAME/nesting1_1/配额,硬阈值2G,等待配额状态为work
#    5.创建子目录FILENAME/nesting1_1/nesting2_1配额,硬阈值1G,等待配额状态为work
#    6.子目录nesting2_1下写个1100M文件预期total_size=1G
#    7.子目录nesting1_1下写1100M个文件预期total_size=2G
#    8.父目录FILENAME创建1100M个文件，预期total_size=3G
# @changelog：
#################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
SCRIPT_PATH = os.path.join(quota_common.QUOTA_PATH, FILE_NAME)           # /mnt/volume1/qouta_test_dir/quota_11_0_3_1
LARGE_BS = random.choice([True, False])   # True大文件，False:小文件

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

    log.info("2> 创建目录FILENAME/nesting1_1/nesting2_1")
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

    log.info("3> 创建父目录配额,硬阈值3G 等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir0,
                                                   auth_provider_id=auth_provider_id, user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_3G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_USER, u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("4> 创建子目录FILENAME/nesting1_1/配额,硬阈值2G,等待配额状态为work")

    rc, pscli_info = quota_common.create_one_quota(create_quota_dir1_1,
                                                   auth_provider_id=auth_provider_id, user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_2G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir1_1,quota_common.TYPE_USER, u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info('5> 创建子目录FILENAME/nesting1_1/nesting2_1配额,硬阈值1G,等待配额状态为work')
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir2_1,
                                                   auth_provider_id=auth_provider_id, user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_1G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir2_1, quota_common.TYPE_USER, u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info('6> 子目录nesting2_1下写个1100M文件预期total_size=1G')
    if LARGE_BS:
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, dir2_1, 1, 1100, 'a',
                                                                quota_common.QUOTA_USER, quota_id=quota_id_lst[2])
    else:
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, dir2_1, 1100, 1, 'a',
                                                                quota_common.QUOTA_USER, quota_id=quota_id_lst[2])
    dir2_1_size = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, dir2_1, quota_common.QUOTA_USER)
    if dir2_1_size != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (dir2_1, dir2_1_size)

    log.info('7> 子目录nesting1_1下写个1100M文件预期total_size=2G')
    if LARGE_BS:
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_2, dir1_1, 1, 1100, 'b',
                                                                quota_common.QUOTA_USER, quota_id=quota_id_lst[1])
    else:
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_2, dir1_1, 1100, 1, 'b',
                                                                quota_common.QUOTA_USER, quota_id=quota_id_lst[1])
    dir1_1_size = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_2, dir1_1,  quota_common.QUOTA_USER)
    if dir1_1_size != quota_common.FILE_SIZE_2G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (dir1_1, dir1_1_size)

    log.info('8> 父目录下写个1100M文件预期total_size=3G')
    if LARGE_BS:
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_3, dir0, 1, 1100, 'c',
                                                                quota_common.QUOTA_USER, quota_id=quota_id_lst[0])
    else:
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_3, dir0, 1100, 1, 'c',
                                                                quota_common.QUOTA_USER, quota_id=quota_id_lst[0])
    dir0_size = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_3, dir0, quota_common.QUOTA_USER)
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
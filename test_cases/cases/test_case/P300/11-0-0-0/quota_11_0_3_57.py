# -*-coding:utf-8 -*
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
# Date: 2018-10-16
# @summary：
#    用户：
#    对父目录a创建硬阈值配额2G，创建子目录b硬阈值为1G，子目录写truncate1G
#    将子目录文件移动到父目录下，查看移动后，配额规则是否生效
#    将父母录文件truncate到2G，父目录和子目录分别写数据，预计失败。
#  @steps:
#    1.创建用户用户组
#    2.创建目录FILENAME/nesting1_1
#    3.创建目录FILENAME配额,硬阈值2G 等待配额状态为work
#    4.创建子目录FILENAME/nesting1_1配额,硬阈值1G,等待配额状态为work
#    5.子目录truncate 1G文件，再写失败，预期total_size 1G
#    6.将子目录下面的部分文件移动到父目录
#    7.等待10s，待父目录、子目录规则都为work状态
#    8.检测配额已使用量在移动后统计是否准确 预期父目录1G，子目录0
#    9.查看移动后，配额规则是否还生效,父目录truncate到2G,父目录和子目录下再写文件失败
# @changelog：
#################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
SCRIPT_PATH = os.path.join(quota_common.QUOTA_PATH, FILE_NAME)  # /mnt/volume1/qouta_test_dir/quota_11_0_3_1
LARGE_BS = random.choice([True, False])  # True大文件，False:小文件


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

    log.info("2> 创建目录FILENAME/nesting1_1")
    quota_id_lst = []
    dir0 = SCRIPT_PATH
    dir1_1 = os.path.join(dir0, 'nesting1_1')
    quota_common.creating_dir(quota_common.NOTE_IP_1, dir1_1)

    create_quota_dir0 = os.path.join(get_config.get_one_volume_name() + ':', quota_common.QUOTA_PATH_BASENAME,
                                     os.path.basename(dir0))
    log.info(create_quota_dir0)
    create_quota_dir1_1 = os.path.join(create_quota_dir0, os.path.basename(dir1_1))

    log.info("3> 创建目录FILENAME配额,硬阈值2G 等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir0,
                                                   auth_provider_id=auth_provider_id, user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_2G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_USER,
                                                 u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("4> 创建子目录FILENAME/nesting1_1配额,硬阈值1G,等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir1_1,
                                                   auth_provider_id=auth_provider_id, user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   logical_hard_threshold=quota_common.FILE_SIZE_1G,
                                                   logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir1_1, quota_common.TYPE_USER,
                                                 u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("5> 子目录truncate 1G文件，再写失败，预期total_size 1G")
    cmd = ("cd %s; su quota_user -c \"truncate -s 1G file_1\";") % dir1_1
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    common.judge_rc(rc, 0, "truncate failed!")
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, dir1_1, 1, 1, 'a',
                                                                quota_common.QUOTA_USER, quota_id=quota_id_lst[1])
    dir1_1_size = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, dir1_1, quota_common.QUOTA_USER)
    if dir1_1_size != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (dir1_1, dir1_1_size)

    log.info("6> 将子目录下面的部分文件移动到父目录")
    cmd = "mv %s* %s" % (dir1_1 + "/", dir0)
    rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "mv failed!")

    log.info("7> 等待10s，待父目录、子目录规则都为work状态")
    log.info("time.sleep(10s)")
    time.sleep(10)
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0,
                                                      quota_common.TYPE_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir0)

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1,
                                                        quota_common.TYPE_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc = quota_common.wait_quota_work(quota_id_dir1_1)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("8> 检测配额已使用量在移动后统计是否准确 预期父目录1G，子目录0")
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0,
                                                      quota_common.TYPE_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir0_logical_capacity = quota_common.get_quota_logical_used_capacity(quota_id_dir0)
    if dir0_logical_capacity != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir0, dir0_logical_capacity)

    rc, quota_id_dir1_1 = quota_common.get_one_quota_id(create_quota_dir1_1,
                                                        quota_common.TYPE_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir1_1_logical_capacity = quota_common.get_quota_logical_used_capacity(quota_id_dir1_1)
    if dir1_1_logical_capacity != 0:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s total_size:%s' % (dir1_1, dir1_1_logical_capacity)
    log.info("8> 父目录(预期1G)：%s，子目录（预期0）：%s" % (dir0_logical_capacity, dir1_1_logical_capacity))

    log.info('9>查看移动后，配额规则是否还生效')
    log.info("9.1> 父目录truncate到2G")
    cmd = ("cd %s; su quota_user -c \"truncate -s 2G file_1\";") % SCRIPT_PATH
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    common.judge_rc(rc, 0, "truncate failed!")
    log.info("9.2> 父目录再次创建文件，预期失败")
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, dir0, 1, 1, 'after_mv',
                                                                quota_common.QUOTA_USER, quota_id=quota_id_lst[0])
    dir0_size = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, dir0, quota_common.QUOTA_USER)
    if dir0_size != quota_common.FILE_SIZE_2G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (dir0, dir0_size)

    log.info("9.3> 子目录创建文件，预期失败")
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, dir1_1, 1, 1, 'after_mv',
                                                                quota_common.QUOTA_USER, quota_id=quota_id_lst[1])
    dir1_1_size = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, dir1_1, quota_common.QUOTA_USER)
    if dir1_1_size != 0:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s ' % (dir1_1, dir1_1_size)

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

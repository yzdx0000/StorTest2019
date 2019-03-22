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
# Date: 2018-10-24
# @summary：
#    用户:目录配额  父目录硬阈值配额1000，创建500个属主为quota_user的文件
#    再创建100个属主为root的文件，预计统计数为500；改变属主为quota_user的
#    文件为root属主；查看统计是否正确；删除底层所有文件，查看规则是否生效；
# @steps:
#    1.创建用户，用户组
#    2.创建目录FILENAME
#    3.创建目录FILENAME配额,硬阈值1000 等待配额状态为work
#    4.父目录下创建500个属主为quota_user的文件
#    5.父目录下创建100个属主为root的文件
#    6.将父目录下属主为quota_user的文件改变为属主为root的文件,延时3s
#    7.查看父目录的已使用量应为0
#    8.删除父目录的所有文件
#    9.查看规则是否生效，父目录下创建1100个属主为quota_user的文件
# @changelog：
#################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
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

    log.info("2> 创建目录FILENAME")
    quota_id_lst = []
    dir0 = SCRIPT_PATH
    create_quota_dir0 = os.path.join(get_config.get_one_volume_name() + ':', quota_common.QUOTA_PATH_BASENAME, os.path.basename(dir0))
    log.info(create_quota_dir0)

    log.info("3> 创建父目录配额,硬阈值1000 等待配额状态为work")
    rc, pscli_info = quota_common.create_one_quota(create_quota_dir0,
                                                   auth_provider_id=auth_provider_id, user_type=quota_common.TYPE_USER,
                                                   user_or_group_name=quota_common.QUOTA_USER,
                                                   filenr_hard_threshold=1000,
                                                   filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT)
    common.judge_rc(rc, 0, "create  quota failed")
    rc, quota_id = quota_common.get_one_quota_id(create_quota_dir0, quota_common.TYPE_USER, u_or_g_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    quota_id_lst.append(quota_id)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info('4> 父目录下创建500个属主为quota_user的文件')
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, dir0, 500, 1, 'quota_user',
                                                            quota_common.QUOTA_USER)
    dir0_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, dir0,quota_common.QUOTA_USER)
    if dir0_inode != 500:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s expect: %s user_total_inode: %s ' % (dir0, 500, dir0_inode)

    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0,
                                                      quota_common.TYPE_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir0_filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id_dir0)
    if dir0_filenr_used_nr != 500:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s expect:%s total_size:%s' % (dir0, 500, dir0_filenr_used_nr)

    log.info('5> 父目录下创建100个属主为root的文件')
    quota_common.creating_files(quota_common.CLIENT_IP_1, dir0, 100, 1, 'root')

    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0,
                                                      quota_common.TYPE_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir0_filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id_dir0)
    if dir0_filenr_used_nr != 500:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s expect:%s total_size:%s' % (dir0, 500, dir0_filenr_used_nr)

    log.info('6> 将父目录下属主为quota_user的文件改变为属主为root的文件,延时5s')
    cmd = "cd %s;chgrp %s *quota_user* " % (dir0, "root")
    rc, stdout = common.run_command(quota_common.NOTE_IP_1,cmd)
    common.judge_rc(rc, 0, "chgrp failed!!")
    cmd = "cd %s;chown %s *quota_user* " % (dir0, "root")
    rc, stdout = common.run_command(quota_common.NOTE_IP_1,cmd)
    common.judge_rc(rc, 0, "chown failed!!")
    time.sleep(5)
    rc = quota_common.wait_quota_work(quota_id_dir0)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info('7> 查看父目录的已使用量应为0')
    rc, quota_id_dir0 = quota_common.get_one_quota_id(create_quota_dir0,
                                                      quota_common.TYPE_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    dir0_filenr_used_nr = quota_common.get_quota_filenr_used_nr(quota_id_dir0)
    if dir0_filenr_used_nr != 0:
        rc_lst[sys._getframe().f_lineno] = 'dir:%s expect:%s total_size:%s' % (dir0, 0, dir0_filenr_used_nr)

    log.info('8> 删除父目录的所有文件')
    rm_dir = os.path.join(dir0, "*")
    rc, stdout = common.rm_exe(quota_common.NOTE_IP_1, rm_dir)
    common.judge_rc(rc, 0, "rm failed!")
    dir0_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir0)
    if dir0_inode != 0:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s expect: %s user_total_inode: %s ' % (dir0, 0, dir0_inode)

    log.info('9> 查看规则是否生效，父目录下创建1100个属主为quota_user的文件')
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, dir0, 1100, 1, 'quota_user',
                                                            quota_common.QUOTA_USER)
    dir0_inode = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, dir0, quota_common.QUOTA_USER)
    if dir0_inode != 1000:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s expect: %s user_total_inode: %s ' % (dir0, 1000, dir0_inode)

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

#-*-coding:utf-8 -*
import os
import time
import random
import commands

import utils_path
import common
import quota_common
import log
import get_config
import prepare_clean
import sys
#################################################################
# Author: liyi
# Date: 2018-10-31
# @summary：
#   升级前在各个卷中写入部分数据
# @notice:
#   本脚本执行前提：需要先用quota_11_0_3_66.py创建好N个卷
#   本脚本需要与quota_upgrade_after_1.py配合使用
# @steps:
#    1.volume_1多客户端创建文件2G
#    2.volume_2创建文件1G
#    3.volume_3创建文件1G
# @changelog：
#################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
ip_list = get_config.get_allclient_ip()
mnt_path = get_config.get_mount_paths()  # /mnt/volume
create_quota_dir = quota_common.VOLUME_NAME+":/"


def case():
    """
    author:liyi
    date:2018-10-31
    description: 升级前对各个卷写入数据
    :return:
    """
    log.info("case begin ")
    rc_lst = {}
    obj_storage = common.Storagepool()
    rc, storage_pool_id = obj_storage.get_storagepool_id(storage_pool_name="stor")
    common.judge_rc(rc, 0, "get_storage_pool_id faild!")
    obj_volume = common.Volume()
    volume_name_1 = quota_common.VOLUME_NAME + "_1"
    volume_name_2 = quota_common.VOLUME_NAME + "_2"
    volume_name_3 = quota_common.VOLUME_NAME + "_3"

    volume_id_1 = obj_volume.get_volume_id(volume_name_1)
    volume_id_2 = obj_volume.get_volume_id(volume_name_2)
    volume_id_3 = obj_volume.get_volume_id(volume_name_3)

    mnt_path_1 = get_config.get_mount_paths()[0] + "_1" #/mnt/volume_1
    mnt_path_2 = get_config.get_mount_paths()[0] + "_2" #/mnt/volume_2
    mnt_path_3 = get_config.get_mount_paths()[0] + "_3" #/mnt/volume_3

    log.info("1> volume_1多客户端创建文件2G")
    quota_common.creating_files_for_volume_capacity(quota_common.CLIENT_IP_1,
                                                    quota_path=mnt_path_1,
                                                    file_count=1,
                                                    file_size=1024,
                                                    file_name_identifier="before_a",
                                                    volume_id=volume_id_1)
    quota_common.creating_files_for_volume_capacity(quota_common.CLIENT_IP_2,
                                                    quota_path=mnt_path_1,
                                                    file_count=1024,
                                                    file_size=1,
                                                    file_name_identifier="before_b",
                                                    volume_id=volume_id_1)
    quota_common.creating_files_for_volume_capacity(quota_common.CLIENT_IP_2,
                                                    quota_path=mnt_path_1,
                                                    file_count=1,
                                                    file_size=1,
                                                    file_name_identifier="before_c",
                                                    volume_id=volume_id_1)
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, mnt_path_1)
    if dir_size != quota_common.FILE_SIZE_2G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s expect:%s' % \
                                           (mnt_path_1, dir_size, quota_common.FILE_SIZE_2G)

    log.info("2> volume_2创建文件1G")
    quota_common.creating_files_for_volume_capacity(quota_common.CLIENT_IP_1,
                                                    quota_path=mnt_path_2,
                                                    file_count=1,
                                                    file_size=1024,
                                                    file_name_identifier="before",
                                                    volume_id=volume_id_2)
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, mnt_path_2)
    if dir_size != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s expect:%s'\
                                           % (mnt_path_2, dir_size, quota_common.FILE_SIZE_1G)

    log.info("3> volume_3创建文件1G")
    quota_common.creating_files_for_volume_capacity(quota_common.CLIENT_IP_1,
                                                    quota_path=mnt_path_3,
                                                    file_count=1,
                                                    file_size=1024,
                                                    file_name_identifier="before",
                                                    volume_id=volume_id_3)
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, mnt_path_3)
    if dir_size != quota_common.FILE_SIZE_1G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s expect:%s' %\
                                           (mnt_path_3, dir_size,quota_common.FILE_SIZE_1G)

    """判断rc_lst"""
    if rc_lst != {}:
        log.info(rc_lst)
        for i in rc_lst:
            log.info("check point in line : %s is about :%s " % (i, rc_lst[i]))
        log.info('If there are many lines, you may only need to look at the first line.')
        common.except_exit("some check point failed")


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
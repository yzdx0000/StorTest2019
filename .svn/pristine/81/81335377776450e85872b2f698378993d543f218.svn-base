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
# Date: 2018-11-5
# @summary：
#   升级后，继续在卷中写入数据，查看规则是否生效
# @notice:
#   本脚本需要与quota_upgrade_before_1.py配合使用
# @steps:
#    1.升级前：volume_1多客户端文件2G；升级后：继续写入数据，预计写入失败
#    2.升级前：volume_2文件1G；升级后：继续写入1100M，预计2G
#    3.升级前: volume_3文件1G；升级后：删除之前文件，继续写入，预计共2G
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
ip_list = get_config.get_allclient_ip()
mnt_path = get_config.get_mount_paths()  # /mnt/volume
create_quota_dir = quota_common.VOLUME_NAME+":/"

def case():
    """
    author:liyi
    date:2018-11-5
    description: 升级后，对各个卷写入数据，验证配额规则是否在升级后依然生效
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

    log.info("1> 升级前：volume_1多客户端文件2G；升级后：继续写入数据，预计写入失败")
    quota_common.creating_files_for_volume_capacity(quota_common.CLIENT_IP_2,
                                                    quota_path=mnt_path_1,
                                                    file_count=5,
                                                    file_size=1,
                                                    file_name_identifier="after",
                                                    volume_id=volume_id_1)
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, mnt_path_1)
    if dir_size != quota_common.FILE_SIZE_2G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s expect:%s' % \
                                           (mnt_path_1, dir_size, quota_common.FILE_SIZE_2G)

    log.info("2> 升级前：volume_2文件1G；升级后：继续写入1100M，预计2G")
    quota_common.creating_files_for_volume_capacity(quota_common.CLIENT_IP_1,
                                                    quota_path=mnt_path_2,
                                                    file_count=1100,
                                                    file_size=1,
                                                    file_name_identifier="after",
                                                    volume_id=volume_id_2)
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, mnt_path_2)
    if dir_size != quota_common.FILE_SIZE_2G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s expect:%s'\
                                           % (mnt_path_2, dir_size, quota_common.FILE_SIZE_2G)

    log.info("3> 升级前: volume_3文件1G；升级后：删除之前文件，继续写入，预计共2G")
    log.info("3.1> 删除之前文件")
    rm_path = os.path.join(mnt_path_3, "*")
    rc, stdout = common.rm_exe(quota_common.NOTE_IP_1, rm_path)
    common.judge_rc(rc, 0, "rm failed!")

    log.info("3.2> 写2G多文件到volume_3，预计共2G")
    quota_common.creating_files_for_volume_capacity(quota_common.CLIENT_IP_1,
                                                    quota_path=mnt_path_3,
                                                    file_count=1,
                                                    file_size=1024,
                                                    file_name_identifier="after_a",
                                                    volume_id=volume_id_3)
    quota_common.creating_files_for_volume_capacity(quota_common.CLIENT_IP_2,
                                                    quota_path=mnt_path_3,
                                                    file_count=1100,
                                                    file_size=1,
                                                    file_name_identifier="after_b",
                                                    volume_id=volume_id_3)
    dir_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, mnt_path_3)
    if dir_size != quota_common.FILE_SIZE_2G:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_size: %s expect:%s' %\
                                           (mnt_path_3, dir_size,quota_common.FILE_SIZE_2G)

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
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
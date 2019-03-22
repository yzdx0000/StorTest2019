# -*-coding:utf-8 -*
# !/usr/bin/python

import os
import time

import utils_path
import common
import snap_common
import nas_common
import quota_common
import log
import get_config
import prepare_clean

# =================================================================================
#  latest update:2018-08-10                                                    =
#  Author:wanggl                                                           =
# =================================================================================
# 2018-08-10:
# Author：wanggl
# @summary：
#   目录配额中软链接做link
# @steps:
#   1、文件系统下创建目录dir1,dir1目录下创建50个文件；
#   2、创建file1的软连接ln -s slink file1；
#   3、创建这个软连接的硬链接ln hlink slink；
#   4、对目录dir创建目录配额；
#   5、5分钟后，df查看文件系统是否正常；
#
#

# changelog:


######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
volume_path = os.path.join(nas_common.BASE_NAS_PATH, FILE_NAME)             # /mnt/wangguanglin/cus_6_1_0_49
Private_clientIP1 = get_config.get_client_ip(0)
Private_clientIP2 = get_config.get_client_ip(1)
Private_clientIP3 = get_config.get_client_ip(2)


def case():

    log.info('1> 文件系统下创建目录cus_6_1_0_49,cus_6_1_0_49目录下创建50个文件')
    common.mkdir_path(Private_clientIP1, volume_path)
    cmd = "cd %s && for i in {1..50}; do dd if=/dev/zero of=file_$i bs=1M count=1; done" % volume_path
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'create file')
    file1 = os.path.join(volume_path, 'file1')

    log.info('2> 创建file1的软连接ln -s slink file1')
    slink = os.path.join(volume_path, 'slink')
    cmd = 'ln -s %s %s ' % (file1, slink)
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'create soft link')

    log.info('3> 创建这个软连接的硬链接ln hlink slink')
    hlink = os.path.join(volume_path, 'hlink')
    cmd = 'ln  %s %s ' % (slink, hlink)
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'create soft link')

    log.info('4> 对目录cus_6_1_0_49创建目录配额')
    path = os.path.basename(nas_common.BASE_NAS_PATH) + ':/' + FILE_NAME
    rc, check_result = quota_common.create_one_quota(path=path, filenr_quota_cal_type="QUOTA_COMPUTE")
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    time.sleep(20)
    rc, quota_info = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota info failed")
    pscli_file_nr = quota_info["result"]["quotas"][0]["filenr_used_nr"]
    if pscli_file_nr != 50:
        raise Exception("check quota failed")

    log.info('5> 5分钟后，df查看文件系统是否正常')
    time.sleep(10)
    cmd = 'df '
    rc, stdout = common.run_command(Private_clientIP1, cmd, timeout=10)
    common.judge_rc(rc, 0, 'df check volume')

    common.rm_exe(Private_clientIP1, volume_path)

    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.quota_test_clean(FILE_NAME)
    log.info('succeed!')


if __name__ == '__main__':
    common.case_main(main)
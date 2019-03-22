# -*-coding:utf-8 -*
# !/usr/bin/python

import os
import time
import commands
import json
import hashlib

import utils_path
import common
import snap_common
import nas_common

import random
import log
import shell
import get_config
import tool_use
import prepare_clean

# =================================================================================
#  latest update:2018-08-09                                                    =
#  Author:wanggl                                                           =
# =================================================================================
# 2018-08-09:
# Author：wanggl
# @summary：
#   快照中软链接做link
# @steps:
#   1、文件系统下创建目录dir1,dir1目录下创建50个文件；
#   2、创建file1的软连接ln -s slink file1；
#   3、创建这个软连接的硬链接ln hlink slink；
#   4、对目录dir创建快照，追加file1；
#   5、5分钟后，df查看文件系统是否正常；
#
#

# changelog:


######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/wangguanglin/snap/cus_6_1_0_50
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/cus_6_1_0_50

Private_clientIP1 = get_config.get_client_ip(0)
Private_clientIP2 = get_config.get_client_ip(1)
Private_clientIP3 = get_config.get_client_ip(2)


def case():

    log.info('1> 文件系统下创建目录cus_6_1_0_50,cus_6_1_0_50目录下创建50个文件')
    common.mkdir_path(Private_clientIP1, SNAP_TRUE_PATH)
    cmd = "cd %s && for i in {1..50}; do dd if=/dev/zero of=file_$i bs=1M count=1; done" % SNAP_TRUE_PATH
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'create file')
    file1 = os.path.join(SNAP_TRUE_PATH, 'file1')

    log.info('2> 创建file1的软连接ln -s slink file1')
    slink = os.path.join(SNAP_TRUE_PATH, 'slink')
    cmd = 'ln -s %s %s ' % (file1, slink)
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'create soft link')

    log.info('3> 创建这个软连接的硬链接ln hlink slink')
    hlink = os.path.join(SNAP_TRUE_PATH, 'hlink')
    cmd = 'ln  %s %s ' % (slink, hlink)
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'create soft link')

    log.info('4> 对目录cus_6_1_0_50创建快照，追加file1')
    snap_name = FILE_NAME + '_snapshot1'
    path = os.path.basename(snap_common.BASE_SNAP_PATH) + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    common.judge_rc(rc, 0, 'create snapshot')
    cmd = 'echo 11111111111111111 >> %s' % file1
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'append the file1')

    log.info('5> 5分钟后，df查看文件系统是否正常')
    time.sleep(10)
    rc, stdout = common.run_command(Private_clientIP1, cmd, timeout=10)
    common.judge_rc(rc, 0, 'df check volume')

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('succeed!')


if __name__ == '__main__':
    common.case_main(main)
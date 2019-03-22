# -*-coding:utf-8 -*
# !/usr/bin/python

import os
import time
import commands
import json
import hashlib
from multiprocessing import Process

import utils_path
import common
import snap_common
import nas_common
import quota_common
import random
import log
import shell
import get_config
import tool_use
import prepare_clean
import upgrade_common

# =================================================================================
#  latest update:2018-08-10                                                    =
#  Author:wanggl                                                           =
# =================================================================================
# 2018-08-10:
# Author：wanggl
# @summary：
#   升级后目录权限不一致
# @steps:
#   1、打开双分片，创建大量的数据和文件，权限644；
#   2、修改部分目录和文件的权限到755；
#   3、升级到最新的版本；
#   4、升级成功后，检查目录权限。
#
#

# changelog:


######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
volume_path = os.path.join(nas_common.BASE_NAS_PATH, FILE_NAME)             # /mnt/wangguanglin/cus_6_1_0_20
Private_clientIP1 = get_config.get_client_ip(0)
Private_clientIP2 = get_config.get_client_ip(1)
Private_clientIP3 = get_config.get_client_ip(2)


def case():

    log.info('1> 打开双分片，创建大量的数据和文件，权限644')
    common.mkdir_path(Private_clientIP1, volume_path)
    cmd = '/home/parastor/tools/set_subdir_layout  -n 2 -f %s' % volume_path
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'open two patch')
    cmd = "cd %s; for i in {1..100}; do dd if=/dev/zero of=file_$i bs=1M count=1; done" % volume_path
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'dd create many files')
    cmd = "cd %s; for i in {1..100}; do chmod 644 file_$i; done" % volume_path
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'change files chmod 644')

    log.info('2> 修改部分目录和文件的权限到755')
    cmd = "cd %s&&for i in {1..50}; do chmod 755 file_$i; done" % volume_path
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'change 1/2 files chmod 755')
    cmd = " chmod 755 %s" % volume_path
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'change dir chmod 755')

    log.info('3> 升级到最新的版本')
    rc,stdout = upgrade_common.online_upgrade()
    common.judge_rc(rc, 0, 'upgrade version')

    log.info('4> 升级成功后，检查目录权限')
    cmd = "stat -c %a {}".format(volume_path)
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'check dir chmod')
    common.judge_rc(int(stdout.strip()), 755, 'the chmod of dir is 755')

    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean(FILE_NAME)
    log.info('succeed!')

if __name__ == '__main__':
    common.case_main(main)
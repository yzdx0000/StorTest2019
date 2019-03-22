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
#  latest update:2018-08-27                                                   =
#  Author:wanggl                                                           =
# =================================================================================
# 2018-08-27:
# Author：wanggl
# @summary：
#   文件、目录权限不更新
# @steps:
#   1、parastor挂载两个私有客户端A和B；
#   2、客户端B创建一个文件test.sh，权限644；
#   3、客户端A读取文件test.sh；
#   4、客户端B修改权限为755；
#   5、客户端A执行test.sh;
#   6、客户端B修改权限为644；
#   7、客户端A执行test.sh
#
#

# changelog:


######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
volume_path = os.path.join(nas_common.BASE_NAS_PATH, FILE_NAME)             # /mnt/wangguanglin/cus_6_1_0_16
Private_clientIP1 = get_config.get_client_ip(0)
Private_clientIP2 = get_config.get_client_ip(1)
Private_clientIP3 = get_config.get_client_ip(2)


def case():

    log.info('2> 客户端B创建一个文件test.sh，权限644')
    common.mkdir_path(Private_clientIP2, volume_path)
    test = os.path.join(volume_path, 'test')
    cmd = 'touch %s' % test
    rc, stdout = common.run_command(Private_clientIP2, cmd)
    common.judge_rc(rc, 0, 'create file')
    cmd = "  chmod 644 %s" % test
    rc, stdout = common.run_command(Private_clientIP2, cmd)
    common.judge_rc(rc, 0, 'change file chmod 644')

    log.info('3> 客户端A读取文件test.sh')
    cmd = " cat %s" % test
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'read file')


    log.info('4> 客户端B修改权限为755')
    cmd = "  chmod 755 %s" % test
    rc, stdout = common.run_command(Private_clientIP2, cmd)
    common.judge_rc(rc, 0, 'change file chmod 755')

    log.info('5> 客户端A执行test.sh')
    cmd = " sh %s" % test
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'execute file')

    log.info('6> 客户端B修改权限为644')
    cmd = "  chmod 644 %s" % test
    rc, stdout = common.run_command(Private_clientIP2, cmd)
    common.judge_rc(rc, 0, 'change file chmod 644')

    log.info('7> 客户端A执行test.sh')
    cmd = " sh %s" % test
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'execute file')
    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean(FILE_NAME)
    log.info('succeed!')

if __name__ == '__main__':
    common.case_main(main)
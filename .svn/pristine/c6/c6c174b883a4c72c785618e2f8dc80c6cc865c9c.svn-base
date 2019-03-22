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
#  latest update:2018-08-13                                                   =
#  Author:wanggl                                                           =
# =================================================================================
# 2018-08-13:
# Author：wanggl
# @summary：
#   passwd中存在特殊字符导致升级失败
# @steps:
#   1、/etc/passwd 文件中出现一行“+：：：：：：”测试升级；
#   2、升级版本；
#
#

# changelog:该用集群节点就用集群节点


######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
SYSTEM_IP = get_config.get_parastor_ip()
Private_clientIP1 = get_config.get_client_ip(0)
Private_clientIP2 = get_config.get_client_ip(1)
Private_clientIP3 = get_config.get_client_ip(2)


def case():

    log.info('1> /etc/passwd 文件中出现一行“+：：：：：：”测试升级')
    '''备份/etc/passwd文件 '''
    cmd = 'cp /etc/passwd /etc/passwd_bk'
    rc, stdout = common.run_command(SYSTEM_IP, cmd)
    cmd = 'echo +: : : : : : >> /etc/passwd '
    rc, stdout = common.run_command(SYSTEM_IP, cmd)
    common.judge_rc(rc, 0, 'append special symol to /etc/passwd')

    log.info('2> 升级版本')
    rc = upgrade_common.online_upgrade()
    common.judge_rc(rc, 0, 'upgrade version failed')

    '''恢复/etc/passwd文件 '''
    cmd = 'cp /etc/passwd_bk /etc/passwd'
    rc, stdout = common.run_command(SYSTEM_IP, cmd)

    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean(FILE_NAME)
    log.info('succeed!')

if __name__ == '__main__':
    common.case_main(main)
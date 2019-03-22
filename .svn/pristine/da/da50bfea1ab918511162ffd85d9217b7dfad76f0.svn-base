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
import logging
# =================================================================================
#  latest update:2018-08-21                                                   =
#  Author:wanggl                                                           =
# =================================================================================
# 2018-08-21:
# Author：wanggl
# @summary：
#   私有客户端压缩解压缩场景
# @steps:
#   1、在私有客户端通过命令行循环压缩解压缩10000个1m小文件；

#

# changelog:


######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
volume_path = os.path.join(quota_common.BASE_QUOTA_PATH, FILE_NAME)             # /mnt/wangguanglin/cus_6_1_0_40
Private_clientIP1 = get_config.get_client_ip(0)
Execute_path = quota_common.BASE_QUOTA_PATH
Compress_name = "%s.tar.gz" % FILE_NAME

def tar_log(pwd_dir, tar_name, src_dir, node_ip):
    """
    :Author:         wanggl
    :date  :         2018.08.21
    :description:    压缩目录
    :param pwd_dir:  操作目录
    :param src_dir:  要压缩的源目录
    :param tar_name: 压缩包的名字
    :param node_ip:  执行命令的节点
    :return:
    """
    cmd = 'cd %s && tar zcvf %s %s --remove-files' % (pwd_dir, tar_name, src_dir)
    info_str = "node %s  tar %s  to  %s" % (node_ip, src_dir, tar_name)
    logging.info(info_str)
    rc, stdout = common.run_command(node_ip, cmd)
    if rc != 0:
        logging.error(stdout)
        logging.error("tar failed!!!")
    return rc, stdout


def tar_xvflog(pwd_dir, tar_name,  node_ip):
    """
    :Author:         wanggl
    :date  :         2018.08.21
    :description:    解压缩目录
    :param pwd_dir:  操作目录
    :param tar_name: 压缩包的名字
    :param node_ip:  执行命令的节点
    :return:
    """
    cmd = 'cd %s && tar xvf %s && rm -rf %s' % (pwd_dir, tar_name, tar_name)
    info_str = "node %s  uncompress %s  " % (node_ip, tar_name)
    logging.info(info_str)
    rc, stdout = common.run_command(node_ip, cmd)
    if rc != 0:
        logging.error(stdout)
        logging.error("xtar failed!!!")
    return rc, stdout

def case():

    log.info('1> 在私有客户端通过命令行循环压缩解压缩10000个1m小文件')
    """先创建10000个1m小文件"""
    common.mkdir_path(Private_clientIP1, volume_path)
    cmd = "cd %s && for i in {1..10000}; do dd if=/dev/zero of=file_$i bs=1M count=1; done" % volume_path
    rc, stdout = common.run_command(Private_clientIP1, cmd)
    common.judge_rc(rc, 0, 'create file')
    """循环压缩解压缩10000个1m小文件"""
    for i in range(2):
        rc, stdout = tar_log(Execute_path, Compress_name, FILE_NAME, Private_clientIP1)
        common.judge_rc(rc, 0, 'compress')
        rc, stdout = tar_xvflog(Execute_path, Compress_name,  Private_clientIP1)
        common.judge_rc(rc, 0, 'umcompress')
    """清理环境"""
    common.rm_exe(Private_clientIP1, volume_path)
    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean()
    log.info('succeed!')


if __name__ == '__main__':
    common.case_main(main)

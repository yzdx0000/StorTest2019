#!/usr/bin/python
# -*-coding:utf-8 -*

import os
import subprocess
import sys
import traceback
import datetime


import time
import logging

import utils_path
import get_config
import common
import prepare_clean
import create_s3_xml

##########################################################################
#
# Author: zhanghan
# date 2019-01-23
# @summary：
#    检查集群节点及私有客户端是否又core或者crash，如果有，则将core/crash删除
# @steps:
#    1、检查集群及私有客户端节点是否有core和crash，有的话则删除core/crash；

#
# @changelog：
##########################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]                 # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')

# log_file_path = log.get_log_path(FILE_NAME)
# log.init(log_file_path, True)
log_check_corecrash = None

def log_init_cosbench(case_log_path):
    """
    日志解析
    """
    global log_check_corecrash

    file_name = os.path.basename(__file__)
    file_name = file_name.split('.')[0]
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    log_file_name = now_time + '_' + file_name + '.log'
    log_file_path = os.path.join(case_log_path, log_file_name)
    print log_file_path

    log_check_corecrash = logging.getLogger(name='log_check_corecrash')
    log_check_corecrash.setLevel(level = logging.INFO)

    handler = logging.FileHandler(log_file_path, mode='a')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)

    log_check_corecrash.addHandler(console)
    log_check_corecrash.addHandler(handler)

    return

def rm(ip, origin_file):
    cmd = "ssh %s \"rm -fr %s \"" % (ip, origin_file)
    rc = common.command(cmd)
    return rc

def check_core(ip, check_dir = "/home/parastor/log"):
    cmd = "cd %s;ls | grep core " % check_dir
    (rc, output) = common.run_command(ip, cmd)
    if len(output) != 0:
        log_check_corecrash.info("In node %s:%s, has core %s" % (ip, check_dir, output.replace('\n', ' ')))
        for item in output.split('\n')[:-1]:
            core_tmp = os.path.join(check_dir, item)
            rm_core_rc = rm(ip, core_tmp)
            if 0 != rm_core_rc:
                log_check_corecrash.error("In node %s:%s, rm core %s failed" % (ip, check_dir, core_tmp))
            else:
                log_check_corecrash.info("In node %s:%s, rm core %s success" % (ip, check_dir, core_tmp))

    else:
        log_check_corecrash.info("In node %s:%s, has no core" % (ip, check_dir))

def check_crash(ip, check_dir = "/var/crash"):
    cmd = "cd %s;ls | grep 127.0.0.1 " % check_dir
    (rc, output) = common.run_command(ip, cmd)
    if len(output) != 0:
        log_check_corecrash.info("In node %s:%s, has crash %s" % (ip, check_dir, output.replace('\n', ' ')))
        for item in output.split('\n')[:-1]:
            crash_tmp = os.path.join(check_dir, item)
            rm_crash_rc = rm(ip, crash_tmp)
            if 0 != rm_crash_rc:
                log_check_corecrash.error("In node %s:%s, rm crash %s failed" % (ip, check_dir, crash_tmp))
            else:
                log_check_corecrash.info("In node %s:%s, rm crash %s success" % (ip, check_dir, crash_tmp))
    else:
        log_check_corecrash.info("In node %s:%s, has no crash" % (ip, check_dir))


def check_core_crash(case_log_path, cli_ip_list = None):
    log_init_cosbench(case_log_path)
    log_check_corecrash.info("1> 获取集群节点和私有客户端ip")
    parastor_ip_list = get_config.get_allparastor_ips()
    if None != cli_ip_list:
        parastor_and_client_ip_list = parastor_ip_list + cli_ip_list
    else:
        parastor_and_client_ip_list = parastor_ip_list

    log_check_corecrash.info("2> 检查/home/parastor/log目录下是否有core")
    for ip in parastor_and_client_ip_list:
        check_core(ip)
        check_core(ip, "/")

    log_check_corecrash.info("3> 检查/var/crash目录下是否有crash")
    for ip in parastor_and_client_ip_list:
        check_crash(ip)

def main():
    case_log_path = "/home/StorTest/test_cases/log/case_log"
    check_core_crash(case_log_path, ["10.2.42.79", "10.2.42.80"])


if __name__ == '__main__':
    common.case_main(main)

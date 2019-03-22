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
# date 2019-01-24
# @summary：
#    收集日志
# @steps:
#    1、收集日志；

#
# @changelog：
##########################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]                 # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')

# log_file_path = log.get_log_path(FILE_NAME)
# log.init(log_file_path, True)
log_collect = None

# 获取存放log节点ip和路径
log_storage_ip = get_config.get_log_storage_ip().encode("utf-8")
log_storage_path = get_config.get_log_storage_path().encode("utf-8")
log_collect_scripts_path = get_config.get_log_collect_scripts_path()


def excute_command(cmd):
    log_collect.info(cmd)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = process.stdout.readline()
        if '' == line:
            break
        log_collect.debug(line.rstrip())
    process.wait()
    if process.returncode == 0:
        return 0
    else:
        return -1

def log_init_cosbench(case_log_path):
    """
    日志解析
    """
    global log_collect

    file_name = os.path.basename(__file__)
    file_name = file_name.split('.')[0]
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    log_file_name = now_time + '_' + file_name + '.log'
    log_file_path = os.path.join(case_log_path, log_file_name)
    print log_file_path

    log_collect = logging.getLogger(name='log_collect')
    log_collect.setLevel(level = logging.INFO)

    handler = logging.FileHandler(log_file_path, mode='a')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)

    log_collect.addHandler(console)
    log_collect.addHandler(handler)

    return


def ssh_create_dir(dest_ip, dir):
    cmd = "ssh %s \"mkdir -p %s\"" % (dest_ip, dir)
    rc = excute_command(cmd)
    return rc

def is_crash(ip, check_dir="/var/crash"):
    crash_list = []
    cmd = "cd %s;ls | grep 127.0.0.1 " % check_dir
    (rc, output) = common.run_command(ip, cmd)
    if len(output) != 0:
        for item in output.split('\n')[:-1]:
            crash_list.append(item)
    return crash_list


def get_all_crash(ip_list):
    ip_crash_dict = dict()
    for current_ip in ip_list:
        crash_list_current_ip = is_crash(current_ip)
        if len(crash_list_current_ip):
            ip_crash_dict[current_ip] = crash_list_current_ip
    return ip_crash_dict

def collect_log(case_log_path, case_rc, case_name, item_list = None, client_ip_list = None):
    log_init_cosbench(case_log_path)
    if case_rc != 0:
        rc_collect_log = get_log(case_name, client_ip_list)
        if 0 != rc_collect_log:
            log_collect.error("Please check! Case %s, collect parastor log failed" % case_name)
        else:
            log_collect.info("Case %s, collect parastor log success" % case_name)
        rc_get_stortest_log = get_stortest_log(case_log_path, case_name)
        if 0 != rc_get_stortest_log:
            log_collect.error("Please check! Case %s, collect StorTest log failed" % case_name)
        else:
            log_collect.info("Case %s, collect StorTest log success" % case_name)
        if len(item_list):
            rc_collect_others = get_others(case_name, item_list)
            rc_delete_others = rm_others(item_list)
            if 0 != (rc_collect_others or rc_delete_others):
                log_collect.error("Please check! Case %s, collect %s failed" % (case_name, item_list))
            else:
                log_collect.info("Case %s, collect %s success" % (case_name, item_list))
    else:
        pass

def get_others(case_name, item_list):
    log_collect.info("Collect others %s" % str(item_list))
    date_info = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    log_path = case_name + '_' + date_info + '_vdb'
    final_path = os.path.join(log_storage_path, log_path)
    # os.mkdir(final_path)
    ssh_create_dir(log_storage_ip, final_path)
    for item in item_list:
        name = item.split('/')[-1]
        final_path_tmp = os.path.join(final_path, name)
        os.mkdir(final_path_tmp)
        cmd = "scp -r %s %s:%s" % (item, log_storage_ip, final_path_tmp)
        rc_collect_vdb_output = excute_command(cmd)
        if 0 != rc_collect_vdb_output:
            return rc_collect_vdb_output
    return 0

def get_stortest_log(case_log_path, case_name):
    log_collect.info("Collect StorTest log")
    date_info = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    log_path = case_name + '_' + date_info + '_StorTest'
    final_path = os.path.join(log_storage_path, log_path)
    # os.mkdir(final_path)
    ssh_create_dir(log_storage_ip, final_path)
    cmd_get_stortest_log = "scp -r %s %s:%s" % (case_log_path, log_storage_ip, final_path)
    rc_get_stortest_log = excute_command(cmd_get_stortest_log)
    return rc_get_stortest_log


def rm_others(item_list):
    log_collect.info("The %s has been saved, now will delete them" % str(item_list))
    rc_delete_others = 0
    for item in item_list:
        cmd = "rm -fr %s" % item
        rc_delete_others = excute_command(cmd)
    return rc_delete_others


def get_log(case_name, cli_ip_list):

    log_collect.info("获取所有集群节点ip")
    parastor_ips = get_config.get_allparastor_ips()

    log_collect.info("收集集群节点和私有客户端的日志")
    # 修改ip格式，将unicode修改为str类型
    parastor_ip_list = []
    for para_ip in parastor_ips:
        parastor_ip_list.append(para_ip.encode("utf-8"))
    parastor_ip_str = ""
    for ip in parastor_ip_list:
        parastor_ip_str = parastor_ip_str + ip + ","
    parastor_ip_str = parastor_ip_str[:-1]

    # 获取集群节点和私有客户端的crash（按照日志收集脚本需要的格式）
    if None != cli_ip_list:
        log_collect.info("client ip is %s" % cli_ip_list)
        parastor_and_client_ip_list = parastor_ip_list + cli_ip_list
    else:
        log_collect.info("There has no client!")
        parastor_and_client_ip_list = parastor_ip_list
    crash_dict = get_all_crash(parastor_and_client_ip_list)
    crash_str = ""
    for key in crash_dict:
        for value in crash_dict[key]:
            crash_str = crash_str + key + ":" + value + ","
    crash_str = crash_str[:-1]

    case_name_final = case_name + '_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    log_storage_path_final = os.path.join(log_storage_path, case_name_final)
    print(log_storage_path_final)
    # os.mkdir(log_storage_path_final)
    ssh_create_dir(log_storage_ip, log_storage_path_final)


    if None != cli_ip_list:
        client_ip_str = ""
        for ip in cli_ip_list:
            client_ip_str = client_ip_str + ip + ","
        client_ip_str = client_ip_str[:-1]
        if "" != crash_str:
            cmd = "python %s -i %s -I %s -c %s -d %s:%s" % (
                log_collect_scripts_path, client_ip_str, parastor_ip_str, crash_str, log_storage_ip, log_storage_path_final)
        else:
            cmd = "python %s -i %s -I %s -d %s:%s" % (
                log_collect_scripts_path, client_ip_str, parastor_ip_str, log_storage_ip, log_storage_path_final)
    else:
        if "" != crash_str:
            cmd = "python %s -I %s -c %s -d %s:%s" % (
                log_collect_scripts_path, parastor_ip_str, crash_str, log_storage_ip, log_storage_path_final)
        else:
            cmd = "python %s -I %s -d %s:%s" % (
                log_collect_scripts_path, parastor_ip_str, log_storage_ip, log_storage_path_final)
    rc_collect_log = excute_command(cmd)
    return rc_collect_log


def main():
    cli_ip_list = ["10.2.42.79", "10.2.42.80"]
    collect_log("/home/StorTest/test_cases/log/case_log", 1, "case_1234", ["/home/zhanghan", "/root/nfsd_bak", "/root/tools_bak"], cli_ip_list)
    #log_init_cosbench('/home/StorTest/test_cases/log/case_log')

if __name__ == '__main__':
    common.case_main(main)

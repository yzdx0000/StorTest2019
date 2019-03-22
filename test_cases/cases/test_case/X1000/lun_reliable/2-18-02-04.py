# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
1）创建节点池，创建存储池，配置多访问区，开启SAN协议，
2）制造主oPmgr挂起（gbd），在故障期间创建LUN
检查项：
1）访问区配置成功
2）逻辑卷成功创建

'''


import os
import time
import random
import commands
import threading
import utils_path
import log
import common
import ReliableTest
import env_manage
import decorator_func


'''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log


def setup():
    '''获取业务节点IP和非业务节点IP'''
    global node_ip1
    global node_ip2
    global client_ip1
    node_ip1 = env_manage.get_inter_ids()[0]  # 业务节点IP
    node_ip2 = env_manage.get_inter_ids()[1]  # 业务节点IP
    client_ip1 = env_manage.client_ips[0]


def pasue_threads():
    orole_master_ip = env_manage.com_lh.get_master_oRole(s_ip=node_ip1)
    env_manage.com_lh.pasue_thread(s_ip=orole_master_ip, p_name="oRole", t_name="pmgr")


def run_threads():
    ojmgs_id, ojmgs_ip = env_manage.com_lh.oJmgs_master_id()
    env_manage.com_lh.run_pause_process(node_ip=ojmgs_ip, process="oRole", threads="pmgr")


def case():
    log.info("step:1.创建逻辑卷")
    env_manage.create_lun()
    log.info("step:2.挂起pmgr线程")
    pasue_threads()
    log.info("step:3.删除逻辑卷")
    env_manage.clean_lun()
    log.info("step:4.恢复pmgr线程")
    run_threads()


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:5.检查测试环境")
    env_manage.com_lh.get_os_status(node_ip1)
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)

# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
1）配置节点池，配置存储池
2）创建访问区，创建过程中主oJmgs进程异常，从进程接管业务，创建完成
检查项：
1）节点池，存储池创建成功
2）访问区创建成功

'''

import os
import time
import random
import commands
import threading
import utils_path
import common
import log
import access_env
import ReliableTest
import env_manage
import decorator_func


# from sub_config_lh import config_parser as CP

'''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log


def setup():
    '''获取业务节点IP和非业务节点IP'''
    global node_ip1
    global node_ip2
    global client_ip1
    node_ip1 = env_manage.deploy_ips[0]  # 测试节点IP
    node_ip2 = env_manage.deploy_ips[1]  # 异常节点IP
    client_ip1 = env_manage.client_ips[0]


def run_kill():
    master_oRole_ip = env_manage.com_lh.oJmgs_master_id(node_ip1)
    env_manage.com_lh.run_pause_process(p_ip=master_oRole_ip, p_name="oRole")
    time.sleep(10)


def run_pasuse_process():
    # for i in range(3):
    master_oRole_ip = env_manage.com_lh.oJmgs_master_id(node_ip1)
    env_manage.com_lh.run_process(p_ip=master_oRole_ip, p_name="oRole")
    time.sleep(10)


def check_res():
    decorator_func.judge_target(
        env_manage.osan.get_option(s_ip=node_ip1, command="get_access_zones", indexname='access_zones', argv='name'),
        [u'accesszone1', u'accesszone2'])


def check_os():
    try:
        env_manage.clean_access_zone()
    except Exception as e:
        log.info(e)
    common.ckeck_system()


def case():
    env_manage.create_access(node_ids='1,2', access_name="accesszone1")
    threads = []
    t1 = threading.Thread(target=run_kill)
    threads.append(t1)
    t2 = threading.Thread(target=env_manage.create_access(node_ids='2', access_name="accesszone2"))
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # check_res()
    run_pasuse_process()
    log.info("The case finished!!!")


def main():
    access_env.check_env()
    setup()
    case()


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    main()

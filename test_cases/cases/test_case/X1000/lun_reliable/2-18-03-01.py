# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
1）创建节点池，创建存储池，配置多访问区，开启SAN协议，
2）制造主oJmgs进程反复故障，在故障期间创建LUN
检查项：
1）访问区配置成功
2）逻辑卷成功创建


'''

# testlink case: 1000-33711
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


def run_kill():
    for i in range(3):
        ojmgs_id, ojmgs_ip = env_manage.com_lh.oJmgs_master_id()
        log.info("step:2.2 node %s will kill oJmgs process" % (ojmgs_ip))
        ReliableTest.run_kill_process(node_ip=ojmgs_ip, process="oJmgs")
        time.sleep(10)


def create_luns():
    log.info("step：2.1创建逻辑卷")
    for i in range(2, 10):
        lun_name = "LUN" + str(i)
        env_manage.create_lun(node_ip1, lun_name)


def case():
    log.info("step:1.创建逻辑卷")
    env_manage.create_lun()
    log.info("step:2.创建逻辑卷时kill oJmgs 进程")
    threads = []
    t1 = threading.Thread(target=run_kill)
    threads.append(t1)
    t2 = threading.Thread(target=create_luns)
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:3.清理检查测试环境")
    env_manage.com_lh.get_os_status(node_ip1)
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
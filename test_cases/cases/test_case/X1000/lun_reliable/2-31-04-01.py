# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-10
'''
测试内容：添加主机过程中主ojmgs异常从接管业务
测试步骤：
1）配置节点池，配置存储池
2）配置访问区
3）添加SVIP，VIP池
4）创建主机组，创建/删除主机，创建过程中主ojmgs异常从接管业务
检查项：
1）节点池，存储池创建成功
2）访问区创建成功
3）SVIP、vip池配置成功
4）主机组创建成功，主机创建/删除成功
'''

# testlink case: 1000-33977
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
    global node_ip3
    global client_ip1
    node_ip1 = env_manage.deploy_ips[0]
    node_ip2 = env_manage.deploy_ips[1]
    node_ip3 = env_manage.deploy_ips[2]
    client_ip1 = env_manage.client_ips[0]


def run_kill():
    ojmgs_id, ojmgs_ip = env_manage.com_lh.oJmgs_master_id()
    ReliableTest.run_kill_process(node_ip=ojmgs_ip, process="oJmgs")


def case():
    log.info("step:1.创建主机过程中kill oJmgs")
    threads = []
    t1 = threading.Thread(target=run_kill)
    threads.append(t1)
    t2 = threading.Thread(target=env_manage.create_host, args=(node_ip1,))
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main():
    env_manage.check_san_enable_env()
    setup()
    env_manage.create_host_group()
    case()
    log.info("step:2.检查清理测试环境")
    env_manage.clean_host()
    env_manage.clean_hostgroup()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-15

'''
测试内容: oRole进程异常创建访问区
测试步骤：
1）配置节点池，配置存储池
2）创建访问区，创建过程中主oJmgs进程异常，从进程接管业务，创建完成
检查项：
1）节点池，存储池创建成功
2）访问区创建成功

'''

# testlink case: 1000-34028
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
import access_env
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
    node_ip1 = env_manage.deploy_ips[0]  # 测试节点IP
    node_ip2 = env_manage.deploy_ips[1]  # 异常节点IP
    client_ip1 = env_manage.client_ips[0]


def run_kill(master_ip):
    ReliableTest.run_kill_process(node_ip=master_ip, process="oRole")


def case():
    master_orole_ip = env_manage.com_lh.get_master_oRole(node_ip1)
    log.info("step:1.创建访问区1")
    env_manage.create_access(node_ids='1,2', access_name="accesszone1")
    log.info("step:2.创建访问区2时kill oRole进程")
    threads = []
    t1 = threading.Thread(target=run_kill, args=(master_orole_ip,))
    threads.append(t1)
    t2 = threading.Thread(target=env_manage.create_access, args=(node_ip1, '3,4', "accesszone2"))
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main():
    access_env.check_env()
    setup()
    case()
    log.info("step:3.清理测试环境")
    env_manage.clean_access_zone()
    access_env.check_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=5)
    common.case_main(main)
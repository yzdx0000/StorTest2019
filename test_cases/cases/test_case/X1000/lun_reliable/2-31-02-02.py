# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
1）配置节点池，配置存储池
2）配置访问区
3）添加SVIP，VIP池
4）启用/禁用osan协议过程中主从oJmgs故障，启动过程失败，操作回滚，系统自动清理已配置文件
检查项：
1）节点池，存储池创建成功
2）访问区创建成功
3）SVIP、vip池配置成功
4）启用/禁用协议成功

'''

# testlink case: 1000-33970
import os
import time
import random
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
    global node_ip3
    global client_ip1
    node_ip1 = env_manage.deploy_ips[0]
    node_ip2 = env_manage.deploy_ips[1]
    node_ip3 = env_manage.deploy_ips[2]
    client_ip1 = env_manage.client_ips[0]


def run_kill():
    for i in range(3):
        ojmgs_id, ojmgs_ip = env_manage.com_lh.oJmgs_master_id()
        node_ip = random.choice(env_manage.deploy_ips)
        if node_ip == ojmgs_ip:
            continue
        else:
            ReliableTest.run_kill_process(node_ip=ojmgs_ip, process="oJmgs")
            ReliableTest.run_kill_process(node_ip=node_ip, process="oJmgs")


def san_test():
    san_status = env_manage.com_lh.get_san_state(node_ip1)
    log.info("get the san status: %s" % (san_status))
    if san_status is None:
        log.info("check san status is inactive")
    elif all(san_status) is True:
        env_manage.disable_san()
    elif all(san_status) is False:
        env_manage.enable_san()
    else:
        log.error("have other access zone san failed %s" % (san_status))


def case():
    log.info("step:1.检查san协议开启或关闭并kill oJmgs进程")
    threads = []
    t1 = threading.Thread(target=run_kill)
    threads.append(t1)
    t2 = threading.Thread(target=san_test)
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main():
    env_manage.check_san_enable_env()
    setup()
    case()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)

#!usr/bin/env python
# -*- coding:utf-8 _*-
'''
测试步骤：
1）配置访问区，映射逻辑卷到主机
2）制造一台日志组非业务节点数据网+日志组业务节点oSan进程异常
检查项：
1）访问区配置成功
2）逻辑卷创建成功
'''

# testlink case: 1000-33946
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
    node_ip1 = env_manage.get_inter_ids()[0]  # 业务节点IP
    node_ip2 = env_manage.get_inter_ids()[-1]  # 非业务节点IP
    node_ip3 = env_manage.get_inter_ids()[1]
    client_ip1 = env_manage.client_ips[0]


def net_pro_test(net_name):
    ReliableTest.run_kill_process(node_ip=node_ip1, process="oSan")
    env_manage.down_network(node_ip2, net_name)


def case():
    log.info("step:1.创建逻辑卷")
    subnet_eth = env_manage.com_lh.get_vip_eth_name(node_ip1)
    env_manage.create_lun()
    log.info("step:2.创建逻辑卷过程中进程和网卡异常")
    threads = []
    t1 = threading.Thread(target=net_pro_test, args=(subnet_eth,))
    threads.append(t1)
    t2 = threading.Thread(target=env_manage.create_lun_map, args=(node_ip3,))
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("step:3.网卡恢复")
    env_manage.up_network(node_ip2, subnet_eth)


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:4.检查清理测试环境")
    env_manage.clean_lun_map()
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(
        file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)

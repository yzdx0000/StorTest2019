# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-14

'''
测试内容: 数据网断开后创建访问区
测试步骤：
1、创建节点池，创建存储池
2、创建访问区access1
3、业务节点数据网断开
4、创建访问区access2
检查项：
1）节点池、存储池创建成功
2）创建访问区成功

'''

# testlink case: 1000-34014
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


def case():
    subnet_eth = env_manage.com_lh.get_vip_eth_name(node_ip1)
    log.info("step:1.创建访问区1")
    env_manage.create_access(node_ids='1,2', access_name="accesszone1")
    log.info("step:2.业务网断开")
    env_manage.down_network(node_ip1, subnet_eth)
    log.info("step:3.创建访问区2")
    env_manage.create_access(ips=node_ip2, node_ids='3,4', access_name="accesszone2")
    log.info("step:4.网卡恢复")
    env_manage.up_network(node_ip1, subnet_eth)


def main():
    access_env.check_env()
    setup()
    case()
    log.info("step:5.清理测试环境")
    env_manage.clean_access_zone()
    access_env.check_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=5)
    common.case_main(main)

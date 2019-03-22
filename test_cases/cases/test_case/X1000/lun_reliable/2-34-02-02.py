# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
1、创建节点池，创建存储池
2、创建访问区access1
3、将任意一个节点断电
4、创建访问区access2
检查项：
1）节点池、存储池创建成功
2）节点正常关闭
3）创建访问区成功

'''

# testlink case: 1000-33997
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
    '''配置测试环境创建节点池，存储池，主机组，主机，SVIP，VIP，添加启动器'''
    log.info("step:1.创建访问区accesszone1和accesszon2")
    env_manage.create_access(node_ids='1,2')
    env_manage.create_access(node_ids='3,4', access_name="accesszone2")
    log.info("step:2.将节点重启")
    os_type = env_manage.get_os_type(node_ip2)
    env_manage.down_node(node_ip2, os_type, "init 6")  # 节点关机
    log.info("step:3.删除访问区accesszone2")
    azs = env_manage.osan.get_access_zone_id(s_ip=node_ip1)
    env_manage.osan.delete_access_zone(s_ip=node_ip1, azid=azs[-1])
    log.info("step:4.检查节点运行状态，检查服务恢复情况。")
    env_manage.com_lh.get_os_status(node_ip2)


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
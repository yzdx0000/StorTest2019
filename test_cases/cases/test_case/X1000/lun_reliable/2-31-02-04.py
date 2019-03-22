# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
1）配置节点池，配置存储池
2）配置访问区
3）添加SVIP，VIP池
4）重复激活oSan协议，系统自动拒绝再激活
检查项：
1）节点池，存储池创建成功
2）访问区创建成功
3）SVIP、vip池配置成功
4）启用/禁用协议成功

'''

# testlink case: 1000-33972
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


def enable_san():
    az_id = env_manage.osan.get_access_zone_id(s_ip=node_ip1)
    env_manage.osan.enable_san(s_ip=node_ip1, access_zone_id=az_id[0])


def run_kill():
    ojmgs_id, ojmgs_ip = env_manage.com_lh.oJmgs_master_id()
    ReliableTest.run_kill_process(node_ip=ojmgs_ip, process="oJmgs")
    time.sleep(10)


def case():
    log.info("step:1.检查环境，查看san协议是否激活")
    san_status = env_manage.com_lh.get_san_state(node_ip1)
    if all(san_status) is True:
        log.info("check all san is active, all san status:%s" % (san_status))
        env_manage.disable_san()
    else:
        log.info("check san status is :%s" % (san_status))
    log.info("step:2.确认san协议未激活后执行激活san协议并kill oJmgs进程")
    enable_san()
    log.info("step:3.重复激活san")
    rc = enable_san()
    if rc != 0:
        log.info("os can not again enable san ")
    else:
        log.error("again enable san do not expect")
        os._exit(1)


def main():
    env_manage.check_san_enable_env()
    setup()
    case()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)

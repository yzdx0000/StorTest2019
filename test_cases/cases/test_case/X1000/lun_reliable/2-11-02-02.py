# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
逻辑卷创建过程中将日志组一台非业务节点重启
检查项：
逻辑卷创建成功
'''

# testlink case: 1000-33658
import os
import time
import random
import commands
import threading
import utils_path
import log
import common
import ReliableTest
import prepare_x1000
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
    node_ip2 = env_manage.get_inter_ids()[-1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def os_down():
    '''在系统下使用执行命令正常关机, reten os ID'''
    rc = env_manage.com_lh.get_cmd_status(node_ip1, cmd_name="create_lun")
    if rc == 0:
        type = env_manage.get_os_type(node_ip2)
        info = env_manage.down_node(node_ip2, type, "init 6")
        log.info("节点%s 即将reboot，节点类型 %s，节点ID or IPMI IP：%s " % (node_ip2, info, type))
        return
    elif rc == 1:
        log.error("Not find CMD ,timeout will exit")
        os._exit(1)


def create_luns():
    for i in range(10):
        lun_name = "LUN" + str(i)
        env_manage.create_lun(node_ip1, lun_name)


def case():
    log.info("step:1.创建逻辑卷时节点重启")
    threads = []  # 创建并发队列
    t1 = threading.Thread(target=create_luns)  # 创建lun
    threads.append(t1)
    t2 = threading.Thread(target=os_down)  # 节点关机
    threads.append(t2)
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    log.info("step:2.检查节点及服务运行状态")
    env_manage.com_lh.get_os_status(node_ip2)


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:3.检查节点及服务运行状态")
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
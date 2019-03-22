# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-16
'''
测试内容:日志组业务节点+日志组非业务节点关机后创建逻辑卷
测试步骤：
1）创建多个访问区，配置访问区将日志组业务节点和一个日志组非业务节点正常关机
2）创建逻辑卷
检查项：
逻辑卷创建成功
注意：
    测试节点数》=5
'''
# testlink case: 1000-33680
import os
import time
import random
import commands
import threading
import utils_path
import log
import common
import prepare_x1000
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
    global node_ip4
    global node_ip5
    global client_ip1
    node_ip1 = env_manage.get_inter_ids()[0]
    node_ip2 = env_manage.get_inter_ids()[-1]
    node_ip3 = env_manage.get_inter_ids()[-2]
    node_ip4 = env_manage.get_inter_ids()[1]
    node_ip5 = env_manage.get_inter_ids()[2]
    client_ip1 = env_manage.client_ips[0]


def case():
    log.info("step:1.将两个节点关机")
    type1 = env_manage.get_os_type(node_ip2)
    info1 = env_manage.down_node(node_ip2, type1, "init 0")
    type2 = env_manage.get_os_type(node_ip3)
    info2 = env_manage.down_node(node_ip3, type2, "init 0")
    log.info("step:2.创建逻辑卷")
    env_manage.create_lun(node_ip4, "LUN1")
    log.info("step:3.节点开机")
    env_manage.up_node(info1, type1)
    env_manage.up_node(info2, type2)
    log.info("step:4.检查节点状态")
    rc1 = env_manage.com_lh.get_os_status(node_ip2)
    rc2 = env_manage.com_lh.get_os_status(node_ip3)
    if rc1 == 0 and rc2 == 0:
        return


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:5.清理检查测试环境")
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=5)
    common.case_main(main)

# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-14

'''
测试内容: 数据网闪断异常后删除逻辑卷
测试步骤：
1）创建多个访问区，配置访问区将日志组业务节点重启
2）创建逻辑卷
检查项：
逻辑卷创建成功
'''

# testlink case: 1000-33655
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


def case():
    log.info("step: will get machine info")
    type = env_manage.get_os_type(node_ip1)
    info = env_manage.down_node(node_ip1, type, "init 6")
    log.info("step:1.节点%s 即将reboot，节点类型 %s，节点ID or IPMI IP：%s " % (node_ip1, info, type))
    log.info("step:2.创建逻辑卷")
    env_manage.create_lun(node_ip2)
    log.info("step:3.检查节点及服务运行状态")
    env_manage.com_lh.get_os_status(node_ip1)


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:4.检查节点及服务运行状态")
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)

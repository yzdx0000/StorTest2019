# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-6
'''
测试内容:异常后查看
测试步骤：
1）创建逻辑卷创建完成后映射至主机将日志组一台非业务节点关机
3）检查逻辑卷详细信息，显示与实际相符
检查项：
显示信息正确
'''
# testlink case: 1000-33632
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
    log.info("******************* case start **********************")
    log.info("step:1.创建逻辑卷")
    env_manage.create_luns(s_ip=node_ip1)
    log.info("step:2.节点关机")
    type = env_manage.get_os_type(node_ip2)
    info = env_manage.down_node(node_ip2, type, "init 0")
    log.info("step:3.获取 lun 信息")
    env_manage.osan.get_lun(s_ip=node_ip1)
    log.info("step:4.%s 节点开机 节点类型%s,节点ID or IPMI IP: %s" % (node_ip2, type, info))
    env_manage.up_node(info, type)
    log.info("step:5.检查节点运行状态，检查服务恢复情况。")
    env_manage.com_lh.get_os_status(node_ip2)
    log.info("******************* case end ************************")


def main():
    log.info("step: checking the test environment")
    env_manage.clean_test_env()
    log.info("step: initialize node ip")
    setup()
    case()
    log.info("step:6.清理测试环境")
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)

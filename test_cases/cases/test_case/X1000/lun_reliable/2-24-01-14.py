# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-9
'''
测试内容:非业务节点数据网异常情况下修改逻辑卷
测试步骤：
1）创建多访问区，配置访问区将日志组业务节点数据网闪断5次
2）创建逻辑卷

检查项：
1）访问区配置成功
2）逻辑卷创建成功

'''

# testlink case: 1000-33843
import os
import time
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
    log.info("step:1.创建逻辑卷")
    env_manage.create_luns()
    log.info("step:2.网卡闪断")
    data_net = env_manage.com_lh.get_eth_name(s_ip=node_ip2)[1]
    env_manage.com_lh.net_flash_test(node_ip2, data_net)
    log.info("step:3.修改逻辑卷")
    env_manage.update_luns()


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:4.清理检查测试环境")
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)

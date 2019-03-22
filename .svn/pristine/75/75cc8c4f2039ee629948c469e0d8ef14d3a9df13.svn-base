# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-6
'''
测试内容:节点异常情况下创建访问区
测试步骤：
1）创建节点池，创建存储池
2）将一个节点数据网断开
3）检查管理端是否有告警
4）配置访问区
检查项：
1）节点异常
2）访问区不能配置

'''

# testlink case: 1000-33959
import os
import time
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


def create_access():
    env_manage.osan.create_access_zone(s_ip=node_ip1, node_id='1,2,3', name='accesszone1')


def network_down(net_name):
    env_manage.down_network(node_ip2, net_name)


def case():
    data_name = env_manage.com_lh.get_eth_name(node_ip2)[1]
    log.info("step:1.创建访问区过程中关闭业务节点网卡")
    threads = []
    t1 = threading.Thread(target=network_down, args=(data_name,))
    threads.append(t1)
    t2 = threading.Thread(target=create_access)
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("step:2.恢复网卡")
    env_manage.up_network(node_ip2, data_name)


def main():
    access_env.check_env()
    setup()
    case()
    log.info("step:3.清理检查测试环境")
    env_manage.clean_access_zone()
    access_env.check_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)

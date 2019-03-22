# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-15

'''
测试内容: 数据网断开后创建逻辑卷
测试步骤：
1、创建节点池，创建存储池，配置访问区，添加启动器
2、创建逻辑卷lun1
3、业务节点数据网断开
4、创建逻辑卷lun2
检查项：
1）节点池、存储池创建成功
2）节点正常关闭
3）创建访问区成功

'''

# testlink case: 1000-34016
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
    global client_ip1
    node_ip1 = env_manage.get_inter_ids()[0]  # 业务节点IP
    node_ip2 = env_manage.get_inter_ids()[-1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def run_case():
    subnet_eth = env_manage.com_lh.get_vip_eth_name(node_ip1)
    time.sleep(60)
    log.info("step:2.关闭业务网卡")
    env_manage.down_network(node_ip1, subnet_eth)
    log.info("step:3.创建逻辑卷")
    env_manage.create_lun(node_ip2, "LUN2")
    log.info("step:4.恢复网卡")
    env_manage.up_network(node_ip1, subnet_eth)


def case():
    log.info("step:1.创建逻辑卷")
    env_manage.create_lun()
    threads = []
    threads.append(threading.Thread(target=env_manage.vdb_test))
    threads.append(threading.Thread(target=run_case))
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:5.清理检查测试环境")
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)

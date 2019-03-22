# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-6

'''
测试内容:节点异常情况下创建逻辑卷
测试步骤：
1）创建多个访问区，配置访问区配置逻辑卷前将日志组业务节点正常关机
2）创建逻辑卷
检查项：
逻辑卷创建成功

'''

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


os_types = []
infos = []


def node_down(down_ip):
    time.sleep(20)
    log.info("step node down start")
    os_type = env_manage.get_os_type(down_ip)
    info = env_manage.down_node(down_ip, os_type)
    os_types.append(os_type)
    infos.append(info)
    log.info("step node down finish")


def case():
    log.info("******************* start case **********************")
    log.info("step:1.创建逻辑卷")
    env_manage.create_luns()
    log.info("step:2.创建lun map,创建过程中节点下电")
    threads = []
    threads.append(threading.Thread(target=env_manage.create_lun_map, args=(node_ip2,)))
    threads.append(threading.Thread(target=node_down, args=(node_ip1,)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("step:3.获取lun map 数量")
    lun_map_ids = env_manage.osan.get_lun_maps(node_ip2)
    lun_ids = env_manage.osan.get_lun()
    if len(lun_map_ids) == len(lun_ids):
        log.info("step:4.检查lun map数量确认信息符合预期")
        log.info("step:5.%s 节点开机 节点类型%s,节点ID or IPMI IP: %s" % (node_ip1, os_types[0], infos[0]))
        env_manage.up_node(infos[0], os_types[0])
        log.info("step:6.检查节点及服务运行状态")
        env_manage.com_lh.get_os_status(node_ip1)
    else:
        log.info("lun map test fail")
        exit(1)
    log.info("******************* case end ***********************")


def main():
    log.info("step: checking the test environment")
    env_manage.clean_test_env()
    log.info("step: initialize node ip")
    setup()
    case()
    log.info("step:7.清理检查测试环境")
    env_manage.clean_lun_map()
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)

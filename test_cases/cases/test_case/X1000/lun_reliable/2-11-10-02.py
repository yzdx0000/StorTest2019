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


def case():
    log.info("step:1.create lun")
    env_manage.create_luns(s_ip=node_ip1, nums=10)
    os_type = env_manage.get_os_type(node_ip1)
    lun_ids = env_manage.osan.get_lun(s_ip=node_ip1)
    log.info("step:2.change lun attribute")
    i=0
    for lun_id in lun_ids:
        rc = env_manage.update_luns(s_ip=node_ip1, id=lun_id)
        if rc == id:
            i = i +1
        if i == 5:
            log.info("step:3.the node reboot")
            env_manage.down_node(node_ip2, os_type, "init 6")
    log.info("step:2.创建lun 映射")
    env_manage.create_lun_map(node_ip1)
    lun_maps = env_manage.osan.get_lun_maps(node_ip1)
    lun_ids = env_manage.osan.get_lun()
    if len(lun_maps) == len(lun_ids):
        log.info("step:4.检查lun map 符合预期，检查节点及服务状态")
        env_manage.com_lh.get_os_status(node_ip2)
    else:
        log.info("lun map test fail")
        exit(1)


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:5.清理测试环境。")
    env_manage.clean_lun_map()
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)

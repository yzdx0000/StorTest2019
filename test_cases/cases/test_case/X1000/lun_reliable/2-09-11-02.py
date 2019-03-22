# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-6

'''
测试内容:节点异常情况下创建逻辑卷
测试步骤：
1）创建逻辑卷
2）修改逻辑卷信息（名称，容量等），修改过程中将日志组非业务节点关机
3）保存后可生效
检查项：
修改后立即生效

'''

# testlink case: 1000-33637
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
    infos = []
    log.info("step:1.创建逻辑卷")
    env_manage.create_luns(s_ip=node_ip1)
    log.info("step:2.节点关机")
    os_type = env_manage.get_os_type(node_ip2)
    lun_ids = env_manage.osan.get_lun(s_ip=node_ip2)
    log.info("step:3.修改逻辑卷属性")
    i=0
    for id in lun_ids:
        rc = env_manage.update_luns(s_ip=node_ip1, id=id)
        if rc == id:
            i = i +1
        if i == 5:
            log.info("step:4.节点关机")
            info = env_manage.down_node(node_ip2, os_type, "init 0")
            infos.append(info)
    log.info("step:5.%s 节点开机 节点类型%s,节点ID or IPMI IP: %s" % (node_ip2, os_type, infos[0]))
    env_manage.up_node(infos[0], os_type)
    log.info("step:6.检查节点运行状态，检查服务恢复情况。")
    env_manage.com_lh.get_os_status(node_ip1)
    log.info("******************* case end ************************")


def main():
    log.info("step: checking the test environment")
    env_manage.clean_test_env()
    log.info("step: initialize node ip")
    setup()
    case()
    log.info("step:7.清理测试环境")
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)

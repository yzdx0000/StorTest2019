# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
逻辑卷删除过程中将日志组业务节点正常关机
检查项：
逻辑卷删除成功


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
    global new_node1
    node_ip1 = env_manage.deploy_ips[0]  # 业务节点IP
    node_ip2 = env_manage.deploy_ips[1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]
    new_node1 = env_manage.new_ips[0]


def remove_nodes():
    id = env_manage.node.get_node_id_by_ip(new_node1)
    env_manage.com_lh.del_node(node_ip=node_ip1, node_id=id)


def check_new_node():
    cmd = ("ssh %s \"/home/parastor/tools/deployment/uninstall_local_software.py\"" % (new_node1))
    log.info(cmd)
    rc, output = commands.getstatusoutput(cmd)
    log.info(output)
    cmd1 = ("ssh %s \"rm -rf /home/parastor/\"" % (new_node1))
    commands.getstatusoutput(cmd1)
    cmd2 = ("ssh %s \"rm -rf /core*\"" % (new_node1))
    commands.getstatusoutput(cmd2)


def create_luns():
    for i in range(10):
        lun_name = "LUN" + str(i)
        env_manage.create_lun(node_ip1, lun_name)


def case():
    log.info("*******************start case**********************")
    check_new_node()
    log.info("step:1.向xstor添加新节点,创建逻辑卷")
    env_manage.check_add_node_xml(new_node1, node_ip1)
    env_manage.com_lh.add_node(node_ip=node_ip1, config_file="/home/deploy/deploy_config_1.xml")
    create_luns()
    log.info("step:2.删除逻辑卷过程中删除一个节点")
    threads = []
    t1 = threading.Thread(target=env_manage.clean_lun, args=(node_ip1,))
    threads.append(t1)
    t2 = threading.Thread(target=remove_nodes)
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:3.清理检查环境")
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
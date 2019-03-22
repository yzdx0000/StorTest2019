# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
1）使用三个节点创建节点池创建存储池，在该存储池中创建逻辑卷，
2）创建完成后，删除逻辑卷，删除过程中从该节点池中移除一个节点
检查项：
删除无异常

'''
import os
import time
import random
import json
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
    global new_node1
    node_ip1 = env_manage.deploy_ips[0]  # 业务节点IP
    node_ip2 = env_manage.deploy_ips[1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]
    new_node1 = env_manage.new_ips[0]


def add_stor(conf):
    env_manage.check_add_node_xml(new_node1, node_ip1)
    env_manage.com_lh.add_node(node_ip=node_ip1, config_file=conf)


def check_nodes():
    cmd = ("ssh %s \"pscli --command=get_nodes\"" % (node_ip2))
    nodes_ids = []
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        node_info = common.json_loads(stdout)
        nodes = node_info['result']['nodes']
        for node in nodes:
            nodes_ids.append(node['node_id'])
    return len(nodes_ids)


def check_new_node():
    cmd = ("ssh %s \"/home/parastor/tools/deployment/uninstall_local_software.py\"" % (new_node1))
    log.info(cmd)
    rc, output = commands.getstatusoutput(cmd)
    log.info(output)
    cmd1 = ("ssh %s \"rm -rf /home/parastor/\"" % (new_node1))
    commands.getstatusoutput(cmd1)
    cmd2 = ("ssh %s \"rm -rf /core*\"" % (new_node1))
    commands.getstatusoutput(cmd2)


def del_nodes(del_ip):
    del_node_id = env_manage.com_lh.get_node_id_by_ip(node_ip=del_ip)
    env_manage.com_lh.del_node(node_ip=node_ip1, node_id=del_node_id)


def case():
    log.info("*******************start case**********************")
    log.info("step:1.检查节点数量，创建逻辑卷")
    node_nums1 = check_nodes()
    check_new_node()
    log.info("start get node number :%s" % (node_nums1))
    env_manage.create_luns()
    log.info("step:2.删除逻辑卷过程中添加节点")
    threads = []
    t1 = threading.Thread(target=env_manage.clean_lun, args=(node_ip1,))
    threads.append(t1)
    t2 = threading.Thread(target=add_stor, args=("/home/deploy/deploy_config_1.xml",))
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("step:3.检查节点数量")
    node_nums2 = check_nodes()
    log.info("get numbers of node :%s" % (node_nums2))
    if node_nums2 - node_nums1 == 1:
        log.info("step:4.节点添加成功")
        return
    else:
        log.error("add node failed")
        exit(1)
    log.info("******************* case end ************************")


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:5.清理检查测试环境")
    del_nodes(new_node1)
    env_manage.clean_lun()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)

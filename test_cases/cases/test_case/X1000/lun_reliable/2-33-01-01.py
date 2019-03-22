#!usr/bin/env python
# -*- coding:utf-8 _*-
'''
测试步骤：
1）配置节点池，配置存储池
2）配置访问区，非日志节点数据网+日志组业务节点异常，创建/删除访问区
检查项：
1）访问区配置成功
2）逻辑卷创建成功
'''

# testlink case: 1000-33986
import os
import time
import random
import commands
import threading
import utils_path
import log
import common
import access_env
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
    global node_ip3
    global client_ip1
    node_ip1 = env_manage.deploy_ips[0]
    node_ip2 = env_manage.deploy_ips[1]
    node_ip3 = env_manage.deploy_ips[2]
    client_ip1 = env_manage.client_ips[0]


ojmgs_ips = []
test_net_ip = []
create_lun_ip = []
os_types = []
infos = []


def check_ip():
    ojmgs_id, ojmgs_ip = env_manage.com_lh.oJmgs_master_id()
    if ojmgs_ip == node_ip1:
        ojmgs_ips.append(ojmgs_ip)
        test_net_ip.append(ojmgs_ip)
        create_lun_ip.append(node_ip2)
    elif ojmgs_ip == node_ip2:
        ojmgs_ips.append(ojmgs_ip)
        test_net_ip.append(node_ip1)
        create_lun_ip.append(node_ip3)
    else:
        ojmgs_ips.append(ojmgs_ip)
        test_net_ip.append(node_ip1)
        create_lun_ip.append(node_ip2)


def node_pro_test(eth_name):
    ReliableTest.run_kill_process(node_ip=ojmgs_ips[0], process="oJmgs")
    os_type = env_manage.get_os_type(eth_name)
    info = env_manage.down_node(eth_name, os_type, "init 0")
    os_types.append(os_type)
    infos.append(info)


def create_access():
    env_manage.deploy_ips.remove(ojmgs_ips[0], test_net_ip[0])
    node_ids = []
    for ip in env_manage.deploy_ips:
        node_id = env_manage.com_lh.get_node_id_by_ip(ip)
        node_ids.append(node_id)
    env_manage.create_access(create_lun_ip[0], node_ids, "accesszone1")


def case():
    check_ip()
    threads = []
    t1 = threading.Thread(target=node_pro_test, args=(test_net_ip[0],))
    threads.append(t1)
    t2 = threading.Thread(target=create_access)
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    env_manage.up_node(infos[0], os_types[0])
    log.info("step：4、检查节点运行状态，检查服务恢复情况。")
    rc = env_manage.com_lh.get_os_status(test_net_ip[0])
    if rc == 0:
        return


def main():
    access_env.check_env()
    setup()
    case()
    env_manage.clean_access_zone()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=5)
    common.case_main(main)
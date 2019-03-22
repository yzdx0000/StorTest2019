#!usr/bin/env python
# -*- coding:utf-8 _*-
'''
测试步骤：
1）配置访问区，创建逻辑卷
2）修改过程中制造日志组业务节点+日志组非业务节点oRole进程异常
检查项：
1）访问区配置成功
2）逻辑卷修改成功
'''

# testlink case: 1000-33927
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
    global node_ip3
    global client_ip1
    node_ip1 = env_manage.get_inter_ids()[0]  # 业务节点IP
    node_ip2 = env_manage.get_inter_ids()[-1]  # 非业务节点IP
    node_ip3 = env_manage.get_inter_ids()[1]
    client_ip1 = env_manage.client_ips[0]


pro_ips = []
test_net_ip = []
create_lun_ip = []


def check_ip():
    orole_ip = env_manage.com_lh.get_master_oRole(node_ip1)
    if orole_ip == node_ip1:
        pro_ips.append(orole_ip)
        test_net_ip.append(orole_ip)
        create_lun_ip.append(node_ip2)
    elif orole_ip == node_ip2:
        pro_ips.append(orole_ip)
        test_net_ip.append(node_ip1)
        create_lun_ip.append(node_ip3)
    else:
        pro_ips.append(orole_ip)
        test_net_ip.append(node_ip1)
        create_lun_ip.append(node_ip2)


def net_prro_test(net_name):
    ReliableTest.run_kill_process(node_ip=pro_ips[0], process="oRole")
    env_manage.down_network(test_net_ip[0], net_name)


def case():
    env_manage.create_luns()
    check_ip()
    data_net = env_manage.com_lh.get_eth_name(s_ip=test_net_ip[0])[1]
    threads = []
    t1 = threading.Thread(target=net_prro_test, args=(data_net,))
    threads.append(t1)
    t2 = threading.Thread(target=env_manage.update_luns, args=(create_lun_ip[0],))
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    env_manage.up_network(test_net_ip[0], data_net)


def main():
    env_manage.clean_test_env()
    setup()
    case()
    env_manage.clean_lun()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
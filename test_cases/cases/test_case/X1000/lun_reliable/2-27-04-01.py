#!usr/bin/env python
# -*- coding:utf-8 _*-
'''
测试步骤：
1）配置访问区，映射逻辑卷到主机
2）制造日志组业务节点+日志组非业务节点oPmgr进程异常
检查项：
1）访问区配置成功
2）逻辑卷成功映射
'''

# testlink case: 1000-33911
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


orole_ips = []
power_ips = []
create_lun_ip = []
os_types = []
infos = []


def check_ip():
    '''
    获取和分配故障节点IP，kill进程的IP，创建逻辑卷的节点IP
    :return:
    '''
    orole_ip = env_manage.com_lh.get_master_oRole(node_ip1)
    if orole_ip == node_ip1:
        orole_ips.append(orole_ip)
        power_ips.append(orole_ip)
        create_lun_ip.append(node_ip2)
    elif orole_ip == node_ip2:
        orole_ips.append(orole_ip)
        power_ips.append(node_ip1)
        create_lun_ip.append(node_ip3)
    else:
        orole_ips.append(orole_ip)
        power_ips.append(node_ip1)
        create_lun_ip.append(node_ip2)


def running_break():
    env_manage.com_lh.kill_thread(s_ip=orole_ips[0], p_name="oRole", t_name="pmgr")
    os_type = env_manage.get_os_type(power_ips[0])
    info = env_manage.down_node(power_ips[0], os_type, "init 0")
    os_types.append(os_type)
    infos.append(info)


def case():
    log.info("step:1.创建逻辑卷，检查系统IP")
    env_manage.create_lun()
    check_ip()
    log.info("step:2.杀进程关节点时映射逻辑卷")
    check_ip()
    threads = []
    t1 = threading.Thread(target=running_break)
    threads.append(t1)
    t2 = threading.Thread(target=env_manage.create_lun_map, args=(create_lun_ip[0],))
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("step:3.%s 节点开机" % (power_ips[0]))
    env_manage.up_node(infos[0], os_types[0])
    log.info("step:4.等待节点和服务恢复")
    env_manage.com_lh.get_os_status(power_ips[0])


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:5.检查清理测试环境")
    env_manage.clean_lun_map()
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
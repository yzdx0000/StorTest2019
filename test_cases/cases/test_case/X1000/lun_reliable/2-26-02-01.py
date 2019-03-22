#!usr/bin/env python
# -*- coding:utf-8 _*-

'''
测试步骤：
1）配置访问区，移除存储节点
2）制造日志组业务节点+日志组非业务节点数据网故障
3）删除逻辑卷
检查项：
1）访问区配置成功
2）逻辑卷删除成功
'''

# testlink case: 1000-33893
import os
import time
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


infos = []
os_types = []


def node_off():
    type = env_manage.get_os_type(node_ip1)
    info = env_manage.down_node(node_ip1, type, "init 0")
    os_types.append(type)
    infos.append(info)


def net_down(s_ip, name):
    env_manage.down_network(s_ip, name)


def case():
    data_net = env_manage.com_lh.get_eth_name(node_ip2)[1]
    log.info("step:1.创建逻辑卷")
    env_manage.create_lun()
    log.info("step:2.删除逻辑卷过程中将一个业务节点关机和非业务节点网卡断开")
    threads = []
    t1 = threading.Thread(target=node_off)
    threads.append(t1)
    t2 = threading.Thread(target=env_manage.clean_lun, args=(node_ip3,))
    threads.append(t2)
    t3 = threading.Thread(target=net_down, args=(node_ip2, data_net))
    threads.append(t3)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("step:3.节点开机，恢复网卡")
    env_manage.up_node(infos[0], os_types[0])
    env_manage.up_network(node_ip2, data_net)
    log.info("step:4.等待节点和服务恢复")
    env_manage.com_lh.get_os_status(node_ip1)


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:5.检查清理测试环境")
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, jnl_rep=3,free_jnl_num=0, node_num=5)
    common.case_main(main)
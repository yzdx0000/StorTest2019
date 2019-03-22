# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-10
'''
测试内容：删除逻辑卷时日志组非业务节点数据网断开
测试步骤：
1）创建多访问区，配置访问区
2）删除逻辑卷
3）删除时将日志组业务节点数据网断开
检查项：
1）访问区配置成功
2）逻辑卷删除成功

'''

# testlink case: 1000-33861
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


def down_network(ipaddr, name):
    rc = env_manage.com_lh.get_cmd_status(node_ip1, "delete_lun_map")
    if rc == 0:
        log.info("关闭节点 %s 网卡 %s " % (ipaddr, name))
        env_manage.down_network(ipaddr, name)
        return
    elif rc == 1:
        log.error("Not find CMD ,timeout will exit")
        os._exit(1)


def create_luns():
    for i in range(10):
        lun_name = "LUN" + str(i)
        env_manage.create_lun(node_ip1, lun_name)


def case():
    data_net = env_manage.com_lh.get_eth_name(s_ip=node_ip2)[1]
    log.info("step:1.创建逻辑卷，创建lun map")
    create_luns()
    env_manage.create_lun_map()
    log.info("step:2.删除lun map过程中断开网卡")
    threads = []
    t1 = threading.Thread(target=down_network, args=(node_ip2, data_net))
    threads.append(t1)
    t2 = threading.Thread(target=env_manage.clean_lun_map, args=(node_ip1,))
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("step:3.恢复网卡")
    env_manage.up_network(ipaddr=node_ip2, name=data_net)


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:4.清理检查环境")
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-10
'''
测试内容：创建逻辑卷时异常
测试步骤：
1）创建多访问区，配置访问区
2）创建逻辑卷
3）将日志组业务节点业务网断开
检查项：
1）访问区配置成功
2）逻辑卷创建成功

'''

# testlink case: 1000-33880
import os
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
    rc = env_manage.com_lh.get_cmd_status(node_ip2, "create_lun")
    if rc == 0:
        env_manage.down_network(ipaddr, name)
        return
    elif rc == 1:
        log.error("Not find CMD ,timeout will exit")
        os._exit(1)


def case():
    subnet_eth = env_manage.com_lh.get_vip_eth_name(node_ip1)
    log.info("step:1.创建逻辑卷过程中关闭网卡")
    threads = []
    t1 = threading.Thread(target=down_network, args=(node_ip1, subnet_eth))
    threads.append(t1)
    t2 = threading.Thread(target=env_manage.create_lun, args=(node_ip2, "LUN1"))
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("step:2.恢复网卡")
    env_manage.up_network(node_ip1, subnet_eth)


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:3.清理检查环境")
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)

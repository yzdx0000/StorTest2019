# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-10
'''
测试内容：创建逻辑卷后日志组业务节点数据网异常
测试步骤：
1）创建逻辑卷创建完成后映射至主机日志组业务节点数据网断开
2）检查逻辑卷状态
3）对逻辑卷进行读写
检查项：
1）逻辑卷状态显示正常
2）可正常读写

'''

# testlink case: 1000-33855
import os
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
    log.info("step:1.创建逻辑卷")
    data_net = env_manage.com_lh.get_eth_name(s_ip=node_ip2)[1]
    env_manage.create_lun()
    log.info("step:2.关闭网卡")
    env_manage.down_network(ipaddr=node_ip2, name=data_net)
    log.info("step:3.检查逻辑卷")
    env_manage.osan.get_lun(node_ip1)
    log.info("step:4.恢复网卡")
    env_manage.up_network(ipaddr=node_ip2, name=data_net)


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:5.清理测试环境")
    env_manage.clean_lun()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)

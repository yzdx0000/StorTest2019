# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-10
'''
测试内容：业务网闪断时解除映射
测试步骤：
1）创建逻辑卷创建完成后映射至主机将日志组业务节点业务网闪断5次
2）检查逻辑卷状态
3）删除逻辑卷映射关系
4）删除逻辑卷
检查项：
1）逻辑卷状态显示正常
2）逻辑卷可正常删除

'''

# testlink case: 1000-33874
import os
import time
import commands
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



def network_test(node_ip, eth):
    env_manage.com_lh.net_flash_test(node_ip, eth)


def case():
    subnet_eth = env_manage.com_lh.get_vip_eth_name(node_ip1)
    log.info("step:1.创建逻辑卷，创建lun map")
    env_manage.create_lun()
    env_manage.create_lun_map()
    log.info("step:2.网卡闪断")
    network_test(node_ip1, subnet_eth)
    log.info("step:3.检查lun map")
    env_manage.osan.get_lun_maps(node_ip1)
    log.info("step:4.清理lun map")
    env_manage.clean_lun_map()


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:5.清理检查测试环境")
    env_manage.clean_lun()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
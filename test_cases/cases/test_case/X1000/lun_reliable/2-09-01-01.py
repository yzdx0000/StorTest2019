# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-6

"""
测试内容:节点异常情况下创建逻辑卷
测试步骤：
1）创建多个访问区，配置访问区配置逻辑卷前将日志组业务节点正常关机
2）创建逻辑卷
检查项：
逻辑卷创建成功
"""
# testlink case: 1000-33617
import os
import utils_path
import log
import common
import env_manage

'''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log


def setup():
    """Define node IP"""
    global node_ip1
    global node_ip2
    global client_ip1
    node_ip1 = env_manage.get_inter_ids()[0]  # 业务节点IP
    node_ip2 = env_manage.get_inter_ids()[-1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def case():
    log.info("******************* case start **********************")
    log.info("step：1、the business node is going to shutdown")
    os_type = env_manage.get_os_type(node_ip1)
    info = env_manage.down_node(node_ip1, os_type, "init 0")
    log.info("step：2、create lun。")
    env_manage.create_luns(s_ip=node_ip2)
    log.info("step：3、%s node will start up,The node type:%s, and ID or IPMI IP: %s" % (node_ip1, os_type, info))
    env_manage.up_node(info, os_type)
    log.info("step：4、The node os status and services are checked。")
    env_manage.com_lh.get_os_status(node_ip1)
    # env_manage.com_bd_disk.multi_check_part_lun_uniform_by_ip()  # 校验一致性
    log.info("******************* case end ************************")


def main():
    log.info("step: checking the test environment")
    env_manage.clean_test_env()
    log.info("step: initialize node ip")
    setup()
    case()
    log.info("step:5.The test environment will be cleaned up.")
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)

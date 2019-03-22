# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:访问区创建

步骤:
1）配置节点池设置副本数为3
2）创建存储池，使用全部磁盘
3）通过管理端cli命令创建访问区

检查项:
1）节点池创建成功
2）存储池创建成功
3）访问区创建成功
"""
import os, sys
import random
import time
import utils_path
import Lun_managerTest
import common
import log
import error
import get_config
import login
import error
import decorator_func
from get_config import config_parser as cp
import env_manage_lun_manage

node_ip1 = env_manage_lun_manage.deploy_ips[0]

file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件


def case():
    node_pool_id = env_manage_lun_manage.osan.get_option(s_ip=node_ip1, command="get_node_pools", indexname="node_pools",
                                                         argv="id")[-1]

    env_manage_lun_manage.osan.startup(s_ip=node_ip1)
    env_manage_lun_manage.osan.create_storage_pool(s_ip=node_ip1, node_pool_ids=node_pool_id, name='pool1')
    node_ids_list = env_manage_lun_manage.osan.get_nodes(node_ip1)
    node_ids = ",".join('%s' % id for id in node_ids_list)
    az_id = env_manage_lun_manage.osan.create_access_zone(s_ip=node_ip1,
                                    node_id="{},{}".format(node_ids_list[0], node_ids_list[1],
                                    name='accesszonetest'))

def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean(target="storage_pool")
    case()  # 用例步骤

    env_manage_lun_manage.init_env(reboot_node=1)  # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()
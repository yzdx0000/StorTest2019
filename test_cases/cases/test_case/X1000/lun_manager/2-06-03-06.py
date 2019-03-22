# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:删除多个存储池

步骤:
1、选择3个节点创建节点池
2、创建3个存储池，使用全部磁盘
3、删除2个存储池

检查项:
1、节点池创建成功
2、存储池创建成功
3、存储池删除成功
"""
# testlink case: 1000-34060
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

node_ip = env_manage_lun_manage.deploy_ips[0]

file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件


def case():
    sto_pool_ids = env_manage_lun_manage.osan.get_storage_id(s_ip=node_ip)
    if len(sto_pool_ids) >= 2:
        sto_pool_ids.remove(1)  # 列表删除共享池
        log.info(sto_pool_ids)
        env_manage_lun_manage.osan.delete_storage_pool(s_ip=node_ip, id=sto_pool_ids[0])
        env_manage_lun_manage.osan.delete_storage_pool(s_ip=node_ip, id=sto_pool_ids[1])




def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    # env_manage_lun_manage.rel_check_before_run(filename=file_name)  # 环境检测和准备
    env_manage_lun_manage.init_env(target="create_storage_pool",reboot_node=1,storage_pool_num=3)
    case()  # 用例步骤
    decorator_func.pass_flag()
    env_manage_lun_manage.init_env(reboot_node=1) # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试


if __name__ == '__main__':
    main()

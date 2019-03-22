#!usr/bin/env python  
# -*- coding:utf-8 -*-
"""
:author: Liu he
:Description:
@file: 5-01-01-01.py
@time: 2018/11/01
"""

import os
import re
import time
import json
import utils_path
import Lun_managerTest
import common
import common2
import commands
import breakdown
import log
import env_cache
import env_manage
import prepare_x1000
import get_config

'''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)
# env_cache.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)

conf_file = get_config.CONFIG_FILE  # 配置文件路径
deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP

'''定义节点IP'''
node_ip1 = env_cache.deploy_ips[0]
client_ip = env_cache.client_ips[0]

test = ['a', 'b', 'c', 'd']
print test[2:3]
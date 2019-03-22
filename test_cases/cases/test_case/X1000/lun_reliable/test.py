#!usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author: Liu he
@file: test.py 
@time: 2018/10/31 
"""

import os
import re
import sys
import time
import inspect
import random
import xml
import xml.dom.minidom
import utils_path
import Lun_managerTest
import common
import common2
import commands
import breakdown
import env_manage
import log
import json
import prepare_x1000
import prepare_x1000
import get_config

import decorator_func
import ReliableTest
import access_env

# 初始化配置文件
conf_file = get_config.CONFIG_FILE
deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP

# '''日志初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log

log.init(log_file_path, True)
#
# 类实例化
osan = Lun_managerTest.oSan()
com_lh = breakdown.Os_Reliable()
com_disk = common.Disk()
node = common.Node()
com2_osan = common2.oSan()
com_bd_disk = breakdown.disk()

node_ip1 = env_manage.deploy_ips[0]  # 业务节点IP
node_ip2 = env_manage.deploy_ips[1]  # 非业务节点IP
client_ip1 = env_manage.client_ips[0]

orole_ip = env_manage.com_lh.get_master_oRole(node_ip1)
node_id = env_manage.com_lh.get_node_id_by_ip(orole_ip)  # 拿到主orole id
nodes_id = env_manage.osan.get_nodes(node_ip1)  # 获取全部ID

print node_ip1
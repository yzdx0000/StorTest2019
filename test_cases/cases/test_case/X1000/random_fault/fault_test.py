#!usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
:author: Liu he
:Description:
@file: fault_test.py 
@time: 2018/12/27 
"""  
import os
import re
import sys
import time
import inspect
import random
import datetime
import utils_path
import Lun_managerTest
import common
import common2
import commands
import breakdown
import log
import json
import disk
import prepare_x1000
# import prepare_clean
# import prepare_x1000
import get_config
from get_config import config_parser as cp
import decorator_func
import ReliableTest
import env_manage
import env

file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)

env.prepare()


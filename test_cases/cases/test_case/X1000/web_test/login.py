#!usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
:author: Liu he
:Description:
@file: login.py 
@time: 2019/03/16 
"""
import utils_path
import time
import os
import common
import log
import prepare_clean
import quota_common
import get_config
import web_common
from selenium import webdriver
from selenium.webdriver.support.select import Select

'''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
current_path = os.path.dirname(os.path.abspath(__file__))

driver = web_common.init_web_driver()

#!usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
:author: Liu he
:Description:
@file: qqq.py 
@time: 2018/12/26 
"""
import os
# import re
# import sys
# import time
# import json
# import signal
# import random
# import traceback
# import threading
# import subprocess
# import commands
# import xml.dom.minidom
# from optparse import OptionParser
# from multiprocessing import Process
import utils_path
import log
import env_manage

file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)

oper = 1
aaa = str(oper)
print type(aaa)
print aaa
print type(eval(aaa))
print list(eval(aaa))
# nnn = list(eval(aaa))
# print nnn

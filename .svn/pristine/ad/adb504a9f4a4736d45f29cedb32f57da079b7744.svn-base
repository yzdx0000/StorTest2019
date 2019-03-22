#!/bin/python
# -*-coding:utf-8 -*
import os
import sys
import threading
from multiprocessing.process import Process
import time
import signal
import subprocess
##########################################
#
# Author: duyuli
# date 2019-03-13
# @summary：
# 开发用例编写模板,需要并发时执行
# @changelog：
##########################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
# 开发并行用例列表
path_list = ["a.sh", "b.sh"]

def func(path):
    exe = ""
    if path.endswith(".sh"):
        exe = "sh"
    if path.endswith(".py"):
        exe = "python -u"
    cmd = "cd %s;%s %s" % (FILE_DIR, exe, path)
    print cmd
    return cmd

def print_stdout(process):
    while True:
        line = process.stdout.readline()
        if '' == line:
            break
        print (line.rstrip())
    return

def case():
    th_list = []

    for path in path_list:
        cmd = func(path)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        th_list.append(process)

    for th in th_list:
        thd = threading.Thread(target=print_stdout, args=(th,))
        thd.setDaemon(True)
        thd.start()

    flag = True
    while flag:
        for t in th_list:
            if t.poll() is not None:
                if t.returncode == 0:
                    print "%s success" % FILE_NAME
                    flag = False
                    break
                else:
                    raise Exception("%s exe error")

    for t in th_list:
        if t.poll() is None:
            t.terminate()


if __name__ == '__main__':
    case()
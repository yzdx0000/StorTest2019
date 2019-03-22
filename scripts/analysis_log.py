#!/usr/bin/python
# -*- conding:utf-8 -*-
# The Author:wuyuqiao
# Create Date:2018/12/17
# Fuction:Analysis the log of failed case
# Rusult: log file log_info
# Parameter:None ,case dirnmae,eg.3-01-01-08

import os
import sys
import time
import commands

log_lines = 25 #the bottom lines you want to watch
bug_dir = os.getcwd()
log_info = bug_dir+'/log_info'
if os.path.isfile(log_info) == True:
    os.remove(log_info)
if len(sys.argv) == 1:
    print('Default analyze all cases dirname logs.')
    print('If you want specified cases,please add log dirname.')
    time.sleep(3)
    log_list = os.listdir(bug_dir)
    logs = log_list[:]
    for log in log_list:
       log_path = os.path.join(bug_dir,log)
       if os.path.isfile(log_path):
           logs.remove(log)
    print logs
else:
    case_list = sys.argv[1:]
    for case in case_list:
        print('%s logs will be analyzed...' % case)
    logs = case_list

def put(stdin):
    print(stdin)
    with open(log_info,'a+') as record:
        record.write(stdin)
        record.write('\n')

def check_core(dir_name):
    if dir_name == None:
        put("the parmfile is not a dirname!")
        return 1
    else:
        os.chdir(dir_name)
        tmp_dir = os.listdir('.')
        data_dir = tmp_dir[-1]
        os.chdir(data_dir)
        put('*-*-*-*-*-*-*-*-* case_SN: %s *-*-*-*-*-*-*-*-*' % dir_name)
        log_dir = None
        dir_len = 0
        for log_file in os.listdir('.'):
            if len(log_file) >= dir_len:
                dir_len = len(log_file)
                log_dir = log_file
        os.chdir(log_dir)
        log_name = os.listdir('.')[0]
        cmd = ('tail -n %d %s' % (log_lines, log_name))
        rc,stdout = commands.getstatusoutput(cmd)
        if rc != 0:
            put("Open the case log failed.Please check!")
        else:
            put(stdout)
    put('*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n')
    put('')
    os.chdir(bug_dir)

if __name__ == '__main__':
    for log in logs:
        check_core(log)


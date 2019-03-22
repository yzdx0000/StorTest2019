#!/usr/bin/python
# -*- conding:utf-8 -*-
# The Author:wuyuqiao
# Create Date:2018/12/17
# Fuction:Analysis all cores in logs
# Rusult: log file core_info
# Parameter:None ,case dirnmae,eg.3-01-01-08

import os
import sys
import time
import commands

bug_dir = os.getcwd()
core_info = bug_dir+'/core_info'
if os.path.isfile(core_info) == True:
    os.remove(core_info)
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
else:
    case_list = sys.argv[1:]
    for case in case_list:
        print('%s logs will be analyzed...' % case)
    logs = case_list
'''
def put(stdin):
    print(stdin)
    with open(core_info,'a+') as record:
        record.write(stdin)
        record.write('\n')
'''

def check_core(dir_name):
    if dir_name == None:
        print("the parmfile is not a dirname!")
        return 1
    else:
        os.chdir(dir_name)
        tmp_dir = os.listdir('.')
        data_dir = tmp_dir[-1]
        os.chdir(data_dir)
        print('*-*-*-*-*-*-*-*-* case_SN: %s *-*-*-*-*-*-*-*-*' % dir_name)
        ser_logs = [log for log in os.listdir('.') if 'ser' in log]
        for ser_log in ser_logs:
            cmd = ('ls %s/pro_log | grep core' % ser_log)
            rc,stdout = commands.getstatusoutput(cmd)
            if rc != 0:
                print("server log %s doesn't have any core" % ser_log)
            else:
                cores = stdout.split('\n')
                print('###### server log %s core: %s ######' % (ser_log, cores))
                for core in cores:
                    cmd = ('file %s/pro_log/%s' % (ser_log, core))
                    result = commands.getoutput(cmd)
                    info = result.split(',')[3]
                    print('------------------------------------------------------------------')
                    print('%s is%s' % (core,info))
                    core_ls = info.split('/')[-1]
                    core_type = core_ls[:-1]
                    os.system('echo "bt" >bt')
                    cmd = ('gdb %s/bin/%s %s/pro_log/%s <bt' % (ser_log, core_type, ser_log, core))
                    result = commands.getoutput(cmd)
                    core_info = result.split('\n')
                    for line in core_info:
                        if '#0' in line:
                            s_num = core_info.index(line)
                    core_stack = core_info[s_num:-1]
                    print('%s stack:\n%s' % (core, '\n'.join(core_stack)))
    print('*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n')
    os.chdir(bug_dir)

if __name__ == '__main__':
    for log in logs:
        check_core(log)


#!/usr/bin/python
#-*-coding:utf-8-*-

################################################################################
#                                                                              #
#        Copyright (C), 1995-2014, Sugon Information Industry Co., Ltd.        #
#                                                                              #
################################################################################
# File Name     : tc_run.py                                                    #
# Module Name   : Testing Framework                                            #
# Version       : 1.0.0                                                        #
# Author        : Zhang Jianbin <zhangjb@sugon.com>                            #
# Created Date  : 2014/05/05                                                   #
# Description   : DLM common module                                            #
#                                                                              #
# History       :                                                              #
# 1.Date         : 2014/05/05                                                  #
#   Author       : Zhang Jianbin <zhangjb@sugon.com>                           #
#   Modification : Creating file                                               #
#                                                                              #
################################################################################
import commands, string, os, sys
from dlm_print import *
from threading import Thread

# SSH ip, and exec command
def ssh2(ip, user, passwd, cmd, callback):
    try: 
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,port=22,username=user,password=passwd)
        
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read()
        callback(out)
            
        print_beauty('%s OK' %(ip))
        ssh.close()
    except:
        print_beauty('%s Error' %(ip))

# Create thread for execing remote command
def dlm_remote_exec_cmd(key, item):
    username = 'root'
    passwd = '111111'
    
    print_a_hash_line()
    print_beauty('%s START' %(key))

    for i in range(len(item)):
        print_a_hash_line()
        ssh2(item[i][0], username, passwd, item[i][1], item[i][2])

    print_a_hash_line()
    print_beauty('%s END' %(key))
 

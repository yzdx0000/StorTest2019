#!/usr/bin/python
# -*- encoding=utf8 -*-

import os
import json
import shell
import time
import subprocess
import commands
import log
import get_config
import sys
import re
import random
import datetime
import ReliableTest
import common
reload(sys)
sys.setdefaultencoding('utf-8')

def write_line(s_ip,c_ip,f_name,final1):
    final1 = re.sub('( ){11,}','\n',final1)
    final1 = re.sub('\(|\)',':',final1)
    for line in final1.split('\n'):
        if len(line) < 1:
            continue
#        elif re.search('.*:.*:',line):
#            cmd = ("ssh %s 'echo -e %s >> /root/vdb_summary/%s/%s.dpc'" %(c_ip,line,s_ip,f_name))
#            (res, final) = commands.getstatusoutput(cmd)
#        elif line.strip().split(':')[1] == "0":
#            continue
        cmd = ("ssh %s 'mkdir -p /root/vdb_summary/%s/%s'" % (c_ip, s_ip, f_name))
        commands.getstatusoutput(cmd)
        cmd = ("ssh %s 'echo %s >> /root/vdb_summary/%s/%s/%s.dpc'" %(c_ip,line,s_ip,f_name,f_name))
        (res, final) = commands.getstatusoutput(cmd)

def dpc_wb_bw(s_ip,c_ip,f_name):
    '''
    date    :   2018-07-14
    Description :   
    param   :   s_ip : iscsi服务端IP; node_id : 节点ID; name : 访问区名称
    return  :   
    '''
    
    cmd = ("ssh %s '/home/parastor/tools/nWatch -t oSan -i 1 -c oSan#dpc_wb_bw  | tail -3'" %(s_ip))
    (res, final1) = commands.getstatusoutput(cmd)
    if res != 0:
        print "dpc_wb_bw failed."
        return
    else:
        cmd = ("ssh %s 'mkdir -p /root/vdb_summary/%s/%s'" % (c_ip, s_ip, f_name))
        commands.getstatusoutput(cmd)
        cmd = ("ssh %s 'echo -e \#\#\#\#\#\#\#\#\#\#\#   dpc_wb_bw : \#\#\#\#\#\#\#\#\# >> /root/vdb_summary/%s/%s/%s.dpc '" %(c_ip,s_ip,f_name,f_name))
        (res, final) = commands.getstatusoutput(cmd)
        write_line(s_ip,c_ip,f_name,final1)
def dpc_stats(s_ip,c_ip,f_name):
    '''
    date    :   2018-07-14
    Description :   
    param   :   s_ip : iscsi服务端IP; node_id : 节点ID; name : 访问区名称
    return  :   
    '''
    cmd = ("ssh %s '/home/parastor/tools/nWatch -t oSan -i 1 -c oSan#dpc_stats  | grep lpc_zalloc'" %(s_ip))
    (res, final1) = commands.getstatusoutput(cmd)
    if res != 0:
        print "dpc_stats failed."
        return
    else:
        cmd = ("ssh %s 'mkdir -p /root/vdb_summary/%s/%s'" % (c_ip, s_ip, f_name))
        commands.getstatusoutput(cmd)
        cmd = ("ssh %s 'echo -e \#\#\#\#\#\#\#\#\#\#\#  dpc_stats : \#\#\#\#\#\#\#\#\# >> /root/vdb_summary/%s/%s/%s.dpc '" %(c_ip,s_ip,f_name,f_name))
        (res, final) = commands.getstatusoutput(cmd)
        write_line(s_ip,c_ip,f_name,final1)
def dpc_concur_stats(s_ip,c_ip,f_name):
    '''
    date    :   2018-07-14
    Description :   
    param   :   s_ip : iscsi服务端IP; node_id : 节点ID; name : 访问区名称
    return  :   
    '''
    cmd = ("ssh %s '/home/parastor/tools/nWatch -t oSan -i 1 -c oSan#dpc_concur_stats'" %(s_ip))
    (res, final1) = commands.getstatusoutput(cmd)
    if res != 0:
        print "dpc_concur_stats failed."
        return
    else:
        cmd = ("ssh %s 'mkdir -p /root/vdb_summary/%s/%s'" % (c_ip, s_ip, f_name))
        commands.getstatusoutput(cmd)
        cmd = ("ssh %s 'echo -e \#\#\#\#\#\#\#\#\#\#\#  dpc_concur_stats : \#\#\#\#\#\#\#\#\# >> /root/vdb_summary/%s/%s/%s.dpc '" %(c_ip,s_ip,f_name,f_name))
        (res, final) = commands.getstatusoutput(cmd)
        write_line(s_ip,c_ip,f_name,final1)
def dpc_io_stats(s_ip,c_ip,f_name):
    '''
    date    :   2018-07-14
    Description :   
    param   :   s_ip : iscsi服务端IP; node_id : 节点ID; name : 访问区名称
    return  :   
    '''
    cmd = ("ssh %s '/home/parastor/tools/nWatch -t oSan -i 1 -c oSan#dpc_io_stats | grep -E \"cnt|request\" | grep -E -v \"ahead|dalloc|rebuild|dpci\"'" %(s_ip))
    (res, final1) = commands.getstatusoutput(cmd)
    if res != 0:
        print "dpc_io_stats failed."
        return
    else:
        cmd = ("ssh %s 'mkdir -p /root/vdb_summary/%s/%s'" % (c_ip, s_ip, f_name))
        commands.getstatusoutput(cmd)
        cmd = ("ssh %s 'echo -e \#\#\#\#\#\#\#\#\#\#\#  dpc_io_stats : \#\#\#\#\#\#\#\#\# >> /root/vdb_summary/%s/%s/%s.dpc '" %(c_ip,s_ip,f_name,f_name))
        (res, final) = commands.getstatusoutput(cmd)
        write_line(s_ip,c_ip,f_name,final1)

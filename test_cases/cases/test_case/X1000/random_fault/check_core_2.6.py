#!/usr/bin/python
# -*- encoding=utf8 -*-

import os
import sys
import commands
import json

node_ips = []

core_stack_lst = []

core_exist_flag = False

CORE_PATH_lst = ['/home/parastor/log/', '/']


def json_loads(stdout):
    # stdout_str = stdout.replace('\n', '')
    # stdout_str = stdout_str.replace('\\', '')
    stdout_str = json.loads(stdout, strict=False)
    return stdout_str


# 获取集群内所有节点的ip
cmd = "pscli --command=get_nodes"
rc, result = commands.getstatusoutput(cmd)
if 0 != rc:
    raise Exception("There is not parastor or get nodes ip failed!!!")
else:
    result = json_loads(result)
    nodes_lst = result['result']['nodes']
    for node in nodes_lst:
        node_ips.append(node['ctl_ips'][0]['ip_address'])

cmd = "pscli --command=get_clients"
rc, result = commands.getstatusoutput(cmd)
if 0 != rc:
    raise Exception("There is not parastor or get nodes ip failed!!!")
else:
    result = json_loads(result)
    nodes_lst = result['result']
    for node in nodes_lst:
        if node['type'] == 'INTERNAL':
            continue
        node_ips.append(node['ip'])


def get_core_file(node_ip):
    '''
    检查节点上是否有core
    '''
    core_file_lst = []
    for core_path in CORE_PATH_lst:
        cmd = 'ssh %s "ls %score*"' % (node_ip, core_path)
        rc, result = commands.getstatusoutput(cmd)
        if rc == 0:
            core_lst = result.split()
            core_file_lst.extend(core_lst)
    return core_file_lst


for node in node_ips:
    # 检查节点上是否有core
    core_lst = get_core_file(node)
    if not core_lst:
        continue
    # 系统内有一个core就说明有core
    core_exist_flag = True

    print 'node:%s' % node, core_lst
    for core in core_lst:
        # get core name
        core_dir = {}
        core_dir['name'] = core

        # 用file命令获取产生core的进程
        cmd1 = 'ssh %s "file %s"' % (node, core)
        rc, result = commands.getstatusoutput(cmd1)
        if 0 != rc:
            continue
        result_lst = result.split(",")
        if len(result_lst) < 2:
            continue
        for result_mem in result_lst:
            if 'from' in result_mem:
                core_dir['module'] = result_mem.split("'")[1].split()[0]

        # 获取core的栈
        cmd1 = 'ssh %s "echo bt > /tmp/cmd"' % (node)
        rc, result = commands.getstatusoutput(cmd1)
        if 0 != rc:
            raise Exception("%s failed!!!" % cmd1)

        cmd2 = 'ssh %s "gdb %s %s < /tmp/cmd"' % (node, core_dir['module'], core_dir['name'])
        rc, result = commands.getstatusoutput(cmd2)
        if 0 != rc:
            continue
        stack_lst = result.split('\n')
        i = 0
        for line in stack_lst:
            if line.startswith('(gdb)'):
                break
            i += 1
        length = len(stack_lst)
        function_lst = []

        # 判断core的栈是否已经有了，判断标准栈的每层函数是否一致
        for j in range(i, length):
            if j == i:
                function_lst.append(stack_lst[j].split()[4])
                continue
            else:
                if '#' in stack_lst[j]:
                    function_lst.append(stack_lst[j].split()[3])
                    continue

        flag = False
        for mem in core_stack_lst:
            if mem == function_lst:
                flag = True
                break
        if flag is True:
            continue
        # 之前没有这个core，则把栈的函数列表加到全局列表中
        core_stack_lst.append(function_lst)

        # 打印栈
        print '\n'
        print ("-------------------- %s     %s     %s --------------------" % (node, core_dir['module'], core_dir['name']))
        for j in range(i, length):
            if '#' in stack_lst[j] or '(gdb)' in stack_lst[j]:
                str = stack_lst[j]
            else:
                str = str + stack_lst[j].lstrip()

            if j < length - 1 and ('#' in stack_lst[j+1] or '(gdb)' in stack_lst[j+1]):
                print str
            if j == length - 1:
                print str

    # 删除cmd文件
    cmd = 'ssh %s "ls /tmp/cmd"' % (node)
    rc, result = commands.getstatusoutput(cmd)
    if 0 == rc:
        cmd1 = 'ssh %s "rm -rf /tmp/cmd"' % (node)
        rc, result = commands.getstatusoutput(cmd1)

if False == core_exist_flag:
    print ('******************** system has no core!!! ********************')

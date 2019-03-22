#!/usr/bin/python
# -*- encoding=utf8 -*-

"""
author:      baoruobing
date:        2018.11.14
description: 环境检查脚本
"""

import os
import sys
import json
import time
import logging
import subprocess
from optparse import OptionParser

VdbenchIP = None            # vdbench所在节点，如果是本节点则为None
VdbenchDir = None           # vdbench日志目录
DataCheck = False           # 数据校验标记

Core_Path_Lst = ['/home/parastor/log/', '/']


def run_command(cmd, node_ip=None):
    """
    在某个节点执行命令
    """
    if node_ip:
        cmd1 = 'ssh %s "%s"' % (node_ip, cmd)
    else:
        cmd1 = cmd
    process = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, unused_err = process.communicate()
    retcode = process.poll()
    return retcode, output


def json_loads(stdout):
    """
    json解析
    """
    stdout_str = json.loads(stdout, strict=False)
    return stdout_str


def get_nodes_id_ip():
    """
    获取所有集群节点的ip
    """
    cmd = "pscli --command=get_nodes"
    rc, result = run_command(cmd)
    if 0 != rc:
        raise Exception("There is not parastor or get nodes ip failed!!!")
    else:
        result = json_loads(result)
        node_id_lst = []
        node_ip_lst = []
        nodes_lst = result['result']['nodes']
        for node in nodes_lst:
            node_ip_lst.append(node['ctl_ips'][0]['ip_address'])
            node_id_lst.append(node['node_id'])
        return node_id_lst, node_ip_lst


def get_clients_ip():
    """
    获取所有客户端节点的ip
    """
    cmd = "pscli --command=get_clients"
    rc, result = run_command(cmd)
    if 0 != rc:
        raise Exception("There is not parastor or get nodes ip failed!!!")
    else:
        result = json_loads(result)
        client_ip_lst = []
        nodes_lst = result['result']
        for node in nodes_lst:
            if node['type'] == 'INTERNAL' or node['inTimeStatus'] != 'SERV_STATE_OK':
                continue
            client_ip_lst.append(node['ip'])
        return client_ip_lst

Node_Id_Lst, Node_Ip_Lst = get_nodes_id_ip()
Client_Ip_Lst = get_clients_ip()


def check_dir_exist(dir, node_ip=None):
    """
    检查某个节点上的路径是否存在
    """
    cmd = 'ls %s' % dir
    rc, stdout = run_command(cmd, node_ip)
    if rc == 0:
        return True
    else:
        return False


def check_ping(node):
    """
    检查节点是否可以ping通
    """
    cmd = 'ping -c 3 %s | grep "0 received" | wc -l' % node
    rc, stdout = run_command(cmd)
    if '0' != stdout.strip():
        return False
    else:
        return True


def make_dir(dir, node_ip=None):
    """
    创建目录
    """
    if check_dir_exist(dir, node_ip):
        cmd = "rm -rf %s" % dir
        run_command(cmd, node_ip)
    cmd = "mkdir -p %s" % dir
    rc, stdout = run_command(cmd, node_ip)
    return rc, stdout


def colour_str(string, colour='cyan'):
    """
    输出带颜色字符
    """
    colour_dic = {'black': 30,      # 黑色
                  'red': 31,        # 红色
                  'green': 32,      # 绿色
                  'yellow': 33,     # 黄色
                  'blue': 34,       # 蓝色
                  'purple': 35,     # 紫红色
                  'cyan': 36,       # 青蓝色
                  'white': 37,      # 白色
                  }
    str_colour = "\033[;%sm%s\033[0m" % (colour_dic[colour], string)
    return str_colour


def check_crash():
    """
    检查crash
    """
    logging.info("******************** check crash begin ********************")
    cmd = "ls /var/crash/ | grep - | grep :"
    node_lst = Node_Ip_Lst + Client_Ip_Lst
    for node_ip in node_lst:
        rc, stdout = run_command(cmd, node_ip)
        if rc == 0:
            logging.info("node: %s, crash:" % node_ip)
            logging.info(colour_str(stdout.strip()))
        else:
            logging.info("node %s does not have crash" % node_ip)
    logging.info("******************** check crash finish ********************\n")


def get_core_file(node_ip):
    '''
    检查节点上是否有core
    '''
    core_file_lst = []
    for core_path in Core_Path_Lst:
        cmd = "ls %s" % os.path.join(core_path, 'core*')
        rc, result = run_command(cmd, node_ip)
        if rc == 0:
            core_lst = result.split()
            core_file_lst.extend(core_lst)
    return core_file_lst


def check_core():
    """
    检查core
    """
    logging.info("******************** check core begin ********************")
    core_stack_lst = []
    node_lst = Node_Ip_Lst + Client_Ip_Lst
    for node_ip in node_lst:
        """检查节点上是否有core"""
        core_lst = get_core_file(node_ip)
        if not core_lst:
            logging.info("node %s does not have core" % node_ip)
            continue
        logging.info("node: %s core: %s" % (node_ip, colour_str(','.join(core_lst))))
        for core in core_lst:
            """get core name"""
            core_dir = {}
            core_dir['name'] = core

            """用file命令获取产生core的进程"""
            cmd1 = "echo q > /tmp/cmd_core_q"
            rc, result = run_command(cmd1, node_ip)
            if 0 != rc:
                raise Exception("%s failed!!!" % cmd1)

            cmd1 = "gdb -c %s < /tmp/cmd_core_q" % core
            rc, result = run_command(cmd1, node_ip)
            if 0 != rc:
                raise Exception("%s failed!!!" % cmd1)

            result_lst = result.splitlines()
            for line in result_lst:
                if 'Core was generated by' in line:
                    core_dir['module'] = line.split('`')[-1].split("'")[0]

            if 'module' not in core_dir:
                continue

            # 获取core的栈
            cmd1 = "echo bt > /tmp/cmd_core_bt"
            rc, result = run_command(cmd1, node_ip)
            if 0 != rc:
                raise Exception("%s failed!!!" % cmd1)

            cmd2 = "gdb %s %s < /tmp/cmd_core_bt" % (core_dir['module'], core_dir['name'])
            rc, result = run_command(cmd2, node_ip)
            if 0 != rc:
                continue
            stack_lst = result.splitlines()
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
            logging.info("\n-------------------- %s     %s     %s --------------------"
                         % (node_ip, core_dir['module'], core_dir['name']))
            for j in range(i, length):
                if '#' in stack_lst[j] or '(gdb)' in stack_lst[j]:
                    str = stack_lst[j]
                else:
                    str = str + stack_lst[j].lstrip()
                if j < length - 1 and ('#' in stack_lst[j + 1] or '(gdb)' in stack_lst[j + 1]):
                    print str
                if j == length - 1:
                    print str
        """删除cmd文件"""
        cmd = "ls /tmp/cmd_core_bt"
        rc, result = run_command(cmd, node_ip)
        if 0 == rc:
            cmd1 = "rm -rf /tmp/cmd_core_bt"
            run_command(cmd1, node_ip)
    logging.info("******************** check core finish ********************\n")


def check_bad_seg_obj():
    """
    检查坏对象和坏段
    """
    logging.info("******************** check bad seg obj begin ********************")
    node_bad_info_dic = {}
    """获取坏段"""
    cmd = "cd /home/parastor/tools/;sh badseg.sh"
    rc, stdout = run_command(cmd)
    stdout_lines = stdout.splitlines()
    node_ip = ''
    for line in stdout_lines:
        if 'NODEIP:' in line:
            node_ip = line.split()[1].split(':')[-1].strip('"')
            node_bad_info_dic[node_ip] = {}
        if 'bad objnr:' in line:
            bad_seg = line.split(',')[0].split(':')[-1].strip()
            node_bad_info_dic[node_ip]['bad_seg'] = bad_seg

    """获取坏对象"""
    cmd = "cd /home/parastor/tools/;sh badobj.sh"
    rc, stdout = run_command(cmd)
    stdout_lines = stdout.splitlines()
    for line in stdout_lines:
        if 'NODEIP:' in line:
            node_ip = line.split()[1].split(':')[-1].strip('"')
        if 'badobjnr:' in line:
            bad_obj = line.split(':')[-1].strip()
            node_bad_info_dic[node_ip]['bad_obj'] = bad_obj

    for node_ip in node_bad_info_dic:
        if 'bad_seg' in node_bad_info_dic[node_ip]:
            bad_seg = node_bad_info_dic[node_ip]['bad_seg']
        else:
            bad_seg = 'get failed'
        if 'bad_obj' in node_bad_info_dic[node_ip]:
            bad_obj = node_bad_info_dic[node_ip]['bad_obj']
        else:
            bad_obj = 'get failed'
        bad_seg = bad_seg if bad_seg == '0' else colour_str(bad_seg)
        bad_obj = bad_obj if bad_obj == '0' else colour_str(bad_obj)
        logging.info("node: %s, bad seg: %s, bad obj: %s" % (node_ip, bad_seg, bad_obj))
    logging.info("******************** check bad seg obj finish ********************\n")


def check_sys_data_status():
    """
    检查系统数据状态
    """
    logging.info("******************** check degrade begin ********************")
    cmd = "pscli --command=get_services"
    rc, stdout = run_command(cmd)
    if rc != 0:
        logging.error("%s failed\nstdout: %s" % (cmd, stdout))
        return
    stdout_json = json_loads(stdout)
    check_service_lst = ['oRole', 'oPara', 'oStor', 'oJob']
    node_service_lst = stdout_json['result']['nodes']
    service_data_lst = []
    for node_info in node_service_lst:
        services_lst = node_info['services']
        for service_info in services_lst:
            if service_info['service_type'] in check_service_lst and service_info['inTimeStatus'] == 'SERV_STATE_OK':
                service_data_lst.append(service_info['systemDataState'])
    if 'SYSTEM_FAULT' in service_data_lst:
        logging.info("System data status: %s" % colour_str('故障(FAULT)'))
    elif 'SYSTEM_DEGRADE' in service_data_lst:
        logging.info("System data status: %s" % colour_str('降级(DEGRADE)'))
    else:
        logging.info("System data status: 正常(NORMAL)")
    logging.info("******************** check degrade finish ********************\n")


def check_services():
    """
    检查服务状态
    """
    logging.info("******************** check services begin ********************")
    cmd = "pscli --command=get_services"
    rc, stdout = run_command(cmd)
    if rc != 0:
        logging.error("%s failed\nstdout: %s" % (cmd, stdout))
        return
    stdout_json = json_loads(stdout)
    node_service_lst = stdout_json['result']['nodes']
    fault_flag = False
    for node_service_info in node_service_lst:
        service_info_lst = node_service_info['services']
        for service_info in service_info_lst:
            if service_info['inTimeStatus'] != 'SERV_STATE_OK' and service_info['inTimeStatus'] != 'SERV_STATE_READY':
                fault_flag = True
                logging.info("node %s,    %s status: %s" % (node_service_info['node_id'], service_info['service_type'],
                                                            colour_str(service_info['inTimeStatus'])))
    if not fault_flag:
        logging.info("all services is OK")
    logging.info("******************** check services finish ********************\n")


def check_disk_balance():
    """
    检查磁盘是否均衡
    """
    logging.info("******************** check disk balance begin ********************")
    fault_disk_lst = []
    share_disk_lst = []
    data_disk_dic = {}
    for i in range(len(Node_Id_Lst)):
        node_id = Node_Id_Lst[i]
        node_ip = Node_Ip_Lst[i]
        cmd = "pscli --command=get_disks --node_ids=%s" % node_id
        rc, stdout = run_command(cmd)
        if rc != 0:
            logging.error("%s failed\nstdout: %s" % (cmd, stdout))
            return
        stdout_json = json_loads(stdout)
        disk_info_lst = stdout_json['result']['disks']
        for disk_info in disk_info_lst:
            if disk_info['usedState'] != 'IN_USE' \
                    or disk_info['state'] != 'DISK_STATE_HEALTHY' \
                    or (disk_info['usage'] != 'SHARED' and disk_info['usage'] != 'DATA'):
                fault_disk_dic = {}
                if disk_info['usedState'] != 'IN_USE':
                    fault_disk_dic['disk_name'] = disk_info['devname']
                    fault_disk_dic['node_ip'] = node_ip
                    fault_disk_dic['usedState'] = disk_info['usedState']
                    fault_disk_dic['state'] = disk_info['state']
                    fault_disk_lst.append(fault_disk_dic)
                elif disk_info['state'] != 'DISK_STATE_HEALTHY':
                    fault_disk_dic['disk_name'] = disk_info['devname']
                    fault_disk_dic['node_ip'] = node_ip
                    fault_disk_dic['usedState'] = disk_info['usedState']
                    fault_disk_dic['state'] = disk_info['state']
                    fault_disk_lst.append(fault_disk_dic)
                continue
            disk_info_dic = {}
            disk_usage = round(float(disk_info['used_bytes']) / disk_info['capacity'], 4) * 100
            disk_info_dic['disk_name'] = disk_info['devname']
            disk_info_dic['node_ip'] = node_ip
            disk_info_dic['disk_usage'] = disk_usage
            if disk_info['usage'] == 'SHARED':
                share_disk_lst.append(disk_info_dic)
            else:
                stor_pool_id = disk_info['storagePoolId']
                if stor_pool_id in data_disk_dic:
                    data_disk_dic[stor_pool_id].append(disk_info_dic)
                else:
                    data_disk_dic[stor_pool_id] = [disk_info_dic]
    """显示故障盘"""
    logging.info("fault disk info:")
    for fault_disk in fault_disk_lst:
        logging.info(colour_str("node: %s, disk: %s, usedState: %s, state: %s" % (fault_disk['node_ip'],
                                                                                  fault_disk['disk_name'],
                                                                                  fault_disk['usedState'],
                                                                                  fault_disk['state'])))
    logging.info("----------------------------------------------------------")
    """显示磁盘使用率"""
    share_disk_max_usage = max(share_disk_lst, key=lambda x: x['disk_usage'])['disk_usage']
    share_disk_min_usage = min(share_disk_lst, key=lambda x: x['disk_usage'])['disk_usage']
    logging.info("share disk usage info:")
    share_diff_usage = share_disk_max_usage - share_disk_min_usage
    share_diff_usage = (('%s%%' % share_diff_usage) if share_diff_usage < 5.0
                        else colour_str(('%s%%' % share_diff_usage)))
    logging.info("max usage: %s%%, min usage: %s%%, difference value: %s"
                 % (share_disk_max_usage, share_disk_min_usage, share_diff_usage))
    for share_disk_dic in share_disk_lst:
        print_str = "node: %s, disk: %s, usage: %s%%" % (share_disk_dic['node_ip'], share_disk_dic['disk_name'],
                                                         share_disk_dic['disk_usage'])
        if ((share_disk_max_usage - share_disk_min_usage >= 5.0)
            and (share_disk_dic['disk_usage'] == share_disk_max_usage
                 or share_disk_dic['disk_usage'] == share_disk_min_usage)):
            print_str = colour_str(print_str)
        logging.info(print_str)
    logging.info("----------------------------------------------------------")
    logging.info("data disk usage info:")
    for stor_pool_id in data_disk_dic:
        data_disk_lst = data_disk_dic[stor_pool_id]
        data_disk_max_usage = max(data_disk_lst, key=lambda x: x['disk_usage'])['disk_usage']
        data_disk_min_usage = min(data_disk_lst, key=lambda x: x['disk_usage'])['disk_usage']
        data_diff_usage = data_disk_max_usage - data_disk_min_usage
        data_diff_usage = (('%s%%' % data_diff_usage) if data_diff_usage < 5.0
                           else colour_str(('%s%%' % data_diff_usage)))
        logging.info("storage pool %s:" % stor_pool_id)
        logging.info("max usage: %s%%, min usage: %s%%, difference value: %s"
                     % (data_disk_max_usage, data_disk_min_usage, data_diff_usage))
        for data_disk_info_dic in data_disk_lst:
            print_str = "node: %s, disk: %s, usage: %s%%" % (data_disk_info_dic['node_ip'],
                                                             data_disk_info_dic['disk_name'],
                                                             data_disk_info_dic['disk_usage'])
            if ((data_disk_max_usage - data_disk_min_usage >= 5.0)
                and (data_disk_info_dic['disk_usage'] == data_disk_max_usage
                     or data_disk_info_dic['disk_usage'] == data_disk_min_usage)):
                print_str = colour_str(print_str)
            logging.info(print_str)
    logging.info("******************** check disk balance finish ********************\n")


def check_node_time():
    """
    检查各个节点时间
    """
    logging.info("******************** check node time begin ********************")
    node_ip_lst = Node_Ip_Lst + Client_Ip_Lst
    node_ip_str = ','.join(node_ip_lst)
    cmd = 'nprsh -on %s "date"' % node_ip_str
    rc, stdout = run_command(cmd)
    logging.info(stdout.strip())
    logging.info("******************** check node time finish ********************\n")


def check_log():
    """
    检查各个节点的日志
    """
    logging.info("******************** check log begin ********************")
    node_ip_lst = Node_Ip_Lst + Client_Ip_Lst
    cmd = "ls -ltr /home/parastor/log/backup"
    for node_ip in node_ip_lst:
        rc, stdout = run_command(cmd, node_ip)
        stdout_line_lst = stdout.splitlines()
        stdout_line_lst = stdout_line_lst[1:]
        log_info_dic = {}
        normal_flag = True
        for line in stdout_line_lst:
            line_str_lst = line.split()
            log_module = line_str_lst[-1].split('_')[0]
            if log_module == 'imp':
                log_module = '%s_%s' % (log_module, line_str_lst[-1].split('_')[1])
            log_day = "%s %s" % (line_str_lst[5], line_str_lst[6])
            if log_module not in log_info_dic:
                log_info_dic[log_module] = [{'date': log_day, 'log': [line]}]
            else:
                if log_day != log_info_dic[log_module][-1]['date']:
                    log_info_dic[log_module].append({'date': log_day, 'log': [line]})
                else:
                    log_info_dic[log_module][-1]['log'].append(line)
                    if len(log_info_dic[log_module][-1]['log']) >= 2:
                        normal_flag = False
        if normal_flag:
            logging.info("--------------------------------------------")
            logging.info("node %s log OK" % node_ip)
        else:
            logging.info("--------------------------------------------")
            logging.info("node %s log abnormal:" % node_ip)
            for log_module in log_info_dic:
                for mem in log_info_dic[log_module]:
                    log_day = mem['date']
                    num = len(mem['log'])
                    if num >= 2:
                        logging.info("%s  %s  tar.gz num %s:" % (log_module.ljust(15), log_day.ljust(8),
                                                                 colour_str(num)))
    logging.info("******************** check log finish ********************\n")


def check_vdbench():
    """
    检查vdbench断流
    """
    logging.info("******************** check vdbench begin ********************")
    if VdbenchIP:
        flatfile_path = os.path.join(VdbenchDir, "flatfile.html")
        if not check_dir_exist(flatfile_path, VdbenchIP):
            logging.error("node %s %s is not exist" % (VdbenchIP, flatfile_path))
            return
        """创建vdbench目录"""
        tmp_vdbench = "/tmp/env_check_vdbench"
        make_dir(tmp_vdbench)
        """拷贝flatfile.html"""
        cmd = "scp -r root@%s:%s %s" % (VdbenchIP, flatfile_path, tmp_vdbench)
        run_command(cmd)
    else:
        flatfile_path = os.path.join(VdbenchDir, "flatfile.html")
        if not check_dir_exist(flatfile_path):
            logging.error("%s is not exist" % flatfile_path)
            return
        tmp_vdbench = VdbenchDir
    tmp_flatfile = os.path.join(tmp_vdbench, "flatfile.html")
    begin_flag = False
    run_times = 0

    tod_index = None
    timestamp_index = None
    rate_index = None
    xfersize_index = None
    resp_index = None
    bandwidth_index = None
    read_rate_index = None
    read_resp_index = None
    read_bandwidth_index = None
    write_rate_index = None
    write_resp_index = None
    write_bandwidth_index = None

    rate_sum = 0.0000
    resp_sum = 0.0000
    bandwidth_sum = 0.0000
    read_rate_sum = 0.0000
    read_resp_sum = 0.0000
    read_bandwidth_sum = 0.0000
    write_rate_sum = 0.0000
    write_resp_sum = 0.0000
    write_bandwidth_sum = 0.0000

    vdbench_cutoff_dic = {}
    vdbench_cutoff_lst = []

    cutoff_num = 0
    with open(tmp_flatfile, 'r') as fd:
        while True:
            line = fd.readline().strip()
            if not line:
                if vdbench_cutoff_dic:
                    """断流结束"""
                    vdbench_cutoff_lst.append(vdbench_cutoff_dic)
                break
            line_lst = line.split()
            if 'tod' in line and 'timestamp' in line:
                tod_index = line_lst.index('tod')
                timestamp_index = line_lst.index('timestamp')
                xfersize_index = line_lst.index('Xfersize')
                if 'rate' in line_lst:
                    rate_index = line_lst.index('rate')
                else:
                    rate_index = line_lst.index('Rate')
                if 'resp' in line_lst:
                    resp_index = line_lst.index('resp')
                else:
                    resp_index = line_lst.index('Resp')
                bandwidth_index = line_lst.index('MB/sec')
                read_rate_index = line_lst.index('Read_rate')
                read_resp_index = line_lst.index('Read_resp')
                read_bandwidth_index = line_lst.index('MB_read')
                write_rate_index = line_lst.index('Write_rate')
                write_resp_index = line_lst.index('Write_resp')
                write_bandwidth_index = line_lst.index('MB_write')
                continue
            if tod_index is not None:
                try:
                    rate_int = int(float(line_lst[rate_index]))
                except:
                    continue
                xfersize_int = int(line_lst[xfersize_index])
                if begin_flag is False and rate_int != 0:
                    begin_flag = True
                if not begin_flag:
                    continue
                """记录断流"""
                if rate_int == 0 and xfersize_int == 0:
                    cutoff_num = 0
                    if not vdbench_cutoff_dic:
                        """断流开始"""
                        vdbench_cutoff_dic['begin_time'] = line_lst[timestamp_index]
                        vdbench_cutoff_dic['time'] = 1
                    else:
                        """断流持续"""
                        vdbench_cutoff_dic['end_time'] = line_lst[timestamp_index]
                        vdbench_cutoff_dic['time'] += 1
                else:
                    if vdbench_cutoff_dic:
                        if cutoff_num >= 10:
                            """断流结束"""
                            vdbench_cutoff_lst.append(vdbench_cutoff_dic)
                            vdbench_cutoff_dic = {}
                            cutoff_num = 0
                        else:
                            cutoff_num += 1
                """有数据读写时，记录数据"""
                run_times += 1
                rate_sum += float(rate_int)
                resp_sum += float(line_lst[resp_index])
                bandwidth_sum += float(line_lst[bandwidth_index])
                read_rate_sum += float(line_lst[read_rate_index])
                read_resp_sum += float(line_lst[read_resp_index])
                read_bandwidth_sum += float(line_lst[read_bandwidth_index])
                write_rate_sum += float(line_lst[write_rate_index])
                write_resp_sum += float(line_lst[write_resp_index])
                write_bandwidth_sum += float(line_lst[write_bandwidth_index])

    logging.info("vdbench cutoff info:")
    less_1_num = 0
    more_1_num = 0
    more_5_num = 0
    more_10_num = 0
    print_cutoff_lst = []
    for vdbench_cutoff_info in vdbench_cutoff_lst:
        if vdbench_cutoff_info['time'] < 60:
            less_1_num += 1
        else:
            more_1_num += 1
            print_cutoff_lst.append(vdbench_cutoff_info)
            if vdbench_cutoff_info['time'] >= 300:
                more_5_num += 1
            if vdbench_cutoff_info['time'] >= 600:
                more_10_num += 1
    less_1_num = less_1_num if less_1_num == 0 else colour_str(less_1_num)
    more_1_num = more_1_num if more_1_num == 0 else colour_str(more_1_num)
    more_5_num = more_5_num if more_5_num == 0 else colour_str(more_5_num)
    more_10_num = more_10_num if more_10_num == 0 else colour_str(more_10_num)
    logging.info("less 1 minute: %s        more 1 minute: %s       more 5 minute: %s        more 10 minute: %s"
                 % (less_1_num, more_1_num, more_5_num, more_10_num))
    logging.info("more 1 minute cutoff info:")
    for vdbench_cutoff_info in print_cutoff_lst:
        m, s = divmod(vdbench_cutoff_info['time'], 60)
        h, m = divmod(m, 60)
        str_cutoff = colour_str("begin: %s,    end: %s,    length of time: %dh:%dm:%ds" %
                                (vdbench_cutoff_info['begin_time'], vdbench_cutoff_info['end_time'], h, m, s))
        logging.info(str_cutoff)
    logging.info("----------------------------------------------------------")
    logging.info("vdbench property data:")
    rate_ave = 0 if run_times == 0 else rate_sum / run_times
    resp_ave = 0 if run_times == 0 else resp_sum / run_times
    bandwidth_ave = 0 if run_times == 0 else bandwidth_sum / run_times
    read_rate_ave = 0 if run_times == 0 else read_rate_sum / run_times
    read_resp_ave = 0 if run_times == 0 else read_resp_sum / run_times
    read_bandwidth_ave = 0 if run_times == 0 else read_bandwidth_sum / run_times
    write_rate_ave = 0 if run_times == 0 else write_rate_sum / run_times
    write_resp_ave = 0 if run_times == 0 else write_resp_sum / run_times
    write_bandwidth_ave = 0 if run_times == 0 else write_bandwidth_sum / run_times
    logging.info("<total average>     IOPS: %s,        delay: %s/ms,        bandwidth: %sMB/sec"
                 % (rate_ave, resp_ave, bandwidth_ave))
    logging.info("<read average>      IOPS: %s,        delay: %s/ms,        bandwidth: %sMB/sec"
                 % (read_rate_ave, read_resp_ave, read_bandwidth_ave))
    logging.info("<write average>     IOPS: %s,        delay: %s/ms,        bandwidth: %sMB/sec"
                 % (write_rate_ave, write_resp_ave, write_bandwidth_ave))
    logging.info("******************** check vdbench finish ********************\n")


def check_data_meta():
    logging.info("******************** check data meta begin ********************")
    cmd = "pscli --command=get_volumes"
    rc, stdout = run_command(cmd)
    if rc != 0:
        logging.error("%s failed\n%s" % (cmd, stdout))
        return
    stdout_json = json_loads(stdout)
    volume_lst = stdout_json['result']['volumes']
    volume_id_lst = []
    for volume in volume_lst:
        if volume['volume_type'] == 'USER_VOLUME':
            volume_id_lst.append(volume['id'])

    logging.info("you will wait a long long long ... long time")

    start_time = time.time()
    for volume_id in volume_id_lst:
        cmd = '/home/parastor/tools/nWatch -t oJob -i 1 -c OSCAN#conchk -a "fsid=%s path=/"' % volume_id
        run_command(cmd)
    pre_num = 0
    while True:
        time.sleep(20)
        cmd = 'sh /home/parastor/tools/concheck_result.sh f'
        rc, stdout = run_command(cmd)
        if 'Task continuing' not in stdout:
            logging.info(stdout)
            end_time = time.time()
            m, s = divmod(end_time - start_time, 60)
            h, m = divmod(m, 60)
            logging.info("\nyou have wait for it %dh:%dm:%ds" % (h, m, s))
            break
        else:
            exist_time = int(time.time() - start_time)
            if 60 <= exist_time <= 80:
                logging.info("1 minute passed ...")
            else:
                num = exist_time / 600
                if num == pre_num:
                    continue
                else:
                    logging.info("%s minutes passed ..." % (10*num))
                    pre_num = num
    logging.info("******************** check data meta finish ********************\n")


def log_init():
    """
    日志初始化
    """
    file_path = os.path.split(os.path.realpath(__file__))[0]
    file_name = os.path.basename(__file__)
    file_name = file_name[:-3]
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    file_name = now_time + '_' + file_name + '.log'
    file_name = os.path.join(file_path, file_name)
    print file_name
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(levelname)s][%(asctime)s]%(lineno)d:  %(message)s',
                        datefmt='%y-%m-%d %H:%M:%S',
                        filename=file_name,
                        filemode='a')

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(console)
    return


def arg_analysis():
    global VdbenchIP
    global VdbenchDir
    global DataCheck
    usage = "usage: %prog [options] arg1 arg2 arg3"
    version = "%prog 5.0"
    parser = OptionParser(usage=usage, version=version)
    parser.add_option("-v", "--vdbench",
                      type="str",
                      dest="vdbench",
                      help="Required:False   Type:int  Help:vdbench output dir. e.g."
                           "local node: /home/vdbench/output                        "
                           "other node: 10.2.40.1:/home/vdbench/output              ")

    parser.add_option("-d", "--datacheck",
                      action="store_true",
                      dest="datacheck",
                      help="Required:False   Type:bool  Help:If you want to check data and meta, "
                           "you need to configure this parameter. "
                           "WARN: need a long time")

    options, args = parser.parse_args()

    """检查-v参数"""
    if options.vdbench is not None:
        """检查是否是本地"""
        if ':' not in options.vdbench:
            vdb_dir = options.vdbench
            if vdb_dir == '':
                parser.error('-v is not right, e.g. "10.2.40.1:/home/vdench/output"')
            elif not check_dir_exist(vdb_dir):
                parser.error('-v is not right, e.g. "10.2.40.1:/home/vdench/output"')
            VdbenchIP = None
            VdbenchDir = vdb_dir
        else:
            vdb_ip = options.vdbench.strip().split(':')[0]
            vdb_dir = options.vdbench.strip().split(':')[-1]
            if check_ping(vdb_ip) is False:
                parser.error("-v is not right, %s can't ping" % vdb_ip)
            """检查放vdbench日志的目录是否存在"""
            if vdb_dir == '':
                parser.error('-v is not right, e.g. "10.2.40.1:/home/vdench/output"')
            elif check_dir_exist(vdb_dir, vdb_ip) is False:
                parser.error('-v is not right, %s %s is not exist' % (vdb_ip, vdb_dir))
            VdbenchIP = vdb_ip
            VdbenchDir = vdb_dir

    """检查-d参数"""
    if options.datacheck is True:
        DataCheck = True


def run_env_check():
    """
    检查环境
    """
    logging.info(" ".join(sys.argv))
    """检查crash"""
    check_crash()
    """检查core"""
    check_core()
    """检查坏段和坏对象"""
    check_bad_seg_obj()
    """检查系统数据状态"""
    check_sys_data_status()
    """检查服务状态"""
    check_services()
    """检查磁盘均衡"""
    check_disk_balance()
    """检查各节点的时间"""
    check_node_time()
    """检查各节点的日志"""
    check_log()
    """检查vdbench断流时间"""
    if VdbenchDir:
        check_vdbench()
    """检查数据和元数据的一致性"""
    if DataCheck:
        check_data_meta()


def main():
    """
    主函数
    """
    """参数解析"""
    arg_analysis()
    """初始化日志文件"""
    log_init()
    """执行环境检查"""
    run_env_check()


if __name__ == '__main__':
    main()
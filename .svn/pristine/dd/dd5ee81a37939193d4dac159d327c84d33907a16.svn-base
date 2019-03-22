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
import traceback
from optparse import OptionParser

import result
import utils_path
import get_config
import common
import get_config

VdbenchIP = None            # vdbench所在节点，如果是本节点则为None
VdbenchDir = None           # vdbench日志目录
DataCheck = False           # 数据校验标记
cutoff_log = None
#Core_Path_Lst = ['/home/parastor/log/', '/']
def log_init(case_log_path):
    """
    日志解析
    """
    global cutoff_log
    file_name = os.path.basename(__file__)
    file_name = file_name.split('.')[0]
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    file_name = now_time + '_' + file_name + '.log'
    file_name = os.path.join(case_log_path, file_name)
    print file_name

    cutoff_log = logging.getLogger(name='cutoff_log')
    cutoff_log.setLevel(level=logging.INFO)

    handler = logging.FileHandler(file_name, mode='a')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)

    cutoff_log.addHandler(console)
    cutoff_log.addHandler(handler)

    return

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


def check_vdbench(Vdbench_Info_Lst, cut_off_time_standard):
    """
    检查vdbench断流
    """
    cutoff_log.info("******************** check vdbench begin ********************")
    allcutoffinfos = []
    allcutoffinfo = dict()
    for vdbench_info in Vdbench_Info_Lst:
        vdbench_ip = vdbench_info['vdbench_ip']
        vdbench_dir = vdbench_info['vdbench_dir']
        if vdbench_ip:
            print_str = "%s:%s" % (vdbench_ip, vdbench_dir)
        else:
            print_str = vdbench_dir
        print "\n########## %s ##########" %print_str
        #logging.info("\n########## %s ##########" % print_str)
        if vdbench_ip:
            flatfile_path = os.path.join(vdbench_dir, "flatfile.html")
            if not check_dir_exist(flatfile_path, vdbench_ip):
                cutoff_log.error("node %s %s is not exist" % (vdbench_ip, flatfile_path))
                return
            """创建vdbench目录"""
            tmp_vdbench = "/tmp/env_check_vdbench"
            make_dir(tmp_vdbench)
            """拷贝flatfile.html"""
            cmd = "scp -r root@%s:%s %s" % (vdbench_ip, flatfile_path, tmp_vdbench)
            run_command(cmd)
        else:
            flatfile_path = os.path.join(vdbench_dir, "flatfile.html")
            if not check_dir_exist(flatfile_path):
                cutoff_log.error("%s is not exist" % flatfile_path)
                return
            tmp_vdbench = vdbench_dir
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
        rmdir_rate_index = None
        delete_rate_index = None

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
                    rmdir_rate_index = line_lst.index('Rmdir_rate')
                    delete_rate_index = line_lst.index('Delete_rate')
                    continue
                if tod_index is not None:
                    try:
                        rate_int = int(float(line_lst[rate_index]))
                        xfersize_int = int(line_lst[xfersize_index])
                        rmdir_rate_int = int(float(line_lst[rmdir_rate_index]))
                        delete_rate_int = int(float(line_lst[delete_rate_index]))
                    except:
                        continue

                    if begin_flag is False and rate_int != 0:
                        begin_flag = True
                    if not begin_flag:
                        continue
                    """记录断流"""
                    if rate_int == 0 and xfersize_int == 0 and rmdir_rate_int == 0 and delete_rate_int == 0:
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

        cutoff_log.info("vdbench cutoff info:")
        if None == cut_off_time_standard:
            less_1_num = 0
            more_1_num = 0
            more_5_num = 0
            more_10_num = 0
            print_cutoff_lst = []
            for vdbench_cutoff_info in vdbench_cutoff_lst:
                if vdbench_cutoff_info['time'] < 120:
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

            cutoff_log.info(
                "less than 1 min: %s        more than 1 min: %s       more than 5 min: %s        more than 10 min: %s"
                % (less_1_num, more_1_num, more_5_num, more_10_num))
            cutoff_log.info("more than 1 min cutoff info:")

        else:
            # less_standard_time = 0
            more_standard_time = 0
            print_cutoff_lst = []
            for vdbench_cutoff_info in vdbench_cutoff_lst:
                if vdbench_cutoff_info['time'] < cut_off_time_standard:
                    #less_standard_time += 1
                    pass
                else:
                    more_standard_time += 1
                    print_cutoff_lst.append(vdbench_cutoff_info)
            # less_standard_time = less_standard_time if less_standard_time == 0 else colour_str(less_standard_time)
            more_standard_time = more_standard_time if more_standard_time == 0 else colour_str(more_standard_time)

            cutoff_log.info(
                "more than standard:%d s: %s       "
                % (cut_off_time_standard, more_standard_time))

        for vdbench_cutoff_info in print_cutoff_lst:
            m, s = divmod(vdbench_cutoff_info['time'], 60)
            h, m = divmod(m, 60)
            str_cutoff = colour_str("begin: %s,    end: %s,    length of time: %dh:%dm:%ds" %
                                    (vdbench_cutoff_info['begin_time'], vdbench_cutoff_info['end_time'], h, m, s))
            cutoff_log.info(str_cutoff)
        cutoff_log.info("----------------------------------------------------------")
        cutoff_log.info("vdbench property data:")
        rate_ave = 0 if run_times == 0 else rate_sum / run_times
        resp_ave = 0 if run_times == 0 else resp_sum / run_times
        bandwidth_ave = 0 if run_times == 0 else bandwidth_sum / run_times
        read_rate_ave = 0 if run_times == 0 else read_rate_sum / run_times
        read_resp_ave = 0 if run_times == 0 else read_resp_sum / run_times
        read_bandwidth_ave = 0 if run_times == 0 else read_bandwidth_sum / run_times
        write_rate_ave = 0 if run_times == 0 else write_rate_sum / run_times
        write_resp_ave = 0 if run_times == 0 else write_resp_sum / run_times
        write_bandwidth_ave = 0 if run_times == 0 else write_bandwidth_sum / run_times
        cutoff_log.info("<total average>     IOPS: %s,        delay: %s/ms,        bandwidth: %sMB/sec"
                     % (rate_ave, resp_ave, bandwidth_ave))
        cutoff_log.info("<read average>      IOPS: %s,        delay: %s/ms,        bandwidth: %sMB/sec"
                     % (read_rate_ave, read_resp_ave, read_bandwidth_ave))
        cutoff_log.info("<write average>     IOPS: %s,        delay: %s/ms,        bandwidth: %sMB/sec"
                     % (write_rate_ave, write_resp_ave, write_bandwidth_ave))
        print 'vdbench_info is %s' %vdbench_info
        vdbench_info = vdbench_ip + ':' +vdbench_dir
        print 'after vdbench_info is %s' % vdbench_info
        if print_cutoff_lst == '':
            print_cutoff_lst = "None"
        print 'print_cutoff_lst is %s' % print_cutoff_lst
        allcutoffinfo[vdbench_info] = print_cutoff_lst
        print 'allcutoffinfo is %s' %allcutoffinfo
        print '/n'
    cutoff_log.info("******************** check vdbench finish ********************\n")
    #return print_cutoff_lst
    return allcutoffinfo

def main(FILE_NAME, cut_off_time_standard):
    '''
    :param FILE_NAME:case名称
    :param case_log_path: case的路径
    :return: 返回的是断流信息，例如：{'10.2.40.34:/home/StorTest/test_cases/log/vdbench_log/main_case0124_vdbenchnasoutput': [], '10.2.40.34:/home/StorTe
st/test_cases/log/vdbench_log/main_case0124_vdbenchposixoutput': [{'time': 76, 'end_time': '01/24/2019-19:21:01-CST', 'begin_time': '01/24/2019-19:19:46-CST'}]}
也就是返回一个字典，字典中有两个键值对，分别是nas和posix的out路径以及断流信息
    '''
    # 获取vdbench的flag
    nas_vdbench_param = get_config.get_nas_vdbench_param()
    nas_vdbflagname = nas_vdbench_param['vdbflagname']
    posix_vdbench_param = get_config.get_posix_vdbench_param()
    posix_vdbflagname = posix_vdbench_param['vdbflagname']
    # 获取vdbnech输出目录的路径
    current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    outputpath = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname
            (os.path.dirname(
            os.path.realpath(
                __file__))))))))
    outputpath = os.path.join(outputpath, 'log', 'vdbench_log')
    outputname1 = FILE_NAME + '_' + nas_vdbflagname + 'output'
    outputname2 = FILE_NAME + '_' + posix_vdbflagname + 'output'
    outputpathnas = os.path.join(outputpath, outputname1)
    outputpathposix = os.path.join(outputpath, outputname2)
    cutoff_log.info("outputpathnas is %s" % outputpathnas)
    cutoff_log.info("outputpathposix is %s" % outputpathposix)

    # 获取执行主函数的节点的ip
    cosbench_param_dict = get_config.get_cosbench_param()
    cosbench_client_ip_lst = cosbench_param_dict['cosbench_client_ip_lst']
    localip = cosbench_client_ip_lst[0]

    # 组合断流所需的参数list
    Vdbench_Info_Lst = []
    Vdbench_Infonas = dict()
    Vdbench_Infonas['vdbench_ip'] = localip
    Vdbench_Infonas['vdbench_dir'] = outputpathnas
    Vdbench_Infoposix = dict()
    Vdbench_Infoposix['vdbench_ip'] = localip
    Vdbench_Infoposix['vdbench_dir'] = outputpathposix
    Vdbench_Info_Lst.append(Vdbench_Infonas)
    Vdbench_Info_Lst.append(Vdbench_Infoposix)
    print Vdbench_Info_Lst
    allcutoffinfos = check_vdbench(Vdbench_Info_Lst, cut_off_time_standard)
    return allcutoffinfos


def aftercase_ifcutoff(case_name, case_log_path, cut_off_time_standard=None):
    # case_result 用来判断整个case 是否成功执行了
    #case_result = True
    # 如果上面的判断成功了，依旧是谁整个用例执行成功了，那么检查是否断流

    log_init(case_log_path)
    cutoff_log.info("*******初始化日志********")

    cutoffdir = []
    cutoffinfo= main(case_name, cut_off_time_standard)
    # cutoffinfo = check_if_cutoff.main('main_case0124', '/opt/a')
    # 在返回的字典中判断是否断流
    for key in cutoffinfo:
        print 'key is %s' % key
        value = cutoffinfo[key]
        print 'info is %s' % value
        if cutoffinfo[key] == []:
            pass
        else:
            cutoff_log.error('##########cutoff happend#################')
            cutoff_log.error('cuntoffpath is %s' % key )
            cutoff_log.error('cuntoffinfo is %s' % value)
            dir = key.split(':')[1]
            cutoffdir.append(dir)
    cutoff_log.error('cutoffdir of %s is %s' % (case_name, cutoffdir))

    #判断断流的结果是否为空，如果为空则往/tmp/result下打一个用例号以及0，如果不为空则/tmp/result下打一个用例号以及1且在
    if cutoffdir == []:
        cutoff_log.info('%s finish!' % case_name)
        cutoff_log.info('%s success!' % case_name)
        result.result(case_name, 0)
    else:
        cutoff_log.info('%s finish!' % case_name)
        cutoff_log.info('%s failed!' % case_name)
        result.result(case_name, -1)
        now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        failfile = os.path.join('/tmp/script_err',now_time)
        cmd = "touch %s" %failfile
        common.command(cmd)
    return cutoffdir


if __name__=="__main__":

    #Vdbench_Info_Lst = [{'vdbench_ip': '10.2.40.34', 'vdbench_dir': '/home/StorTest/test_cases/log/vdbench_log/main_case0124_vdbenchnasoutput'}, {'vdbench_ip': '10.2.40.34', 'vdbench_dir': '/home/StorTest/test_cases/log/vdbench_log/main_case0124_vdbenchposixoutput'}]
    #print Vdbench_Info_Lst
    case_log_path = '/home/StorTest/test_cases/log/case_log'
    # main('main_case0124', case_log_path)
    aftercase_ifcutoff('30-0-0-1', case_log_path)

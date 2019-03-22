#!/usr/bin/python
# -*- encoding=utf8 -*-
"""
 author 鲍若冰
 date 2018-07-28
 @summary：
    收集Prastor的日志。
 @changelog：
"""

import os
import re
import time
import json
import logging
import traceback
import subprocess
from optparse import OptionParser

ParastorBinPath = "/home/parastor/bin/"         # 集群bin文件路径
ParastorLogPath = "/home/parastor/log/"         # 集群log文件路径
BackupLogPath = "/home/parastor/log/backup"     # 集群backup路径
ClientBinPath = "/cliparastor/bin/"             # 客户端bin文件路径
ClientLogPath = "/var/log/"                     # 客户端log文件路径
LogModule = {'oPara': 'oPara.*', 'oStor': 'oStor.*', 'oRole': 'oRole.*',
             'oJob': 'oJob.*', 'oJmgs': 'oJmgs.*', 'oMgcd': 'mgcd.*','oSan':'oSan.*'}
ImpLogModule = {'oPara': 'imp_oPara.*', 'oStor': 'imp_oStor.*',
                'oRole': 'imp_oRole.*', 'oJob': 'imp_oJob.*','oSan':'oSan.*'}
BackupLogModule = {'oPara': '*oPara*', 'oStor': '*oStor*', 'oRole': '*oRole*',
                   'oJob': '*oJob*', 'oJmgs': '*oJmgs*', 'oMgcd': '*mgcd*'}
ClientLogModule = {'oMgcd_client': 'mgcd.*', 'parastor': 'parastor.log_*','oSan':'oSan.*'}
Client_IOstat = '/proc/parastor/cli_iostat'     # 客户端IO性能统计

global Operation            # BUG类型
global FaultNodeIp          # 出现故障的节点ip
global Core_Name_lst        # core的名字；列表
global LogHoldIP            # log保存到的节点ip
global LogHoldDir           # log保存到的路径
global VdbenchIP            # vdbench日志存放的ip
global VdbenchDir           # vdbench日志存放的目录

"""****************************** common ******************************"""


def run_command(cmd, node_ip=None):
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   在某个节点执行命令
    :param cmd:     要执行的命令
    :param node_ip: 节点ip，不输入则默认本节点
    :return: 
    """
    if node_ip:
        cmd1 = 'ssh %s "%s"' % (node_ip, cmd)
    else:
        cmd1 = cmd
    process = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, unused_err = process.communicate()
    retcode = process.poll()
    return retcode, output


def scp_log(log_lst, src_node_ip, dest_node_ip, dest_dir):
    for log in log_lst:
        if check_dir_exist(log, src_node_ip) is False:
            continue
        cmd = 'scp -r root@%s:%s root@%s:%s' % \
              (src_node_ip, log, dest_node_ip, dest_dir)
        info_str = "scp %s:%s  to  %s:%s" % (src_node_ip, log, dest_node_ip, dest_dir)
        logging.info(info_str)
        rc, stdout = run_command(cmd)
        if rc != 0:
            logging.error(stdout)
            logging.error('scp log failed!!!')


def tar_log(pwd_dir, tar_name, src_dir, node_ip):
    """
    :author:         baoruobing
    :date  :         2018.07.28
    :description:    压缩目录
    :param pwd_dir:  操作目录
    :param src_dir:  要压缩的源目录
    :param tar_name: 压缩包的名字
    :param node_ip:  执行命令的节点
    :return: 
    """
    cmd = 'cd %s;tar zcvf %s %s --remove-files ' % (pwd_dir, tar_name, src_dir)
    info_str = "node %s  tar %s  to  %s" % (node_ip, src_dir, tar_name)
    logging.info(info_str)
    rc, stdout = run_command(cmd, node_ip)
    if rc != 0:
        logging.error(stdout)
        logging.error("tar failed!!!")
    return rc, stdout


def run_tar_log():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 公共压缩目录操作
    :return: 
    """
    return
    """
    pwd_dir = os.path.dirname(LogHoldDir)
    src_dir = os.path.basename(LogHoldDir)
    tar_name = "%s.tar.gz" % src_dir
    tar_log(pwd_dir, tar_name, src_dir, LogHoldIP)
    return
    """


def check_ip(ip):
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 检查ip格式
    :param ip:    要检查的ip
    :return: 
    """
    pattern = re.compile(r'((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    match = pattern.match(ip)
    if match:
        return True
    else:
        return False


def check_ping(node):
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 检查节点是否可以ping通
    :param node:  节点ip或者节点别名
    :return: 
    """
    cmd = 'ping -c 3 %s | grep "0 received" | wc -l' % node
    rc, stdout = run_command(cmd)
    if '0' != stdout.strip():
        return False
    else:
        return True


def get_one_node_all_ip(node_ip=None):
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   获取一个节点的所有网卡的ip
    :param node_ip: 节点的ip或者别名,不输入则是本节点执行
    :return: 
    """
    cmd = 'ifconfig | grep "inet "'
    rc, stdout = run_command(cmd, node_ip)
    if rc != 0:
        raise Exception("get node %s all ip failed!!!" % node_ip)
    node_ip_lst = []
    line_lst = stdout.splitlines()
    for line in line_lst:
        ip = line.strip().split()[1]
        node_ip_lst.append(ip)
    return node_ip_lst


def check_dir_exist(dir, node_ip=None):
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   检查某个节点上的路径是否存在
    :param dir:     路径
    :param node_ip: 节点ip
    :return:        True:存在，False:不存在
    """
    cmd = 'ls %s' % dir
    rc, stdout = run_command(cmd, node_ip)
    if rc == 0:
        return True
    else:
        return False


def make_dir(dir, node_ip=None):
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   在某个节点上创建目录
    :param dir:     要创建的目录
    :param node_ip: 节点ip
    :return: 
    """
    if check_dir_exist(dir, node_ip):
        return
    cmd = 'mkdir %s' % dir
    run_command(cmd, node_ip)
    return


def get_current_time():
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   获取当前时间
    :return: 
    """
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    return now_time


def json_loads(stdout):
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   json解析
    :param stdout:  要解析的json字符串
    :return: 
    """
    try:
        stdout_str = json.loads(stdout, strict=False)
        return stdout_str
    except Exception, e:
        logging.error(stdout)
        raise Exception("Error msg is %s" % e)


def get_nodes_ctrl_ip():
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   获取所有集群节点的管理ip
    :return: 
    """
    cmd = 'pscli --command=get_nodes'
    rc, stdout = run_command(cmd)
    if rc != 0:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    node_ip_lst = []
    stdout = json_loads(stdout)
    node_info_lst = stdout['result']['nodes']
    for node_info in node_info_lst:
        ip = node_info['ctl_ips'][0]['ip_address']
        node_ip_lst.append(ip)
    return node_ip_lst


def get_ext_client_ip():
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   获取所有独立客户端的ip
    :return: 
    """
    cmd = "pscli --command=get_clients"
    rc, result = run_command(cmd)
    if 0 != rc:
        raise Exception("There is not parastor or get nodes ip failed!!!")
    else:
        client_ip_lst = []
        result = json_loads(result)
        nodes_lst = result['result']
        for node in nodes_lst:
            if node['type'] == 'EXTERNAL':
                client_ip_lst.append(node['ip'])
        return client_ip_lst


def get_all_log_for_module(*args):
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   获取某个模块所有的日志(包括imp和backup)
    :param args: 
    :return: 
    """
    parastor_log_lst = []
    for module in args:
        """获取log"""
        if module in LogModule:
            parastor_log_lst.append(os.path.join(ParastorLogPath, LogModule[module]))
        """获取implog"""
        if module in ImpLogModule:
            parastor_log_lst.append(os.path.join(ParastorLogPath, ImpLogModule[module]))
        """获取backup中的log"""
        if module in BackupLogModule:
            parastor_log_lst.append(os.path.join(BackupLogPath, BackupLogModule[module]))
    return parastor_log_lst

"""****************************** init log ******************************"""


def log_init():
    file_path = os.path.split(os.path.realpath(__file__))[0]
    file_name = os.path.basename(__file__)
    file_name = file_name[:-3]
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    file_name = now_time + '_' + file_name + '.log'
    file_name = os.path.join(file_path, file_name)
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(levelname)s][%(asctime)s]%(lineno)d:  %(message)s',
                        datefmt='%y-%m-%d %H:%M:%S',
                        filename=file_name,
                        filemode='a')

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    return

"""****************************** crash log ******************************"""


def collect_log_crash():
    pass

"""****************************** core log ******************************"""


def get_core_modular(corename, node_ip):
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 获取core的模块
    :return: 
    """
    cmd = "file %s" % corename
    rc, stdout = run_command(cmd, node_ip)
    if rc != 0:
        raise Exception('cmd:%s failed' % cmd)
    result_lst = stdout.split(",")
    for result_mem in result_lst:
        if 'from' in result_mem:
            return result_mem.split("'")[1].split()[0]
    else:
        raise Exception("get core modular failed!!!")


def collect_cluster_core_log():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 收集集群节点的core的log
    :return: 
    """
    col_log_lst = Core_Name_lst[:]

    """获取core的模块"""
    modular_name_lst = []
    for core_name in Core_Name_lst:
        modular = get_core_modular(core_name, FaultNodeIp)
        modular_name = os.path.basename(modular)
        modular_name_lst.append(modular_name)
    modular_name_lst = list(set(modular_name_lst))

    """获取每个模块的bin文件、log文件、implog文件、backup的log"""
    for modular_name in modular_name_lst:
        modular_log_lst = get_all_log_for_module(modular_name)
        col_log_lst += modular_log_lst
        bin_file = os.path.join(ParastorBinPath, modular_name)
        col_log_lst.append(bin_file)

    """创建以故障节点为名字的存放log的目录"""
    log_put_dir = os.path.join(LogHoldDir, FaultNodeIp)
    make_dir(log_put_dir, LogHoldIP)
    """拷贝日志"""
    info_str = 'node %s: %s will scp' % (FaultNodeIp, col_log_lst)
    logging.info(info_str)
    scp_log(col_log_lst, FaultNodeIp, LogHoldIP, log_put_dir)

    """压缩日志"""
    run_tar_log()
    return


def collect_client_core_log():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 收集独立客户端节点的core的log
    :return: 
    """
    col_log_lst = Core_Name_lst[:]
    """获取core的模块"""
    modular_name_lst = []
    for core_name in Core_Name_lst:
        modular = get_core_modular(core_name, FaultNodeIp)
        modular_name = os.path.basename(modular)
        modular_name_lst.append(modular_name)
    modular_name_lst = list(set(modular_name_lst))

    """获取每个模块的bin文件、log文件"""
    for modular_name in modular_name_lst:
        if modular_name in ClientLogModule:
            log_file = os.path.join(ClientLogPath, ClientLogModule[modular_name])
            col_log_lst.append(log_file)
        bin_file = os.path.join(ClientBinPath, modular_name)
        col_log_lst.append(bin_file)

    """创建以故障节点为名字的存放log的目录"""
    log_put_dir = os.path.join(LogHoldDir, FaultNodeIp)
    make_dir(log_put_dir, LogHoldIP)
    """拷贝日志"""
    info_str = 'node %s: %s will scp' % (FaultNodeIp, col_log_lst)
    logging.info(info_str)
    scp_log(col_log_lst, FaultNodeIp, LogHoldIP, log_put_dir)

    """压缩日志"""
    run_tar_log()
    return


def collect_log_core():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 出现core,开始收集log
    :return: 
    """
    logging.info("******************** collect core log begin ********************")
    """获取故障点的所有网卡ip"""
    fault_node_all_ip_lst = get_one_node_all_ip(FaultNodeIp)
    """获取集群和客户端的ip"""
    node_ip_lst = get_nodes_ctrl_ip()
    client_ip_lst = get_ext_client_ip()

    parastor_flag = False
    client_flag = False
    for fault_node_ip in fault_node_all_ip_lst:
        if fault_node_ip in node_ip_lst:
            parastor_flag = True
        if fault_node_ip in client_ip_lst:
            client_flag = True

    if parastor_flag is True:
        collect_cluster_core_log()
        logging.info("******************** collect core log succeed ********************")
    elif client_flag is True:
        collect_client_core_log()
        logging.info("******************** collect core log succeed ********************")
    else:
        logging.error('node %s is not parastor or client node' % FaultNodeIp)
        logging.info("******************** collect core log failed!!! ********************")
    return

"""****************************** client cutoff log ******************************"""


def get_lat_log():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 获取各模块的性能统计信息
    :return: 
    """
    cmd = 'sh /home/parastor/tools/print_lat.sh'
    rc, stdout = run_command(cmd)
    if rc != 0:
        logging.error("print_lat.sh failed!!!")
    cmd = 'ls /root/lat.*'
    rc, stdout = run_command(cmd)
    if rc != 0:
        logging.error("%s failed!!!" % cmd)
    lat_log_lst = stdout.strip().split()
    return lat_log_lst


def collect_log_cutoff():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 出现断流,开始收集log
    :return: 
    """
    logging.info("******************** collect cutoff log begin ********************")
    col_log_dir = {}
    """获取客户端的性能统计"""
    client_log_lst = []
    client_log_lst.append(Client_IOstat)
    """获取客户端的日志"""
    client_log_lst.append(os.path.join(ClientLogPath, ClientLogModule['parastor']))
    col_log_dir[FaultNodeIp] = client_log_lst

    """获取本节点的所有ip"""
    local_node_ip_lst = get_one_node_all_ip()
    """获取集群节点的log"""
    node_ip_lst = get_nodes_ctrl_ip()
    for node_ip in node_ip_lst:
        parastor_log_lst = []
        """本节点获取性能统计"""
        if node_ip in local_node_ip_lst:
            lat_log_lst = get_lat_log()
            parastor_log_lst = lat_log_lst[:]
        """获取log"""
        module_log_lst = get_all_log_for_module('oPara', 'oStor')
        parastor_log_lst += module_log_lst
        col_log_dir[node_ip] = parastor_log_lst

    """拷贝log文件"""
    for key in col_log_dir:
        """创建日志存放路径"""
        log_put_dir = os.path.join(LogHoldDir, key)
        make_dir(log_put_dir, LogHoldIP)
        """拷贝日志"""
        logging.info("******************************")
        info_str = 'node %s: %s will scp' % (key, col_log_dir[key])
        logging.info(info_str)
        scp_log(col_log_dir[key], key, LogHoldIP, log_put_dir)

    """拷贝vdbench日志"""
    vdbench_put_dir = os.path.join(LogHoldDir, 'vdbench_output')
    make_dir(vdbench_put_dir, LogHoldIP)
    logging.info("******************************")
    info_str = 'node %s: %s will scp' % (VdbenchDir, VdbenchIP)
    logging.info(info_str)
    scp_log([VdbenchDir], VdbenchIP, LogHoldIP, vdbench_put_dir)

    """压缩日志"""
    run_tar_log()
    logging.info("******************** collect cutoff log succeed ********************")
    return

"""****************************** client EIO log ******************************"""


def collect_log_eio():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 出现EIO,开始收集log
    :return: 
    """
    logging.info("******************** collect EIO log begin ********************")
    col_log_dir = {}
    client_log_lst = []
    """获取客户端的日志"""
    client_log_lst.append(os.path.join(ClientLogPath, ClientLogModule['parastor']))
    col_log_dir[FaultNodeIp] = client_log_lst

    """获取集群节点的log"""
    node_ip_lst = get_nodes_ctrl_ip()
    for node_ip in node_ip_lst:
        parastor_log_lst = get_all_log_for_module('oPara', 'oStor')
        col_log_dir[node_ip] = parastor_log_lst

    """拷贝文件"""
    for key in col_log_dir:
        """创建日志存放路径"""
        log_put_dir = os.path.join(LogHoldDir, key)
        make_dir(log_put_dir, LogHoldIP)
        """拷贝日志"""
        logging.info("******************************")
        info_str = 'node %s: %s will scp' % (key, col_log_dir[key])
        logging.info(info_str)
        scp_log(col_log_dir[key], key, LogHoldIP, log_put_dir)
    """压缩日志"""
    run_tar_log()
    logging.info("******************** collect EIO log succeed ********************")
    return

"""****************************** function error log ******************************"""


def collect_log_other():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 出现功能bug,开始收集所有log
    :return: 
    """
    logging.info("******************** collect all log begin ********************")
    col_log_dir = {}
    """获取集群节点的所有log"""
    node_ip_lst = get_nodes_ctrl_ip()
    for node_ip in node_ip_lst:
        parastor_log_lst = []
        cmd = "ls %s" % os.path.join(ParastorLogPath, '*log*')
        rc, stdout = run_command(cmd, node_ip)
        log_lst = stdout.strip().split()
        for log in log_lst:
            if 'imp' not in log_lst:
                parastor_log_lst.append(log)
        cmd = "ls %s" % os.path.join(BackupLogPath, '*tar*')
        rc, stdout = run_command(cmd, node_ip)
        if rc == 0:
            log_lst = stdout.strip().split()
            for log in log_lst:
                if 'imp' not in log_lst:
                    parastor_log_lst.append(log)
        col_log_dir[node_ip] = parastor_log_lst

    """拷贝文件"""
    for key in col_log_dir:
        """创建日志存放路径"""
        log_put_dir = os.path.join(LogHoldDir, key)
        make_dir(log_put_dir, LogHoldIP)
        """拷贝日志"""
        logging.info("******************************")
        info_str = 'node %s: %s will scp' % (key, col_log_dir[key])
        logging.info(info_str)
        scp_log(col_log_dir[key], key, LogHoldIP, log_put_dir)
    """压缩日志"""
    run_tar_log()
    logging.info("******************** collect all log succeed ********************")
    return


def check_core_exist(core_str, fault_node_ip):
    """
    :author:              baoruobing
    :date  :              2018.07.28
    :description:         检查参数输入的core是否都存在
    :param core_str:      参数输入的core的名字
    :param fault_node_ip: 节点ip
    :return: 
    """
    core_lst = []
    core_name_lst = core_str.strip().split()
    for core_name in core_name_lst:
        if '/' in core_name:
            if check_dir_exist(core_name, fault_node_ip) is False:
                return -1, core_lst
            else:
                core_lst.append(core_name)
        else:

            if check_dir_exist('/' + core_name, fault_node_ip) is False:
                parastor_core_name = os.path.join('/home/parastor/log', core_name)
                if check_dir_exist(parastor_core_name, fault_node_ip) is False:
                    return -1, core_lst
                else:
                    core_lst.append(parastor_core_name)
            else:
                core_lst.append('/' + core_name)
    return 0, core_lst


def arg_analysis():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 参数解析
    :return: 
    """
    global Operation
    global FaultNodeIp
    global Core_Name_lst
    global LogHoldIP
    global LogHoldDir
    global VdbenchIP
    global VdbenchDir

    usage = "usage: %prog [options] arg1 arg2 arg3"
    version = "%prog 4.8"
    parser = OptionParser(usage=usage, version=version)
    parser.add_option("-o", "--operation",
                      type="int",
                      dest="operation",
                      help="Required:True   Type:int                                     "
                           "fault operation                                              "
                           "1 : crash                                                    "
                           "2 : core                                                     "
                           "3 : client cutoff                                            "
                           "4 : EIO                                                      "
                           "5 : other                                                    ")

    parser.add_option("-i", "--ip",
                      type="str",
                      dest="nodeip",
                      default=None,
                      help="Required:True   Type:str   Help:fault node IP or hostname")

    parser.add_option("-c", "--core_name",
                      type="str",
                      dest="core",
                      help='Required:False  Type:str   Help:core name. e.g. "core.1102 core.87220"')

    parser.add_option("-n", "--logname",
                      type="str",
                      dest="logname",
                      help='Required:False  Type:str   Help:log name. e.g. bao')

    parser.add_option("-d", "--destdir",
                      type="str",
                      dest="destdir",
                      help='Required:True   Type:str   Help:dest dir. e.g. 10.2.40.1:/home/log, node1:/home/log')

    parser.add_option("-v", "--vdblog",
                      type="str",
                      dest="vdblog",
                      help='Required:False  Type:str   Help:vdbench log dir. e.g. 10.2.40.1:/home/log, node1:/home/log.'
                           'when -o is 3, this is request')

    options, args = parser.parse_args()
    """检查-o参数"""
    if options.operation is None:
        parser.error("please input -o or --operation")
    if options.operation not in [1, 2, 3, 4, 5]:
        parser.error('the -o or --operation is 1-5')
    Operation = options.operation

    """检查-i参数"""
    if options.nodeip is None:
        parser.error("please input -i or --ip")
    if check_ping(options.nodeip) is False:
        parser.error("-i the ip format is incorrent!!!")
    FaultNodeIp = options.nodeip

    """检查-c参数"""
    if Operation == 2:
        if options.core is None:
            parser.error("please input -c core name")
        """检查节点上core是否存在"""
        rc, core_lst = check_core_exist(options.core, FaultNodeIp)
        if rc != 0:
            parser.error("core is not exist")
        Core_Name_lst = core_lst

    """检查-n参数"""
    dest_log_name = ''
    if options.logname is not None:
        dest_log_name = options.logname.strip()
        if ' ' in dest_log_name:
            parser.error('-n can not have space')

    """检查-d参数"""
    if options.destdir is None:
        parser.error("please input -d or --destdir, collect log dest dir")
    else:
        dest_node_dir = options.destdir.strip()
        if dest_node_dir.count(':') != 1:
            parser.error('-d is not right, e.g. "10.2.40.1:/home/log"')
        """检查节点ip是否存在"""
        dest_ip = dest_node_dir.split(':')[0]
        dest_dir = dest_node_dir.split(':')[-1]
        if check_ping(dest_ip) is False:
            parser.error('-d is not right, e.g. "10.2.40.1:/home/log"')
        """检查log存放目录是否存在"""
        if dest_dir == '':
            parser.error('-d is not right, e.g. "10.2.40.1:/home/log"')
        elif check_dir_exist(dest_dir, dest_ip) is False:
            parser.error('-d is not right, e.g. "10.2.40.1:/home/log"')
        """获取当前时间"""
        current_time = get_current_time()
        if dest_log_name:
            tem_name = '%s_%s' % (current_time, dest_log_name)
        else:
            tem_name = current_time
        dest_dir = os.path.join(dest_dir, tem_name)
        """生成log存放的目录"""
        make_dir(dest_dir, dest_ip)
        LogHoldIP = dest_ip
        LogHoldDir = dest_dir

    """检查-v参数"""
    if Operation == 3:
        if options.vdblog is None:
            parser.error("please input -v vdbench log")
        """检查节点是否可以ping通"""
        vdb_ip = options.vdblog.strip().split(':')[0]
        vdb_dir = options.vdblog.strip().split(':')[-1]
        if check_ping(vdb_ip) is False:
            parser.error('-v is not right, e.g. "10.2.40.1:/home/vdench/output"')
        """检查放vdbench日志的目录是否存在"""
        if vdb_dir == '':
            parser.error('-v is not right, e.g. "10.2.40.1:/home/vdench/output"')
        elif check_dir_exist(vdb_dir, vdb_ip) is False:
            parser.error('-v is not right, e.g. "10.2.40.1:/home/vdench/output"')
        VdbenchIP = vdb_ip
        VdbenchDir = vdb_dir
    return


def collect_log():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 获取执行收集log的类型
    :return: 
    """
    all_collect_log = {1: collect_log_crash,
                       2: collect_log_core,
                       3: collect_log_cutoff,
                       4: collect_log_eio,
                       5: collect_log_other}

    all_collect_log_name = {1: "collect_log_crash",
                            2: "collect_log_core",
                            3: "collect_log_cutoff",
                            4: "collect_log_eio",
                            5: "collect_log_other"}

    str_tem = "This function will be done %s" % all_collect_log_name[Operation]
    logging.info(str_tem)
    return all_collect_log[Operation]


def collect_log_main():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 执行收集日志的主函数
    :return: 
    """
    logging.info("*********** collect log beginning ***********")
    func = collect_log()
    func()
    logging.info("*********** collect log finishing ***********")


def main():
    """参数解析"""
    arg_analysis()
    """初始化日志"""
    log_init()
    """收集日志"""
    collect_log_main()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error("", exc_info=1)
        traceback.print_exc()
        exit(1)

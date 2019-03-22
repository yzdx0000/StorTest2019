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
import sys
import time
import json
import logging
import traceback
import subprocess
import xml.dom.minidom
from optparse import OptionParser
import xml.etree.ElementTree as Et

reload(sys)
sys.setdefaultencoding('utf8')

ParastorBinPath = "/home/parastor/bin/"         # 集群bin文件路径
ParastorLogPath = "/home/parastor/log/"         # 集群log文件路径
BackupLogPath = "/home/parastor/log/backup"     # 集群backup路径
ClientBinPath = "/cliparastor/bin/"             # 客户端bin文件路径
ClientLogPath = "/var/log/"                     # 客户端log文件路径
oOmsBinPath = "/home/parastor/oms/oOms"         # oOms bin文件
oOssBinPath = "/home/parastor/oss/oOss"         # oOss bin文件
LogModule = {'oPara': 'oPara.*', 'oStor': 'oStor.*', 'oRole': 'oRole.*',
             'oJob': 'oJob.*', 'oJmgs': 'oJmgs.*', 'oMgcd': 'mgcd.*',
             'oOms': 'oOms.*', 'oOss': 'oOss.*'}
ImpLogModule = {'oPara': 'imp_oPara.*', 'oStor': 'imp_oStor.*',
                'oRole': 'imp_oRole.*', 'oJob': 'imp_oJob.*',
                'oOms': 'imp_oOms.*', 'oOss': 'imp_oOss.*'}
BackupLogModule = {'oPara': '*oPara*', 'oStor': '*oStor*', 'oRole': '*oRole*',
                   'oJob': '*oJob*', 'oJmgs': '*oJmgs*', 'oMgcd': '*mgcd*'}
ClientLogModule = {'oMgcd_client': 'mgcd.*', 'parastor': 'parastor*', 'imp_parastor': 'imp_parastor*'}
DmesgLogModule = {'message': 'messages*'}
Client_IOstat = '/proc/parastor/cli_iostat'     # 客户端IO性能统计
Client_blstat = '/proc/parastor/cli_block_stat'
Client_iodebug = '/proc/parastor/cli_iocmd_debug'

ParastorKO = '/home/parastor/tools/client/*.ko'
ClientKO = '/cliparastor/tools/client/*.ko'

ZK_Path = '/home/parastor/conf/zk'

Operation = None           # BUG类型
FaultNodeIpLst = []        # 需要收集日志的客户端ip
Crash_Name_dir = {}        # crash的名字，字典, {'10.2.40.1':['crash1', 'crash2'], '10.2.40.2':['crash3']}
Core_Name_dir = {}         # core的名字, 字典, {'10.2.40.1':['core1', 'core2'], '10.2.40.2':['core3']}
LogHoldIP = None           # log保存到的节点ip
LogHoldDir = None          # log保存到的路径
VdbenchIP = None           # vdbench日志存放的ip
VdbenchDir = None          # vdbench日志存放的目录
ModularLst = []            # 模块列表

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


def add_log_lst_to_dic(log_dic, key, log_lst):
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   添加log列表到log字典中
    :param log_dic: log字典
    :param key:     字典的key
    :param log_lst: log列表
    :return: 
    """
    if key in log_dic:
        log_dic[key] += log_lst
    else:
        log_dic[key] = log_lst


def scp_log(log_lst, src_node_ip, dest_node_ip, dest_dir):
    """
    :author:             baoruobing
    :date  :             2018.07.28
    :description:        拷贝log
    :param log_lst:      日志列表
    :param src_node_ip:  源节点
    :param dest_node_ip: 日志存放节点
    :param dest_dir:     日志存放目录
    :return: 
    """
    log_list_true = list(set(log_lst))
    for log in log_list_true:
        if check_dir_exist(log, src_node_ip) is False:
            continue
        if "backup" in log:
            dest_dir_backup = os.path.join(dest_dir, 'backup')
            make_dir(dest_dir_backup, dest_node_ip)
            cmd = 'scp -rp root@%s:%s root@%s:%s' % \
                  (src_node_ip, log, dest_node_ip, dest_dir_backup)
            info_str = "scp %s:%s  to  %s:%s" % (src_node_ip, log, dest_node_ip, dest_dir_backup)
        else:
            cmd = 'scp -rp root@%s:%s root@%s:%s' % \
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
    """
    pwd_dir = os.path.dirname(LogHoldDir)
    src_dir = os.path.basename(LogHoldDir)
    tar_name = "%s.tar.gz" % src_dir
    tar_log(pwd_dir, tar_name, src_dir, LogHoldIP)
    """
    return


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


def get_node_id_by_ip(node_ip):
    '''
    date  :      2017.07.12
    Description: 根据节点ip获取节点的id
    :param       node_ip:节点ip 
    :return:     节点id
    '''
    cmd = 'pscli --command=get_nodes'
    rc, stdout = run_command(cmd)
    if rc != 0:
        raise Exception("get node %s all ip failed!!!" % node_ip)
    msg = json_loads(stdout)
    nodes_info = msg["result"]["nodes"]
    for node in nodes_info:
        ctl_ip = node["ctl_ips"][0]["ip_address"]
        if node_ip == ctl_ip:
            return node["node_id"]
    return None


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


def stat_file(file, node_ip=None):
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   获取文件的元数据
    :param file:    文件
    :param node_ip: 节点ip
    :return: 
    """
    cmd = 'stat %s'
    rc, stdout = run_command(cmd, node_ip)
    if rc != 0:
        raise Exception("cmd: %s failed!!!" % cmd)
    return rc, stdout


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
    '''
    config_info = xml.dom.minidom.parse('/home/parastor/conf/node.xml')
    zk_info = config_info.getElementsByTagName('zookeeper')[0]
    zk_server_lst = zk_info.getElementsByTagName('zk_server')
    node_ip_lst = []
    for zk_server in zk_server_lst:
        node_ip = zk_server.getElementsByTagName('zk_ips')[0].getElementsByTagName('ip')[0].firstChild.nodeValue
        node_ip_lst.append(node_ip)
    return node_ip_lst
    
    cmd = "pscli --command=get_nodes"
    rc, stdout = run_command(cmd)
    if rc != 0:
        raise Exception("get nodes failed")
    stdout = json_loads(stdout)
    node_info_lst = stdout['result']['nodes']
    node_ip_lst = []
    for node_info in node_info_lst:
        node_ip = node_info['ctl_ips'][0]['ip_address']
        node_ip_lst.append(node_ip)
    return node_ip_lst
    '''
    zk_cli = os.path.join(ZK_Path, 'bin', 'zkCli.sh')
    cmd = "sh %s get /parastor0/conf/NODES/0" % zk_cli
    rc, stdout = run_command(cmd)
    if rc != 0:
        raise Exception("zk get nodes failed!!!")
    pre_id = stdout.find('<?xml version="1.0"')
    last_id = stdout.find('</nodes>') + 8
    xml_str = stdout[pre_id:last_id]
    root = Et.fromstring(xml_str)
    node_ip_lst = []
    for ctl_ips in root.iter('ctl_ips'):
        ip = ctl_ips.find('ip')
        node_ip_lst.append(ip.attrib['ip_address'])
    return node_ip_lst


def get_mgr_nodes_ip():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 获取所有管理节点的管理ip
    :return: 
    """
    zk_cli = os.path.join(ZK_Path, 'bin', 'zkCli.sh')
    cmd = "sh %s get /parastor0/conf/NODES/0" % zk_cli
    rc, stdout = run_command(cmd)
    if rc != 0:
        raise Exception("zk get nodes failed!!!")
    pre_id = stdout.find('<?xml version="1.0"')
    last_id = stdout.find('</nodes>') + 8
    xml_str = stdout[pre_id:last_id]
    root = Et.fromstring(xml_str)
    mgr_node_ip_lst = []
    for node in root.findall('node'):
        if node.find('zkId').text == '0':
            continue
        mgr_node_ip_lst.append(node.find('ctl_ips').find('ip').attrib['ip_address'])
    return mgr_node_ip_lst


def check_node_mgr(node_ip):
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   检查一个节点是否是管理节点
    :param node_ip: 节点ip
    :return: 
    """
    mgr_node_ip_lst = get_mgr_nodes_ip()
    if node_ip in mgr_node_ip_lst:
        return True
    else:
        return False


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


def collent_log_mod():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 按照模块收集日志
    :return: 
    """
    logging.info("******************** collect modular log begin ********************")
    col_log_dir = {}

    """获取客户端的日志"""
    for node_ip in FaultNodeIpLst:
        """获取客户端的性能统计"""
        client_log_lst = []
        client_iostat_lst = get_client_iostat(node_ip)
        client_log_lst += client_iostat_lst
        """获取客户端的日志"""
        client_log_lst.append(os.path.join(ClientLogPath, ClientLogModule['parastor']))
        client_log_lst.append(os.path.join(ClientLogPath, ClientLogModule['imp_parastor']))
        client_log_lst.append(os.path.join(BackupLogPath, "*"))
        client_log_lst.append(os.path.join(ClientLogPath, DmesgLogModule['message']))
        add_log_lst_to_dic(col_log_dir, node_ip, client_log_lst)

    """获取集群节点的所有log"""
    node_ip_lst = get_nodes_ctrl_ip()
    for node_ip in node_ip_lst:
        parastor_log_lst = []
        for modular in ModularLst:
            if modular == 'oMgcd':
                modular = 'mgcd'
            parastor_log_lst.append(os.path.join(ParastorLogPath, '*%s*' % modular))
            parastor_log_lst.append(os.path.join(BackupLogPath, '*%s*' % modular))
        add_log_lst_to_dic(col_log_dir, node_ip, parastor_log_lst)

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


def collect_log_crash():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 出现crash,收集crash相关log
    :return: 
    """
    logging.info("******************** collect crash log begin ********************")
    col_log_dir = {}
    for node_ip in Crash_Name_dir:
        log_lst = []
        if check_dir_exist(ParastorKO, node_ip):
            """收集crash"""
            log_lst += Crash_Name_dir[node_ip]
            """收集ko"""
            log_lst.append(ParastorKO)
            """收集客户端log"""
            log_lst.append(os.path.join(ClientLogPath, ClientLogModule['parastor']))
            log_lst.append(os.path.join(ClientLogPath, ClientLogModule['imp_parastor']))
            log_lst.append(os.path.join(ClientLogPath, DmesgLogModule['message']))
        elif check_dir_exist(ClientKO, node_ip):
            """收集crash"""
            log_lst += Crash_Name_dir[node_ip]
            """收集ko"""
            log_lst.append(ClientKO)
            """收集客户端log"""
            log_lst.append(os.path.join(ClientLogPath, ClientLogModule['parastor']))
            log_lst.append(os.path.join(ClientLogPath, ClientLogModule['imp_parastor']))
            log_lst.append(os.path.join(BackupLogPath, "*"))
            log_lst.append(os.path.join(ClientLogPath, DmesgLogModule['message']))
        else:
            """收集crash"""
            log_lst += Crash_Name_dir[node_ip]
            """收集客户端log"""
            log_lst.append(os.path.join(ClientLogPath, ClientLogModule['parastor']))
            log_lst.append(os.path.join(ClientLogPath, ClientLogModule['imp_parastor']))
            log_lst.append(os.path.join(BackupLogPath, "*"))
            log_lst.append(os.path.join(ClientLogPath, DmesgLogModule['message']))
        col_log_dir[node_ip] = log_lst

    """拷贝log文件"""
    for node_ip in col_log_dir:
        """创建日志存放路径"""
        log_put_dir = os.path.join(LogHoldDir, node_ip)
        make_dir(log_put_dir, LogHoldIP)
        """拷贝日志"""
        logging.info("******************************")
        info_str = 'node %s: %s will scp' % (node_ip, col_log_dir[node_ip])
        logging.info(info_str)
        scp_log(col_log_dir[node_ip], node_ip, LogHoldIP, log_put_dir)

    """压缩日志"""
    run_tar_log()
    logging.info("******************** collect crash log succeed ********************")
    return

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


def collect_log_core():
    logging.info("******************** collect core log begin ********************")
    col_log_dir = {}

    """获取集群各个节点的ip"""
    node_ip_lst = get_nodes_ctrl_ip()

    """获取所有core的模块"""
    core_modular_lst = []
    core_modular_name_lst = []
    for node_ip in Core_Name_dir:
        for core_name in Core_Name_dir[node_ip]:
            modular = get_core_modular(core_name, node_ip)
            if modular not in core_modular_lst:
                core_modular_lst.append(modular)
                core_modular_name_lst.append(os.path.basename(modular))

    for node_ip in node_ip_lst:
        parastor_log_lst = []
        """1> 保存这个节点的core"""
        if node_ip in Core_Name_dir:
            parastor_log_lst = Core_Name_dir[node_ip][:]
        """2> 保存所有bin文件"""
        core_modular_tmp_lst = core_modular_lst[:]
        if '/cliparastor/bin/oMgcd_client' in core_modular_tmp_lst:
            core_modular_tmp_lst.remove('/cliparastor/bin/oMgcd_client')
        parastor_log_lst += core_modular_tmp_lst
        """3> 保存log"""
        for modular_name in core_modular_name_lst:
            if modular_name == 'oMgcd_client':
                continue
            if modular_name == 'oPara':
                parastor_log_lst += get_all_log_for_module('oPara', 'oRole')
                parastor_log_lst.append(os.path.join(ParastorLogPath, 'jnl*'))
                parastor_log_lst.append(os.path.join(ParastorLogPath, '*mgs*'))
                continue
            if modular_name == 'oStor':
                parastor_log_lst += get_all_log_for_module('oStor')
                parastor_log_lst.append(os.path.join(ParastorLogPath, '*obs*'))
                parastor_log_lst.append(os.path.join(ParastorLogPath, '*ssdc*'))
                continue
            if modular_name in LogModule:
                parastor_log_lst += get_all_log_for_module(modular_name)
            else:
                parastor_log_lst.append(os.path.join(ParastorLogPath, '*cnas*'))
                parastor_log_lst.append(os.path.join(ParastorLogPath, 'log.*'))
                parastor_log_lst.append(os.path.join(BackupLogPath, '*cnas*'))
                parastor_log_lst.append(os.path.join(BackupLogPath, '*log.*'))
        parastor_log_lst.append(os.path.join(ClientLogPath, DmesgLogModule['message']))
        add_log_lst_to_dic(col_log_dir, node_ip, parastor_log_lst)

    for node_ip in Core_Name_dir:
        if node_ip not in node_ip_lst:
            """1> 保存这个节点的core"""
            parastor_log_lst = Core_Name_dir[node_ip][:]
            """2> 保存所有bin文件"""
            modular_name_lst = []
            for core_name in Core_Name_dir[node_ip]:
                modular = get_core_modular(core_name, node_ip)
                modular_name = os.path.basename(modular)
                modular_name_lst.append(modular_name)
            modular_name_lst = list(set(modular_name_lst))

            for modular_name in modular_name_lst:
                if modular_name in ClientLogModule:
                    log_file = os.path.join(ClientLogPath, ClientLogModule[modular_name])
                    parastor_log_lst.append(log_file)
                bin_file = os.path.join(ClientBinPath, modular_name)
                parastor_log_lst.append(bin_file)
            parastor_log_lst.append(os.path.join(ClientLogPath, DmesgLogModule['message']))
            add_log_lst_to_dic(col_log_dir, node_ip, parastor_log_lst)

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
    logging.info("******************** collect core log succeed ********************")
    return


"""****************************** client cutoff log ******************************"""


def get_lat_log():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 获取各模块的性能统计信息
    :return: 
    """
    lat_path = '/tmp/lat_log_col_p300'
    if os.path.exists(lat_path):
        cmd = 'rm -rf %s' % lat_path
        run_command(cmd)
    os.makedirs(lat_path)
    lat_file = os.path.join(lat_path, 'lat.log')
    logging.info("get lat log begin, please wait for a while")
    cmd = 'sh /home/parastor/tools/print_lat.sh %s' % lat_file
    rc, stdout = run_command(cmd)
    if rc != 0:
        logging.error("print_lat.sh failed!!!")
    return lat_path


def get_client_iostat(node_ip):
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   获取客户端性能文件
    :param node_ip: 节点ip
    :return: 
    """
    client_iostat_dir = '/tmp/client_iostat_col_p300'
    if check_dir_exist(client_iostat_dir, node_ip):
        cmd = 'rm -rf %s' % client_iostat_dir
        run_command(cmd, node_ip)
    make_dir(client_iostat_dir, node_ip)
    client_iostat_file = os.path.join(client_iostat_dir, 'cli_iostat')
    client_blstat_file = os.path.join(client_iostat_dir, 'cli_block_stat')
    client_iodebug_file = os.path.join(client_iostat_dir, 'cli_iocmd_debug')
    cmd = "cat %s > %s" % (Client_IOstat, client_iostat_file)
    run_command(cmd, node_ip)
    cmd = "cat %s > %s" % (Client_blstat, client_blstat_file)
    run_command(cmd, node_ip)
    cmd = "cat %s > %s" % (Client_iodebug, client_iodebug_file)
    run_command(cmd, node_ip)
    cli_lat_lst = [client_iostat_file, client_blstat_file, client_iodebug_file]
    return cli_lat_lst


def collect_log_cutoff():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 出现断流,开始收集log
    :return: 
    """
    logging.info("******************** collect cutoff log begin ********************")
    col_log_dir = {}
    for node_ip in FaultNodeIpLst:
        """获取客户端的性能统计"""
        client_log_lst = []
        client_iostat_lst = get_client_iostat(node_ip)
        client_log_lst += client_iostat_lst
        """获取客户端的日志"""
        client_log_lst.append(os.path.join(ClientLogPath, ClientLogModule['parastor']))
        client_log_lst.append(os.path.join(ClientLogPath, ClientLogModule['imp_parastor']))
        client_log_lst.append(os.path.join(BackupLogPath, "*"))
        client_log_lst.append(os.path.join(ClientLogPath, DmesgLogModule['message']))
        add_log_lst_to_dic(col_log_dir, node_ip, client_log_lst)

    """获取本节点的所有ip"""
    local_node_ip_lst = get_one_node_all_ip()
    """获取集群节点的log"""
    node_ip_lst = get_nodes_ctrl_ip()
    for node_ip in node_ip_lst:
        parastor_log_lst = []
        """本节点获取性能统计"""
        if node_ip in local_node_ip_lst:
            lat_log_path = get_lat_log()
            parastor_log_lst.append(lat_log_path)
        """获取log"""
        parastor_log_lst.append(os.path.join(ParastorLogPath, '*log*'))
        parastor_log_lst.append(os.path.join(BackupLogPath, '*'))

        parastor_log_lst.append(os.path.join(ClientLogPath, ClientLogModule['parastor']))
        parastor_log_lst.append(os.path.join(ClientLogPath, DmesgLogModule['message']))
        add_log_lst_to_dic(col_log_dir, node_ip, parastor_log_lst)

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

    if VdbenchIP is not None:
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
    for node_ip in FaultNodeIpLst:
        """获取客户端的性能统计"""
        client_log_lst = []
        client_iostat_lst = get_client_iostat(node_ip)
        client_log_lst += client_iostat_lst
        """获取客户端的日志"""
        client_log_lst.append(os.path.join(ClientLogPath, ClientLogModule['parastor']))
        client_log_lst.append(os.path.join(ClientLogPath, ClientLogModule['imp_parastor']))
        client_log_lst.append(os.path.join(BackupLogPath, "*"))
        client_log_lst.append(os.path.join(ClientLogPath, DmesgLogModule['message']))
        add_log_lst_to_dic(col_log_dir, node_ip, client_log_lst)

    """获取集群节点的log"""
    node_ip_lst = get_nodes_ctrl_ip()
    for node_ip in node_ip_lst:
        parastor_log_lst = get_all_log_for_module('oPara', 'oStor')
        parastor_log_lst.append(os.path.join(ClientLogPath, DmesgLogModule['message']))
        add_log_lst_to_dic(col_log_dir, node_ip, parastor_log_lst)

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


def collect_log_all():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 出现功能bug,开始收集所有log
    :return: 
    """
    logging.info("******************** collect all log begin ********************")
    col_log_dir = {}

    """获取客户端的日志"""
    for node_ip in FaultNodeIpLst:
        """获取客户端的性能统计"""
        client_log_lst = []
        client_iostat_lst = get_client_iostat(node_ip)
        client_log_lst += client_iostat_lst
        """获取客户端的日志"""
        client_log_lst.append(os.path.join(ClientLogPath, ClientLogModule['parastor']))
        client_log_lst.append(os.path.join(ClientLogPath, ClientLogModule['imp_parastor']))
        client_log_lst.append(os.path.join(BackupLogPath, "*"))
        client_log_lst.append(os.path.join(ClientLogPath, DmesgLogModule['message']))
        add_log_lst_to_dic(col_log_dir, node_ip, client_log_lst)

    """获取本节点的所有ip"""
    local_node_ip_lst = get_one_node_all_ip()
    """获取集群节点的所有log"""
    node_ip_lst = get_nodes_ctrl_ip()
    for node_ip in node_ip_lst:
        parastor_log_lst = []
        """本节点获取性能统计"""
        # if node_ip in local_node_ip_lst:
        #    lat_log_path = get_lat_log()
        #    parastor_log_lst.append(lat_log_path)

        parastor_log_lst.append(os.path.join(ParastorLogPath, '*log*'))
        parastor_log_lst.append(os.path.join(BackupLogPath, '*'))

        parastor_log_lst.append(os.path.join(ClientLogPath, ClientLogModule['parastor']))
        parastor_log_lst.append(os.path.join(ClientLogPath, DmesgLogModule['message']))
        add_log_lst_to_dic(col_log_dir, node_ip, parastor_log_lst)

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


def get_process_pid(node_ip, process):
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   获取节点某个进程的pid
    :param node_ip: 节点ip
    :param process: 进程标志
    :return: 
    """
    ps_cmd = ('ps -ef | grep %s | grep -v grep' % process)
    rc, stdout = run_command(ps_cmd, node_ip)
    if rc != 0:
        return None
    pid = stdout.splitlines()[0].split()[1]
    return pid


def get_mgr_log(node_ip):
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   获取节点的管理日志
    :param node_ip: 节点ip
    :return: 
    """
    mgr_log_lst = []
    """1> 收集/tmp/*.log日志"""
    mgr_log_lst.append("/tmp/*.log")

    """2> 收集dev/shm/parastor下所有日志"""
    mgr_log_lst.append("/dev/shm/parastor")

    """3> 收集zk日志"""
    if check_dir_exist(ZK_Path, node_ip=node_ip):
        # mgr_log_lst.append(os.path.join(ZK_Path, 'zookeeper.log*'))
        # mgr_log_lst.append(os.path.join(ZK_Path, 'data'))
        mgr_log_lst.append(ZK_Path)

    """4> 收集/home/parastor/log下日志"""
    mgr_log_lst.append(os.path.join(ParastorLogPath, '*log*'))
    mgr_log_lst.append(os.path.join(BackupLogPath, '*'))

    """5> 收集oJmgs栈信息"""
    ojmgs_jstack_log = "/tmp/oJmgs_jstack_log"
    pid = get_process_pid(node_ip, "/home/parastor/bin/oJmgs")
    if pid:
        cmd = "jstack %s > %s" % (pid, ojmgs_jstack_log)
        run_command(cmd, node_ip)
        mgr_log_lst.append(ojmgs_jstack_log)

    """6> 收集所有进程信息"""
    all_pro_log = "/tmp/all_pro_log"
    cmd = "ps -ef > %s" % all_pro_log
    run_command(cmd, node_ip)
    mgr_log_lst.append(all_pro_log)

    """7> 收集配置文件"""
    conf_log_path = "/home/parastor/conf"
    mgr_log_lst.append(conf_log_path)
    return mgr_log_lst


def collent_log_mgr():
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   收集管理日志
    :return: 
    """
    logging.info("******************** collect mgr log begin ********************")
    col_log_dir = {}

    """获取客户端的日志"""
    for node_ip in FaultNodeIpLst:
        """获取客户端的性能统计"""
        client_log_lst = []
        client_iostat_lst = get_client_iostat(node_ip)
        client_log_lst += client_iostat_lst
        """获取客户端的日志"""
        client_log_lst.append(os.path.join(ClientLogPath, ClientLogModule['parastor']))
        client_log_lst.append(os.path.join(ClientLogPath, ClientLogModule['imp_parastor']))
        client_log_lst.append(os.path.join(BackupLogPath, "*"))
        client_log_lst.append(os.path.join(ClientLogPath, DmesgLogModule['message']))
        add_log_lst_to_dic(col_log_dir, node_ip, client_log_lst)

    """获取本节点的所有ip"""
    local_node_ip_lst = get_one_node_all_ip()
    """获取集群节点的所有log"""
    node_ip_lst = get_nodes_ctrl_ip()
    for node_ip in node_ip_lst:
        parastor_log_lst = []
        """本节点获取pscli命令信息"""
        if node_ip in local_node_ip_lst:
            pscli_node_log = "/tmp/pscli_nodes_log"
            pscli_backend_log = "/tmp/pscli_backend_log"
            pscli_front_log = "/tmp/pscli_front_log"
            pscli_perf_log = "/tmp/pscli_perf_log"
            pscli_all_jobs_log = "/tmp/pscli_all_jobs_log"
            cmd = "pscli --command=get_nodes > %s" % pscli_node_log
            run_command(cmd)
            cmd = "pscli --command=get_node_stat >> %s" % pscli_node_log
            run_command(cmd)
            cmd = "pscli --command=get_top_job_stat --job_type=Backend --limit=500 > %s" % pscli_backend_log
            run_command(cmd)
            cmd = "pscli --command=get_top_job_stat --job_type=Front --limit=500 > %s" % pscli_front_log
            run_command(cmd)
            cmd = "pscli --command=get_perf_data > %s" % pscli_perf_log
            run_command(cmd)
            cmd = "pscli --command=get_all_jobs > %s" % pscli_all_jobs_log
            run_command(cmd)
            parastor_log_lst.append(pscli_node_log)
            parastor_log_lst.append(pscli_backend_log)
            parastor_log_lst.append(pscli_front_log)
            parastor_log_lst.append(pscli_perf_log)
            parastor_log_lst.append(pscli_all_jobs_log)

        """管理节点收集日志"""
        if check_node_mgr(node_ip):
            mgr_log_lst = get_mgr_log(node_ip)
            parastor_log_lst += mgr_log_lst
            parastor_log_lst.append(os.path.join(ClientLogPath, ClientLogModule['parastor']))
            parastor_log_lst.append(os.path.join(ClientLogPath, DmesgLogModule['message']))
        else:
            parastor_log_lst.append(os.path.join(ParastorLogPath, '*log*'))
            parastor_log_lst.append(os.path.join(BackupLogPath, '*'))
            parastor_log_lst.append(os.path.join(ClientLogPath, ClientLogModule['parastor']))
            parastor_log_lst.append(os.path.join(ClientLogPath, DmesgLogModule['message']))
        """收集WebUI日志"""
        if check_dir_exist("/opt/gridview/", node_ip):
            parastor_log_lst.append("/opt/gridview/GridviewLog")
            parastor_log_lst.append("/opt/gridview/conf")
        add_log_lst_to_dic(col_log_dir, node_ip, parastor_log_lst)

    """拷贝文件"""
    for key in col_log_dir:
        if not col_log_dir[key]:
            continue
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

    logging.info("******************** collect mgr log succeed ********************")
    return


"""****************************** analysis args ******************************"""


def get_crash_info(crash_str):
    """
    :author:          baoruobing
    :date  :          2018.07.28
    :description:     检查参数输入的crash是否都存在,获取所有要收集的crash
    :param crash_str: 参数输入的crash信息,节点和名字
    :return: 
    """
    crash_dir = {}
    crash_info_lst = crash_str.strip().split(',')
    for crash_info in crash_info_lst:
        crash_str_lst = crash_info.strip().split(':')
        fault_node_ip = crash_str_lst[0].strip()
        crash_name = ':'.join(crash_str_lst[1:])
        if '/' in crash_name:
            crash_path = crash_name
        else:
            crash_path = os.path.join('/var/crash', crash_name)
        if fault_node_ip in crash_dir:
            if crash_path in crash_dir[fault_node_ip]:
                continue
            else:
                if check_dir_exist(crash_path, fault_node_ip) is False:
                    return -1, None
                else:
                    crash_dir[fault_node_ip].append(crash_path)
        else:
            tem_lst = []
            if check_ping(fault_node_ip) is False:
                return -2, None
            if check_dir_exist(crash_path, fault_node_ip) is False:
                return -1, None
            tem_lst.append(crash_path)
            crash_dir[fault_node_ip] = tem_lst
    return 0, crash_dir


def check_core_exist(core_name, fault_node_ip):
    """
    :author:              baoruobing
    :date  :              2018.07.28
    :description:         检查参数输入的core是否都存在，获取所有要收集的core
    :param core_name:     core名字
    :param fault_node_ip: core所在的节点ip
    :return: 
    """
    if '/' in core_name:
        if check_dir_exist(core_name, fault_node_ip) is False:
            return -1, ''
        else:
            parastor_core_name = core_name
    else:
        if check_dir_exist('/' + core_name, fault_node_ip) is False:
            parastor_core_name = os.path.join('/home/parastor/log', core_name)
            if check_dir_exist(parastor_core_name, fault_node_ip) is False:
                return -1, ''
        else:
            parastor_core_name = '/' + core_name

    return 0, parastor_core_name


def get_core_info(core_str):
    """
    :author:          baoruobing
    :date  :          2018.07.28
    :description:     检查参数输入的core是否都存在,获取所有要收集的core
    :param core_str:  参数输入的core信息,节点和名字
    :return: 
    """
    core_dir = {}
    core_info_lst = core_str.strip().split(',')
    for core_info in core_info_lst:
        fault_node_ip = core_info.strip().split(':')[0].strip()
        core_name = os.path.basename(core_info.strip().split(':')[-1].strip())
        if fault_node_ip in core_dir:
            rc, core_abs_name = check_core_exist(core_name, fault_node_ip)
            if rc != 0:
                return rc, None
            elif core_abs_name in core_dir[fault_node_ip]:
                continue
            else:
                core_dir[fault_node_ip].append(core_abs_name)
        else:
            tem_lst = []
            if check_ping(fault_node_ip) is False:
                return -2, None
            rc, core_abs_name = check_core_exist(core_name, fault_node_ip)
            if rc != 0:
                return rc, None
            else:
                tem_lst.append(core_abs_name)
                core_dir[fault_node_ip] = tem_lst
    return 0, core_dir


def arg_analysis():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 参数解析
    :return: 
    """
    global Operation
    global Crash_Name_dir
    global Core_Name_dir
    global LogHoldIP
    global LogHoldDir
    global VdbenchIP
    global VdbenchDir
    global FaultNodeIpLst
    global ModularLst

    usage = "usage: %prog [options] arg1 arg2 arg3"
    version = "%prog 0.3"
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
                           "5 : all(不包括管理日志)                                         "
                           "6 : mgr                                                      ")

    parser.add_option("-i", "--ip",
                      type="str",
                      dest="nodeip",
                      default=None,
                      help='Required:False   Type:str   Help:Nodes that need to collect logs.'
                           'e.g. "10.2.40.1, 10.2.40.2"')

    parser.add_option("-c", "--coreorcrash",
                      type="str",
                      dest="coreorcrash",
                      default=None,
                      help='Required:False  Type:str   Help:core or crash name. e.g. '
                           '"10.2.40.1:core.1102, 10.2.40.1:core.87220, 10.2.40.2:core.43520"'
                           '"10.2.40.1:127.0.0.1-2018-07-25-06:30:21, 10.2.40.2:127.0.0.1-2018-07-25-06:30:21"')

    parser.add_option("-n", "--logname",
                      type="str",
                      dest="logname",
                      default=None,
                      help='Required:False  Type:str   Help:log name. e.g. bao')

    parser.add_option("-d", "--destdir",
                      type="str",
                      dest="destdir",
                      default=None,
                      help='Required:True   Type:str   Help:dest dir. e.g. 10.2.40.1:/home/log, node1:/home/log')

    parser.add_option("-v", "--vdblog",
                      type="str",
                      dest="vdblog",
                      default=None,
                      help='Required:False  Type:str   Help:vdbench log dir. e.g. 10.2.40.1:/home/log, node1:/home/log.'
                           'when -o is 3, this is request')

    options, args = parser.parse_args()
    if len(args) == 0:
        """检查-o参数"""
        if options.operation is None:
            parser.error("please input -o or --operation")
        if options.operation not in [1, 2, 3, 4, 5, 6]:
            parser.error('the -o or --operation is 1-6')
        Operation = options.operation
    else:
        Operation = 0
        ModularLst = args

    """检查-i参数"""
    if options.nodeip is None:
        if Operation == 3 or Operation == 4:
            parser.error("-o 3 or 4 need set -i")
    else:
        node_ip_multi = options.nodeip
        if ',' not in node_ip_multi:
            if check_ping(node_ip_multi) is False:
                parser.error("-i the ip format is incorrent!!!")
            FaultNodeIpLst = [node_ip_multi]
        else:
            node_ip_lst = node_ip_multi.split(',')
            node_ip_lst = [node_ip.strip() for node_ip in node_ip_lst]
            for node_ip in node_ip_lst:
                if check_ping(node_ip) is False:
                    parser.error("-i the ip format is incorrent!!!")
            FaultNodeIpLst = node_ip_lst[:]

    """检查-c参数"""
    if Operation == 1 or Operation == 2:
        coreorcrash = options.coreorcrash
        if coreorcrash is None:
            parser.error("please input -c core or crash name")
        if Operation == 1:
            """检查节点crash是否存在"""
            rc, Crash_Name_dir = get_crash_info(coreorcrash)
            if rc == -2:
                parser.error("node ip can not ping")
            elif rc == -1:
                parser.error("crash is not exist")
        else:
            """检查节点上core是否存在"""
            rc, Core_Name_dir = get_core_info(coreorcrash)
            if rc == -2:
                parser.error("node ip can not ping")
            elif rc == -1:
                parser.error("core is not exist")

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
    if options.vdblog is not None:
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
    all_collect_log = {0: collent_log_mod,
                       1: collect_log_crash,
                       2: collect_log_core,
                       3: collect_log_cutoff,
                       4: collect_log_eio,
                       5: collect_log_all,
                       6: collent_log_mgr}

    all_collect_log_name = {0: "collent_log_mod",
                            1: "collect_log_crash",
                            2: "collect_log_core",
                            3: "collect_log_cutoff",
                            4: "collect_log_eio",
                            5: "collect_log_all",
                            6: "collent_log_mgr"}

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
    logging.info(" ".join(sys.argv))
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
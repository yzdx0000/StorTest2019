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
import threading
import subprocess
from optparse import OptionParser
import xml.etree.ElementTree as Et
from multiprocessing import Process


reload(sys)
sys.setdefaultencoding('utf8')

ParastorBinPath = "/home/parastor/bin/"         # 集群bin文件路径
ParastorLogPath = "/home/parastor/log/"         # 集群log文件路径
BackupLogPath = "/home/parastor/log/backup"     # 集群backup路径
ClientBinPath = "/cliparastor/bin/"             # 客户端bin文件路径
ClientLogPath = "/var/log/"                     # 客户端log文件路径
oOmsBinPath = "/home/parastor/oms/oOms"         # oOms bin文件
oOssBinPath = "/home/parastor/oss/oOss"         # oOss bin文件
MysqlPath = "/opt/gvmysql/data"                 # mysql路径
ParastorToolsPath = "/home/parastor/tools"      # 集群tools路径
ClientToolsPath = "/cliparastor/tools"          # 客户端tools路径
BackupLogModule = {'oPara': '*oPara*', 'oStor': '*oStor*', 'oRole': '*oRole*',
                   'oJob': '*oJob*', 'oJmgs': '*oJmgs*', 'oMgcd': '*mgcd*'}
ClientLogModule = {'oMgcd_client': 'mgcd.*', 'parastor': 'parastor*', 'imp_parastor': 'imp_parastor*'}
DmesgLogModule = {'message': 'messages*'}
Client_Property = '/proc/parastor'     # 客户端性能统计

ParastorKO = '/home/parastor/tools/client/*.ko'
ClientKO = '/cliparastor/tools/client/*.ko'

ZK_Path = '/home/parastor/conf/zk'

TmpCollectLogPath = '/tmp/parastor_collect_logs'

ClientNodeIpLst = []        # 需要收集日志的客户端ip
ParastorNodeIpLst = []      # 需要收集日志的集群ip
Crash_Name_dir = {}         # crash的名字，字典, {'10.2.40.1':['crash1', 'crash2'], '10.2.40.2':['crash3']}
LogHoldIP = None            # log保存到的节点ip
LogHoldDir = None           # log保存到的路径
VdbenchIP = None            # vdbench日志存放的ip
VdbenchDir = None           # vdbench日志存放的目录
ModularLst = []             # 模块列表
BadFile = None              # 数据校验错误的文件
BadSector = None            # 数据校验错误的段

"""****************************** common ******************************"""


def run_command(cmd, node_ip=None, timeout=None):
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

    if timeout:
        cmd1 = "timeout %s %s" % (timeout, cmd1)
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
    for log_info in log_lst:
        if check_dir_exist(log_info['log'], src_node_ip) is False:
            continue
        if log_info['path']:
            true_dest_dir = os.path.join(dest_dir, log_info['path'])
            make_dir(true_dest_dir, dest_node_ip)
        else:
            true_dest_dir = dest_dir
        cmd = 'scp -rp %s root@%s:%s' % (log_info['log'], dest_node_ip, true_dest_dir)
        info_str = "scp %s:%s to %s:%s" % (src_node_ip, log_info['log'], dest_node_ip, true_dest_dir)
        logging.info(info_str)
        rc, stdout = run_command(cmd, node_ip=src_node_ip)
        if rc != 0:
            logging.error("node: %s, cmd: %s" % (src_node_ip, cmd))
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


def scp_all_log(col_log_dir):
    """拷贝所有log"""
    logging.info("******************************")
    for key in col_log_dir:
        log_info_list = []
        for mem in col_log_dir[key]:
            if mem not in log_info_list:
                log_info_list.append(mem)
        col_log_dir[key] = log_info_list[:]

        log_lst = []
        for log_info in col_log_dir[key]:
            log_lst.append(log_info['log'])
        info_str = 'node %s: %s will scp' % (key, log_lst)
        logging.info(info_str)
    logging.info("******************************")

    def _scp_all_log(key, col_log_lst):
        """创建日志存放路径"""
        log_put_dir = os.path.join(LogHoldDir, key)
        make_dir(log_put_dir, LogHoldIP)

        scp_log(col_log_lst, key, LogHoldIP, log_put_dir)

    thread_lst = []
    for key in col_log_dir:
        th = threading.Thread(target=_scp_all_log, args=(key, col_log_dir[key]))
        thread_lst.append(th)

    for th in thread_lst:
        th.daemon = True
        th.start()

    while True:
        time.sleep(2)
        for th in thread_lst:
            if th.is_alive():
                break
        else:
            break


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
    cmd = 'mkdir -p %s' % dir
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
    if ParastorNodeIpLst:
        node_ip_lst = ParastorNodeIpLst[:]
    else:
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
    if ParastorNodeIpLst:
        rc, stdout = run_command(cmd, node_ip=ParastorNodeIpLst[0])
    else:
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


def get_lat_log(node_ip):
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 获取各模块的性能统计信息
    :return: 
    """
    lat_path = os.path.join(TmpCollectLogPath, 'lat_log_col_p300')
    if check_dir_exist(lat_path, node_ip=node_ip):
        cmd = 'rm -rf %s' % lat_path
        run_command(cmd)
    make_dir(lat_path, node_ip=node_ip)
    lat_file = os.path.join(lat_path, 'lat.log')
    logging.info("get lat log begin, please wait for a while")
    cmd = 'sh /home/parastor/tools/print_lat.sh %s' % lat_file
    rc, stdout = run_command(cmd, node_ip=node_ip, timeout=1800)
    if rc != 0:
        logging.error("print_lat.sh failed!!!")
        return rc, None
    return rc, lat_path


def get_tools_log(node_ip):
    """收集tools信息"""
    parastor_tools_path = os.path.join(TmpCollectLogPath, "home_parastor_tools_log")
    if check_dir_exist(parastor_tools_path, node_ip=node_ip):
        cmd = 'rm -rf %s' % parastor_tools_path
        run_command(cmd)
    make_dir(parastor_tools_path, node_ip=node_ip)
    badseg_path = os.path.join(parastor_tools_path, "badseg.log")
    badobj_path = os.path.join(parastor_tools_path, "badobj.log")
    ldisktask_injob_path = os.path.join(parastor_tools_path, "ldisktask_injob.log")
    ldisktask_inmos_path = os.path.join(parastor_tools_path, "ldisktask_inmos.log")
    predbg_rcvr_path = os.path.join(parastor_tools_path, "predbg_rcvr.log")
    cmd = "sh /home/parastor/tools/badseg.sh > %s" % badseg_path
    rc, stdout = run_command(cmd, node_ip=node_ip, timeout=900)
    if rc != 0:
        logging.error("badseg.sh failed!!!")
    cmd = "sh /home/parastor/tools/badobj.sh > %s" % badobj_path
    rc, stdout = run_command(cmd, node_ip=node_ip, timeout=900)
    if rc != 0:
        logging.error("badobj.sh failed!!!")
    cmd = "sh /home/parastor/tools/ldisktask_injob.sh > %s" % ldisktask_injob_path
    rc, stdout = run_command(cmd, node_ip=node_ip, timeout=900)
    if rc != 0:
        logging.error("ldisktask_injob.sh failed!!!")
    cmd = "sh /home/parastor/tools/ldisktask_inmos.sh > %s" % ldisktask_inmos_path
    rc, stdout = run_command(cmd, node_ip=node_ip, timeout=900)
    if rc != 0:
        logging.error("ldisktask_inmos.sh failed!!!")
    cmd = "sh /home/parastor/tools/predbg_rcvr.sh > %s" % predbg_rcvr_path
    rc, stdout = run_command(cmd, node_ip=node_ip, timeout=900)
    if rc != 0:
        logging.error("predbg_rcvr.sh failed!!!")

    if BadFile:
        getinfo_datacon_log = os.path.join(parastor_tools_path, "getinfo_datacon.log")
        cmd = "sh /home/parastor/tools/getinfo_datacon.sh %s %s | tee %s" % (BadFile, BadSector, getinfo_datacon_log)
        rc, stdout = run_command(cmd, node_ip=node_ip, timeout=900)
        if rc != 0:
            logging.error("getinfo_datacon.sh failed!!!")
        line_lst = stdout.splitlines()
        badfile_ino = ''
        badseg_index = 0
        for line in line_lst:
            if 'badfile ino' in line:
                badfile_ino = line.split(':')[-1].strip()
            if 'badseg infile' in line:
                badseg_index = line.split(':')[-1].strip()

        ecode_dump_log = os.path.join(parastor_tools_path, "ecode-dump.log")
        cmd = "cd /home/parastor/tools/ecodecheck;sh ecode-dump.sh %s %s %s > %s" % (node_ip, BadFile, badseg_index,
                                                                                     ecode_dump_log)
        rc, stdout = run_command(cmd, node_ip=node_ip, timeout=900)
        if rc != 0:
            logging.error("ecode-dump.sh failed!!!")

        rep_dump_log = os.path.join(parastor_tools_path, "rep-dump.log")
        cmd = "cd /home/parastor/tools/ecodecheck;sh rep-dump.sh %s %s > %s" % (node_ip, BadFile, rep_dump_log)
        rc, stdout = run_command(cmd, node_ip=node_ip, timeout=900)
        if rc != 0:
            logging.error("rep-dump.sh failed!!!")

        cmd = "mv /tmp/iNode-%s* %s" % (badfile_ino, parastor_tools_path)
        run_command(cmd, node_ip=node_ip, timeout=900)
    return parastor_tools_path


def get_nWatch_log(node_ip):
    """
    收集nWatch的log
    """
    cmd = "/home/parastor/tools/collectloginfos.sh all"
    rc, stdout = run_command(cmd, node_ip)
    if rc != 0:
        logging.error("collectloginfos.sh failed!!!")


def get_pscli_log(node_ip):
    """
    收集pscli的log
    """
    pscli_path = os.path.join(TmpCollectLogPath, "pscli")
    if check_dir_exist(pscli_path, node_ip=node_ip):
        cmd = 'rm -rf %s' % pscli_path
        run_command(cmd)
    make_dir(pscli_path, node_ip=node_ip)

    pscli_quota_log = os.path.join(pscli_path, "pscli_quota.log")
    pscli_top_job_log = os.path.join(pscli_path, "pscli_top_job.log")
    pscli_subnets_log = os.path.join(pscli_path, "pscli_subnets.log")
    pscli_all_jobs_log = os.path.join(pscli_path, "pscli_all_jobs.log")
    pscli_perf_data_log = os.path.join(pscli_path, "pscli_perf_data.log")
    pscli_access_zones_log = os.path.join(pscli_path, "pscli_access_zones.log")
    pscli_executor_stat_log = os.path.join(pscli_path, "pscli_executor_stat.log")
    pscli_resource_lock_log = os.path.join(pscli_path, "pscli_resource_lock.log")
    pscli_vip_address_pools_log = os.path.join(pscli_path, "pscli_vip_address_pools.log")
    cmd = "pscli --command=get_quota > %s" % pscli_quota_log
    run_command(cmd, node_ip=node_ip)
    cmd = "pscli --command=get_subnets > %s" % pscli_subnets_log
    run_command(cmd, node_ip=node_ip)
    cmd = "pscli --command=get_all_jobs > %s" % pscli_all_jobs_log
    run_command(cmd, node_ip=node_ip)
    cmd = "pscli --command=get_perf_data > %s" % pscli_perf_data_log
    run_command(cmd, node_ip=node_ip)
    cmd = "pscli --command=get_top_job_stat > %s" % pscli_top_job_log
    run_command(cmd, node_ip=node_ip)
    cmd = "pscli --command=get_access_zones > %s" % pscli_access_zones_log
    run_command(cmd, node_ip=node_ip)
    cmd = "pscli --command=get_executor_stat > %s" % pscli_executor_stat_log
    run_command(cmd, node_ip=node_ip)
    cmd = "pscli --command=get_resource_lock_info > %s" % pscli_resource_lock_log
    run_command(cmd, node_ip=node_ip)
    cmd = "pscli --command=get_vip_address_pools > %s" % pscli_vip_address_pools_log
    run_command(cmd, node_ip=node_ip)
    return pscli_path


def get_process_stack(node_ip):
    """
    收集节点进程栈
    """
    pro_stack_dir = os.path.join(TmpCollectLogPath, "process_stack")
    if check_dir_exist(pro_stack_dir, node_ip):
        cmd = 'rm -rf %s' % pro_stack_dir
        run_command(cmd, node_ip)
    make_dir(pro_stack_dir, node_ip)

    all_pro_log = os.path.join(pro_stack_dir, "all_process.log")
    cmd = "ps -ef > %s" % all_pro_log
    run_command(cmd, node_ip)

    omgcd_stack_log = os.path.join(pro_stack_dir, "omgcd_stack.log")
    cmd = "pidof oMgcd"
    retcode, output = run_command(cmd, node_ip)
    cmd = "pstack %s > %s" % (output.strip(), omgcd_stack_log)
    run_command(cmd, node_ip)

    orole_stack_log = os.path.join(pro_stack_dir, "orole_stack.log")
    cmd = "pidof oRole"
    retcode, output = run_command(cmd, node_ip)
    cmd = "pstack %s > %s" % (output.strip(), orole_stack_log)
    run_command(cmd, node_ip)
    return pro_stack_dir


def get_ip_info(node_ip):
    """
    获取节点ip和路由
    """
    ip_info_dir = os.path.join(TmpCollectLogPath, "ip_route_info")
    if check_dir_exist(ip_info_dir, node_ip):
        cmd = 'rm -rf %s' % ip_info_dir
        run_command(cmd, node_ip)
    make_dir(ip_info_dir, node_ip)

    ip_addr_log = os.path.join(ip_info_dir, "ip_addr.log")
    cmd = "ip addr > %s" % ip_addr_log
    run_command(cmd, node_ip)

    ip_rule_log = os.path.join(ip_info_dir, "ip_rule.log")
    cmd = "ip rule > %s" % ip_rule_log
    run_command(cmd, node_ip)

    ip_route_log = os.path.join(ip_info_dir, "ip_route.log")
    cmd = "ip route > %s" % ip_route_log
    run_command(cmd, node_ip)

    ip_route_show_table_all_log = os.path.join(ip_info_dir, "ip_route_show_table_all.log")
    cmd = "ip route show table all > %s" % ip_route_show_table_all_log
    run_command(cmd, node_ip)

    ip_tables_log = os.path.join(ip_info_dir, "ip_tables.log")
    cmd = "iptables -L > %s" % ip_tables_log
    run_command(cmd, node_ip)
    return ip_info_dir


def get_client_iostat(node_ip):
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   获取客户端性能文件
    :param node_ip: 节点ip
    :return: 
    """
    client_iostat_dir = os.path.join(TmpCollectLogPath, 'proc_parastor')
    if check_dir_exist(client_iostat_dir, node_ip):
        cmd = 'rm -rf %s' % client_iostat_dir
        run_command(cmd, node_ip)
    make_dir(client_iostat_dir, node_ip)

    cmd = "cp -rp %s %s" % (os.path.join(Client_Property, '*'), client_iostat_dir)
    run_command(cmd, node_ip)
    return client_iostat_dir


def run_dlm_mml(node_ip, dlm_mml_file_path, dlm_mml_cmd_lst):
    """
    执行dlm_mml命令
    """
    dlm_mml_sh = os.path.join(dlm_mml_file_path, 'dlm_mml.sh')
    dlm_mml_sh_local = os.path.join('/tmp', 'dlm_mml.sh')

    with open(dlm_mml_sh_local, 'w') as fd:
        for dlm_mml_cmd in dlm_mml_cmd_lst:
            fd.write("%s\n" % dlm_mml_cmd)

    cmd = "scp %s %s:%s" % (dlm_mml_sh_local, node_ip, dlm_mml_sh)
    run_command(cmd)
    cmd = "rm -rf %s" % dlm_mml_sh_local
    run_command(cmd)
    cmd = "sh %s" % dlm_mml_sh
    run_command(cmd, node_ip)


def patastor_get_dlm_mml(node_ip):
    """
    获取集群dlm_mml的日志
    """
    dlm_mml_dir = os.path.join(TmpCollectLogPath, 'dlm_mml')
    if check_dir_exist(dlm_mml_dir, node_ip):
        cmd = 'rm -rf %s' % dlm_mml_dir
        run_command(cmd, node_ip)
    make_dir(dlm_mml_dir, node_ip)

    dlm_mml_path = os.path.join(ParastorToolsPath, 'dlm_mml')

    dlm_mml_5208_1 = os.path.join(dlm_mml_dir, 'dlm_mml_t_5208_l_1.log')
    dlm_mml_5208_0 = os.path.join(dlm_mml_dir, 'dlm_mml_t_5208_l_0.log')
    dlm_mml_5209 = os.path.join(dlm_mml_dir, 'dlm_mml_t_5209_l_0.log')
    dlm_mml_5210 = os.path.join(dlm_mml_dir, 'dlm_mml_t_5210_l_0.log')
    dlm_mml_5211 = os.path.join(dlm_mml_dir, 'dlm_mml_t_5211_l_0.log')

    dlm_mml_5208_1_cmd = ('%s -t 5208 -a -l 1 | grep "coordid" | awk \'{ split($4,ids,":"); split(ids[2],id,",");'
                          'print id[1];}\' | xargs -i %s -t 5208 -p -s {} -l 1 > %s' % (dlm_mml_path, dlm_mml_path,
                                                                                        dlm_mml_5208_1))
    dlm_mml_5208_0_cmd = ('%s -t 5208 -a -l 0 | grep "space handle" | awk \'{ split($3,id,","); print id[1];}\' '
                          '| xargs -i %s -t 5208 -p -s {} -l 0 > %s' % (dlm_mml_path, dlm_mml_path, dlm_mml_5208_0))
    dlm_mml_5209_cmd = ('%s -t 5209 -a -l 0 | grep "space handle" | awk \'{ split($3,id,","); print id[1];}\' '
                        '| xargs -i %s -t 5209 -p -s {} -l 0 > %s' % (dlm_mml_path, dlm_mml_path, dlm_mml_5209))
    dlm_mml_5210_cmd = ('%s -t 5210 -a -l 0 | grep "space handle" | awk \'{ split($3,id,","); print id[1];}\' '
                        '| xargs -i %s -t 5210 -p -s {} -l 0 > %s' % (dlm_mml_path, dlm_mml_path, dlm_mml_5210))
    dlm_mml_5211_cmd = ('%s -t 5211 -a -l 0 | grep "space handle" | awk \'{ split($3,id,","); print id[1];}\' '
                        '| xargs -i %s -t 5211 -p -s {} -l 0 > %s' % (dlm_mml_path, dlm_mml_path, dlm_mml_5211))
    dlm_mml_cmd_lst = [dlm_mml_5208_1_cmd, dlm_mml_5208_0_cmd, dlm_mml_5209_cmd, dlm_mml_5210_cmd, dlm_mml_5211_cmd]
    run_dlm_mml(node_ip, dlm_mml_dir, dlm_mml_cmd_lst)
    return dlm_mml_dir


def client_get_dlm_mml(node_ip):
    """
    获取客户端dlm_mml的日志
    """
    dlm_mml_dir = os.path.join(TmpCollectLogPath, 'dlm_mml')
    if check_dir_exist(dlm_mml_dir, node_ip):
        cmd = 'rm -rf %s' % dlm_mml_dir
        run_command(cmd, node_ip)
    make_dir(dlm_mml_dir, node_ip)

    dlm_mml_path = os.path.join(ClientToolsPath, 'dlm_mml')
    dlm_mml_5210 = os.path.join(dlm_mml_dir, 'dlm_mml_t_5210_l_0.log')
    dlm_mml_cmd_lst = ['%s -t 5210 -a -l 0 | grep "space handle" | awk \'{ split($3,id,","); print id[1];}\' '
                       '| xargs -i %s -t 5210 -p -s {} -l 0 > %s' % (dlm_mml_path, dlm_mml_path, dlm_mml_5210)]
    run_dlm_mml(node_ip, dlm_mml_dir, dlm_mml_cmd_lst)
    return dlm_mml_dir


def get_dlm_mml(node_ip):
    """
    收集dlm_mml信息
    """
    if check_dir_exist(ClientToolsPath, node_ip):
        return client_get_dlm_mml(node_ip)
    else:
        return patastor_get_dlm_mml(node_ip)


"""****************************** function error log ******************************"""


def get_crash_log(node_ip_lst, col_log_dir):
    """
    收集crash日志
    """
    if not Crash_Name_dir:
        return

    for node_ip in Crash_Name_dir:
        log_lst = []
        """收集crash"""
        for crash_log in Crash_Name_dir[node_ip]:
            log_dic = {'log': crash_log, 'path': 'var_crash'}
            log_lst.append(log_dic)
        """收集客户端log"""
        log_dic = {'log': os.path.join(ClientLogPath, ClientLogModule['parastor']), 'path': 'var_log'}
        log_lst.append(log_dic)
        log_dic = {'log': os.path.join(ClientLogPath, ClientLogModule['imp_parastor']), 'path': 'var_log'}
        log_lst.append(log_dic)
        log_dic = {'log': os.path.join(ClientLogPath, DmesgLogModule['message']), 'path': 'var_log'}
        log_lst.append(log_dic)
        log_dic = {'log': os.path.join(ClientLogPath, 'cron*'), 'path': 'var_log'}
        log_lst.append(log_dic)

        if node_ip in node_ip_lst:
            """收集ko"""
            log_dic = {'log': ParastorKO, 'path': 'ko'}
            log_lst.append(log_dic)
        else:
            """收集ko"""
            log_dic = {'log': ClientKO, 'path': 'ko'}
            log_lst.append(log_dic)
            """收集客户端log"""
            log_dic = {'log': ParastorLogPath, 'path': 'home_parastor_log'}
            log_lst.append(log_dic)
        add_log_lst_to_dic(col_log_dir, node_ip, log_lst)


def collect_log_all():
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
    for node_ip in node_ip_lst+ClientNodeIpLst:
        if check_dir_exist(TmpCollectLogPath, node_ip=node_ip):
            cmd = 'rm -rf %s' % TmpCollectLogPath
            run_command(cmd, node_ip=node_ip)
        make_dir(TmpCollectLogPath, node_ip=node_ip)

    """获取客户端的日志"""
    for node_ip in ClientNodeIpLst:
        """获取客户端的性能统计"""
        client_log_lst = []
        client_propert = get_client_iostat(node_ip)
        log_dic = {'log': client_propert, 'path': None}
        client_log_lst.append(log_dic)
        """获取客户端的日志"""
        log_dic = {'log': os.path.join(ClientLogPath, ClientLogModule['parastor']), 'path': 'var_log'}
        client_log_lst.append(log_dic)
        log_dic = {'log': os.path.join(ClientLogPath, ClientLogModule['imp_parastor']), 'path': 'var_log'}
        client_log_lst.append(log_dic)
        log_dic = {'log': os.path.join(ClientLogPath, DmesgLogModule['message']), 'path': 'var_log'}
        client_log_lst.append(log_dic)
        log_dic = {'log': os.path.join(ClientLogPath, 'mgcd*'), 'path': 'var_log'}
        client_log_lst.append(log_dic)
        log_dic = {'log': os.path.join(ClientLogPath, 'cron*'), 'path': 'var_log'}
        client_log_lst.append(log_dic)
        log_dic = {'log': ParastorLogPath, 'path': 'home_parastor_log'}
        client_log_lst.append(log_dic)

        """获取dlm_mml输出"""
        dlm_mml_path = get_dlm_mml(node_ip)
        log_dic = {'log': dlm_mml_path, 'path': None}
        client_log_lst.append(log_dic)

        """获取根目录core"""
        core_lst = get_root_core(node_ip)
        client_log_lst += core_lst
        add_log_lst_to_dic(col_log_dir, node_ip, client_log_lst)

    """获取crash日志"""
    get_crash_log(node_ip_lst+ClientNodeIpLst, col_log_dir)

    for node_ip in node_ip_lst:
        parastor_log_lst = []
        """本节点获取pscli命令信息"""
        if node_ip == node_ip_lst[0]:
            """本节点获取性能统计"""
            rc, lat_log_path = get_lat_log(node_ip)
            log_dic = {'log': lat_log_path, 'path': None}
            parastor_log_lst.append(log_dic)

            """工具打印信息"""
            parastor_tools_path = get_tools_log(node_ip)
            log_dic = {'log': parastor_tools_path, 'path': None}
            parastor_log_lst.append(log_dic)

            """nWatch日志"""
            get_nWatch_log(node_ip)

            """pscli打印"""
            mgr_path = get_pscli_log(node_ip)
            log_dic = {'log': mgr_path, 'path': None}
            parastor_log_lst.append(log_dic)

        """管理节点收集日志"""
        if check_node_mgr(node_ip):
            mgr_log_lst = get_mgr_log(node_ip)
            parastor_log_lst += mgr_log_lst

        """收集/tmp/*.log日志"""
        log_dic = {'log': '/tmp/*.log*', 'path': 'tmp'}
        parastor_log_lst.append(log_dic)

        """收集dev/shm/parastor下所有日志"""
        log_dic = {'log': '/dev/shm/parastor', 'path': 'dev_shm_parastor'}
        parastor_log_lst.append(log_dic)

        """收集所有进程信息"""
        pro_stack_dir = get_process_stack(node_ip)
        log_dic = {'log': pro_stack_dir, 'path': None}
        parastor_log_lst.append(log_dic)

        """收集所有ip信息"""
        ip_info_dir = get_ip_info(node_ip)
        log_dic = {'log': ip_info_dir, 'path': None}
        parastor_log_lst.append(log_dic)

        """收集配置文件"""
        conf_log_path = "/home/parastor/conf"
        log_dic = {'log': conf_log_path, 'path': 'home_parastor_conf'}
        parastor_log_lst.append(log_dic)

        """获取客户端的性能统计"""
        client_propert = get_client_iostat(node_ip)
        log_dic = {'log': client_propert, 'path': None}
        parastor_log_lst.append(log_dic)
        log_dic = {'log': os.path.join(ClientLogPath, ClientLogModule['imp_parastor']), 'path': 'var_log'}
        parastor_log_lst.append(log_dic)
        log_dic = {'log': os.path.join(ClientLogPath, ClientLogModule['parastor']), 'path': 'var_log'}
        parastor_log_lst.append(log_dic)
        log_dic = {'log': os.path.join(ClientLogPath, DmesgLogModule['message']), 'path': 'var_log'}
        parastor_log_lst.append(log_dic)
        log_dic = {'log': os.path.join(ClientLogPath, 'cron*'), 'path': 'var_log'}
        parastor_log_lst.append(log_dic)
        log_dic = {'log': os.path.join(ClientLogPath, 'mgcd*'), 'path': 'var_log'}
        parastor_log_lst.append(log_dic)

        """获取集群日志"""
        log_dic = {'log': ParastorLogPath, 'path': 'home_parastor_log'}
        parastor_log_lst.append(log_dic)
        log_dic = {'log': ParastorBinPath, 'path': 'home_parastor_bin'}
        parastor_log_lst.append(log_dic)
        log_dic = {'log': '/home/parastor/oms/', 'path': 'home_parastor_bin'}
        parastor_log_lst.append(log_dic)
        log_dic = {'log': '/home/parastor/oss/', 'path': 'home_parastor_bin'}
        parastor_log_lst.append(log_dic)

        """获取dlm_mml输出"""
        dlm_mml_path = get_dlm_mml(node_ip)
        log_dic = {'log': dlm_mml_path, 'path': None}
        parastor_log_lst.append(log_dic)

        """获取根目录core"""
        core_lst = get_root_core(node_ip)
        parastor_log_lst += core_lst

        """收集WebUI日志"""
        if check_dir_exist("/opt/gridview/", node_ip):
            log_dic = {'log': "/opt/gridview/GridviewLog", 'path': 'opt_gridview'}
            parastor_log_lst.append(log_dic)
            log_dic = {'log': "/opt/gridview/conf", 'path': 'opt_gridview'}
            parastor_log_lst.append(log_dic)

        """收集数据库日志"""
        if check_dir_exist(MysqlPath, node_ip):
            log_dic = {'log': os.path.join(MysqlPath, 'mysql-bin.*'), 'path': 'opt_gvmysql_data'}
            parastor_log_lst.append(log_dic)
            log_dic = {'log': os.path.join(MysqlPath, '*.err'), 'path': 'opt_gvmysql_data'}
            parastor_log_lst.append(log_dic)
        add_log_lst_to_dic(col_log_dir, node_ip, parastor_log_lst)

    """收集其他日志"""
    if VdbenchIP:
        log_dic = {'log': VdbenchDir, 'path': None}
        add_log_lst_to_dic(col_log_dir, VdbenchIP, [log_dic])

    """拷贝文件"""
    scp_all_log(col_log_dir)

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


def get_root_core(node_ip):
    """
    获取根目录core
    """
    cmd = "ls /core*"
    rc, stdout = run_command(cmd, node_ip)
    if rc != 0:
        return []
    else:
        core_lst = []
        core_tmp_lst = stdout.split()
        for core_info in core_tmp_lst:
            log_dic = {'log': core_info, 'path': 'root_core'}
            core_lst.append(log_dic)
        return core_lst


def get_mgr_log(node_ip):
    """
    :author:        baoruobing
    :date  :        2018.07.28
    :description:   获取节点的管理日志
    :param node_ip: 节点ip
    :return: 
    """
    mgr_log_lst = []
    """3> 收集zk日志"""
    if check_dir_exist(ZK_Path, node_ip=node_ip):
        # mgr_log_lst.append(os.path.join(ZK_Path, 'zookeeper.log*'))
        # mgr_log_lst.append(os.path.join(ZK_Path, 'data'))
        log_dic = {'log': ZK_Path, 'path': None}
        mgr_log_lst.append(log_dic)

    """5> 收集oJmgs栈信息"""
    ojmgs_jstack_log = os.path.join(TmpCollectLogPath, "oJmgs_jstack_log")
    jcmd_native_memory_log = os.path.join(TmpCollectLogPath, "jcmd_native_memory.log")
    jmap_histo_log = os.path.join(TmpCollectLogPath, "jmap_histo.log")
    jmap_heap_log = os.path.join(TmpCollectLogPath, "jmap_heap.log")
    dump_bin_log = os.path.join(TmpCollectLogPath, "dump.bin")
    jstat_log = os.path.join(TmpCollectLogPath, "jstat.log")
    pid = get_process_pid(node_ip, "/home/parastor/bin/oJmgs")
    if pid:
        cmd = "jstack %s > %s" % (pid, ojmgs_jstack_log)
        run_command(cmd, node_ip)
        log_dic = {'log': ojmgs_jstack_log, 'path': 'mgr'}
        mgr_log_lst.append(log_dic)

        cmd = "jcmd %s VM.native_memory > %s" % (pid, jcmd_native_memory_log)
        run_command(cmd, node_ip)
        log_dic = {'log': jcmd_native_memory_log, 'path': 'mgr'}
        mgr_log_lst.append(log_dic)

        cmd = "jmap -histo %s > %s" % (pid, jmap_histo_log)
        run_command(cmd, node_ip)
        log_dic = {'log': jmap_histo_log, 'path': 'mgr'}
        mgr_log_lst.append(log_dic)

        cmd = "jmap -heap %s > %s" % (pid, jmap_heap_log)
        run_command(cmd, node_ip)
        log_dic = {'log': jmap_heap_log, 'path': 'mgr'}
        mgr_log_lst.append(log_dic)

        cmd = "jmap -dump:format=b,file=%s %s" % (dump_bin_log, pid)
        run_command(cmd, node_ip)
        log_dic = {'log': dump_bin_log, 'path': 'mgr'}
        mgr_log_lst.append(log_dic)

        cmd = "jstat -gcutil %s 1s 5 > %s" % (pid, jstat_log)
        run_command(cmd, node_ip)
        log_dic = {'log': jstat_log, 'path': 'mgr'}
        mgr_log_lst.append(log_dic)
    return mgr_log_lst


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
    global Crash_Name_dir
    global LogHoldIP
    global LogHoldDir
    global VdbenchIP
    global VdbenchDir
    global ClientNodeIpLst
    global ParastorNodeIpLst
    global ModularLst
    global BadFile
    global BadSector

    usage = "usage: %prog [options] arg1 arg2 arg3"
    version = "%prog 0.3"
    parser = OptionParser(usage=usage, version=version)
    parser.add_option("-i", "--clientip",
                      type="str",
                      dest="clientip",
                      default=None,
                      help='Required:False   Type:str   Help:Client nodes that need to collect logs.'
                           'e.g. "10.2.40.1, 10.2.40.2"')

    parser.add_option("-I", "--parastorip",
                      type="str",
                      dest="parastorip",
                      default=None,
                      help='Required:False   Type:str   Help:Parastor nodes that need to collect logs.'
                           'e.g. "10.2.40.1, 10.2.40.2"'
                      )
    
    parser.add_option("-c", "--crash",
                      type="str",
                      dest="crash",
                      default=None,
                      help='Required:False  Type:str   Help:crash name. e.g. '
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
                      )

    parser.add_option("-b", "--badfile",
                      type="str",
                      dest="badfile",
                      default=None,
                      help="Required:False  Type:str   Help:data check failed file and bad sector. "
                           "e.g. /mnt/parastor/vdbench/vdb_f0110.file,0x004f0000")

    options, args = parser.parse_args()
    """检查-i参数"""
    if options.clientip:
        node_ip_multi = options.clientip
        if ',' not in node_ip_multi:
            if check_ping(node_ip_multi) is False:
                parser.error("-i the ip format is incorrent!!!")
            ClientNodeIpLst = [node_ip_multi]
        else:
            node_ip_lst = node_ip_multi.split(',')
            node_ip_lst = [node_ip.strip() for node_ip in node_ip_lst]
            for node_ip in node_ip_lst:
                if check_ping(node_ip) is False:
                    parser.error("-i the ip format is incorrent!!!")
            ClientNodeIpLst = node_ip_lst[:]

    """检查-I参数"""
    if options.parastorip:
        parastor_ip_str = options.parastorip
        parastor_ip_lst = parastor_ip_str.split(',')
        parastor_ip_lst = [node_ip.strip() for node_ip in parastor_ip_lst]
        for node_ip in parastor_ip_lst:
            if check_ping(node_ip) is False:
                parser.error("-I the ip format is incorrent!!!")
        ParastorNodeIpLst = parastor_ip_lst[:]

    """检查-c参数"""
    crash = options.crash
    if crash:
        """检查节点crash是否存在"""
        rc, Crash_Name_dir = get_crash_info(crash)
        if rc == -2:
            parser.error("node ip can not ping")
        elif rc == -1:
            parser.error("crash is not exist")

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

    """检查-b参数"""
    if options.badfile is not None:
        BadFile = options.badfile.strip().split(',')[0]
        BadSector = options.badfile.strip().split(',')[-1]
    return


def collect_log_main():
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 执行收集日志的主函数
    :return: 
    """
    logging.info(" ".join(sys.argv))
    logging.info("*********** collect log beginning ***********")
    collect_log_all()
    logging.info("*********** collect log finishing ***********")


def main():
    """主函数"""
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
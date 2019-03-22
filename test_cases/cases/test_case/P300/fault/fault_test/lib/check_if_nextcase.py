#!/usr/bin/python
# -*- encoding=utf8 -*-

import utils_path
import os
import re
import sys
import time
import json
import signal
import logging
import threading
import subprocess
import common
import shell
import get_config

global LOCALNODEFLAG   # 执行脚本的节点是否是集群节点的标志，True:是集群节点，False:非集群节点
LOCALNODEFLAG = False
global LOCALNODEIP     # 本节点ip
global NODE_IP_LST        # 集群节点的管理ip，当执行脚本的节点不是集群节点时使用，列表
global NODE_DATA_IP_LST   # 集群节点的数据ip，当执行脚本的节点不是集群节点时使用，列表
CHECKBADOBJ_WAIT_TIME = 300    # 故障完成后到检查坏对象的等待时间, 单位:s

wait_times = {'down_disk': [1, 300], 'del_disk': [300, 600],
              'down_net': [1, 300], 'del_node': [600, 1200]}


'''
提供给管理网和数据网复用的环境使用。
1、如果管理网和数据网分开的，这个字典不用填写。
2、如果管理网和数据网复用的环境，需要填写每个节点的一个非管理网的ip（可以ping通）
数据类型是字典，键是节点的管理网ip，值是空闲的ip
举例：FREE_IP_DIR = {"10.2.40.1":"20.10.10.1", "10.2.40.2":"20.10.10.2"}
"10.2.40.1"是管理网ip，"20.10.10.1"是数据网没有使用的ip，需要填写所有集群ip
'''
FREE_IP_DIR = {}

global MGR_DATA_IP_SAME    # 管理网和数据网是否复用的标志


Run_Times = 0               # 记录一共运行了多少次


'''***********************************   日志记录   ***********************************'''


##############################################################################
# ##name  :      log_init
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 日志模块初始化
##############################################################################
def log_init(case_log_path):
    """
    日志解析
    """
    global if_nextcase_log
    file_name = os.path.basename(__file__)
    file_name = file_name.split('.')[0]
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    file_name = now_time + '_' + file_name + '.log'
    file_name = os.path.join(case_log_path, file_name)
    print file_name

    if_nextcase_log = logging.getLogger(name='if_nextcase_log')
    if_nextcase_log.setLevel(level=logging.INFO)

    handler = logging.FileHandler(file_name, mode='a')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)

    if_nextcase_log.addHandler(console)
    if_nextcase_log.addHandler(handler)

    return

'''*******************************相关函数 **********************************'''
##############################################################################
# ##name  :      get_nodes_ips_by_ip
# ##parameter:   node_ip:节点ip
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 通过输入的ip获取集群中的所有节点的ip
##############################################################################
def get_nodes_ips_by_ip(node_ip):
    cmd = '"pscli --command=get_nodes"'
    rc, stdout = command(cmd, node_ip)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        node_ip_lst = []
        node_info = json_loads(stdout)
        nodes = node_info['result']['nodes']
        for node in nodes:
            node_ip_lst.append(node['ctl_ips'][0]['ip_address'])

    return node_ip_lst


##############################################################################
# ##name  :      get_local_node_ip
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取本节点的管理ip
##############################################################################
def get_local_node_ip():
    cmd = "pscli --command=get_nodes"
    nodes_ips = []
    rc, stdout = command(cmd)
    if 0 != rc:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        node_info = json_loads(stdout)
        nodes = node_info['result']['nodes']
        for node in nodes:
            nodes_ips.append(node['ctl_ips'][0]['ip_address'])

    cmd = 'ip addr | grep "inet "'
    rc, stdout = command(cmd)
    if 0 != rc:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    lines = stdout.strip().split('\n')
    for line in lines:
        ip = line.split()[1].split('/')[0]
        if ip in nodes_ips:
            return ip
    return None




'''***********************************   公共函数   ***********************************'''


##############################################################################
# ##name  :      command
# ##parameter:   node_ip:节点ip
# ##             cmd:要执行的命令
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 执行命令
##############################################################################
def command(cmd, node_ip=None, timeout=None):
    if node_ip:
        cmd1 = 'ssh %s "%s"' % (node_ip, cmd)
    else:
        cmd1 = cmd

    if timeout is None:
        process = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, unused_err = process.communicate()
        retcode = process.poll()
        return retcode, output
    else:
        result = [None, 0, "", "Timeout"]

        def target(result):
            p = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, preexec_fn=os.setsid)
            result[0] = p
            (result[2], result[3]) = p.communicate()
            result[1] = p.returncode

        thread = threading.Thread(target=target, kwargs={'result': result})
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            # Timeout
            p = result[0]
            wait_time = 5
            while p is None:
                time.sleep(1)
                p = result[0]
                wait_time -= wait_time
                if wait_time == 0:
                    print 'Create process for cmd %s failed.' % cmd
                    exit(1)
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            print 'Process %d is killed.' % p.pid
            thread.join()
        return result[1], result[2]


##############################################################################
# ##name  :      json_loads
# ##parameter:   stdout:需要解析的json格式的字符串
# ##return:      stdout_str:解析的json内容
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 将字符串解析成json
##############################################################################
def json_loads(stdout):
    try:
        # stdout = stdout.replace('\\', '')
        stdout_str = json.loads(stdout, strict=False)
        return stdout_str
    except Exception, e:
        logging.error(stdout)
        raise Exception("Error msg is %s" % e)


##############################################################################
# ##name  :      check_datanet
# ##parameter:   node_ip:节点ip
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 检查节点数据网是否存在
##############################################################################
def check_datanet(node_ip):
    cmd = '"ip addr | grep "inet ""'
    rc, stdout = command(cmd, node_ip)
    if 0 != rc:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    lines = stdout.strip().split('\n')
    for line in lines:
        ip = line.split()[1].split('/')[0]
        if ip in NODE_DATA_IP_LST:
            return True
    return False


##############################################################################
# ##name  :      check_path
# ##parameter:   node_ip:节点ip path:路径
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 执行命令
##############################################################################
def check_path(node_ip, path):
    cmd = 'ls %s' % path
    rc, stdout = command(cmd, node_ip)
    return rc


##############################################################################
# ##name  :      run_cluster_command
# ##parameter:   cmd:要执行的命令
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 执行命令
##############################################################################
def run_cluster_command(cmd, fault_node_ip=None):

    if (fault_node_ip is not None) and (fault_node_ip in NODE_IP_LST):
        node_ips_list = NODE_IP_LST[:]
        node_ips_list.remove(fault_node_ip)
    else:
        node_ips_list = NODE_IP_LST[:]

    for node_ip in node_ips_list:
        # 判断节点是否可以ping通
        if check_ping(node_ip) is False:
            continue
        # 判断数据网是否正常
        if check_datanet(node_ip) is False:
            continue
        # 判断节点上是否有/home/parastor/conf
        if 0 != check_path(node_ip, '/home/parastor/conf'):
            continue
        # 判断节点上是否有集群
        rc, stdout = command(cmd, node_ip)
        if rc == 127:
            continue
        if (rc != 0) and ('FindMasterError' in stdout):
            num = 1
            logging.warn('%s return "FindMasterError" %d times' % (cmd, num))
            while True:
                time.sleep(20)
                num += 1
                rc, stdout = command(cmd, node_ip)
                if (rc != 0) and ('FindMasterError' in stdout):
                    logging.warn('%s return "FindMasterError" %d times' % (cmd, num))
                else:
                    break
        return rc, stdout
    return rc, stdout


##############################################################################
# ##name  :      run_check_vset
# ##parameter:   node_id:节点id
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 检查某个节点是否可以故障元数据盘
##############################################################################
def run_check_vset():
    mgr_node_id_lst = get_mgr_node_ids()
    for node_id in mgr_node_id_lst:
        cmd = '/home/parastor/tools/nWatch -i %s -t oRole -c oRole#rolemgr_view_dump' % node_id
        rc, stdout = run_cluster_command(cmd)
        if 0 != rc or check_stdout(stdout):
            logging.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            continue
        else:
            break
    else:
        return -1
    stdout_lst = stdout.strip().splitlines()
    index = None
    for line in stdout_lst:
        if 'jtype:1 info' in line:
            index = stdout_lst.index(line)
            break
    if index is None:
        logging.warn("get mgrid failed!!!")
        return -1
    stdout_lst1 = stdout_lst[index+1:]
    index = None
    for line in stdout_lst1:
        if 'jtype:' in line:
            index = stdout_lst1.index(line)
            stdout_lst2 = stdout_lst1[:index]
            break
    else:
        stdout_lst2 = stdout_lst1[:]

    index = None
    for line in stdout_lst2:
        if 'grpview info' in line:
            index = stdout_lst2.index(line)
    if index is None:
        logging.warn("get mgrid failed!!!")
        return
    stdout_grpview_lst = stdout_lst2[index:]
    """支持多vmgr的场景"""
    node_lnode_lst = []
    lnode_dic = {}
    lnodeid_lst = []
    for line in stdout_grpview_lst:
        if '-->-->--> lnodeid:' not in line:
            if lnode_dic and 'lnode_id' in lnode_dic:
                node_lnode_lst.append(lnode_dic)
            lnode_dic = {}
            lnodeid_lst = []
        if '-->--> node_sn:' in line:
            node_id = line.split(',')[1].split(':')[-1].strip()
            lnode_dic['node_id'] = node_id
        if '-->-->--> lnodeid:' in line:
            lnodeid = line.split(',')[0].split(':')[-1].strip()
            lnodeid_lst.append(lnodeid)
            lnode_dic['lnode_id'] = lnodeid_lst

    if lnode_dic and 'lnode_id' in lnode_dic:
        node_lnode_lst.append(lnode_dic)
    if not node_lnode_lst:
        logging.warn("There is not lnode")
        return -1
    for lnode_dic in node_lnode_lst:
        node_id = lnode_dic['node_id']
        lnode_lst = lnode_dic['lnode_id']
        for lnode_id in lnode_lst:
            cmd = '/home/parastor/tools/nWatch -i %s -t oPara -c oPara#vmgr_flattennr_dump -a "vmgrid=%s"' \
                  % (node_id, lnode_id)
            rc, stdout = run_cluster_command(cmd)
            if (0 != rc) or check_stdout(stdout) or ('support' in stdout):
                logging.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
                return -1
            vset_num = stdout.strip().split('\n')[-1].split()[2]
            try:
                if int(vset_num) != 0:
                    return 1
                else:
                    logging.info("The current environment all vset is flatten")
                    continue
            except Exception, e:
                logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
                raise Exception("Error msg is %s" % e)

    return 0


##############################################################################
# ##name  :      check_vset
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 每隔一段时间检查一遍是否还有vset没有展平
##############################################################################
def check_vset():
    vset_warnning = 0
    start_time = time.time()
    while True:
        time.sleep(20)
        rc = run_check_vset()
        if 0 == rc:
            break
        now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        if_nextcase_log.info('check_if_nestcase nowtime is %s' % now_time)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        if 1 == rc:
            time_str = "vset exist %dh:%dm:%ds" % (h, m, s)
            logging.info(time_str)
        if vset_warnning ==0:
            if exist_time > 86400:
                vset_warnning = 1
                failfile = os.path.join('/tmp/script_err', now_time)
                cmd = "touch %s" % failfile
                common.command(cmd)
                if_nextcase_log.info('touch %s' %failfile )
                if_nextcase_log.info('####################################')
                if_nextcase_log.info('vset no normal exists more than 1 day')
                if_nextcase_log.info('####################################')
    return


##############################################################################
# ##name  :      run_check_ds
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 检查所有ds是否提供服务
##############################################################################
def run_check_ds():
    node_ids = get_nodes_id()
    for node_id in node_ids:
        cmd = '/home/parastor/tools/nWatch -i %s -t oStor -c oStor#get_basicinfo' % node_id
        rc, stdout = run_cluster_command(cmd)
        if 0 != rc or check_stdout(stdout):
            if_nextcase_log.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            return -1
        else:
            stdout_lst = stdout.strip().split('\n')
            for line in stdout_lst:
                if 'provide serv' in line:
                    flag = line.split(':')[-1].strip()
                    try:
                        if 1 != int(flag):
                            return 1
                    except Exception, e:
                        if_nextcase_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
                        raise Exception("Error msg is %s" % e)

    if_nextcase_log.info("The current environment all ds service is OK")
    return 0


##############################################################################
# ##name  :      check_ds
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 每隔一段时间检查所有ds是否提供服务
##############################################################################
def check_ds():
    dsservice_warnning =0
    start_time = time.time()
    while True:
        time.sleep(20)
        rc = run_check_ds()
        if 0 == rc:
            break
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        if 1 == rc:
            time_str = "ds don't provide service %dh:%dm:%ds" % (h, m, s)
            if_nextcase_log.info(time_str)
        now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        if_nextcase_log.info('check_if_nestcase nowtime is %s' % now_time)
        if dsservice_warnning == 0:
            if exist_time > 86400:
                dsservice_warnning = 1
                failfile = os.path.join('/tmp/script_err', now_time)
                cmd = "touch %s" % failfile
                common.command(cmd)
                if_nextcase_log.info('touch %s' %failfile )
                if_nextcase_log.info('####################################')
                if_nextcase_log.info('ds donnot provide service more than 1 day')
                if_nextcase_log.info('####################################')
    return


##############################################################################
# ##name  :      check_metanode
# ##parameter:   node_id:节点id
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 检查某个节点是否可以故障元数据盘
##############################################################################
def check_metanode(node_id):
    mgr_node_id_lst = get_mgr_node_ids()
    cmd = '/home/parastor/tools/nWatch -t oRole -i %s -c oRole#rolemgr_master_dump' % mgr_node_id_lst[0]
    rc, stdout = run_cluster_command(cmd)
    if 0 != rc or check_stdout(stdout):
        if_nextcase_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        return False
    master_node_id = stdout.split(':')[-1].strip()
    cmd1 = '/home/parastor/tools/nWatch -t oRole -i %s -c oRole#rolemgr_slaveready_dump' % master_node_id
    rc, stdout = run_cluster_command(cmd1)
    if 0 != rc or check_stdout(stdout):
        if_nextcase_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd1, stdout))
        return False
    stdout_lst = stdout.strip().split('\n')
    for line in stdout_lst:
        if 'nodeid' in line and 'is_takeoverable' in line:
            node_id_tmp = line.split()[-2].split(':')[-1].rstrip(',')
            takeoverable = line.split()[-1].split(':')[-1].strip()
            if node_id_tmp != str(node_id):
                continue
            if takeoverable != '1':
                return False

    return True


def check_stdout(stdout):
    # line_lst = stdout.splitlines()
    # line_lst_tmp = line_lst[:]
    # for line in line_lst:
    #     if 'failed to allocate context for device' in line:
    #         line_lst_tmp.remove(line)
    # stdout = '\n'.join(line_lst_tmp)
    if 'failed' in stdout:
        return True
    else:
        return False


##############################################################################
# ##name  :      run_check_badobj
# ##parameter:
# ##return:      False:有坏对象  True:没有坏对象
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 检查是否还有坏对象
##############################################################################
def run_check_badobj(node_id):
    """
    #todo 用oPara还是oJob
    node_id_lst = get_nodes_id()
    badobj_num = 0
    for node_id in node_id_lst:
        cmd = "/home/parastor/tools/nWatch -t oPara -i %d -c RCVR#badobj" % node_id
        rc, stdout = run_cluster_command(cmd)
        if 0 != rc:
            logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        badobj_num += int(stdout.splitlines()[1].strip().split()[-1].strip())

    if badobj_num != 0:
        logging.info("badobj_num = %d" % (badobj_num))
        return False
    """
    cmd = "/home/parastor/tools/nWatch -t oJob -i %s -c RCVR#jobinfo" % node_id
    rc, stdout = run_cluster_command(cmd)
    if 0 != rc or check_stdout(stdout):
        if_nextcase_log.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        return -1
    master_job_id = stdout.split(',')[0].split()[-1]

    cmd = "/home/parastor/tools/nWatch -t oJob -i %s -c RCVR#repairjob" % master_job_id
    rc, result_badobj = run_cluster_command(cmd)
    if 0 != rc or check_stdout(stdout):
        if_nextcase_log.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, result_badobj))
        return -1
    result_tmp = result_badobj.split()
    if "0" != result_tmp[-3]:
        if_nextcase_log.info("masterjob = %s, badobj_num = %s" % (master_job_id, result_tmp[-3]))
        return 1

    if_nextcase_log.info("The current environment does not have badobj")
    return 0


##############################################################################
# ##name  :      check_badobj
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 每隔一段时间检查一遍是否还有坏对象
##############################################################################
def check_badobj(waitflag=True, fault_ip=None):
    badobj_warnning = 0
    if waitflag is True:
        # 等待60s
        if_nextcase_log.info("wait %ds" % CHECKBADOBJ_WAIT_TIME)
        time.sleep(CHECKBADOBJ_WAIT_TIME)

    def _check_badjob():
        node_ip_lst_bak = NODE_IP_LST[:]
        if fault_ip:
            if fault_ip in node_ip_lst_bak:
                node_ip_lst_bak.remove(fault_ip)
        for node_ip in node_ip_lst_bak:
            # 检查是否可以ping通
            if check_ping(node_ip) is False:
                continue
            node_id = get_node_id_by_ip(node_ip)
            result = run_check_badobj(node_id)
            if -1 == result:
                continue
            elif 1 == result:
                return 1
            else:
                return 0

    start_time = time.time()
    num = 0
    while True:
        time.sleep(20)
        if LOCALNODEFLAG is False:
            if 0 == _check_badjob():
                num += 1
                if num >= 10:
                    break
                else:
                    if_nextcase_log.info("The %s time badobj is 0, total times is 10" % num)
                    continue
            else:
                num = 0
        else:
            local_node_id = get_node_id_by_ip(LOCALNODEIP)
            if 0 == run_check_badobj(local_node_id):
                num += 1
                if num >= 10:
                    break
                else:
                    if_nextcase_log.info("The %s time badobj is 0, total times is 10" % num)
                    continue
            else:
                num = 0
        now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        if_nextcase_log.info('check_if_nestcase nowtime is %s' %now_time)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        time_str = "badobj exist %dh:%dm:%ds" % (h, m, s)
        if_nextcase_log.info(time_str)
        if badobj_warnning == 0:
            if exist_time > 86400:
                badobj_warnning = 1
                failfile = os.path.join('/tmp/script_err', now_time)
                cmd = "touch %s" % failfile
                common.command(cmd)
                if_nextcase_log.info('touch %s' %failfile )
                if_nextcase_log.info('####################################')
                if_nextcase_log.info('bad object exists more than 1 day')
                if_nextcase_log.info('####################################')
    return


##############################################################################
# ##name  :      check_metadata
# ##parameter:
# ##return:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 检查元数据的正确性
##############################################################################
def check_metadata():
    cmd = 'sh /home/parastor/tools/chkmobjconn.sh'

    def _check_meta(result):
        flag = True
        line_lst = result.strip().splitlines()
        for line in line_lst:
            if 'mobjs not consistant' not in line:
                continue
            else:
                if line.strip().split()[1] != '0':
                    if_nextcase_log.error(line)
                    flag = False

        if flag is False:
            raise Exception('The current environment has bad mobjs!!!')
        else:
            return

    while True:
        rc, result = run_cluster_command(cmd)
        if 0 != rc:
            if_nextcase_log.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, result))
            continue
        else:
            _check_meta(result)
            if_nextcase_log.info('The current environment does not have bad mobjs')
            break


##############################################################################
# ##name  :      run_check_core
# ##parameter:   node_ip:节点ip
# ##return:      False:有core  True:没有core
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 检查某个节点是否有core
##############################################################################
def run_check_core(node_ip):
    core_path_lst = ['/home/parastor/log/', '/']
    for core_path in core_path_lst:
        core_path_tmp = os.path.join(core_path, 'core*')
        cmd = 'ls %s' % core_path_tmp
        rc, result = command(cmd, node_ip)
        if 0 != rc:
            return True
        else:
            return False


def get_all_volume_layout():
    """
    :author:      baoruobing
    :date  :      2018.08.15
    :description: 获取所有卷的配比
    :return:      (list)卷的配比信息,[{'disk_parity_num':2,'node_parity_num':1,'replica_num':4}]
    """
    cmd = "pscli --command=get_volumes"
    rc, stdout = run_cluster_command(cmd)
    if rc != 0:
        raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    volumes_info = json_loads(stdout)
    volumes_lst = volumes_info['result']['volumes']
    layout_lst = []
    for volume in volumes_lst:
        layout_dic = {}
        layout_dic['disk_parity_num'] = volume['layout']['disk_parity_num']
        layout_dic['node_parity_num'] = volume['layout']['node_parity_num']
        layout_dic['replica_num'] = volume['layout']['replica_num']
        layout_lst.append(layout_dic)
    return layout_lst


def check_share_disk_fault(share_disk_num):
    """
    :author:               baoruobing
    :date  :               2018.08.15
    :description:          检查是否可以做元数据盘故障
    :param share_disk_num: 共享盘个数
    :return:
    """
    """获取所有卷的最大副本数"""
    layout_lst = get_all_volume_layout()
    replica_num = 0
    for layout in layout_lst:
        if layout['disk_parity_num'] != 0:
            replica_num_tmp = layout['disk_parity_num'] + 1
        else:
            replica_num_tmp = layout['replica_num']
        replica_num = replica_num_tmp > replica_num and replica_num_tmp or replica_num

    if share_disk_num > replica_num:
        return True
    else:
        return False


def get_sys_ip():
    sys_ip_lst = []
    cmd = "pscli --command=get_clients"
    rc, result = run_cluster_command(cmd)
    if 0 != rc:
        raise Exception("There is not parastor or get nodes ip failed!!!")
    else:
        result = json_loads(result)
        nodes_lst = result['result']
        for node in nodes_lst:
            sys_ip_lst.append(node['ip'])
    return sys_ip_lst


##############################################################################
# ##name  :      check_core
# ##parameter:
# ##return:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 检查环境是否有core
##############################################################################
def check_core():
    flag = True
    core_node_lst = []
    sys_ip_lst = get_sys_ip()
    for node_ip in sys_ip_lst:
        # 先检查是否可以ping通
        if check_ping(node_ip) is False:
            if_nextcase_log.warn('node %s ping failed!!!' % node_ip)
            continue
        else:
            if run_check_core(node_ip) is False:
                flag = False
                core_node_lst.append(node_ip)
    if flag is False:
        core_node = ','.join(core_node_lst)
        if_nextcase_log.warn("These nodes %s has core!!! ", core_node)
    else:
        if_nextcase_log.info("The current environment does not have core")

    return


##############################################################################
# ##name  :      get_nodes_ip
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取集群中所有节点的管理ip
##############################################################################
def get_nodes_ip():
    cmd = "pscli --command=get_nodes"
    nodes_ips = []
    rc, stdout = run_cluster_command(cmd)
    if 0 != rc:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        node_info = json_loads(stdout)
        nodes = node_info['result']['nodes']
        for node in nodes:
            nodes_ips.append(node['ctl_ips'][0]['ip_address'])

    return nodes_ips


##############################################################################
# ##name  :      get_nodes_id
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取集群中所有节点的id
##############################################################################
def get_nodes_id():
    cmd = "pscli --command=get_nodes"
    nodes_ids = []
    rc, stdout = run_cluster_command(cmd)
    if 0 != rc:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        node_info = json_loads(stdout)
        nodes = node_info['result']['nodes']
        for node in nodes:
            nodes_ids.append(node['node_id'])

    return nodes_ids


##############################################################################
# ##name  :      get_nodes_ips_by_ip
# ##parameter:   node_ip:节点ip
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 通过输入的ip获取集群中的所有节点的ip
##############################################################################
def get_nodes_ips_by_ip(node_ip):
    cmd = '"pscli --command=get_nodes"'
    rc, stdout = command(cmd, node_ip)
    if 0 != rc:
        if_nextcase_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        node_ip_lst = []
        node_info = json_loads(stdout)
        nodes = node_info['result']['nodes']
        for node in nodes:
            node_ip_lst.append(node['ctl_ips'][0]['ip_address'])

    return node_ip_lst


##############################################################################
# ##name  :      get_local_node_ip
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取本节点的管理ip
##############################################################################
def get_local_node_ip():
    cmd = "pscli --command=get_nodes"
    nodes_ips = []
    rc, stdout = command(cmd)
    if 0 != rc:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        node_info = json_loads(stdout)
        nodes = node_info['result']['nodes']
        for node in nodes:
            nodes_ips.append(node['ctl_ips'][0]['ip_address'])

    cmd = 'ip addr | grep "inet "'
    rc, stdout = command(cmd)
    if 0 != rc:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    lines = stdout.strip().split('\n')
    for line in lines:
        ip = line.split()[1].split('/')[0]
        if ip in nodes_ips:
            return ip
    return None


##############################################################################
# ##name  :      get_node_id_by_ip
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 通过节点ip获取节点的id
##############################################################################
def get_node_id_by_ip(node_ip):
    cmd = 'pscli --command=get_nodes'
    rc, stdout = run_cluster_command(cmd)
    if 0 != rc:
        if_nextcase_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        msg = json_loads(stdout)
        nodes_info = msg["result"]["nodes"]
        for node in nodes_info:
            ctl_ip = node["ctl_ips"][0]["ip_address"]
            if node_ip == ctl_ip:
                return node["node_id"]
        if_nextcase_log.info("there is not a node's ip is %s!!!" % node_ip)
        return None


def get_node_ip_by_id(node_id):
    """
    :author:        baoruobing
    :date  :        2018.08.15
    :description:   通过节点id获取节点ip
    :param node_id: (int)节点id
    :return:
    """
    cmd = "pscli --command=get_nodes --ids=%s" % node_id
    rc, stdout = run_cluster_command(cmd)
    if 0 != rc:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        msg = json_loads(stdout)
        node_info = msg["result"]["nodes"][0]
        node_ip = node_info['ctl_ips'][0]['ip_address']
        return node_ip


##############################################################################
# ##name  :      check_node_exist
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 检查某个节点是否存在
##############################################################################
def check_node_exist(node_id, fault_node_ip=None):
    cmd = 'pscli --command=get_nodes'
    rc, stdout = run_cluster_command(cmd, fault_node_ip)
    if 0 != rc:
        if_nextcase_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        msg = json_loads(stdout)
        nodes_info = msg["result"]["nodes"]
        for node in nodes_info:
            if node["node_id"] == node_id:
                return True
        return False


##############################################################################
# ##name  :      get_nodes_data_ip
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取集群的所有数据网ip
##############################################################################
def get_nodes_data_ip():
    cmd = 'pscli --command=get_nodes'
    rc, stdout = run_cluster_command(cmd)
    if rc != 0:
        if_nextcase_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    data_ip_lst = []
    stdout = json_loads(stdout)
    node_info_lst = stdout['result']['nodes']
    for node_info in node_info_lst:
        for data_ip_info in node_info['data_ips']:
            data_ip_lst.append(data_ip_info['ip_address'])

    return data_ip_lst


##############################################################################
# ##name  :      get_nodes_data_ip_by_ip
# ##parameter:   node_ip:节点ip
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取集群的所有数据网ip
##############################################################################
def get_nodes_data_ip_by_ip(node_ip):
    cmd = '"pscli --command=get_nodes"'
    rc, stdout = command(cmd, node_ip)
    if rc != 0:
        if_nextcase_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    data_ip_lst = []
    stdout = json_loads(stdout)
    node_info_lst = stdout['result']['nodes']
    for node_info in node_info_lst:
        for data_ip_info in node_info['data_ips']:
            data_ip_lst.append(data_ip_info['ip_address'])

    return data_ip_lst


##############################################################################
# ##name  :      get_nodepoolid_by_nodeid
# ##parameter:   node_id:节点id
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 通过节点id获取节点所在的节点池的id
##############################################################################
def get_nodepoolid_by_nodeid(node_id):
    cmd = 'pscli --command=get_nodes --ids=%s' % node_id
    rc, stdout = run_cluster_command(cmd)
    if 0 != rc:
        if_nextcase_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        msg = json_loads(stdout)
        node_pool_id = msg["result"]["nodes"][0]['node_pool_id']
        return node_pool_id


##############################################################################
# ##name  :      get_mgr_node_ids
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取集群的管理节点id
##############################################################################
def get_mgr_node_ids():
    cmd = 'pscli --command=get_nodes'
    mgr_node_id_lst = []
    rc, stdout = run_cluster_command(cmd)
    if 0 != rc:
        if_nextcase_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        msg = json_loads(stdout)
        nodes_info = msg["result"]["nodes"]
        for node_info in nodes_info:
            for service_info in node_info['services']:
                if service_info['service_type'] == 'oJmgs':
                    mgr_node_id_lst.append(node_info['node_id'])
                    break
    return mgr_node_id_lst

##############################################################################
# ##name  :      check_rebuild_job
# ##parameter:
# ##return:      True:重建任务存在，Flase:重建任务不存在
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 检查重建任务
##############################################################################
def check_rebuild_job(fault_node_ip=None):
    cmd = 'pscli --command=get_jobengine_state'
    rc, stdout = run_cluster_command(cmd, fault_node_ip)
    if 0 != rc:
        if_nextcase_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        msg = json_loads(stdout)
        jobs_info = msg["result"]["job_engines"]
        for job in jobs_info:
            if job['type'] == 'JOB_ENGINE_REBUILD':
                return True
        return False


##############################################################################
# ##name  :      expand_disk_2_storage_pool
# ##parameter:   storage_pool_id:存储池id  disk_id:磁盘id
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 将磁盘添加到存储池中
##############################################################################
def expand_disk_2_storage_pool(storage_pool_id, disk_id):
    cmd = 'pscli --command=expand_storage_pool --storage_pool_id=%s --disk_ids=%s' % (storage_pool_id, disk_id)
    rc, stdout = run_cluster_command(cmd)
    if 0 != rc:
        if_nextcase_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return

##############################################################################
# ##name  :      check_ping
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 检查ip是否可以ping通
##############################################################################
def check_ping(ip):
    cmd = 'ping -c 3 %s | grep "0 received" | wc -l' % ip
    rc, stdout = command(cmd, timeout=20)
    if '0' != stdout.strip():
        return False
    else:
        cmd = 'ssh %s "ls /"' % ip
        rc, stdout = command(cmd, timeout=20)
        if rc != 0:
            return False
        else:
            return True


##############################################################################
# ##name  :      get_zk_node_ips
# ##parameter:
# ##return:      zk_node_ip_lst: zk节点的管理ip列表
# ##             unzk_node_ip_lst: 非zk节点的管理ip列表
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取系统当前的zk节点和非zk节点的管理ip
##############################################################################
def get_zk_node_ips():
    cmd = "pscli --command=get_nodes"
    rc, stdout = run_cluster_command(cmd)
    if 0 != rc:
        if_nextcase_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        zk_node_ip_lst = []
        unzk_node_ip_lst = []
        stdout_info = json_loads(stdout)
        nodes_info = stdout_info['result']['nodes']
        for node_info in nodes_info:
            if node_info['zk_id'] == 0:
                unzk_node_ip_lst.append(node_info['ctl_ips'][0]['ip_address'])
            else:
                zk_node_ip_lst.append(node_info['ctl_ips'][0]['ip_address'])
        return zk_node_ip_lst, unzk_node_ip_lst



##############################################################################
# ##name  :      check_ip
# ##parameter:   ip:***.***.***.***的格式的ip
# ##return:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 检查ip格式是否正确
##############################################################################
def check_ip(ip):
    pattern = re.compile(r'((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    match = pattern.match(ip)
    if match:
        return True
    else:
        return False


##############################################################################
# ##name  :      update_badjob_time
# ##parameter:
# ##return:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 修改坏对象上报时间
##############################################################################
def update_badjob_time():
    cmd = 'pscli --command=update_param --section=oApp --name=dataio_cmd_timeout_ms --current=120000'
    rc, stdout = run_cluster_command(cmd)
    if 0 != rc:
        if_nextcase_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return


'''***********************************   参数解析   ***********************************'''


##############################################################################
# ##name  :      arg_analysis
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 参数解析
##############################################################################
def arg_analysis():
    global LOCALNODEFLAG
    global LOCALNODEIP
    global NODE_IP_LST
    global NODE_DATA_IP_LST
    global MGR_DATA_IP_SAME

	
def run_command(node_ip, cmd, print_flag=True, timeout=None):
    """
    :author:           baoruobing
    :date  :           2018.07.28
    :description:      执行命令的函数
    :param node_ip:    节点ip
    :param cmd:        要执行的命令
    :param print_flag: 是否需要打印执行的命令和命令执行的结果,默认值:打印
    :param timeout:    命令超时时间
    :return:
    """
    info_str = "node: %s   cmd: %s" % (node_ip, cmd)
    if_nextcase_log.info(info_str)
    rc, stdout, stderr = shell.ssh(node_ip, cmd, timeout)
    if 0 != rc:
        if_nextcase_log.info(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" %
            (cmd, stdout, stderr))
        if stdout != '':
            return rc, stdout
        else:
            return rc, stderr
    elif '' != stdout and print_flag is True:
        if_nextcase_log.info(stdout)
    return rc, stdout


def check_mount_posix(timeout=120):
    # timeout = 120  #run_command执行的超时时间
    posix_ip = get_config.get_client_ip()
    cmd_mount = "mount | grep 'type parastor'"
    rc, stdout = run_command(posix_ip, cmd_mount, True, timeout)
    if 0 != rc:
        if_nextcase_log.error("posix client %s is not mount!" % posix_ip)
        return -1
    else:
        # 获取posix挂载目录
        posix_mount_path = stdout.split(' ')[-4]
        cmd_df = "df -h"
        rc, stdout = run_command(posix_ip, cmd_df, True, timeout)
        if 0 != rc:
            if_nextcase_log.error(
                "posix client %s, operation 'df' timeout!" %
                posix_ip)
            return -1
        else:
            for line in stdout.split('\n'):
                if posix_mount_path in line:
                    if_nextcase_log.info(
                        "posix client %s, mount path: '%s' mount normal" %
                        (posix_ip, posix_mount_path))
                    return 0
                else:
                    pass
            if_nextcase_log.error(
                "posix client %s, operation 'df', dosen't find mount path '%s'" %
                (posix_ip, posix_mount_path))
            return -1


def check_mount_nfs(timeout=120):
    nfs_ip = get_config.get_nfs_client_ip()[0]
    cmd_mount = "mount | grep 'type nfs'"
    rc, stdout = run_command(nfs_ip, cmd_mount, True, timeout)
    if 0 != rc:
        if_nextcase_log.error(
            "nfs client %s is not mount" % nfs_ip)
        return -1
    else:
        nfs_mount_path = stdout.split(' ')[-4]
        cmd_df = "df -h"
        rc, stdout = run_command(nfs_ip, cmd_df, True, timeout)
        if 0 != rc:
            if_nextcase_log.error(
                "nfs client %s, operation 'df' timeout!" %
                nfs_ip)
            return -1
        else:
            for line in stdout.split('\n'):
                if nfs_mount_path in line:
                    if_nextcase_log.info(
                        "nfs client %s, mount path: '%s' mount normal" %
                        (nfs_ip, nfs_mount_path))
                    return 0
                else:
                    pass
            if_nextcase_log.error(
                "nfs client %s, operation 'df', dosen't find mount path '%s'" %
                (nfs_ip, nfs_mount_path))
            return -1


##############################################################################
# ##name  :      check_ping_ssh
# ##parameter:
# ##author:      zhanghan
# ##date  :      2019.02.22
# ##Description: 检查ip是否可以ping通
##############################################################################
def check_ping_ssh(ssh_ip, target_ip):
    cmd = 'ping -c 3 %s | grep "0 received" | wc -l' % target_ip
    rc, stdout = run_command(ssh_ip, cmd, timeout=20)
    if '0' != stdout.strip():
        return False
    else:
        cmd = 'ssh %s "ls /"' % target_ip
        rc, stdout = run_command(ssh_ip, cmd, timeout=20)
        if rc != 0:
            return False
        else:
            return True


def check_vip_address_pool():
    rc, stdout = common.get_vip_address_pools()
    if 0 != rc:
        if_nextcase_log.error("get vip_address_pool failed")
        return -1
    else:
        nas_vip_address_list = list()
        s3_vip_address_list = list()
        stdout = json_loads(stdout)
        info_list = stdout["result"]["ip_address_pools"]
        for sub_info in info_list:
            if sub_info["supported_protocol"] == "NAS":
                nas_vip_address_list = sub_info["vip_addresses"]
            elif sub_info["supported_protocol"] == "S3":
                s3_vip_address_list = sub_info["vip_addresses"]
            else:
                domian_name = sub_info["domain_name"]
                supported_protocol = sub_info["supported_protocol"]
                if_nextcase_log.error(
                    "the supported_protocol of vip_address_pool %s is %s, not NAS or S3!" %
                    (domian_name, supported_protocol))
                return -1

        # add by zhanghan 20190319
        # 对ip池中的两种格式(10.2.40.11-13/10.2.40.11,10.2.40.12,10.2.40.13)作出区分
        nas_vip_list_tmp = list()
        for ip in nas_vip_address_list:
            ip = ip.encode("utf-8")
            if  '-' in ip:
                ip_prefix = ip[0:ip.split('-')[0].rfind('.')]
                ip_suffix_start = int(ip.split('-')[0].split('.')[-1])
                ip_suffix_end = int(ip.split('-')[-1])
                for ip_suffix in range(ip_suffix_start, ip_suffix_end + 1):
                    nas_vip_list_tmp.append(ip_prefix + '.' + str(ip_suffix))
                nas_vip_address_list.remove(ip)
            else:
                pass
        nas_vip_address_list = nas_vip_address_list + nas_vip_list_tmp

        s3_vip_list_tmp = list()
        for ip in s3_vip_address_list:
            ip = ip.encode("utf-8")
            if '-' in ip:
                ip_prefix = ip[0:ip.split('-')[0].rfind('.')]
                ip_suffix_start = int(ip.split('-')[0].split('.')[-1])
                ip_suffix_end = int(ip.split('-')[-1])
                for ip_suffix in range(ip_suffix_start, ip_suffix_end + 1):
                    s3_vip_list_tmp.append(ip_prefix + '.' + str(ip_suffix))
                s3_vip_address_list.remove(ip)
            else:
                pass
        s3_vip_address_list = s3_vip_address_list + s3_vip_list_tmp


        nfs_client_ip = get_config.get_nfs_client_ip()[0]
        s3_client_ip = get_config.get_cosbench_param()["cosbench_client_ip_lst"][0]
        for ip_nas_tmp in nas_vip_address_list:
            res_check_ping_nas = check_ping_ssh(nfs_client_ip, ip_nas_tmp)
            if True != res_check_ping_nas:
                if_nextcase_log.error("ip '%s' in nas vip_addresses can not ping pass!" % ip_nas_tmp)
                return -1
            else:
                pass
        for ip_s3_tmp in s3_vip_address_list:
            res_check_ping_s3 = check_ping_ssh(s3_client_ip, ip_s3_tmp)
            if True != res_check_ping_s3:
                if_nextcase_log.error("ip '%s' in s3 vip_addresses can not ping pass!" % ip_s3_tmp)
                return -1
            else:
                pass
        return 0

def run_func(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            if_nextcase_log.error("the function <%s> excute failed! Please check!!!" % func.__name__)
            sys.exit(1)
    return wrapper

@run_func
def check_others():
    # 检查posix客户端挂载状态及df是否正常
    if_nextcase_log.info("检查posix客户端挂载状态及df")
    rc_check_posix = check_mount_posix()
    if 0 != rc_check_posix:
        raise Exception("posix client mount checking error!")

    # 检查nfs客户端挂载状态及df是否正常
    if_nextcase_log.info("检查nfs客户端挂载状态及df是否正常")
    rc_check_nfs = check_mount_nfs()
    if 0 != rc_check_nfs:
        raise Exception("nfs client mount checking error!")

    # 检查nas/s3协议对应的ip池中的所有ip是否存在，如存在是否可以ping通
    if_nextcase_log.info("检查nas/s3协议对应的ip池中的所有ip是否存在，如存在是否可以ping通")
    rc_check_vip = check_vip_address_pool()
    if 0 != rc_check_vip:
        raise Exception("vip addresses pool checking error!")	
	
	
def run_fault():
    global NODE_IP_LST
    global NODE_DATA_IP_LST
    if_nextcase_log.info(" ".join(sys.argv))
    if_nextcase_log.info("*********** the check if the environment is ok***********")
    # # 检查环境是否有core
    # check_core()
    #
    # # 检查环境是否有坏对象
    # check_badobj(waitflag=False)
    # # 检查环境是否有vset没有展平
    # check_vset()
    # # 检查环境中所有ds是否提供服务
    # check_ds()
    # 检查元数据正确性
    # check_metadata()
	
	# 其他检查项，如posix/nfs客户端挂载状态，vip_address_pool是否正常等
    check_others()
   
    if_nextcase_log.info("***********the environment is ok,you can make fault***********")


def main(case_log_path,mgr_ip):
    global LOCALNODEFLAG
    global  NODE_IP_LST
    global NODE_DATA_IP_LST
    NODE_DATA_IP_LST = get_nodes_data_ip_by_ip(mgr_ip)
    # 参数解析
    arg_analysis()
    # 初始化日志文件
    log_init(case_log_path)
    LOCALNODEFLAG = False
    NODE_IP_LST = get_nodes_ips_by_ip(mgr_ip)
    # 执行故障
    run_fault()


if __name__ == '__main__':
    case_log_path = '/opt/a'
    main(case_log_path,'10.2.40.36')

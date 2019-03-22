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
import traceback
import re
import random
import rep_common
import threading


reload(sys)
sys.setdefaultencoding('utf8')

'''集群节点ip'''
SYSTEM_IP = get_config.get_parastor_ip(0)
deploy_ips = get_config.get_allparastor_ips()

MASTER = rep_common.MASTER
SLAVE_NODE_LST = rep_common.SLAVE_NODE_LST
SLAVE = rep_common.SLAVE
THIRD = rep_common.THIRD




##############################################################################
# ##name  :      command
# ##parameter:   cmd:执行的命令
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 执行命令，并将命令的打印信息写到log文件中,如果想对返回信息进行处理,不能用这个命令
#############################################################################
def command(cmd):
    log.info(cmd)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = process.stdout.readline()
        if '' == line:
            break
        log.debug(line.rstrip())
    process.wait()
    if process.returncode == 0:
        return 0
    else:
        return -1


def pscli_run_command(cmd, print_flag=True, timeout=None, fault_node_ip=None, run_cluster=MASTER):
    """
    :author:              baoruobing
    :date  :              2018.07.28
    :description:         执行pscli和nWatch命令的函数
    :param cmd:           执行的命令
    :param print_flag:    是否需要打印执行的命令和命令执行的结果,默认值:打印
    :param timeout:       命令超时时间
    :param fault_node_ip: 故障的节点, 即不想让命令执行的节点
    :return:
    """
    node_ips_list = []
    if run_cluster == MASTER:
        node_ips_list = deploy_ips[:]
    elif run_cluster == SLAVE:
        salve_ips = SLAVE_NODE_LST
        node_ips_list = salve_ips[:]
    if (fault_node_ip is not None) and (fault_node_ip in deploy_ips):
        node_ips_list.remove(fault_node_ip)

    '''
    def _check_datanet(node_ip):
        cmd = 'ip addr | grep "inet "'
        rc, stdout = run_command_shot_time(cmd, node_ip, print_flag=False)
        judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        lines = stdout.strip().split('\n')
        for line in lines:
            ip = line.split()[1].split('/')[0]
            if ip in Data_Ip_Lst:
                return True
        return False
    '''
    for node_ip in node_ips_list:
        """判断节点是否可以ping通"""
        if check_ping(node_ip) is False:
            continue
        """判断数据网是否正常"""
        # if _check_datanet(node_ip) is False:
        #     continue
        """判断节点上是否有/home/parastor/conf"""
        if check_file_exist(node_ip, '/home/parastor/conf') is False:
            continue
        """判断节点上是否有集群"""
        rc, stdout = run_command(node_ip, cmd, print_flag=print_flag, timeout=timeout)
        if rc == 127:
            continue
        return rc, stdout
    else:
        return 1, None


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
    log.info(info_str)
    rc, stdout, stderr = shell.ssh(node_ip, cmd, timeout)
    if 0 != rc:
        log.info("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
        if stdout != '':
            return rc, stdout
        else:
            return rc, stderr
    elif '' != stdout and print_flag is True:
        log.info(stdout)
    return rc, stdout


def run_command_shot_time(cmd, node_ip=None, print_flag=True):
    """
    :author:           baoruobing
    :date  :           2018.07.28
    :description:      执行shell命令(短时间运行的命令),适用于linux和windows
    :param cmd:        要执行的命令
    :param print_flag: 是否需要打印执行的命令和命令执行的结果,默认值:打印
    :return:
    """
    if node_ip:
        cmd1 = 'ssh %s "%s"' % (node_ip, cmd)
        if print_flag:
            log.info("node: %s   cmd: %s" % (node_ip, cmd))
    else:
        cmd1 = cmd
        if print_flag:
            log.info("cmd: %s" % cmd)
    process = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if '' != output and print_flag is True:
        log.info(output)
    return retcode, output


def case_main(fun, *args, **kwargs):
    """
    :author:         baoruobing
    :date  :         2018.04.17
    :description:    提供给脚本的main函数，可以捕获脚本运行中的异常
    :param fun:     函数对象，一般为脚本入口函数
    :param args:    函数参数
    :param kwargs:  函数参数
    :return:
    """
    try:
        return fun(*args, **kwargs)
    except:
        log.error("case failed!!!", exc_info=1)
        traceback.print_exc()
        exit(1)
    return


def except_exit(info=None, error_code=1):
    """
    :author:            baoruobing
    :date  :            2018.04.17
    :description:       异常退出脚本
    :param error_code:  异常退出码
    :return:
    """
    if info is not None:
        log.error(info)
    log.error(''.join(traceback.format_stack()))
    sys.exit(error_code)


def judge_rc(true_rc, expect_rc, info, exit_flag=True, error_code=1):
    """
    :author:            baoruobing
    :date  :            2018.04.17
    :description:       判断返回码是否等于期望，不等就打印栈和退出脚本
    :param true_rc:     实际返回码
    :param expect_rc:   期望的返回码
    :param info:        步骤信息
    :param exit_flag:   当实际返回码和期望的不同时，是否退出脚本，默认退出
    :param error_code:  退出脚本的错误码，默认1
    :return:
    """
    if true_rc != expect_rc:
        print_info = ("true_rc's type:%s, true_rc:%s, expect_rc's type:%s, expect_rc:%s, info:%s"
                      % (type(true_rc), true_rc, type(expect_rc), expect_rc, info))
        if exit_flag:
            log.error(print_info)
            except_exit(None, error_code)
        else:
            log.warn(print_info)
    return


def judge_rc_unequal(true_rc, unexpect_rc, info, exit_flag=True, error_code=1):
    """
    :author:            baoruobing
    :date  :            2018.04.17
    :description:       判断返回码是否等于期望，相等就打印栈和退出脚本
    :param true_rc:     实际返回码
    :param unexpect_rc: 不期望的返回码
    :param info:        打印信息
    :param exit_flag:   当实际返回码和期望的相同时，是否退出脚本，默认退出
    :param error_code:  退出脚本的错误码，默认1
    :return:
    """
    if true_rc == unexpect_rc:
        print_info = ("true_rc's type:%s, true_rc:%s, unexpect_rc's type:%s, unexpect_rc:%s, info:%s"
                      % (type(true_rc), true_rc, type(unexpect_rc), unexpect_rc, info))
        if exit_flag:
            log.error(print_info)
            except_exit(None, error_code)
        else:
            log.warn(print_info)
    return


##############################################################################
# ##name  :      json_loads
# ##parameter:   json_str:json格式的字符串
# ##author:      baoruobing
# ##date  :      2018.06.04
# ##Description: 将json字符串转成字典格式
#############################################################################
def json_loads(json_str):
    # stdout_str = json_str.replace("\\", "")
    # stdout_str = json.loads(stdout_str, strict=False)
    json_str = json.loads(json_str)
    return json_str


def get_nodes_dataip():
    """
    此函数为初始化时调用，所以保留pscli
    :return:
    """
    cmd = "pscli --command=get_nodes"
    rc, stdout = run_command(SYSTEM_IP, cmd, print_flag=False)
    judge_rc(rc, 0, "get_nodes failed!!!\nstdout:%s" % stdout)
    data_ip_lst = []
    stdout = json_loads(stdout)
    node_info_lst = stdout['result']['nodes']
    for node_info in node_info_lst:
        for data_ip_info in node_info['data_ips']:
            data_ip_lst.append(data_ip_info['ip_address'])
    return data_ip_lst


# Data_Ip_Lst = get_nodes_dataip()


def check_ping(ip, num=2):
    """
    :author:      baoruobing
    :date  :      2018.07.28
    :description: 检查节点是否可以ping通
    :param ip:    要ping的ip
    :return:
    """
    cmd = "ping -c %s %s" % (num, ip)
    rc, stdout = run_command_shot_time(cmd, print_flag=False)
    if rc == 0:
        return True
    else:
        return False


##############################################################################
# ##name  :      check_ip
# ##parameter:   ip:被检测节点的IP
# ##author:      DiWeisong
# ##date  :      2018.04.12
# ##Description: 检测IP是否能够联通
#############################################################################
def check_ip(ip):
    cmd = "ping -c 2 %s" % (ip)
    (res, output) = commands.getstatusoutput(cmd)
    while res != 0:
        log.error("Can not attach %s,please check it." % (ip))
        time.sleep(30)
        cmd = "ping -c 2 %s" % (ip)
        (res, output) = commands.getstatusoutput(cmd)
    else:
        log.info("The ip : %s is ok." % (ip))


class Node():
    '''
    集群中节点的信息及操作
    '''

    def __init__(self):
        pass

    def _command(self, cmd):
        rc, stdout = pscli_run_command(cmd, print_flag=False)
        judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        return stdout

    def get_nodes(self, ids=None):
        """
        :author:      zhangchengyu
        :date  :      2018.11.03
        :description: get_nodes命令
        :return:      标准输出
        """
        rc, stdout = get_nodes(ids=ids)
        judge_rc(rc, 0, "Execute command: get nodes failed. \nstdout: %s" % stdout)
        msg = json_loads(stdout)
        return msg

    def get_nodes_num(self, run_cluster=MASTER):
        """
        :author:      baoruobing
        :date  :      2018.07.24
        :description: 获取节点个数
        :return:      节点个数
        """
        rc, stdout = get_nodes(run_cluster=MASTER)
        judge_rc(rc, 0, "Execute command: get nodes failed. \nstdout: %s" % stdout)
        node_info = json_loads(stdout)
        node_num = node_info['result']['total']
        return node_num

    def get_nodes_id(self, run_cluster=MASTER):
        '''
        date  :      2017.07.12
        Description: 获取集群所有节点的id
        '''
        rc, stdout = get_nodes(run_cluster=run_cluster)
        judge_rc(rc, 0, "Execute command: get nodes failed. \nstdout: %s" % stdout)
        node_info = json_loads(stdout)
        nodes = node_info['result']['nodes']
        nodes_ids = []
        for node in nodes:
            nodes_ids.append(node['node_id'])
        return nodes_ids

    def get_nodes_ip(self):
        '''
        date  :      2017.07.12
        Description: 获取集群所有节点的ip
                     所有节点的ip
        '''
        rc, stdout = get_nodes()
        judge_rc(rc, 0, "Execute command: get nodes failed. \nstdout: %s" % stdout)
        node_info = json_loads(stdout)
        nodes = node_info['result']['nodes']
        nodes_ips = []
        for node in nodes:
            nodes_ips.append(node['ctl_ips'][0]['ip_address'])
        return nodes_ips

    def get_node_ip_by_id(self, node_id):
        '''
        date  :      2017.07.12
        Description: 根据节点id获取节点的ip
        :param       node_id: 节点id
        :return:     节点ip
        '''
        rc, stdout = get_nodes(ids=node_id)
        judge_rc(rc, 0, "Execute command: get nodes failed. \nstdout: %s" % stdout)
        msg = json_loads(stdout)
        node_ip = msg['result']['nodes'][0]['ctl_ips'][0]['ip_address']
        return node_ip

    def get_node_id_by_ip(self, node_ip):
        '''
        date  :      2017.07.12
        Description: 根据节点ip获取节点的id
        :param       node_ip:节点ip
        :return:     节点id
        '''
        rc, stdout = get_nodes()
        judge_rc(rc, 0, "Execute command: get nodes failed. \nstdout: %s" % stdout)
        msg = json_loads(stdout)
        nodes_info = msg["result"]["nodes"]
        for node in nodes_info:
            ctl_ip = node["ctl_ips"][0]["ip_address"]
            if node_ip == ctl_ip:
                return node["node_id"]
        log.warn("there is not a node's ip is %s!!!" % node_ip)
        return None

    def get_node_state(self, node_id):
        '''
        date  :      2017.07.12
        Description: 根据节点id获取节点的状态
        :param       node_id: 节点id
        :return:     节点状态
        '''
        rc, stdout = get_nodes(ids=node_id)
        judge_rc(rc, 0, "Execute command: get nodes failed. \nstdout: %s" % stdout)
        msg_json = json_loads(stdout)
        state = msg_json['result']['nodes'][0]['state']
        return state

    def add_node(self, config_file, fault_node_ip=None):
        """
        :date:              2018.08.11
        :description:       添加节点
        :param config_file: 节点配置文件
        :return:
        """
        rc, stdout = add_nodes(config_file=config_file, fault_node_ip=fault_node_ip)
        return rc, stdout

    def remove_nodes(self, node_ids, remove_mode='AUTO_REBOOT', auto_query=None, msg_out=False, fault_node_ip=None):
        '''
        date  :      2017.07.12
        Description: 删除节点
        :param       node_ids: 节点id
        :return:
        changelog: 20181107   zhangchengyu添加参数remove_mode
        '''
        rc, stdout = remove_node(id=node_ids, remove_mode=remove_mode, auto_query=auto_query,
                                 fault_node_ip=fault_node_ip)
        judge_rc(rc, 0, "Execute command: remove nodes failed. \nstdout: %s" % stdout)
        msgs = ""
        if msg_out is not False:
            msgs = json_loads(stdout)
        return msgs

    def cancel_remove_nodes(self, node_ids):
        '''
        date  :      2018.11.06  zhangchengyu
        Description: 取消删除节点
        :param       node_ids: 节点id
        :return:
        '''
        rc, stdout = cancel_remove_nodes(ids=node_ids)
        judge_rc(rc, 0, "Execute command: cancel remove nodes failed. \nstdout: %s" % stdout)
        msg = json_loads(stdout)
        return msg

    def get_node_eth(self, node_id):
        '''
        date  :      2017.07.12
        Description: 获取节点的数据网eth名字
        :param       node_id:节点id
        :return:     eth_list:网口名字列表
        '''
        rc, stdout = get_nodes(ids=node_id)
        judge_rc(rc, 0, "Execute command: get nodes failed. \nstdout: %s" % stdout)
        data_ip_list = []
        ip_mask_lst = []
        result = json_loads(stdout)
        data_ips = result['result']['nodes'][0]['data_ips']
        for data_ip in data_ips:
            ip = data_ip['ip_address']
            mask = data_ip['subnet_mask']
            data_ip_list.append(ip)
            ip_and_mask = '%s/%s' % (ip, mask)
            ip_mask_lst.append(ip_and_mask)

        node_ip = self.get_node_ip_by_id(node_id)
        eth_list = []
        for ip in data_ip_list:
            cmd1 = 'ip addr | grep %s' % (ip)
            rc, stdout = run_command(node_ip, cmd1)
            judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd1, stdout))
            eth_name = stdout.split()[-1]
            eth_list.append(eth_name)

        return eth_list, data_ip_list, ip_mask_lst

    def get_nodepoolid_by_nodeid(self, node_id):
        """
        :date:          2018.08.11
        :description:   添加节点
        :param node_id: 节点id
        :return:
        """
        rc, stdout = get_nodes(ids=node_id)
        judge_rc(rc, 0, "Execute command: get nodes failed. \nstdout: %s" % stdout)
        msg = json_loads(stdout)
        node_pool_id = msg["result"]["nodes"][0]['node_pool_id']
        return node_pool_id

    def get_client_ips(self):
        '''
        date  :      2017.07.12
        Description: 获取所有客户端节点的ip
        return:      所有客户端节点的ip
        '''
        rc, stdout = get_clients()
        judge_rc(rc, 0, "Execute command: get clients failed. \nstdout: %s" % stdout)
        client_ips = []
        clients_info = json_loads(stdout)
        clients = clients_info['result']
        for client in clients:
            if client['type'] == 'EXTERNAL' and client['inTimeStatus'] != 'SERV_STATE_OK':
                continue
            client_ips.append(client['ip'])
        return client_ips

    def get_external_client_ips(self):
        '''
        date  :      2017.07.12
        Description: 获取所有私有客户端节点的ip
        return:      所有私有客户端节点的ip
        '''
        rc, stdout = get_clients()
        judge_rc(rc, 0, "Execute command: get clients failed. \nstdout: %s" % stdout)
        client_ips = []
        clients_info = json_loads(stdout)
        clients = clients_info['result']
        for client in clients:
            if client['type'] == 'EXTERNAL':
                client_ips.append(client['ip'])
        return client_ips

    def get_node_name_by_id(self, node_id):
        """
        :author:        baorb
        :date:          2017.07.12
        :description:   获取所有私有客户端节点的ip
        :param node_id: 节点id
        :return:
        """
        rc, stdout = get_nodes(ids=node_id)
        judge_rc(rc, 0, "Execute command: get nodes failed. \nstdout: %s" % stdout)
        msg = json_loads(stdout)
        node_ip = msg['result']['nodes'][0]['node_name']
        return node_ip

    def get_master(self):
        """
        :author:      zhangchengyu
        :date:        2018.11.05
        :description: 获取主管理节点ip
        :return:
        """
        rc, stdout = get_master()
        judge_rc(rc, 0, "Execute command: get master failed. \nstdout: %s" % stdout)
        msg = json_loads(stdout)
        return msg

    def get_master_mgr_id(self):
        """
        :author:      baorb
        :date:        2017.07.12
        :description: 获取主管理节点id
        :return:
        """
        rc, stdout = get_master()
        judge_rc(rc, 0, "Execute command: get master failed. \nstdout: %s" % stdout)
        msg = json_loads(stdout)
        node_id = msg['result']['node_id']
        return node_id

    def get_node_all_services(self, node_id):
        """
        :author:        baorb
        :date:          2017.07.12
        :description:   获取一个节点的所有服务
        :param node_id: 节点id
        :return:
        """
        rc, stdout = get_services(node_ids=node_id)
        if rc != 0:
            return rc, []
        stdout = json_loads(stdout)
        service_lst = []
        service_info = stdout['result']['nodes'][0]['services']
        for service in service_info:
            service_lst.append(service['service_type'])
        return rc, service_lst

    def get_orole_node_ids(self):
        """
        :author:        baorb
        :date:          2017.07.12
        :description:   获取管理节点id
        :return:
        """
        mgr_node_id_lst = []
        rc, stdout = get_nodes()
        judge_rc(rc, 0, "get_nodes failed!!! stdout: %s" % stdout)
        msg = json_loads(stdout)
        nodes_info = msg["result"]["nodes"]
        for node_info in nodes_info:
            for service_info in node_info['services']:
                if service_info['service_type'] == 'oRole':
                    mgr_node_id_lst.append(node_info['node_id'])
                    break
        return mgr_node_id_lst


class Nodepool():
    '''
    节点池的信息和操作
    '''

    def __init__(self):
        pass

    def create_node_pool(self, node_pool_name, node_ids, n, m, b, r):
        '''
        date  :      2017.07.12
        Description: 创建节点池
        :param       node_pool_name: 节点池名字
        :param       node_ids: 节点id，格式"1,2,3"
        :param       n: 条带宽度
        :param       m: 磁盘冗余
        :param       b: 节点冗余
        :param       r: 副本数
        :return:
        '''
        rc, stdout = create_node_pool(name=node_pool_name, node_ids=node_ids, stripe_width=n, disk_parity_num=m,
                                      node_parity_num=b, replica_num=r)
        judge_rc(rc, 0, "create node pool failed!!!\nstdout:%s" % stdout)
        log.info("node_pool create succeed!!!")
        return

    def update_node_pool(self, node_pool_id, name, node_ids):
        '''
        date  :      2017.07.12
        Description: 更新节点池
        :param       node_pool_id:
        :param name:
        :param node_ids:
        :return:
        '''
        rc, stdout = update_node_pool(node_pool_id=node_pool_id, name=name, node_ids=node_ids)
        judge_rc(rc, 0, "update node pool failed!!!\nstdout:%s" % stdout)
        log.info("node_pool update succeed!!!")
        return

    def get_node_pool_id_by_name(self, node_pool_name):
        '''
        date  :      2017.07.12
        Description: 根据节点池名字获取节点池id
        :return:     节点池名字
        '''
        rc, stdout = get_node_pools()
        node_pools = stdout
        node_pools = json_loads(node_pools)
        node_pools = node_pools.get('result')
        node_pools = node_pools.get('node_pools')
        for node_pool in node_pools:
            if node_pool.get('name') == node_pool_name:
                return node_pool.get('id')
        return None

    def get_all_node_pool_ids(self):
        '''
        date  :      2017.07.12
        Description: 获取所有节点池id
        :return:     所有节点池的id
        '''
        rc, stdout = get_node_pools()
        node_pools = stdout
        node_pools = json_loads(node_pools)
        node_pools = node_pools.get('result')
        node_pools = node_pools.get('node_pools')
        nodepool_ids = [node_pool.get('id') for node_pool in node_pools]
        return nodepool_ids

    def get_nodepool_info_by_id(self, node_pool_id):
        rc, stdout = get_node_pools(id=node_pool_id)
        judge_rc(rc, 0, "get node pool failed!!!\nstdout:%s" % stdout)
        return stdout

    def delete_node_pool_by_name(self, node_pool_name):
        '''
        date  :      2017.07.12
        Description: 根据节点池名字删除节点池
        :param       node_pool_name: 节点池名字
        :return:
        '''
        node_pool_id = self.get_node_pool_id_by_name(node_pool_name)
        rc, stdout = delete_node_pools(ids=node_pool_id)
        judge_rc(rc, 0, "delete nodepool faild\nstdout:%s" % stdout)
        log.info("node_pool delete succeed!!!")
        return

    def delete_all_node_pools(self):
        '''
        date  :      2017.07.12
        Desription: 删除所有节点池
        :return:
        '''
        nodepool_ids = self.get_all_node_pool_ids()
        if len(nodepool_ids) == 0:
            log.info("ip: %s has no nodepool info!" % SYSTEM_IP)
            return
        ids_str = ",".join(str(i) for i in nodepool_ids)

        rc, stdout = delete_node_pools(ids=ids_str)
        judge_rc(rc, 0, "delete nodepool faild\nstdout:%s" % stdout)
        log.info("node_pools delete succeed!!!")
        return


class Storagepool():
    '''
    存储池相关操作
    '''

    def __init__(self):
        pass

    def create_storage_pool_by_nodepoolid(self, storage_pool_name, node_pool_ids, storage_pool_type="FILE"):
        '''
        date  :      2017.07.12
        Description: 根据节点池id创建存储池
        :param       storage_pool_name: 存储池名字
        :param       node_pool_ids: 节点池id
        :param       storage_pool_type: 存储池类型
        :return:
        '''
        rc, stdout = create_storage_pool(name=storage_pool_name, type=storage_pool_type, node_pool_ids=node_pool_ids)
        if 0 != rc:
            log.error("create storage_pool faild!!!")
        else:
            log.info("storage_pool create succeed!!!")
        return rc, stdout

    def create_storage_pool_by_disks(self, storage_pool_name, disks_ids, storage_pool_type="FILE"):
        '''
        date  :      2017.07.12
        Description: 根据硬盘创建存储池
        :param       storage_pool_name: 存储池名字
        :param       disks_ids: 硬盘id
        :param       storage_pool_type: 存储池类型
        :return:
        '''
        rc, stdout = create_storage_pool(name=storage_pool_name, type=storage_pool_type, disk_ids=disks_ids)
        if 0 != rc:
            log.error("create storage_pool faild!!!")
        else:
            log.info("storage_pool create succeed!!!")
        return rc, stdout

    def expand_storage_pool(self, storagepool_id, disks_ids):
        '''
        date  :      2017.07.12
        Description: 扩充存储池
        :param       storagepool_id: 存储池id
        :param       disks_ids: 硬盘id
        :return:
        '''
        rc, stdout = expand_storage_pool(storage_pool_id=storagepool_id, disk_ids=disks_ids)
        if 0 != rc:
            log.error("expand storage_pool faild!!!")
        else:
            log.info("storage_pool expand succeed!!!")
        return rc, stdout

    def get_storagepool_id(self, storage_pool_name):
        '''
        date  :      2017.07.12
        Description: 根据存储池名字获取id
        :param       storage_pool_name: 存储池名字
        :return:
        '''
        rc, stdout = get_storage_pools()
        if rc != 0:
            return rc, None
        storage_pools = json_loads(stdout)
        storage_pools = storage_pools['result']['storage_pools']
        for storage_pool in storage_pools:
            if storage_pool['name'] == storage_pool_name:
                return rc, storage_pool['id']
        return rc, None

    def get_storage_pool_freevolumebytes(self, storage_pool_id):
        '''
        date  :      2017.07.12
        Description: 根据存储池id获取卷可用的空闲空间
        :param       storage_pool_id: 存储池id
        :return:
        '''
        rc, stdout = get_storage_pools(ids=storage_pool_id)
        if rc != 0:
            return rc, 0
        storage_pools = json_loads(stdout)
        free_volume_bytes = storage_pools['result']['storage_pools'][0]['free_volume_bytes']
        return rc, free_volume_bytes

    def get_storage_pool_totalandusedbytes(self, storage_pool_id):
        '''
        date  :      2017.07.12
        Description: 根据存储池id获取总空间和使用空间
        :param       storage_pool_id: 存储池id
        :return:
        '''
        rc, stdout = get_storage_pools(ids=storage_pool_id)
        if rc != 0:
            return rc, 0, 0
        storage_pools = json_loads(stdout)
        storage_pool_totalbytes = storage_pools['result']['storage_pools'][0]['total_bytes']
        storage_pool_usedbytes = storage_pools['result']['storage_pools'][0]['used_bytes']
        return rc, storage_pool_totalbytes, storage_pool_usedbytes

    def get_all_storagepool_ids(self):
        '''
        date  :      2017.07.12
        Description: 获取所有存储池的id
        :return:
        '''
        rc, stdout = get_storage_pools()
        if rc != 0:
            return rc, None
        storage_pools = json_loads(stdout)
        storage_pools = storage_pools.get('result')
        storage_pools = storage_pools.get('storage_pools')
        storagepool_ids = [int(storage_pool.get('id')) for storage_pool in storage_pools]
        return rc, storagepool_ids

    def get_storagepool_info(self, ids=None):
        '''
        :Author:      chenjy1
        :date  :      2018.09.03
        :Description: 获取所有存储池的信息
        :return:
        '''
        rc, stdout = get_storage_pools(ids=ids)
        if rc != 0:
            return rc, stdout
        pscli_info = json_loads(stdout)
        return rc, pscli_info


class Volume():
    '''
    卷的相关操作
    '''

    def __init__(self):
        pass

    def create_volume(self, name, storage_pool_id, stripe_width, disk_parity_num, node_parity_num, replica_num,
                      total_bytes=None, dir_slice_num=None, chunk_size=None, obj_size=None, remark=None):
        """
        :Date  :                2017.07.12
        :Description:           正常创建卷
        :param volume_name:     卷名字
        :param storage_pool_id: 存储池id
        :param stripe_width:    条带宽度
        :param disk_parity_num: 磁盘冗余
        :param node_parity_num: 节点冗余
        :param replica_num:     副本数
        :param total_bytes:     卷容量
        :param dir_slice_num:   目录分片
        :param chunk_size:      chunk大小
        :param obj_size:        最大对象大小
        :return:
        """
        rc, stdout = create_volume(name=name, storage_pool_id=storage_pool_id, stripe_width=stripe_width,
                                   disk_parity_num=disk_parity_num, node_parity_num=node_parity_num,
                                   replica_num=replica_num, total_bytes=total_bytes, dir_slice_num=dir_slice_num,
                                   chunk_size=chunk_size, object_size=obj_size, remark=remark)
        if rc != 0:
            log.info("create volume faild!!!")
            return rc, {}
        else:
            json_info = json_loads(stdout)
            return rc, json_info

    def get_volume_id(self, volume_name):
        '''
        date  :      2017.07.12
        Description: 根据卷名字获取卷的id
        :param volume_name: 卷名字
        '''
        rc, stdout = get_volumes()
        judge_rc(rc, 0, "Execute command: get volumes failed. \nstdout: %s" % (stdout))
        volumes = json_loads(stdout)
        volumes = volumes['result']['volumes']
        for volume in volumes:
            if volume['name'] == volume_name:
                volumeid = volume['id']
                return volumeid
        return None

    def get_all_volumes_id(self):
        '''
        date  :      2017.07.12
        Description: 获取所有卷id
        :return:
        '''
        rc, stdout = get_volumes()
        if rc == 0:
            volumes = stdout
            volumes = json_loads(volumes)
            volumes = volumes.get('result').get('volumes')
            volume_ids = [int(volume.get('id')) for volume in volumes]
            return volume_ids
        else:
            except_exit("Execute command: get volumes failed. \nstdout: %s" % (stdout))

    def delete_volume(self, id):
        '''
        date  :      2018.05.09
        Description: 删除存储卷
        :return:
        '''
        rc, stdout = delete_volumes(ids=id)
        return rc

    def get_all_volume_layout(self, run_cluster=MASTER):
        """
        :author:      baoruobing
        :date  :      2018.08.15
        :description: 获取所有卷的配比
        :return:      (list)卷的配比信息,[{'disk_parity_num':2,'node_parity_num':1,'replica_num':4}]
        """
        rc, stdout = get_volumes(run_cluster=run_cluster)
        if rc != 0:
            return rc, []
        volumes_info = json_loads(stdout)
        volumes_lst = volumes_info['result']['volumes']
        layout_lst = []
        for volume in volumes_lst:
            layout_dic = {}
            layout_dic['disk_parity_num'] = volume['layout']['disk_parity_num']
            layout_dic['node_parity_num'] = volume['layout']['node_parity_num']
            layout_dic['replica_num'] = volume['layout']['replica_num']
            layout_lst.append(layout_dic)
        return rc, layout_lst

    def get_all_volumes(self, ids=None):
        '''
        :Author: chenjy1
        date  :      2018.09.03
        Description: 获取所有卷信息
        '''
        rc, stdout = get_volumes(ids=ids)
        if rc != 0:
            return rc, stdout
        pscli_info = json_loads(stdout)
        return rc, pscli_info

    def update_volume(self, id, total_bytes=None, remark=None):
        '''
        :Author: chenjy1
        date  :      2018.09.03
        Description: 更新卷
        '''
        rc, stdout = update_volume(id=id, total_bytes=total_bytes, remark=remark)
        if rc != 0:
            return rc, 0
        pscli_info = json_loads(stdout)
        return rc, pscli_info

    def get_volumeinfo_by_id(self, id):
        '''
        :Author: chenjy1
        date  :      2018.09.03
        Description: 获取特定id卷的信息
        '''
        rc, stdout = get_volumes(ids=id)
        if rc != 0:
            return rc, 0
        pscli_info = json_loads(stdout)
        return rc, pscli_info

    def ready_to_del_volume(self, name):
        '''
        :Author: chenjy1
        date  :      2018.09.03
        Description: 删除卷前的准备工作，（删除文件，配额、快照等）
        '''
        rc, stdout = get_quota(param_name='path', param_value='%s:/' % name, print_flag=True)
        if rc != 0:
            return rc, stdout
        json_info = json_loads(stdout)
        for quota in json_info['result']['quotas']:
            rc, stdout = delete_quota(quota['id'])
            if rc != 0:
                return rc, stdout
        rc, stdout = get_snapshot(param_name='path', param_value='%s:/' % name, print_flag=True)
        if rc != 0:
            return rc, stdout
        json_info = json_loads(stdout)
        for snap in json_info['result']['snapshots']:
            rc, stdout = delete_snapshot(snap['id'])
            if rc != 0:
                return rc, stdout
        rc, stdout = get_snapshot_strategy(param_name='path', param_value='%s:/' % name, print_flag=True)
        if rc != 0:
            return rc, stdout
        json_info = json_loads(stdout)
        for snapshot_strategy in json_info['result']['snapshot_strategies']:
            rc, stdout = delete_snapshot_strategy(snapshot_strategy['id'])
            if rc != 0:
                return rc, stdout
        rc, stdout = rm_exe(SYSTEM_IP, '/mnt/%s/*' % name)
        if rc != 0:
            return rc, stdout
        return 0, ''


class Clientauth():
    '''
    客户端授权相关操作
    '''

    def __init__(self):
        pass

    def create_client_auth(self, ip, volume_ids, auto_mount=None, atime=None,
                           acl=None, user_xattr=None, sync=None, desc=None):
        '''
        date  :            2017.07.12
        Description:       正常配置客户端授权
        :param ip:         需要授权的客户端的ip
        :param volume_ids: volume_ids需要挂载的卷的id
        :return:
        '''
        rc, stdout = create_client_auth(ip=ip, volume_ids=volume_ids, auto_mount=auto_mount, atime=atime, acl=acl,
                                        user_xattr=user_xattr, sync=sync, desc=desc)
        return rc, stdout

    def update_client_auth(self, client_auth_id, ip, volume_ids, auto_mount=None, atime=None,
                           acl=None, user_xattr=None, sync=None, desc=None):
        '''
        date  :                2017.07.12
        Description:           更新客户端授权
        :param client_auth_id: 客户端授权的id
        :param ip:             客户端授权的id
        :param volume_ids:     volume_ids需要挂载的卷的id
        :return:
        '''
        rc, stdout = update_client_auth(client_auth_id=client_auth_id, ip=ip, volume_ids=volume_ids,
                                        auto_mount=auto_mount, atime=atime, acl=acl, user_xattr=user_xattr, sync=sync,
                                        desc=desc)
        if 0 != rc:
            log.warn("Update client_auth failed!!!")
        return rc

    def get_client_auth_id(self, ip, volume_ids, print_flag=True):
        '''
        date  :      2017.07.12
        Description: 获取客户端授权
        :param ip:   客户端授权的ip
        :param volume_ids: 客户端授权卷的id(列表)
        :return:
        '''
        rc, stdout = get_client_auth(print_flag=print_flag)
        judge_rc(rc, 0, "Execute command: get client auth failed. \nstdout: %s" % (stdout))
        client_auths = json_loads(stdout)
        client_auths = client_auths['result']
        for client_auth in client_auths:
            if client_auth['ip'] == ip and client_auth['volume_ids'] == volume_ids:
                clientauthid = client_auth['id']
                return clientauthid
        return None

    def get_all_client_auth_ids(self, volume_id):
        '''
        author: liyao
        date: 2018.08.07
        description: 获取一个存储卷上的所有客户端授权
        :param volume_id: 特定存储卷id
        :return: 上述存储卷上添加的所有客户端授权
        '''
        rc, stdout = get_client_auth()
        if 0 != rc:
            log.error("Execute command: get client auth failed!!!")
        stdout = json_loads(stdout)
        client_auth_info = stdout['result']
        client_auth_ids = []
        for client_auth in client_auth_info:
            if volume_id in client_auth['volume_ids']:
                client_auth_ids.append(client_auth['id'])
        return rc, client_auth_ids

    def delete_client_auth(self, client_auth_id):
        '''
        date  :      2018.05.07
        Description: 删除客户端授权
        :param client_auth_id: 客户端授权的id
        :return:
        '''
        rc, stdout = delete_client_auth(ids=client_auth_id)
        if 0 != rc:
            log.warn("Delete client_auth faild!!!")
        return rc

    def get_all_clientip_str(self, ip_lst):
        """
        auth:chenjy1
        description:以x.x.x.x , x.x.x.x ,x.x.x.x格式返回客户端ip
        :return:
        """
        ip_str = ','.join(str(i) for i in ip_lst)
        return ip_str


class Client():
    '''
    客户端操作
    '''

    def __init__(self):
        pass

    def _command(self, ip, cmd):
        rc, stdout = run_command(ip, cmd)
        if rc != 0:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        return stdout

    def insmod_client(self, node_ip):
        '''
        date  :      2017.07.12
        Description: 集群内部加载客户端内核
        :param node_ip:
        :return:
        '''
        insmod_cmd = "/home/parastor/tools/client/p300_insmod.sh"
        log.info(insmod_cmd)
        self._command(node_ip, insmod_cmd)
        return

    def rmmod_client(self, node_ip):
        '''
        date  :      2017.07.12
        Description: 集群内部卸载客户端内核
        :param node_ip:
        :return:
        '''
        rmmod_cmd = ("/home/parastor/tools/client/p300_rmmod.sh")
        log.info(rmmod_cmd)
        self._command(node_ip, rmmod_cmd)

    def mount_client(self, client_ip, mount_path, volume_name):
        '''
        date  :      2017.07.12
        Description: 进行mount操作
        :param client_ip: 客户端节点ip
        :param mount_path: 挂载的路径
        :param volume_name: 卷的名字
        :return:
        '''
        '''检查mount路径是否存在'''
        if not check_file_exist(client_ip, mount_path):
            cmd = ("mkdir %s" % mount_path)
            log.info(cmd)
            self._command(client_ip, cmd)

        sys_name = get_sysname()
        mount_cmd = "mount -t parastor nodev %s -o sysname=%s -o fsname=%s" % (mount_path, sys_name, volume_name)
        log.info(mount_cmd)
        self._command(client_ip, mount_cmd)
        return

    def umount_client(self, client_ip, mount_path):
        '''
        date  :      2017.07.12
        Description: 取消客户端挂载，进行umount操作
        :param client_ip: 客户端节点ip
        :param mount_path: 挂载的路径
        :return:
        '''
        cmd = ("umount %s" % mount_path)
        log.info(cmd)
        self._command(client_ip, cmd)
        return

    def get_client_eth_by_ip(self, clientip, ip_for_eth):
        """
        author:chenjy1
        date:20181201
        description:获取特定ip的网卡名
        :param clientip: 客户端管理ip
        :param ip_for_eth:
        :return:
        """
        cmd = 'ip addr | grep %s | grep inet' % ip_for_eth
        rc, stdout = run_command(clientip, cmd)
        if rc != 0:
            return rc, ''
        eth_name = stdout.split()[-1]
        return rc, eth_name


class Disk():
    '''
    硬盘及硬盘池相关操作
    '''

    def __init__(self):
        pass

    def add_disks(self, node_ids, uuid, usage):
        '''
        date  :      2017.07.12
        Description: 添加硬盘
        :param node_ids: 节点id
        :param uuid: 硬盘的uuid
        :param usage: (FREE,CACHE,JOURNAL)
        :return:
        '''
        rc, stdout = get_disks(node_ids, print_flag=False)
        judge_rc(rc, 0, 'get_disks failed')
        json_info = json_loads(stdout)
        devname = ''
        same_devname_cnt = 0
        for disk in json_info['result']['disks']:
            if disk['uuid'] == uuid:
                devname = disk['devname']
        for disk in json_info['result']['disks']:
            if disk['devname'] == devname:
                same_devname_cnt += 1
        if same_devname_cnt > 1:
            except_exit('more than 1 devname in node:%s devname is %s' % (node_ids, devname))
        rc, stdout = add_disks(node_ids=node_ids, disk_uuids=uuid, usage=usage)
        return rc, stdout

    def get_disk_info(self, node_ids, run_cluster=MASTER):
        '''
        date  :      2017.07.12
        Description: 获取节点内的所有硬盘信息
        :param node_ids: 节点id
        :return:
        '''
        rc, stdout = get_disks(node_ids=node_ids, run_cluster=run_cluster)
        return rc, stdout

    def get_all_disks_id_and_bytes(self, node_ids):
        '''
        date  :      2017.07.12
        Description: 获取节点内的所有硬盘id
        :param node_ids: 节点id
        :return:
        '''
        rc, stdout = self.get_disk_info(node_ids)
        judge_rc(rc, 0, 'get disk failed!!!')
        disks = json_loads(stdout)
        disks = disks['result']['disks']
        disk_ids = []
        disks_totabytes = 0
        disks_usedbytes = 0
        for disk in disks:
            if (disk['id'] != 0) and (disk['is_system'] != 'true'):
                disk_ids.append(disk['id'])
                disks_totabytes = disks_totabytes + (disk['total_bytes'])
                disks_usedbytes = disks_usedbytes + (disk['used_bytes'])
                # log.info('id=%s total_bytes=%s used_bytes=%s' % (disk['id'], disk['total_bytes'], disk['used_bytes']))

        # log.info('all disks Total_bytes=%s, UsedBytes=%s' % (disks_TotaBytes, disks_UsedBytes))
        return disk_ids, disks_totabytes, disks_totabytes

    def get_disks_uuids(self, node_ids):
        '''
        date  :      2017.07.12
        Description: 获取节点内所有非系统盘的uuid
        :param node_ids: 节点id
        :return:
        '''
        rc, stdout = self.get_disk_info(node_ids)
        judge_rc(rc, 0, 'get disk failed!!!')
        disks = json_loads(stdout)
        disks = disks['result']['disks']
        disk_uuids = []
        for disk in disks:
            if (disk['is_system'] is not True) and (disk['usedState'] == 'IN_USE'):
                disk_uuids.append(disk['uuid'])
        return disk_uuids

    def get_diskid_by_name(self, node_id, disk_name):
        '''
        date  :      2017.07.12
        Description: 根据磁盘名字获取磁盘id
        :param node_id: 节点id
        :param disk_name: 磁盘名字
        :return: 磁盘id
        '''
        rc, stdout = self.get_disk_info(node_id)
        judge_rc(rc, 0, 'get disk failed!!!')
        result = json_loads(stdout)
        disk_list = result['result']['disks']
        for disk in disk_list:
            if disk['devname'] == disk_name:
                return disk['id']
        return None

    def get_disk_name_by_id(self, node_id, disk_id):
        """通过磁盘id获取磁盘名字"""
        rc, stdout = self.get_disk_info(node_id)
        judge_rc(rc, 0, 'get disk failed!!!')
        result = json_loads(stdout)
        disk_list = result['result']['disks']
        for disk in disk_list:
            if disk['id'] == int(disk_id):
                return disk['devname']
        return None

    def get_disk_uuid_by_name(self, node_id, disk_name):
        '''
        date  :      2017.07.12
        description: 获取某个节点的某个磁盘的uuid
        :param node_id: 节点id
        :param disk_name: 硬盘名字
        :return: 磁盘uuid
        '''
        rc, stdout = self.get_disk_info(node_id)
        judge_rc(rc, 0, 'get disk failed!!!')
        result = json_loads(stdout)
        disk_list = result['result']['disks']
        for disk in disk_list:
            if disk['devname'] == disk_name:
                return disk['uuid']
        return None

    def get_disk_usage_by_name(self, node_id, disk_name):
        '''
        date  :      2017.07.12
        description: 获取某个节点的某个磁盘的uuid
        :param node_id: 节点id
        :param disk_name: 硬盘名字
        :return: 磁盘用途
        '''
        rc, stdout = self.get_disk_info(node_id)
        judge_rc(rc, 0, 'get disk failed!!!')
        result = json_loads(stdout)
        disk_list = result['result']['disks']
        for disk in disk_list:
            if disk['devname'] == disk_name:
                return disk['usage']
        return None

    def get_disk_id_by_uuid(self, node_id, disk_uuid):
        '''
        date  :      2017.07.12
        description: 通过uuid获取磁盘的id
        :param node_id: 节点id
        :param disk_uuid: 磁盘uuid
        :return: 磁盘id
        '''
        rc, stdout = self.get_disk_info(node_id)
        judge_rc(rc, 0, 'get disk failed!!!')
        result = json_loads(stdout)
        disk_list = result['result']['disks']
        for disk in disk_list:
            if disk['uuid'] == disk_uuid:
                return disk['id']
        return None

    def get_disk_state_by_id(self, node_id, disk_id):
        """
        date  :         2018.07.6
        description:    通过id获取磁盘的状态
        :param node_id: 节点id
        :param disk_id: 磁盘id
        :return:
        """
        rc, stdout = self.get_disk_info(node_id)
        judge_rc(rc, 0, 'get disk failed!!!')
        result = json_loads(stdout)
        disk_list = result['result']['disks']
        for disk in disk_list:
            if disk['id'] == int(disk_id):
                return disk['state']
        return None

    def remove_disks(self, disk_ids):
        '''
        date  :      2017.07.12
        Description: 删除硬盘(同步)
        :param disk_ids: 硬盘id
        :return:
        '''

        rc, stdout = remove_disks(disk_ids=disk_ids)
        return rc, stdout

    def remove_disks_asyn(self, disk_ids):
        '''
        date  :      2017.07.12
        Description: 删除硬盘(异步)
        :param disk_ids: 硬盘id
        :return:
        '''
        rc, stdout = remove_disks(disk_ids=disk_ids, auto_query='false')
        return rc, stdout

    def cancel_delete_disk(self, disk_id):
        rc, stdout = cancel_remove_disks(disk_ids=disk_id)
        return rc, stdout

    def get_diskpool_ids(self):
        '''
        date  :      2017.07.12
        Description: 删除硬盘
        :return:
        '''
        cmd = ("/root/zk/bin/zkCli.sh get /parastor0/conf/DISK_POOLS/0")
        rc, stdout = pscli_run_command(cmd)
        list_stdout = stdout.split('\n')
        share_diskpool_ids = []
        monopoly_diskpool_ids = []
        for mem in list_stdout:
            if 'DISK_POOL_TYPE_MONOPOLY' in mem:
                mem_list = mem.split()
                monopoly_diskpool_ids.append(mem_list[1].split('"')[1])
            elif 'DISK_POOL_TYPE_SHARE' in mem:
                mem_list = mem.split()
                share_diskpool_ids.append(mem_list[1].split('"')[1])
        return share_diskpool_ids, monopoly_diskpool_ids

    def get_share_monopoly_disk_names(self, node_id, run_cluster=MASTER):
        '''
        date  :      2017.07.12
        Description: 获取某个节点的所有共享硬盘和数据硬盘的名字
        :param node_id: 节点id
        :return: share_disk_names:共享盘名字
                 monopoly_disk_names:数据盘名字
        '''
        rc, stdout = self.get_disk_info(node_id, run_cluster=run_cluster)
        judge_rc(rc, 0, 'get disk failed!!!')
        msg = json_loads(stdout)
        share_disk_names = []
        monopoly_disk_names = []
        disks_pool = msg['result']['disks']
        for disk in disks_pool:
            if disk['usage'] == 'SHARED' and disk['state'] == 'DISK_STATE_HEALTHY' and disk['usedState'] != "UNUSED":
                share_disk_names.append(disk['devname'])
            elif disk['usage'] == 'DATA' and disk['state'] == 'DISK_STATE_HEALTHY' and disk['usedState'] != "UNUSED":
                monopoly_disk_names.append(disk['devname'])
        return share_disk_names, monopoly_disk_names


    def get_physicalid_by_name(self, node_ip, disk_name):
        '''
        date  :      2017.07.12
        Description: 获取某个节点的所有共享硬盘和数据硬盘的名字
        :param node_ip: 节点ip
        :param disk_name: 硬盘名字
        :return:
        '''
        cmd = "lsscsi"
        log.info(cmd)
        rc, stdout = run_command(node_ip, cmd)
        log.info(stdout)
        judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        list_stdout = stdout.split('\n')
        for mem in list_stdout:
            if disk_name in mem:
                list_mem = mem.split()
                id = list_mem[0]
                id = id[1:-1]
                return id
        raise Exception("get node %s disk %s lsscsi id failed!!!" % (node_ip, disk_name))

    def get_share_monopoly_disk_physicalid(self, node_id, run_cluster=MASTER):
        '''
                date  :      2019.03.19
                Description: 获取某个节点的所有共享硬盘和数据硬盘的scsi id(例如 0 0 3 0)
                :param node_ip: 节点ip
                :return:两个list，第一个是所有共享盘的在用scsi id list，第二个是数据盘的
                '''
        share_disk_names, monopoly_disk_names = self.get_share_monopoly_disk_names(node_id)
        share_disk_scsi_ids = []
        monopoly_disk_scsi_id = []
        node = Node()
        node_ip = node.get_node_ip_by_id(node_id)
        for share_disk_name in share_disk_names:
            log.info('share_disk_name is %s' %share_disk_name )
            id = self.get_physicalid_by_name(node_ip, share_disk_name)
            share_disk_scsi_ids.append(id)
        for monopoly_disk_name in monopoly_disk_names:
            id = self.get_physicalid_by_name(node_ip, monopoly_disk_name)
            monopoly_disk_scsi_id.append(id)
        return share_disk_scsi_ids, monopoly_disk_scsi_id



    def get_storage_pool_id_by_diskid(self, node_id, disk_id):
        '''
        date  :      2017.07.12
        Description: 获取磁盘所在的存储池的id
        :param       node_id:节点id
        :param       disk_id:磁盘id
        :return:
        '''
        rc, stdout = self.get_disk_info(node_id)
        judge_rc(rc, 0, 'get disk failed!!!')
        msg = json_loads(stdout)
        disks_info = msg['result']['disks']
        for disk in disks_info:
            if disk['id'] == disk_id:
                return disk['storagePoolId']
        return None

    def check_disk_exist(self, node_id, disk_id):
        '''
        date  :      2017.07.12
        Description: 检查磁盘是否存在
        :param       disk_id:节点id
        :return:     True or False
        '''
        rc, stdout = self.get_disk_info(node_id)
        judge_rc(rc, 0, 'get disk failed!!!')
        msg = json_loads(stdout)
        disk_info = msg['result']['disks']
        for disk in disk_info:
            if disk['id'] == disk_id:
                return True
        return False

    def change_disk_speed_level(self, disk_ids, speed_level):
        """
        auth:                  chenjy1
        date:                  20181106
        :param disk_ids:      disk_ids
        :param speed_level:   speed_level
        :return:              rc, stdout
        """
        rc, stdout = change_disk_speed_level(disk_ids=disk_ids, speed_level=speed_level)
        return rc, stdout

    def change_disk_speed_level_map(self, speed_type, speed_level):
        """
        auth:                  chenjy1
        date:                  20181106
        :param speed_type:
        :param speed_level:
        :return:
        """
        rc, stdout = change_disk_speed_level_map(speed_type=speed_type, speed_level=speed_level)
        return rc, stdout


class NWatch():
    '''nWatch相关查询'''

    def _command(self, cmd):
        rc, stdout = pscli_run_command(cmd)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        return stdout

    def get_lmos_node_id(self):
        '''
        date  :      2017.07.12
        Description: 根据节点ip获取节点的id
        :return:     逻辑mos节点id
        '''
        orole_nodes_id_lst = Node().get_orole_node_ids()
        for node_id in orole_nodes_id_lst:
            cmd = "/home/parastor/tools/nWatch -t oRole -i %s -c oRole#rolemgr_view_dump" % node_id
            rc, stdout = pscli_run_command(cmd, print_flag=False)
            if 0 != rc or 'failed' in stdout.splitlines()[0]:
                log.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
                continue
            else:
                break
        else:
            return None
        result_lst = stdout.split('\n')
        for line in result_lst:
            if 'node_sn: 0' in line:
                mem_lst = line.split(',')
                for mem in mem_lst:
                    if 'node_id' in mem:
                        return mem[-1]
        log.warn("There is not mos node!!!")
        return None


def mkdir_path(node_ip, path, run_cluster=MASTER):
    """
    :author:         baoruobing
    :date  :         2018.04.17
    :Description:    在节点node_ip上创建目录path
    :param node_ip:  节点ip
    :param path:     要创建的目录
    :return:
    """
    cmd = 'ls %s' % path
    rc, stdout = run_command_shot_time(cmd, node_ip, print_flag=False)
    if 0 == rc:
        return
    cmd = 'mkdir -p %s' % path
    rc, stdout = run_command_shot_time(cmd, node_ip, print_flag=False)
    if rc != 0:
        raise Exception('%s mkdir faild!!!' % path)
    return


##############################################################################
# ##name  :      check_file_exist
# ##parameter:   ip:节点ip, path:路径, file:文件名
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 检查某个路径下是否有某个文件或者文件夹
##############################################################################
def check_file_exist(ip, filename):
    cmd = "ls %s" % filename
    rc, stdout = run_command_shot_time(cmd, ip, print_flag=False)
    if rc == 0:
        return True
    else:
        return False


##############################################################################
# ##name  :      get_sysname
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 获取存储集群名字
##############################################################################
def get_sysname():
    '''获取系统名字'''
    rc, stdout = get_cluster_overview()
    judge_rc(rc, 0, "Execute command: get_cluster_overview failed. \nstdout: %s" % (stdout))
    msg = json_loads(stdout)
    sys_name = msg['result']['name']
    return sys_name


##############################################################################
# ##name  :      get_param
# ##parameter:   section:参数所属的模块, name:参数名字
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 获取param的当前值
##############################################################################
def get_param_current(section, name):
    rc, stdout = get_params(section=section, name=name)
    judge_rc(rc, 0, "get params failed\nstdout: %s" % stdout)
    msg_json = json_loads(stdout)
    value = msg_json['result']['parameters'][0]['current']
    return value


##############################################################################
# ##name  :      get_param_default
# ##parameter:   section:参数所属的模块, name:参数名字
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 获取param的默认值
##############################################################################
def get_param_default(section, name):
    rc, stdout = get_params(section=section, name=name)
    judge_rc(rc, 0, "get params failed\nstdout: %s" % stdout)
    msg_json = json_loads(stdout)
    default_value = msg_json['result']['parameters'][0]['default']
    return default_value


"""****************************** 环境检查 ******************************"""


##############################################################################
# ##name  :      check_job_repair
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 检查修复任务是否存在
##############################################################################
def check_job_repair():
    rc, stdout = get_jobengine_state()
    judge_rc(rc, 0, "get jobengine state failed.\nstdout: %s" % stdout)
    msg_json = json_loads(stdout)
    jobs = msg_json['result']['job_engines']
    for job in jobs:
        if job['type'] == 'JOB_ENGINE_REPAIR':
            return True
    return False


##############################################################################
# ##name  :      check_rebuild_job
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 检查重建任务是否存在
##############################################################################
def check_rebuild_job(fault_node_ip=None):
    rc, stdout = get_jobengine_state(fault_node_ip=fault_node_ip)
    judge_rc(rc, 0, "get jobengine state failed.\nstdout: %s" % stdout)
    msg_json = json_loads(stdout)
    jobs = msg_json['result']['job_engines']
    for job in jobs:
        if job['type'] == 'JOB_ENGINE_REBUILD':
            return True
    return False


##############################################################################
# ##name  :      check_badjobnr
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 检查系统是否有坏对象
##############################################################################
def check_badjobnr():
    '''获取集群中所有节点的id'''
    ob_node_info = Node()
    nodes_id = ob_node_info.get_nodes_id()
    cmd = '/home/parastor/tools/nWatch -t oJob -i %d -c RCVR#jobinfo' % nodes_id[0]
    rc, stdout = pscli_run_command(cmd, print_flag=False)
    if 0 != rc:
        log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        # raise Exception("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
        return False
    else:
        node_id = stdout.split(',')[0].split()[-1]
        cmd1 = "/home/parastor/tools/nWatch -t oJob -i %s -c RCVR#repairjob" % node_id
        rc, stdout = pscli_run_command(cmd1)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd1, stdout))
            # raise Exception("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd1, stdout, stderr))
            return False
        else:
            log.info(stdout)
            result = stdout.split('\n')
            for mem in result:
                if 'badobjnr' in mem:
                    mem_temp = mem.split()
                    if mem_temp[1] != '0':
                        log.info("badobj %s" % mem_temp[1])
                        return False
    return True


def check_vset():
    """
    :author:      baoruobing
    :return:
    :date  :      2018.06.06
    :description: 检查环境中vset是否展平
    """
    """获取集群中的所有节点"""
    ob_node_info = Node()
    orole_nodes_id_lst = ob_node_info.get_orole_node_ids()

    """获取lnodeid"""
    for node_id in orole_nodes_id_lst:
        cmd = '/home/parastor/tools/nWatch -i %d -t oRole -c oRole#rolemgr_view_dump' % node_id
        rc, stdout = pscli_run_command(cmd, print_flag=False)
        if 0 != rc or 'failed' in stdout.splitlines()[0]:
            log.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            continue
        else:
            break
    else:
        return False

    stdout_lst = stdout.strip().splitlines()
    index = None
    for line in stdout_lst:
        if 'jtype:1 info' in line:
            index = stdout_lst.index(line)
            break
    if index is None:
        log.warn("get mgrid failed!!!")
        return False
    stdout_lst1 = stdout_lst[index + 1:]

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
        log.warn("get mgrid failed!!!")
        return False
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

    """检查vset是否没有展平"""
    for lnode_dic in node_lnode_lst:
        node_id = lnode_dic['node_id']
        lnode_lst = lnode_dic['lnode_id']
        for lnode_id in lnode_lst:
            cmd = '/home/parastor/tools/nWatch -i %s -t oPara -c oPara#vmgr_flattennr_dump -a "vmgrid=%s"' \
                  % (node_id, lnode_id)
            rc, stdout = pscli_run_command(cmd)
            if (0 != rc) or ('failed' in stdout) or ('support' in stdout):
                log.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
                return False
            vset_num = stdout.strip().split('\n')[-1].split()[2]
            try:
                if int(vset_num) != 0:
                    return False
                else:
                    log.info("The current environment all vset is flatten")
                    continue
            except Exception, e:
                log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
                raise Exception("Error msg is %s" % e)
    return True


def check_ds():
    """
    :author:      baoruobing
    :return:
    :date  :      2018.06.06
    :description: 检查环境中ds是否正常
    """
    """获取集群中的所有节点"""
    ob_node_info = Node()
    nodes_id_lst = ob_node_info.get_nodes_id()
    for node_id in nodes_id_lst:
        cmd = '/home/parastor/tools/nWatch -i %d -t oStor -c oStor#get_basicinfo' % node_id
        rc, stdout = pscli_run_command(cmd)
        if 0 != rc or 'failed' in stdout.splitlines()[0]:
            log.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            return False
        else:
            stdout_lst = stdout.split('\n')
            for line in stdout_lst:
                if 'provide serv' in line:
                    flag = line.split(':')[-1].strip()
                    try:
                        if 1 != int(flag):
                            log.warn("node %d ds don't provide service" % node_id)
                            return False
                    except Exception as e:
                        log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
                        raise Exception("Error msg is %s" % e)

    return True


def check_jnl():
    """
    :author:      baoruobing
    :return:
    :date  :      2018.06.06
    :description: 检查环境中jnl是否正常
    """
    """获取集群中的所有节点"""
    ob_node_info = Node()
    orole_nodes_id_lst = ob_node_info.get_orole_node_ids()
    for node_id in orole_nodes_id_lst:
        cmd = '/home/parastor/tools/nWatch -t oRole -i %s -c oRole#rolemgr_master_dump' % node_id
        rc, stdout = pscli_run_command(cmd)
        if 0 != rc or 'failed' in stdout.splitlines()[0]:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            continue
        else:
            break
    else:
        return False
    master_node_id = stdout.split(':')[-1].strip()
    cmd1 = '/home/parastor/tools/nWatch -t oRole -i %s -c oRole#rolemgr_slaveready_dump' % master_node_id
    rc, stdout = pscli_run_command(cmd1)
    if 0 != rc or 'failed' in stdout.splitlines()[0]:
        log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd1, stdout))
        return False
    stdout_lst = stdout.split('\n')
    for node_id in orole_nodes_id_lst:
        for line in stdout_lst:
            if 'nodeid' in line and 'is_takeoverable' in line:
                node_id_tmp = line.split()[-2].split(':')[-1].rstrip(',')
                takeoverable = line.split()[-1].split(':')[-1].strip()
                if node_id_tmp != str(node_id):
                    continue
                if takeoverable != '1':
                    log.warn("node %d jnl is not OK!!!" % node_id)
                    return False
    return True


def check_alldisks_health():
    """
    :author:      baoruobing
    :date  :      2018.06.06
    :description: 检查环境中所有磁盘的状态是否是health
    :return:
    """
    """获取集群所有节点id"""
    ob_node_info = Node()
    nodes_id_lst = ob_node_info.get_nodes_id()

    """获取所有磁盘id"""
    ob_disk = Disk()
    for node_id in nodes_id_lst:
        rc, stdout = ob_disk.get_disk_info(node_id)
        judge_rc(rc, 0, 'get disk failed!!!')
        disks_info = json_loads(stdout)
        for disk_info in disks_info['result']['disks']:
            if disk_info['usedState'] != 'IN_USE' or disk_info['usage'] == 'SYSTEM':
                continue
            if disk_info['state'] != 'DISK_STATE_HEALTHY':
                log.warn("disk %s is %s" % (str(disk_info['id']), disk_info['state']))
                return False
    return True


def check_service_state(fault_node_ip=None):
    """
    :author:      baoruobing
    :date  :      2018.06.06
    :description: 检查环境中所有服务的状态是否正常
    :return:
    """
    rc, stdout = get_services(fault_node_ip=fault_node_ip)
    if rc != 0:
        return False
    services_info = json_loads(stdout)
    service_lst = services_info['result']['nodes']
    for service_node in service_lst:
        service_node_lst = service_node['services']
        for service in service_node_lst:
            if service['service_type'] in ['oJmgs', 'oRole', 'oPara', 'oMgcd', 'oJob', 'oStor']:
                if service['inTimeStatus'] != 'SERV_STATE_OK' and service['inTimeStatus'] != 'SERV_STATE_READY':
                    log.warn("node %s: %s's status is %s" %
                             (service['node_id'], service['service_type'], service['inTimeStatus']))
                    return False
    return True


def get_san_state(s_ip=None):
    """
    :Auther: Liu he
    :Description: 获取san状态(默认第一个访问区)
    :return: 开启返回True 未开启返回False
    """
    param_list = [s_ip]
    if all(param_list):
        cmd = ("ssh %s \"pscli --command=get_access_zones\"" % (s_ip))
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        if rc != 0:
            log.error("get cmd failed,Error infor:%s" % (stdout))
            os._exit(1)
        else:
            status_san = []
            stdout = json.loads(stdout)
            chk_san = stdout["result"]["access_zones"]
            if chk_san:
                for i in range(len(chk_san)):
                    san_state = stdout["result"]["access_zones"][i]["enable_san"]
                    status_san.append(san_state)
                return status_san
            else:
                return
    else:
        log.error("param is None error :s_ip :%s " % (s_ip))
        os._exit(1)


def check_x1000_service_state():
    """
    :author:      wuyuqiao
    :date  :      2018.08.30
    :description: 检查x1000环境中所有服务的状态是否正常
    :return:
    """
    log.info("check system services after 2 minute...")
    time.sleep(120)
    rc, stdout = get_services()
    if rc != 0:
        os._exit(1)
    services_info = json_loads(stdout)
    service_lst = services_info['result']['nodes']
    san_status = get_san_state(deploy_ips[0])
    for service_node in service_lst:
        service_node_lst = service_node['services']
        for service in service_node_lst:
            if service['service_type'] == 'oSan':
                if False in san_status:
                    break
            if service['service_type'] == 'oApp':
                break
            elif service['service_type'] == 'oRole':
                if service['inTimeStatus'] != 'SERV_STATE_OK' and service['inTimeStatus'] != 'SERV_STATE_READY':
                    log.error("node %s: %s's status is %s" %
                              (service['node_id'], service['service_type'], service['inTimeStatus']))
                    os._exit(1)
            elif service['inTimeStatus'] != 'SERV_STATE_OK':
                log.error("node %s: %s's status is %s" %
                          (service['node_id'], service['service_type'], service['inTimeStatus']))
                os._exit(1)
            log.info("node_id:%s,services---%s is %s" %
                     (service['node_id'], service['service_type'], service['inTimeStatus']))
    return True


##############################################################################
# ##name  :      ckeck_system
# ##parameter:   sys_state:期望的系统状态
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 检查系统是否有异常
##############################################################################
def ckeck_system(sys_state='RUNNING'):
    log.info('check system begin')

    # 检查坏对象（待补充）
    return


class CheckEnv(object):
    """
    #-----------------------------
    #检查IP是否能连通
    1. check_ip                 #检查IP
    2. execute_cmd              #执行shell命令，并检查返回值。返回值为执行命令的返回值
    """

    def __init__(self):
        pass

    def check_ip(self, ip):
        """
            |
        """
        cmd = "ping -c 2 %s" % (ip)
        (res, output) = commands.getstatusoutput(cmd)
        while res != 0:
            log.error("Can not attach %s,please check it." % (ip))
            time.sleep(30)
            cmd = "ping -c 2 %s" % (ip)
            (res, output) = commands.getstatusoutput(cmd)
        else:
            log.info("The ip : %s is ok." % (ip))

    def execute_cmd(self, cmd):
        """
            |
        """
        (res, output) = commands.getstatusoutput(cmd)
        if res != 0:
            log.error("Execute %s failed,the output is: %s." % (cmd, output))
        else:
            log.info("Execute %s success." % (cmd))
        return res


def rm_exe(node_ip, dir, run_cluster=MASTER):
    """
    common.py-NULL-rm_exe:——该方法不在类中
    作用：删除目录或者文件，排除执行风险
    作者： liyao
    修改时间：2018.04.19
    参数含义：node_ip:命令执行节点ip
            　dir:期望删除目录
    示例：rm_execution(10.2.41.131,/mnt/liyao/snap/snap_13_1_2_1)

    """
    if dir == '' or re.match('[/\*]*$', dir) is not None:
        log.warn('-----There is a dangerous command!!!-----')
        return -1, None
    else:
        cmd = 'rm -rf %s' % dir
        rc, stdout = run_command(node_ip, cmd)
        return rc, stdout


def get_special_character(num):
    '''
    author:      yangwm
    date  :      2019.01.28
    Description: 生成特殊字符字符串
    return:      以字符串形式返回特殊字符，例:.){-_=#-
    '''
    if (isinstance(num, int) and num > 0):
        result = []
        character_storehouse = ['`', '~', '!', '@', '#', '$', '%', '^', '(', ')', '_', '-', '+', '=', ' ', '[',
                                '{', ']', '}', ',', '.', ';']
        while num > 0:
            temple = random.choice(character_storehouse)
            result.append(temple)
            num -= 1
        temple1 = ''.join(result)
        return temple1
    elif re.search(r'[a-zA-Z]', num):
        log.info('Include Letter,Please input integer!')
    else:
        log.info('Please input integer!')


def get_corefile_info():
    '''
    author:      baoruobing
    date  :      2018.04.17
    Description: 获取集群中的core文件信息
    return:      以字典的形式返回core信息，例:{'10.2.41.101':['core.12353']}
    '''
    core_file_info = {}
    node_ip_lst = get_config.get_allparastor_ips()
    client_ip_lst = get_config.get_allclient_ip()
    all_node_ip_lst = node_ip_lst + client_ip_lst
    for node_ip in all_node_ip_lst:
        core_lst1 = []
        core_lst2 = []
        cmd = 'ls /home/parastor/log/core.* 2> /dev/null'
        rc, stdout = run_command_shot_time(cmd, node_ip=node_ip, print_flag=False)
        if rc == 0:
            core_lst1 = stdout.split()
        cmd = 'ls /core.* 2> /dev/null'
        rc, stdout = run_command_shot_time(cmd, node_ip=node_ip, print_flag=False)
        if rc == 0:
            core_lst2 = stdout.split()
        core_lst = core_lst1 + core_lst2
        if core_lst:
            core_file_info[node_ip] = core_lst
    return core_file_info


def cmd_with_timeout(command, timeout=60):
    """
    :author:              chenjinyu
    :date  :              2018.07.27
    :description:         执行某个命令，如超时，则return '', ''
    :param command:      要执行的命令
    :param timeout=60:   超时时间
    :return:             如超时，则return -1, '', ''
                          没超时，则返回0, stdout, stderr
    """
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    poll_seconds = 1
    deadline = time.time() + timeout
    while time.time() < deadline and proc.poll() is None:
        time.sleep(poll_seconds)
    if proc.poll() is None:
        proc.kill()
        return -1, '', ''
    stdout, stderr = proc.communicate()
    return 0, stdout, stderr


def check_client_state_by_list(ip_list, volume_name, timeout=300):
    """
    :author:              chenjinyu
    :date  :              2018.07.27
    :description:         检查客户端是否卡住，是否掉了
    :param ip_list:      要检查的节点
    :param volume_name:  要检查的挂载卷名
    :return:             0:正常
                          -1:ssh 失败，需要检查节点
                          -2:客户端卡住
                          -3:挂载的卷丢失
    """
    for ip in ip_list:
        rc, stdout = run_command(ip, 'pwd')
        if rc != 0:
            log.info("IP:%s ssh failed. \nstdout: %s" % (ip, stdout))
            return -1
        cmd = 'ssh %s df' % ip
        rc, stdout, stderr = cmd_with_timeout(cmd, timeout)
        if rc:
            log.info('IP:%s df : client is blockup!!! \nstdout: %s \nstderr: %s' % (ip, stdout, stderr))
            return -2
        if rc == 0 and (volume_name not in stdout):
            log.info('IP:%s df : not found volume !!!  \nstdout: %s \nstderr: %s' % (ip, stdout, stderr))
            return -3
    return 0


def check_client_state(ip, volume_name, timeout=300):
    """
    :author:              chenjinyu
    :date  :              2018.07.27
    :description:         检查客户端是否卡住，是否掉了
    :param ip:            要检查的节点
    :param volume_name:   要检查的挂载卷名
    :return:              0:正常
                          -1:ssh 失败，需要检查节点
                          -2:客户端卡住
                          -3:挂载的卷丢失
    """

    rc, stdout = run_command(ip, 'pwd')
    if rc != 0:
        log.info("IP:%s ssh failed. \nstdout: %s" % (ip, stdout))
        return -1
    cmd = 'ssh %s df' % ip
    rc, stdout, stderr = cmd_with_timeout(cmd, timeout)
    if rc:
        log.info('IP:%s df : client is blockup!!! \nstdout: %s \nstderr: %s' % (ip, stdout, stderr))
        return -2
    if rc == 0 and (volume_name not in stdout):
        log.info('IP:%s df : not found volume !!!  \nstdout: %s \nstderr: %s' % (ip, stdout, stderr))
        return -3
    return 0


def wait_df_find_volume(client_lst, volume_name, timeout_blockup, timeout_wait):
    """
    :Author:                  chenjy1
    :Date:                    2018.09.03
    :param client_lst:       (str)要检查的节点管理网ip
    :param volume_name:      (str)要检查的卷名
    :param timeout_blockup:  (int)认为卡住的超时时间 秒
    :param timeout_wait:     (int)等待发现卷的时间（不包含卡住的时间）秒
    :return: ret_lst:        (list)元素个数和lient_lst一样，对应的值含义为:
                                0:正常
                               -1:执行脚本的节点ssh到该节点不通
                               -2:该节点客户端卡住
                               -3:该节点等了timeout_wait时间仍未发现卷
                               None:未查到？此函数有问题
    """
    ret_lst = []
    for i in range(len(client_lst)):
        ret_lst.append(None)
    tmp_timeout_wait = 0  # 临时timeout_wait,用于在timeout_wait中去掉timeout_blockup的时间

    flag_ip_volume = 1
    for i in range(len(client_lst) - 1):
        flag_ip_volume = (flag_ip_volume << 1) + 1  # 111111
    res_ip_volume = flag_ip_volume  # 111111

    start_time = time.time()
    while True:
        for i, ip in enumerate(client_lst):
            if (flag_ip_volume & (1 << i)) != 0:  # 仅看还未发现卷的节点
                res = check_client_state(ip, volume_name, timeout=timeout_blockup)  # 使用判断客户端超时的函数
                ret_lst[i] = res
                if (0 == res) or (-1 == res):
                    flag_ip_volume &= (res_ip_volume ^ (1 << i))  # 将i对应的标志位置0
                elif -2 == res:
                    flag_ip_volume &= (res_ip_volume ^ (1 << i))
                    tmp_timeout_wait += timeout_blockup
                elif -3 == res:
                    log.info('still waiting %s' % ip)
        if flag_ip_volume & res_ip_volume == 0:  # 全0则获取到了全部状态
            break
        time.sleep(10)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('not found volume exist %dh:%dm:%ds' % (h, m, s))
        if exist_time >= timeout_wait + tmp_timeout_wait:
            log.info('have wait %s s' % timeout_wait)
            break
    return ret_lst


"""****************************** pscli 命令管理 ******************************"""


def run_pscli(command, print_flag=True, fault_node_ip=None, timeout_pscli=None, run_cluster=MASTER, **kwargs):
    """
    :author:              baoruobing
    :date:                2018.11.06
    :description:         执行pscli命令
    :param command:       具体的pscli命令
    :param print_flag:    是否打印执行结果
    :param fault_node_ip: 故障点的ip
    :param kwargs:        pscli命令的参数
    :return:
    """
    cmd = "pscli --command=%s" % command
    for key in kwargs:
        if kwargs[key] is not None:
            cmd += " --%s=%s" % (key, kwargs[key])
    print cmd
    rc, stdout = pscli_run_command(cmd=cmd, print_flag=print_flag, fault_node_ip=fault_node_ip, timeout=timeout_pscli,
                                   run_cluster=run_cluster)
    return rc, stdout


def get_master(**kwargs):
    rc, stdout = run_pscli(command='get_master', **kwargs)
    return rc, stdout


def get_all_jobs(**kwargs):
    rc, stdout = run_pscli(command='get_all_jobs', **kwargs)
    return rc, stdout


def get_perf_data(sortby=None, **kwargs):
    rc, stdout = run_pscli(command='get_perf_data', sortby=sortby, **kwargs)
    return rc, stdout


def get_perf_data_per_second(**kwargs):
    rc, stdout = run_pscli(command='get_perf_data_per_second', **kwargs)
    return rc, stdout


def get_top_job_stat(job_type=None, limit=None, **kwargs):
    rc, stdout = run_pscli(command='get_top_job_stat', job_type=job_type, limit=limit, **kwargs)
    return rc, stdout


def get_services(node_ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_services', node_ids=node_ids, **kwargs)
    return rc, stdout


def get_system_state(**kwargs):
    rc, stdout = run_pscli(command='get_system_state', **kwargs)
    return rc, stdout


def get_jnl_replica(output_value=None, **kwargs):
    rc, stdout = run_pscli(command='get_jnl_replica', output_value=output_value, **kwargs)
    return rc, stdout


def get_meta_replica(output_value=None, **kwargs):
    rc, stdout = run_pscli(command='get_meta_replica', output_value=output_value, **kwargs)
    return rc, stdout


def get_system_perf(**kwargs):
    rc, stdout = run_pscli(command='get_system_perf', **kwargs)
    return rc, stdout


def get_cluster_overview(**kwargs):
    rc, stdout = run_pscli(command='get_cluster_overview', **kwargs)
    return rc, stdout


def reload_server_properties(path=None, **kwargs):
    rc, stdout = run_pscli(command='reload_server_properties', path=path, **kwargs)
    return rc, stdout


def shutdown_force(node_ids=None, **kwargs):
    rc, stdout = run_pscli(command='shutdown_force', node_ids=node_ids, **kwargs)
    return rc, stdout


def startup(node_ids=None, **kwargs):
    rc, stdout = run_pscli(command='startup', node_ids=node_ids, **kwargs)
    return rc, stdout


def shutdown(node_ids=None, **kwargs):
    rc, stdout = run_pscli(command='shutdown', node_ids=node_ids, **kwargs)
    return rc, stdout


def set_cluster_uuid(uuid, **kwargs):
    rc, stdout = run_pscli(command='set_cluster_uuid', uuid=uuid, **kwargs)
    return rc, stdout


def get_node_config(node_id=None, ips=None, **kwargs):
    rc, stdout = run_pscli(command='get_node_config', node_id=node_id, ips=ips, **kwargs)
    return rc, stdout


def add_param(section, name, current, default, type, unit=None, min_value=None, max_value=None, max_length=None,
              **kwargs):
    rc, stdout = run_pscli(command='add_param', section=section, name=name, current=current, default=default,
                           type=type, unit=unit, min_value=min_value, max_value=max_value, max_length=max_length,
                           **kwargs)
    return rc, stdout


def update_param(section, name, current, **kwargs):
    rc, stdout = run_pscli(command='update_param', section=section, name=name, current=current, **kwargs)
    return rc, stdout


def get_params(section=None, name=None, output_value=None, filter_changed_params=None, **kwargs):
    rc, stdout = run_pscli(command='get_params', section=section, name=name, output_value=output_value,
                           filter_changed_params=filter_changed_params, **kwargs)
    return rc, stdout


def update_node_state(id, state, **kwargs):
    rc, stdout = run_pscli(command='update_node_state', id=id, state=state, **kwargs)
    return rc, stdout


def reinstall(node_ids, **kwargs):
    rc, stdout = run_pscli(command='reinstall', node_ids=node_ids, **kwargs)
    return rc, stdout


def add_nodes(config_file, **kwargs):
    rc, stdout = run_pscli(command='add_nodes', config_file=config_file, **kwargs)
    return rc, stdout


def remove_node(id, remove_mode=None, auto_query=None, **kwargs):
    rc, stdout = run_pscli(command='remove_node', id=id, remove_mode=remove_mode, auto_query=auto_query, **kwargs)
    return rc, stdout


def cancel_remove_nodes(ids, **kwargs):
    rc, stdout = run_pscli(command='cancel_remove_nodes', ids=ids, **kwargs)
    return rc, stdout


def shutdown_mgs(shutdown_others=None, **kwargs):
    rc, stdout = run_pscli(command='shutdown_mgs', shutdown_others=shutdown_others, **kwargs)
    return rc, stdout


def get_free_nodes(**kwargs):
    rc, stdout = run_pscli(command='get_free_nodes', **kwargs)
    return rc, stdout


def get_nodes(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_nodes', ids=ids, **kwargs)
    return rc, stdout


def make_nodes_online(ids, force=None, **kwargs):
    rc, stdout = run_pscli(command='make_nodes_online', ids=ids, force=force, **kwargs)
    return rc, stdout


def make_node_offline(id, **kwargs):
    rc, stdout = run_pscli(command='make_node_offline', id=id, **kwargs)
    return rc, stdout


def get_node_stat(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_node_stat', ids=ids, **kwargs)
    return rc, stdout


def create_node_pool(name, node_ids, stripe_width=None, disk_parity_num=None, node_parity_num=None, replica_num=None,
                     cascade=None, **kwargs):
    rc, stdout = run_pscli(command='create_node_pool', name=name, node_ids=node_ids, stripe_width=stripe_width,
                           disk_parity_num=disk_parity_num, node_parity_num=node_parity_num, replica_num=replica_num,
                           cascade=cascade, **kwargs)
    return rc, stdout


def create_node_pools(name, node_ids, stripe_width=None, disk_parity_num=None, node_parity_num=None, replica_num=None,
                      **kwargs):
    rc, stdout = run_pscli(command='create_node_pools', name=name, node_ids=node_ids, stripe_width=stripe_width,
                           disk_parity_num=disk_parity_num, node_parity_num=node_parity_num, replica_num=replica_num,
                           **kwargs)
    return rc, stdout


def delete_node_pools(ids, **kwargs):
    rc, stdout = run_pscli(command='delete_node_pools', ids=ids, **kwargs)
    return rc, stdout


def get_node_pools(id=None, **kwargs):
    rc, stdout = run_pscli(command='get_node_pools', id=id, **kwargs)
    return rc, stdout


def update_node_pool(node_pool_id, name, node_ids, **kwargs):
    rc, stdout = run_pscli(command='update_node_pool', node_pool_id=node_pool_id, name=name, node_ids=node_ids,
                           **kwargs)
    return rc, stdout


def preview_node_pool(node_ids, scenario_id, layoutView, **kwargs):
    rc, stdout = run_pscli(command='preview_node_pool', node_ids=node_ids, scenario_id=scenario_id,
                           layoutView=layoutView, **kwargs)
    return rc, stdout


def get_legal_node_pool_layouts(node_ids, **kwargs):
    rc, stdout = run_pscli(command='get_legal_node_pool_layouts', node_ids=node_ids, **kwargs)
    return rc, stdout


def get_node_pool_stat(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_node_pool_stat', ids=ids, **kwargs)
    return rc, stdout


def create_storage_pool(name, type, node_pool_ids=None, disk_ids=None, shared_types=None, scenario_id=None,
                        enable_data_cache=None, **kwargs):
    rc, stdout = run_pscli(command='create_storage_pool', name=name, type=type, node_pool_ids=node_pool_ids,
                           disk_ids=disk_ids, shared_types=shared_types, scenario_id=scenario_id,
                           enable_data_cache=enable_data_cache, **kwargs)
    return rc, stdout


def delete_storage_pool(id, **kwargs):
    rc, stdout = run_pscli(command='delete_storage_pool', id=id, **kwargs)
    return rc, stdout


def get_free_disks_by_node_pool_id(ids, **kwargs):
    rc, stdout = run_pscli(command='get_free_disks_by_node_pool_id', ids=ids, **kwargs)
    return rc, stdout


def get_shared_disks_by_node_pool_id(ids, **kwargs):
    rc, stdout = run_pscli(command='get_shared_disks_by_node_pool_id', ids=ids, **kwargs)
    return rc, stdout


def get_storage_pools(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_storage_pools', ids=ids, **kwargs)
    return rc, stdout


def expand_storage_pool(storage_pool_id, node_pool_ids=None, disk_ids=None, shared_types=None, **kwargs):
    rc, stdout = run_pscli(command='expand_storage_pool', storage_pool_id=storage_pool_id,
                           node_pool_ids=node_pool_ids, disk_ids=disk_ids, shared_types=shared_types, **kwargs)
    return rc, stdout


def get_storage_pool_stat(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_storage_pool_stat', ids=ids, **kwargs)
    return rc, stdout


def get_storage_pool_scenario(id, **kwargs):
    rc, stdout = run_pscli(command='get_storage_pool_scenario', id=id, **kwargs)
    return rc, stdout


def get_storage_pool_scenarios(**kwargs):
    rc, stdout = run_pscli(command='get_storage_pool_scenarios', **kwargs)
    return rc, stdout


def get_disks(node_ids, **kwargs):
    rc, stdout = run_pscli(command='get_disks', node_ids=node_ids, **kwargs)
    return rc, stdout


def add_disks(node_ids, disk_uuids, usage, storage_pool_id=None, **kwargs):
    rc, stdout = run_pscli(command='add_disks', node_ids=node_ids, disk_uuids=disk_uuids, usage=usage,
                           storage_pool_id=storage_pool_id, **kwargs)
    return rc, stdout


def remove_disks(disk_ids, auto_query=None, **kwargs):
    rc, stdout = run_pscli(command='remove_disks', disk_ids=disk_ids, auto_query=auto_query, **kwargs)
    return rc, stdout


def remove_disk_force(disk_id, **kwargs):
    rc, stdout = run_pscli(command='remove_disk_force', disk_id=disk_id, **kwargs)
    return rc, stdout


def cancel_remove_disks(disk_ids, **kwargs):
    rc, stdout = run_pscli(command='cancel_remove_disks', disk_ids=disk_ids, **kwargs)
    return rc, stdout


def change_disk_speed_level_map(speed_type, speed_level, **kwargs):
    rc, stdout = run_pscli(command='change_disk_speed_level_map', speed_type=speed_type, speed_level=speed_level,
                           **kwargs)
    return rc, stdout


def change_disk_speed_level(disk_ids, speed_level, **kwargs):
    rc, stdout = run_pscli(command='change_disk_speed_level', disk_ids=disk_ids, speed_level=speed_level, **kwargs)
    return rc, stdout


def locate_disk(bus_number=None, device_number=None, function_number=None, enclosure_number=None, slot_number=None,
                locate_switch=None, turn_off_all=None, node_id=None, **kwargs):
    rc, stdout = run_pscli(command='locate_disk', bus_number=bus_number, device_number=device_number,
                           function_number=function_number, enclosure_number=enclosure_number,
                           slot_number=slot_number, locate_switch=locate_switch, turn_off_all=turn_off_all,
                           node_id=node_id, **kwargs)
    return rc, stdout


def get_disk_smart(disk_id, **kwargs):
    rc, stdout = run_pscli(command='get_disk_smart', disk_id=disk_id, **kwargs)
    return rc, stdout


def add_nvrams(node_ids, sns, **kwargs):
    rc, stdout = run_pscli(command='add_nvrams', node_ids=node_ids, sns=sns, **kwargs)
    return rc, stdout


def remove_nvrams(ids, **kwargs):
    rc, stdout = run_pscli(command='remove_nvrams', ids=ids, **kwargs)
    return rc, stdout


def get_nvrams(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_nvrams', ids=ids, **kwargs)
    return rc, stdout


def create_client_auth(ip, volume_ids, auto_mount=None, atime=None, acl=None, user_xattr=None, sync=None, desc=None,
                       **kwargs):
    rc, stdout = run_pscli(command='create_client_auth', ip=ip, volume_ids=volume_ids, auto_mount=auto_mount,
                           atime=atime, acl=acl, user_xattr=user_xattr, sync=sync, desc=desc, **kwargs)
    return rc, stdout


def delete_client_auth(ids, **kwargs):
    rc, stdout = run_pscli(command='delete_client_auth', ids=ids, **kwargs)
    return rc, stdout


def get_client_auth(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_client_auth', ids=ids, **kwargs)
    return rc, stdout


def update_client_auth(client_auth_id, ip, volume_ids, auto_mount=None, atime=None, acl=None, user_xattr=None,
                       sync=None, desc=None, **kwargs):
    rc, stdout = run_pscli(command='update_client_auth', client_auth_id=client_auth_id, ip=ip, volume_ids=volume_ids,
                           auto_mount=auto_mount, atime=atime, acl=acl, user_xattr=user_xattr, sync=sync, desc=desc,
                           **kwargs)
    return rc, stdout


def get_clients(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_clients', ids=ids, **kwargs)
    return rc, stdout


def get_events(category=None, level=None, data_limit=None, event_code=None, **kwargs):
    rc, stdout = run_pscli(command='get_events', category=category, level=level, data_limit=data_limit,
                           event_code=event_code, **kwargs)
    return rc, stdout


def delete_events(ids, **kwargs):
    rc, stdout = run_pscli(command='delete_events', ids=ids, **kwargs)
    return rc, stdout


def create_volume(name, storage_pool_id, stripe_width, disk_parity_num, node_parity_num, replica_num,
                  total_bytes=None, dir_slice_num=None, chunk_size=None, obj_size=None, object_size=None,
                  remark=None, **kwargs):
    rc, stdout = run_pscli(command='create_volume', name=name, storage_pool_id=storage_pool_id,
                           stripe_width=stripe_width, disk_parity_num=disk_parity_num, node_parity_num=node_parity_num,
                           replica_num=replica_num, total_bytes=total_bytes, dir_slice_num=dir_slice_num,
                           chunk_size=chunk_size, obj_size=obj_size, object_size=object_size, remark=remark,
                           **kwargs)
    return rc, stdout


def delete_volumes(ids, **kwargs):
    rc, stdout = run_pscli(command='delete_volumes', ids=ids, **kwargs)
    return rc, stdout


def get_volumes(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_volumes', ids=ids, **kwargs)
    return rc, stdout


def update_volume(id, total_bytes=None, remark=None, **kwargs):
    rc, stdout = run_pscli(command='update_volume', id=id, total_bytes=total_bytes,  remark=remark, **kwargs)
    return rc, stdout


def get_legal_volume_layouts(storage_pool_id=None, stripe_width=None, disk_parity_num=None, node_parity_num=None,
                             replica_num=None, **kwargs):
    rc, stdout = run_pscli(command='get_legal_volume_layouts', storage_pool_id=storage_pool_id,
                           stripe_width=stripe_width, disk_parity_num=disk_parity_num, node_parity_num=node_parity_num,
                           replica_num=replica_num, **kwargs)
    return rc, stdout


def get_all_layouts(**kwargs):
    rc, stdout = run_pscli(command='get_all_layouts', **kwargs)
    return rc, stdout


def create_quota(path, auth_provider_id=None, user_type=None, user_or_group_name=None, logical_quota_cal_type=None,
                 logical_hard_threshold=None, logical_soft_threshold=None, logical_grace_time=None,
                 logical_suggest_threshold=None, physical_quota_cal_type=None, physical_hard_threshold=None,
                 physical_soft_threshold=None, physical_grace_time=None, physical_suggest_threshold=None,
                 physical_count_snapshot=None, physical_count_redundant_space=None, filenr_quota_cal_type=None,
                 filenr_hard_threshold=None, filenr_soft_threshold=None, filenr_grace_time=None,
                 filenr_suggest_threshold=None, description=None, **kwargs):
    rc, stdout = run_pscli(command='create_quota', path=path, auth_provider_id=auth_provider_id, user_type=user_type,
                           user_or_group_name=user_or_group_name, logical_quota_cal_type=logical_quota_cal_type,
                           logical_hard_threshold=logical_hard_threshold, logical_soft_threshold=logical_soft_threshold,
                           logical_grace_time=logical_grace_time, logical_suggest_threshold=logical_suggest_threshold,
                           physical_quota_cal_type=physical_quota_cal_type,
                           physical_hard_threshold=physical_hard_threshold,
                           physical_soft_threshold=physical_soft_threshold, physical_grace_time=physical_grace_time,
                           physical_suggest_threshold=physical_suggest_threshold,
                           physical_count_snapshot=physical_count_snapshot, filenr_quota_cal_type=filenr_quota_cal_type,
                           physical_count_redundant_space=physical_count_redundant_space,
                           filenr_hard_threshold=filenr_hard_threshold, filenr_soft_threshold=filenr_soft_threshold,
                           filenr_grace_time=filenr_grace_time, filenr_suggest_threshold=filenr_suggest_threshold,
                           description=description, **kwargs)
    return rc, stdout


def delete_quota(ids, **kwargs):
    rc, stdout = run_pscli(command='delete_quota', ids=ids, **kwargs)
    return rc, stdout


def update_quota(id, logical_quota_cal_type=None, logical_hard_threshold=None, logical_soft_threshold=None,
                 logical_grace_time=None, logical_suggest_threshold=None, physical_quota_cal_type=None,
                 physical_hard_threshold=None, physical_soft_threshold=None, physical_grace_time=None,
                 physical_suggest_threshold=None, physical_count_snapshot=None, physical_count_redundant_space=None,
                 filenr_quota_cal_type=None, filenr_hard_threshold=None, filenr_soft_threshold=None,
                 filenr_grace_time=None, filenr_suggest_threshold=None, description=None, **kwargs):
    rc, stdout = run_pscli(command='update_quota', id=id, logical_quota_cal_type=logical_quota_cal_type,
                           logical_hard_threshold=logical_hard_threshold, logical_soft_threshold=logical_soft_threshold,
                           logical_grace_time=logical_grace_time, logical_suggest_threshold=logical_suggest_threshold,
                           physical_quota_cal_type=physical_quota_cal_type,
                           physical_hard_threshold=physical_hard_threshold,
                           physical_soft_threshold=physical_soft_threshold, physical_grace_time=physical_grace_time,
                           physical_suggest_threshold=physical_suggest_threshold,
                           physical_count_snapshot=physical_count_snapshot, filenr_quota_cal_type=filenr_quota_cal_type,
                           physical_count_redundant_space=physical_count_redundant_space,
                           filenr_hard_threshold=filenr_hard_threshold, filenr_soft_threshold=filenr_soft_threshold,
                           filenr_grace_time=filenr_grace_time, filenr_suggest_threshold=filenr_suggest_threshold,
                           description=description, **kwargs)
    return rc, stdout


def get_quota(param_name=None, param_value=None, start=None, limit=None, ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_quota', param_name=param_name, param_value=param_value, start=start,
                           limit=limit, ids=ids, **kwargs)
    return rc, stdout


def create_snapshot(name, path, expire_time, description=None, **kwargs):
    rc, stdout = run_pscli(command='create_snapshot', name=name, path=path, expire_time=expire_time,
                           description=description, **kwargs)
    return rc, stdout


def update_snapshot(id, description=None, expire_time=None, **kwargs):
    rc, stdout = run_pscli(command='update_snapshot', id=id, expire_time=expire_time, description=description, **kwargs)
    return rc, stdout


def delete_snapshot(ids, **kwargs):
    rc, stdout = run_pscli(command='delete_snapshot', ids=ids, **kwargs)
    return rc, stdout


def get_snapshot(param_name=None, param_value=None, start=None, limit=None, ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_snapshot', param_name=param_name, param_value=param_value, start=start,
                           limit=limit, ids=ids, **kwargs)
    return rc, stdout


def revert_snapshot(snapshot_id, **kwargs):
    rc, stdout = run_pscli(command='revert_snapshot', snapshot_id=snapshot_id, **kwargs)
    return rc, stdout


def get_revert_snapshot(**kwargs):
    rc, stdout = run_pscli(command='get_revert_snapshot', **kwargs)
    return rc, stdout


def delete_revert_snapshot(ids, **kwargs):
    rc, stdout = run_pscli(command='delete_revert_snapshot', ids=ids, **kwargs)
    return rc, stdout


def create_snapshot_strategy(name, path, period_type=None, months=None, week_days=None, days=None, hours=None,
                             minute=None, expire_time=None, description=None, **kwargs):
    rc, stdout = run_pscli(command='create_snapshot_strategy', name=name, path=path, period_type=period_type,
                           months=months, week_days=week_days, days=days, hours=hours, minute=minute,
                           expire_time=expire_time, description=description, **kwargs)
    return rc, stdout


def update_snapshot_strategy(id, period_type=None, months=None, week_days=None, days=None, hours=None,
                             minute=None, expire_time=None, description=None, **kwargs):
    rc, stdout = run_pscli(command='update_snapshot_strategy', id=id, period_type=period_type, months=months,
                           week_days=week_days, days=days, hours=hours, minute=minute, expire_time=expire_time,
                           description=description, **kwargs)
    return rc, stdout


def delete_snapshot_strategy(ids, **kwargs):
    rc, stdout = run_pscli(command='delete_snapshot_strategy', ids=ids, **kwargs)
    return rc, stdout


def get_snapshot_strategy(param_name=None, param_value=None, start=None, limit=None, ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_snapshot_strategy', param_name=param_name, param_value=param_value,
                           start=start, limit=limit, ids=ids, **kwargs)
    return rc, stdout


def validate_license(key, type, **kwargs):
    rc, stdout = run_pscli(command='validate_license', key=key, type=type, **kwargs)
    return rc, stdout


def get_jobengine_state(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_jobengine_state', ids=ids, **kwargs)
    return rc, stdout


def start_jobengine(type, **kwargs):
    rc, stdout = run_pscli(command='start_jobengine', type=type, **kwargs)
    return rc, stdout


def pause_jobengine(type, backend_id, **kwargs):
    rc, stdout = run_pscli(command='pause_jobengine', type=type, backend_id=backend_id, **kwargs)
    return rc, stdout


def restart_jobengine(type, backend_id, **kwargs):
    rc, stdout = run_pscli(command='restart_jobengine', type=type, backend_id=backend_id, **kwargs)
    return rc, stdout


def cancel_jobengine(type, backend_id, **kwargs):
    rc, stdout = run_pscli(command='cancel_jobengine', type=type, backend_id=backend_id, **kwargs)
    return rc, stdout


def get_jobengines(type=None, **kwargs):
    rc, stdout = run_pscli(command='get_jobengines', type=type, **kwargs)
    return rc, stdout


def create_jobengine_impact(impact_info, **kwargs):
    rc, stdout = run_pscli(command='create_jobengine_impact', impact_info=impact_info, **kwargs)
    return rc, stdout


def update_jobengine_impact(id, impact_info, **kwargs):
    rc, stdout = run_pscli(command='update_jobengine_impact', id=id, impact_info=impact_info, **kwargs)
    return rc, stdout


def delete_jobengine_impact(ids, **kwargs):
    rc, stdout = run_pscli(command='delete_jobengine_impact', ids=ids, **kwargs)
    return rc, stdout


def get_jobengine_impact(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_jobengine_impact', ids=ids, **kwargs)
    return rc, stdout


def update_jobengine(type, priority=None, impact_id=None, enable_type=None, time_policy=None, by_day=None,
                     by_week=None, interval=None, **kwargs):
    rc, stdout = run_pscli(command='update_jobengine', type=type, priority=priority, impact_id=impact_id,
                           enable_type=enable_type, time_policy=time_policy, by_day=by_day, by_week=by_week,
                           interval=interval, **kwargs)
    return rc, stdout


def get_alarms(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_alarms', ids=ids, **kwargs)
    return rc, stdout


def clean_alarms(ids=None, **kwargs):
    rc, stdout = run_pscli(command='clean_alarms', ids=ids, **kwargs)
    return rc, stdout


def get_job(job_id, **kwargs):
    rc, stdout = run_pscli(command='get_job', job_id=job_id, **kwargs)
    return rc, stdout


def reload_hardware_config(ids, **kwargs):
    rc, stdout = run_pscli(command='reload_hardware_config', ids=ids, **kwargs)
    return rc, stdout


def add_hardware_config(node_id, dev_name, dev_key, **kwargs):
    rc, stdout = run_pscli(command='add_hardware_config', node_id=node_id, dev_name=dev_name, dev_key=dev_key, **kwargs)
    return rc, stdout


def delete_hardware_config(node_id, dev_name, dev_key, **kwargs):
    rc, stdout = run_pscli(command='delete_hardware_config', node_id=node_id, dev_name=dev_name, dev_key=dev_key,
                           **kwargs)
    return rc, stdout


def add_cabinets(cabinet_names, cabinet_height, **kwargs):
    rc, stdout = run_pscli(command='add_cabinets', cabinet_names=cabinet_names, cabinet_height=cabinet_height, **kwargs)
    return rc, stdout


def get_cabinets(**kwargs):
    rc, stdout = run_pscli(command='get_cabinets', **kwargs)
    return rc, stdout


def remove_cabinet(cabinet_id, **kwargs):
    rc, stdout = run_pscli(command='remove_cabinet', cabinet_id=cabinet_id, **kwargs)
    return rc, stdout


def config_virtual_ip(virtual_ip, subnet_mask, netcard_name, type=None, **kwargs):
    rc, stdout = run_pscli(command='config_virtual_ip', virtual_ip=virtual_ip, subnet_mask=subnet_mask,
                           netcard_name=netcard_name, type=type, **kwargs)
    return rc, stdout


def delete_virtual_ip(**kwargs):
    rc, stdout = run_pscli(command='delete_virtual_ip', **kwargs)
    return rc, stdout


def get_virtual_ip(**kwargs):
    rc, stdout = run_pscli(command='get_virtual_ip', **kwargs)
    return rc, stdout


def get_ntp(**kwargs):
    rc, stdout = run_pscli(command='get_ntp', **kwargs)
    return rc, stdout


def set_ntp(is_enabled, ntp_servers, sync_period=None, **kwargs):
    rc, stdout = run_pscli(command='set_ntp', is_enabled=is_enabled, ntp_servers=ntp_servers, sync_period=sync_period,
                           **kwargs)
    return rc, stdout


def test_ntp_servers(ntp_servers, **kwargs):
    rc, stdout = run_pscli(command='test_ntp_servers', ntp_servers=ntp_servers, **kwargs)
    return rc, stdout


def enable_san(access_zone_id, **kwargs):
    rc, stdout = run_pscli(command='enable_san', access_zone_id=access_zone_id, **kwargs)
    return rc, stdout


def get_targets(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_targets', ids=ids, **kwargs)
    return rc, stdout


def get_targets_by_subnet_ids(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_targets_by_subnet_ids', ids=ids, **kwargs)
    return rc, stdout


def get_cache_set(**kwargs):
    rc, stdout = run_pscli(command='get_cache_set', **kwargs)
    return rc, stdout


def get_snmp(**kwargs):
    rc, stdout = run_pscli(command='get_snmp', **kwargs)
    return rc, stdout


def set_snmp(enabled=None, snmp_version=None, community=None, port=None, trap_hosts=None, trap_level=None, **kwargs):
    rc, stdout = run_pscli(command='set_snmp', enabled=enabled, snmp_version=snmp_version, community=community,
                           port=port, trap_hosts=trap_hosts, trap_level=trap_level, **kwargs)
    return rc, stdout


def add_snmp_usmuser(user_name, auth_algorithm, auth_password, privacy_algorithm, privacy_password, **kwargs):
    rc, stdout = run_pscli(command='add_snmp_usmuser', user_name=user_name, auth_algorithm=auth_algorithm,
                           auth_password=auth_password, privacy_algorithm=privacy_algorithm,
                           privacy_password=privacy_password, **kwargs)
    return rc, stdout


def delete_snmp_usmuser(id, **kwargs):
    rc, stdout = run_pscli(command='delete_snmp_usmuser', id=id, **kwargs)
    return rc, stdout


def update_snmp_usmuser(id, user_name, auth_algorithm, auth_password, privacy_algorithm, privacy_password, **kwargs):
    rc, stdout = run_pscli(command='update_snmp_usmuser', id=id, user_name=user_name, auth_algorithm=auth_algorithm,
                           auth_password=auth_password, privacy_algorithm=privacy_algorithm,
                           privacy_password=privacy_password, **kwargs)
    return rc, stdout


def get_snmp_usmuser(id=None, **kwargs):
    rc, stdout = run_pscli(command='get_snmp_usmuser', id=id, **kwargs)
    return rc, stdout


def check_before_upgrade(**kwargs):
    rc, stdout = run_pscli(command='check_before_upgrade', **kwargs)
    return rc, stdout


def online_upgrade(version, min_version, package_time, upgrade_item=None, **kwargs):
    rc, stdout = run_pscli(command='online_upgrade', version=version, min_version=min_version,
                           package_time=package_time, upgrade_item=upgrade_item, **kwargs)
    return rc, stdout


def offline_upgrade(version, min_version, package_time, upgrade_item=None, **kwargs):
    rc, stdout = run_pscli(command='offline_upgrade', version=version, min_version=min_version,
                           package_time=package_time, upgrade_item=upgrade_item, **kwargs)
    return rc, stdout


def get_upgrade_info(**kwargs):
    rc, stdout = run_pscli(command='get_upgrade_info', **kwargs)
    return rc, stdout


def set_system_version(system_version, **kwargs):
    rc, stdout = run_pscli(command='set_system_version', system_version=system_version,  **kwargs)
    return rc, stdout


def get_system_version(**kwargs):
    rc, stdout = run_pscli(command='get_system_version', **kwargs)
    return rc, stdout


def set_package_time(package_time, **kwargs):
    rc, stdout = run_pscli(command='set_package_time', package_time=package_time, **kwargs)
    return rc, stdout


def get_package_time(**kwargs):
    rc, stdout = run_pscli(command='get_package_time', **kwargs)
    return rc, stdout


def cancel_upgrade(**kwargs):
    rc, stdout = run_pscli(command='cancel_upgrade', **kwargs)
    return rc, stdout


def distribute_package(host_ips, path, upgrade_version, **kwargs):
    rc, stdout = run_pscli(command='distribute_package', host_ips=host_ips, path=path, upgrade_version=upgrade_version,
                           **kwargs)
    return rc, stdout


def get_access_zones(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_access_zones', ids=ids, **kwargs)
    return rc, stdout


def create_access_zone(node_ids, name, auth_provider_id=None, isns_address=None, **kwargs):
    rc, stdout = run_pscli(command='create_access_zone', node_ids=node_ids, name=name,
                           auth_provider_id=auth_provider_id, isns_address=isns_address, **kwargs)
    return rc, stdout


def update_access_zone(id, name=None, node_ids=None, auth_provider_id=None, isns_address=None, **kwargs):
    rc, stdout = run_pscli(command='update_access_zone', id=id, name=name, node_ids=node_ids,
                           auth_provider_id=auth_provider_id, isns_address=isns_address, **kwargs)
    return rc, stdout


def delete_access_zone(id, **kwargs):
    rc, stdout = run_pscli(command='delete_access_zone', id=id, **kwargs)
    return rc, stdout


def get_subnets(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_subnets', ids=ids, **kwargs)
    return rc, stdout


def create_subnet(access_zone_id, name, ip_family, svip, subnet_mask, network_interfaces, subnet_gateway=None,
                  mtu=None, description=None, **kwargs):
    rc, stdout = run_pscli(command='create_subnet', access_zone_id=access_zone_id, name=name, ip_family=ip_family,
                           svip=svip, subnet_mask=subnet_mask, subnet_gateway=subnet_gateway,
                           network_interfaces=network_interfaces, mtu=mtu, description=description, **kwargs)
    return rc, stdout


def update_subnet(id, name=None, svip=None, subnet_mask=None, subnet_gateway=None, network_interfaces=None,
                  mtu=None, description=None, **kwargs):
    rc, stdout = run_pscli(command='update_subnet', id=id, name=name, svip=svip, subnet_mask=subnet_mask,
                           subnet_gateway=subnet_gateway, network_interfaces=network_interfaces, mtu=mtu,
                           description=description, **kwargs)
    return rc, stdout


def delete_subnet(id, **kwargs):
    rc, stdout = run_pscli(command='delete_subnet', id=id, **kwargs)
    return rc, stdout


def get_network_interfaces(access_zone_id, **kwargs):
    rc, stdout = run_pscli(command='get_network_interfaces', access_zone_id=access_zone_id, **kwargs)
    return rc, stdout


def get_vip_address_pools(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_vip_address_pools', ids=ids, **kwargs)
    return rc, stdout


def add_vip_address_pool(subnet_id, domain_name, vip_addresses, supported_protocol, allocation_method,
                         load_balance_policy=None, ip_failover_policy=None, rebalance_policy=None, **kwargs):
    rc, stdout = run_pscli(command='add_vip_address_pool', subnet_id=subnet_id, domain_name=domain_name,
                           vip_addresses=vip_addresses, supported_protocol=supported_protocol,
                           allocation_method=allocation_method, load_balance_policy=load_balance_policy,
                           ip_failover_policy=ip_failover_policy, rebalance_policy=rebalance_policy, **kwargs)
    return rc, stdout


def update_vip_address_pool(id, domain_name=None, vip_addresses=None, load_balance_policy=None, ip_failover_policy=None,
                            rebalance_policy=None, **kwargs):
    rc, stdout = run_pscli(command='update_vip_address_pool', id=id, domain_name=domain_name,
                           vip_addresses=vip_addresses, load_balance_policy=load_balance_policy,
                           ip_failover_policy=ip_failover_policy, rebalance_policy=rebalance_policy, **kwargs)
    return rc, stdout


def delete_vip_address_pool(id, **kwargs):
    rc, stdout = run_pscli(command='delete_vip_address_pool', id=id, **kwargs)
    return rc, stdout


def get_vip_distribution(access_zone_id=None, subnet_id=None, ip_address_pool_id=None, **kwargs):
    rc, stdout = run_pscli(command='get_vip_distribution', access_zone_id=access_zone_id, subnet_id=subnet_id,
                           ip_address_pool_id=ip_address_pool_id, **kwargs)
    return rc, stdout


def create_host_group(name, **kwargs):
    rc, stdout = run_pscli(command='create_host_group', name=name, **kwargs)
    return rc, stdout


def get_host_groups(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_host_groups', ids=ids, **kwargs)
    return rc, stdout


def delete_host_groups(ids, **kwargs):
    rc, stdout = run_pscli(command='delete_host_groups', ids=ids, **kwargs)
    return rc, stdout


def update_host_group(host_group_id, name, **kwargs):
    rc, stdout = run_pscli(command='update_host_group', host_group_id=host_group_id, name=name, **kwargs)
    return rc, stdout


def add_host(name, host_group_id, os_type=None, **kwargs):
    rc, stdout = run_pscli(command='add_host', name=name, host_group_id=host_group_id, os_type=os_type, **kwargs)
    return rc, stdout


def get_hosts(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_hosts', ids=ids, **kwargs)
    return rc, stdout


def update_host(host_id, name, **kwargs):
    rc, stdout = run_pscli(command='update_host', host_id=host_id, name=name, **kwargs)
    return rc, stdout


def remove_hosts(ids, **kwargs):
    rc, stdout = run_pscli(command='remove_hosts', ids=ids, **kwargs)
    return rc, stdout


def add_initiator(iqn, alias, host_id, auth_type=None, chap_username=None, chap_password=None, **kwargs):
    rc, stdout = run_pscli(command='add_initiator', iqn=iqn, alias=alias, host_id=host_id, auth_type=auth_type,
                           chap_username=chap_username, chap_password=chap_password, **kwargs)
    return rc, stdout


def get_initiators(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_initiators', ids=ids, **kwargs)
    return rc, stdout


def remove_initiator(id, **kwargs):
    rc, stdout = run_pscli(command='remove_initiator', id=id, **kwargs)
    return rc, stdout


def update_initiator(initiator_id, alias=None, auth_type=None, chap_username=None, chap_password=None, **kwargs):
    rc, stdout = run_pscli(command='update_initiator', initiator_id=initiator_id, alias=alias, auth_type=auth_type,
                           chap_username=chap_username, chap_password=chap_password, **kwargs)
    return rc, stdout


def create_lun(name, type, storage_pool_id, access_zone_id, total_bytes, max_throughput, max_iops, stripe_width,
               disk_parity_num, node_parity_num, replica_num, **kwargs):
    rc, stdout = run_pscli(command='create_lun', name=name, type=type, storage_pool_id=storage_pool_id,
                           access_zone_id=access_zone_id, total_bytes=total_bytes, max_throughput=max_throughput,
                           max_iops=max_iops, stripe_width=stripe_width, disk_parity_num=disk_parity_num,
                           node_parity_num=node_parity_num, replica_num=replica_num, **kwargs)
    return rc, stdout


def create_luns(name_list, type_list, storage_pool_id_list, access_zone_id_list, total_bytes_list, max_throughput_list,
                max_iops_list, stripe_width_list, disk_parity_num_list, node_parity_num_list, replica_num_list,
                **kwargs):
    rc, stdout = run_pscli(command='create_luns', name_list=name_list, type_list=type_list,
                           storage_pool_id_list=storage_pool_id_list, access_zone_id_list=access_zone_id_list,
                           total_bytes_list=total_bytes_list, max_throughput_list=max_throughput_list,
                           max_iops_list=max_iops_list, stripe_width_list=stripe_width_list,
                           disk_parity_num_list=disk_parity_num_list, node_parity_num_list=node_parity_num_list,
                           replica_num_list=replica_num_list, **kwargs)
    return rc, stdout


def delete_lun(id, **kwargs):
    rc, stdout = run_pscli(command='delete_lun', id=id, **kwargs)
    return rc, stdout


def get_luns(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_luns', ids=ids, **kwargs)
    return rc, stdout


def map_luns_to_host_group(lun_ids, host_group_id, target_id=None, **kwargs):
    rc, stdout = run_pscli(command='map_luns_to_host_group', lun_ids=lun_ids, host_group_id=host_group_id,
                           target_id=target_id, **kwargs)
    return rc, stdout


def get_lun_maps(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_lun_maps', ids=ids, **kwargs)
    return rc, stdout


def get_lun_maps_by_lun_id(lun_ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_lun_maps_by_lun_id', lun_ids=lun_ids, **kwargs)
    return rc, stdout


def get_lun_maps_by_hostgroup_id(host_group_ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_lun_maps_by_hostgroup_id', host_group_ids=host_group_ids, **kwargs)
    return rc, stdout


def delete_lun_map(id, **kwargs):
    rc, stdout = run_pscli(command='delete_lun_map', id=id, **kwargs)
    return rc, stdout


def get_auth_providers_summary(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_auth_providers_summary', ids=ids, **kwargs)
    return rc, stdout


def get_auth_providers_ad(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_auth_providers_ad', ids=ids, **kwargs)
    return rc, stdout


def get_auth_providers_ldap(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_auth_providers_ldap', ids=ids, **kwargs)
    return rc, stdout


def get_auth_providers_nis(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_auth_providers_nis', ids=ids, **kwargs)
    return rc, stdout


def get_auth_providers_local(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_auth_providers_local', ids=ids, **kwargs)
    return rc, stdout


def delete_auth_providers(ids, **kwargs):
    rc, stdout = run_pscli(command='delete_auth_providers', ids=ids, **kwargs)
    return rc, stdout


def add_auth_provider_ad(name, domain_name, dns_addresses, username, password, services_for_unix, unix_id_range=None,
                         other_unix_id_range=None, check=None, **kwargs):
    rc, stdout = run_pscli(command='add_auth_provider_ad', name=name, domain_name=domain_name,
                           dns_addresses=dns_addresses, username=username, password=password,
                           services_for_unix=services_for_unix, unix_id_range=unix_id_range,
                           other_unix_id_range=other_unix_id_range, check=check, **kwargs)
    return rc, stdout


def add_auth_provider_nis(name, domain_name, ip_addresses, check=None, **kwargs):
    rc, stdout = run_pscli(command='add_auth_provider_nis', name=name, domain_name=domain_name,
                           ip_addresses=ip_addresses, check=check, **kwargs)
    return rc, stdout


def add_auth_provider_ldap(name, base_dn, ip_addresses, port=None, bind_dn=None, bind_password=None,
                           domain_password=None, user_search_path=None, group_search_path=None, check=None, **kwargs):
    rc, stdout = run_pscli(command='add_auth_provider_ldap', name=name, base_dn=base_dn, ip_addresses=ip_addresses,
                           port=port, bind_dn=bind_dn, bind_password=bind_password, domain_password=domain_password,
                           user_search_path=user_search_path, group_search_path=group_search_path, check=check,
                           **kwargs)
    return rc, stdout


def update_auth_provider_ad(id, name=None, domain_name=None, dns_addresses=None, username=None, password=None,
                            check=None, **kwargs):
    rc, stdout = run_pscli(command='update_auth_provider_ad', id=id, name=name, domain_name=domain_name,
                           dns_addresses=dns_addresses, username=username, password=password, check=check, **kwargs)
    return rc, stdout


def update_auth_provider_nis(id, name=None, domain_name=None, ip_addresses=None, check=None, **kwargs):
    rc, stdout = run_pscli(command='update_auth_provider_nis', id=id, name=name, domain_name=domain_name,
                           ip_addresses=ip_addresses, check=check, **kwargs)
    return rc, stdout


def update_auth_provider_ldap(id, name=None, base_dn=None, ip_addresses=None, port=None, bind_dn=None,
                              bind_password=None, domain_password=None, user_search_path=None,
                              group_search_path=None, check=None, **kwargs):
    rc, stdout = run_pscli(command='update_auth_provider_ldap', id=id, name=name, base_dn=base_dn,
                           ip_addresses=ip_addresses, port=port, bind_dn=bind_dn, bind_password=bind_password,
                           domain_password=domain_password, user_search_path=user_search_path,
                           group_search_path=group_search_path, check=check, **kwargs)
    return rc, stdout


def update_auth_provider_local(id, bind_password=None, **kwargs):
    rc, stdout = run_pscli(command='update_auth_provider_local', id=id, bind_password=bind_password, **kwargs)
    return rc, stdout


def check_auth_provider(id, **kwargs):
    rc, stdout = run_pscli(command='check_auth_provider', id=id, **kwargs)
    return rc, stdout


def get_auth_users(auth_provider_id, group_id=None, start=None, limit=None, **kwargs):
    rc, stdout = run_pscli(command='get_auth_users', auth_provider_id=auth_provider_id, group_id=group_id,
                           start=start, limit=limit, **kwargs)
    return rc, stdout


def create_auth_user(auth_provider_id, name, password, primary_group_id, secondary_group_ids=None, home_dir=None,
                     **kwargs):
    rc, stdout = run_pscli(command='create_auth_user', auth_provider_id=auth_provider_id, name=name, password=password,
                           primary_group_id=primary_group_id, secondary_group_ids=secondary_group_ids,
                           home_dir=home_dir, **kwargs)
    return rc, stdout


def update_auth_user(id, password=None, primary_group_id=None, secondary_group_ids=None, **kwargs):
    rc, stdout = run_pscli(command='update_auth_user', id=id, password=password, primary_group_id=primary_group_id,
                           secondary_group_ids=secondary_group_ids, **kwargs)
    return rc, stdout


def delete_auth_users(ids, **kwargs):
    rc, stdout = run_pscli(command='delete_auth_users', ids=ids, **kwargs)
    return rc, stdout


def get_auth_groups(auth_provider_id, start=None, limit=None, **kwargs):
    rc, stdout = run_pscli(command='get_auth_groups', auth_provider_id=auth_provider_id, start=start, limit=limit,
                           **kwargs)
    return rc, stdout


def create_auth_group(auth_provider_id, name, **kwargs):
    rc, stdout = run_pscli(command='create_auth_group', auth_provider_id=auth_provider_id, name=name, **kwargs)
    return rc, stdout


def delete_auth_groups(ids, **kwargs):
    rc, stdout = run_pscli(command='delete_auth_groups', ids=ids, **kwargs)
    return rc, stdout


def get_smb_exports(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_smb_exports', ids=ids, **kwargs)
    return rc, stdout


def create_smb_export(access_zone_id, export_name, export_path, description=None, enable_ntfs_acl=None,
                      allow_create_ntfs_acl=None, enable_alternative_datasource=None, enable_dos_attributes=None,
                      enable_os2style_ex_attrs=None, enable_guest=None, enable_oplocks=None, authorization_ip=None,
                      **kwargs):
    rc, stdout = run_pscli(command='create_smb_export', access_zone_id=access_zone_id, export_name=export_name,
                           export_path=export_path, description=description, enable_ntfs_acl=enable_ntfs_acl,
                           allow_create_ntfs_acl=allow_create_ntfs_acl, enable_dos_attributes=enable_dos_attributes,
                           enable_alternative_datasource=enable_alternative_datasource,
                           enable_os2style_ex_attrs=enable_os2style_ex_attrs, enable_guest=enable_guest,
                           enable_oplocks=enable_oplocks, authorization_ip=authorization_ip, **kwargs)
    return rc, stdout


def update_smb_export(id, description=None, enable_ntfs_acl=None, allow_create_ntfs_acl=None,
                      enable_alternative_datasource=None, enable_dos_attributes=None, enable_os2style_ex_attrs=None,
                      enable_guest=None, enable_oplocks=None, authorization_ip=None, **kwargs):
    rc, stdout = run_pscli(command='update_smb_export', id=id, description=description, enable_ntfs_acl=enable_ntfs_acl,
                           allow_create_ntfs_acl=allow_create_ntfs_acl, enable_dos_attributes=enable_dos_attributes,
                           enable_alternative_datasource=enable_alternative_datasource,
                           enable_os2style_ex_attrs=enable_os2style_ex_attrs, enable_guest=enable_guest,
                           enable_oplocks=enable_oplocks, authorization_ip=authorization_ip, **kwargs)
    return rc, stdout


def delete_smb_exports(ids, **kwargs):
    rc, stdout = run_pscli(command='delete_smb_exports', ids=ids, **kwargs)
    return rc, stdout


def get_smb_export_auth_clients(export_ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_smb_export_auth_clients', export_ids=export_ids, **kwargs)
    return rc, stdout


def add_smb_export_auth_clients(export_id, name, type, run_as_root, permission_level=None, **kwargs):
    rc, stdout = run_pscli(command='add_smb_export_auth_clients', export_id=export_id, name=name, type=type,
                           run_as_root=run_as_root, permission_level=permission_level, **kwargs)
    return rc, stdout


def update_smb_export_auth_client(id, run_as_root, permission_level=None, **kwargs):
    rc, stdout = run_pscli(command='update_smb_export_auth_client', id=id, run_as_root=run_as_root,
                           permission_level=permission_level, **kwargs)
    return rc, stdout


def remove_smb_export_auth_clients(ids, **kwargs):
    rc, stdout = run_pscli(command='remove_smb_export_auth_clients', ids=ids, **kwargs)
    return rc, stdout


def get_smb_global_configs(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_smb_global_configs', ids=ids, **kwargs)
    return rc, stdout


def update_smb_global_config(id, enable_change_notify=None, enable_guest=None, enable_send_ntlmv2=None, home_dir=None,
                             enable_alternative_datasource=None, enable_dos_attributes=None, enable_ntfs_acl=None,
                             enable_os2style_ex_attrs=None, allow_create_ntfs_acl=None, enable_oplocks=None,
                             **kwargs):
    rc, stdout = run_pscli(command='update_smb_global_config', id=id, enable_change_notify=enable_change_notify,
                           enable_guest=enable_guest, enable_send_ntlmv2=enable_send_ntlmv2, home_dir=home_dir,
                           enable_alternative_datasource=enable_alternative_datasource,
                           enable_dos_attributes=enable_dos_attributes, enable_ntfs_acl=enable_ntfs_acl,
                           enable_os2style_ex_attrs=enable_os2style_ex_attrs, enable_oplocks=enable_oplocks,
                           allow_create_ntfs_acl=allow_create_ntfs_acl, **kwargs)
    return rc, stdout


def get_nfs_exports(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_nfs_exports', ids=ids, **kwargs)
    return rc, stdout


def create_nfs_export(access_zone_id, export_name, export_path, description=None, **kwargs):
    rc, stdout = run_pscli(command='create_nfs_export', access_zone_id=access_zone_id, export_name=export_name,
                           export_path=export_path, description=description, **kwargs)
    return rc, stdout


def update_nfs_export(id, description=None, **kwargs):
    rc, stdout = run_pscli(command='update_nfs_export', id=id, description=description, **kwargs)
    return rc, stdout


def delete_nfs_exports(ids, **kwargs):
    rc, stdout = run_pscli(command='delete_nfs_exports', ids=ids, **kwargs)
    return rc, stdout


def get_nfs_export_auth_clients(export_ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_nfs_export_auth_clients', export_ids=export_ids, **kwargs)
    return rc, stdout


def add_nfs_export_auth_clients(export_id, name, permission_level, write_mode=None, port_constraint=None,
                                permission_constraint=None, anonuid=None, anongid=None, **kwargs):
    rc, stdout = run_pscli(command='add_nfs_export_auth_clients', export_id=export_id, name=name,
                           permission_level=permission_level, write_mode=write_mode, port_constraint=port_constraint,
                           permission_constraint=permission_constraint, anonuid=anonuid, anongid=anongid, **kwargs)
    return rc, stdout


def update_nfs_export_auth_client(id, permission_level=None, write_mode=None, port_constraint=None,
                                  permission_constraint=None, anonuid=None, anongid=None, **kwargs):
    rc, stdout = run_pscli(command='update_nfs_export_auth_client', id=id, permission_level=permission_level,
                           write_mode=write_mode, port_constraint=port_constraint,
                           permission_constraint=permission_constraint, anonuid=anonuid, anongid=anongid, **kwargs)
    return rc, stdout


def remove_nfs_export_auth_clients(ids, **kwargs):
    rc, stdout = run_pscli(command='remove_nfs_export_auth_clients', ids=ids, **kwargs)
    return rc, stdout


def get_ftp_exports(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_ftp_exports', ids=ids, **kwargs)
    return rc, stdout


def create_ftp_export(access_zone_id, user_name, export_path, enable_dirlist=None, enable_create_folder=None,
                      enable_delete_and_rename=None, enable_upload=None, upload_local_max_rate=None,
                      enable_download=None, download_local_max_rate=None, **kwargs):
    rc, stdout = run_pscli(command='create_ftp_export', access_zone_id=access_zone_id, user_name=user_name,
                           export_path=export_path, enable_dirlist=enable_dirlist,
                           enable_create_folder=enable_create_folder, enable_delete_and_rename=enable_delete_and_rename,
                           enable_upload=enable_upload, upload_local_max_rate=upload_local_max_rate,
                           enable_download=enable_download, download_local_max_rate=download_local_max_rate, **kwargs)
    return rc, stdout


def update_ftp_export(id, export_path=None, enable_dirlist=None, enable_create_folder=None,
                      enable_delete_and_rename=None, enable_upload=None, upload_local_max_rate=None,
                      enable_download=None, download_local_max_rate=None, **kwargs):
    rc, stdout = run_pscli(command='update_ftp_export', id=id,
                           export_path=export_path, enable_dirlist=enable_dirlist,
                           enable_create_folder=enable_create_folder, enable_delete_and_rename=enable_delete_and_rename,
                           enable_upload=enable_upload, upload_local_max_rate=upload_local_max_rate,
                           enable_download=enable_download, download_local_max_rate=download_local_max_rate, **kwargs)
    return rc, stdout


def delete_ftp_exports(ids, **kwargs):
    rc, stdout = run_pscli(command='delete_ftp_exports', ids=ids, **kwargs)
    return rc, stdout


def get_ftp_global_config(access_zone_id, **kwargs):
    rc, stdout = run_pscli(command='get_ftp_global_config', access_zone_id=access_zone_id, **kwargs)
    return rc, stdout


def update_ftp_global_config(access_zone_id, anonymous_enable=None, anon_root=None, anon_upload_enable=None,
                             anon_upload_max_rate=None, anon_download_enable=None, anon_download_max_rate=None,
                             **kwargs):
    rc, stdout = run_pscli(command='update_ftp_global_config', access_zone_id=access_zone_id,
                           anonymous_enable=anonymous_enable, anon_root=anon_root,
                           anon_upload_enable=anon_upload_enable, anon_upload_max_rate=anon_upload_max_rate,
                           anon_download_enable=anon_download_enable, anon_download_max_rate=anon_download_max_rate,
                           **kwargs)
    return rc, stdout


def get_nas_protocol_params(protocol_type, access_zone_id=None, **kwargs):
    rc, stdout = run_pscli(command='get_nas_protocol_params', protocol_type=protocol_type,
                           access_zone_id=access_zone_id, **kwargs)
    return rc, stdout


def update_nas_protocol_param(protocol_type, access_zone_id, param_key, param_value, force=None, **kwargs):
    rc, stdout = run_pscli(command='update_nas_protocol_param', protocol_type=protocol_type,
                           access_zone_id=access_zone_id, param_key=param_key, param_value=param_value, force=force,
                           **kwargs)
    return rc, stdout


def delete_nas_protocol_param(protocol_type, access_zone_id, param_key, **kwargs):
    rc, stdout = run_pscli(command='delete_nas_protocol_param', protocol_type=protocol_type,
                           access_zone_id=access_zone_id, param_key=param_key, **kwargs)
    return rc, stdout


def enable_nas(access_zone_id, protocol_types=None, **kwargs):
    rc, stdout = run_pscli(command='enable_nas', access_zone_id=access_zone_id, protocol_types=protocol_types, **kwargs)
    return rc, stdout


def disable_nas(access_zone_id, protocol_types=None, **kwargs):
    rc, stdout = run_pscli(command='disable_nas', access_zone_id=access_zone_id, protocol_types=protocol_types,
                           **kwargs)
    return rc, stdout


def notify_nas_sync_auth_user_group(access_zone_id, **kwargs):
    rc, stdout = run_pscli(command='notify_nas_sync_auth_user_group', access_zone_id=access_zone_id, **kwargs)
    return rc, stdout


def resolve_domain_name(domain_name, **kwargs):
    rc, stdout = run_pscli(command='resolve_domain_name', domain_name=domain_name, **kwargs)
    return rc, stdout


def get_file_list(path, type=None, display_details=None, start=None, limit=None, **kwargs):
    rc, stdout = run_pscli(command='get_file_list', path=path, type=type, display_details=display_details,
                           start=start, limit=limit, **kwargs)
    return rc, stdout


def create_file(path, posix_permission=None, **kwargs):
    rc, stdout = run_pscli(command='create_file', path=path, posix_permission=posix_permission, **kwargs)
    return rc, stdout


def update_file(path, posix_permission, **kwargs):
    rc, stdout = run_pscli(command='update_file', path=path, posix_permission=posix_permission, **kwargs)
    return rc, stdout


def delete_file(path, **kwargs):
    rc, stdout = run_pscli(command='delete_file', path=path, **kwargs)
    return rc, stdout


def enable_s3(access_zone_id, **kwargs):
    rc, stdout = run_pscli(command='enable_s3', access_zone_id=access_zone_id, **kwargs)
    return rc, stdout


def disable_s3(access_zone_id, **kwargs):
    rc, stdout = run_pscli(command='disable_s3', access_zone_id=access_zone_id, **kwargs)
    return rc, stdout


def add_certificate(account_id, **kwargs):
    rc, stdout = run_pscli(command='add_certificate', account_id=account_id, **kwargs)
    return rc, stdout


def update_certificate(certificate_id, state, **kwargs):
    rc, stdout = run_pscli(command='update_certificate', certificate_id=certificate_id, state=state, **kwargs)
    return rc, stdout


def delete_certificate(certificate_id, **kwargs):
    rc, stdout = run_pscli(command='delete_certificate', certificate_id=certificate_id, **kwargs)
    return rc, stdout


def list_certificates(account_id, **kwargs):
    rc, stdout = run_pscli(command='list_certificates', account_id=account_id, **kwargs)
    return rc, stdout


def add_account(account_name, account_email, account_quota, **kwargs):
    rc, stdout = run_pscli(command='add_account', account_name=account_name, account_email=account_email,
                           account_quota=account_quota, **kwargs)
    return rc, stdout


def delete_account(account_id, **kwargs):
    rc, stdout = run_pscli(command='delete_account', account_id=account_id, **kwargs)
    return rc, stdout


def update_account(account_id, account_quota, **kwargs):
    rc, stdout = run_pscli(command='update_account', account_id=account_id, account_quota=account_quota, **kwargs)
    return rc, stdout


def get_account(account_id, **kwargs):
    rc, stdout = run_pscli(command='get_account', account_id=account_id, **kwargs)
    return rc, stdout


def find_account(account_email, **kwargs):
    rc, stdout = run_pscli(command='find_account', account_email=account_email, **kwargs)
    return rc, stdout


def list_accounts(start_account_id, number, **kwargs):
    rc, stdout = run_pscli(command='list_accounts', start_account_id=start_account_id, number=number, **kwargs)
    return rc, stdout


def list_accounts_sort(start_account_name, number, **kwargs):
    rc, stdout = run_pscli(command='list_accounts_sort', start_account_name=start_account_name, number=number, **kwargs)
    return rc, stdout


def get_internal_perf_report_state(node_ids, **kwargs):
    rc, stdout = run_pscli(command='get_internal_perf_report_state', node_ids=node_ids, **kwargs)
    return rc, stdout


def set_internal_perf_report_state(internal_perf_report_state, node_ids, **kwargs):
    rc, stdout = run_pscli(command='set_internal_perf_report_state', node_ids=node_ids,
                           internal_perf_report_state=internal_perf_report_state, **kwargs)
    return rc, stdout


def get_performance_categories(segment, **kwargs):
    rc, stdout = run_pscli(command='get_performance_categories', segment=segment, **kwargs)
    return rc, stdout


def get_performance_report_data(segment, category, id, start_time=None, end_time=None, from_web=None, **kwargs):
    rc, stdout = run_pscli(command='get_performance_report_data', segment=segment, category=category, id=id,
                           start_time=start_time, end_time=end_time, from_web=from_web, **kwargs)
    return rc, stdout


def get_performance_item_list(segment, category, **kwargs):
    rc, stdout = run_pscli(command='get_performance_item_list', segment=segment, category=category, **kwargs)
    return rc, stdout


def get_multi_performance_report_real_data(segment, categories, ids, **kwargs):
    rc, stdout = run_pscli(command='get_multi_performance_report_real_data', segment=segment, categories=categories,
                           ids=ids, **kwargs)
    return rc, stdout


def get_smsmodem(**kwargs):
    rc, stdout = run_pscli(command='get_smsmodem', **kwargs)
    return rc, stdout


def set_smsmodem(enabled=None, ip=None, ip_port=None, test_phone_number=None, **kwargs):
    rc, stdout = run_pscli(command='set_smsmodem', enabled=enabled, ip=ip, ip_port=ip_port,
                           test_phone_number=test_phone_number, **kwargs)
    return rc, stdout


def test_smsmodem(test_phone_number, **kwargs):
    rc, stdout = run_pscli(command='test_smsmodem', test_phone_number=test_phone_number, **kwargs)
    return rc, stdout


def add_recipient(user_name, strategy, phone_number=None, email=None, **kwargs):
    rc, stdout = run_pscli(command='add_recipient', user_name=user_name, strategy=strategy, phone_number=phone_number,
                           email=email, **kwargs)
    return rc, stdout


def delete_recipient(ids, **kwargs):
    rc, stdout = run_pscli(command='delete_recipient', ids=ids, **kwargs)
    return rc, stdout


def update_recipient(id, user_name=None, phone_number=None, email=None, strategy=None, **kwargs):
    rc, stdout = run_pscli(command='update_recipient', id=id, user_name=user_name, phone_number=phone_number,
                           email=email, strategy=strategy, **kwargs)
    return rc, stdout


def get_recipients(**kwargs):
    rc, stdout = run_pscli(command='get_recipients', **kwargs)
    return rc, stdout


def get_email_config(**kwargs):
    rc, stdout = run_pscli(command='get_email_config', **kwargs)
    return rc, stdout


def send_test_email(address, **kwargs):
    rc, stdout = run_pscli(command='send_test_email', address=address, **kwargs)
    return rc, stdout


def set_email_config(enabled=None, sender_email=None, smtp_server=None, smtp_server_port=None, encrypt_protocol=None,
                     smtp_user_valid=None, user_name=None, password=None, test_email=None, **kwargs):
    rc, stdout = run_pscli(command='set_email_config', enabled=enabled, sender_email=sender_email,
                           smtp_server=smtp_server, smtp_server_port=smtp_server_port,
                           encrypt_protocol=encrypt_protocol, smtp_user_valid=smtp_user_valid, user_name=user_name,
                           password=password, test_email=test_email, **kwargs)
    return rc, stdout


def get_alert_strategies(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_alert_strategies', ids=ids, **kwargs)
    return rc, stdout


def get_alert_strategies_by_key_word(keyWord=None, **kwargs):
    rc, stdout = run_pscli(command='get_alert_strategies_by_key_word', keyWord=keyWord, **kwargs)
    return rc, stdout


def add_alert_strategy(name, language, filterBy, level=None, alarms=None, **kwargs):
    rc, stdout = run_pscli(command='add_alert_strategy', name=name, language=language, filterBy=filterBy,
                           level=level, alarms=alarms, **kwargs)
    return rc, stdout


def update_alert_strategy(id, name=None, language=None, filterBy=None, level=None, alarms=None, **kwargs):
    rc, stdout = run_pscli(command='update_alert_strategy', id=id, name=name, language=language, filterBy=filterBy,
                           level=level, alarms=alarms, **kwargs)
    return rc, stdout


def remove_alert_strategies(ids, **kwargs):
    rc, stdout = run_pscli(command='remove_alert_strategies', ids=ids, **kwargs)
    return rc, stdout


def export_zk(output_dir, dump_name, **kwargs):
    rc, stdout = run_pscli(command='export_zk', output_dir=output_dir, dump_name=dump_name, **kwargs)
    return rc, stdout


def get_fence_versions(**kwargs):
    rc, stdout = run_pscli(command='get_fence_versions', **kwargs)
    return rc, stdout


def get_fence_version_matrix(**kwargs):
    rc, stdout = run_pscli(command='get_fence_version_matrix', **kwargs)
    return rc, stdout


def get_fence_services(node_id=None, service_type=None, **kwargs):
    rc, stdout = run_pscli(command='get_fence_services', node_id=node_id, service_type=service_type, **kwargs)
    return rc, stdout


def add_fence_service(sender_type, node_id, service_type, force=None, **kwargs):
    rc, stdout = run_pscli(command='add_fence_service', sender_type=sender_type, node_id=node_id,
                           service_type=service_type, force=force, **kwargs)
    return rc, stdout


def remove_fence_service(node_id, service_type, **kwargs):
    rc, stdout = run_pscli(command='remove_fence_service', node_id=node_id, service_type=service_type, **kwargs)
    return rc, stdout


def enable_rep_server(node_ids=None, **kwargs):
    rc, stdout = run_pscli(command='enable_rep_server', node_ids=node_ids, **kwargs)
    return rc, stdout


def disable_rep_server(node_ids=None, **kwargs):
    rc, stdout = run_pscli(command='disable_rep_server', node_ids=node_ids, **kwargs)
    return rc, stdout


def get_rep_area(**kwargs):
    rc, stdout = run_pscli(command='get_rep_area', **kwargs)
    return rc, stdout


def create_rep_channel(name=None, ip=None, **kwargs):
    rc, stdout = run_pscli(command='create_rep_channel', name=name, ip=ip, **kwargs)
    return rc, stdout


def delete_rep_channel(channel_id=None, **kwargs):
    rc, stdout = run_pscli(command='delete_rep_channel', channel_id=channel_id, **kwargs)
    return rc, stdout


def get_rep_channels(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_rep_channels', ids=ids, **kwargs)
    return rc, stdout


def get_rep_remote_dir(channel_id=None, parent_dir=None, page_number=None, **kwargs):
    rc, stdout = run_pscli(command='get_rep_remote_dir', channel_id=channel_id, parent_dir=parent_dir,
                           page_number=page_number, **kwargs)
    return rc, stdout


def create_rep_pair(rep_channel_id=None, source_directory=None, destination_directory=None, **kwargs):
    rc, stdout = run_pscli(command='get_rep_remote_dir', rep_channel_id=rep_channel_id,
                           source_directory=source_directory, destination_directory=destination_directory, **kwargs)
    return rc, stdout


def split_rep_pair(id=None, **kwargs):
    rc, stdout = run_pscli(command='split_rep_pair', id=id, **kwargs)
    return rc, stdout


def recover_rep_pair(id=None, **kwargs):
    rc, stdout = run_pscli(command='recover_rep_pair', id=id, **kwargs)
    return rc, stdout


def delete_rep_pair(id=None, **kwargs):
    rc, stdout = run_pscli(command='delete_rep_pair', id=id, **kwargs)
    return rc, stdout


def get_rep_pairs(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_rep_pairs', id=ids, **kwargs)
    return rc, stdout


def create_rep_policy(name=None, rep_pair_id=None, period_type=None, months=False, week_days=None, days=None,
                      hours=None, minute=None, expire_time=None, **kwargs):
    rc, stdout = run_pscli(command='create_rep_policy', name=name, rep_pair_id=rep_pair_id, period_type=period_type,
                           months=months, week_days=week_days, days=days, hours=hours, minute=minute,
                           expire_time=expire_time, **kwargs)
    return rc, stdout


def delete_rep_policies(ids=None, **kwargs):
    rc, stdout = run_pscli(command='delete_rep_policies', ids=ids, **kwargs)
    return rc, stdout


def update_rep_policy(id=None, name=None, rep_pair_id=None, period_type=None, months=False, week_days=None, days=None,
                      hours=None, minute=None, expire_time=None, **kwargs):
    rc, stdout = run_pscli(command='create_rep_policy', id=id, name=name, rep_pair_id=rep_pair_id,
                           period_type=period_type, months=months, week_days=week_days, days=days, hours=hours,
                           minute=minute, expire_time=expire_time, **kwargs)
    return rc, stdout


def get_rep_policies(ids=None, **kwargs):
    rc, stdout = run_pscli(command='get_rep_policies', ids=ids, **kwargs)
    return rc, stdout


def start_rep_task(id=None, **kwargs):
    rc, stdout = run_pscli(command='start_rep_task', id=id, **kwargs)
    return rc, stdout


def pause_rep_task(id=None, **kwargs):
    rc, stdout = run_pscli(command='pause_rep_task', id=id, **kwargs)
    return rc, stdout


def resume_rep_task(id=None, **kwargs):
    rc, stdout = run_pscli(command='resume_rep_task', id=id, **kwargs)
    return rc, stdout


def delete_abnormal_rep_task(id=None, **kwargs):
    rc, stdout = run_pscli(command='delete_abnormal_rep_task', id=id, **kwargs)
    return rc, stdout

"""****************************** nWatch 命令管理 ******************************"""
def get_orole_master():
    """
        :author:      liuyzhb
        :date:        2010.03.12
        :description: 获取主oRole节点id
        :description: 方法：找到集群中所有节点i，逐个获取orole的主，如果获取到则返回orole主节点id，
                            如果失败（可能是由于这个节点），则到下一个节点上执行获取命令，知道获取到
                            主，如果三次遍历所有节点都获取不到，则返回-1，None
        :return:获取成功返回0，id，获取失败返回-1，None
        """
    ob_node_info = Node()
    nodes_id_lst = ob_node_info.get_nodes_id()
    for i in range(3):
        for id in nodes_id_lst:
            cmd = '/home/parastor/tools/nWatch -t oRole -i %s -c oRole#rolemgr_master_dump' % id
            rc, stdout = pscli_run_command(cmd)
            judge_rc(rc, 0, "get_master_of_orole in nodeid %s!!!\nstdout:%s" % (id, stdout),exit_flag = False)
            if rc == 0 and stdout.find('id')>= 0:
                id = stdout.strip().split(':')[1]
                log.info('id of orole master is %s' % id)
                return 0, id
            else:
                log.warn('run %s in node_id %s failed' %(cmd,id))
                log.info('stdout is %s' %stdout )
                continue
    return -1, None


def get_zk_status(node_ip):
    """
            :author:      liuyzhb
            :date:        2010.03.12
            :description: 获取指定ip的zk角色：leader或者follower
            :return:如果成功，返回0和mode，否则返回-1和None
            """
    cmd = "/home/parastor/conf/zk/bin/zkServer.sh status"
    log.info('cmd: %s' %cmd)
    rc, stdout = run_command(node_ip, cmd)
    judge_rc(rc, 0, "get_zk status failed!!!\nstdout:%s" % stdout,exit_flag = False)
    if rc == 0:
        mode = stdout.split(':')[1]
        log.info('zk status of %s is %s ' % (node_ip, mode))
        return rc,mode
    else:
        return rc,None

def get_lock_nr():
    """
    :author:      liuyzhb
    :date:        2010.03.12
    :description: 获取客户端锁的数量
    :description: 方法是到集群中的节点上执行获取命令。如果获取到则返回锁的个数，否则到其他节点上获取
                  如果所有节点都获取不到，则返回-1
    :return:获取成功返回0，锁的个数。否则返回-1，None
    """
    ob_node_info = Node()
    nodes_ip_lst = ob_node_info.get_nodes_ip()
    for ip in nodes_ip_lst:
        cmd = "/home/parastor/tools/dlm_mml -t 5210 -a -l 0"
        rc, stdout = run_command(ip, cmd)
        if rc ==0 and stdout.find('DLM LIST ')>=0:
            if stdout.find('lock_nr') >= 0:
                lock_nr = (stdout.split(',')[2]).split(':')[1]
                log.info('lock_nr is %s' % lock_nr)
                return 0, lock_nr
            else:
                log.info('lock_nr is 0')
                return 0, 0
        else:
            continue
    return -1,None

def get_time_of_parastor():
    """
    :author:      liuyzhb
    :date:        2010.03.15
    :description: 获取集群的时间
    :description: 方法是到集群中的节点上执行"date +%s"
    :return:      如果成功，则返回0和时间戳（十位数字组合，例如：1552628988），否则返回-1和None
    """
    ob_node_info = Node()
    nodes_ip_lst = ob_node_info.get_nodes_ip()
    for ip in nodes_ip_lst:
        cmd= 'date +"%s"'
        rc, stdout = run_command(ip, cmd)
        judge_rc(rc, 0, "get time on node %s fail,let we change another node" %ip, exit_flag=False)
        if rc == 0:
            return 0,stdout
        else:
            pass
    log.error("get time on all nodes %s failled!!!" % nodes_ip_lst)
    return -1,None










class MyThread(threading.Thread):
    """重新定义带返回值的线程类 duyuli"""
    result = None

    def __init__(self, target, args=(), exit_err=True):
        super(MyThread, self).__init__()   # 初始化线程类
        self.func = target
        self.args = args
        self.exitcode = 0          # 退出码
        self.exit_err = exit_err   # 线程异常退出是否抛出异常

    def run(self):
        try:
            self.result = self.func(*self.args)   # 获取返回值
        except Exception:
            self.exitcode = 1
            if self.exit_err:
                raise

    def get_result(self):
            return self.result


def get_cpu_load(node_ip):
    '''
    author: liujx
    date: 2019.03.18
    description: get节点最近一分钟内cpu的平均负载
    :param node_ip: 节点ip
    :return: cpu_load:CPU负载，float
             rc, 0代表执行成功，其他代表执行失败
    '''
    cmd = 'cat /proc/loadavg'
    rc, stdout = run_command(node_ip, cmd, print_flag=False)
    if rc != 0:
        return rc, stdout

    cpu_load = float(stdout.split()[0])
    return rc, cpu_load


def get_memory(node_ip):
    '''
    author: liujx
    date: 2019.03.18
    description: get节点当前的内存使用率
    :param node_ip:
    :return: [rc, mem_rate]
    '''
    cmd = 'free |grep Mem'
    rc, stdout = run_command(node_ip, cmd, print_flag=False)
    if rc != 0:
        return rc, stdout
    result_lst = stdout.split()
    return rc, round(100*float(result_lst[-5])/float(result_lst[-6]), 2)


def get_storage_rate():
    '''
    author: liujx
    date: 2019.03.18
    description: 获取集群中每个节点的存储容量占用率
    :return:[rc, rates_lst]
    '''
    rates_lst = []
    rc = -1
    obj_node = Node()
    node_ids = obj_node.get_nodes_id()
    for node_id in node_ids:
        rc, stdout = get_nodes(ids=node_id, print_flag=False)
        if rc != 0:
            return rc, stdout
        result = json_loads(stdout)
        rates_lst.append(round(float(100)*float(result['result']['nodes'][0]['used_bytes'])/
                           float(result['result']['nodes'][0]['total_bytes']), 2))

    return rc, rates_lst

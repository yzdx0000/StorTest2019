#!/usr/bin/python
# -*- encoding=utf8 -*-

"""
Author: baoruobing
Description: 故障脚本
"""
import os
import sys
import time
import json
import signal
import random
import logging
import threading
import traceback
import subprocess
import ConfigParser
from copy import deepcopy
from optparse import OptionParser
from multiprocessing import Process, Manager


fault_log = None


def log_init(case_log_path=None):
    """
    日志解析
    """
    global fault_log
    if case_log_path:
        file_path = case_log_path
    else:
        file_path = os.path.split(os.path.realpath(__file__))[0]
    file_name = os.path.basename(__file__)
    file_name = file_name.split('.')[0]
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    file_name = now_time + '_' + file_name + '.log'
    file_name = os.path.join(file_path, file_name)

    fault_log = logging.getLogger(name='fault_log')
    fault_log.setLevel(level=logging.INFO)

    handler = logging.FileHandler(file_name, mode='a')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)

    fault_log.addHandler(console)
    fault_log.addHandler(handler)
    return


def run_func_class(func):
    """
    打印错误日志
    """

    def _get_fault(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception:
            self._return_value = False
            fault_log.error("", exc_info=1)
            traceback.print_exc()
            sys.exit(1)
    return _get_fault


def run_func(func):
    """
    打印错误日志
    """
    def _get_fault(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            fault_log.error("", exc_info=1)
            traceback.print_exc()
            sys.exit(1)
    return _get_fault


def arg_analysis():
    """
    参数解析
    """
    parser = OptionParser()
    parser.add_option("-n", "--num",
                      type="int",
                      dest="num",
                      default=10000,
                      help="Required:False   Type:int  Help:fault execution nums, default: %default, range is 1-10000")

    parser.add_option("-c", "--configfile",
                      type="string",
                      dest="configfile",
                      default="config.conf",
                      help="Required:False   Type:string  Help:confile name. default: %default")

    options, args = parser.parse_args()
    # 检查-n参数
    if options.num < 1 or options.num > 10000:
        parser.error("the range of -n or --num is 1-10000")

    test_num = options.num
    config_file = options.configfile
    return test_num, config_file


class Fault_test(object):
    """故障测试"""
    def __init__(self):
        self.start_flag = True
        self.stop_flag = False
        self._running_flag = False
        self._return_value = True
        self.thread_lst = []
        self.run_info_dic = {}

    @run_func_class
    def node_down(self, node_ip, fault_time, wait_time):
        self._node_down(node_ip, fault_time, wait_time)

    @run_func_class
    def net_down(self, node_ip, net_lst, fault_num, all_data_ip, fault_time, wait_time):
        self._net_down(node_ip, net_lst, fault_num, all_data_ip, fault_time, wait_time)

    @run_func_class
    def data_disk_down(self, node_ip, disk_lsscsi_id_lst, fault_num, fault_time, wait_time):
        self._data_disk_down(node_ip, disk_lsscsi_id_lst, fault_num, fault_time, wait_time)

    @run_func_class
    def share_disk_down(self, node_ip, disk_lsscsi_id_lst, fault_num, fault_time, wait_time):
        self._share_disk_down(node_ip, disk_lsscsi_id_lst, fault_num, fault_time, wait_time)

    @run_func_class
    def pro_kill(self, node_ip, pro_lst, fault_num, wait_time):
        self._pro_kill(node_ip, pro_lst, fault_num, wait_time)

    fault_dic = {
        'node_down': {'func': node_down, 'kwargs': {'node_ip': None, 'fault_time': None, 'wait_time': None},
                      'info': 'node_down'},
        'net_down': {'func': net_down, 'kwargs': {'node_ip': None, 'net_lst': None, 'fault_num': None,
                                                  'all_data_ip': None, 'fault_time': None, 'wait_time': None},
                     'info': 'net_down'},
        'data_disk_down': {'func': data_disk_down, 'kwargs': {'node_ip': None, 'disk_lsscsi_id_lst': None,
                                                              'fault_num': None, 'fault_time': None,
                                                              'wait_time': None},
                           'info': 'data_disk_down'},
        'share_disk_down': {'func': share_disk_down, 'kwargs': {'node_ip': None, 'disk_lsscsi_id_lst': None,
                                                                'fault_num': None, 'fault_time': None,
                                                                'wait_time': None},
                            'info': 'share_disk_down'},
        'pro_kill': {'func': pro_kill, 'kwargs': {'node_ip': None, 'pro_lst': None,
                                                  'fault_num': None, 'wait_time': None},
                     'info': 'pro_kill'}
    }

    def start(self, case_log_path=None, config_file='config.conf', test_nums=10000):
        """开始执行故障"""
        self.test_nums = test_nums
        self.stop_flag = False
        """不断检查是否开始，给cosbench使用"""
        while True:
            if self.start_flag:
                break
            time.sleep(10)

        """初始化日志"""
        log_init(case_log_path)

        """获取截取ip信息"""
        self.node_ip_lst, self.node_data_ip_lst, self.node_ip_id_dic = self.get_nodes_info(config_file)

        """解析配置文件"""
        fault_lst = self.get_fault_fun_lst(config_file)

        """执行"""
        self.run_fault(fault_lst)

    def pause(self):
        """暂停，给cosbench使用"""
        self.start_flag = False

    def continue_run(self):
        """继续执行，给cosbench使用"""
        self.start_flag = True

    def stop(self):
        """停止故障运行"""
        self.stop_flag = True

    def join(self):
        """等待故障运行"""
        while True:
            time.sleep(2)
            for th in self.thread_lst:
                if th.is_alive():
                    break
            else:
                break

    @property
    def is_running(self):
        """返回故障是否在执行"""
        return self._running_flag

    @property
    def return_value(self):
        """返回值"""
        return self._return_value

    def run_fault(self, fault_lst):
        """
        执行故障
        """
        self.thread_lst = []
        self.run_info_dic = {}

        fault_log.info("These fault will be performed:")
        for fault_info in fault_lst:
            node_ip = fault_info['kwargs']['node_ip']
            fault_name = fault_info['info']
            fault_log.info("node: %s  %s" % (node_ip, fault_name))
            key = "%s:%s" % (node_ip, fault_name)
            self.run_info_dic[key] = [0, 'stop']

            th = threading.Thread(target=fault_info['func'], args=(self,), kwargs=fault_info['kwargs'], name=key)
            self.thread_lst.append(th)
        fault_log.info("************************************************************")

        self._running_flag = True

        for th in self.thread_lst:
            th.daemon = True
            th.start()

        time.sleep(5)
        print_run_info_th = threading.Thread(target=self.print_run_info)
        print_run_info_th.daemon = True
        print_run_info_th.start()

    def print_run_info(self):
        if self.test_nums == 0:
            test_nums = 10000
        else:
            test_nums = self.test_nums

        while True:
            time.sleep(300)
            running_flag = False
            should_stop_flag = True
            for th in self.thread_lst:
                if th.is_alive():
                    self.run_info_dic[th.name][-1] = 'running'
                    running_flag = True
                    if self.run_info_dic[th.name][0] < test_nums:
                        should_stop_flag = False
                else:
                    self.run_info_dic[th.name][-1] = 'stop'
            fault_log.info("********** %s **********" % self.run_info_dic)
            if not running_flag:
                break
            if should_stop_flag:
                self.stop_flag = True
        self._running_flag = False
        fault_log.info("\n ******************** test finish ********************\n")

    def get_fault_fun_lst(self, config_file):
        fault_lst = []
        cf = ConfigParser.ConfigParser()
        cf.read(config_file)
        section_lst = cf.sections()
        for section in section_lst:
            key_lst = cf.options(section)
            if 'run_down_node_fault' in key_lst and cf.getint(section, 'run_down_node_fault') == 1:
                down_node_fault_time = cf.get(section, 'down_node_fault_time')
                down_node_wait_time = cf.get(section, 'down_node_wait_time')
                node_down_dic = deepcopy(self.fault_dic['node_down'])
                node_down_dic['kwargs']['node_ip'] = section
                node_down_dic['kwargs']['fault_time'] = down_node_fault_time
                node_down_dic['kwargs']['wait_time'] = down_node_wait_time
                fault_lst.append(node_down_dic)
            if 'run_down_net_fault' in key_lst and cf.getint(section, 'run_down_net_fault') == 1:
                net_lst = cf.get(section, 'net_lst').split(',')
                net_fault_num = cf.getint(section, 'net_fault_num')
                net_fault_num = len(net_lst) if net_fault_num > len(net_lst) else net_fault_num
                net_fault_time = cf.get(section, 'net_fault_time')
                net_wait_time = cf.get(section, 'net_wait_time')
                net_down_dic = deepcopy(self.fault_dic['net_down'])
                net_info_lst = self._get_node_net_info(section, net_lst)
                data_ip_lst = self._get_node_data_ip(section)
                net_down_dic['kwargs']['node_ip'] = section
                net_down_dic['kwargs']['net_lst'] = net_info_lst
                net_down_dic['kwargs']['fault_num'] = net_fault_num
                net_down_dic['kwargs']['all_data_ip'] = data_ip_lst
                net_down_dic['kwargs']['fault_time'] = net_fault_time
                net_down_dic['kwargs']['wait_time'] = net_wait_time
                fault_lst.append(net_down_dic)
            if 'run_down_data_disk_fault' in key_lst and cf.getint(section, 'run_down_data_disk_fault') == 1:
                data_disk_fault_lst = cf.get(section, 'data_disk_fault_lst')
                data_disk_fault_lst = None if data_disk_fault_lst == 'None' else data_disk_fault_lst.split(',')
                data_disk_fault_num = cf.getint(section, 'data_disk_fault_num')
                if data_disk_fault_lst:
                    data_disk_fault_num = len(data_disk_fault_lst) if data_disk_fault_num > len(
                        data_disk_fault_lst) else data_disk_fault_num
                data_disk_fault_time = cf.get(section, 'data_disk_fault_time')
                data_disk_wait_time = cf.get(section, 'data_disk_wait_time')
                data_disk_lsscsi_id_lst = self._get_disk_lsscsi_id(section, 'data', data_disk_fault_lst)
                data_disk_down_dic = deepcopy(self.fault_dic['data_disk_down'])
                data_disk_down_dic['kwargs']['node_ip'] = section
                data_disk_down_dic['kwargs']['disk_lsscsi_id_lst'] = data_disk_lsscsi_id_lst
                data_disk_down_dic['kwargs']['fault_num'] = data_disk_fault_num
                data_disk_down_dic['kwargs']['fault_time'] = data_disk_fault_time
                data_disk_down_dic['kwargs']['wait_time'] = data_disk_wait_time
                fault_lst.append(data_disk_down_dic)
            if 'run_down_share_disk_fault' in key_lst and cf.getint(section, 'run_down_share_disk_fault') == 1:
                share_disk_fault_lst = cf.get(section, 'share_disk_fault_lst')
                share_disk_fault_lst = None if share_disk_fault_lst == 'None' else share_disk_fault_lst.split(',')
                share_disk_fault_num = cf.getint(section, 'share_disk_fault_num')
                if share_disk_fault_lst:
                    share_disk_fault_num = len(share_disk_fault_lst) if share_disk_fault_num > len(
                        share_disk_fault_lst) else share_disk_fault_num
                share_disk_fault_time = cf.get(section, 'share_disk_fault_time')
                share_disk_wait_time = cf.get(section, 'share_disk_wait_time')
                share_disk_lsscsi_id_lst = self._get_disk_lsscsi_id(section, 'meta', share_disk_fault_lst)
                share_disk_down_dic = deepcopy(self.fault_dic['share_disk_down'])
                share_disk_down_dic['kwargs']['node_ip'] = section
                share_disk_down_dic['kwargs']['disk_lsscsi_id_lst'] = share_disk_lsscsi_id_lst
                share_disk_down_dic['kwargs']['fault_num'] = share_disk_fault_num
                share_disk_down_dic['kwargs']['fault_time'] = share_disk_fault_time
                share_disk_down_dic['kwargs']['wait_time'] = share_disk_wait_time
                fault_lst.append(share_disk_down_dic)
            if 'run_process_fault' in key_lst and cf.getint(section, 'run_process_fault') == 1:
                pro_fault_lst = cf.get(section, 'pro_fault_lst')
                pro_fault_num = cf.getint(section, 'pro_fault_num')
                pro_fault_num = len(pro_fault_lst) if pro_fault_num > len(pro_fault_lst) else pro_fault_num
                pro_wait_time = cf.get(section, 'pro_wait_time')
                pro_kill_dic = deepcopy(self.fault_dic['pro_kill'])
                pro_kill_dic['kwargs']['node_ip'] = section
                pro_kill_dic['kwargs']['pro_lst'] = pro_fault_lst.split(',')
                pro_kill_dic['kwargs']['fault_num'] = pro_fault_num
                pro_kill_dic['kwargs']['wait_time'] = pro_wait_time
                fault_lst.append(pro_kill_dic)
        return fault_lst

    def _get_disk_lsscsi_id(self, node_ip, disk_type, disk_lst):
        disk_lsscsi_id_lst = []
        if disk_lst:
            for disk_name in disk_lst:
                rc, disk_lsscsi_id = self.get_physicalid_by_name(node_ip, disk_name)
                if rc == 0:
                    disk_lsscsi_id_lst.append(disk_lsscsi_id)
                else:
                    fault_log.error("node: %s, disk %s not exist!!!" % (node_ip, disk_name))
        else:
            rc, node_id = self.get_node_id_by_ip(node_ip)
            share_disk_names, monopoly_disk_names = self.get_share_monopoly_disk_ids(node_id, node_ip)
            if disk_type.lower() == 'data':
                disk_name_lst = monopoly_disk_names
            else:
                disk_name_lst = share_disk_names

            for disk_name in disk_name_lst:
                rc, disk_lsscsi_id = self.get_physicalid_by_name(node_ip, disk_name)
                if rc == 0:
                    disk_lsscsi_id_lst.append(disk_lsscsi_id)
                else:
                    fault_log.error("node: %s, disk %s not exist!!!" % (node_ip, disk_name))
        return disk_lsscsi_id_lst

    def _get_node_net_info(self, node_ip, eth_lst):
        eth_info_lst = []
        for eth in eth_lst:
            cmd = "ip addr | grep %s$" % (eth)
            rc, stdout = self.command(cmd, node_ip=node_ip)
            if rc != 0:
                continue
            ip_and_mask = stdout.split()[1]
            ip = ip_and_mask.split('/')[0]
            eth_info_dic = {'eth': eth, 'ip': ip, 'ip_mask': ip_and_mask}
            eth_info_lst.append(eth_info_dic)
        return eth_info_lst

    def _get_node_data_ip(self, node_ip):
        rc, node_id = self.get_node_id_by_ip(node_ip)
        if rc != 0:
            fault_log.error("%s is not in parastor" % node_ip)
            raise Exception("%s is not in parastor" % node_ip)
        cmd = "pscli --command=get_nodes --ids=%s" % node_id
        rc, stdout = self.command(cmd, node_ip=node_ip)
        if 0 != rc:
            fault_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            return rc, None
        else:
            msg = self.json_loads(stdout)
            data_ips_lst = msg["result"]["nodes"][0]["data_ips"]
            data_ip_lst = []
            for data_ip_info in data_ips_lst:
                data_ip_lst.append(data_ip_info['ip_address'])
            return data_ip_lst

    def get_nodes_info(self, config_file):
        cf = ConfigParser.ConfigParser()
        cf.read(config_file)
        section_lst = cf.sections()
        node_id_lst = self.get_nodes_ids(section_lst[0])
        fault_node_id_lst = []
        node_ip_id_dic = {}
        for section in section_lst:
            rc, node_id = self.get_node_id_by_ip(section)
            if rc != 0:
                fault_log.error("%s is not in parastor" % section)
                raise Exception("%s is not in parastor" % section)
            node_ip_id_dic[section] = node_id
            key_lst = cf.options(section)
            if (('run_down_node_fault' in key_lst and cf.getint(section, 'run_down_node_fault') == 1) or
                    ('run_down_net_fault' in key_lst and cf.getint(section, 'run_down_net_fault') == 1)):
                fault_node_id_lst.append(node_id)

        node_ip_lst = []
        """不是所有节点都有节点和网络故障"""
        for node_id in node_id_lst:
            if node_id not in fault_node_id_lst:
                rc, node_mgr_ip = self.get_node_ip_by_id(node_id, section_lst[0])
                if rc != 0:
                    continue
                node_ip_lst.append(node_mgr_ip)
        if not node_ip_lst:
            node_ip_lst = section_lst[:]
        node_data_ip_lst = self.get_nodes_data_ips(section_lst[0])
        return node_ip_lst, node_data_ip_lst, node_ip_id_dic

    def command(self, cmd, node_ip=None, timeout=None):
        """
        执行shell命令
        """
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

    def run_command(self, cmd):
        """
        执行pscli命令
        """
        rc = 1
        stdout = None
        for node_ip in self.node_ip_lst:
            # 判断节点是否可以ping通
            if self.check_ping(node_ip) is False:
                continue
            # 判断数据网是否正常
            if self.check_datanet(node_ip) is False:
                continue
            # 判断节点上是否有/home/parastor/conf
            if 0 != self.check_path(node_ip, '/home/parastor/conf'):
                continue
            # 判断节点上是否有集群
            rc, stdout = self.command(cmd, node_ip=node_ip)
            if rc == 0:
                return rc, stdout
            if (rc != 0) and ('FindMasterError' in stdout.strip().splitlines()[-1]):
                num = 1
                fault_log.warn('%s return "FindMasterError" %d times' % (cmd, num))
                while True:
                    time.sleep(20)
                    num += 1
                    rc, stdout = self.command(cmd, node_ip)
                    if (rc != 0) and ('FindMasterError' in stdout.strip().splitlines()[-1]):
                        fault_log.warn('%s return "FindMasterError" %d times' % (cmd, num))
                    else:
                        break
            if rc != 0:
                continue
        else:
            return rc, stdout

    def json_loads(self, stdout):
        """
        解析json
        """
        try:
            # stdout = stdout.replace('\\', '')
            stdout_str = json.loads(stdout, strict=False)
            return stdout_str
        except Exception, e:
            fault_log.error(stdout)
            raise Exception("Error msg is %s" % e)

    def get_time(self, time_str):
        """解析配置文件时间"""
        if '-' in time_str:
            time_lst = time_str.split('-')
            time_true = random.randint(int(time_lst[0]), int(time_lst[-1]))
        else:
            time_true = int(time_str)
        return time_true

    def check_ping(self, ip):
        """
        检查ip是否可以ping通
        """
        cmd = 'ping -c 2 %s | grep "0 received" | wc -l' % ip
        rc, stdout = self.command(cmd, timeout=30)
        if '0' != stdout.strip():
            return False
        else:
            return True

    def check_path(self, node_ip, path):
        """
        检查节点上的某个路径是否存在
        """
        cmd = 'ls %s' % path
        rc, stdout = self.command(cmd, node_ip)
        return rc

    def get_ipmi_ip(self, node_ip):
        """
        获取ipmi ip
        """
        cmd = 'ipmitool lan print'
        rc, stdout = self.command(cmd, node_ip)
        if 0 != rc:
            fault_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            return None
        else:
            lines_lst = stdout.strip().split('\n')
            for line in lines_lst:
                if 'IP Address  ' in line:
                    ip = line.split(':')[-1].strip()
                    return ip
            return None

    def get_nodes_ips(self, node_ip):
        """
        获取所有集群节点的管理ip
        """
        cmd = '"pscli --command=get_nodes"'
        rc, stdout = self.command(cmd, node_ip)
        if 0 != rc:
            fault_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        else:
            node_ip_lst = []
            node_info = self.json_loads(stdout)
            nodes = node_info['result']['nodes']
            for node in nodes:
                node_ip_lst.append(node['ctl_ips'][0]['ip_address'])
        return node_ip_lst

    def get_nodes_ids(self, node_ip):
        """
        获取所有集群节点的id
        """
        cmd = '"pscli --command=get_nodes"'
        rc, stdout = self.command(cmd, node_ip)
        if 0 != rc:
            fault_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        else:
            node_id_lst = []
            node_info = self.json_loads(stdout)
            nodes = node_info['result']['nodes']
            for node in nodes:
                node_id_lst.append(node['node_id'])
        return node_id_lst

    def get_nodes_data_ips(self, node_ip):
        """
        获取集群所有节点的数据ip
        """
        cmd = '"pscli --command=get_nodes"'
        rc, stdout = self.command(cmd, node_ip)
        if rc != 0:
            raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        data_ip_lst = []
        stdout = self.json_loads(stdout)
        node_info_lst = stdout['result']['nodes']
        for node_info in node_info_lst:
            for data_ip_info in node_info['data_ips']:
                data_ip_lst.append(data_ip_info['ip_address'])
        return data_ip_lst

    def get_disk_uuid_by_name(self, node_id, disk_name):
        """
        获取磁盘的uuid
        """
        cmd = "pscli --command=get_disks --node_ids=%s" % node_id
        rc, stdout = self.run_command(cmd)
        if 0 != rc:
            fault_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            return rc, None
        else:
            result = self.json_loads(stdout)
            disk_list = result['result']['disks']
            for disk in disk_list:
                if disk['devname'] == disk_name:
                    return rc, disk['uuid']
        return 1, None

    def get_disk_usage_by_name(self, node_id, disk_name):
        """
        获取磁盘的类型
        """
        cmd = "pscli --command=get_disks --node_ids=%s" % node_id
        rc, stdout = self.run_command(cmd)
        if 0 != rc:
            fault_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            return rc, None
        else:
            result = self.json_loads(stdout)
            disk_list = result['result']['disks']
            for disk in disk_list:
                if disk['devname'] == disk_name:
                    return rc, disk['usage']
        return 1, None

    def get_disk_id_by_uuid(self, node_id, disk_uuid):
        """
        通过磁盘uuid获取磁盘id
        """
        cmd = "pscli --command=get_disks --node_ids=%s" % node_id
        rc, stdout = self.run_command(cmd)
        if 0 != rc:
            fault_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            return rc, None
        else:
            result = self.json_loads(stdout)
            disk_list = result['result']['disks']
            for disk in disk_list:
                if disk['uuid'] == disk_uuid:
                    return rc, disk['id']
        return 1, None

    def add_disk(self, node_id, uuid, usage):
        """
        添加磁盘
        """
        cmd = ("pscli --command=add_disks --node_ids=%s --disk_uuids=%s --usage=%s" % (node_id, uuid, usage))
        rc, stdout = self.run_command(cmd)
        if 0 != rc:
            fault_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        return

    def delete_disk(self, disk_id):
        """
        删除磁盘
        """
        cmd = "pscli --command=remove_disks --disk_ids=%s --auto_query=false" % disk_id
        rc, stdout = self.run_command(cmd)
        return rc, stdout

    def check_disk_del_by_uuid(self, node_id, disk_uuid):
        cmd = "pscli --command=get_disks --node_ids=%s" % node_id
        rc, stdout = self.run_command(cmd)
        if 0 != rc:
            fault_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        else:
            result = self.json_loads(stdout)
            disk_list = result['result']['disks']
            for disk in disk_list:
                if disk['uuid'] == disk_uuid:
                    if disk['usedState'] == 'UNUSED':
                        return True
                    else:
                        return False
            return False

    def check_disk_del_ostor(self, node_id, disk_id):
        cmd = '/home/parastor/tools/nWatch -t oStor -i %s -c oStor#disk_is_deleted -a "diskid=%s"' % (node_id, disk_id)
        rc, stdout = self.run_command(cmd)
        if 0 != rc:
            fault_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        else:
            if stdout.strip() == '1':
                return True
            else:
                return False

    def check_datanet(self, node_ip):
        """
        检查节点的数据网是否存在
        """
        cmd = '"ip addr | grep "inet ""'
        rc, stdout = self.command(cmd, node_ip)
        if 0 != rc:
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        lines = stdout.strip().split('\n')
        for line in lines:
            ip = line.split()[1].split('/')[0]
            if ip in self.node_data_ip_lst:
                return True
        return False

    def run_down_node(self, node_ip):
        """
        通过impi下电节点
        """
        fault_log.info("node: %s, down" % (node_ip))
        cmd = "echo b > /proc/sysrq-trigger"
        self.command(cmd, node_ip=node_ip, timeout=10)

    def run_up_node(self, ipmi_ip):
        """
        通过impi上电节点
        """
        cmd1 = 'ipmitool -H %s -I lan -U admin -P admin power on' % ipmi_ip
        cmd2 = 'ipmitool -H %s -I lan -U ADMIN -P ADMIN power on' % ipmi_ip
        rc, stdout = self.command(cmd1)
        if 0 != rc:
            if 'Invalid user name' in stdout:
                rc, stdout = self.command(cmd2)
                if 0 != rc:
                    return False
                else:
                    return True
            else:
                return False
        else:
            return True

    def _node_down(self, node_ip, fault_time, wait_time):
        """
        下电节点
        """
        time.sleep(10)

        key = "%s:node_down" % node_ip

        while True:
            if self.stop_flag is True:
                break
            # 下电
            self.run_down_node(node_ip)
            fault_log.info('node: %s,  down node' % node_ip)

            """不断ping节点，知道可以ping通"""
            start_time = time.time()
            while True:
                if self.check_ping(node_ip):
                    break
                exist_time = int(time.time() - start_time)
                m, s = divmod(exist_time, 60)
                h, m = divmod(m, 60)
                fault_log.info('node: %s cannot ping pass %dh:%dm:%ds' % (node_ip, h, m, s))
                time.sleep(20)

            wait_time_true = self.get_time(wait_time)
            time.sleep(wait_time_true)

            self.run_info_dic[key][0] += 1

    def run_down_net(self, node_ip, eth_lst):
        """
        执行断网
        """
        for eth_info_dic in eth_lst:
            cmd = 'ifconfig %s down' % eth_info_dic['eth']
            fault_log.info("node: %s,  ifconfig %s down" % (node_ip, eth_info_dic['eth']))
            rc, stdout = self.command(cmd, node_ip, timeout=60)
            if 0 != rc:
                fault_log.warn("node %s  ifconfig %s down failed!!!" % (node_ip, eth_info_dic['eth']))
        return

    def run_up_net(self, node_ip, eth_lst):
        """
        恢复网络
        """
        for eth_info_dic in eth_lst:
            cmd = 'ifconfig %s %s up' % (eth_info_dic['eth'], eth_info_dic['ip_mask'])
            fault_log.info("node: %s,  ifconfig %s up" % (node_ip, eth_info_dic['eth']))
            rc, stdout = self.command(cmd, node_ip, timeout=60)
            if 0 != rc:
                fault_log.warn("node %s ifconfig %s up failed!!!" % (node_ip, eth_info_dic['eth']))
        return

    def _net_down(self, node_ip, net_lst, fault_num, all_data_ip, fault_time, wait_time):
        """
        断网
        """
        def _check_fault_all_data_ip(all_data_ip_lst, fault_net_info_lst):
            for data_ip in all_data_ip_lst:
                if data_ip not in [eth_info['ip'] for eth_info in fault_net_info_lst]:
                    return False
            return True

        key = "%s:net_down" % node_ip

        while True:
            if self.stop_flag is True:
                break

            fault_net_lst = random.sample(net_lst, fault_num)

            if _check_fault_all_data_ip(all_data_ip, fault_net_lst):
                self.run_down_node(node_ip)
                """不断ping节点，知道可以ping通"""
                start_time = time.time()
                while True:
                    time.sleep(20)
                    if self.check_ping(node_ip):
                        break
                    exist_time = int(time.time() - start_time)
                    m, s = divmod(exist_time, 60)
                    h, m = divmod(m, 60)
                    fault_log.info('node: %s cannot ping pass %dh:%dm:%ds' % (node_ip, h, m, s))
            else:
                """断网"""
                self.run_down_net(node_ip, fault_net_lst)

                fault_time_true = self.get_time(fault_time)
                time.sleep(fault_time_true)

                """不断ping节点，知道可以ping通"""
                start_time = time.time()
                while True:
                    if self.check_ping(node_ip):
                        break
                    exist_time = int(time.time() - start_time)
                    m, s = divmod(exist_time, 60)
                    h, m = divmod(m, 60)
                    fault_log.info('node: %s cannot ping pass %dh:%dm:%ds' % (node_ip, h, m, s))
                    time.sleep(20)

                """恢复"""
                self.run_up_net(node_ip, fault_net_lst)

            wait_time_true = self.get_time(wait_time)
            time.sleep(wait_time_true)

            self.run_info_dic[key][0] += 1

    def get_node_id_by_ip(self, node_ip):
        """
        通过节点ip获取id
        """
        def _get_node_ips(self, node_ip):
            cmd = 'ip addr | grep "inet "'
            rc, stdout = self.command(cmd, node_ip)
            if 0 != rc:
                raise Exception(
                    "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            node_ip_lst = []
            lines = stdout.strip().split('\n')
            for line in lines:
                ip = line.split()[1].split('/')[0]
                node_ip_lst.append(ip)
            return node_ip_lst

        cmd = 'pscli --command=get_nodes'
        rc, stdout = self.command(cmd, node_ip=node_ip)
        if 0 != rc:
            fault_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            return rc, None
        else:
            node_ip_lst = _get_node_ips(self, node_ip)
            msg = self.json_loads(stdout)
            nodes_info = msg["result"]["nodes"]
            for node in nodes_info:
                ctl_ip = node["ctl_ips"][0]["ip_address"]
                if ctl_ip in node_ip_lst:
                    return rc, node["node_id"]
            fault_log.info("there is not a node's ip is %s!!!" % node_ip)
            return 1, None

    def get_node_ip_by_id(self, node_id, node_ip=None):
        """
        通过节点id获取节点ip
        """
        cmd = 'pscli --command=get_nodes --ids=%s' % node_id
        if node_ip:
            rc, stdout = self.command(cmd, node_ip, timeout=60)
        else:
            rc, stdout = self.run_command(cmd)
        if 0 != rc:
            fault_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            return rc, None
        else:
            msg = self.json_loads(stdout)
            node_info = msg["result"]["nodes"][0]
            node_ip = node_info['ctl_ips'][0]['ip_address']
            return rc, node_ip

    def get_physicalid_by_name(self, node_ip, disk_name):
        """
        通过磁盘名字获取磁盘的lsscsi id
        """
        cmd = 'lsscsi'
        rc, stdout = self.command(cmd, node_ip, timeout=60)
        if 0 != rc:
            return rc, None
        else:
            list_stdout = stdout.strip().split('\n')
            for mem in list_stdout:
                if disk_name in mem:
                    list_mem = mem.split()
                    id = list_mem[0]
                    id = id[1:-1]
                    return rc, id
        return 1, None

    def get_diskname_by_lsscsiid(self, node_ip, lsscsi_id):
        """
        通过磁盘lsscsi id获取磁盘的名字
        """
        cmd = 'lsscsi'
        rc, stdout = self.command(cmd, node_ip, timeout=60)
        if 0 != rc:
            return rc, None
        else:
            list_stdout = stdout.strip().split('\n')
            for mem in list_stdout:
                if lsscsi_id in mem:
                    list_mem = mem.split()
                    disk_name = list_mem[-1]
                    return rc, disk_name
        return 1, None

    def get_share_monopoly_disk_ids(self, node_id, node_ip):
        cmd = ("pscli --command=get_disks --node_ids=%s" % node_id)
        rc, stdout = self.command(cmd, node_ip, timeout=60)
        if 0 != rc:
            fault_log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        else:
            msg = self.json_loads(stdout)
            share_disk_names = []
            monopoly_disk_names = []
            disks_pool = msg['result']['disks']
            for disk in disks_pool:
                if disk['usage'] == 'SHARED' and disk['usedState'] == 'IN_USE' and disk['state'] == 'DISK_STATE_HEALTHY':
                    share_disk_names.append(disk['devname'])
                elif disk['usage'] == 'DATA' and disk['usedState'] == 'IN_USE' and disk['state'] == 'DISK_STATE_HEALTHY':
                    monopoly_disk_names.append(disk['devname'])
        return share_disk_names, monopoly_disk_names

    def pullout_disk(self, node_ip, disk_id):
        """
        拔盘
        """
        cmd = 'echo scsi remove-single-device %s > /proc/scsi/scsi' % disk_id
        fault_log.info('node: %s,  pullout disk %s' % (node_ip, disk_id))
        rc, stdout = self.command(cmd, node_ip, timeout=60)
        if 0 != rc:
            fault_log.error('node %s pullout disk %s failed!!!' % (node_ip, disk_id))
        return

    def insert_disk(self, node_ip, disk_id):
        """
        插盘
        """
        cmd = 'echo scsi add-single-device %s > /proc/scsi/scsi' % disk_id
        fault_log.info('node: %s,  insert disk %s' % (node_ip, disk_id))
        rc, stdout = self.command(cmd, node_ip, timeout=60)
        if 0 != rc:
            fault_log.error('node %s insert disk %s failed!!!' % (node_ip, disk_id))
        time.sleep(5)
        return

    def _data_disk_down(self, node_ip, disk_lsscsi_id_lst, fault_num, fault_time, wait_time):
        """
        拔数据盘故障
        """
        key = "%s:data_disk_down" % node_ip

        while True:
            if self.stop_flag is True:
                break
            fault_disk_lsscsi_id_lst = random.sample(disk_lsscsi_id_lst, fault_num)

            """拔盘"""
            """不断ping节点，知道可以ping通"""
            start_time = time.time()
            while True:
                if self.check_ping(node_ip):
                    break
                exist_time = int(time.time() - start_time)
                m, s = divmod(exist_time, 60)
                h, m = divmod(m, 60)
                fault_log.info('node: %s cannot ping pass %dh:%dm:%ds' % (node_ip, h, m, s))
                time.sleep(20)
            for disk_lsscsi_id in fault_disk_lsscsi_id_lst:
                self.pullout_disk(node_ip, disk_lsscsi_id)

            fault_disk_time = self.get_time(fault_time)
            time.sleep(fault_disk_time)

            """插盘"""
            """不断ping节点，知道可以ping通"""
            start_time = time.time()
            while True:
                if self.check_ping(node_ip):
                    break
                exist_time = int(time.time() - start_time)
                m, s = divmod(exist_time, 60)
                h, m = divmod(m, 60)
                fault_log.info('node: %s cannot ping pass %dh:%dm:%ds' % (node_ip, h, m, s))
                time.sleep(20)
            for disk_lsscsi_id in fault_disk_lsscsi_id_lst:
                self.insert_disk(node_ip, disk_lsscsi_id)

            wait_disk_time = self.get_time(wait_time)
            time.sleep(wait_disk_time)

            self.run_info_dic[key][0] += 1

    def _share_disk_down(self, node_ip, disk_lsscsi_id_lst, fault_num, fault_time, wait_time):
        key = "%s:share_disk_down" % node_ip

        while True:
            if self.stop_flag is True:
                break
            fault_disk_info_lst = []
            fault_disk_lsscsi_id_lst = random.sample(disk_lsscsi_id_lst, fault_num)
            """不断ping节点，知道可以ping通"""
            start_time = time.time()
            while True:
                if self.check_ping(node_ip):
                    break
                exist_time = int(time.time() - start_time)
                m, s = divmod(exist_time, 60)
                h, m = divmod(m, 60)
                fault_log.info('node: %s cannot ping pass %dh:%dm:%ds' % (node_ip, h, m, s))
                time.sleep(20)
            for disk_lsscsi_id in fault_disk_lsscsi_id_lst:
                rc, fault_disk_name = self.get_diskname_by_lsscsiid(node_ip, disk_lsscsi_id)
                if rc != 0:
                    fault_log.error("node: %s, disk %s not exist!!!" % (node_ip, disk_lsscsi_id))
                    continue
                fault_node_id = self.node_ip_id_dic[node_ip]
                rc, fault_disk_uuid = self.get_disk_uuid_by_name(fault_node_id, fault_disk_name)
                if rc != 0:
                    continue
                rc, fault_disk_usage = self.get_disk_usage_by_name(fault_node_id, fault_disk_name)
                if rc != 0:
                    continue
                rc, fault_disk_id = self.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)
                if rc != 0:
                    continue
                fault_disk_info_lst.append({'fault_node_id': fault_node_id,
                                            'fault_disk_name': fault_disk_name,
                                            'fault_disk_lsscsi_id': disk_lsscsi_id,
                                            'fault_disk_uuid': fault_disk_uuid,
                                            'fault_disk_usage': fault_disk_usage,
                                            'fault_disk_id': fault_disk_id})
            """拔盘"""
            """不断ping节点，知道可以ping通"""
            start_time = time.time()
            while True:
                if self.check_ping(node_ip):
                    break
                exist_time = int(time.time() - start_time)
                m, s = divmod(exist_time, 60)
                h, m = divmod(m, 60)
                fault_log.info('node: %s cannot ping pass %dh:%dm:%ds' % (node_ip, h, m, s))
                time.sleep(20)
            for fault_disk_info in fault_disk_info_lst:
                self.pullout_disk(node_ip, fault_disk_info['fault_disk_lsscsi_id'])

            fault_disk_time = self.get_time(fault_time)
            time.sleep(fault_disk_time)

            """插盘"""
            """不断ping节点，知道可以ping通"""
            start_time = time.time()
            while True:
                if self.check_ping(node_ip):
                    break
                exist_time = int(time.time() - start_time)
                m, s = divmod(exist_time, 60)
                h, m = divmod(m, 60)
                fault_log.info('node: %s cannot ping pass %dh:%dm:%ds' % (node_ip, h, m, s))
                time.sleep(20)
            for fault_disk_info in fault_disk_info_lst:
                self.insert_disk(node_ip, fault_disk_info['fault_disk_lsscsi_id'])

            """删盘"""
            """不断ping节点，知道可以ping通"""
            start_time = time.time()
            while True:
                if self.check_ping(node_ip):
                    break
                exist_time = int(time.time() - start_time)
                m, s = divmod(exist_time, 60)
                h, m = divmod(m, 60)
                fault_log.info('node: %s cannot ping pass %dh:%dm:%ds' % (node_ip, h, m, s))
                time.sleep(20)
            for fault_disk_info in fault_disk_info_lst:
                fault_disk_name = fault_disk_info['fault_disk_name']
                fault_disk_id_old = fault_disk_info['fault_disk_id']
                fault_log.info('node %s delete disk %s' % (node_ip, fault_disk_name))
                while True:
                    rc, stdout = self.delete_disk(fault_disk_id_old)
                    if rc != 0:
                        stdout = self.json_loads(stdout)
                        if stdout['err_no'] == 6117:
                            fault_log.warning('other delete disk task is running, wait 30s')
                            time.sleep(30)
                        else:
                            raise Exception("Execute command: delete disk failed. \nstdout: %s" % (stdout))
                    else:
                        break
                # fault_log.info('node %s delete disk %s success' % (node_ip, fault_disk_name))

            """检查磁盘是否删除"""
            start_time = time.time()
            for fault_disk_info in fault_disk_info_lst:
                fault_node_id = fault_disk_info['fault_node_id']
                fault_disk_name = fault_disk_info['fault_disk_name']
                fault_disk_uuid = fault_disk_info['fault_disk_uuid']
                fault_disk_id = fault_disk_info['fault_disk_id']
                # 检查磁盘是否删除
                while True:
                    if (self.check_disk_del_by_uuid(fault_node_id, fault_disk_uuid) and
                            self.check_disk_del_ostor(fault_node_id, fault_disk_id)):
                        fault_log.info('node %s disk %s delete success!!!' % (node_ip, fault_disk_name))
                        break
                    time.sleep(20)
                    exist_time = int(time.time() - start_time)
                    m, s = divmod(exist_time, 60)
                    h, m = divmod(m, 60)
                    fault_log.info('node %s disk %s delete %dh:%dm:%ds' % (node_ip, fault_disk_name, h, m, s))

            time.sleep(90)

            """加盘"""
            for fault_disk_info in fault_disk_info_lst:
                fault_disk_name = fault_disk_info['fault_disk_name']
                fault_node_id = fault_disk_info["fault_node_id"]
                fault_disk_uuid = fault_disk_info['fault_disk_uuid']
                fault_disk_usage = fault_disk_info['fault_disk_usage']
                fault_log.info('node %s add disk %s' % (node_ip, fault_disk_name))
                self.add_disk(fault_node_id, fault_disk_uuid, fault_disk_usage)
                fault_log.info('node %s add disk %s success' % (node_ip, fault_disk_name))

            wait_disk_time = self.get_time(wait_time)
            time.sleep(wait_disk_time)

            self.run_info_dic[key][0] += 1

    def run_kill_process(self, node_ip, process):
        """
        kill进程
        """
        pidof_pro = ['oStor', 'oPara', 'oRole', 'oMgcd', 'oJob', 'oOss', 'oOms', 'oCnas']
        flag = False
        for pro in pidof_pro:
            if pro in process:
                flag = True
                break
        if flag:
            ps_cmd = "pidof %s" % process
            rc, stdout = self.command(ps_cmd, node_ip, timeout=60)
            if "" == stdout:
                return
            kill_cmd = ("kill -9 %s" % stdout)
            rc, stdout = self.command(kill_cmd, node_ip, timeout=60)
            if rc != 0:
                fault_log.error(
                    "node: %s, cmd: %s (process:%s) failed. \nstdout: %s \n" % (node_ip, kill_cmd, process, stdout))
        else:
            ps_cmd = ("ps -ef|grep %s | grep -v grep" % process)
            rc, stdout = self.command(ps_cmd, node_ip, timeout=60)
            if "" == stdout:
                return
            lines = stdout.split('\n')
            for line in lines:
                if line:
                    vars = line.split()
                    pid = vars[1]
                    kill_cmd = ("kill -9 %s" % pid)
                    rc, stdout = self.command(kill_cmd, node_ip, timeout=60)
                    if rc != 0:
                        fault_log.error("Execute command: \"%s\" failed. \nstdout: %s \n" % (kill_cmd, stdout))
        return

    def _pro_kill(self, node_ip, pro_lst, fault_num, wait_time):
        """
        进程故障
        """
        key = "%s:pro_kill" % node_ip

        while True:
            if self.stop_flag is True:
                break

            fault_pro_lst = random.sample(pro_lst, fault_num)

            """kill 进程"""
            for pro in fault_pro_lst:
                fault_log.info("node: %s,  kill %s" % (node_ip, pro))
                self.run_kill_process(node_ip, pro)

            wait_disk_time = self.get_time(wait_time)
            time.sleep(wait_disk_time)

            self.run_info_dic[key][0] += 1


@run_func
def main():
    """
    主函数
    """
    """解析参数"""
    test_num, config_file = arg_analysis()
    obj_fault_test = Fault_test()
    obj_fault_test.start(None, config_file, test_num)
    obj_fault_test.join()


if __name__ == '__main__':
    main()
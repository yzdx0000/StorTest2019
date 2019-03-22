#!/usr/bin/python
# -*- encoding=utf8 -*-

"""
author:      liuyzhb
date:        2018.02.24
description: 向posix节点的指定目录下用iozone写入数据
"""
import os
import re
import threading#!/usr/bin/python
# -*- encoding=utf8 -*-

"""
author:      liuyzhb
date:        2018.02.24
description: 向posix节点的指定目录下用iozone写入数据
"""
import os
import re
import threading
import time
import logging
import traceback

import sys

import utils_path
import get_config
import common
import iozonenas
iozoneposix_log = None


def run_func(func):
    """
    打印错误日志
    """
    def _get_fault(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            iozoneposix_log.error("", exc_info=1)
            traceback.print_exc()
            sys.exit(1)
    return _get_fault

def log_init_iozoneposix(case_log_path):
    """
    日志解析
    """
    global iozoneposix_log

    file_name = os.path.basename(__file__)
    file_name = file_name.split('.')[0]
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    log_file_name = now_time + '_' + file_name + '.log'
    log_file_path = os.path.join(case_log_path, log_file_name)
    print log_file_path

    iozoneposix_log = logging.getLogger(name='iozoneposix_log')
    iozoneposix_log.setLevel(level=logging.INFO)

    handler = logging.FileHandler(log_file_path, mode='a')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)

    iozoneposix_log.addHandler(console)
    iozoneposix_log.addHandler(handler)

    return


class IozonePosix(object):
    def __init__(self, case_log_path, casename):
        log_init_iozoneposix(case_log_path)
        iozoneposix_log.info("********** 初始化 log_init_iozoneposix ************")

        self.casename = casename
        self.start_flag = True
        self._running_flag = False
        self._return_value = True
        self._intervals = 30
        self.thread_lst = []

        posix_vdbench_param = get_config.get_posix_vdbench_param()
        self.posix_ip = posix_vdbench_param['ip']

    @run_func
    def start(self, ):
        self.thread_lst = []
        th = threading.Thread(target=self.run_iozone_main)
        self.thread_lst.append(th)
        self._running_flag = True
        for th in self.thread_lst:
            th.daemon = True
            th.start()

    @run_func
    def stop(self):
        iozoneposix_log.info("===============stop posix iozone==============")
        self.stop_iozone()

    @run_func
    def is_running(self):
        """返回线程是否在执行"""
        return self._running_flag

    @run_func
    def return_value(self):
        """返回值"""
        return self._return_value

    ##############################################################################
    # ##name  :      run_iozone_posix
    # ##parameter:   iozonethreads：iozone配置文件中的每个ip的行数，iozone的总线程数（-t后面的参数）为该值*运行iozone的节点的个数
    #                size：-s后的参数
    #                xfersize :-r 后面的参数
    #                运行命令：iozone -t [run_thread] -s [size] -r [xfersize] -+m [这个参数在函数内部]  -w
    #                num ：上述iozone命令循环的次数
    # ##author:      liuyzhb
    # ##date  :      2019.02.17
    # ##Description: 集群运行iozone,iozone配置文件中的节点ip来自于p300_s3_config.xml文件的nas和私有客户端ip
    ##############################################################################
    @run_func
    def run_iozone_posix(self, iozonethreads, size, xfersize, num):
        # 获取 posix_node 的 ip 参数
        posix_vdbench_param = get_config.get_posix_vdbench_param()
        posix_ip = posix_vdbench_param['ip']
        if posix_ip.find(',') < 0:
            posix_ip=[posix_ip]
        else:
            posix_ip.split(',')
        iozoneposix_log.info('posix_ip is %s' % posix_ip)
        posix_anchor_path = posix_vdbench_param['anchor_path']
        posix_iozone_name = 'posixiozone'
        posix_iozone_path = os.path.join(posix_anchor_path, posix_iozone_name)
        iozoneposix_log.info('posix_iozone_path is %s' % posix_iozone_path)
        for ip in posix_ip:
            print ip
            common.mkdir_path(ip, posix_iozone_path)
        iozoneposix_log.info('posix iozone is ready to start')
        self.iozone_run_faultrun(len(posix_ip),
                                 iozonethreads,
                                 posix_iozone_path,
                                 len(posix_ip)*iozonethreads,
                                 size,
                                 xfersize,
                                 posix_ip,
                                 'posix',
                                 num)
        iozoneposix_log.info('iozoneposix is finish')
        self._running_flag = False


    ##############################################################################
    # ##name  :      run_iozone_main
    # ##parameter:
    #                case_log_path: 记录日志的文件夹路径
    # ##author:      liuyzhb
    # ##date  :      2019.02.17
    # ##Description: 集群运行iozone,iozone配置文件中的节点ip来自于p300_s3_config.xml文件的nas和私有客户端ip
    ##############################################################################
    @run_func
    def run_iozone_main(self):
        # 获取参数
        posix_iozone_param = get_config.get_posix_iozone_param()
        iozonethreads = int(posix_iozone_param['iozonethreads'])
        size = posix_iozone_param['size']
        xfersize = posix_iozone_param['xfersize']
        num = int(posix_iozone_param['num'])
        self.run_iozone_posix(iozonethreads, size, xfersize, num)

    @run_func
    def stop_iozone(self):
        cmd = 'ps -ef | grep "iozone" |grep -v "python" |grep -v "grep" | awk \'{print $2}\' | xargs kill -9'
        cmd1 = 'killall iozone'
        iozoneposix_log.info(common.run_command_shot_time(cmd1, self.posix_ip))

        time.sleep(5)
        iozoneposix_log.info(common.run_command_shot_time(cmd))
        common.run_command_shot_time(cmd)
        # common.run_command_shot_time(cmd, self.posix_ip)
        iozoneposix_log.info("kill all iozone process")
        self._running_flag = False

    ##############################################################################
    # ##name  :      iozone_run_faultrun
    # ##parameter:   node_count：对几个节点运行
    #                line_per_node：每个node有line_per_node行
    #                运行命令：iozone -t [run_thread] -s [size] -r [xfersize] -+m [这个参数在函数内部]  -w
    #                path参数为对哪个目录iozone
    #                ips:执行iozone的节点ip列表
    #                flag:iozone配置文件的名称标志
    #                num:iozone命令执行的次数
    # ##author:      liuyzhb
    # ##date  :      2019.02.17
    # ##Description: 集群运行iozone,iozone配置文件中的节点ip来自于p300_s3_config.xml文件的nas和私有客户端ip
    ##############################################################################
    def iozone_run_faultrun(
            self,
            node_count,
            line_per_node,
            path,
            run_thread,
            size,
            xfersize,
            ips,
            flag,
            num):
        iozoneposix_log.info("\t[ iozone_run ]")
        iozoneposix_log.info("prepare iozone config file")
        tools_path = get_config.get_tools_path()
        iozone_file_path = tools_path + '/iozone/iozonetest' + flag

        # 清除旧的iozone配置文件
        if iozone_file_path == '' or re.match(r'[/\*]*$', iozone_file_path) is not None:
            iozoneposix_log.warn('-----There is a dangerous command!!!-----')
            return -1, None
        else:
            cmd = 'rm -rf %s' % iozone_file_path
            rc = common.command(cmd)
            if rc != 0:
                iozoneposix_log.info("rm -rf iozonefile failed!!!!!!")

        # 开始按设定的参数写入配置文件
        file_object = open(iozone_file_path, 'w')
        for i in range(len(ips)):
            for j in range(line_per_node):
                node_ip_tmp = ips[i]
                file_object.write(node_ip_tmp + '   ')
                file_object.write(path + '   ' + 'iozone' + '\n')
        file_object.close()
        # 执行iozone
        cmd = 'iozone -t %d -s %s -r %s -+m %s -i 0 -w' % (run_thread,
                                                           size,
                                                           xfersize,
                                                           iozone_file_path)
        iozoneposix_log.info('cmd: %s' % cmd)
        for i in range(num):
            time.sleep(10)
            iozoneposix_log.info('_running_flag: %s' % self._running_flag)
            if self._running_flag is False:
                break
            iozoneposix_log.info("start run iozone num %d " % i)
            rc = common.command(cmd)
        return rc


if __name__=="__main__":

    case_log_path = '/home/StorTest/test_cases/log/case_log/test'
    io = IozonePosix(case_log_path, '30-0-0-1')
    io.start()

    for i in range(20):
        iozoneposix_log.info("running flag: %s" % io.is_running())
        time.sleep(10)

    io.stop()
    while True:
        iozoneposix_log.info("running flag: %s" % io.is_running())
        time.sleep(30)


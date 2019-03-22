# -*-coding:utf-8 -*
import os
import sys
import threading
import time
import logging
import traceback
import re

import utils_path
import get_config
import common
import tool_use

"""
author:      xutengda
date:        2019.02.21
description: 向指定节点的指定目录下用mdtest写入数据
"""
mdtest_log = None


def log_init_mdtest(case_log_path):
    """
    日志解析
    """
    global mdtest_log

    file_name = os.path.basename(__file__)
    file_name = file_name.split('.')[0]
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    log_file_name = now_time + '_' + file_name + '.log'
    log_file_path = os.path.join(case_log_path, log_file_name)
    print log_file_path

    mdtest_log = logging.getLogger(name='mdtest_log')
    mdtest_log.setLevel(level = logging.INFO)

    handler = logging.FileHandler(log_file_path, mode='a')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)

    mdtest_log.addHandler(console)
    mdtest_log.addHandler(handler)

    return


def run_func(func):
    """
    打印错误日志
    """
    def _get_fault(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            mdtest_log.error("", exc_info=1)
            traceback.print_exc()
            sys.exit(1)
    return _get_fault


class MdtestTest(object):
    def __init__(self, case_log_path, casename):
        log_init_mdtest(case_log_path)
        mdtest_log.info("********** 初始化 mdtest_log ************")

        self.start_flag = True
        self._running_flag = False
        self._return_value = True
        self._intervals = 30
        self.thread_lst = []
        self.casename = casename
        #获取mdtest参数
        mdtest_param = get_config.get_mdtest_param()
        self.depth = mdtest_param['depth']
        self.width = mdtest_param['width']
        self.files = mdtest_param['files']
        self.sizes = mdtest_param['sizes']
        self.num = mdtest_param['num']
        self.run_in_nas = mdtest_param['run_in_nas']
        self.run_in_posix = mdtest_param['run_in_posix']
        mdtest_param_nas = get_config.get_nas_vdbench_param()  #获取nas的参数
        self.nas_ip = mdtest_param_nas['ip']
        self.nas_path = mdtest_param_nas['anchor_path']
        mdtest_param_posix = get_config.get_posix_vdbench_param()  #获取私有客户端的参数
        self.posix_ip = mdtest_param_posix['ip']
        self.posix_path = mdtest_param_posix['anchor_path']

    @run_func
    def start(self,):
        self.thread_lst = []
        th = threading.Thread(target=self.start_mdtest_nas)
        th2 = threading.Thread(target=self.start_mdtest_posix)
        self.thread_lst.append(th)
        self.thread_lst.append(th2)
        self._running_flag = True
        for th in self.thread_lst:
            th.daemon = True
            th.start()

    @run_func
    def stop(self):
        mdtest_log.info("===============stop mdtest==============")
        self.stop_mdtest()

    @run_func
    def is_running(self):
        """返回线程是否在执行"""
        return self._running_flag

    @run_func
    def return_value(self):
        """返回值"""
        return self._return_value

    @run_func
    def run_mdtest(self, ip, mdtest_path, depth=None, width=None, files=None, sizes=None, num=None):
        mdtest_log.info('clean old mdtest dir......')

        cmd_check_mdtest_path = "ls -l %s" % mdtest_path
        rc, output = common.run_command(ip, cmd_check_mdtest_path)
        if 0 == rc:
        # if os.path.exists(mdtest_path):  # 旧的判断mdtest目录是否存在有问题，只是在StorTest节点判断，没有到nfs/posix节点去判断，20190320
            cmd1 = 'rm -rf %s/' % mdtest_path
            mdtest_log.info('cmd1: %s' % cmd1)
            rc, stdout = common.run_command(ip, cmd1)
            if rc != 0:
                mdtest_log.error("rm mdtest_path failed!!!")
                self._running_flag = False
                raise Exception
        mdtest_log.info(depth, width, files, sizes, mdtest_path)
        cmd2 = 'mdtest -z %s -b %s -I %s -F -w %s -d %s' % (depth, width, files, sizes, mdtest_path)
        mdtest_log.info('cmd2: %s' % cmd2)
        mdtest_log.info("start run mdtest: %s" % cmd2)
        for i in range(num):
            time.sleep(10)
            mdtest_log.info('self._running_flag: %s' % self._running_flag)
            if self._running_flag is False:
                mdtest_log.info('mdtest is finish')
                break
            else:
                mdtest_log.info("start run mdtest num %d " % i)
                rc, stdout = common.run_command(ip, cmd2)
                if rc != 0:
                    mdtest_log.info(stdout)
                    mdtest_log.error("run_mdtest failed")
                    self._running_flag = False
                    break
        mdtest_log.info('mdtest is finish')
        self._running_flag = False

    @run_func
    def start_mdtest_nas(self):
        mdtest_log.info('**********获取nas_mdtest参数**********')
        #获取参数
        # mdtest_nas_name = self.casename + '_nas_mdtest'
        mdtest_nas_name = 'nas_mdtest'
        mdtest_nas_path = os.path.join(self.nas_path, mdtest_nas_name)
        depth = self.depth
        width = self.width
        files = self.files
        sizes = self.sizes
        nas_ip = self.nas_ip
        num = int(self.num)
        if self.run_in_nas == 'yes':
            mdtest_log.info('nas_mdtest is ready to start')
            self.run_mdtest(nas_ip, mdtest_nas_path, depth, width, files, sizes, num)
        else:
            mdtest_log.info('nas_mdtest is no need to run')
        return

    @run_func
    def start_mdtest_posix(self):
        mdtest_log.info('**********获取posix_mdtest参数**********')
        # 获取参数
        # mdtest_posix_name = self.casename + '_posix_mdtest'
        mdtest_posix_name = 'posix_mdtest'
        mdtest_posix_path = os.path.join(self.posix_path, mdtest_posix_name)
        depth = self.depth
        width = self.width
        files = self.files
        sizes = self.sizes
        posix_ip = self.posix_ip
        num = int(self.num)
        if self.run_in_posix == 'yes':
            mdtest_log.info('posix_mdtest is ready to start')
            self.run_mdtest(posix_ip, mdtest_posix_path, depth, width, files, sizes, num)
        else:
            mdtest_log.info('posix_mdtest is no need to run')
        return

    def stop_mdtest(self):
        cmd = "ps -ef | grep mdtest |grep -v python |grep -v grep"

        mdtest_log.info("start to stop nas mdtest...")
        rc, output = common.run_command(self.nas_ip, cmd)
        for item in output.split('\n')[:-1]:
            cmd_test_final = re.split('\s+', item)
            pro_num_nas = cmd_test_final[1]
            cmd_kill = "kill -9 %s" % pro_num_nas
            rc_kill_nas, output_kill_nas = common.run_command(self.nas_ip, cmd_kill)
            mdtest_log.info("nas mdtest process id is:%s\n cmd:%s\n rc is %d\n output is %s\n" % (pro_num_nas, cmd_kill, rc_kill_nas, output_kill_nas))
        mdtest_log.info('stop nas mdtest success')

        mdtest_log.info("start to stop posix mdtest...")
        rc, output = common.run_command(self.posix_ip, cmd)
        for item in output.split('\n')[:-1]:
            cmd_test_final = re.split('\s+', item)
            pro_num_posix = cmd_test_final[1]
            cmd_kill = "kill -9 %s" % pro_num_posix
            rc_kill_posix, output_kill_posix = common.run_command(self.nas_ip, cmd_kill)
            mdtest_log.info("posix mdtest process id is:%s\n cmd:%s\n rc is %d\n output is %s\n" % (pro_num_posix, cmd_kill, rc_kill_posix, output_kill_posix))
        mdtest_log.info('stop posix mdtest success')




        
        self._running_flag = False


if __name__ == "__main__":
    case_log_path='/home/StorTest/test_cases/log/case_log/test'
    md = MdtestTest(case_log_path, '30-0-0-1')
    md.start()

    for i in range(10):
        mdtest_log.info("running flag: %s" % md.is_running())
        time.sleep(10)
    md.stop()
    while True:
        mdtest_log.info("running flag: %s" % md.is_running())
        time.sleep(30)


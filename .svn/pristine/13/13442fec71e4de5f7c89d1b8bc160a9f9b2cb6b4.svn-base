# -*-coding:utf-8 -*
import os
import sys
import threading
import time
import logging
import traceback

import utils_path
import get_config
import common
import tool_use

mdtest_mpirun_log = None


def run_func(func):
    """
    打印错误日志
    """
    def _get_fault(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            mdtest_mpirun_log.error("", exc_info=1)
            traceback.print_exc()
            sys.exit(1)
    return _get_fault


def log_init_mdtest_mpirun(case_log_path):
    """
    日志解析
    """
    global mdtest_mpirun_log

    file_name = os.path.basename(__file__)
    file_name = file_name.split('.')[0]
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    log_file_name = now_time + '_' + file_name + '.log'
    log_file_path = os.path.join(case_log_path, log_file_name)
    print log_file_path

    mdtest_mpirun_log = logging.getLogger(name='mdtest_mpirun_log')
    mdtest_mpirun_log.setLevel(level = logging.INFO)

    handler = logging.FileHandler(log_file_path, mode='a')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)

    mdtest_mpirun_log.addHandler(console)
    mdtest_mpirun_log.addHandler(handler)

    return


class Mdtest_MpirunTest(object):
    def __init__(self):
        self.start_flag = True
        self._running_flag = False
        self._return_value = True
        self._intervals = 30
        self.thread_lst = []

    @run_func
    def start(self, case_log_path, casename, mdtest_mpirun_flag=None):
        log_init_mdtest_mpirun(case_log_path)
        mdtest_mpirun_log.info("********** 初始化 mdtest_mpirun_log ************")

        self.thread_lst = []
        th = threading.Thread(target=self.start_nas,
                              args=(casename, mdtest_mpirun_flag,))
        self.thread_lst.append(th)
        self._running_flag = True
        for th in self.thread_lst:
            th.daemon = True
            th.start()

    @run_func
    def stop(self):
        mdtest_mpirun_log.info("===============stop mdtest==============")
        self.stop_nas()

    @run_func
    def is_running(self):
        """返回线程是否在执行"""
        return self._running_flag

    @run_func
    def return_value(self):
        """返回值"""
        return self._return_value

    @run_func
    def run_mdtest_mpirun(self, ip, mdtestfile_path, mdtest_path,
                          depth=None, width=None, files=None, sizes=None):
        cmd='mpirun --allow-run-as-root --machinefile %s ' \
            'mdtest -z %s -I %s -b %s -F -w %s -C -d %s'% (mdtestfile_path,
                                                           depth, width, files, sizes, mdtest_path)
        print cmd
        mdtest_mpirun_log.info("start run mdtest")
        rc, stdout = common.run_command(ip, cmd)
        return rc, stdout

    @run_func
    def start_mdtest_mpirun(self):
        mdtest_mpirun_log.info('**********获取参数**********')
        # 获取参数
        ip = '10.2.40.84'
        mdtest_path = '/mnt/xutd/mdtest'
        mdtestfile_path = '/mnt/xutd/mdtest/mdtestfile'
        depth = '3'
        width = '3'
        files = '3'
        sizes = '4k'
        #生成mdtestfile
        cmd='echo -e "20.10.10.84 slots=50\n20.10.10.181 slots=50" > %s ' %mdtestfile_path
        print cmd
        mdtest_mpirun_log.info('开始创建mdtestfile配置文件')
        rc, stdout = common.run_command(ip, cmd)
        if rc != 0:
            mdtest_mpirun_log.info(stdout)
            mdtest_mpirun_log.error("创建配置文件 failed")

        mdtest_mpirun_log.info('mdtest is ready to start')

        rc, stdout = self.run_mdtest_mpirun(ip, mdtestfile_path, mdtest_path,
                                            depth, width, files, sizes)
        if rc != 0:
            mdtest_mpirun_log.info(stdout)
            mdtest_mpirun_log.error("mdtest_mpirun failed")
        return


if __name__ == "__main__":
    log_init_mdtest_mpirun(case_log_path='/home')
    md = Mdtest_MpirunTest()
    md.start_mdtest_mpirun()
    
#!/usr/bin/python
# -*-coding:utf-8 -*

import os
import subprocess
import sys
import threading
import traceback

import requests
import time
import logging

import utils_path
import get_config
import common
import create_s3_xml

##########################################################################
#
# Author: lichengxu
# date 2018-12-26
# @summary：
#    运行 cosbench 并判断各种状态
# @steps:
#    1、导入待运行的脚本；
#    2、运行 cosbench
#    9、清理环境
#
# @changelog：
##########################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]                 # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')

cosbench_log = None

def command(cmd, node_ip=None):
    """
    :author:        baoruobing
    :date  :        2018.08.15
    :description:   执行shell命令
    :param cmd:     (str)要执行的命令
    :param node_ip: (str)节点ip,不输入时为本节点
    :return:
    """
    if node_ip:
        cmd1 = 'ssh %s "%s"' % (node_ip, cmd)
    else:
        cmd1 = cmd
    process = subprocess.Popen(
        cmd1,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    output, unused_err = process.communicate()
    retcode = process.poll()
    return retcode, output


def log_init_cosbench(case_log_path):
    """
    日志解析
    """
    global cosbench_log

    file_name = os.path.basename(__file__)
    file_name = file_name.split('.')[0]
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    log_file_name = now_time + '_' + file_name + '.log'
    log_file_path = os.path.join(case_log_path, log_file_name)
    print log_file_path

    cosbench_log = logging.getLogger(name='cosbench_log')
    cosbench_log.setLevel(level = logging.INFO)

    handler = logging.FileHandler(log_file_path, mode='a')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)

    cosbench_log.addHandler(console)
    cosbench_log.addHandler(handler)
    return


def run_func(func):
    """
    打印错误日志
    """
    def _get_fault(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            cosbench_log.error("", exc_info=1)
            traceback.print_exc()
            sys.exit(1)
    return _get_fault


class CosbenchTest(object):
    def __init__(self, case_log_path, account_name):
        log_init_cosbench(case_log_path)
        cosbench_log.info("********** 初始化 cosbench-log ************")

        self.start_flag = True
        self._running_flag = False
        self._return_value = True
        self._intervals = 10
        self.thread_lst = []

        self.IF_MAKE_FAULT = False
        self.init_run_time = 0
        self.prepare_run_time = 0
        self.main_run_time = 0
        self.workload_id = None

        self.account_name = account_name
        cosbench_param_dict = get_config.get_cosbench_param()
        self.cosbench_path = cosbench_param_dict['cosbench_path']
        self.init_base_time = int(cosbench_param_dict['init_base_time'])
        self.prepare_base_time = int(cosbench_param_dict['prepare_base_time'])
        self.main_base_time = int(cosbench_param_dict['main_base_time'])
        self.fault_in_which_stage = cosbench_param_dict['fault_in_which_stage']
        cosbench_client_ip_lst = cosbench_param_dict['cosbench_client_ip_lst']
        self.cosbench_client_ip = cosbench_client_ip_lst[0]
        xml_path_lst = cosbench_param_dict['xml_path_lst']
        self.xml_file_path = xml_path_lst[0]
        self.xml_file_path_no_init = xml_path_lst[1]
        # 获取s3 vip池的域名
        self.s3_domain_name = get_config.get_vip_domain_name()[0]

    @run_func
    def start(self,):
        self.thread_lst = []
        th = threading.Thread(target=self.check_in_loop,
                              args=(self.account_name, ))
        self.thread_lst.append(th)
        self._running_flag = True
        for th in self.thread_lst:
            th.daemon = True
            th.start()

    @run_func
    def stop(self):
        """停止cosbench"""
        self.start_flag = False
        self.cancel_cosbench(self.cosbench_client_ip, self.cosbench_path)

    @run_func
    def is_running(self):
        """返回故障是否在执行"""
        return self._running_flag

    @run_func
    def return_value(self):
        """返回值"""
        return self._return_value

    @run_func
    def check_in_loop(self, account_name):
        cosbench_log.info("********** 运行第一个cosbench ************")
        self.stop_start_cosbench(self.cosbench_path)
        workload_id = self.run_cosbench(self.account_name,
                                        self.xml_file_path,
                                        self.s3_domain_name,
                                        self.cosbench_path)
        self.workload_id = workload_id
        cosbench_log.info('make fault in which stage: %s' % self.fault_in_which_stage)
        '''循环获取当前运行状态'''
        while True:
            cosbench_log.info('IF_MAKE_FAULT: %s' % self.IF_MAKE_FAULT)
            if self.start_flag is False:
                self._running_flag = False
                break
            # 根据workload_id 获取该任务的当前状态
            State, pro_status = self.get_state_by_workid(self.workload_id)
            while True:
                if State == 'PROCESSING' or State == 'QUEUING':
                    cosbench_log.info('cosbench run normal')
                    break
                elif State == 'TERMINATED':
                    cosbench_log.error("workload has terminated")
                    if pro_status == 'init':
                        self._return_value = False
                        cosbench_log.error("cosbench has terminated in init stage!!!")
                        # 需要确认这里要不要退出
                    else:
                        workload_id = self.run_cosbench(account_name,
                                                        self.xml_file_path_no_init,
                                                        self.s3_domain_name,
                                                        self.cosbench_path)
                        self.workload_id = workload_id
                        self.prepare_run_time = 0
                        self.main_run_time = 0
                        break
                else:
                    workload_id = self.run_cosbench(account_name,
                                                    self.xml_file_path_no_init,
                                                    self.s3_domain_name,
                                                    self.cosbench_path)
                    self.workload_id = workload_id
                    self.prepare_run_time = 0
                    self.main_run_time = 0
                    break
                time.sleep(self._intervals)
            if self.fault_in_which_stage == 'prepare':
                self.cosbench_check_prepare(self.workload_id)
            elif self.fault_in_which_stage == 'main':
                self.cosbench_check_main(account_name, workload_id)
            else:
                cosbench_log.error("please check stage name, and input right stage_name!!!")
                self._return_value = False
                raise Exception
            time.sleep(self._intervals)


    @run_func
    def get_active_workloads(self, ip):
        """
         :author:              lichengxu
         :date:                2018.12.11
         :description:         获取正在运行的workloads ID
         :param sk:            (str)ip
         :return:               返回正在运行的workload id列表
         """
        response = None
        ids = []
        try:
            url = 'http://%s:19088/controller/cli/activeworkload.action' % ip
            response = requests.get(url)
        except ValueError as e:
            self._running_flag = False
            print e
        if response:
            data = response.json()
            ActiveWorkloads = data.get('ActiveWorkloads')
            for work in ActiveWorkloads:
                id = work.get('ID')
                ids.append(id)
        return ids

    @run_func
    def stop_start_cosbench(self, cosbench_path):
        """
        :author:                    lichengxu
        :date:                      2018.12.28
        :description:               重新启动cosbench
        :param cosbench_path:       cosbench_path
        :return:
        """
        if os.path.exists(cosbench_path):
            stop_all_path = 'stop-all.sh'
            start_all_path = 'start-all.sh'
            # 直接kill 所有java进程
            cmd1 = 'ps -ef |grep "Dcosbench" | grep -v "grep" | awk \'{print $2}\' | xargs kill -9'
            common.run_command_shot_time(cmd1)
            cosbench_log.info("kill all Cosbench processes!")

            cmd2 = 'cd %s;sh %s' % (cosbench_path, stop_all_path)
            rc, stdout = common.run_command_shot_time(cmd2)
            common.judge_rc(rc, 0, "stop driver failed!")
            cosbench_log.info("stop all success!")

            cmd3 = 'cd %s;sh %s' % (cosbench_path, start_all_path)
            rc, stdout = common.run_command_shot_time(cmd3)
            common.judge_rc(rc, 0, "start driver failed")
            cosbench_log.info("start all success!")

        else:
            cosbench_log.error("we cannot found cosbench path")
            self._running_flag = False
        return

    @run_func
    def run_cosbench(
            self,
            account_name,
            xml_file_path,
            domain_name,
            cosbench_path,
            node_ip=None):
        """
        :author:                    lichengxu
        :date:                      2018.12.11
        :description:               运行cosbench
        :param xml_file_path:       (str)xml_file_path
        :param account_name         account_name
        :param domain_name          domain_name
        :param cosbench_path        cosbench_path
        :return:                    返回执行cosbench 的workloadID
        """
        if os.path.exists(cosbench_path):
            rc, stdout = create_s3_xml.create_s3(
                account_name, xml_file_path, domain_name)
            common.judge_rc(rc, 0, "cmd run failed!")
            cosbench_log.info("cosbench workload run success!")
            # 处理返回值，返回任务ID
            data = stdout.splitlines()
            workload_id = ""
            for line in data:
                if "Accepted" in line:
                    workload_id = line.split()[-1]
            return workload_id
        else:
            cosbench_log.error("please install Cosbench!")
            self._running_flag = False
            raise Exception

    @run_func
    def cancel_cosbench(self, client_ip, cosbench_path, node_ip=None):
        """
        :author:              lichengxu
        :date:                2018.12.20
        :description:         停止cosbench
        :param client_ip:       (str)client_ip
        :param cosbench_path:     (str)cosbench_path
        :node_ip
        :return:
        """
        ids = self.get_active_workloads(client_ip)
        if len(ids) != 0:
            work_id = ids[0]
            if os.path.exists(cosbench_path):
                cli_path = os.path.join(cosbench_path, 'cli.sh')
                cmd = "sh %s cancel %s anonymous:cosbench@127.0.0.1:19088" % (
                    cli_path, work_id)
                cosbench_log.info("cmd: %s" % cmd)
                rc, stdout = common.run_command_shot_time(cmd, node_ip)
                common.judge_rc(rc, 0, "cmd run failed!")
            else:
                cosbench_log.error("cosbench path not exist")
        else:
            cosbench_log.info("there is no active workloads")
        cosbench_log.info("cancel workload success")

    @run_func
    def get_workload_detail_by_id(self, ip, id):
        """
         :author:              lichengxu
         :date:                2018.12.11
         :description:         判断当前运行的任务是否在main阶段
         :param sk:            (str)ip
         :param sk:            (str)ids
         :return:              当前任务状态，任务处于哪个阶段，prepare运行时间，main运行时间
         """
        url = "http://%s:19088/controller/cli/workloaddetails.action?id=%s" % (
            ip, id)
        cosbench_log.info("url: %s" % url)
        response = requests.get(url)
        WorkloadDetails = response.json()
        details = WorkloadDetails.get('WorkLoadDetails')

        StagesInfo = details.get('StagesInfo')
        work_state = details.get("State").encode()

        start_time = details.get('StartedAt').encode()
        start_time = time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S"))

        pro_status = None
        for stage in StagesInfo:
            cosbench_log.info(stage)
            if stage.get('Name') == 'init':
                if stage.get('State') == 'AUTHING':
                    cosbench_log.info("init authing")
                elif stage.get('State') == 'SUBMITTING':
                    cosbench_log.info("init submitting!")
                elif stage.get('State') == 'WAITING':
                    cosbench_log.info("init waiting!")
                elif stage.get('State') == 'LAUNCHED':
                    cosbench_log.info("init launched")
                elif stage.get('State') == 'RUNNING':
                    cosbench_log.info("init running!")
                    self.init_run_time = time.time() - start_time
                    pro_status = stage.get('Name')
                elif stage.get('State') == 'COMPLETED':
                    cosbench_log.info("init completed!")
                elif stage.get('State') == 'FAILED':
                    cosbench_log.error("init stage has failed!!!")
                    self._running_flag = False
                    break
                else:
                    continue

            elif stage.get('Name') == 'prepare':
                if stage.get('State') == 'WAITING':
                    cosbench_log.info("prepare waiting!")
                elif stage.get('State') == 'RUNNING':
                    cosbench_log.info("prepare running!")
                    self.prepare_run_time = time.time() - start_time - self.init_run_time
                    pro_status = stage.get('Name')
                elif stage.get('State') == 'COMPLETED':
                    cosbench_log.info("prepare completed!")
                    continue
                elif stage.get('State') == 'FAILED':
                    cosbench_log.error("prepare stage has failed!!!")
                    break
                else:
                    continue

            elif stage.get('Name') == 'main':
                if stage.get('State') == 'WAITING':
                    cosbench_log.info("main waiting!")
                elif stage.get('State') == 'RUNNING':
                    cosbench_log.info("main running!")
                    self.main_run_time = time.time() - start_time - self.init_run_time - self.prepare_run_time
                    pro_status = stage.get('Name')
                elif stage.get('State') == 'COMPLETED':
                    cosbench_log.info("main completed!")
                    continue
                elif stage.get('State') == 'FAILED':
                    cosbench_log.error("main stage has failed!!!")
                    break
                else:
                    continue

            elif stage.get('Name') == 'cleanup':
                if stage.get('State') == 'WAITING':
                    cosbench_log.info("cleanup waiting!")
                elif stage.get('State') == 'RUNNING':
                    cosbench_log.info("cleanup running!")
                    pro_status = stage.get('Name')
                elif stage.get('State') == 'COMPLETED':
                    cosbench_log.info("cleanup completed!")
                    continue
                else:
                    continue

            elif stage.get('Name') == 'dispose':
                if stage.get('State') == 'WAITING':
                    cosbench_log.info("dispose waiting!")
                elif stage.get('State') == 'RUNNING':
                    cosbench_log.info("dispose running!")
                    pro_status = stage.get('Name')
                elif stage.get('State') == 'COMPLETED':
                    cosbench_log.info("dispose completed!")
                    continue
                else:
                    continue
            else:
                cosbench_log.info("workload has terminated!")
                break

        return work_state, pro_status, self.init_run_time, self.prepare_run_time, self.main_run_time


    def get_state_by_workid(self, workid):
        """
                 :author:              lichengxu
                 :date:                2019.3.20
                 :description:         根据任务id获取该任务的当前状态
                 :param sk:            (str)ip
                 :param sk:            (str)ids
                 :return:              当前任务状态
                 """
        url = "http://%s:19088/controller/cli/workloaddetails.action?id=%s" % (self.cosbench_client_ip,
                                                                               workid)
        cosbench_log.info("url: %s" % url)
        response = requests.get(url)
        WorkloadDetails = response.json()
        details = WorkloadDetails.get('WorkLoadDetails')
        work_state = details.get("State").encode()

        StagesInfo = details.get('StagesInfo')
        pro_state = ''
        for stage in StagesInfo:
            if stage.get('State') == 'TERMINATED':
                pro_state = stage.get('Name')
        return work_state, pro_state


    @run_func
    def cosbench_check_prepare(self, workload_id):
        '''
        : cosbench 运行结果循环检测，并判断是否开始/结束故障
        :param account_name:
        :return:
        '''
        '''检测cosbench当前运行状态，并获取返回值'''
        work_state, pro_status, init_run_time, prepare_run_time, main_run_time = \
            self.get_workload_detail_by_id(self.cosbench_client_ip, workload_id)
        cosbench_log.info("result: %s, %s, %s, %s " %
            (work_state, init_run_time, prepare_run_time, main_run_time))
        '''根据返回值，判断cosbench是否开启下一轮故障'''
        if (pro_status == 'prepare') and (
                prepare_run_time < self.prepare_base_time):
            cosbench_log.info("work is in prepare stage, please start fault")
            self.IF_MAKE_FAULT = True
        elif (pro_status == 'main') and (main_run_time < self.main_base_time):
            cosbench_log.info(" work is in main stage...")
            self.IF_MAKE_FAULT = True
        elif (init_run_time > self.init_base_time) or \
                (prepare_run_time > self.prepare_base_time) or \
                (main_run_time > self.main_base_time):
            self._return_value = False
        time.sleep(self._intervals)
        return


    @run_func
    def cosbench_check_main(self, account_name, workload_id):
        '''
        : cosbench 运行结果循环检测，并判断是否开始/结束故障
        :param account_name:
        :return:
        '''
        '''检测cosbench当前运行状态，并获取返回值'''
        work_state, pro_status, init_run_time, prepare_run_time, main_run_time = \
            self.get_workload_detail_by_id(self.cosbench_client_ip, workload_id)
        cosbench_log.info("result: %s, %s, %s, %s " %
                          (work_state, init_run_time, prepare_run_time, main_run_time))
        '''根据返回值，判断cosbench是否开启下一轮故障'''
        if (pro_status == 'prepare') and (
                prepare_run_time < self.prepare_base_time):
            cosbench_log.info("work is in prepare stage...")
        elif (pro_status == 'main') and (main_run_time < self.main_base_time):
            cosbench_log.info(" work is in main stage, please start fault")
            self.IF_MAKE_FAULT = True
        elif (init_run_time > self.init_base_time) or \
                (prepare_run_time > self.prepare_base_time) or \
                (main_run_time > self.main_base_time):
            self._return_value = False
        time.sleep(self._intervals)
        return


@run_func
def main():
    case_log_path = '/home/StorTest/test_cases/log/case_log'
    log_init_cosbench(case_log_path)

    aaa = CosbenchTest(case_log_path, 'test')
    aaa.start()

    for i in range(20):
        cosbench_log.info("running flag: %s" % aaa.is_running())
        time.sleep(30)
    aaa.stop()

    while True:
        cosbench_log.info("running flag: %s" % aaa.is_running())
        time.sleep(30)

if __name__ == '__main__':
    main()

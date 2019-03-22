#!/usr/bin/python
# -*- encoding=utf8 -*-

"""
author:      baoruobing
date:        2019.02.21
description: jenkins下发测试
"""

import os
import sys

import utils_path
import get_config
import common
import log


class Jenkins_test(object):
    tar_path = "/home/StorTest/src_code/P300"
    SYSTEM_IP_0 = get_config.get_parastor_ip(0)

    def __init__(self):
        self.user_name = sys.argv[1]
        self.reinstall = sys.argv[2]
        self.test_case_list_file = sys.argv[3]
        self.test_list_parameter = sys.argv[4]
        self.parastor_path = sys.argv[5]
        self.develop_list_dir = sys.argv[6]
        self.develop_list_str = sys.argv[7]
        self.jenkins_ip = get_config.get_jenkins_ip(get_config.CONFIG_FILE)
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.stortest_path = os.path.dirname(self.current_path)
        self.test_case_path = os.path.join(self.stortest_path, 'test_cases', 'cases', 'test_case')
        self.case_list_path = os.path.join(self.stortest_path, 'test_cases', 'cases', 'case_list')
        self.develop_list_path = os.path.join(self.test_case_path, 'develop', 'develop_scripts')
        self.develop_new_path = os.path.join(self.test_case_path, 'develop', 'develop_new')
        self.develop_example_path = os.path.join(self.stortest_path, 'jenkins', 'developer_standard_example.py')
        self.run_all_test_path = os.path.join(self.stortest_path, 'scripts', 'run_all_tests_p300.py')
        self.auto_install_path = os.path.join(self.stortest_path, 'scripts', 'P300_AutoInstall.py')

    def create_develop_file(self):
        exe_path = '/home/develop_jenkins_test'
        exe_list = []

        # 拷贝到指定集群节点
        cmd = "mkdir -p %s;rm -rf %s" % (exe_path, exe_path + "/*")
        common.run_command_shot_time(cmd, Jenkins_test.SYSTEM_IP_0)
        cmd = 'scp %s %s:%s' % (self.develop_list_path + "/*", Jenkins_test.SYSTEM_IP_0, exe_path)
        common.run_command_shot_time(cmd)

        fd = open(self.develop_list_path + '/list', 'r')

        for line in fd:
            exe_list.append(line.strip('\n').strip('\r'))
        fd.close()

        cmd = 'mkdir -p %s;rm -rf %s' % (self.develop_new_path, self.develop_new_path + '/*')
        common.run_command_shot_time(cmd)

        for exe_name in exe_list:
            fd_example = open(self.develop_example_path, 'r')
            fd = open(os.path.join(self.develop_new_path, exe_name.split(".")[0] + ".py"), 'w')

            for line in fd_example:
                if "path = \"\"" in line:
                    line = line.replace("path = \"\"", "path = \"%s\"" % os.path.join(exe_path, exe_name))
                fd.write(line)

            fd_example.close()
            fd.close()

            cmd = 'chmod +x %s' % (os.path.join(self.develop_new_path, exe_name.split(".")[0] + ".py"))
            common.run_command_shot_time(cmd)

        cmd = 'ls %s' % self.develop_new_path
        rc, stdout = common.run_command_shot_time(cmd)
        self.develop_list_str = ','.join(stdout.strip().split())

        web_utils_path = os.path.join(self.test_case_path, "P300", "WEB", "utils_path.py")
        cmd = 'cp %s %s' % (web_utils_path, self.develop_new_path)
        common.run_command_shot_time(cmd)
        return

    def check_list(self):
        if self.develop_list_str == "None" and self.test_case_list_file == "None":
            raise Exception("please choice test_case_list or input your own use case list")

    def reinstall_parastor(self):
        if self.reinstall == "compile_and_install" or self.reinstall == "install_only":
            log.info("start reinstall")
            jenkins_ip = get_config.get_jenkins_ip(get_config.CONFIG_FILE)
            cmd_rm = 'rm -rf %s' % os.path.join(Jenkins_test.tar_path, '*')
            common.run_command_shot_time(cmd_rm)
            cmd_scp = 'scp %s:%s %s' % (jenkins_ip, self.parastor_path, Jenkins_test.tar_path)
            rc, stdout = common.run_command_shot_time(cmd_scp)
            common.judge_rc(rc, 0, "scp tar parastor error")
            if 's3'in self.test_case_list_file:
                cmd = "python -u %s %s" % (self.auto_install_path, 's3')
            else:
                cmd = "python -u %s" % self.auto_install_path
            log.info(cmd)
            rc = os.system(cmd)
            common.judge_rc(rc, 0, "run all test error")
        return

    def run_all_test(self):
        jenkins_case_list = get_config.get_caselist_file()
        with open(jenkins_case_list, 'w') as fd:
            if self.develop_list_str != "None":
                cmd = 'mkdir -p %s' % self.develop_list_path
                common.run_command_shot_time(cmd)
                cmd = 'rm -rf %s;scp %s:%s %s' % (
                    self.develop_list_path + '/*', self.jenkins_ip, self.develop_list_dir + '/*/*', self.develop_list_path)
                common.run_command_shot_time(cmd)

                self.create_develop_file()

                for develop in self.develop_list_str.split(','):
                    develop_path = os.path.join(self.develop_new_path, develop)
                    fd.write(develop_path)
                    fd.write("\n")
            if self.test_case_list_file != "None":
                test_case_list_path = os.path.join(self.case_list_path, self.test_case_list_file)
                fd.write(open(test_case_list_path, 'r').read())

            fd.close()

            if self.test_list_parameter == "None":
                self.test_list_parameter = ""
            else:
                self.test_list_parameter = ' '.join(self.test_list_parameter.split(','))
            cmd = "python -u %s %s" % (self.run_all_test_path, self.test_list_parameter)
            log.info(cmd)
            rc = os.system(cmd)
            common.judge_rc(rc, 0, "run all test error")
        return

def run_test():
    """
    运行测试
    """
    obj_jenkins_test = Jenkins_test()

    """检查用例列表是否为空"""
    obj_jenkins_test.check_list()

    """是否需要重装环境"""
    obj_jenkins_test.reinstall_parastor()

    """调用run_all_tests_p300"""
    obj_jenkins_test.run_all_test()


if __name__ == '__main__':
    file_name = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
    log_file_path = log.get_log_path(file_name)
    log.init(log_file_path, True)
    run_test()
#!/usr/bin/python
# -*- encoding=utf8 -*-

import re
import os
import time
from optparse import OptionParser

import utils_path
import log
import common
import tool_use
import get_config
import collect_log


def arg_analysis():
    parser = OptionParser()
    parser.add_option("-l", "--loop",
                      type="int",
                      dest="loop",
                      default=1,
                      help="When you want to loop run the case, configure this parameter. "
                           "default: %default, rang is 1-1000")

    parser.add_option("-c", "--continue",
                      action="store_true",
                      dest="con",
                      help="If you want to continue to run test when the case failed, configure this parameter")

    parser.add_option("-u", "--upgrade",
                      action="store_true",
                      dest="upgrade",
                      help="If you want to automatically upgrade when testing, configure this parameter")

    parser.add_option("-F", "--failed",
                      action="store_true",
                      dest="failed",
                      help="If you only want to run the failed or never executed case, configure this parameter")

    parser.add_option("-s", "--scp_log",
                      action="store_true",
                      dest="scp_log",
                      help="If you want to automatic copy log, configure this parameter")

    parser.add_option("-W", "--windows",
                      action='store_true',
                      dest='iswindows',
                      help="specify vdbench slave is windows")

    options, args = parser.parse_args()
    if options.loop < 1 or options.loop > 1000:
        parser.error("the range of -l or --loop is 1-1000")
    loopnum = options.loop

    if options.con is True:
        continueflag = True
    else:
        continueflag = False

    if options.upgrade is True:
        upgradeflag = True
    else:
        upgradeflag = False

    if options.failed:
        failedflag = True
    else:
        failedflag = False

    if options.scp_log:
        scplogflag = True
    else:
        scplogflag = False

    if options.iswindows:
        iswindows = True
    else:
        iswindows = False

    return loopnum, continueflag, upgradeflag, failedflag, scplogflag, iswindows


class Run_Test(object):
    runtime_len = 25
    test_file_len = 70
    case_result_len = 20
    time_str_len = 20

    def __init__(self):
        # /StorTest/scripts
        current_path = os.path.dirname(os.path.abspath(__file__))
        # /StorTest/
        stortest_path = os.path.dirname(current_path)
        self.test_case_path = os.path.join(stortest_path, 'test_cases', 'cases', 'test_case')
        """获取参数"""
        self.loopnum, self.continueflag, self.upgradeflag, self.failedflag, self.scplogflag, self.iswindows = arg_analysis()
        self.parastor_ip_lst = get_config.get_allparastor_ips()
        self.client_ip_lst = get_config.get_allclient_ip()
        self.test_result_dir = get_config.get_testresult_path()
        self.test_log_dir = get_config.get_testlog_path()

    def run_tests(self):
        """
        运行
        """
        result_info_dic = {'success_num': 0, 'failed_num': 0, 'skip_num': 0}
        """创建文件"""
        result_file = self.create_result_file()
        """result文件概览"""
        self.write_result_overview(result_file, result_info_dic)
        """result文件写上标头"""
        self.write_result_header(result_file)
        """获取用例列表"""
        tests_file_lst = self.get_test_file_lst()
        stop_flag = False
        for i in range(self.loopnum):
            if stop_flag:
                break
            for test_index, mem in enumerate(tests_file_lst):
                """先检查是否需要升级"""
                self.upgrade(result_file, result_info_dic)

                case_list_file = mem[0]
                num = mem[1]
                test_file = mem[2]
                test_file_path = os.path.join(self.test_case_path, test_file)
                """检查脚本是否存在"""
                if not self.check_testfile_exist(case_list_file, num, test_file_path):
                    continue
                """执行脚本"""
                next_case = self.get_next_lst_case(tests_file_lst, mem)
                result = self.run_one_test(result_file, test_file_path, result_info_dic)
                """更新概览"""
                self.write_result_overview(result_file, result_info_dic)
                if result == -1 and self.continueflag is False:
                    stop_flag = True
                    break
                if result == -1 and self.scplogflag:
                    """重装环境"""
                    current_path = os.path.dirname(os.path.abspath(__file__))
                    install_script = os.path.join(current_path, 'P300_AutoInstall.py')
                    if next_case and os.path.basename(next_case).startswith('29-'):
                        """重装环境"""
                        cmd = "python -u %s s3" % install_script
                        status = os.system(cmd)
                        if status != 0:
                            log.error('P300_AutoInstall.py failed!!!')
                            raise Exception('P300_AutoInstall.py failed!!!')
                        ready_s3_script = os.path.join(self.test_case_path, 'P300', '29-0-0-0', 'ready_s3.py')
                        cmd = "python -u %s" % ready_s3_script
                        status = os.system(cmd)
                        if status != 0:
                            log.error('ready_s3.py failed!!!')
                            raise Exception('ready_s3.py failed!!!')
                    else:
                        cmd = "python -u %s" % install_script
                        status = os.system(cmd)
                        if status != 0:
                            log.error('P300_AutoInstall.py failed!!!')
                            raise Exception('P300_AutoInstall.py failed!!!')

        with open(result_file, 'r') as f:
            print_str = f.read()
        print "\n******************** 执行结果 ********************\n"
        print print_str

    def create_result_file(self):
        """
        创建result文件
        """
        '''获取当前时间'''
        now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        file_name = now_time + '_test_result.txt'
        result_file = os.path.join(self.test_result_dir, file_name)
        f = open(result_file, 'w')
        f.close()
        return result_file

    def write_result_header(self, result_file):

        str0 = 'execution time'.ljust(self.runtime_len + 4)
        str1 = 'case'.ljust(self.test_file_len + 2)
        str2 = 'result'.ljust(self.case_result_len + 2)
        str3 = 'length of time'.ljust(self.time_str_len + 2)
        str4 = 'core\n'
        input_str = [str0, str1, str2, str3, str4]
        with open(result_file, 'a+') as data:
            data.write('\n')
            data.writelines(input_str)

    @staticmethod
    def write_result_overview(result_file, result_info_dic):
        success_num = result_info_dic['success_num']
        failed_num = result_info_dic['failed_num']
        skip_num = result_info_dic['skip_num']
        with open(result_file, "r+") as f:
            f.seek(0, 0)
            f.write("#################### Overview ####################" + "\n")
            f.write("total: {}\n".format(int(success_num + failed_num + skip_num)))
            f.write("pass: {}\n".format(int(success_num)))
            f.write("failed: {}\n".format(int(failed_num)))
            f.write("skipped: {}\n".format(int(skip_num)))

    @staticmethod
    def get_test_file_lst():
        """
        获取要运行的用例列表
        """
        case_list_file = get_config.get_caselist_file()
        tests_file_lst = get_config.get_case_list(case_list_file)
        return tests_file_lst

    @staticmethod
    def check_testfile_exist(case_list_file, num, test_file_path):
        """
        检查测试脚本是否存在
        """
        """检查文件是否存在"""
        if not os.path.exists(test_file_path):
            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            print ("The %s line:%s, %s is not exist!!!" % (case_list_file, num, test_file_path))
            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            return False
        else:
            return True

    def result_to_file(self, result_file, resultfile_time, test_file, case_result, run_time, core_file_dic):
        """
        在result文件中记录脚本结果
        """
        print ("-------- %s %s!!! --------" % (test_file, case_result))
        runtimestr = resultfile_time.ljust(self.runtime_len)
        str1_tmp = test_file.ljust(self.test_file_len)
        str2_tmp = case_result.ljust(self.case_result_len)

        m, s = divmod(run_time, 60)
        h, m = divmod(m, 60)
        time_str = "%dh:%dm:%ds" % (h, m, s)

        if core_file_dic:
            print 'core info: %s' % str(core_file_dic)
            str3_tmp = time_str.ljust(self.time_str_len)
            str4_tmp = str(core_file_dic) + '\n'
            input_str = [runtimestr, str1_tmp, str2_tmp, str3_tmp, str4_tmp]
        else:
            str3_tmp = time_str + '\n'
            input_str = [runtimestr, str1_tmp, str2_tmp, str3_tmp]
        with open(result_file, 'a') as data:
            data.writelines(input_str)

    def run_one_test(self, result_file, test_file_path, result_info_dic):
        """
        运行单个用例
        """
        log.info("\n------------ start running %s ------------" % test_file_path)
        start_time = time.time()
        resultfile_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
        """获取core info"""
        core_file_pre_dic = common.get_corefile_info()
        """获取crash info"""
        crash_info_pre_dic = self.get_crash_info()
        if self.failedflag:
            if self.iswindows:
                status = os.system("python -u %s -F -W %s" % (test_file_path, self.iswindows))
            else:
                status = os.system("python -u %s -F" % test_file_path)
        else:
            if self.iswindows:
                status = os.system("python -u %s -W %s" % (test_file_path, self.iswindows))
            else:
                status = os.system("python -u " + test_file_path)
        status = status >> 8
        end_time = time.time()
        run_time = int(end_time - start_time)
        core_file_after_dic = common.get_corefile_info()
        test_file = os.path.basename(test_file_path)
        crash_info_last_dic = self.get_crash_info()
        if ((0 != status and status != 255) or (core_file_pre_dic != core_file_after_dic) or
                (crash_info_pre_dic != crash_info_last_dic)):
            self.result_to_file(result_file, resultfile_time, test_file, 'Failed', run_time, core_file_after_dic)
            result_info_dic['failed_num'] += 1
            """判断是否上传结果到testlink"""
            if get_config.get_tl():
                tool_use.report_tl_case_result(test_file_path, 'f', run_time, notes='script: %s' % test_file)

            if self.scplogflag:
                """拷贝日志"""
                self.cp_log(test_file, crash_info_pre_dic, crash_info_last_dic)
            return -1
        elif 255 == status:
            self.result_to_file(result_file, resultfile_time, test_file, 'Skipped', run_time, core_file_after_dic)
            result_info_dic['skip_num'] += 1
            return 1
        else:
            self.result_to_file(result_file, resultfile_time, test_file, 'Success', run_time, core_file_after_dic)
            result_info_dic['success_num'] += 1
            """判断是否上传结果到testlink"""
            if get_config.get_tl():
                tool_use.report_tl_case_result(test_file_path, 'p', run_time, notes='script: %s' % test_file)
            return 0

    def upgrade(self, result_file, result_info_dic):
        """
        升级版本
        """
        """检查是否需要升级"""
        if not self.upgradeflag:
            return
        if not self.check_upgrade():
            print "No need to upgrade"
            return
        print "Need to upgrade"
        """升级"""
        # /home/StorTest/Scripts
        scripts_path = os.path.dirname(os.path.abspath(__file__))
        test_file_path = os.path.join(scripts_path, 'P300_AutoUpgrade.py')
        result = self.run_one_test(result_file, test_file_path, result_info_dic)
        if result == -1:
            print "upgrade failed!!!"
            return
        """执行升级后要执行的用例"""
        self.run_upgrade_test(result_file, result_info_dic)

    def check_upgrade(self):
        """
        检查是否需要升级
        """
        """获取当前版本"""
        rc, package_time = self.get_package_time()
        if rc != 0:
            return False
        """获取发包目录的最新包"""
        rc, new_package_time = self.get_new_package()
        if rc != 0:
            return False
        if new_package_time <= package_time:
            return False
        else:
            return True

    @staticmethod
    def get_package_time():
        """
        获取当前版本
        """
        rc, stdout = common.get_package_time()
        if rc != 0:
            return rc, None
        else:
            json_info = common.json_loads(stdout)
            return rc, json_info['result']['package_time']

    @staticmethod
    def get_new_package():
        """
        获取最新包的版本
        """
        package_ip = get_config.get_new_pkg_position().split(':')[0]
        newpackage_path = get_config.get_new_pkg_position().split(':')[1]
        package_lst = []
        cmd = 'ls -Ft %s | grep "/$"' % newpackage_path
        rc, stdout = common.run_command_shot_time(cmd, package_ip, print_flag=False)
        for line in stdout.splitlines():
            line = line.strip().strip('/')
            if re.match('\d{8}', line):
                package_lst.append(line)
        package_lst.sort(reverse=True)
        for package in package_lst:
            path = os.path.join(newpackage_path, package)
            pkg_match_name = 'ParaStor-3.0.0-centos7.5-feature_ofs3.0_lastdebug_*-2-1.tar'
            cmd = 'ls %s' % os.path.join(path, pkg_match_name)
            rc, stdout = common.run_command_shot_time(cmd, package_ip, print_flag=False)
            if rc != 0:
                continue
            line = stdout.strip()
            package_time = re.findall('\d{8}_\d{6}', line)[0]
            return 0, package_time
        return 1, None

    @staticmethod
    def get_upgrade_test_lst():
        """
        获取要运行的用例列表
        """
        upgrade_case_list_file = get_config.get_upgrade_case_file()
        upgrade_tests_file_lst = get_config.get_case_list(upgrade_case_list_file)
        return upgrade_tests_file_lst

    def run_upgrade_test(self, result_file, result_info_dic):
        """
        运行升级后需要跑的用例
        """
        upgrade_tests_file_lst = self.get_upgrade_test_lst()
        for test_index, mem in enumerate(upgrade_tests_file_lst):
            case_list_file = mem[0]
            num = mem[1]
            test_file = mem[2]
            test_file_path = os.path.join(self.test_case_path, test_file)
            """检查脚本是否存在"""
            if not self.check_testfile_exist(case_list_file, num, test_file_path):
                continue
            """执行脚本"""
            next_case = self.get_next_lst_case(upgrade_tests_file_lst, mem)
            result = self.run_one_test(result_file, test_file_path, result_info_dic)
            """更新概览"""
            self.write_result_overview(result_file, result_info_dic)
            if result == -1 and self.continueflag is False:
                break
            if result == -1 and self.scplogflag:
                """重装环境"""
                current_path = os.path.dirname(os.path.abspath(__file__))
                install_script = os.path.join(current_path, 'P300_AutoInstall.py')
                if next_case and os.path.basename(next_case).startswith('29-'):
                    """重装环境"""
                    cmd = "python -u %s s3" % install_script
                    status = os.system(cmd)
                    if status != 0:
                        log.error('P300_AutoInstall.py failed!!!')
                        raise Exception('P300_AutoInstall.py failed!!!')
                    ready_s3_script = os.path.join(self.test_case_path, 'P300', '29-0-0-0', 'ready_s3.py')
                    cmd = "python -u %s" % ready_s3_script
                    status = os.system(cmd)
                    if status != 0:
                        log.error('ready_s3.py failed!!!')
                        raise Exception('ready_s3.py failed!!!')
                else:
                    cmd = "python -u %s" % install_script
                    status = os.system(cmd)
                    if status != 0:
                        log.error('P300_AutoInstall.py failed!!!')
                        raise Exception('P300_AutoInstall.py failed!!!')


    def get_crash_info(self):
        """
        获取crash信息
        """
        cmd = "ls /var/crash/ | grep - | grep :"
        node_lst = self.parastor_ip_lst + self.client_ip_lst
        crash_info_dic = {}
        for node_ip in node_lst:
            rc, stdout = common.run_command_shot_time(cmd, node_ip, print_flag=False)
            if rc == 0:
                crash_lst = stdout.split()
                crash_info_dic[node_ip] = crash_lst
            else:
                crash_info_dic[node_ip] = []
        return crash_info_dic

    def cp_log(self, test_file, crash_info_pre_dic, crash_info_last_dic):
        """
        拷贝日志
        """
        """判断是否有新的crash"""
        if crash_info_pre_dic == crash_info_last_dic:
            crash_dic = None
        else:
            crash_dic = {}
            for key in crash_info_pre_dic:
                crash_dic[key] = list(set(crash_info_pre_dic[key]) ^ set(crash_info_last_dic[key]))

        test_file = os.path.splitext(test_file)[0]

        log_file_lst = os.listdir(self.test_log_dir)
        log_file_lst.sort(reverse=True)
        test_log_lst = None
        for test_log_file in log_file_lst:
            if test_file in test_log_file:
                test_log_lst = [os.path.join(self.test_log_dir, test_log_file)]
                break

        obj_col_log = collect_log.Collect_log(node_ip_lst=self.parastor_ip_lst, client_ip_lst=self.client_ip_lst,
                                              crash_dic=crash_dic, log_name=test_file, test_log_lst=test_log_lst)
        obj_col_log.begin_collect_log()

    @staticmethod
    def get_next_lst_case(lst, new_mem):
        """获取列表下一个元素"""
        new_mem_index = lst.index(new_mem)
        if new_mem_index == len(lst) - 1:
            return None
        else:
            return lst[new_mem_index+1][2]


if __name__ == '__main__':
    file_name = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
    log_file_path = log.get_log_path(file_name)
    log.init(log_file_path, True)
    obj_run_test = Run_Test()
    obj_run_test.run_tests()
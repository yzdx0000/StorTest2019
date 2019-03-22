#!/usr/bin/python
# -*- encoding=utf8 -*-

import os
import sys
import commands
import time
import threading
from optparse import OptionParser

sys.path.append('/home/StorTest/test_cases/libs')

import daemon_pro
import get_config
import common
import collect_log
import common2
import re
import ReliableTest
import breakdown

global LOOPFLAG
global CONTINUEFLAG
global STOPCORE

osan = common2.oSan()
common_node = common.Node()
os_rel = breakdown.Os_Reliable()
# /home/StorTest/Scripts
scripts_path = os.path.dirname(os.path.abspath(__file__))
# /home/StorTest
stortest_path = os.path.dirname(scripts_path)
# /home/StorTest/test_cases/cases/test_case
TEST_CASE_PATH = os.path.join(stortest_path, 'test_cases', 'cases', 'test_case')
conf_file = common2.CONF_FILE
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
err_log_ip = collect_log.get_err_log_ip()
err_log_path = collect_log.get_err_log_path()
# 获取集群内节点的IPMI IP 或者 vmid
m_info = daemon_pro.get_machine_info()
print m_info
##############################################################################
# ##name  :      check_path_exist
# ##parameter:   path:文件路径
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 检查文件路径是否存在
##############################################################################


def check_path_exist(path):
    rc, msg = commands.getstatusoutput("ls %s" % (path, ))
    if 0 == rc:
        return True
    else:
        return False


def result_to_file(test_file, abs_result_file, case_result, run_time):
    """
    name  :   result_to_file
    :param    test_file: 脚本名字
    :param    abs_result_file: 完整的result名字
    :param    case_result: 脚本运行的结果，Failed or Success
    author:   baoruobing
    :return:  是否有core, True是有core，False是没有core
    """
    print("%s %s!!!" % (test_file, case_result))
    core_flag = False

    str1_tmp = test_file.ljust(50)
    str2_tmp = case_result.ljust(20)

    m, s = divmod(run_time, 60)
    h, m = divmod(m, 60)
    time_str = "%dh:%dm:%ds" % (h, m, s)
    '''检查是否环境是否有core'''
    core_file_dic = common.get_corefile_info()
    if core_file_dic:
        print 'core info: %s' % str(core_file_dic)
        core_flag = True
        str3_tmp = time_str.ljust(20)
        str4_tmp = str(core_file_dic) + '\n'
        input_str = [str1_tmp, str2_tmp, str3_tmp, str4_tmp]
    else:
        str3_tmp = time_str + '\n'
        input_str = [str1_tmp, str2_tmp, str3_tmp]
    with open(abs_result_file, 'a') as data:
        data.writelines(input_str)

    return core_flag


def arg_analysis():
    global LOOPFLAG
    global CONTINUEFLAG
    global STOPCORE

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
                      default=False,
                      help="If you want to continue to run test when the case failed, configure this parameter")

    parser.add_option("-s", "--stop",
                      action="store_true",
                      dest="stop_core",
                      help="If you want to stop to run test when the core exist, configure this parameter")

    options, args = parser.parse_args()
    if options.loop < 1 or options.loop > 1000:
        parser.error("the range of -l or --loop is 1-1000")
    LOOPFLAG = options.loop

    if options.con is True:
        CONTINUEFLAG = True
    else:
        CONTINUEFLAG = False

    if options.stop_core is True:
        STOPCORE = True
    else:
        STOPCORE = False

    return


def check_case_timeout(testcase, timeout_file_list):
    testcase = re.sub('^/', '', testcase)
    if False is check_path_exist(timeout_file_list):
        return
    else:
        cmd = ('grep %s %s' % (testcase, timeout_file_list))
        res, output = commands.getstatusoutput(cmd)
        if res == 0:
            return True
        else:
            return False


def run_tests():
    global LOOPFLAG
    global CONTINUEFLAG
    global STOPCORE
    ENV_INSTALL = False
    RE_INSTALL = False
    # 获取所有节点ID
    data_ips = {}
    for c_ip in deploy_ips:
        n_id = common_node.get_node_id_by_ip(c_ip)
        data_ip = ReliableTest.get_data_ips(node_ip=c_ip, node_id=n_id)
        data_ips[c_ip] = ReliableTest.get_eth(node_ip=c_ip, test_ip=data_ip)
    # 获取脚本执行结果的存放路径
    test_result_dir = get_config.get_testresult_path()
    # 创建执行结果文件
    '''获取当前时间'''
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    file_name = now_time + '_test_result.txt'
    str1 = '用例'.ljust(52)
    str2 = '结果'.ljust(22)
    str3 = '时间'.ljust(22)
    str4 = 'core\n'
    input_str = [str1, str2, str3, str4]
    abs_result_file = os.path.join(test_result_dir, file_name)
    with open(abs_result_file, 'w') as data:
        data.writelines(input_str)
    # 获取用例列表文件
    case_list_file = get_config.get_caselist_file()
    case_list_path = os.path.dirname(os.path.abspath(case_list_file))
    timeout_caselist = case_list_path + '/timeout_list'
    test_files = get_config.get_case_list(case_list_file)
    core_flag = False
    core_stop_flag = False
    # 测试结果统计
    success = 0
    failed = 0
    skip = 0
    # 自动部署命令
    install_cmd1 = ("python -u %s/Auto_install.py" % (scripts_path, ))
    install_cmd2 = ("python -u /home/StorTest/test_cases/cases/test_case/X1000"
                    "/lun_manager/env_manage_lun_manage.py")
    install_cmd3 = ("python -u /home/StorTest/test_cases/cases/test_case/X1000/"
                    "repair_test/env_manage_repair_test.py")
    install_cmd = install_cmd1
    for i in range(LOOPFLAG):
        crash_flag = False
        '''检查是否触发了core退出的标志'''
        if core_stop_flag is True:
            break
        file_num = 0
        for mem in test_files:
            '''检查有core是否退出'''
            if STOPCORE is True and core_flag is True:
                core_stop_flag = True
                break
            case_list_file = mem[0]
            num = mem[1]
            test_file = mem[2]
            # 预读下一个要执行的case
            file_num += 1
            check_file = test_file
            if test_file != test_files[-1][2]:
                check_file = test_files[file_num][2]
            # 如果是卷管理类的脚本，则执行env_manage_lun_manage.py
            if re.findall(r'/2-0[1-8]', check_file):
                install_cmd = install_cmd2
            elif re.findall(r'/4-', check_file):
                install_cmd = install_cmd3
            # 非卷管理类的脚本则执行Auto_install.py
            else:
                install_cmd = install_cmd1
            # 如果当前case: test_file和下一个case: check_file都是2-0开头的，则不重装
            if re.findall(r'/2-', test_file) and re.findall(r'/2-', check_file):
                RE_INSTALL = False
            # 如果当前case和下一个case都是3-开头，则不重装
            elif re.findall(r'/3-', test_file) and re.findall(r'/3-', check_file):
                RE_INSTALL = False
            # 如果当前case和下一个case都是4-开头，则不重装
            elif re.findall(r'/4-', test_file) and re.findall(r'/4-', check_file):
                RE_INSTALL = False
            # 如果当前case和下一个case都是1-开头，则不重装
            elif re.findall(r'/1-', test_file) and re.findall(r'/1-', check_file):
                RE_INSTALL = False
            # 其他情况
            else:
                RE_INSTALL = True
            change_file = case_list_path + '/' + case_list_file
            test_file_path = TEST_CASE_PATH + '/' + test_file
            # 检查文件是否存在，不存在则读取下一行
            result = check_path_exist(test_file_path)
            if result is False:
                print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                print("The %s line:%s, %s is not exist!!!" % (case_list_file, num, test_file_path))
                print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                continue

            print "\n------------ start running %s ------------" % test_file
            crash_dict = {}
            crash_dict_new = {}
            crash_list = {}
            for d_ip in deploy_ips:
                cmd = ("ssh root@%s 'ls /var/crash'" % (d_ip,))
                res, output = commands.getstatusoutput(cmd)
                crash_dict[d_ip] = output.split()
            start_time = time.time()
            if True is check_case_timeout(test_file, timeout_caselist):
                daemon_thread = threading.Thread(target=daemon_pro.pro_kill, args=(test_file, 4800))
            else:
                daemon_thread = threading.Thread(target=daemon_pro.pro_kill, args=(test_file, 2400))
            # 启动监控线程，当前执行的脚本运行超过40min后，主动将其杀掉，运行下一个case
            # daemon_thread = threading.Thread(target=daemon_pro.pro_kill, args=(test_file, 2400))
            daemon_thread.setDaemon(True)
            daemon_thread.start()
            # 清理客户端的vdbench log
            for cip in client_ips:
                cmd = ("ssh root@%s 'rm -rf /root/output/*'" % (cip,))
                commands.getstatusoutput(cmd)
            # 执行测试脚本
            status = os.system("python -u " + test_file_path)
            # 等待监控子线程退出
            daemon_thread.join()
            end_time = time.time()
            run_time = int(end_time - start_time)
            # 杀掉所有客户端残留的vdbench进程
            for ip in client_ips:
                cmd = ("ssh root@%s 'killall vdbench'" % (ip, ))
                commands.getstatusoutput(cmd)
            # 检查所有节点管理IP是否能连通，不通的就强制重启
            daemon_pro.restart_node(m_info)
            for ip in deploy_ips:
                cmd = ("ssh %s 'hostname'" % (ip, ))
                print cmd
                rc, stdout = commands.getstatusoutput(cmd)
                while rc != 0:
                    time.sleep(10)
                    rc, stdout = commands.getstatusoutput(cmd)
            # 重启所有节点数据网
            for c_ip in data_ips.keys():
                for d_ip in data_ips[c_ip]:
                    cmd = ("ssh %s 'ifup %s'" % (c_ip, d_ip))
                    commands.getstatusoutput(cmd)
            # 检查是否有core
            for ip in deploy_ips:
                cmd1 = ("ssh root@%s 'ls /core.* 2> /dev/null'" % (ip, ))
                cmd2 = ("ssh root@%s 'ls /home/parastor/log/core.* 2> /dev/null'" % (ip, ))
                rc1, stdout1 = commands.getstatusoutput(cmd1)
                rc2, stdout2 = commands.getstatusoutput(cmd2)
                if rc1 == 0 or rc2 == 0:
                    core_flag = True
                    break
                else:
                    core_flag = False
            # 检查是否新增crash
            for d_ip in deploy_ips:
                cmd = ("ssh root@%s 'ls /var/crash'" % (d_ip,))
                res, output = commands.getstatusoutput(cmd)
                crash_dict_new[d_ip] = output.split()
                new_crash = list(set(crash_dict_new[d_ip]).difference(set(crash_dict[d_ip])))
                if len(new_crash) > 0:
                    crash_list[d_ip] = new_crash
                    for c_file in new_crash:
                        cmd = ("ssh root@%s 'cp /home/parastor/tools/client/knal*ko /var/crash/%s'" % (d_ip, c_file))
                        commands.getstatusoutput(cmd)
                    crash_flag = True
            # 判断脚本执行结果
            if 65280 == status and core_flag is False and crash_flag is False:
                core_flag = result_to_file(test_file, abs_result_file, 'Skipped', run_time)
                skip += 1
                # 注释掉跳过的用例，设置标志skip
                cmd = ("sed -r -i '%ss/^/#skip__/' %s" % (str(num), change_file))
                commands.getstatusoutput(cmd)
                if RE_INSTALL is True:
                    res, output = commands.getstatusoutput(install_cmd)
                    if res != 0:
                        res, output = commands.getstatusoutput(install_cmd)
                        if res != 0:
                            print output
                            exit(1)
                    os_rel.asyn_ntp()
            elif status == 0 and core_flag is False and crash_flag is False:
                core_flag = result_to_file(test_file, abs_result_file, 'Successed', run_time)
                success += 1
                # 注释掉成功的用例，并打标志suc
                cmd = ("sed -r -i '%ss/^/#suc__/' %s" % (str(num), change_file))
                commands.getstatusoutput(cmd)
                if RE_INSTALL is True:
                    res, output = commands.getstatusoutput(install_cmd)
                    if res != 0:
                        res, output = commands.getstatusoutput(install_cmd)
                        if res != 0:
                            print output
                            exit(1)
                    os_rel.asyn_ntp()
            else:
                core_flag = result_to_file(test_file, abs_result_file, 'Failed', run_time)
                '''有用例失败停止运行'''
                print "-------- %s failed!!! --------" % test_file
                failed += 1
                # 注释掉失败的用例，并打标志：failed
                cmd = ("sed -r -i '%ss/^/#failed__/' %s" % (str(num), change_file))
                commands.getstatusoutput(cmd)
                log_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
                # 如果有core产生，则在日志备份目录，添加后缀_CORED
                if core_flag is True:
                    log_path = re.sub('.py', '', test_file).split('/')[-1] + '/' + log_time + '_AUTO_CORED'
                # 如果没有core产生，则主动在每个节点产生oSan的core
                else:
                    log_path = re.sub('.py', '', test_file).split('/')[-1] + '/' + log_time + '_NO_CORED'
                    # for ip in deploy_ips:
                    #     cmd = ("ssh root@%s 'killall -s SIGSEGV oSan'" % (ip,))
                    #     commands.getstatusoutput(cmd)
                # 下刷otrc信息
                for ip in deploy_ips:
                    cmd = ("ssh root@%s '/home/parastor/tools/otrc -c'" % (ip, ))
                    print cmd
                    commands.getstatusoutput(cmd)
                if crash_flag is True:
                    for c_key in crash_list.keys():
                        for c_name in crash_list[c_key]:
                            cmd = ("ssh root@%s 'mkdir -p %s/%s/crash/%s/%s'" % (err_log_ip, err_log_path, log_path, c_key, c_name))
                            commands.getstatusoutput(cmd)
                # 收集服务节点日志
                collect_log.collect_parastors(s_ip=deploy_ips, dst=log_path)
                # 收集主机端日志
                collect_log.collect_clis(s_ip=client_ips, dst=log_path)
                # 收集测试脚本日志
                collect_log.collect_script(dst=log_path)
                if CONTINUEFLAG is False:
                    break
                # 重新部署
                print "Reinstall."
                res, output = commands.getstatusoutput(install_cmd)
                if res != 0:
                    res, output = commands.getstatusoutput(install_cmd)
                    if res != 0:
                        print output
                        exit(1)
                os_rel.asyn_ntp()

    with open("{}".format(abs_result_file), "a+") as f:
        f.write("##############概览#####################" + "\n")
        f.write("total:{}".format(int((success + failed + skip) / LOOPFLAG)) + "\n")
        f.write("pass:{}".format(int(success / LOOPFLAG)) + "\n")
        f.write("failed:{}".format(int(failed / LOOPFLAG)) + "\n")
        f.write("skipped:{}".format(int(skip / LOOPFLAG)) + "\n")

    cmd = "cat " + abs_result_file
    res, msg = commands.getstatusoutput(cmd)
    if res != 0:
        print "File does not exist!!!"
        exit(1)
    else:
        print msg


if __name__ == '__main__':
    arg_analysis()
    run_tests()
    print "The test is finished!!!!!!!!!!!!!!!!!!"
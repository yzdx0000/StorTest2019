#!/usr/bin/python
# -*-coding:utf-8 -*
import logging
import os
import sys
import time
import traceback
import threading

import utils_path
import s3_common
import cosbench_lib
import common
import log
import result
import check_environment
import s3_data_consistency
import get_config
import vdbench_nas
import vdbench_posix
import check_if_cutoff
import collect_log_whenfail
import check_if_nextcase
import iozonenas
import iozoneposix
import mdtest

import fence_common
##########################################################################
#
# Author: zhanghan
# date 2019-03-14
# @summary：
#    主线程
# @steps:
#    1、初始化日志
#    2、运行压力可靠性测试
#       2.1 获取参数
#       2.2 启动各子线程
#    3、判断环境是否断流
#    4、用例失败备份日志
#    5、判断环境是否需要重新部署
#    6、检查并等待环境恢复
#
# @changelog：
##########################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]                 # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')

main_log = None


class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None


def log_init():
    """
    日志解析
    """
    global main_log

    test_log_path = get_config.get_testlog_path()
    file_name = os.path.basename(__file__)
    file_name = file_name.split('.')[0]
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    case_log_dir_name = now_time + '_' + file_name + '_log'
    case_log_path = os.path.join(test_log_path, case_log_dir_name)
    os.mkdir(case_log_path)

    main_file_name = now_time + '_' + file_name + '.log'
    main_file_path = os.path.join(case_log_path, main_file_name)
    print main_file_path

    main_log = logging.getLogger(name='main_log')
    main_log.setLevel(level=logging.INFO)

    handler = logging.FileHandler(main_file_path, mode='a')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(levelname)s][%(asctime)s]   %(message)s',
        '%y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(levelname)s][%(asctime)s]   %(message)s',
        '%y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)

    main_log.addHandler(console)
    main_log.addHandler(handler)

    return case_log_path


def run_func(func):
    """
    打印错误日志
    """
    def _get_fault(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            main_log.error("", exc_info=1)
            traceback.print_exc()
            sys.exit(1)
    return _get_fault


def cleaning_environment(account_email_lst):
    """
    :author:                  baourobing
    :date:                    2018.08.29
    :description:             清理s3用例环境
    :param account_email_lst: (list)账户邮箱
    :return:
    """
    """打开强删桶的开关"""
    rc, stdout = s3_common.set_force_delete_bucket(1)
    common.judge_rc(rc, 0, "set_force_delete_bucket=1 fail!!!")
    main_log.info("wait for force delete bucket working...")
    time.sleep(60)
    main_log.info("begin delete account...")
    """获取账户id"""
    for account_email in account_email_lst:
        """判断账户是否存在"""
        rc, stdout = s3_common.find_account(account_email)
        if rc != 0:
            main_log.info("account is not exist!")
            break
        """获取账户id"""
        rc, account_id = s3_common.get_account_id_by_email(account_email)
        if rc != 0:
            main_log.error("get_account_id_by_email failed")
        """获取证书id列表"""
        rc, certificate_id_lst, certificate_lst = s3_common.get_certificate_by_accountid(
            account_id)
        if rc != 0:
            main_log.error("get certificate by account id failed!")
        # 处理账户证书为空的情况
        if len(certificate_id_lst) == 0:
            s3_common.add_certificate(account_id)
        rc, certificate_id_lst, certificate_lst = s3_common.get_certificate_by_accountid(
            account_id)

        for certificate_id in certificate_id_lst:
            """获取所有桶的列表"""
            rc, bucket_name_lst = s3_common.get_all_bucket_name(certificate_id)
            print rc, bucket_name_lst
            if rc != 0:
                main_log.error("get_all_bucket_name failed!!!")
            while (bucket_name_lst != []) and (bucket_name_lst is not None):
                for bucket_name in bucket_name_lst:
                    """删除桶"""
                    rc, stdout = s3_common.del_bucket(
                        bucket_name, certificate_id)
                    if rc != 0:
                        main_log.error("delete bucket failed!")
                rc, bucket_name_lst = s3_common.get_all_bucket_name(
                    certificate_id)
            """删除证书"""
            s3_common.del_certificate(certificate_id)
        """删除账户"""
        rc, stdout = s3_common.del_account(account_id)
        if rc != 0:
            main_log.error("delete account failed!")
    return


def make_fault(fault_operation, fault_times, check_lock_nr_times, fault_lock_num_max):
    obj_fault_test = fence_common.Fence()
    obj_node = common.Node()
    for fault_num in range(fault_times):  # 故障执行的次数
        main_log.info("the fault times %d will be excuted" % fault_num)
        main_log.info("Wait 60s for next fault")
        time.sleep(60)
        for check_lock_nr_num in range(check_lock_nr_times):  # 判断30次，如果30次内锁的数量均超过10000，则报错退出
            lock_nr = int(common.get_lock_nr())
            main_log.info(
                "fault_num:%d, check_lock_nr_num:%d, lock_nr is %d\n" % (fault_num, check_lock_nr_num, lock_nr))
            if -1 == lock_nr:  # 查询锁数量命令执行失败
                main_log.error("Function:%s, excuted failed!" % ("get_lock_nr"))
                return -4, "Function:%s, excuted failed!" % ("get_lock_nr")
            elif lock_nr <= fault_lock_num_max:
                (rc, master_id) = obj_fault_test.get_master_of_zk()
                if 0 != rc:
                    main_log.error(
                        "Function:%s, excuted failed!" %
                        ("get_master_of_zk"))
                    return -3, "Function:%s, excuted failed!" % ("get_master_of_zk")
                else:
                    master_ip = obj_node.get_node_ip_by_id(master_id)
                    node_ip = get_config.get_stortest_ip()
                    fault_script_path = get_config.get_fault_with_repaire_script_path()
                    fault_node = master_ip
                    cluster_ip_list = get_config.get_allparastor_ips()
                    for current_ip in cluster_ip_list:
                        if current_ip == fault_node:
                            cluster_ip_list.remove(current_ip)
                    mgr_ip = cluster_ip_list[0]
                    if len(cluster_ip_list) < 9:
                        if 0 == (len(cluster_ip_list) % 2):
                            zk_num = len(cluster_ip_list) - 1
                        else:
                            zk_num = len(cluster_ip_list)
                    else:
                        zk_num = 9
                    main_log.info("fault_num:%d, check_lock_nr_num:%d, lock_nr is %d, will fault\n" % (
                    fault_num, check_lock_nr_num, lock_nr))

                    thread_fault = MyThread(
                        obj_fault_test.fault_in_master_node,
                        args=(node_ip, fault_script_path, fault_operation, zk_num, mgr_ip, fault_node),)
                    thread_fault.start()
                    thread_fault.join()
                    result = thread_fault.get_result()
                    main_log.info("Fault %d times\n, the rc is %d\n ,output is %s\n" % (fault_num, result[0], result[1]))
                    if 0 != result[0]:
                        result_err = -2, "Fault excuted failed! the output is %s" % (result[1])
                        return result_err
                    break
            else:
                main_log.info(
                    "Due to 'lock_nr':%d is not smaller than 'fault_lock_num_max':%d. Please wait 1min" %
                    (lock_nr, fault_lock_num_max))
                time.sleep(60)
        else:
            main_log.info("lock_nr has been checked over %d for %d times" % (fault_lock_num_max, check_lock_nr_times))
            return -1, "lock_nr has been checked over %d for %d times, can not to make fault!" % (fault_lock_num_max, check_lock_nr_times)
    return 0, "Fault has been done for %d times, success!" % (fault_times)


@run_func
def case(case_log_path):
    """
    参数说明：
    client_ip :             客户端IP
    oOss_ip :               发送请求到集群IP
    cosbench_path:          cosbench的安装路径
    file_path：              需要运行的cosbench文件
    prepare_stage_time：     prepare阶段运行的最长时间
    main_stage_time：        main阶段运行的最长时间
    :return:
    """
    # 初始化日志
    # case_log_path = log_init()

    main_log.info("****************获取参数*****************")
    account_name = FILE_NAME.replace('_', '-')

    # 获取需要运行哪些压力的参数
    if_run_stress_list = []
    stress_type_param = get_config.get_stress_type_param()
    if_run_cosbench = bool(int(stress_type_param['if_run_cosbench']))
    if_run_stress_list.append(if_run_cosbench)
    if_run_s3_consistency = bool(
        int(stress_type_param['if_run_s3_consistency']))
    if_run_stress_list.append(if_run_s3_consistency)
    if_run_vdbench = bool(int(stress_type_param['if_run_vdbench']))
    if_run_stress_list.append(if_run_vdbench)
    if_run_iozone = bool(int(stress_type_param['if_run_iozone']))
    if_run_stress_list.append(if_run_iozone)
    if_run_mdtest = bool(int(stress_type_param['if_run_mdtest']))
    if_run_stress_list.append(if_run_mdtest)
    # main_log.info("%s, %s, %s, %s" % (if_run_cosbench, if_run_s3_consistency, if_run_vdbench, if_run_iozone))
    for if_run_stress in if_run_stress_list:
        main_log.info(if_run_stress)
        main_log.info(type(if_run_stress))

    main_log.info("=================清理账户_%s==================" % account_name)
    account_email = account_name + '@sugon.com'
    cleaning_environment([account_email])

    operation_list = []
    cosbench_test = cosbench_lib.CosbenchTest(case_log_path, account_name)
    operation_list.append(cosbench_test)
    s3_data_test = s3_data_consistency.S3DataConsistencyTest(case_log_path)
    operation_list.append(s3_data_test)
    check_env_test = check_environment.CheckEnvironmentTest(case_log_path)
    operation_list.append(check_env_test)
    vdb_nas_test = vdbench_nas.VdbenchNasTest(case_log_path, FILE_NAME)
    operation_list.append(vdb_nas_test)
    vdb_posix_test = vdbench_posix.VdbenchPosixTest(case_log_path, FILE_NAME)
    operation_list.append(vdb_posix_test)
    iozone_nas_test = iozonenas.IozoneNas(case_log_path, FILE_NAME)
    operation_list.append(iozone_nas_test)
    iozone_posix_test = iozoneposix.IozonePosix(case_log_path, FILE_NAME)
    operation_list.append(iozone_posix_test)
    mdtest_test = mdtest.MdtestTest(case_log_path, FILE_NAME)
    operation_list.append(mdtest_test)
    for opt in operation_list:
        main_log.info(opt)

    if if_run_cosbench:
        cosbench_test.start()
    if if_run_s3_consistency:
        s3_data_test.start()
    if if_run_vdbench:
        vdb_nas_test.start()
        vdb_posix_test.start()
    if if_run_iozone:
        iozone_nas_test.start()
        iozone_posix_test.start()
    if if_run_mdtest:
        mdtest_test.start()
    check_env_test.start()

    fault_operation = 2
    fault_lock_num_max = 10000
    check_lock_nr_times = 30
    fault_times = 5
    res_fault = 0, ""
    if if_run_cosbench is False:
        main_log.info("cosbench is not run, fault will start after 1 min... ")
        time.sleep(60)
        main_log.info("start fault...")
        res_fault = make_fault(fault_operation, fault_times, check_lock_nr_times, fault_lock_num_max)
    else:
        for i in range(3600):
            main_log.info("---------wait for fault times: %s------------" % i)
            # 判断是否启用故障
            main_log.info('cosbench_test.IF_MAKE_FAULT:%s' % cosbench_test.IF_MAKE_FAULT)
            if cosbench_test.IF_MAKE_FAULT is True:
                main_log.info("start fault...")
                res_fault = make_fault(fault_operation, fault_times, check_lock_nr_times, fault_lock_num_max)
                break
            time.sleep(10)
    if 0 == res_fault[0]:
        log.info("fault excuted success!")
    else:
        log.info("fault excuted failed, the output is %s\n" % (res_fault[1]))


    if (check_env_test.is_running() and
            (not (cosbench_test.is_running() ^ if_run_cosbench)) and
            (not (s3_data_test.is_running() ^ if_run_s3_consistency)) and
            (not (vdb_nas_test.is_running() ^ if_run_vdbench)) and
            (not (vdb_posix_test.is_running() ^ if_run_vdbench)) and
            (not (iozone_nas_test.is_running() ^ if_run_iozone)) and
                (not (iozone_posix_test.is_running() ^ if_run_iozone))) is True:
        press_result = True
    else:
        press_result = False
    main_log.info("press_result is %s" % press_result)
    main_log.info("stop all work !!!")
    for opt in operation_list:
        opt.stop()
        main_log.info("%s has been stoped successfully!" % opt)


    # 判断各个线程是否已经结束
    while True:
        time.sleep(100)
        for opt in operation_list:
            main_log.info("%s: %s" % (opt, opt.is_running()))

        if (check_env_test.is_running() or cosbench_test.is_running() or
                s3_data_test.is_running() or vdb_nas_test.is_running() or
                vdb_posix_test.is_running() or iozone_nas_test.is_running() or
                iozone_posix_test.is_running()) is True:
            continue
        else:
            main_log.info("all threads has been stoped successfully")
            break

    case_result = press_result and not(res_fault[0])

    if case_result:
        main_log.info('%s success!' % FILE_NAME)
    else:
        main_log.info('%s failed!' % FILE_NAME)
    return case_result


@run_func
def main():
    # 初始化底层函数所需日志
    log_file_path = log.get_log_path(FILE_NAME)
    log.init(log_file_path, True)

    # 初始化日志
    case_log_path = log_init()
    main_log.info('>step 01:初始化日志')

    # 跑压力和可靠性，如果没问题且环境没有core，crah和坏段则返回True，否则返回False
    main_log.info('>step 02:跑压力可靠性用例')
    case_result = case(case_log_path)

    # 判断是断流，输出断流的vdbench的output路径list，如果没有断流，则路径为空list []
    main_log.info('>step 03:判断环境是否断流')
    cutoffdir = []
    if case_result is True:
        cutoffdir = check_if_cutoff.aftercase_ifcutoff(
            FILE_NAME, case_log_path, cut_off_time_standard=15)
    # 如果用例失败则跳过检测断流阶段
    else:
        main_log.info('%s finish!' % FILE_NAME)
        main_log.info('%s failed!' % FILE_NAME)
        result.result(FILE_NAME, -1)
        now_time = time.strftime(
            '%Y-%m-%d-%H-%M-%S',
            time.localtime(
                time.time()))
        failfile = os.path.join('/tmp/script_err', now_time)
        cmd = "touch %s" % failfile
        common.command(cmd)

    # 自动备份日志部分暂时注释掉 20190319
    # main_log.info('>step 04:用例备份日志')
    # # 获取私有客户端的ip
    # posix_vdbench_param = get_config.get_posix_vdbench_param()
    # posix_ip = posix_vdbench_param['ip']
    # posix_ip = [posix_ip]
    # main_log.info("posix_ip: %s" % posix_ip)
    # 判断是否需要备份日志
    # if cutoffdir == [] and case_result is True:
    #     main_log.info("case success, and do not need collect log!")
    #     pass
    # else:
    #     main_log.info("case failed, and need collect log!")
    #     collect_log_whenfail.collect_log(
    #         case_log_path, -1, FILE_NAME, cutoffdir, client_ip_list=posix_ip)

    main_log.info('>step 05:检查环直到环境恢复')
    parastor_ips = get_config.get_allparastor_ips()
    parastor_ip_list = []
    for para_ip in parastor_ips:
        parastor_ip_list.append(para_ip.encode("utf-8"))
    mgr_ip = parastor_ip_list[0]

    check_result = check_if_nextcase.main(case_log_path, mgr_ip)
    if check_result == 0:
        main_log.info(
            '>finally:case %s is finish,you can run the next case!!!!' %
            FILE_NAME)

    main_log.info('>step 06：将用例结果输出')
    if case_result and ([] == cutoffdir):
        main_log.info("case %s success!" % FILE_NAME)
        result.result(FILE_NAME, 0)
    else:
        common.except_exit("%s failed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

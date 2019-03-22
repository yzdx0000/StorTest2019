#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import os
import time
import threading
import re

import utils_path
import common
import s3_common
import log
import get_config
import prepare_clean
import result
import cosbench_lib

##########################################################################
#
# Author: zhanghan
# date 2018-12-21
# @summary：
#    验证向bucket用cosbench跑S3，删除bucket：若不打开强删桶的开关，删除失败，环境正常；若打开强删桶的开关,删除成功，环境正常。测试用例：29-0-20-38
# @steps:
#    1、获取参数；
#    2、关闭强删桶开关，cosbench运行时/cosbench运行结束后，分别执行删除桶操作；
#       2-1> 关闭强删桶开关
#       2-2> 多线程运行cosbench及删除桶操作
#       2-3> 停掉cosbench，等没有数据写入后，再次执行删除桶操作"
#    3、打开强删桶开关，删除桶
#       3-1> 打开强删桶开关
#       3-2> 删除桶
#       3-3> 测试结束，关闭强删桶开关
#    4、记录用例执行成功
#
# @changelog：
##########################################################################

# 全局变量
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME.replace('_', '') + "@sugon.com"
CHECK_BUC_STORAGE_TIMES = 30
IS_COS_STOP_CHECK_TIMES = 5


class MyThread(threading.Thread):
    def __init__(self, func, args=(), name=""):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
        self.name = name

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None

    def get_func_name(self):
        return self.name


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, "-1")


cos = cosbench_lib.CosbenchTest()


def case():
    log.info("1> 参数获取")
    account_name = FILE_NAME.replace('_', '')
    cosbench_path = get_config.get_cosbench_path()
    oOss_ip = s3_common.get_ooss_node_ip()
    file_path = get_config.get_cosbench_xml_file_path()[0]
    current_ip = get_config.get_cosbench_client_ip()[0]

    log.info("2> 关闭强删桶开关，cosbench运行时/cosbench运行结束后，分别执行删除桶操作")
    log.info("2-1> 关闭强删桶开关")
    rc, stdout = s3_common.set_force_delete_bucket(0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "set_force_delete_bucket=0 fail!!!")
    log.info("set force_delete_bucket=0 success")
    log.info("2-2 多线程运行cosbench及删除桶操作")
    pro_cos = MyThread(
        cos.run_cosbench,
        args=(account_name, cosbench_path, oOss_ip, file_path),
        name="run_cosbench"
    )
    pro_cos.setDaemon(True)
    pro_cos.start()
    time.sleep(30)
    workload_id = pro_cos.get_result()
    des_str = "w"
    res = re.match(des_str, workload_id)
    if res == 'None':
        log.error("Error! The workload_id got error")
        judge_result(1, FILE_NAME)
        common.judge_rc(1, 0, "Error! The workload_id got error")
    else:
        log.info("The workload_id is %s \n" % workload_id)
        pass

    while True:
        (work_state, pro_status, prepare_run_time,
         main_run_time) = cos.get_workload_detail_by_id(current_ip, workload_id)
        if work_state == "TERMINATED":
            log.error("Error!!! cosbench bas been terminated")
            judge_result(1, FILE_NAME)
            common.judge_rc(1, 0, "Error!!! cosbench bas been terminated")
        else:
            if pro_status == "prepare":
                log.info(
                    "cosbench has been in 'prepare' stage, the operation of deleting bucket can be done")
                time.sleep(20)
                break
            else:
                log.info(
                    "cosbench has not been in 'prepare' stage, the operation of deleting bucket should wait")
                time.sleep(20)

    (rc, acc_id) = s3_common.get_account_id_by_email(ACCOUNT_EMAIL)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "get account id failed")
    (rc, cer_id_list, sk) = s3_common.get_certificate_by_accountid(acc_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "get certificate id failed")
    cer_id = cer_id_list[0]
    (rc, bucket_name_list) = s3_common.get_all_bucket_name(cer_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "get bucket name failed")
    bucket_name = bucket_name_list[0]

    # 检查bucket中已经有对象
    check_buc_storage_time = 0
    while True:
        (rc, buc_storage) = s3_common.get_bucket_storageinfo(bucket_name, cer_id)
        print("buc_storage is %s" % buc_storage)
        if check_buc_storage_time <= CHECK_BUC_STORAGE_TIMES:
            if buc_storage != '0':
                log.info("buc_storage is not 0, the bucket has objects")
                break
            else:
                check_buc_storage_time = check_buc_storage_time + 1
                log.info(
                    "please wait, buc_storage is 0, the bucket has no objects")
                time.sleep(10)
        else:
            log.error("Error! the bucket still has no objects, please check!")
            judge_result(1, FILE_NAME)
            common.judge_rc(
                1, 0, "Error! the bucket still has no objects, please check!")

    pro_del_buc = MyThread(
        s3_common.del_bucket,
        args=(bucket_name, cer_id),
        name="delete_bucket"
    )
    pro_del_buc.setDaemon(True)
    pro_del_buc.start()
    pro_del_buc.join()
    del_buc_rc = pro_del_buc.get_result()[0]
    if del_buc_rc != 0:
        judge_result(0, FILE_NAME)
    common.judge_rc_unequal(del_buc_rc, 0, "Error!!!delete bucket success")

    log.info("2-3> 停掉cosbench，等没有数据写入后，再次执行删除桶操作")
    cos.stop(current_ip, cosbench_path)
    time.sleep(10)
    while True:
        rc, acc_storage_info = s3_common.get_account_storage(acc_id)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "get account storage failed!")
        for check_times in range(IS_COS_STOP_CHECK_TIMES + 1):
            time.sleep(10)
            rc, acc_storage_tmp = s3_common.get_account_storage(acc_id)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "get account storage failed!")
            log.info("acc_storage_tmp is %s" % acc_storage_tmp)
            log.info("acc_storage_info is %s" % acc_storage_info)
            if (acc_storage_tmp == acc_storage_info) and (
                    check_times == IS_COS_STOP_CHECK_TIMES):
                log.info(
                    "check %d times, the cosbench hao no I/O, making sure cosbench has stoped" %
                    IS_COS_STOP_CHECK_TIMES)
                exit_flag = 1
                break
            elif acc_storage_tmp != acc_storage_info:
                log.info("the cosbench still has I/O, wait for next check")
                exit_flag = 0
                break
            else:
                log.info(
                    "check %d times, the cosbench has no I/O, wait for next check" % int(check_times + 1))
                pass
        if exit_flag == 1:
            break
        elif exit_flag == 0:
            pass

    pro_del_buc_twice = MyThread(
        s3_common.del_bucket,
        args=(bucket_name, cer_id),
        name="delete_bucket"
    )
    pro_del_buc_twice.setDaemon(True)
    pro_del_buc_twice.start()
    pro_del_buc_twice.join()
    del_buc_rc = pro_del_buc_twice.get_result()[0]
    if del_buc_rc != 0:
        judge_result(0, FILE_NAME)
    common.judge_rc_unequal(del_buc_rc, 0, "Error!!!delete bucket success")

    log.info("3> 打开强删桶开关，删除桶")
    log.info("3-1> 打开强删桶开关")
    rc, stdout = s3_common.set_force_delete_bucket(1)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "set_force_delete_bucket=1 fail!!!")
    log.info("set force_delete_bucket=1 success")
    time.sleep(10)
    log.info("3-2> 删除桶")
    pro_del_buc_with_force_delete = MyThread(
        s3_common.del_bucket,
        args=(bucket_name, cer_id),
        name="delete_bucket"
    )
    pro_del_buc_with_force_delete.setDaemon(True)
    pro_del_buc_with_force_delete.start()
    pro_del_buc_with_force_delete.join()
    del_buc_rc = pro_del_buc_with_force_delete.get_result()[0]
    judge_result(del_buc_rc, FILE_NAME)
    common.judge_rc(del_buc_rc, 0, "Error!!!delete bucket failed")
    log.info("3-3> 测试结束，关闭强删桶开关")
    rc, stdout = s3_common.set_force_delete_bucket(0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "set_force_delete_bucket=0 fail!!!")
    log.info("set force_delete_bucket=0 success")

    log.info("4> 用例%s执行成功" % FILE_NAME)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL], False)
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s finished!' % FILE_NAME)
    result.result(FILE_NAME, "0")


if __name__ == '__main__':
    common.case_main(main)

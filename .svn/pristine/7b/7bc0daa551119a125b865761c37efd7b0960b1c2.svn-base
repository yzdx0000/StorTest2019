#!/usr/bin/python
# -*-coding:utf-8 -*
import os
import threading
import time

import utils_path
import common
import s3_common
import log
import prepare_clean
import result

##########################################################################
#
# Author: lichengxu
# date 2018-12-1
# @summary：
#    object拷贝过程中，删除bucket
# @steps:
#    1、创建账户；
#    2、检查账户是否存在
#    3、创建证书；
#    4、创建两个桶
#    5、创建上传的文件，并上传对象
#    6、多线程实现拷贝对象，同时删除桶
#    7、检查环境
#    8、清理环境
#
# @changelog：
##########################################################################
# 本脚本名字
FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"
test_path = "/tmp/s3test"

def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, -1)


class MyThread(threading.Thread):
    def __init__(self, func, args=(), name=""):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
        self.name = name

    def run(self, ):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None

    def get_func_name(self):
        return self.name


def case():
    log.info("1> 创建账户")
    account_name = FILE_NAME + "_account1"
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add_account %s failed!!!" % account_name)

    log.info("2> 检查账户是否存在")
    rc, stdout = s3_common.find_account(ACCOUNT_EMAIL)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "find account %s failed!!!" % ACCOUNT_EMAIL)

    log.info("3> 创建证书")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    bucket_name_lst_base = []
    log.info("4> 创建桶")
    for i in range(2):
        bucket_name = FILE_NAME + '_bucket_%s' % i
        bucket_name = bucket_name.replace('_', '-')
        bucket_name_lst_base.append(bucket_name)
        rc, stdout = s3_common.add_bucket(
            bucket_name, certificate_id, exe_node_ip=None)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)
        rc, stdout = s3_common.check_bucket(
            bucket_name, certificate_id, exe_node_ip=None)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "check bucket %s failed!!!" % bucket_name)

    log.info("5> 创建上传文件")
    """创建10M文件"""
    file_size = 1000  # 单位是M
    cmd = "rm -rf %s" % test_path
    common.command(cmd)
    os.mkdir(test_path)
    file_path1 = os.path.join(test_path, 'file1')
    rc, stdout = s3_common.create_file_m(file_path1, file_size)
    common.judge_rc(rc, 0, "create file %s failed!!!" % file_path1)
    log.info("create file success!")

    object_name_lst_base = []
    log.info("6> 上传对象")
    object_name_1 = FILE_NAME + '_object_1'
    object_name_lst_base.append(object_name_1)
    rc, stdout = s3_common.add_object(bucket_name_lst_base[0], object_name_1, file_path1, certificate_id)
    common.judge_rc(rc, 0, "upload object failed!")
    log.info("upload object success!")

    log.info("7> 多线程的方式实现拷贝对象，同时删除bucket")
    object_name_2 = FILE_NAME + '_object_2'
    object_name_lst_base.append(object_name_2)
    thread_list = [
        MyThread(s3_common.cp_object, args=(bucket_name_lst_base[1], object_name_2, certificate_id,
                                            bucket_name_lst_base[0], object_name_1,)),
        MyThread(s3_common.del_bucket, args=(bucket_name_lst_base[1], certificate_id,)),
    ]
    for thread in thread_list:
        thread.start()
        time.sleep(5)
    for thread in thread_list:
        thread.join()

    for thread in thread_list:
        log.info(
            "in func %s, the (final_rc, acl_num) is %s" %
            (thread.get_func_name, thread.get_result()))
    #     common.judge_rc(thread.get_result()[0], 0, "%s excute failed" % thread.get_func_name())
    log.info("put object %s success!" % object_name_2)


    log.info("8> 获取账户内所有的桶")
    rc, bucket_name_lst = s3_common.get_all_bucket_name(certificate_id)
    common.judge_rc(rc, 0, "get bucket failed!!!")

    log.info("9> 检查环境")
    prepare_clean.test_prepare(FILE_NAME, )

    log.info('%s success!' % FILE_NAME)
    result.result(FILE_NAME, 0)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s finish!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

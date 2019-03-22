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
# date 2018-12-24
# @summary：
#    使用PUT上传大约等于1M的对象:使用PUT方法的curl命令向指定的bucket中上传等于1M，1M+64k,2M的对象,验证是否上传成功并校验一致性。测试用例：29-0-20-39
# @steps:
#    1、创建账户
#    2、创建证书
#    3、创建桶
#    4、采用多线程的方式上传对象，对象大小为1M,1M+64k,2M
#       4-1> 创建大小依次为1M,1M+64k,2M的三个对象
#       4-2> 获取这三个文件的MD5值
#       4-3> 多线程上传3个对象,并根据返回值判断对象是否上传成功
#    5、多线程下载对象并重新获取MD5值进行校验
#       5-1> 多线程下载对象
#       5-2> 获取对象MD5值，并进行校验
#    6、记录用例执行成功
#
# @changelog：
##########################################################################

# 全局变量
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"


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


def case():
    log.info("1> 创建账户")
    account_name = FILE_NAME + "_account1"
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create account failed!!!")

    log.info("2> 创建证书")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    log.info("3> 创建桶")
    bucket_name = FILE_NAME + '_bucket1'
    bucket_name = bucket_name.replace('_', '-')
    rc, stdout = s3_common.add_bucket(bucket_name, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add bucket failed!!!")

    log.info("4> 采用多线程的方式上传对象，对象大小为1M,1M+64k,2M")
    log.info("4-1> 创建大小依次为1M,1M+64k,2M的三个对象")
    file_dir = "/tmp"
    file_name_size_dict = {
        "file_1_" + FILE_NAME: 1024,
        "file_2_" + FILE_NAME: 1088,
        "file_3_" + FILE_NAME: 2048}
    file_list = []
    for key in file_name_size_dict:
        file_tmp = os.path.join(file_dir, key)
        rc, stdout = s3_common.create_file_k(
            file_tmp, file_name_size_dict[key])
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "create file failed!!!")
        file_list.append(file_tmp)
    log.info("4-2> 获取这三个文件的MD5值")
    file_md5_list = []
    for file_tmp in file_list:
        (rc, md5) = s3_common.get_file_md5(file_tmp)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "get file MD5 failed!!!")
        file_md5_list.append(md5)
    log.info("4-3> 多线程上传3个对象,并根据返回值判断对象是否上传成功")
    pro_add_obj_list = []
    object_list = [
        "object_1_" +
        FILE_NAME,
        "object_2_" +
        FILE_NAME,
        "object_3_" +
        FILE_NAME]
    for file_tmp, obj_tmp in zip(file_list, object_list):
        object_list.append(obj_tmp)
        pro_add_obj_tmp = MyThread(
            s3_common.add_object,
            args=(bucket_name, obj_tmp, file_tmp, certificate_id),
            name="add_object"
        )
        pro_add_obj_list.append(pro_add_obj_tmp)
    for p in pro_add_obj_list:
        p.setDaemon(True)
        p.start()
    for p in pro_add_obj_list:
        p.join()
    for p in pro_add_obj_list:
        rc = p.get_result()[0]
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "add object failed!!!")

    log.info("5> 多线程下载对象并重新获取MD5值进行校验")
    log.info("5-1> 多线程下载对象")
    pro_download_obj_list = []
    download_file_list = []
    for obj_tmp in object_list:
        print(obj_tmp)
        download_file_path = os.path.join(file_dir, obj_tmp)
        print(download_file_path)
        download_file_list.append(download_file_path)
        pro_download_obj_tmp = MyThread(
            s3_common.download_object,
            args=(bucket_name, obj_tmp, download_file_path, certificate_id),
            name="add_object"
        )
        pro_download_obj_list.append(pro_download_obj_tmp)
    for p in pro_download_obj_list:
        p.setDaemon(True)
        p.start()
    for p in pro_download_obj_list:
        p.join()
    for p in pro_download_obj_list:
        rc = p.get_result()[0]
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "download object failed!!!")
    log.info("5-2> 获取对象MD5值，并进行校验")
    download_file_md5_list = []
    for down_file_tmp in download_file_list:
        (rc, md5) = s3_common.get_file_md5(down_file_tmp)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "get file MD5 failed!!!")
        download_file_md5_list.append(md5)
    if download_file_md5_list.sort() == file_md5_list.sort():
        log.info("success! File MD5 check success")
        judge_result(0, FILE_NAME)
    else:
        log.error("failed! File MD5 check failed")
        judge_result(1, FILE_NAME)
        common.judge_rc(1, 0, "File MD5 check failed!!!")

    log.info("6> 用例%s执行成功" % FILE_NAME)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL], False)
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s finished!' % FILE_NAME)
    result.result(FILE_NAME, "0")


if __name__ == '__main__':
    common.case_main(main)

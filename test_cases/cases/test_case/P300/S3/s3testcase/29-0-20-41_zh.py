#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import os
import random

import utils_path
import common
import s3_common
import log
import prepare_clean
import result


##########################################################################
#
# Author: zhanghan
# date 2018-12-26
# @summary：
#    频繁上传空洞文件至同一个对象,并进行MD5值校验。测试用例：29-0-20-41
# @steps:
#    1、创建账户
#    2、创建证书
#    3、创建桶
#    4、dd创建文件，并执行truncate/echo操作，上传/下载对象，校验MD5
#    5、记录用例执行成功
#
# @changelog：
##########################################################################

# 全局变量
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"
ANCHOR_PATH = '/tmp'
FILE_INIT_SIZE = 3  # 以kbyte为单位
OBJECT_NAME = "object_" + FILE_NAME
TARGET_STRING = "abcdefghigjlmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890,._ "
STEP_SIZE_B = 16 # 单位是byte
ECHO_SIZE_K1 = 3 # 以kbyte为单位
ECHO_SIZE_K2= 4
ECHO_SIZE_K3 = 3
TRUNCATE_SIZE_INIT1 = 4096  # 单位是byte
TRUNCATE_SIZE_STEP1 = 4096
TRUNCATE_SIZE_INIT2 = 8192
TRUNCATE_SIZE_STEP2 = 8192
TRUNCATE_SIZE_INIT3 = 6144
TRUNCATE_SIZE_STEP3 = 6144
REWRITE_SIZE2 = 4
REWRITE_SIZE3 = 3
LOOP_NUM = 10

# 生成size_kbyte指定长度的字符串
def create_random_string_k(size_kbyte, target_string, step_size_byte):
    dst_str = ""
    loop_times = size_kbyte*1024/step_size_byte
    for num in range(loop_times):
        dst_str = dst_str + ''.join(random.sample(target_string, step_size_byte))
    return dst_str

def echo_file(echo_content, filename):
    cmd = "echo %s >> %s" % (echo_content, filename)
    rc = common.command(cmd)
    return rc

def echo_rewrite_file(echo_content, filename):
    cmd = "echo %s > %s" % (echo_content, filename)
    rc = common.command(cmd)
    return rc

def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, "-1")

def judge_md5(md5_put, md5_download):
    if md5_put == md5_download:
        log.info("MD5 check success, the MD5 is %s" % md5_put)
    else:
        log.info(
            "MD5 check failed, the put MD5 is %s, the download MD5 is %s" %
            (md5_put, md5_download))
        judge_result(1, FILE_NAME)
        common.judge_rc(1, 0, "MD5 check failed!!!")

def dd_file_put_download_md5(
        file_init_size,
        file_path,
        bucket_name,
        object_name,
        certificate_id,
        dst_file_path):
    # 创建文件
    rc, stdout = s3_common.create_file_k(file_path, file_init_size)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "dd 3k file failed!!!")
    # 获取文件MD5值
    rc, md5_tmp = s3_common.get_file_md5(file_path)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "get file MD5 failed!!!")
    # 上传对象
    rc, stdout = s3_common.add_object(
        bucket_name, object_name, file_path, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "put object failed!!!")
    # 下载对象
    rc, stdout = s3_common.download_object(
        bucket_name, object_name, dst_file_path, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "download object failed!!!")
    # 获取下载下来的对象MD5值
    rc, md5_tmp_download = s3_common.get_file_md5(file_path)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "get file MD5 failed!!!")
    # MD5值校验
    judge_md5(md5_tmp, md5_tmp_download)

def truncate_file_put_download_md5(
        truncate_size,
        file_path,
        bucket_name,
        object_name,
        certificate_id,
        dst_file_path):
    # truncate文件，增加1k空洞
    rc, stdout = s3_common.truncate_file(file_path, truncate_size)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "truncate failed!!!")
    # 获取truncate后的文件MD5值
    rc, md5_tmp_tru = s3_common.get_file_md5(file_path)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "get file MD5 failed!!!")
    # 再次上传到同一个对象
    rc, stdout = s3_common.add_object(
        bucket_name, object_name, file_path, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "put object failed!!!")
    # 再次下载对象
    rc, stdout = s3_common.download_object(
        bucket_name, object_name, dst_file_path, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "download object failed!!!")
    # 再次获取下载下来的对象MD5值
    rc, md5_tmp_tru_download = s3_common.get_file_md5(file_path)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "get file MD5 failed!!!")
    # 校验MD5值
    judge_md5(md5_tmp_tru, md5_tmp_tru_download)

def echo_file_put_download_md5(
        echo_size,
        target_string,
        step_size_b,
        file_path,
        bucket_name,
        object_name,
        certificate_id,
        dst_file_path):
    # echo >> file
    str = create_random_string_k(echo_size, target_string, step_size_b)
    rc = echo_file(str, file_path)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "echo >> file failed!!!")
    # 获取echo后的文件MD5值
    rc, md5_tmp_echo = s3_common.get_file_md5(file_path)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "get file MD5 failed!!!")
    # 再次上传到同一个对象
    rc, stdout = s3_common.add_object(
        bucket_name, object_name, file_path, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "put object failed!!!")
    # 再次下载对象
    rc, stdout = s3_common.download_object(
        bucket_name, object_name, dst_file_path, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "download object failed!!!")
    # 再次获取下载下来的对象MD5值
    rc, md5_tmp_echo_download = s3_common.get_file_md5(file_path)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "get file MD5 failed!!!")
    # 校验MD5值
    judge_md5(md5_tmp_echo, md5_tmp_echo_download)


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

    file_path = os.path.join(ANCHOR_PATH, 'object_' + FILE_NAME)
    dst_file_path = os.path.join(ANCHOR_PATH, 'dst_object_' + FILE_NAME)
    log.info("4> dd创建文件，并执行truncate/echo操作，校验MD5")
    dd_file_put_download_md5(
        FILE_INIT_SIZE,
        file_path,
        bucket_name,
        OBJECT_NAME,
        certificate_id,
        dst_file_path)
    truncate_size1 = TRUNCATE_SIZE_INIT1
    for loop_time in range(LOOP_NUM):
        truncate_file_put_download_md5(
            truncate_size1,
            file_path,
            bucket_name,
            OBJECT_NAME,
            certificate_id,
            dst_file_path)
        truncate_size1 = truncate_size1 + TRUNCATE_SIZE_STEP1
        echo_file_put_download_md5(
            ECHO_SIZE_K1,
            TARGET_STRING,
            STEP_SIZE_B,
            file_path,
            bucket_name,
            OBJECT_NAME,
            certificate_id,
            dst_file_path)

    # 将文件echo到4k，然后再次进行truncate/echo >>，并上传/下载，校验一致性
    str = create_random_string_k(REWRITE_SIZE2, TARGET_STRING, STEP_SIZE_B)
    rc = echo_rewrite_file(str, file_path)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "echo > file to %s failed!!!" % REWRITE_SIZE2)
    truncate_size2 = TRUNCATE_SIZE_INIT2
    for loop_time in range(LOOP_NUM):
        truncate_file_put_download_md5(
            truncate_size2,
            file_path,
            bucket_name,
            OBJECT_NAME,
            certificate_id,
            dst_file_path)
        truncate_size2 = truncate_size2 + TRUNCATE_SIZE_STEP2
        echo_file_put_download_md5(
            ECHO_SIZE_K2,
            TARGET_STRING,
            STEP_SIZE_B,
            file_path,
            bucket_name,
            OBJECT_NAME,
            certificate_id,
            dst_file_path)

    # 将文件echo到3k，然后再次进行truncate/echo >>，并上传/下载，校验一致性
    str = create_random_string_k(REWRITE_SIZE3, TARGET_STRING, STEP_SIZE_B)
    rc = echo_rewrite_file(str, file_path)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "echo > file to %s failed!!!" % REWRITE_SIZE3)
    truncate_size3 = TRUNCATE_SIZE_INIT3
    for loop_time in range(LOOP_NUM):
        truncate_file_put_download_md5(
            truncate_size3,
            file_path,
            bucket_name,
            OBJECT_NAME,
            certificate_id,
            dst_file_path)
        truncate_size3 = truncate_size3 + TRUNCATE_SIZE_STEP3
        echo_file_put_download_md5(
            ECHO_SIZE_K3,
            TARGET_STRING,
            STEP_SIZE_B,
            file_path,
            bucket_name,
            OBJECT_NAME,
            certificate_id,
            dst_file_path)

    log.info("5> 用例%s执行成功" % FILE_NAME)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL], False)
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s finished!' % FILE_NAME)
    result.result(FILE_NAME, "0")


if __name__ == '__main__':
    common.case_main(main)

#! /usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import commands
import json
import time
import ConfigParser
import random

current_pyth = os.getcwd()
pwd = os.path.dirname(current_pyth)
sys.path.append(pwd + "/S3Lib")
import utils_path
import result
import prepare_clean
import get_config
import log
import s3_common
import common
import utils_path

##########################################################################
#
# Author: wangjianlei
# date 2018-09-06
# @summary：
#    签名认证模式下，桶操作。
# @steps:
#    1、创建账户；
#    2、创建证书；
#    3、上传桶；
#    4、检查桶；
#    5、清理桶；
#    6、删除证书及账户
#
##########################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, "-1")

# def wait_fuc(times, fuc, rvalue=True, *args, **kwargs):
#     for i in range(int(times)):
#         if rvalue==True:
#             rc, opt = fuc(*args, **kwargs)
#         else:
#             fuc(*args, **kwargs)


def case():
    log.info("1> 开启签名认证")
    rc, opt = s3_common.set_oss_http_auth("1")
    time.sleep(12)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "Open sig-mode failed!")

    log.info("2> 创建账户")
    account_name = FILE_NAME + "_account1"
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create account failed!!!")

    log.info("3> 创建证书")
    rc, certificate_id, sk = s3_common.add_certificate(account_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    log.info("4> 上传桶")
    bucket_name_lst = []
    for i in range(2):
        bucket_name = FILE_NAME + '_bucket_%d' % i
        bucket_name = bucket_name.replace('_', '-')
        bucket_name_lst.append(bucket_name)
        rc, opt = s3_common.add_bucket_by_sk(
            bucket_name, certificate_id, sk, complex=True)
        judge_result(rc, FILE_NAME)
        print opt
        common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)
        rc, opt = s3_common.check_bucket_by_sk(bucket_name, certificate_id, sk)
        judge_result(rc, FILE_NAME)
        print opt
        common.judge_rc(rc, 0, "check bucket %s failed!!!" % bucket_name)

    log.info("5> 获取桶列表")
    rc, opt = s3_common.get_all_bucket_by_sk(certificate_id, sk)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "get bucket")

    log.info("6> 关闭签名认证")
    rc, opt = s3_common.set_oss_http_auth("0")
    judge_result(rc, FILE_NAME)
    time.sleep(12)
    common.judge_rc(rc, 0, "Close sig-mode failed!")


def main():
    rc, opt = s3_common.set_oss_http_auth("0")
    time.sleep(12)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "Close sig-mode failed!")
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s succeed!' % FILE_NAME)
    result.result(FILE_NAME, "0")


if __name__ == '__main__':
    common.case_main(main)

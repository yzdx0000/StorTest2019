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
# date 2018-09-08
# @summary：
#    签名认证模式下，桶操作。
# @steps:
#    1、开启签名认证
#    2、创建账户；
#    3、创建证书；
#    4、上传桶；
#    5、错误sig，GET桶列表；
#    6、关闭签名认证
#    7、清理桶；
#    8、删除证书及账户
#
##########################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"
BUCKET_NUM = 2


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, "-1")

# 获取sig函数


def create_sig(sk, StringToSign):
    sig = s3_common.mk_sig(sk, StringToSign)
    sig = s3_common.mk_sig_code(sig)
    return sig

# 命令执行结果判断


def juge(output):
    result_sig = output[output.find("1.1 ") + 4:][:3]
    print "result:%s" % result_sig
    if result_sig == '403':
        return 0
    else:
        return -1


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
    for i in range(BUCKET_NUM):
        bucket_name = FILE_NAME + '_bucket_%d' % i
        bucket_name = bucket_name.replace('_', '-')
        bucket_name_lst.append(bucket_name)
        rc, opt = s3_common.add_bucket_by_sk(bucket_name, certificate_id, sk)
        judge_result(rc, FILE_NAME)
        print opt
        common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)

    log.info("5> 错误sig获取桶列表")
    string = "GET" + "\n" + "" + "\n" + "" + "\n" + "" + "\n" + "" + "/"
    sig = create_sig(sk, string)
    rc1, opt1 = s3_common.get_all_bucket_by_sig(certificate_id, " ")
    rc2, opt2 = s3_common.get_all_bucket_by_sig(
        certificate_id, sig + "-112sdf")
    rc3, opt3 = s3_common.get_all_bucket_by_sig(
        certificate_id, sig + "#$%^@%$")

    if (juge(opt1) == 0 and juge(opt2) == 0 and juge(opt3) == 0):
        log.info("bucket-list delete failed!")
        log.info("testcase %s success!" % FILE_NAME)
        result.result(FILE_NAME, "0")
    else:
        log.info("bucket-list delete failed!")
        result.result(FILE_NAME, "-1")
        common.judge_rc(-1, 0, "testcase %s failed!" % FILE_NAME)

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

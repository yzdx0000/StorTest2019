#! /usr/bin/python
# -*- coding:utf-8 -*-
#**********************************************#
# 标题：功能测试，用例编号29-0-17-12
# 使用方法：python 29-0-17-12_wjl.py
# 在http模式下，获取桶配额操作。日志打印在屏幕上。
# 作者：王建磊
# 创建时间：2018/03/14
#**********************************************#
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

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"
QUOTA = "2097152"

# 创建账户及证书


def create_acc_cer():
    log.info("2> 创建账户")
    account_name = FILE_NAME + "_account1"
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create account failed!!!")
    log.info("3> 创建证书")
    rc, ak, sk = s3_common.add_certificate(account_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")
    return ak, sk

# 获取sig函数


def create_sig(sk, StringToSign):
    sig = s3_common.mk_sig(sk, StringToSign)
    sig = s3_common.mk_sig_code(sig)
    return sig


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, "-1")

# 获取桶配额函数


def bucket_get_quota(bucketname, AK, sig):
    rc, opt = s3_common.get_bucket_quota_by_sig(bucketname, AK, sig)
    return rc, opt

# 设置桶配额函数


def bucket_set_quota(bucketname, AK, quota, sig):
    rc, opt = s3_common.update_bucket_quota_by_sig(bucketname, AK, quota, sig)
    return rc, opt


def case():
    log.info("1> 开启签名认证")
    rc, opt = s3_common.set_oss_http_auth("1")
    time.sleep(12)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "Open sig-mode failed!")

    # 创建账户、证书
    log.info("2> 创建账户、证书")
    ak, sk = create_acc_cer()
    # 创建桶
    log.info("3> 创建桶")
    log.info("bucket create operation:")
    bucket_name = FILE_NAME + '_bucket_0'
    bucket_name = bucket_name.replace('_', '-')
    object_name = FILE_NAME + '_object_0'
    rc, opt = s3_common.add_bucket_by_sk(bucket_name, ak, sk)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)
    # 设置桶的配额
    log.info("4> 设置桶的配额")
    StringToSign = "PUT" + "\n" + "" + "\n" + "application/x-www-form-urlencoded" + \
        "\n" + "" + "\n" + "" + "/" + bucket_name + "?quota"
    sig = create_sig(sk, StringToSign)
    log.info("******设置桶配额结果******")
    rc1, opt1 = bucket_set_quota(bucket_name, ak, QUOTA, sig)
    teg1 = opt1[opt1.find("HTTP/1.1 ") + 9:][:3]
    log.info("******设置桶配额结果******")

    # 获取桶的配额
    log.info("5> 非法sig获取桶的配额")
    StringToSign = "GET" + "\n" + "" + "\n" + "" + "\n" + \
        "" + "\n" + "" + "/" + bucket_name + "?quota"
    sig = create_sig(sk, StringToSign)
    log.info("******查询桶配额结果******")
    rc1, opt1 = bucket_get_quota(bucket_name, ak, "q1" + sig + "1q")
    rc2, opt2 = bucket_get_quota(bucket_name, ak, "#$%@" + sig + "@#$%")
    rc3, opt3 = bucket_get_quota(bucket_name, ak, " " + sig + " ")
    log.info("******查询桶配额结果******")

    print opt1, opt2, opt3

    if (opt1 is None and opt2 is None and opt3 is None):
        pass
    else:
        result.result(FILE_NAME, "-1")
        common.judge_rc(-1, 0, "%s failed!" % FILE_NAME)

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

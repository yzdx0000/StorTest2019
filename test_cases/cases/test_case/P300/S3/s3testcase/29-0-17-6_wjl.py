#! /usr/bin/python
# -*- coding:utf-8 -*-
#**********************************************#
# 标题：功能测试，用例编号29-0-17-6
# 使用方法：python 29-0-17-6_wjl.py
# 在http模式下，创建桶和对象后，使用错误的sig删除桶操作。日志打印在屏幕上。
# 作者：王建磊
# 创建时间：2018/03/12
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
import result  # 返回值打印模块
import prepare_clean
import get_config
import log
import s3_common
import common
import utils_path

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"


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

# 删除桶命函数


def bucket_del(bucketname, AK, sig):
    rc, opt = s3_common.del_bucket_by_sig(bucketname, AK, sig)
    return rc, opt

# 结果判断函数


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
# 创建账户
    AK, SK = create_acc_cer()
# 创建测试桶
    log.info("bucket create operation:")
    bucket_name = FILE_NAME + '_bucket_0'
    bucket_name = bucket_name.replace('_', '-')
    rc, opt = s3_common.add_bucket_by_sk(bucket_name, AK, SK)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)
# 错误sig删除桶
    log.info("4> 删除桶")
    string = "DELETE" + "\n" + "" + "\n" + "" + \
        "\n" + "" + "\n" + "" + "/" + bucket_name
    sig = create_sig(SK, string)
    rc1, opt1 = bucket_del(bucket_name, AK, sig + "s")
    rc2, opt2 = bucket_del(bucket_name, AK, "")
    rc3, opt3 = bucket_del(bucket_name, AK, sig[0:-2])
    if (juge(opt1) == 0 and juge(opt2) == 0 and juge(opt3) == 0):
        log.info("bucket delete failed!")
        log.info("testcase %s success!" % FILE_NAME)
        result.result(FILE_NAME, "0")
    else:
        log.info("bucket delete failed!")
        result.result(FILE_NAME, "-1")
        log.info("testcase %s failed!" % FILE_NAME)

    log.info("5> 关闭签名认证")
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
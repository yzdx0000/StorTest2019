#! /usr/bin/python
# -*- coding:utf-8 -*-
#**********************************************#
# 标题：功能测试，用例编号29-0-17-32
# 使用方法：python 29-0-17-32_wjl.py
# 在http模式下，错误sig上传对象操作。
# 作者：王建磊
# 创建时间：2018/08/14
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
account_name = FILE_NAME + "_" + "account"
email = account_name + "@sugon.com"

# 创建账户及证书


def create_acc_cer(account_name, email):
    rc, account_id = s3_common.add_account(account_name, email, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create account failed!!!")
    rc, ak, sk = s3_common.add_certificate(account_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")
    return ak, sk, account_id

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

# 结果判断函数


def juge(output):
    result_sig = output[output.find("1.1 ") + 4:][:3]
    print "result:%s" % result_sig
    if result_sig == '403':
        return 0
    else:
        return -1


def case():
    # 打开签名认证
    log.info("1> 关闭签名认证")
    rc, opt = s3_common.set_oss_http_auth("1")
    time.sleep(12)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "Open sig-mode failed!")

    # 创建账户a、b
    log.info("2> 创建账户")
    ak, sk, account_id = create_acc_cer(account_name, email)

    # 账户a\b,中分别创建桶
    log.info("3> 在账户中创建桶")
    log.info("bucket create operation:")
    bucket_name = FILE_NAME + '_bucket'
    bucket_name = bucket_name.replace('_', '-')
    object_name = FILE_NAME + '_object'
    rc1, opt1 = s3_common.add_bucket_by_sk(bucket_name, ak, sk)
    judge_result(rc1, FILE_NAME)
    common.judge_rc(rc1, 0, "add bucket %s failed!!!" % bucket_name)

    # 创建对象buc_a>obj_a,acc_b>obj_b
    log.info("4> 在账户的桶中创建对象,指定对象的内容。")
    string = "PUT" + "\n" + "" + "\n" + "application/x-www-form-urlencoded" + \
             "\n" + "" + "\n" + "" + "/" + bucket_name
    sig = create_sig(sk, string)
    rc1, opt1 = s3_common.add_object_info(
        bucket_name, object_name, "helloworld", ak, "  ")
    rc2, opt2 = s3_common.add_object_info(
        bucket_name, object_name, "helloworld", ak, "kglera324")
    rc3, opt3 = s3_common.add_object_info(
        bucket_name, object_name, "helloworld", ak, "#@%$#%^&")
    rc4, opt4 = s3_common.add_object_info(
        bucket_name, object_name, "helloworld", ak, sig + "dsfg")
    if "403" in opt1 and "403" in opt2 and "403" in opt3 and "403" in opt4:
        pass
    else:
        judge_result(-1, FILE_NAME)
        common.judge_rc(-1, 0, "%s failed!" % FILE_NAME)

    log.info("5> 关闭签名认证")
    rc, opt = s3_common.set_oss_http_auth("0")
    time.sleep(12)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "Open sig-mode failed!")


def main():
    rc, opt = s3_common.set_oss_http_auth("0")
    time.sleep(12)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "Close sig-mode failed!")
    prepare_clean.s3_test_prepare(FILE_NAME, [email])
    case()
    prepare_clean.s3_test_clean([email])
    log.info('%s succeed!' % FILE_NAME)
    result.result(FILE_NAME, "0")


if __name__ == '__main__':
    common.case_main(main)

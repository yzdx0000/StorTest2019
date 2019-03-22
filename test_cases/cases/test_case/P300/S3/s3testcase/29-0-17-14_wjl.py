#! /usr/bin/python
# -*- coding:utf-8 -*-
#**********************************************#
# 标题：功能测试，用例编号29-0-17-14
# 使用方法：python 29-0-17-14_wjl.py
# 在http模式下，获取桶的存量信息操作。
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


FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"

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

# 创建文件函数


def create_file(obj_path, amount):
    a = [0 for x in range(1024 * 1024)]
    for i in range(len(a) - 10):
        a[i] = 'a'
    for j in range(10):
        data = random.randint(0, 9)
        a[len(a) - 10 + j] = str(data)
    a = "".join(a)
    f = open(obj_path, 'a+')
    for k in range(amount):
        f.write(a)
    f.close()

# 获取桶存量信息函数


def bucket_get_storageinfo(bucketname, ak, sig):
    rc, opt = s3_common.get_bucket_storageinfo_by_sig(bucketname, ak, sig)
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

    # 获取桶的存量信息
    log.info("4> 获取桶的存量信息")
    StringToSign = "GET" + "\n" + "" + "\n" + "" + "\n" + \
        "" + "\n" + "" + "/" + bucket_name + "?storageinfo"
    sig = create_sig(sk, StringToSign)
    log.info("******获取桶存量信息结果******")
    rc, storageinfo1 = bucket_get_storageinfo(bucket_name, ak, sig)
    log.info("******获取桶存量信息结果******")

    # 上传对象
    log.info("5> 上传对象")
    StringToSign = "PUT" + "\n" + "" + "\n" + "" + "\n" + \
        "" + "\n" + "" + "/" + bucket_name + "/" + object_name
    sig = create_sig(sk, StringToSign)
    create_file(FILE_NAME, 1)
    log.info("******上传对象结果******")
    rc, opt = s3_common.add_object_by_sk(
        bucket_name, object_name, FILE_NAME, ak, sk)
    common.run_command_shot_time("rm %s" % FILE_NAME)
    log.info("******上传对象结果******")

    # 第二次获取桶的存量信息
    log.info("6> 第二次获取桶的存量信息")
    StringToSign = "GET" + "\n" + "" + "\n" + "" + "\n" + \
        "" + "\n" + "" + "/" + bucket_name + "?storageinfo"
    sig = create_sig(sk, StringToSign)
    log.info("******第二次获取桶存量信息结果******")
    rc, storageinfo2 = bucket_get_storageinfo(bucket_name, ak, sig)
    log.info("******第二次获取桶存量信息结果******")

    # 结果判断
    if storageinfo1 == "0" and storageinfo2 == "1048576":
        pass
    else:
        result.result(FILE_NAME, "-1")
        common.judge_rc(-1, 0, "%s failed!" % FILE_NAME)

    log.info("7> 关闭签名认证")
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

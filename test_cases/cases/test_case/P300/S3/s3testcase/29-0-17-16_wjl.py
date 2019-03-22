#! /usr/bin/python
# -*- coding:utf-8 -*-
#**********************************************#
# 标题：功能测试，用例编号29-0-17-16
# 使用方法：python 29-0-17-16_wjl.py
# 在http模式下，设置桶配额操作。
# 作者：王建磊
# 创建时间：2018/09/10
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


# 结果判断函数
def juge(output):
    result_sig = output[output.find("1.1 ") + 4:][:3]
    print "result:%s" % result_sig
    if result_sig == '403':
        return 0
    else:
        return -1


# 获取桶配额函数
def bucket_get_quota(bucketname, AK, sig):
    rc, opt = s3_common.get_bucket_quota_by_sig(bucketname, AK, sig)
    return rc, opt


# 设置桶配额函数
def bucket_set_quota(bucketname, AK, quota, sig):
    rc, opt = s3_common.update_bucket_quota_by_sig(bucketname, AK, quota, sig)
    return rc, opt


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


def case():
    log.info("1> 开启签名认证")
    rc, opt = s3_common.set_oss_http_auth("1")
    time.sleep(12)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "Open sig-mode failed!")

    # 创建账户、证书
    ak, sk = create_acc_cer()
    # 创建桶
    log.info("4> 创建桶")
    log.info("bucket create operation:")
    bucket_name = FILE_NAME + '_bucket_0'
    bucket_name = bucket_name.replace('_', '-')
    object_name = FILE_NAME + '_object_0'
    rc, opt = s3_common.add_bucket_by_sk(bucket_name, ak, sk)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)
    # 设置桶的配额
    log.info("5> 设置桶的配额")
    StringToSign = "PUT" + "\n" + "" + "\n" + "application/x-www-form-urlencoded" + \
        "\n" + "" + "\n" + "" + "/" + bucket_name + "?quota"
    sig = create_sig(sk, StringToSign)
    log.info("******设置桶配额结果******")
    rc1, opt1 = bucket_set_quota(bucket_name, ak, QUOTA, sig)
    teg1 = opt1[opt1.find("HTTP/1.1 ") + 9:][:3]
    log.info("******设置桶配额结果******")

    # 获取桶的配额
    log.info("6> 获取桶的配额")
    StringToSign = "GET" + "\n" + "" + "\n" + "" + "\n" + \
        "" + "\n" + "" + "/" + bucket_name + "?quota"
    sig = create_sig(sk, StringToSign)
    log.info("******查询桶配额结果******")
    rc2, opt2 = bucket_get_quota(bucket_name, ak, sig)
    log.info("******查询桶配额结果******")

    # 上传对象
    log.info("7> 上传对象")
    create_file(FILE_NAME + "_big", 3)
    create_file(FILE_NAME + "_little", 1)
    log.info("******上传大对象结果******")
    rc3, opt3 = s3_common.add_object_by_sk(
        bucket_name, object_name, FILE_NAME + "_big", ak, sk)
    common.run_command_shot_time("rm %s" % FILE_NAME + "_big")
    teg3 = opt3[opt3.find("HTTP/1.1 403") + 9:][:3]
    log.info("******上传大对象结果******")

    log.info("******上传小对象结果******")
    rc4, opt4 = s3_common.add_object_by_sk(
        bucket_name, object_name, FILE_NAME + "_little", ak, sk)
    common.run_command_shot_time("rm %s" % FILE_NAME + "_little")
    teg4 = opt4[opt4.find("HTTP/1.1 200") + 9:][:3]
    log.info("******上传小对象结果******")

    print teg1, opt2, teg3, teg4
    if teg1 == "200" and opt2 == QUOTA and teg3 == "403" and teg4 == "200":
        pass
    else:
        result.result(FILE_NAME, "-1")
        common.judge_rc(-1, 0, "%s failed!" % FILE_NAME)

    log.info("8> 关闭签名认证")
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

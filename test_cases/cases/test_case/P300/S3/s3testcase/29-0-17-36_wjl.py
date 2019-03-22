#! /usr/bin/python
# -*- coding:utf-8 -*- 
#**********************************************#
#标题：功能测试，用例编号29-0-17-36
#使用方法：python 29-0-17-36_wjl.py
#在http模式下，设置/获取桶/对象元数据操作。
#作者：王建磊
#创建时间：2018/03/12
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
sys.path.append(pwd+"/S3Lib")

import utils_path
import common
import s3_common
import log
import get_config
import prepare_clean
import result

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"
META_NMB = "5"
meta_str_list = ["key1:value1", "key2:value2"]


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

    log.info("4> 上传添加元数据的桶，携带5组元数据")
    bucket_name = FILE_NAME + '_bucket'
    bucket_name = bucket_name.replace('_', '-')
    rc, opt = s3_common.add_bucket_with_meta_by_sk(bucket_name, certificate_id, sk, META_NMB)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)

    log.info("5> 上传添加元数据的对象，携带5组元数据")
    object_name = FILE_NAME + '_object'
    create_file(FILE_NAME, 1)
    rc, opt = s3_common.add_object_with_meta_by_sk(bucket_name, object_name, FILE_NAME, certificate_id, sk, META_NMB)
    common.run_command_shot_time("rm %s" % FILE_NAME)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)

    log.info("5> 获取对象元数据")
    stringtosign = ("HEAD" + "\n" + "" + "\n" + "" + "\n" + "" + "\n" + ""+ "/" + bucket_name+"/"+object_name)
    sig = s3_common.mk_sig(sk, stringtosign)
    sig = s3_common.mk_sig_code(sig)
    rc, opt = s3_common.get_object_meta(bucket_name, object_name, certificate_id, sig)
    meta_num = opt.count("x-amz-meta-")
    print "meta_num: ", meta_num
    if str(meta_num) == META_NMB:
        rc = 0
    else:
        rc = -1
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "get bucket failed!")

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
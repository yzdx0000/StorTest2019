#! /usr/bin/python
# -*- coding:utf-8 -*-
#**********************************************#
# 标题：功能测试，用例编号29-0-17-2
# 使用方法：python 29-0-17-2_wjl.py
# 在http模式下，使用错误的sig创建桶操作。
# 作者：王建磊
# 创建时间：2018/03/09
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

##########################################################################
#
# Author: wangjianlei
# date 2018-09-07
# @summary：
#    签名认证模式下，错误sig进行桶操作。
# @steps:
#    1、开启签名认证
#    2、创建账户；
#    3、创建证书；
#    4、错误sig上传桶；
#    5、关闭签名认证；
#    6、清理环境
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


def judge_data(output, string):
    result_sig = output[output.find("1.1 ") + 4:][:3]
    if result_sig == string:
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
    bucket_name = FILE_NAME + '_bucket'
    bucket_name = bucket_name.replace('_', '-')
    bucket_name_lst.append(bucket_name)
    rc, cre_buc_opt1 = s3_common.add_bucket_by_sk(
        bucket_name + "1", certificate_id, sk + " ")
    rc1 = judge_data(cre_buc_opt1, "403")
    rc, cre_buc_opt2 = s3_common.add_bucket_by_sk(
        bucket_name + "2", certificate_id, sk + "QWEqwe")
    rc2 = judge_data(cre_buc_opt2, "403")
    rc, cre_buc_opt3 = s3_common.add_bucket_by_sk(
        bucket_name + "3", certificate_id, sk + "1234ww")
    rc3 = judge_data(cre_buc_opt3, "403")

    log.info("5> 关闭签名认证")
    rc, opt = s3_common.set_oss_http_auth("0")
    judge_result(rc, FILE_NAME)
    time.sleep(12)
    common.judge_rc(rc, 0, "Close sig-mode failed!")
    return (rc1 and rc2 and rc3)


def main():
    rc, opt = s3_common.set_oss_http_auth("0")
    time.sleep(12)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "Close sig-mode failed!")

    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])

    output = case()
    print output, "output"
    if output == 0:
        log.info('%s succeed!' % FILE_NAME)
        result.result(FILE_NAME, "0")
    else:
        result.result(FILE_NAME, "-1")
        log.error('%s failed!' % FILE_NAME)

    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])


if __name__ == '__main__':
    common.case_main(main)

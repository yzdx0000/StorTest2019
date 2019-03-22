#!/usr/bin/python
# -*-coding:utf-8 -*
import os

import utils_path
import common
import s3_common
import log
import prepare_clean
import result
import time
####################################################################################
#
# Author: lichengxu
# date 2018-11-17
# @summary：
#    删除不存在的桶
# @steps:
#    1、创建账户；
#    2、检查账户是否存在
#    3、创建证书；
#    4、删除桶（该桶尚未创建）
#    5、清理环境
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, -1)


def case():
    log.info("1> 创建账户")
    account_name = FILE_NAME + "_account1"
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add_account %s failed!!!" % account_name)

    log.info("2> 检查账户是否存在")
    rc, stdout = s3_common.find_account(ACCOUNT_EMAIL)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "find account %s failed!!!" % ACCOUNT_EMAIL)

    log.info("3> 创建证书")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    log.info("4> 删除桶")
    bucket_name = FILE_NAME + '_bucket_1'
    bucket_name = bucket_name.replace('_', '-')
    """检查桶是否存在"""
    rc, stdout = s3_common.check_bucket(bucket_name, certificate_id,  exe_node_ip=None)
    common.judge_rc(rc, -1, "check bucket %s failed!!!" % bucket_name)

    """删除桶——失败"""
    rc, stdout = s3_common.del_bucket(bucket_name, certificate_id)
    common.judge_rc(rc, -1, "delete bucket %s failed, bucket is not exist." % bucket_name)

    log.info("8> 获取账户内所有的桶")
    rc, bucket_name_lst = s3_common.get_all_bucket_name(certificate_id)
    common.judge_rc(rc, 0, "get bucket failed!!!")
    if len(bucket_name_lst) == 0:
        log.info("account has zero bucket!")

    log.info('%s success!' % FILE_NAME)
    result.result(FILE_NAME, 0)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s finish!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

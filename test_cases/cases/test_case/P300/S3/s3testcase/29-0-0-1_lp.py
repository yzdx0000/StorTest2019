#!/usr/bin/python
# -*-coding:utf-8 -*
import os

import utils_path
import common
import s3_common
import log
import prepare_clean
import result
####################################################################################
#
# Author: liuping,已通
# date 2018-09-06
# @summary：
#    获取桶列表。
# @steps:
#    1、创建账户；
#    2、创建证书；
#    3、上传桶；
#    4、获取桶列表
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

    bucket_name_lst = []
    log.info("4> 上传桶")
    for i in range(50):
        bucket_name = FILE_NAME + '_bucket_%d' % i
        bucket_name = bucket_name.replace('_','-')
        bucket_name_lst.append(bucket_name)
        rc, stdout = s3_common.add_bucket(bucket_name, certificate_id, exe_node_ip=None)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)
        rc, stdout = s3_common.check_bucket(bucket_name, certificate_id,  exe_node_ip=None)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "check bucket %s failed!!!" % bucket_name)

    log.info("5> 获取桶列表")
    rc, stdout = s3_common.get_all_bucket(certificate_id, exe_node_ip=None)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "get bucket failed!!!")

    log.info('%s success!' % FILE_NAME)
    result.result(FILE_NAME, 0)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s finish!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

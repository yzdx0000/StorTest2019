#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import os
import sys
import json

import utils_path
import common
import s3_common
import log
import get_config
import prepare_clean
import result

##########################################################################
#
# Author: zhanghan
# date 2018-09-08
# @summary：
#    验证账户配额可以被修改且修改生效
# @steps:
#    1、创建账户；
#    2、修改账户配额；
#    3、查询账户配额；
#    4、检验查询到的账户配额和修改值是否相同
#    5、清理环境
#
# @changelog：
##########################################################################

# 全局变量
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, "-1")


def case():
    log.info("1> 创建账户")
    account_name = FILE_NAME + "_account1"
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create account failed!!!")

    log.info("2> 修改账户配额")
    account_quota_set = 3000
    rc, output = s3_common.update_account(account_id, account_quota_set)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "update account quota failed!!!")

    log.info("3> 查询账户配额")
    rc, account_quota_get = s3_common.get_account_quote_by_email(ACCOUNT_EMAIL)

    if account_quota_get == account_quota_set:
        log.info("the get value and the set value is %s" % account_quota_get)
        log.info("检验获取到的配额和设置的配额相同")
    else:
        log.info("检验获取到的配额和设置的配额不同")
        check_rc = -1
        judge_result(check_rc, FILE_NAME)
        common.judge_rc(
            check_rc, 0, "check account quota failed, "
            "the get value is not the same with the sey value!!!")

    log.info("4> 用例%s执行成功" % FILE_NAME)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s finished!' % FILE_NAME)
    result.result(FILE_NAME, "0")


if __name__ == '__main__':
    common.case_main(main)

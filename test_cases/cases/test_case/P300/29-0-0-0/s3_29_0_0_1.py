# -*-coding:utf-8 -*
import os
import random

import utils_path
import common
import s3_common
import log
import get_config
import prepare_clean

####################################################################################
#
# Author: baorb
# date 2018-01-19
# @summary：
#    基本桶操作。
# @steps:
#    1、创建账户；
#    2、创建证书；
#    3、上传桶；
#    4、检查桶；
#    5、清理桶；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"


def case():
    log.info("1> 创建账户")
    account_name = FILE_NAME + "_account1"
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    common.judge_rc(rc, 0, "create account failed!!!")

    log.info("2> 创建证书")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    log.info("3> 上传桶")
    bucket_name_lst = []
    for i in range(50):
        bucket_name = FILE_NAME + '_bucket_%d' % i
        bucket_name_lst.append(bucket_name)
        rc = s3_common.add_bucket(bucket_name, certificate_id)
        common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)
        rc = s3_common.check_bucket(bucket_name, certificate_id)
        common.judge_rc(rc, 0, "check bucket %s failed!!!" % bucket_name)

    log.info("4> 获取桶列表")
    rc = s3_common.get_all_bucket(certificate_id)
    common.judge_rc(rc, 0, "get bucket")


def main():
    prepare_clean.s3_test_prepare(FILE_NAME)
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
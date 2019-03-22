#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import os
import sys

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
#    验证桶的配额能生效
# @steps:
#    1、创建账户；
#    2、给账户添加证书；
#    3、上传桶；
#    4、设置桶的配额
#    5、向桶中写入超过配额大小的内容
#    6、清理环境
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

    log.info("2> 创建证书")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    log.info("3> 上传桶")
    # obj_node = common.Node()
    # ooss_node_lst = s3_common.get_ooss_node_ids()
    # oossid = ooss_node_lst[0]
    # oossip = obj_node.get_node_ip_by_id(oossid)
    bucket_name = FILE_NAME + '_bucket1'
    bucket_name = bucket_name.replace('_', '-')
    rc, stdout = s3_common.add_bucket(bucket_name, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add bucket failed!!!")

    log.info("4> 设置桶的配额")
    quota = 2000
    rc, stdout = s3_common.update_bucket_quota(
        bucket_name, certificate_id, quota)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "update bucket quota failed!!!")

    log.info("5> 向桶中写入超过配额大小的内容")
    file_path = "/tmp/file%s" % FILE_NAME
    size = 3  # 以M为单位
    rc, stdout = s3_common.create_file_m(file_path, size)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create file failed!!!")

    object_name = FILE_NAME + '_object1'
    rc, stdout = s3_common.add_object(
        bucket_name, object_name, file_path, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, -1, "bucket quota don't work!!!")

    log.info("6> 用例%s执行成功" % FILE_NAME)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s finished!' % FILE_NAME)
    result.result(FILE_NAME, "0")


if __name__ == '__main__':
    common.case_main(main)

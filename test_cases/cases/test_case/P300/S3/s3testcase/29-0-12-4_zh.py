#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import os
import sys
import random

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
# date 2018-09-11
# @summary：
#    验证单个对象上传最大支持5GB
# @steps:
#    1、创建账户；
#    2、给账户添加证书；
#    3、上传桶；
#    4、向桶中上传5G大小的对象，预期成功
#    5、向桶中上传5G+1B大小的对象，预期失败
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

    log.info("4> 向桶中上传5G大小的对象")
    file_path_1 = "/tmp/file%s_5G" % FILE_NAME
    size_1 = 5120  # 以M为单位
    rc, stdout = s3_common.create_file_m(file_path_1, size_1)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create file failed!!!")

    object_name_1 = FILE_NAME + '_object1'
    rc, stdout = s3_common.add_object(
        bucket_name, object_name_1, file_path_1, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "put object failed!!!")

    log.info("5> 向桶中上传5G+1B大小的对象")
    file_path_2 = "/tmp/file%s_5Gand1B" % FILE_NAME
    size_2 = 5121  # 以M为单位
    rc, stdout = s3_common.create_file_m(file_path_2, size_2)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create file failed!!!")

    object_name_2 = FILE_NAME + '_object2'
    rc, stdout = s3_common.add_object(
        bucket_name, object_name_2, file_path_2, certificate_id)
    if rc == 0:
        rc_jugge = -1
    else:
        rc_jugge = 0
    judge_result(rc_jugge, FILE_NAME)
    common.judge_rc(
        rc, -1, "duo to over the max size, the object should not put success!!!")

    log.info("6> 用例%s执行成功" % FILE_NAME)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s finished!' % FILE_NAME)
    result.result(FILE_NAME, "0")


if __name__ == '__main__':
    common.case_main(main)

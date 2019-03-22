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
#    验证桶的acl上限个数为100
# @steps:
#    1、创建账户；
#    2、给账户添加证书；
#    3、上传桶；
#    4、创建目标账户及目标证书
#    5、设置桶的acl，设置100条
#    6、重新设置桶的acl，设置101条
#    7、删除目标账户
#    8、清理环境
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

    log.info("4> 创建目标账户及目标证书")
    des_account_num = 101
    des_account_pre = FILE_NAME + "_des_acc_"
    des_account_name_list = []
    des_account_email_list = []
    des_account_id_list = []
    for i in range(1, des_account_num + 1):
        log.info("创建目标账户")
        des_account_name_tmp = des_account_pre + str(i)
        des_account_name_list.append(des_account_name_tmp)
        des_account_email_tmp = des_account_name_tmp + "@sugon.com"
        des_account_email_list.append(des_account_email_tmp)

        rc, account_id_tmp = s3_common.add_account(
            des_account_name_tmp, des_account_email_tmp, 0)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "create destination account failed!!!")
        des_account_id_list.append(account_id_tmp)

        rc, certificate_id_tmp, certificate_tmp = s3_common.add_certificate(
            account_id_tmp)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "create certificate failed!!!")

    log.info("5> 设置桶的acl，设置100条")
    operation = "READ"
    des_account_info_list = []
    for i in range(0, des_account_num - 1):
        account_id_curr = des_account_id_list[i]
        account_email_curr = des_account_email_list[i]
        des_account_info_list.append(
            {'account_id': account_id_curr, 'account_email': account_email_curr})
    rc, output = s3_common.set_bucket_acl_multi(
        bucket_name, certificate_id, account_id, ACCOUNT_EMAIL, des_account_info_list, operation)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "set bucket multi acls failed!!!")

    log.info("6> 重新设置桶的acl，设置101条")
    operation = "READ"
    des_account_info_list = []
    for i in range(0, des_account_num):
        account_id_curr = des_account_id_list[i]
        account_email_curr = des_account_email_list[i]
        des_account_info_list.append(
            {'account_id': account_id_curr, 'account_email': account_email_curr})
    rc, output = s3_common.set_bucket_acl_multi(
        bucket_name, certificate_id, account_id, ACCOUNT_EMAIL, des_account_info_list, operation)
    if rc != -1:
        result.result(FILE_NAME, "-1")
    else:
        log.info("success, bucket acls number upper limit take effect")
        pass
    common.judge_rc(
        rc, -1, "failed, bucket acls number upper limit don't work!!!")

    log.info("7> 删除目标账户")
    s3_common.cleaning_environment(des_account_email_list)

    log.info("8> 用例%s执行成功" % FILE_NAME)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s finished!' % FILE_NAME)
    result.result(FILE_NAME, "0")


if __name__ == '__main__':
    common.case_main(main)

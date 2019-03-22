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
#    创建对象名称长度设定
# @steps:
#    1、创建账户；
#    2、检查账户是否存在
#    3、创建证书；
#    4、创建桶
#    5、创建对象名称长度分别为1/2/1023/1024/1025 字节长度
#    6、清理环境
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

    bucket_name_lst_base = []
    log.info("4> 创建桶")
    bucket_name = FILE_NAME + '_bucket_1'
    bucket_name = bucket_name.replace('_', '-')
    bucket_name_lst_base.append(bucket_name)
    rc, stdout = s3_common.add_bucket(bucket_name, certificate_id, exe_node_ip=None)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)
    rc, stdout = s3_common.check_bucket(bucket_name, certificate_id, exe_node_ip=None)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "check bucket %s failed!!!" % bucket_name)

    log.info("5> 创建对象")
    object_name_1 = "a"
    object_name_2 = "aa"
    object_name_1023 = "a" * 1023
    object_name_1024 = "a" * 1024
    object_name_1025 = "a" * 1025
    """创建10M文件"""
    test_path = '/tmp/s3test'
    if os.path.exists(test_path):
        cmd = "rm -rf %s" % test_path
        common.run_command_shot_time(cmd)
    os.mkdir(test_path)
    file_path = os.path.join(test_path, 'file_10m')
    rc, stdout = s3_common.create_file_m(file_path, 10)
    common.judge_rc(rc, 0, "create file %s failed!!!" % file_path)
    """获取桶内所有对象"""
    rc, object_name_lst = s3_common.get_all_object_in_bucket(bucket_name, certificate_id)
    common.judge_rc(rc, 0, "get all object in bucket %s failed!!!" % bucket_name)
    if object_name_1 not in object_name_lst:
        rc, stdout = s3_common.add_object(bucket_name, object_name_1, file_path, certificate_id)
        common.judge_rc(rc, 0, "add object %s failed!!!" % object_name_1)
        log.info("%s put success!" % object_name_1)
    if object_name_2 not in object_name_lst:
        rc, stdout = s3_common.add_object(bucket_name, object_name_2, file_path, certificate_id)
        common.judge_rc(rc, 0, "add object %s failed!!!" % object_name_2)
        log.info("%s put success!" % object_name_2)
    if object_name_1023 not in object_name_lst:
        rc, stdout = s3_common.add_object(bucket_name, object_name_1023, file_path, certificate_id)
        common.judge_rc(rc, 0, "add object %s failed!!!" % object_name_1023)
        log.info("%s put success!" % object_name_1023)
    if object_name_1024 not in object_name_lst:
        rc, stdout = s3_common.add_object(bucket_name, object_name_1024, file_path, certificate_id)
        common.judge_rc(rc, -1, "add object %s failed!!!" % object_name_1024)
        log.info("%s put failed!" % object_name_1024)
    if object_name_1025 not in object_name_lst:
        rc, stdout = s3_common.add_object(bucket_name, object_name_1025, file_path, certificate_id)
        common.judge_rc(rc, -1, "add object %s failed!!!" % object_name_1025)
        log.info("%s put failed!" % object_name_1025)

    log.info("6> 获取账户内所有的桶")
    rc, bucket_name_lst = s3_common.get_all_bucket_name(certificate_id)
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

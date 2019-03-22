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
#    验证桶的空间大小统计和对象个数统计正确
# @steps:
#    1、创建账户；
#    2、给账户添加证书；
#    3、上传桶；
#    4、向桶中上传多个对象
#    5、统计桶的空间大小及对象个数
#    6、验证桶的空间大小与对象个数与设置值是否相同
#    7、清理环境
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

    log.info("4> 向桶中上传多个对象")
    object_num_set = random.randint(1, 20)
    obj_size_all = 0
    for i in range(0, object_num_set):
        file_path = "/tmp/file%s_%s" % (FILE_NAME, str(i))
        size_tmp = random.randint(1, 30)       # 以M为单位
        obj_size_all = obj_size_all + size_tmp
        rc, stdout = s3_common.create_file_m(file_path, size_tmp)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "create file failed!!!")

        object_name = FILE_NAME + '_object' + str(i)
        rc, stdout = s3_common.add_object(
            bucket_name, object_name, file_path, certificate_id)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "bucket quota don't work!!!")

    log.info("5> 统计桶的空间大小及对象个数")
    rc, obj_num_get_list = s3_common.get_all_object_in_bucket(
        bucket_name, certificate_id)
    obj_num_get = len(obj_num_get_list)

    rc, buc_storage_size = s3_common.get_bucket_storageinfo(
        bucket_name, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "get bucket failed!!!")

    log.info("6> 验证桶的空间大小与对象个数与设置值是否相同")
    obj_size_all_set = obj_size_all * 1024 * 1024
    obj_size_all_get = buc_storage_size
    if (obj_size_all_set == int(obj_size_all_get)) and (
            object_num_set == obj_num_get):
        log.info(
            "the bucket storage is %d Byte, and the object number is %d" %
            (obj_size_all_set, object_num_set))
        log.info("check bucket storage and object number success!")
    else:
        log.info("check bucket storage and object number failed!")
        rc = -1
        common.judge_rc(
            rc, 0, "check bucket storage and object number failed!")

    log.info("7> 用例%s执行成功" % FILE_NAME)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s finished!' % FILE_NAME)
    result.result(FILE_NAME, "0")


if __name__ == '__main__':
    common.case_main(main)

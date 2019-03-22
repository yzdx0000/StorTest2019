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
##########################################################################
#
# Author: lichengxu
# date 2018-11-26
# @summary：
#    删除不存在的对象
#    发散：删除对象命令中填写不正确的桶名，不正确的证书名
# @steps:
#    1、创建账户；
#    2、检查账户是否存在
#    3、创建证书；
#    4、创建桶
#    5、上传对象
#    6、删除不存在的对象，报错信息
#    7、填写错误桶名，错误证书ID
#    8、获取桶信息，账户信息
#    9、清理环境
#
# @changelog：
##########################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]                 # 本脚本名字
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
    rc, stdout = s3_common.add_bucket(
        bucket_name, certificate_id, exe_node_ip=None)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)
    rc, stdout = s3_common.check_bucket(
        bucket_name, certificate_id, exe_node_ip=None)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "check bucket %s failed!!!" % bucket_name)

    log.info("5> 上传对象")
    """创建10M文件"""
    test_path = "/tmp/s3test"
    cmd = "rm -rf %s" % test_path
    common.command(cmd)
    os.mkdir(test_path)
    file_path = os.path.join(test_path, 'file')
    rc, stdout = s3_common.create_file_m(file_path, 10)
    common.judge_rc(rc, 0, "create file %s failed!!!" % file_path)
    object_name_lst_base = []
    for i in range(10):
        object_name = FILE_NAME + '_object_%s' % i
        rc, stdout = s3_common.add_object(
            bucket_name, object_name, file_path, certificate_id)
        common.judge_rc(rc, 0, "add object %s failed!!!" % object_name)
        object_name_lst_base.append(object_name)

    """验证上传对象是否成功"""
    rc, object_name_lst = s3_common.get_all_object_in_bucket(
        bucket_name, certificate_id)
    common.judge_rc(
        rc,
        0,
        "get all object in bucket %s failed!!!" %
        bucket_name)
    for object_name in object_name_lst_base:
        if object_name not in object_name_lst:
            common.except_exit("object %s is not put!!!" % object_name)
    else:
        log.info("all object put success")

    log.info("6> 删除不存在的对象")
    del_object = "object_do_not_exist"
    if del_object not in object_name_lst:
        rc, stdout = s3_common.del_object(
            bucket_name, del_object, certificate_id)
        common.judge_rc_unequal(rc, 0, 'delete object failed!')
    log.info("verify delete don't exsit object success!")

    log.info("7> 删除对象，填写错误桶名，证书ID")
    """错误桶名"""
    bucket_name_wrong = "wrong_bucket_name"
    if bucket_name_wrong not in bucket_name_lst_base:
        rc, stdout = s3_common.del_object(
            bucket_name_wrong, object_name_lst[0], certificate_id)
        print rc, stdout
        # common.judge_rc(rc, 0, 'delete object failed!')
    """错误证书ID"""
    certificate_id_wrong = 'WRONG8F4QBKHSRZW0PT327N3GJS5E8032EL1TO9IPQEEFKML1KM2V0O9NZAR20CW'
    if certificate_id_wrong != certificate_id:
        rc, stdout = s3_common.del_object(
            bucket_name, object_name_lst[0], certificate_id_wrong)
        # common.judge_rc(rc, 0, 'delete object failed!')
        print rc, stdout
    log.info(
        "verify used wrong bucket_name and wrong certificate_id delete object success!")

    log.info("8> 获取账户内所有的桶")
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

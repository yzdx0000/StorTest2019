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
#    有对象读写权限时，查询对象元数据
# @steps:
#    1、创建账户；
#    2、检查账户是否存在
#    3、创建证书；
#    4、创建桶
#    5、上传带元数据信息的对象
#    6、设置对象ACL权限，拥有对象读写权限
#    7、获取对象ACL
#    8、查询元数据信息
#    9、清理环境
#
# @changelog：
##########################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]                 # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"
ACCOUNT_EMAIL_2 = FILE_NAME + "2@sugon.com"


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
    """创建另一个账户"""
    account_name_2 = FILE_NAME + "_account2"
    rc, account_id_2 = s3_common.add_account(
        account_name_2, ACCOUNT_EMAIL_2, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add_account %s failed!!!" % account_name_2)

    log.info("2> 检查账户是否存在")
    rc, stdout = s3_common.find_account(ACCOUNT_EMAIL)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "find account %s failed!!!" % ACCOUNT_EMAIL)

    rc, stdout = s3_common.find_account(ACCOUNT_EMAIL_2)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "find account %s failed!!!" % ACCOUNT_EMAIL_2)

    log.info("3> 创建证书")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    rc, certificate_id_2, certificate_2 = s3_common.add_certificate(
        account_id_2)
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

    log.info("5> 上传带元数据信息的对象")
    """创建10M文件"""
    test_path = "/tmp/s3test"
    cmd = "rm -rf %s" % test_path
    common.command(cmd)
    os.mkdir(test_path)
    file_path = os.path.join(test_path, 'file')
    rc, stdout = s3_common.create_file_m(file_path, 10)
    common.judge_rc(rc, 0, "create file %s failed!!!" % file_path)
    object_name_lst_base = []
    object_name = FILE_NAME + '_object_1'
    # rc, stdout = s3_common.add_object(bucket_name, object_name, file_path, certificate_id)
    rc, stdout = s3_common.add_object_with_meta_by_sk(
        bucket_name, object_name, file_path, certificate_id, certificate, 6)
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

    log.info("6> 设置ACL权限")
    ACL_TYPE = "FULL_CONTROL"
    rc, stdout = s3_common.set_object_acl(bucket_name, object_name, certificate_id, account_id, ACCOUNT_EMAIL,
                                          account_id_2, ACCOUNT_EMAIL_2, ACL_TYPE)
    common.judge_rc(rc, 0, 'set %s acl failed' % object_name)
    log.info("set object acl success!")

    log.info("7> 获取对象ACL权限")
    rc, account_id_lst, account_email_lst, permission_lst = s3_common.get_object_acl(
        bucket_name, object_name, certificate_id_2)
    common.judge_rc(rc, 0, 'get %s acl failed' % object_name)
    log.info("get object acl success!")

    log.info("8> 查询对象的元数据信息")
    rc, stdout = s3_common.get_object_meta(
        bucket_name, object_name, certificate_id_2)
    common.judge_rc_unequal(rc, -1, 'get object %s meta failed!' % object_name)
    if '200 OK' in stdout:
        log.info("curl command execute success!")
    log.info("get object meta data success!")

    log.info("9> 获取账户内所有的桶下的对象")
    for bucket_name in bucket_name_lst_base:
        rc, object_name_lst = s3_common.get_all_object_in_bucket(
            bucket_name, certificate_id)
        common.judge_rc(
            rc, 0, "get all object in bucket %s failed!!!" %
            bucket_name)

    log.info("10> 获取账户内所有的桶")
    rc, bucket_name_lst = s3_common.get_all_bucket_name(certificate_id)
    common.judge_rc(rc, 0, "get bucket failed!!!")

    log.info('%s success!' % FILE_NAME)
    result.result(FILE_NAME, 0)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL, ACCOUNT_EMAIL_2])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL, ACCOUNT_EMAIL_2])
    log.info('%s finish!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

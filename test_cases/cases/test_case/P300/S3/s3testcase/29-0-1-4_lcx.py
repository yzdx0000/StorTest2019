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
#    删除有object的桶，关闭强删开关/开启强删开关
# @steps:
#    1、创建账户；
#    2、检查账户是否存在
#    3、创建证书；
#    4、上传桶
#    5、上传对象
#    6、查询桶内是否有对象
#    7、删除桶
#    8、清理环境
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
    log.info("4> 上传桶")
    bucket_name = FILE_NAME + '_bucket_1'
    bucket_name = bucket_name.replace('_', '-')
    bucket_name_lst_base.append(bucket_name)
    rc, stdout = s3_common.add_bucket(bucket_name, certificate_id, exe_node_ip=None)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)
    rc, stdout = s3_common.check_bucket(bucket_name, certificate_id,  exe_node_ip=None)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "check bucket %s failed!!!" % bucket_name)

    log.info("5> 上传对象")
    """创建10M文件"""
    test_path = '/tmp/s3test'
    if os.path.exists(test_path):
        cmd = "rm -rf %s" % test_path
        common.run_command_shot_time(cmd)
    os.mkdir(test_path)
    file_path = os.path.join(test_path, 'file_10m')
    rc, stdout = s3_common.create_file_m(file_path, 10)
    common.judge_rc(rc, 0, "create file %s failed!!!" % file_path)
    object_name_lst_base = []
    for i in range(10):
        object_name = FILE_NAME + '_object_%d' % i
        rc, stdout = s3_common.add_object(bucket_name, object_name, file_path, certificate_id)
        common.judge_rc(rc, 0, "add object %s failed!!!" % object_name)
        object_name_lst_base.append(object_name)
    """验证对象是否上传成功"""
    rc, object_name_lst = s3_common.get_all_object_in_bucket(bucket_name, certificate_id)
    common.judge_rc(rc, 0, "get all object in bucket %s failed!!!" % bucket_name)
    for object_name in object_name_lst_base:
        if object_name not in object_name_lst:
            common.except_exit("object %s is not put!!!" % object_name)
    else:
        log.info("all object put success")

    log.info("6> 删除桶（关闭强删开关）")
    """关闭强删桶的开关"""
    rc, stdout = s3_common.set_force_delete_bucket(0)
    common.judge_rc(rc, 0, "set_force_delete_bucket=0 fail!!!")
    time.sleep(10)
    """删除桶-失败"""
    rc, stdout = s3_common.del_bucket(bucket_name, certificate_id)
    common.judge_rc(rc, -1, "delete bucket %s failed, bucket has object." % bucket_name)

    log.info("7> 删除桶（打开强删开关）")
    """打开强删桶的开关"""
    rc, stdout = s3_common.set_force_delete_bucket(1)
    common.judge_rc(rc, 0, "set_force_delete_bucket=0 fail!!!")
    time.sleep(10)
    """删除桶——成功"""
    rc, stdout = s3_common.del_bucket(bucket_name, certificate_id)
    common.judge_rc(rc, 0, "delete bucket %s failed, bucket has object." % bucket_name)

    log.info("8> 获取账户内所有的桶")
    rc, bucket_name_lst = s3_common.get_all_bucket_name(certificate_id)
    common.judge_rc(rc, 0, "get bucket failed!!!")
    if len(bucket_name_lst) == 0:
        log.info("account has zero bucket!")

    log.info('%s success!' % FILE_NAME)
    result.result(FILE_NAME, 0)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s finish!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

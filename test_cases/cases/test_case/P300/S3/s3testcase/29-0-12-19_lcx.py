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
# date 2018-12-10
# @summary：
#    验证单桶/单对象最多支持8个自定义元数据
# @steps:
#    1、创建账户；
#    2、检查账户是否存在
#    3、创建证书；
#    4、添加带8个自定义原始的桶
#    5、添加带9个自定义原始的桶
#    6、创建上传对象的文件
#    7、添加带8个自定义原始的对象
#    8、添加带8个自定义原始的对象
#    9、清理环境
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
    log.info("4> 添加带8个自定义原始的桶")
    bucket_name = FILE_NAME + '_bucket_1'
    bucket_name = bucket_name.replace('_', '-')
    bucket_name_lst_base.append(bucket_name)
    rc, stdout = s3_common.add_bucket_with_meta_by_sk(bucket_name, certificate_id, certificate, meta_num=8)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add bucket %s with eight metas failed!!!" % bucket_name)
    rc, stdout = s3_common.check_bucket(bucket_name, certificate_id, exe_node_ip=None)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "check bucket %s failed!!!" % bucket_name)
    log.info("add bucket with eight meta success!")

    log.info("5> 添加带9个自定义原始的桶")
    bucket_name_2 = FILE_NAME + '_bucket_2'
    bucket_name_lst_base.append(bucket_name_2)
    rc, stdout = s3_common.add_bucket_with_meta_by_sk(bucket_name_2, certificate_id, certificate, meta_num=9)
    common.judge_rc_unequal(rc, 0, "add bucket %s with nine metas failed !" % bucket_name_2)
    log.info("add bucket with nine meta failed!")

    log.info("6> 创建上传对象的文件")
    """创建一个5G文件"""
    test_path = '/mnt/licx_s3'
    cmd = "rm -rf %s" % test_path
    common.command(cmd)
    os.mkdir(test_path)
    file_size = 5
    file_path = os.path.join(test_path, 'file_5M')
    rc, stdout = s3_common.create_file_m(file_path, file_size)
    common.judge_rc(rc, 0, "create file %s failed!!!" % file_path)
    log.info("create file success!")

    log.info("7> 添加带8个自定义元数据的对象")
    object_name = FILE_NAME + '_object_1'
    rc, stdout = s3_common.add_object_with_meta_by_sk(bucket_name, object_name, file_path, certificate_id,
                                                      certificate, meta_num=8)
    common.judge_rc(rc, 0, "add object %s failed!" % object_name)
    log.info("add object with eight meta success!")

    log.info("8> 添加带9个自定义元数据的对象")
    object_name_2 = FILE_NAME + '_object_2'
    rc, stdout = s3_common.add_object_with_meta_by_sk(bucket_name, object_name_2, file_path, certificate_id,
                                                      certificate, meta_num=9)
    common.judge_rc_unequal(rc, 0, "add object %s failed!" % object_name)
    log.info("add object with nine meta failed!")

    log.info("9> 获取账户内所有的桶")
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
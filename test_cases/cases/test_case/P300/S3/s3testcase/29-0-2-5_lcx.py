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
# date 2018-11-19
# @summary：
#    上传同名对象
# @steps:
#    1、创建账户；
#    2、检查账户是否存在
#    3、创建证书；
#    4、创建桶（两个）
#    5、向同一桶上传同名，不同内容的object
#    6、验证上传对象的一致性
#    7、向同一桶上传同名，同内容的object
#    8、向不同桶上传同名，同内容的object
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
    log.info("4> 创建桶")
    for i in range(2):
        bucket_name = FILE_NAME + '_bucket_%d' % i
        bucket_name = bucket_name.replace('_', '-')
        bucket_name_lst_base.append(bucket_name)
        rc, stdout = s3_common.add_bucket(bucket_name, certificate_id, exe_node_ip=None)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)
        rc, stdout = s3_common.check_bucket(bucket_name, certificate_id, exe_node_ip=None)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "check bucket %s failed!!!" % bucket_name)

    log.info("5> 创建文件并上传，再创建一个同名文件并上传")
    """创建一个5M文件"""
    test_path = '/tmp/s3test'
    if os.path.exists(test_path):
        cmd = "rm -rf %s" % test_path
        common.run_command_shot_time(cmd)
    os.mkdir(test_path)
    file_path1 = os.path.join(test_path, 'file1_10m')
    rc, stdout = s3_common.create_file_m(file_path1, 10)
    common.judge_rc(rc, 0, "create file %s failed!!!" % file_path1)
    object_name = FILE_NAME + '_object_1'
    rc, stdout = s3_common.add_object(bucket_name_lst_base[0], object_name, file_path1, certificate_id)
    common.judge_rc(rc, 0, "add object %s failed!!!" % object_name)
    log.info("%s put success!" % object_name)
    """再创建一个同名的10M文件"""
    file_path2 = os.path.join(test_path, 'file2_20m')
    rc, stdout = s3_common.create_file_m(file_path2, 20)
    common.judge_rc(rc, 0, "create file %s failed!!!" % file_path2)
    rc, stdout = s3_common.add_object(bucket_name_lst_base[0], object_name, file_path2, certificate_id)
    common.judge_rc(rc, 0, "add object %s failed!!!" % object_name)
    log.info("%s put success!" % object_name)

    log.info("6> 验证上传同名对象是否覆盖")
    file_down_path = os.path.join("/tmp", object_name + 'down')
    rc, stdout = s3_common.download_object(bucket_name_lst_base[0], object_name, file_down_path, certificate_id)
    common.judge_rc(rc, 0, "download object %s failed!!!" % object_name)
    """获取第一次上传文件MD5值"""
    rc, base_file1_md5 = s3_common.get_file_md5(file_path1)
    common.judge_rc(rc, 0, "get file %s failed!!!" % file_path1)
    """获取第二次上传文件MD5值"""
    rc, base_file2_md5 = s3_common.get_file_md5(file_path2)
    common.judge_rc(rc, 0, "get file %s failed!!!" % file_path2)
    """获取上传文件的MD5值"""
    rc, file_md5 = s3_common.get_file_md5(file_down_path)
    common.judge_rc(rc, 0, "get file %s failed!!!" % file_down_path)
    """比较两个MD5值"""
    # if base_file1_md5 != file_md5 & base_file2_md5 == file_md5:
    #     log.info("file overide old object!!!")
    # else:
    #     log.error("file md5 is not same")
    # common.judge_rc(base_file1_md5, file_md5, "file md5 is not same")
    common.judge_rc(base_file2_md5, file_md5, "file md5 is not same")

    log.info("7> 创建同一文件并上传两次")
    """创建一个15M文件"""
    file_path3 = '/tmp/s3testfile3'
    rc, stdout = s3_common.create_file_m(file_path3, 15)
    common.judge_rc(rc, 0, "create file %s failed!!!" % file_path3)
    object_name = FILE_NAME + '_object_2'
    """同名文件第一次上传"""
    rc, stdout = s3_common.add_object(bucket_name_lst_base[0], object_name, file_path3, certificate_id)
    common.judge_rc(rc, 0, "add object %s failed!!!" % object_name)
    log.info("%s put success!" % object_name)
    """同名文件第二次上传"""
    rc, stdout = s3_common.add_object(bucket_name_lst_base[0], object_name, file_path3, certificate_id)
    common.judge_rc(rc, 0, "add object %s failed!!!" % object_name)
    log.info("%s put success!" % object_name)

    log.info("8> 创建同一文件并上传两次到不同的桶")
    """创建一个20M文件"""
    file_path4 = '/tmp/s3testfile3'
    rc, stdout = s3_common.create_file_m(file_path4, 20)
    common.judge_rc(rc, 0, "create file %s failed!!!" % file_path4)
    object_name = FILE_NAME + '_object_3'
    """同名文件第一次上传至桶1"""
    rc, stdout = s3_common.add_object(bucket_name_lst_base[0], object_name, file_path4, certificate_id)
    common.judge_rc(rc, 0, "add object %s failed!!!" % object_name)
    log.info("%s put success!" % object_name)
    """同名文件第二次上传至桶2"""
    rc, stdout = s3_common.add_object(bucket_name_lst_base[1], object_name, file_path4, certificate_id)
    common.judge_rc(rc, 0, "add object %s failed!!!" % object_name)
    log.info("%s put success!" % object_name)

    log.info("9> 获取账户内所有的桶下的对象")
    for bucket_name in bucket_name_lst_base:
        rc, object_name_lst = s3_common.get_all_object_in_bucket(bucket_name, certificate_id)
        common.judge_rc(rc, 0, "get all object in bucket %s failed!!!" % bucket_name)

    log.info("10> 获取账户内所有的桶")
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

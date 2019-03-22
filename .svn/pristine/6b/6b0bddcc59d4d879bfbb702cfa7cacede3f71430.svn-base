#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import os

import utils_path
import common
import s3_common
import log
import prepare_clean
import result
import tool_use

##########################################################################
#
# Author: zhanghan
# date 2018-12-27
# @summary：
#    频繁上传不同对象大小的文件至同一个对象,并进行MD5值校验。测试用例：29-0-20-42
# @steps:
#    1、创建账户
#    2、创建证书
#    3、创建桶
#    4、上传对象
#    5、使用vdbench创建不同大小的文件
#    6、覆盖上传对象，设置对象的acl，并进行验证
#       6-1> 创建目标账户/证书
#       6-2> 设置对象的acl:READ
#       6-3> 连续上传不同vdbench文件到同一个对象后下载校验MD5，并验证acl:READ
#    7、记录用例执行成功
#
# @changelog：
##########################################################################

# 全局变量
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"
VDB_THREADS = 5
ANCHOR_PATH = '/tmp'
src_path = os.path.join(ANCHOR_PATH, 'src_vdb')
dst_path = os.path.join(ANCHOR_PATH, 'dst_vdb')
object_name = "object_" + FILE_NAME
tar_account_name = FILE_NAME + "_account_target"
tar_account_email = tar_account_name + "@sugon.com"
acl = 'READ'


def get_dir_files(path):
    if os.path.exists(path):
        for src_dirpath, src_dirnames, src_filenames in os.walk(path):
            break
    else:
        common.except_exit("The path:%s doesn't exist." % path)
    return (src_dirpath, src_dirnames, src_filenames)


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, "-1")


def case():

    is_exists = os.path.exists(dst_path)
    if not is_exists:
        os.makedirs(dst_path)

    log.info("1> 创建账户")
    account_name = FILE_NAME + "_account1"
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create account failed!!!")

    log.info("2> 创建证书")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    log.info("3> 创建桶")
    bucket_name = FILE_NAME + '_bucket1'
    bucket_name = bucket_name.replace('_', '-')
    rc, stdout = s3_common.add_bucket(bucket_name, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add bucket failed!!!")

    log.info("4> 上传对象")
    file_path = os.path.join(ANCHOR_PATH, 'file_' + FILE_NAME)
    size = 3  # 以M为单位
    rc, stdout = s3_common.create_file_m(file_path, size)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create file failed!!!")

    rc, stdout = s3_common.add_object(
        bucket_name, object_name, file_path, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "put object failed!!!")

    log.info("5> 使用vdbench创建不同大小的文件")
    obj_vdb = tool_use.Vdbenchrun(
        depth=1,
        width=VDB_THREADS,
        files=10,
        size='(4k,10,64k,20,120k,10,1M,10,2M,10,500k,20,10M,10,8M,10)',
        xfersize='4K',
        threads=VDB_THREADS)
    rc = obj_vdb.run_create(anchor_path=src_path, journal_path=ANCHOR_PATH)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "vdbench create file failed!!!")

    log.info("6> 覆盖上传对象，设置对象的acl，并进行验证")
    log.info("6-1> 创建目标账户/证书")
    rc, tar_account_id = s3_common.add_account(
        tar_account_name, tar_account_email, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create account failed!!!")
    rc, tar_certificate_id, tar_certificate = s3_common.add_certificate(
        tar_account_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    log.info("6-2> 设置对象的acl:READ")
    rc, stdout = s3_common.set_object_acl(
        bucket_name, object_name, certificate_id, account_id, ACCOUNT_EMAIL, tar_account_id, tar_account_email, acl)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "set object acl failed!!!")

    rc, account_id_lst, account_email_lst, permission_lst = s3_common.get_object_acl(
        bucket_name, object_name, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "get object acl failed, please check")

    log.info("6-3> 连续上传不同vdbench文件到同一个对象后下载校验MD5，并验证acl:READ")
    src_dirpath, src_dirnames, src_filenames = get_dir_files(src_path)
    for src_dirname in src_dirnames:
        file_name_list = []
        src_dir = os.path.join(src_dirpath, src_dirname)
        print("src_dir is %s" % src_dir)
        src_dirpath, src_dirnames, src_filenames = get_dir_files(src_dir)
        for item in src_filenames:
            file_name_tmp = os.path.join(src_dir, item)
            file_name_list.append(file_name_tmp)
            (rc, md5_tmp) = s3_common.get_file_md5(file_name_tmp)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "get file MD5 failed!!!")
            # 上传文件到同一个对象并获取文件MD5值
            (rc, stdout) = s3_common.add_object(
                bucket_name, object_name, file_name_tmp, certificate_id)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "add object failed!!!")
            # 下载对象并获取MD5值
            dst_file_name = "dst_" + src_dirname + "_" + item
            dst_file_name_tmp = os.path.join(dst_path, dst_file_name)
            (rc, stdout) = s3_common.download_object(
                bucket_name, object_name, dst_file_name_tmp, certificate_id)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "download object failed!!!")
            (rc, dst_md5_tmp) = s3_common.get_file_md5(dst_file_name_tmp)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "get file MD5 failed!!!")
            # MD5值校验
            if md5_tmp == dst_md5_tmp:
                log.info(
                    "file is %s , the MD5 is %s, check MD5 success!" %
                    (file_name_tmp, md5_tmp))
            else:
                log.info(
                    "Error! Check MD5 failed, file is %s, put file MD5 is %s, download file MD5 is %s " %
                    (file_name_tmp, md5_tmp, dst_md5_tmp))
                judge_result(1, FILE_NAME)
                common.judge_rc(1, 0, "Check MD5 failed, please check")

            # 设置对象的acl
            rc, stdout = s3_common.set_object_acl(
                bucket_name, object_name, certificate_id, account_id, ACCOUNT_EMAIL, tar_account_id, tar_account_email,
                acl)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "set object acl failed!!!")

            # 获取对象acl
            rc, account_id_lst, account_email_lst, permission_lst = s3_common.get_object_acl(
                bucket_name, object_name, certificate_id)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "get object acl failed, please check")

            # 检验对象acl:READ是否设置成功
            rc, stdout = s3_common.get_object_meta(
                bucket_name, object_name, tar_certificate_id)
            if rc == 18 or rc == 0:
                log.info("the object %s acl:READ take effect" % file_name_tmp)
                pass
            else:
                log.info("Error! the object %s acl:READ dosen't take effect" % file_name_tmp)
                common.judge_rc(rc, 0, "get object meta failed!!!")

        (src_dirpath, src_dirname) = os.path.split(src_dirpath)

    cmd2 = "rm -rf %s" % dst_path
    common.command(cmd2)

    log.info("7> 用例%s执行成功" % FILE_NAME)


def main():
    email_list = [ACCOUNT_EMAIL, tar_account_email]
    prepare_clean.s3_test_prepare(FILE_NAME, email_list, False)
    case()
    prepare_clean.s3_test_clean(email_list)
    log.info('%s finished!' % FILE_NAME)
    result.result(FILE_NAME, "0")


if __name__ == '__main__':
    common.case_main(main)

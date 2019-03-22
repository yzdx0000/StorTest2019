# -*-coding:utf-8 -*
import os

import utils_path
import common
import s3_common
import log
import prepare_clean

####################################################################################
#
# Author: baorb
# date 2018-01-19
# @summary：
#    多段上传对象
# @steps:
#    1、创建账户；
#    2、创建证书；
#    3、创建桶；
#    4、创建多个文件；
#    5、初始化多段上传；
#    6、上传文件；
#    7、合并段；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"


def case():
    log.info("1> 创建账户")
    account_name = FILE_NAME + "_account1"
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    common.judge_rc(rc, 0, "create account failed!!!")

    log.info("2> 创建证书")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    log.info("3> 创建桶")
    bucket_name = FILE_NAME + '_bucket'
    rc, stdout = s3_common.add_bucket(bucket_name, certificate_id)
    common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)

    log.info("4> 创建文件")
    file_num = 25
    test_path = '/tmp/s3_segment'
    cmd = "rm -rf %s" % test_path
    common.command(cmd)
    os.mkdir(test_path)
    """生成250M的文件"""
    file_path = os.path.join(test_path, 's3_test')
    rc, stdout = s3_common.create_file_m(file_path, 250)
    common.judge_rc(rc, 0, "create file %s failed!!!")

    """分割文件"""
    os.chdir(test_path)
    cmd = "split -b 10m %s" % file_path
    common.command(cmd)
    os.chdir(os.getcwd())

    child_file = os.path.join(test_path, 'x*')
    cmd = "ls %s" % child_file
    rc, stdout = common.run_command_shot_time(cmd)
    file_lst = stdout.split()

    log.info("5> 初始化多段上传")
    object_name = FILE_NAME + '_object'
    rc, upload_id = s3_common.init_put_object_by_segment(bucket_name, object_name, certificate_id)
    common.judge_rc(rc, 0, "init segment failed!!!")

    log.info("6> 多段上传")
    i = 1
    for file_name in file_lst:
        rc, stdout = s3_common.put_object_segment(bucket_name, object_name, i, upload_id, certificate_id, file_name)
        common.judge_rc(rc, 0, "put object segment failed!!!")
        i += 1

    log.info("7> 合并段")
    rc, stdout = s3_common.merge_object_seg(bucket_name, object_name, upload_id, certificate_id, file_num)
    common.judge_rc(rc, 0, "metge object failed!!!")

    log.info("8> 下载对象")
    file_down_path = os.path.join(test_path, 's3_test_down')
    rc, stdout = s3_common.download_object(bucket_name, object_name, file_down_path, certificate_id)
    common.judge_rc(rc, 0, "download object %s failed!!!" % object_name)

    log.info("9> 检查文件MD5值")
    file_check_path = os.path.join(test_path, 's3_test_check')
    cmd = "cat %s > %s" % (child_file, file_check_path)
    common.command(cmd)
    rc, src_file_md5 = s3_common.get_file_md5(file_path)
    rc, down_file_md5 = s3_common.get_file_md5(file_down_path)
    rc, check_file_md5 = s3_common.get_file_md5(file_check_path)
    common.judge_rc(src_file_md5, check_file_md5, "check file md5 failed!!!")
    common.judge_rc(src_file_md5, down_file_md5, "down file md5 failed!!!")

    log.info("10> 删除文件")
    cmd = "rm -rf %s" % test_path
    common.command(cmd)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
#!/usr/bin/python
# -*-coding:utf-8 -*
import os
import utils_path
import common
import s3_common
import log
import prepare_clean
import result
####################################################################################
#
# Author: lichengxu
# date 2018-11-20
# @summary：
#    分段上传5T对象
# @steps:
#    1、创建账户；
#    2、检查账户是否存在
#    3、创建证书；
#    4、创建桶
#    5、创建文件
#    6、初始化多段上传
#    7、多段上传对象
#    8、合并段
#    9、下载对象
#    10、比较MD5值
#    11、清理环境
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
    # common.judge_rc(-1, 0, "WARING: you are putting 5T object, please check again and delete this row")
    log.info("WARING: you are putting 5T object, please check again and delete this row")
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

    log.info("5> 创建5T文件")
    """创建一个5G文件"""
    test_path = '/mnt/volume_lichx/s3test'
    file_size = 5 * 1024
    log.info("判断共享目录是否存在")
    if os.path.exists(test_path):
        # common.judge_rc(-1, 0, "请添加集群共享路径/mnt/volume_lichx/s3test，不要添加本地路径")
        cmd = "rm -rf %s" % test_path
        common.command(cmd)
    os.mkdir(test_path)
    file_path1 = os.path.join(test_path, 'file_5G')
    rc, stdout = s3_common.create_file_m(file_path1, file_size)
    common.judge_rc(rc, 0, "create file %s failed!!!" % file_path1)

    file_path2 = os.path.join(test_path, "file_5T")
    rc, stdout = s3_common.create_file_m(file_path2, 10)
    common.judge_rc(rc, 0, "create file %s failed!!!" % file_path2)

    """追加文件到5T大小"""
    for i in range(1024):
        cmd = "cat %s >> %s" % (file_path1, file_path2)
        common.command(cmd)

    """分割文件为1G大小"""
    os.chdir(test_path)
    cmd = "split -b 1G %s -d -a 3" % file_path2
    common.command(cmd)

    os.chdir(os.getcwd())
    child_file = os.path.join(test_path, 'x*')
    cmd = "ls %s" % child_file
    rc, stdout = common.run_command_shot_time(cmd)
    file_lst = stdout.split()

    log.info("5> 初始化多段上传")
    object_name = FILE_NAME + '_object_1'
    rc, upload_id = s3_common.init_put_object_by_segment(bucket_name, object_name, certificate_id)
    common.judge_rc(rc, 0, "init segment failed!!!")
    log.info("init segment %s put success!" % object_name)

    log.info("6> 多段上传")
    for i, file_name in zip(range(len(file_lst)), file_lst):
        rc, stdout = s3_common.put_object_segment(bucket_name, object_name, i+1, upload_id, certificate_id, file_name)
        common.judge_rc(rc, 0, "put object segment failed!!!")
    log.info("segment put %s put success!" % object_name)

    log.info("7> 合并段")
    rc, stdout = s3_common.merge_object_seg(bucket_name, object_name, upload_id, certificate_id, len(file_lst))
    common.judge_rc(rc, 0, "metge object failed!!!")
    log.info("merge %s success!" % object_name)

    log.info("8> 下载对象，并验证MD5值")
    file_down_path = os.path.join(test_path, object_name + 'down')
    rc, stdout = s3_common.download_object(bucket_name_lst_base[0], object_name, file_down_path, certificate_id)
    common.judge_rc(rc, 0, "download object %s failed!!!" % object_name)
    log.info("download %s success!" % object_name)

    """获取第一次上传文件MD5值"""
    rc, base_file_md5 = s3_common.get_file_md5(file_path2)
    common.judge_rc(rc, 0, "get file %s failed!!!" % file_path2)
    """获取上传文件的MD5值"""
    rc, file_md5 = s3_common.get_file_md5(file_down_path)
    common.judge_rc(rc, 0, "get file %s failed!!!" % file_down_path)
    """比较两个MD5值"""
    common.judge_rc(base_file_md5, file_md5, "file md5 is not same")
    log.info("file md5 is same!!!")

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
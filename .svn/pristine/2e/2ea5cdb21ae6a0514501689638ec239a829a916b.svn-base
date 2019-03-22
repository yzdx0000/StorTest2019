#! /usr/bin/python
# -*- coding:utf-8 -*-
# 标题：功能测试，用例编号29-0-17-41
# 使用方法：python 29-0-17-43_44_45_46_47_48_wjl_lyz.py
# 在http模式下，小文件多段上传测试。日志打印在屏幕上。
# 作者：liuyzhb
# 创建时间：2018/03/28
import sys
import os
import commands
import json
import time
import ConfigParser
import random

current_pyth = os.getcwd()
pwd = os.path.dirname(current_pyth)
sys.path.append(pwd + "/S3Lib")
import utils_path
import common
import s3_common
import log
import get_config
import prepare_clean
import result

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, "-1")


# 文件split后，保存生成的各个文件存在状态，True代表存在，False代表不存在
split_seg = {}

# 主函数


def case():
    log.info("1> 开启签名认证")
    rc, opt = s3_common.set_oss_http_auth("1")
    time.sleep(12)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "Open sig-mode failed!")

    log.info("2> 创建账户")
    account_name = FILE_NAME + "_account1"
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create account failed!!!")

    log.info("3> 创建证书")
    rc, certificate_id, sk = s3_common.add_certificate(account_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    log.info("4> 上传桶")
    bucket_name = FILE_NAME + '_bucket'
    bucket_name = bucket_name.replace('_', '-')
    rc, opt = s3_common.add_bucket_by_sk(bucket_name, certificate_id, sk)
    judge_result(rc, FILE_NAME)
    log.info(opt)
    common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)
    rc, opt = s3_common.check_bucket_by_sk(bucket_name, certificate_id, sk)
    judge_result(rc, FILE_NAME)
    log.info(opt)
    common.judge_rc(rc, 0, "check bucket %s failed!!!" % bucket_name)

    log.info("5> 创建文件")
    file_num = 5
    test_path = '/tmp/s3_segment'
    cmd = "rm -rf %s" % test_path
    common.command(cmd)
    os.mkdir(test_path)
    """生成50M的文件"""
    file_path = os.path.join(test_path, 's3_test')
    rc, stdout = s3_common.create_file_m(file_path, 50)
    judge_result(rc, FILE_NAME)
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

    child_file = os.path.join(test_path, 'x*')
    cmd = "ls %s" % child_file
    rc, stdout = common.run_command_shot_time(cmd)
    file_lst = stdout.split()

    child_file = os.path.join(test_path, 'x*')
    cmd = "ls %s" % child_file
    rc, stdout = common.run_command_shot_time(cmd)
    file_lst = stdout.split()

    # 计算原文件的MD5值
    rc, src_file_md5 = s3_common.get_file_md5(file_path)

    log.info("6> 初始化多段上传,在开关切换之后立即执行，就相当于初始化和开关切换同时执行了，因为开关切换有延迟")
    object_name = FILE_NAME + '_object'
    rc1s = []
    rc0s = []
    rchttp0s = []
    rchttp1s = []
    for i in range(2):
        rc1, upload_id = s3_common.init_put_object_by_segment_by_sig(
            bucket_name, object_name, certificate_id, sk)
        rchttp0, opt = s3_common.set_oss_http_auth("0")
        rc0, upload_id = s3_common.init_put_object_by_segment_by_sig(
            bucket_name, object_name, certificate_id, sk)
        rchttp1, opt = s3_common.set_oss_http_auth("1")
        rc1s.append(rc1)
        rc0s.append(rc0)
        rchttp0s.append(rchttp0)
        rchttp1s.append(rchttp1)
    for i in range(2):
        judge_result(rc1s[i], FILE_NAME)
        judge_result(rc0s[i], FILE_NAME)
        judge_result(rchttp0s[i], FILE_NAME)
        judge_result(rchttp1s[i], FILE_NAME)
        common.judge_rc(
            rc1s[i],
            0,
            "init segment and open http at the sametime failed")
        common.judge_rc(
            rc0s[i],
            0,
            "init segment and close http at the sametimefailed!!!")
        common.judge_rc(
            rchttp0s[i],
            0,
            "close http and failed!!!init segment at the same time")
        common.judge_rc(
            rchttp1s[i],
            0,
            "open http failed!!!init segment at the same time")

    log.info("7> 多段上传")
    i = 1
    for file_name in file_lst:
        log.info('上传第%d段' % i)
        rc1s = []
        rc0s = []
        rchttp0s = []
        rchttp1s = []
        for j in range(2):
            rc1, stdout = s3_common.put_object_segment_by_sig(
                bucket_name, object_name, i, upload_id, certificate_id, sk, file_name)
            rchttp0, opt = s3_common.set_oss_http_auth("0")
            rc0, stdout = s3_common.put_object_segment_by_sig(
                bucket_name, object_name, i, upload_id, certificate_id, sk, file_name)
            rchttp1, opt = s3_common.set_oss_http_auth("1")
            rc1s.append(rc1)
            rc0s.append(rc0)
            rchttp0s.append(rchttp0)
            rchttp1s.append(rchttp1)
        for j in range(2):
            judge_result(rc1s[j], FILE_NAME)
            judge_result(rc0s[j], FILE_NAME)
            judge_result(rchttp0s[j], FILE_NAME)
            judge_result(rchttp1s[j], FILE_NAME)
            common.judge_rc(
                rc1s[j],
                0,
                "put object segment and open http at the sametime failed")
            common.judge_rc(
                rc0s[j],
                0,
                "put object segment and close http at the sametimefailed!!!")
            common.judge_rc(
                rchttp0s[j],
                0,
                "close http and failed!!!put object segment at the same time")
            common.judge_rc(
                rchttp1s[j],
                0,
                "open http failed!!!put object segment at the same time")
        i += 1

    log.info("8> 合并段")
    rc1s = []
    rc0s = []
    rchttp0s = []
    rchttp1s = []
    # for i in range(2):
    rchttp0, opt = s3_common.set_oss_http_auth("0")
    rc1, stdout = s3_common.merge_object_seg_by_sig(
        bucket_name, object_name, upload_id, certificate_id, sk, file_num)
    #rchttp0, opt = s3_common.set_oss_http_auth("0")
    #rc0, stdout = s3_common.merge_object_seg_by_sig(bucket_name, object_name, upload_id, certificate_id, sk, file_num)
    #rchttp1, opt = s3_common.set_oss_http_auth("1")
    # rc1s.append(rc1)
    # rc0s.append(rc0)
    # rchttp0s.append(rchttp0)
    # rchttp1s.append(rchttp1)
    judge_result(rc1, FILE_NAME)
    #judge_result(rc0, FILE_NAME)
    judge_result(rchttp0, FILE_NAME)
    #judge_result(rchttp1, FILE_NAME)
    common.judge_rc(
        rc1,
        0,
        "merge_object and open http at the sametime failed")
    #common.judge_rc(rc0, 0, "merge_object and close http at the sametimefailed!!!")
    common.judge_rc(
        rchttp0,
        0,
        "close http and failed!!!merge_object at the same time")
    #common.judge_rc(rchttp1, 0, "open http failed!!!merge_object at the same time")

    log.info("9> 下载对象")
    # 先计算sig
    stringtosign = "GET" + "\n" + "" + "\n" + "" + "\n" + \
        "" + "\n" + "" + "/" + bucket_name + "/" + object_name
    log.info('param of downobject is %s' % stringtosign)
    siga = s3_common.mk_sig(sk, stringtosign)
    siga = s3_common.mk_sig_code(siga)
    log.info('sig of downobject is %s' % siga)
    # 然后下载
    file_down_path = os.path.join(test_path, 's3_test_down')
    rc, stdout = s3_common.download_object_by_sig(bucket_name, object_name, file_down_path, certificate_id, sig=siga,
                                                  exe_node_ip=None, print_flag=True, retry=False)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "download object %s failed!!!" % object_name)

    log.info("10> 检查文件MD5值")
    file_check_path = os.path.join(test_path, 's3_test_check')
    cmd = "cat %s > %s" % (child_file, file_check_path)
    common.command(cmd)
    rc, src_file_md5 = s3_common.get_file_md5(file_path)
    rc, down_file_md5 = s3_common.get_file_md5(file_down_path)
    rc, check_file_md5 = s3_common.get_file_md5(file_check_path)
    common.judge_rc(src_file_md5, check_file_md5, "check file md5 failed!!!")
    common.judge_rc(src_file_md5, down_file_md5, "down file md5 failed!!!")


def main():
    rc, opt = s3_common.set_oss_http_auth("0")
    time.sleep(12)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "Close sig-mode failed!")
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    rc, opt = s3_common.set_oss_http_auth("0")
    time.sleep(12)
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s succeed!' % FILE_NAME)
    result.result(FILE_NAME, "0")


if __name__ == '__main__':
    common.case_main(main)

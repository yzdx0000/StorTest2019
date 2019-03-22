#! /usr/bin/python
# -*- coding:utf-8 -*-
# 标题：功能测试，用例编号29-0-17-41
# 使用方法：python 29-0-17-41_wjl_lyz.py
# 在http模式下，小文件多段上传测试。日志打印在屏幕上。
# 作者：liuyzhb
# 创建时间：2018/10/09
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


'''文件split后，保存生成的各个文件存在状态，True代表存在，False代表不存在'''
split_seg = {}


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

    child_file = os.path.join(test_path, 'x*')
    cmd = "ls %s" % child_file
    rc, stdout = common.run_command_shot_time(cmd)
    file_lst = stdout.split()

    child_file = os.path.join(test_path, 'x*')
    cmd = "ls %s" % child_file
    rc, stdout = common.run_command_shot_time(cmd)
    file_lst = stdout.split()

    """分割文件"""
    os.chdir(test_path)
    cmd = "split -b 10m %s" % file_path
    common.command(cmd)
    os.chdir(os.getcwd())

    child_file = os.path.join(test_path, 'x*')
    cmd = "ls %s" % child_file
    rc, stdout = common.run_command_shot_time(cmd)
    file_lst = stdout.split()

    # 计算原文件的MD5值
    rc, src_file_md5 = s3_common.get_file_md5(file_path)

    log.info("6> 错误的sig初始化多段上传")
    object_name = FILE_NAME + '_object'
    stringtosign = "POST" + "\n" + "" + "\n" + "" + "\n" + "" + \
        "\n" + "" + "/" + bucket_name + "/" + object_name + '?uploads'
    log.info('param of init_put_object_by_segment_by_sig is %s' % stringtosign)
    sig = s3_common.mk_sig(sk, stringtosign)
    sig = s3_common.mk_sig_code(sig)
    log.info('wright sig of init_put_object_by_segment_by_sig is %s' % sig)
    sig1 = 'fault' + sig
    log.info('wrong sig of init_put_object_by_segment_by_sig is %s' % sig1)
    log.info("6.1> 错误的sig:sig前面加fault，初始化多段上传")
    rc, upload_id = s3_common.init_put_object_by_segment_by_sig(
        bucket_name, object_name, certificate_id, sk, sig1)
    if rc == 0:
        log.error('init segment by fault sig is finish ,that\'s wrong')
        result.result(FILE_NAME, "-1")
    else:
        rc = -1
    common.judge_rc(
        rc, -1, "init segment by fault sig is finish ,that\'s wrong!!!")
    log.info("6.2> 错误的sig:将sig的倒数第五位替换字母，初始化多段上传")
    if sig[5] == 'a':
        sig2 = sig[:-5] + 'b' + sig[-4:]
    else:
        sig2 = sig[:-5] + 'a' + sig[-4:]
    log.info('wright sig of init_put_object_by_segment_by_sig is %s' % sig)
    log.info('wrong sig of init_put_object_by_segment_by_sig is %s' % sig2)
    rc, upload_id = s3_common.init_put_object_by_segment_by_sig(
        bucket_name, object_name, certificate_id, sk, sig2)
    if rc == 0:
        log.error('init segment by fault sig is finish ,that\'s wrong')
        result.result(FILE_NAME, "-1")
    else:
        rc = -1
    common.judge_rc(
        rc, -1, "init segment by fault sig is finish ,that\'s wrong!!!")

    log.info("7> 初始化多段上传")
    object_name = FILE_NAME + '_object'
    rc, upload_id = s3_common.init_put_object_by_segment_by_sig(
        bucket_name, object_name, certificate_id, sk)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "init segment failed!!!")

    log.info("8> 错误的sig多段上传")
    log.info("8.1> 错误的sig：sig前面加fault，多段上传")
    i = 1

    for file_name in file_lst:
        stringtosign = "PUT" + "\n" + "" + "\n" + "" + "\n" + "" + "\n" + "" + "/" + \
            bucket_name + "/" + object_name + '?partNumber=' + str(i) + '&uploadId=' + str(upload_id)
        log.info('param of sig is %s' % stringtosign)
        sig = s3_common.mk_sig(sk, stringtosign)
        sig = s3_common.mk_sig_code(sig)
        log.info('wright sig of put_object_segment_by_sig is %s' % sig)
        sig1 = 'fault' + sig
        log.info('wrong sig of init_put_object_by_segment_by_sig is %s' % sig1)
        rc, stdout = s3_common.put_object_segment_by_sig(
            bucket_name, object_name, i, upload_id, certificate_id, sk, file_name, sig1)
        if rc == 0:
            log.error('put segment by fault sig is finish ,that\'s wrong')
            result.result(FILE_NAME, "-1")
        else:
            rc = -1
        i += 1
        common.judge_rc(
            rc, -1, "init segment by fault sig is finish ,that\'s wrong!!!")
    log.info("8.2> 错误的sig：sig的倒数第五位替换字符，多段上传")
    i = 1

    for file_name in file_lst:
        stringtosign = "PUT" + "\n" + "" + "\n" + "" + "\n" + "" + "\n" + "" + "/" + \
            bucket_name + "/" + object_name + '?partNumber=' + str(i) + '&uploadId=' + str(upload_id)
        log.info('param of sig is %s' % stringtosign)
        sig = s3_common.mk_sig(sk, stringtosign)
        sig = s3_common.mk_sig_code(sig)
        log.info('wright sig of put_object_segment_by_sig is %s' % sig)
        if sig[-5] == 'a':
            sig2 = sig[:-5] + 'b' + sig[-4:]
        else:
            sig2 = sig[:-5] + 'a' + sig[-4:]
        log.info('right sig of init_put_object_by_segment_by_sig is %s' % sig)
        log.info('wrong sig of init_put_object_by_segment_by_sig is %s' % sig2)
        rc, stdout = s3_common.put_object_segment_by_sig(
            bucket_name, object_name, i, upload_id, certificate_id, sk, file_name, sig2)
        if rc == 0:
            log.error('put segment by fault sig is finish ,that\'s wrong')
            result.result(FILE_NAME, "-1")
        else:
            rc = -1
        i += 1
        common.judge_rc(
            rc, -1, "init segment by fault sig is finish ,that\'s wrong!!!")
    log.info("9> 多段上传")
    i = 1
    for file_name in file_lst:
        rc, stdout = s3_common.put_object_segment_by_sig(
            bucket_name, object_name, i, upload_id, certificate_id, sk, file_name)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "put object segment failed!!!")
        i += 1
    log.info("10> 错误sig合并段")
    log.info("10.1> 错误sig:sig前加fault，合并段")
    stringtosign = "POST" + "\n" + "" + "\n" + "" + "\n" + "" + "\n" + "" + \
        "/" + bucket_name + "/" + object_name + '?uploadId=' + upload_id
    log.info('param of sig is %s' % stringtosign)
    sig = s3_common.mk_sig(sk, stringtosign)
    sig = s3_common.mk_sig_code(sig)
    log.info('right sig of merge_object_seg_by_faultsig is %s' % sig)
    sig1 = 'fault' + sig
    log.info('wrong sig of merge_object_seg_by_faultsig is %s' % sig1)
    rc, stdout = s3_common.merge_object_seg_by_sig(
        bucket_name, object_name, upload_id, certificate_id, sk, file_num, sig1)
    if rc == 0:
        log.error('merge_objec by fault sig is finish ,that\'s wrong')
        result.result(FILE_NAME, "-1")
    else:
        rc = -1
    common.judge_rc(
        rc, -1, "'merge_object by fault sig is finish ,that\'s wrong!!!")
    log.info("10.2> 错误sig:sig的倒数第五位换字符，合并段")
    log.info('right sig of merge_object_seg_by_faultsig is %s' % sig)
    if sig[-5] == 'a':
        sig2 = sig[:-5] + 'b' + sig[-4:]
    else:
        sig2 = sig[:-5] + 'a' + sig[-4:]
    log.info('wrong sig of merge_object_seg_by_faultsig is %s' % sig2)
    rc, stdout = s3_common.merge_object_seg_by_sig(
        bucket_name, object_name, upload_id, certificate_id, sk, file_num, sig2)
    if rc == 0:
        log.error('merge_objec by fault sig is finish ,that\'s wrong')
        result.result(FILE_NAME, "-1")
    else:
        rc = -1
    common.judge_rc(
        rc, -1, "'merge_objec by fault sig is finish ,that\'s wrong!!!")

    log.info("11> 正确的合并段")
    rc, stdout = s3_common.merge_object_seg_by_sig(
        bucket_name, object_name, upload_id, certificate_id, sk, file_num)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "metge object failed!!!")


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

#! /usr/bin/python
# -*- coding:utf-8 -*-
#**********************************************#
# 标题：功能测试，用例编号29-0-17-50
# 使用方法：python 29-0-17-50_wjl.py
# 在http模式下，设置对象的acl，并用错误sig查询。
# 作者：王建磊
# 创建时间：2018/10/09
#**********************************************#
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
import result
import prepare_clean
import get_config
import log
import s3_common
import common
import utils_path

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
FILE_NAME = FILE_NAME.replace('-', '_')
account_name1 = FILE_NAME + "_" + "account_a"
account_name2 = FILE_NAME + "_" + "account_b"
email1 = account_name1 + "@sugon.com"
email2 = account_name2 + "@sugon.com"

# 创建账户及证书


def create_acc_cer(account_name, email):
    rc, account_id = s3_common.add_account(account_name, email, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create account failed!!!")
    rc, ak, sk = s3_common.add_certificate(account_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")
    return ak, sk, account_id

# 获取sig函数


def create_sig(sk, StringToSign):
    sig = s3_common.mk_sig(sk, StringToSign)
    sig = s3_common.mk_sig_code(sig)
    return sig


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, "-1")

# 结果判断函数


def juge(output):
    result_sig = output[output.find("1.1 ") + 4:][:3]
    print "result:%s" % result_sig
    if result_sig == '403':
        return 0
    else:
        return -1

# 获取桶配额函数


def bucket_get_quota(bucketname, AK, sig):
    rc, opt = s3_common.get_bucket_quota_by_sig(bucketname, AK, sig)
    return rc, opt

# 设置桶配额函数


def bucket_set_quota(bucketname, AK, quota, sig):
    rc, opt = s3_common.update_bucket_quota_by_sig(bucketname, AK, quota, sig)
    return rc, opt

# 创建文件函数


def create_file(obj_path, amount):
    a = [0 for x in range(1024 * 1024)]
    for i in range(len(a) - 10):
        a[i] = 'a'
    for j in range(10):
        data = random.randint(0, 9)
        a[len(a) - 10 + j] = str(data)
    a = "".join(a)
    f = open(obj_path, 'a+')
    for k in range(amount):
        f.write(a)
    f.close()


def case():
    log.info("1> 开启签名认证")
    rc, opt = s3_common.set_oss_http_auth("1")
    time.sleep(12)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "Open sig-mode failed!")

    # 创建账户a、b
    log.info("2> 创建账户a，b")
    ak1, sk1, account_id1 = create_acc_cer(account_name1, email1)
    ak2, sk2, account_id2 = create_acc_cer(account_name2, email2)

    # 账户a\b,中分别创建桶
    log.info("3> 分别在账户a,b中创建桶")
    log.info("bucket create operation:")
    bucket_name1 = FILE_NAME + '_bucket_a'
    bucket_name1 = bucket_name1.replace('_', '-')
    object_name1 = FILE_NAME + '_object_a'
    bucket_name2 = FILE_NAME + '_bucket_b'
    bucket_name2 = bucket_name2.replace('_', '-')
    object_name2 = FILE_NAME + '_object_b'
    rc1, opt1 = s3_common.add_bucket_by_sk(bucket_name1, ak1, sk1)
    rc2, opt2 = s3_common.add_bucket_by_sk(bucket_name2, ak2, sk2)
    judge_result(rc1, FILE_NAME)
    judge_result(rc2, FILE_NAME)
    common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name1)
    common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name2)

    # 创建对象buc_a>obj_a,acc_b>obj_b
    log.info("4> 分别在账户a,b的桶中创建对象")
    create_file(FILE_NAME, 1)
    rc, o_md5 = common.run_command_shot_time("md5sum %s" % FILE_NAME)
    o_md5 = o_md5[0:32]
    log.info("o_md5: %s" % o_md5)
    rc, opt = s3_common.add_object_by_sk(
        bucket_name1, object_name1, FILE_NAME, ak1, sk1)
    rc, opt = s3_common.add_object_by_sk(
        bucket_name2, object_name2, FILE_NAME, ak2, sk2)
    common.run_command_shot_time("rm %s" % FILE_NAME)

    # 设置ACL
    # 设置读权限
    log.info("5> 对象读权限的设置与验证")
    log.info("********************读权限测试及验证********************")
    ACL_TYPE = "READ"
    string = "PUT" + "\n" + "" + "\n" + "application/x-www-form-urlencoded" + \
        "\n" + "" + "\n" + "" + "/" + bucket_name1 + "/" + object_name1 + "?acl"
    sig = create_sig(sk1, string)
    log.info("******设置的读权限,start.******")
    rc, opt = s3_common.set_object_acl(bucket_name1, object_name1, ak1, account_id1, email1,
                                       account_id2, email2, ACL_TYPE, sig)
    log.info(opt)
    log.info("******设置的读权限,end.******")
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "%s failed!" % FILE_NAME)

    # 验证读权限
    string = "GET" + "\n" + "" + "\n" + "" + "\n" + "" + \
        "\n" + "" + "/" + bucket_name1 + "/" + object_name1
    sig = create_sig(sk2, string)
    log.info("******使用ak2下载obj1,start.******")
    rc, opt = s3_common.download_object(
        bucket_name1, object_name1, FILE_NAME + "_down", ak2, sig)
    print rc
    log.info(opt)
    log.info("******使用ak2下载obj1,end.******")
    rc, d_md5 = common.run_command_shot_time("md5sum %s" % FILE_NAME + "_down")
    d_md5 = d_md5[0:32]
    log.info("d_md5: %s" % d_md5)
    print type(d_md5)
    print type(o_md5)
    if d_md5 == o_md5:
        common.run_command_shot_time("rm %s* -rf" % (FILE_NAME + "_down"))
    else:
        result.result(FILE_NAME, "-1")
        common.judge_rc(-1, 0, "%s failed!" % FILE_NAME)

    # 查询读权限
    StringToSign = "GET" + "\n" + "" + "\n" + "" + "\n" + "" + \
        "\n" + "" + "/" + bucket_name1 + "/" + object_name1 + "?acl"
    sig = create_sig(sk2, StringToSign)
    log.info("******使用错误sig读取obj1的ACL权限,start.******")
    rc1, opt1, opt2, opt3 = s3_common.get_object_acl(
        bucket_name1, object_name1, ak1, "   ")
    rc2, opt1, opt2, opt3 = s3_common.get_object_acl(
        bucket_name1, object_name1, ak1, "@#%$#%$SDF")
    rc3, opt1, opt2, opt3 = s3_common.get_object_acl(
        bucket_name1, object_name1, ak1, sig + "@%$DFG")

    log.info("******使用错误sig读取obj1的ACL权限,end.******")
    if rc1 == rc2 == rc3 == -1:
        pass
    else:
        result.result(FILE_NAME, "-1")
        common.judge_rc(-1, 0, "%s failed!" % FILE_NAME)

    log.info("6> 关闭签名认证")
    rc, opt = s3_common.set_oss_http_auth("0")
    judge_result(rc, FILE_NAME)
    time.sleep(12)
    common.judge_rc(rc, 0, "Close sig-mode failed!")


def main():
    rc, opt = s3_common.set_oss_http_auth("0")
    time.sleep(12)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "Close sig-mode failed!")
    prepare_clean.s3_test_prepare(FILE_NAME, [email1, email2])
    case()
    prepare_clean.s3_test_clean([email1, email2])
    log.info('%s succeed!' % FILE_NAME)
    result.result(FILE_NAME, "0")


if __name__ == '__main__':
    common.case_main(main)

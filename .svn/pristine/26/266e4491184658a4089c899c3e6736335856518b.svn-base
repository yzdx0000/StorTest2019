#! /usr/bin/python
# -*- coding:utf-8 -*-
#**********************************************#
# 标题：功能测试，用例编号29-0-17-64
# 使用方法：python 29-0-17-64_wjl.py
# 在http模式下，复制对象后下载对象，并验证。
# 作者：王建磊
# 创建时间：2018/10/10
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


def judge_result_judge(rc):
    judge_result(rc, FILE_NAME)


def case():
    log.info("1> 开启签名认证")
    rc, opt = s3_common.set_oss_http_auth("1")
    time.sleep(12)
    judge_result_judge(rc)
    common.judge_rc(rc, 0, "Open sig-mode failed!")

    # 创建账户a、b
    log.info("2> 创建账户")
    ak1, sk1, account_id1 = create_acc_cer(account_name1, email1)

    # 账户中创建桶
    log.info("3> 在账户中创建桶")
    log.info("bucket create operation:")
    bucketname = FILE_NAME + '_bucket_a'
    bucketname = bucketname.replace('_', '-')
    bucketname2 = bucketname + "_cp"
    bucketname2 = bucketname2.replace('_', '-')
    objectname = FILE_NAME + '_object_a'
    rc1, opt1 = s3_common.add_bucket_by_sk(bucketname, ak1, sk1)
    rc1, opt1 = s3_common.add_bucket_by_sk(bucketname2, ak1, sk1)
    judge_result_judge(rc1)
    common.judge_rc(rc1, 0, "add bucket %s failed!!!" % bucketname)

    # 创建对象buc_a>obj_a
    log.info("4> 在账户的桶中创建对象")
    create_file(FILE_NAME, 1)
    rc, o_md5 = common.run_command_shot_time("md5sum %s" % FILE_NAME)
    o_md5 = o_md5[0:32]
    log.info("o_md5: %s" % o_md5)
    rc1, opt1 = s3_common.add_object_by_sk(
        bucketname, objectname, FILE_NAME, ak1, sk1)
    common.run_command_shot_time("rm %s" % FILE_NAME)
    judge_result_judge(rc1)

    # 复制对象
    log.info("5> 拷贝对象为obj2")
    CanonicalizedHeaders = "x-amz-copy-source:/" + bucketname + "/" + objectname
    CanonicalizedResource = "/" + bucketname2 + "/" + objectname
    string = "PUT" + "\n" + "" + "\n" + "" + "\n" + "" + "\n" + \
        CanonicalizedHeaders + "\n" + CanonicalizedResource
    print string
    sig = create_sig(sk1, string)
    rc, opt = s3_common.cp_object(
        bucketname2, objectname, ak1, bucketname, objectname, sig)
    log.info(opt)
    if "200 OK" in opt:
        rc = 0
    else:
        rc = -1
    judge_result_judge(rc)

    # 下载对象
    log.info("6> 下载拷贝后的对象")
    string = "GET" + "\n" + "" + "\n" + "" + "\n" + "" + \
        "\n" + "" + "/" + bucketname2 + "/" + objectname
    sig = create_sig(sk1, string)
    rc, opt = s3_common.download_object(
        bucketname2, objectname, FILE_NAME + "_down1", ak1, sig)
    print rc
    log.info(opt)
    rc, d_md5 = common.run_command_shot_time(
        "md5sum %s" % FILE_NAME + "_down1")
    d_md5 = d_md5[0:32]
    log.info("d_md5: %s" % d_md5)
    print type(d_md5)
    print type(o_md5)
    if d_md5 == o_md5:
        common.run_command_shot_time("rm %s* -rf" % (FILE_NAME + "_down1"))
    else:
        judge_result_judge(-1)
        common.judge_rc(-1, 0, "%s failed!" % FILE_NAME)

    log.info("7> 关闭签名认证")
    rc, opt = s3_common.set_oss_http_auth("0")
    judge_result_judge(rc)
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

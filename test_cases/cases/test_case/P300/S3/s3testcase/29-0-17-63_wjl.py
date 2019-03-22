#! /usr/bin/python
# -*- coding:utf-8 -*-
#**********************************************#
# 标题：功能测试，用例编号29-0-17-63
# 使用方法：python 29-0-17-63_wjl.py
# 在http模式下，并发下载对象过程中关闭认证开关，并验证下载内容。
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
from multiprocessing import Process, Manager, Lock

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
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"
CONCURRENCY = 5
OBJECT_NUM_PER_PROCESS = 1

downlock = Lock()
manager1 = Manager()

# 创建成功标志
downflag = manager1.Value('tmp', 0)
process = {}
conf = ConfigParser.ConfigParser()


# 认证开关函数
def sig_auth_on_off():
    for i in range(7):
        s3_common.set_oss_http_auth(0)
        time.sleep(5)
        s3_common.set_oss_http_auth(1)
        time.sleep(5)


# 下载对象函数
def download_obj(
        bucketname,
        objectname,
        filepath,
        ak,
        obj_num,
        o_md5,
        sig,
        downlock):
    for i in range(obj_num):
        rc, opt = s3_common.download_object(
            bucketname, objectname, filepath + str(i), ak, sig)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "Download object failed!")
        rc, d_md5 = common.run_command_shot_time(
            "md5sum %s" % filepath + str(i))
        d_md5 = d_md5[0:32]
        log.info("md5sum: %s" % d_md5)
        log.info("o_md5sum: %s" % o_md5)
        if rc == 0 and o_md5 == d_md5:
            with downlock:
                downflag.value += 1
        log.info("testing delflag=%s" % (str(downflag.value)))


# 并发下载函数
def mul_procs_download_obj(
        bucketname,
        objectname,
        filepath,
        obj_num,
        ak,
        o_md5,
        sig):
    global process
    for i in range(int(CONCURRENCY)):
        process["p" + str(i)] = Process(target=download_obj,
                                        args=(bucketname,
                                              objectname,
                                              filepath + "_p" + str(i) + "a",
                                              ak,
                                              obj_num,
                                              o_md5,
                                              sig,
                                              downlock,
                                              ))
    for j in range(int(CONCURRENCY)):
        process["p" + str(j)].start()
    time.sleep(1)
    s3_common.set_oss_http_auth(0)
    for g in range(int(CONCURRENCY)):
        process["p" + str(g)].join()


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


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, "-1")


# 获取sig函数
def create_sig(sk, StringToSign):
    sig = s3_common.mk_sig(sk, StringToSign)
    sig = s3_common.mk_sig_code(sig)
    return sig


def case():
    global download_filename
    log.info("1> 打开签名认证")
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

    log.info("4> 创建测试用的桶")
    bucketname = FILE_NAME + '_bucket'
    bucketname = bucketname.replace('_', '-')
    rc, opt = s3_common.add_bucket_by_sk(bucketname, certificate_id, sk)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create bucket failed!!!")

    log.info("5> 创建1G对象")
    objectname = FILE_NAME + '_object'
    create_file(FILE_NAME, 1024)
    rc, o_md5 = common.run_command_shot_time("md5sum %s" % FILE_NAME)
    o_md5 = o_md5[0:32]
    rc, opt = s3_common.add_object_by_sk(
        bucketname, objectname, FILE_NAME, certificate_id, sk)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add object failed!!!")
    common.run_command_shot_time("rm %s* -rf" % (FILE_NAME))

    log.info("6> 并发下载1G对象")
    string = "GET" + "\n" + "" + "\n" + "" + "\n" + "" + \
        "\n" + "" + "/" + bucketname + "/" + objectname
    sig = create_sig(sk, string)
    mul_procs_download_obj(
        bucketname,
        objectname,
        FILE_NAME,
        OBJECT_NUM_PER_PROCESS,
        certificate_id,
        o_md5,
        sig)

    if downflag.value == CONCURRENCY * OBJECT_NUM_PER_PROCESS:
        pass
    else:
        judge_result(-1, FILE_NAME)
        common.judge_rc(-1, 0, "Get object md5 failed!!!")

    common.run_command_shot_time("rm %s* -rf" % FILE_NAME)


def main():
    rc, opt = s3_common.set_oss_http_auth("0")
    time.sleep(12)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "Close sig-mode failed!")
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s succeed!' % FILE_NAME)
    result.result(FILE_NAME, "0")


if __name__ == '__main__':
    common.case_main(main)

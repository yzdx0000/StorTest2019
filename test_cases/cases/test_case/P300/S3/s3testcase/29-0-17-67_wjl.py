#! /usr/bin/python
# -*- coding:utf-8 -*-
#**********************************************#
# 标题：功能测试，用例编号29-0-17-67
# 使用方法：python 29-0-17-67_wjl.py
# 在http模式下，并发拷贝对象过程中关闭认证开关
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

copylock = Lock()
manager1 = Manager()

# 创建成功标志
copyflag = manager1.Value('tmp', 0)
process = {}
conf = ConfigParser.ConfigParser()

# 获取sig函数


def create_sig(sk, StringToSign):
    sig = s3_common.mk_sig(sk, StringToSign)
    sig = s3_common.mk_sig_code(sig)
    return sig


# 拷贝对象函数
def copy_obj(
        bucketname2,
        bucketname,
        objectname,
        objectname2,
        ak,
        obj_num,
        copylock):
    for i in range(obj_num):
        rc, opt = s3_common.cp_object(
            bucketname2, objectname2, ak, bucketname, objectname)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "Copy object failed!")
        if rc == 0 and "200 OK" in opt:
            with copylock:
                copyflag.value += 1
        log.info("testing copyflag=%s" % (str(copyflag.value)))


# 并发拷贝函数
def mul_procs_copy_obj(bucketname2, bucketname, objectname, ak, obj_num):
    global process
    for i in range(int(CONCURRENCY)):
        process["p" + str(i)] = Process(target=copy_obj,
                                        args=(bucketname2,
                                              bucketname,
                                              objectname,
                                              objectname + "_p" + str(i) + "a",
                                              ak,
                                              obj_num,
                                              copylock,
                                              ))
    for j in range(int(CONCURRENCY)):
        process["p" + str(j)].start()
    s3_common.set_oss_http_auth(1)
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


def case():
    global download_filename
    log.info("1> 关闭签名认证")
    rc, opt = s3_common.set_oss_http_auth("0")
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
    bucketname2 = bucketname + "_cp"
    bucketname2 = bucketname2.replace('_', '-')
    rc, opt = s3_common.add_bucket_by_sk(bucketname, certificate_id, sk)
    rc, opt = s3_common.add_bucket_by_sk(bucketname2, certificate_id, sk)
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

    log.info("6> 并发拷贝1G对象,过程中打开认证")
    mul_procs_copy_obj(
        bucketname2,
        bucketname,
        objectname,
        certificate_id,
        OBJECT_NUM_PER_PROCESS)

    if copyflag.value == CONCURRENCY * OBJECT_NUM_PER_PROCESS:
        pass
    else:
        judge_result(-1, FILE_NAME)
        common.judge_rc(-1, 0, "Object copy failed!!!")

    log.info("7> 关闭签名认证")
    rc, opt = s3_common.set_oss_http_auth("0")
    judge_result(rc, FILE_NAME)
    time.sleep(12)
    common.judge_rc(rc, 0, "Close sig-mode failed!")


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

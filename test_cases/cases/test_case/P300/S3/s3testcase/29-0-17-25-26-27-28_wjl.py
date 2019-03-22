#! /usr/bin/python
# -*- coding:utf-8 -*-
#**********************************************#
# 标题：功能测试，用例编号29-0-17-25_26_27_28
# 使用方法：python 29-0-17-25_26_27_28_wjl.py
# 在http模式下，并发创建删除桶，打开关闭验证开关，原指令校验认证。日志打印在屏幕上。
# 作者：王建磊
# 创建时间：2018/10/08
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
# 并发操作进程数
CONCURRENCY = 40
# 每个进程循环创建/删除桶的个数
BUCKET_NUM_PER_PROCESS = 10

crelock = Lock()
dellock = Lock()
manager1 = Manager()
manager2 = Manager()

# 创建成功标志
creflag = manager1.Value('tmp', 0)
# 删除成功标志
delflag = manager2.Value('tmp', 0)
process = {}
conf = ConfigParser.ConfigParser()


# 认证开关函数
def sig_auth_on_off():
    for i in range(7):
        s3_common.set_oss_http_auth(0)
        time.sleep(5)
        s3_common.set_oss_http_auth(1)
        time.sleep(5)


# 循环创建桶函数
def loop_crebuck(bucketname, ak, sk, buc_num, crelock):
    for i in range(buc_num):
        rc, opt = s3_common.add_bucket_by_sk(bucketname + str(i), ak, sk)
        log.info(opt)
        if rc == 0:
            pass
        else:
            judge_result(rc, "29-0-17-25")
            judge_result(rc, "29-0-17-26")
        common.judge_rc(rc, 0, "Create bucket failed!")
        if rc == 0:
            with crelock:
                creflag.value += 1
        log.info("testing creflag=%s" % (str(creflag.value)))


# 循环删除桶函数
def loop_delbuck(bucketname, ak, sk, buc_num, dellock):
    for i in range(buc_num):
        rc, opt = s3_common.del_bucket_by_sk(bucketname + str(i), ak, sk)
        if rc == 0:
            pass
        else:
            judge_result(rc, "29-0-17-27")
            judge_result(rc, "29-0-17-28")
            common.judge_rc(rc, 0, "Delete bucket failed!")
        if rc == 0:
            with dellock:
                delflag.value += 1
        log.info("testing delflag=%s" % (str(delflag.value)))


# 并发创建桶函数
def mul_thred_creat_bukt(bucketname, buc_num, ak, sk):
    global process
    for i in range(int(CONCURRENCY)):
        process["p" + str(i)] = Process(target=loop_crebuck,
                                        args=(bucketname + str(i) + "a", ak, sk, buc_num, crelock,))
    print "******************************"
    print process
    print "******************************"
    for j in range(int(CONCURRENCY)):
        process["p" + str(j)].start()
    sig_auth_on_off()
    for g in range(int(CONCURRENCY)):
        process["p" + str(g)].join()


# 并发删除桶函数
def mul_procs_del_bukt(bucketname, buc_num, ak, sk):
    global process
    for i in range(int(CONCURRENCY)):
        process["p" + str(i)] = Process(target=loop_delbuck,
                                        args=(bucketname + str(i) + "a", ak, sk, buc_num, dellock,))
    for j in range(int(CONCURRENCY)):
        process["p" + str(j)].start()
    sig_auth_on_off()
    for g in range(int(CONCURRENCY)):
        process["p" + str(g)].join()


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, "-1")


def judge_result_judge(rc):
    judge_result(rc, "29-0-17-25_wjl")
    judge_result(rc, "29-0-17-26_wjl")
    judge_result(rc, "29-0-17-27_wjl")
    judge_result(rc, "29-0-17-28_wjl")


def case():
    log.info("1> 开启签名认证")
    rc, opt = s3_common.set_oss_http_auth("1")
    time.sleep(12)
    judge_result_judge(rc)
    common.judge_rc(rc, 0, "Open sig-mode failed!")

    log.info("2> 创建账户")
    account_name = FILE_NAME + "_account1"
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    judge_result_judge(rc)
    common.judge_rc(rc, 0, "create account failed!!!")

    log.info("3> 创建证书")
    rc, certificate_id, sk = s3_common.add_certificate(account_id)
    judge_result_judge(rc)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    log.info("4> 并发创建桶过程中切换认证开关")
    bucketname = FILE_NAME + '_bucket'
    bucketname = bucketname.replace('_', '-')
    # rc, opt = s3_common.add_bucket_by_sk(bucketname, certificate_id, sk)
    # print rc, opt
    # loop_crebuck(bucketname, certificate_id, sk, 2, crelock)
    mul_thred_creat_bukt(
        bucketname,
        BUCKET_NUM_PER_PROCESS,
        certificate_id,
        sk)
    if creflag.value == CONCURRENCY * BUCKET_NUM_PER_PROCESS:
        result.result("29-0-17-25_wjl", "0")
        result.result("29-0-17-26_wjl", "0")
    else:
        judge_result(-1, "29-0-17-25_wjl")
        judge_result(-1, "29-0-17-26_wjl")
        common.judge_rc(-1, 0, "Concurrent create bucket failed!!!")

    log.info("5> 并发删除桶过程中切换认证开关")
    mul_procs_del_bukt(bucketname, BUCKET_NUM_PER_PROCESS, certificate_id, sk)
    if delflag.value == CONCURRENCY * BUCKET_NUM_PER_PROCESS:
        result.result("29-0-17-27_wjl", "0")
        result.result("29-0-17-28_wjl", "0")
    else:
        judge_result(-1, "29-0-17-27_wjl")
        judge_result(-1, "29-0-17-28_wjl")
        common.judge_rc(-1, 0, "Concurrent delete bucket failed!!!")

    log.info("6> 关闭签名认证")
    rc, opt = s3_common.set_oss_http_auth("0")
    if rc == 0:
        pass
    else:
        judge_result(rc, "29-0-17-25")
        judge_result(rc, "29-0-17-26")
        judge_result(rc, "29-0-17-27")
        judge_result(rc, "29-0-17-28")
    time.sleep(12)
    common.judge_rc(rc, 0, "Close sig-mode failed!")


def main():
    rc, opt = s3_common.set_oss_http_auth("0")
    time.sleep(12)
    if rc == 0:
        pass
    else:
        judge_result(rc, "29-0-17-25")
        judge_result(rc, "29-0-17-26")
        judge_result(rc, "29-0-17-27")
        judge_result(rc, "29-0-17-28")
    common.judge_rc(rc, 0, "Close sig-mode failed!")
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

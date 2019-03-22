#! /usr/bin/python
# -*- coding:utf-8 -*-
#**********************************************#
# 标题：功能测试，用例编号29-0-17-56_57_58_59
# 使用方法：python 29-0-17-56_57_58_59_wjl.py
# 在http模式下，并发创建删除对象，打开关闭验证开关，原指令校验认证。
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
CONCURRENCY = 50
OBJECT_NUM_PER_PROCESS = 0

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


# 循环创建对象函数
def loop_creobj(bucketname, objectname, file_path, ak, sk, obj_num, crelock):
    for i in range(obj_num):
        rc, opt = s3_common.add_object_by_sk(
            bucketname, objectname + str(i), file_path, ak, sk)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "Create object failed!")
        if rc == 0:
            with crelock:
                creflag.value += 1
        log.info("testing creflag=%s" % (str(creflag.value)))


# 循环删除对象函数
def loop_delobj(bucketname, objectname, ak, sk, obj_num, dellock):
    for i in range(obj_num):
        stringtosign = "DELETE" + "\n" + "" + "\n" + "" + "\n" + "" + \
            "\n" + "" + "/" + bucketname + "/" + objectname + str(i)
        sig = s3_common.mk_sig(sk, stringtosign)
        sig = s3_common.mk_sig_code(sig)
        rc, opt = s3_common.del_object(
            bucketname, objectname + str(i), ak, sig)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "Delete object failed!")
        if rc == 0:
            with dellock:
                delflag.value += 1
        log.info("testing delflag=%s" % (str(delflag.value)))


# 并发创建对象函数
def mul_thred_creat_obj(bucketname, objectname, file_path, obj_num, ak, sk):
    global process
    for i in range(int(CONCURRENCY)):
        process["p" + str(i)] = Process(target=loop_creobj,
                                        args=(bucketname,
                                              objectname + str(i) + "a",
                                              file_path,
                                              ak,
                                              sk,
                                              obj_num,
                                              crelock,
                                              ))
    for j in range(int(CONCURRENCY)):
        process["p" + str(j)].start()
    sig_auth_on_off()
    for g in range(int(CONCURRENCY)):
        process["p" + str(g)].join()


# 并发删除桶函数
def mul_procs_del_obj(bucketname, objectname, obj_num, ak, sk):
    global process
    for i in range(int(CONCURRENCY)):
        process["p" + str(i)] = Process(target=loop_delobj,
                                        args=(bucketname,
                                              objectname + str(i) + "a",
                                              ak,
                                              sk,
                                              obj_num,
                                              dellock,
                                              ))
    for j in range(int(CONCURRENCY)):
        process["p" + str(j)].start()
    sig_auth_on_off()
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


def judge_result_judge(rc):
    judge_result(rc, "29-0-17-56_wjl")
    judge_result(rc, "29-0-17-57_wjl")
    judge_result(rc, "29-0-17-58_wjl")
    judge_result(rc, "29-0-17-59_wjl")


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

    log.info("4> 创建测试用的桶")
    bucketname = FILE_NAME + '_bucket'
    bucketname = bucketname.replace('_', '-')
    rc, opt = s3_common.add_bucket_by_sk(bucketname, certificate_id, sk)
    judge_result_judge(rc)
    common.judge_rc(rc, 0, "create bucket failed!!!")

    log.info("5> 并发创建对象过程中切换认证开关")
    objectname = FILE_NAME + '_object'
    create_file(FILE_NAME, 10)
    # rc, opt = s3_common.add_bucket_by_sk(bucketname, certificate_id, sk)
    # print rc, opt
    # loop_crebuck(bucketname, certificate_id, sk, 2, crelock)
    mul_thred_creat_obj(
        bucketname,
        objectname,
        FILE_NAME,
        OBJECT_NUM_PER_PROCESS,
        certificate_id,
        sk)
    if creflag.value == CONCURRENCY * OBJECT_NUM_PER_PROCESS:
        common.run_command_shot_time("rm %s" % FILE_NAME)
        result.result("29-0-17-56_wjl", "0")
        result.result("29-0-17-57_wjl", "0")
    else:
        judge_result(-1, "29-0-17-56_wjl")
        judge_result(-1, "29-0-17-57_wjl")
        common.judge_rc(-1, 0, "Concurrent create object failed!!!")

    log.info("6> 并发删除对象过程中切换认证开关")
    mul_procs_del_obj(
        bucketname,
        objectname,
        OBJECT_NUM_PER_PROCESS,
        certificate_id,
        sk)
    if delflag.value == CONCURRENCY * OBJECT_NUM_PER_PROCESS:
        result.result("29-0-17-58_wjl", "0")
        result.result("29-0-17-59_wjl", "0")
    else:
        judge_result(-1, "29-0-17-58_wjl")
        judge_result(-1, "29-0-17-59_wjl")
        common.judge_rc(-1, 0, "Concurrent delete bucket failed!!!")

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
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
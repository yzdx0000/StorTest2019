# ! /usr/bin/python
# -*- coding:utf-8 -*-
# **********************************************#
# 标题：功能测试，用例编号29-0-9-18
# 使用方法：python 29-0-9-xx_wjl.py
# 将账户1的object赋予账户2读ACP权限。
# 将该object改为对账户2的完全权限。
# 作者：王建磊
# 创建时间：2018/09/11
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


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, "-1")

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

# 创建账户及证书


def create_acc_cer(account_name, email):
    rc, account_id = s3_common.add_account(account_name, email, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create account failed!!!")
    rc, ak, sk = s3_common.add_certificate(account_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")
    return ak, account_id

# *******************************************
# 设置账户ACL函数
# 设置ACL，key=1;将acc1的object赋予acc2读ACP权限。
# key=2;将acc1的object赋予acc2完全权限
# *******************************************


def acl_set_write(bucket_name, object_name, ak1, accid1, accid2, key):
    ACL_TYPE1 = "READ_ACP"
    ACL_TYPE2 = "FULL_CONTROL"
    if key == "1":
        log.info("设置对象的读ACP权限。")
        rc, opt = s3_common.set_object_acl(
            bucket_name, object_name, ak1, accid1, email1, accid2, email2, ACL_TYPE1)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "%s failed!" % FILE_NAME)
    elif key == "2":
        log.info("设置对象的完全权限。")
        rc, opt = s3_common.set_object_acl(
            bucket_name, object_name, ak1, accid1, email1, accid2, email2, ACL_TYPE2)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "%s failed!" % FILE_NAME)
    else:
        opt = None
    return opt

# *******************************************
# ACL验证函数
# 用ak2对桶上传对象。
# 用ak2对acc1的对象读取ACL操作,下载操作。
# *******************************************


def confirm_acl(bucket_name, objectname, ak2, accid1, accid2, key):
    rc = []
    opt = []
    if key == "1":
        log.info("【对象读ACP权限验证1】,使用ak2修改acc1的对象为READ_ACP权限.")
        rc1, opt1 = s3_common.set_object_acl(
            bucket_name, objectname, ak2, accid1, email1, accid2, email2, "READ_ACP")
        rc.append(rc1)  # 403
        opt.append(opt1)

        log.info("【对象读ACP权限验证2】,使用ak2对acc1的对象读取ACL.")
        rc2, opt2, opt3, opt4 = s3_common.get_object_acl(
            bucket_name, objectname, ak2)
        rc.append(rc2)  # "READ_ACP"
        opt.append(opt4)
        judge_result(rc2, FILE_NAME)
        common.judge_rc(rc2, 0, "%s failed!" % FILE_NAME)

    elif key == "2":
        log.info("【对象完全权限验证1】使用ak2对acc1的对象读取ACL操作。")
        rc2, opt2, opt3, opt4 = s3_common.get_object_acl(
            bucket_name, objectname, ak2)
        judge_result(rc2, FILE_NAME)
        common.judge_rc(rc2, 0, "%s failed!" % FILE_NAME)
        rc.append(rc2)  # "FULL_CONTROL"
        opt.append(opt4)

        log.info("【对象完全权限验证2】使用ak2对acc1的对象进行下载操作，验证对象的ACL读权限")
        rc1, opt5 = s3_common.download_object(
            bucket_name, objectname, FILE_NAME, ak2)
        md5_d = common.run_command_shot_time("md5sum %s" % FILE_NAME)
        common.run_command_shot_time("rm %s" % FILE_NAME)
        judge_result(rc1, FILE_NAME)
        common.judge_rc(rc1, 0, "%s failed!" % FILE_NAME)
        rc.append(rc1)  # "md5_d"
        opt.append(md5_d)
    else:
        rc = []
        opt = []
    return rc, opt


def case():
    log.info("1> 创建账户a/b及其证书")
    ak1, accid1 = create_acc_cer(account_name1, email1)
    ak2, accid2 = create_acc_cer(account_name2, email2)

    log.info("2> 在账户1中创建桶")
    bucket_name1 = FILE_NAME + '_bucket_a'
    bucket_name1 = bucket_name1.replace('_', '-')
    object_name1 = FILE_NAME + '_object_a'
    rc, opt = s3_common.add_bucket(bucket_name1, ak1)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "%s failed!" % FILE_NAME)

    log.info("3> 在账户1的桶中创建对象")
    create_file(FILE_NAME, 2)
    md5_o = common.run_command_shot_time("md5sum %s" % FILE_NAME)
    rc1, opt = s3_common.add_object(bucket_name1, object_name1, FILE_NAME, ak1)
    common.run_command_shot_time("rm %s" % FILE_NAME)
    judge_result(rc1, FILE_NAME)
    common.judge_rc(rc1, 0, "%s failed!" % FILE_NAME)

    log.info("4.1> ACL设置读ACP权限")
    opt1 = acl_set_write(
        bucket_name1,
        object_name1,
        ak1,
        accid1,
        accid2,
        key="1")
    log.info("4.2> ACL读ACP权限验证")
    rc_l1, opt_l1 = confirm_acl(
        bucket_name1, object_name1, ak2, accid1, accid2, key="1")

    log.info("5.1> ACL改为完全权限")
    opt2 = acl_set_write(
        bucket_name1,
        object_name1,
        ak1,
        accid1,
        accid2,
        key="2")
    log.info("5.2> ACL完全权限验证")
    rc_l2, opt_l2 = confirm_acl(
        bucket_name1, object_name1, ak2, accid1, accid2, key="2")

    if "200 OK" in opt1 and "200 OK" in opt2 and "READ_ACP" == opt_l1[1][
            0] and "403" in opt_l1[0] and "FULL_CONTROL" == opt_l2[0][0] and opt_l2[1] == md5_o:
        pass
    else:
        judge_result(-1, FILE_NAME)
        common.judge_rc(-1, 0, "%s failed!" % FILE_NAME)


def main():
    rc, opt = s3_common.set_oss_http_auth("0")
    time.sleep(6)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "Close sig-mode failed!")
    prepare_clean.s3_test_prepare(FILE_NAME, [email1, email2])
    case()
    prepare_clean.s3_test_clean([email1, email2])
    log.info('%s succeed!' % FILE_NAME)
    result.result(FILE_NAME, "0")


if __name__ == '__main__':
    common.case_main(main)

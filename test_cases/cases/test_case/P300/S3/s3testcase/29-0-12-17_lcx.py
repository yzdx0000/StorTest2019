#!/usr/bin/python
# -*-coding:utf-8 -*
import os
import threading
import time

import utils_path
import common
import s3_common
import log
import prepare_clean
import result

##########################################################################
#
# Author: lichengxu
# date 2018-12-07
# @summary：
#    验证每个账户最多添加5个证书
# @steps:
#    1、创建账户；
#    2、检查账户是否存在;
#    3、创建5个证书；
#    4、创建第6个证书
#    5、清理环境
#
# @changelog：
##########################################################################
# 本脚本名字
FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]
FILE_NAME = FILE_NAME.replace('-', '_')
test_path = "/tmp/s3test"


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, -1)


class MyThread(threading.Thread):
    def __init__(self, func, args=(), name=""):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
        self.name = name

    def run(self, ):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None

    def get_func_name(self):
        return self.name


def case():
    account_email_lst = []
    account_email = FILE_NAME + "@sugon.com"
    account_name = FILE_NAME + "_account_1"
    account_email_lst.append(account_email)
    log.info("1> 创建账户 %s" % account_name)
    rc, account_id = s3_common.add_account(account_name, account_email, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add_account %s failed!!!" % account_name)

    log.info("2> 验证账户 %s" % account_name)
    rc, stdout = s3_common.find_account(account_email)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "find account %s failed!!!" % account_email)

    log.info("3> 添加账户 %s 的证书" % account_name)
    for i in range(5):
        rc, certificate_id, certificate = s3_common.add_certificate(account_id)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "create certificate failed!!!")
    log.info("add five certificates success")

    log.info("4> 添加账户 %s 的第6个证书" % account_name)
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    common.judge_rc_unequal(rc, 0, "create certificate failed!!!")
    log.info("add sixth certificate failed!")

    log.info("5> 检查环境")
    prepare_clean.test_prepare(FILE_NAME, )

    log.info('%s success!' % FILE_NAME)
    result.result(FILE_NAME, 0)

    return account_email_lst


def main():
    prepare_clean.s3_test_prepare(FILE_NAME)
    account_email_lst = case()
    prepare_clean.s3_test_clean(account_email_lst)
    log.info('%s finish!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

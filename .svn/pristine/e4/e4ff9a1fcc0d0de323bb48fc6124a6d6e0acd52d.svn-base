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
#    验证添加100w 账户，并给每个账户添加证书
# @steps:
#    1、创建账户；
#    2、检查账户是否存在;
#    3、创建证书；
#    8、清理环境
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


def add_account_lst(account_name_lst, account_email_lst):
    for account_name, account_email in zip(account_name_lst, account_email_lst):
        s3_common.add_account(account_name, account_email, 0)


def del_account_lst(account_email_lst):
    for account_email in account_email_lst:
        rc, account_id = s3_common.get_account_id_by_email(account_email)
        s3_common.del_account(account_id)

def case():
    """单线程方法"""
    # account_email_lst = []
    # account_name_lst = []
    # for i in range(100):
    #     account_email = FILE_NAME + "_%s@sugon.com" % i
    #     account_name = FILE_NAME + "_account_%s" % i
    #     account_email_lst.append(account_email)
    #     account_name_lst.append(account_name)
    #     log.info("创建账户 %s" % account_name)
    #     rc, account_id = s3_common.add_account(account_name, account_email, 0)
    #     judge_result(rc, FILE_NAME)
    #     common.judge_rc(rc, 0, "add_account %s failed!!!" % account_name)

        # log.info("创建账户 %s 的证书" % account_name)
        # rc, certificate_id, certificate = s3_common.add_certificate(account_id)
        # judge_result(rc, FILE_NAME)
        # common.judge_rc(rc, 0, "create certificate failed!!!")


    """多线程方法"""
    account_email_lst = []
    account_name_lst = []
    for i in range(1000000):
        account_email = FILE_NAME + "_%s@sugon.com" % i
        account_name = FILE_NAME + "_account_%s" % i
        account_email_lst.append(account_email)
        account_name_lst.append(account_name)


    thread_list = []
    coefficient = 10000
    for i in range(100):
        t = MyThread(add_account_lst, args=(account_name_lst[(coefficient*i):(coefficient*(i+1))],
                                            account_email_lst[(coefficient*i):(coefficient*(i+1))], ))
        thread_list.append(t)

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()

    log.info("10> 检查环境")
    prepare_clean.test_prepare(FILE_NAME, )

    log.info('%s success!' % FILE_NAME)
    result.result(FILE_NAME, 0)


def clean_account():
    # 多线程 批量删除账户
    account_email_lst = []
    for i in range(1000000):
        account_email = FILE_NAME + "_%s@sugon.com" % i
        account_email_lst.append(account_email)

    thread_list = []
    coefficient = 10000
    for i in range(100):
        t = MyThread(del_account_lst, args=(account_email_lst[(coefficient * i):(coefficient * (i + 1))],))
        thread_list.append(t)

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()


def main():
    prepare_clean.s3_test_prepare(FILE_NAME)
    case()
    clean_account()
    log.info('%s finish!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

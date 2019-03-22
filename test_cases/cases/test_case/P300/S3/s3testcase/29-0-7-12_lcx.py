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
# date 2018-12-4
# @summary：
#    bucket删除的同时，查询object的 ACL
# @steps:
#    1、创建两个账户，一个所有者账户，一个查询账户；
#    2、检查账户是否存在
#    3、创建证书；
#    4、创建桶，给所有者账户创建桶
#    5、创建文件，并给所有者账户上传对象
#    6、给对象设置ACL权限
#    7、删除桶，同时给查询对象的ACL权限
#    8、检查环境
#    9、清理环境
#
# @changelog：
##########################################################################
# 本脚本名字
FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"
ACCOUNT_EMAIL_2 = FILE_NAME + "2@sugon.com"
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
    log.info("1> 创建账户")
    account_name = FILE_NAME + "_account1"
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add_account %s failed!!!" % account_name)

    account_name_2 = FILE_NAME + "_account2"
    rc, account_id_2 = s3_common.add_account(account_name_2, ACCOUNT_EMAIL_2, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add_account %s failed!!!" % account_name)

    log.info("2> 检查账户是否存在")
    rc, stdout = s3_common.find_account(ACCOUNT_EMAIL)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "find account %s failed!!!" % ACCOUNT_EMAIL)

    rc, stdout = s3_common.find_account(ACCOUNT_EMAIL_2)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "find account %s failed!!!" % ACCOUNT_EMAIL_2)

    log.info("3> 创建证书")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    rc, certificate_id_2, certificate_2 = s3_common.add_certificate(account_id_2)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    bucket_name_lst_base = []
    log.info("4> 创建桶")
    bucket_name = FILE_NAME + '_bucket_1'
    bucket_name = bucket_name.replace('_', '-')
    bucket_name_lst_base.append(bucket_name)
    rc, stdout = s3_common.add_bucket(bucket_name, certificate_id)
    common.judge_rc(rc, 0, "add and delete bucket failed!")
    '''验证桶'''
    rc, stdout = s3_common.check_bucket(bucket_name, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "check bucket %s failed!!!" % bucket_name)
    log.info("add bucket success!")

    log.info("5> 创建文件，并上传对象")
    """创建10M文件"""
    file_size = 10  # 单位是M
    cmd = "rm -rf %s" % test_path
    common.command(cmd)
    os.mkdir(test_path)
    file_path = os.path.join(test_path, 'file1')
    rc, stdout = s3_common.create_file_m(file_path, file_size)
    common.judge_rc(rc, 0, "create file %s failed!!!" % file_path)
    log.info("create file success!")
    """上传对象"""
    object_name_lst_base = []
    object_name = FILE_NAME + '_object_1'
    rc, stdout = s3_common.add_object(bucket_name, object_name, file_path, certificate_id)
    common.judge_rc(rc, 0, "add object %s failed!!!" % object_name)
    object_name_lst_base.append(object_name)
    log.info("upload object success!")

    log.info("6> 给对象设置ACL权限")
    ACL_TYPE = "FULL_CONTROL"
    rc, stdout = s3_common.set_object_acl(bucket_name, object_name, certificate_id, account_id,
                                          ACCOUNT_EMAIL, account_id_2, ACCOUNT_EMAIL_2, ACL_TYPE)
    common.judge_rc(rc, 0, "set object acl failed!")
    log.info("set object acl success!")

    log.info("7> 删除桶，同时查询账户所有者账户桶下对象的ACL权限")
    threads = []
    thread1 = MyThread(s3_common.del_bucket, args=(bucket_name, certificate_id, ))
    thread2 = MyThread(s3_common.get_object_acl, args=(bucket_name, object_name, certificate_id_2, ))
    threads.append(thread1)
    threads.append(thread2)

    for thread in threads:
        thread.setDaemon(True)
        thread.start()
        time.sleep(1)

    for thread in threads:
        thread.join()

    for thread in [thread1, thread2]:
        log.info(
            "in func %s, the (final_rc, acl_num) is %s" %
            (thread.get_func_name, thread.get_result()))
        # common.judge_rc(thread.get_result()[0], 0, "%s excute failed" % thread.get_func_name())
    log.info("delete bucket and get bucket acl success!")

    log.info("8> 检查环境")
    prepare_clean.test_prepare(FILE_NAME, )

    log.info("9> 获取账户内所有的桶")
    rc, bucket_name_lst = s3_common.get_all_bucket_name(certificate_id)
    common.judge_rc(rc, 0, "get bucket failed!!!")

    log.info('%s success!' % FILE_NAME)
    result.result(FILE_NAME, 0)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL, ACCOUNT_EMAIL_2])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL, ACCOUNT_EMAIL_2])
    log.info('%s finish!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

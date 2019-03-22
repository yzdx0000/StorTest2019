#!/usr/bin/python
# -*-coding:utf-8 -*
import os

import utils_path
import common
import s3_common
import log
import get_config
import prepare_clean
import result

###################################################################################
#
# Author: liuping
# date 2018-09-07
# @summary：
#    设置桶的ACL-READ_ACP权限
# @steps:
#    1、创建两个账户；
#    2、分别别账户添加证书；
#    3、向账户1中上传5个桶，
#    4、向账户1的其中的1个桶中上传10个对象
#    5、向账户2中上传5个桶
#    6、获取账户1和账户2的桶列表
#    7、账户1赋予账户2其中一个桶的READ_ACP权限
#    8、验证账户2对账户1的桶具有READ_ACP权限
#    9、清理环境
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
current_path = os.path.abspath('')
current_uppath = os.path.dirname(current_path)
S3outputpath = os.path.join(current_uppath, 'S3output')
filepath = os.path.join(S3outputpath, FILE_NAME)


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, -1)


ACCOUNT_EMAIL_LST = []
for i in range(2):
    i += 1
    ACCOUNT_EMAIL = FILE_NAME + str(i) + "@sugon.com"
    ACCOUNT_EMAIL_LST.append(ACCOUNT_EMAIL)


def case():
    log.info("1> 创建两个账户")
    i = 0
    account_id_lst = []
    account_name_lst = []
    for account_email in ACCOUNT_EMAIL_LST:
        i += 1
        account_name = FILE_NAME + '_account_%d' % i
        account_name_lst.append(account_name)
        rc, account_id = s3_common.add_account(account_name, account_email, 0)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "add_account %s failed!!!" % account_name)
        account_id_lst.append(account_id)
        """检查账户是否存在"""
        rc, stdout = s3_common.find_account(account_email)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "find account %s failed!!!" % account_email)

    log.info(account_id_lst)
    log.info("2> 每个账户添加账户信息")
    certificate_id_lst = []
    for account_id in account_id_lst:
        rc, certificate_id, certificate = s3_common.add_certificate(account_id)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "add certificate by accountid %s failed!!!" % account_id)
        certificate_id_lst.append(certificate_id)

    owner_account_name = account_name_lst[0]
    owner_account_id = account_id_lst[0]
    owner_certificate_id = certificate_id_lst[0]
    owner_account_email = ACCOUNT_EMAIL_LST[0]

    dst_account_name = account_name_lst[1]
    dst_account_id = account_id_lst[1]
    dst_certificate_id = certificate_id_lst[1]
    dst_account_email = ACCOUNT_EMAIL_LST[1]

    log.info("3> 为账户%s上传5个桶,并向桶0中上传10个对象" % owner_account_name)
    owner_bucket_name_lst = []
    for j in range(5):
        owner_bucket_name = owner_account_name + '_bucket_%d' % j
        owner_bucket_name = owner_bucket_name.replace('_','-')
        owner_bucket_name_lst.append(owner_bucket_name)
        rc, stdout = s3_common.add_bucket(owner_bucket_name, owner_certificate_id, exe_node_ip=None)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "add bucket %s failed!!!" % owner_bucket_name)

        rc, stdout = s3_common.check_bucket(owner_bucket_name, owner_certificate_id, exe_node_ip=None)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "check bucket %s failed!!!" % owner_bucket_name)

    rc, stdout = s3_common.create_file_m(filepath, 10, exe_node_ip=None)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create_file_m fail!!!")

    bucket_name = owner_bucket_name_lst[0]
    for k in range(10):
        object_name = bucket_name + '_obj_%d' % k
        rc, stdout = s3_common.add_object(bucket_name, object_name, filepath, owner_certificate_id, exe_node_ip=None)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "add_object %s fail!!!" % object_name)

    log.info("3> 为账户%s上传5个桶" % dst_account_name)
    dst_bucket_name_lst = []
    for j in range(5):
        dst_bucket_name = dst_account_name + '_bucket_%d' % j
        dst_bucket_name = dst_bucket_name.replace('_','-')
        dst_bucket_name_lst.append(dst_bucket_name)
        rc, stdout = s3_common.add_bucket(dst_bucket_name, dst_certificate_id, exe_node_ip=None)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "add bucket %s failed!!!" % dst_bucket_name)

        rc, stdout = s3_common.check_bucket(dst_bucket_name, dst_certificate_id, exe_node_ip=None)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "check bucket %s failed!!!" % dst_bucket_name)

    log.info("3> 每个账户获取各自的桶列表")
    for certificate_id in certificate_id_lst:
        rc, stdout = s3_common.get_all_bucket(certificate_id)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "get_all_bucket by %s failed!!!" % certificate_id)

    log.info("3> 账户%s赋予账户%s对桶%s的READ_ACP权限" % (owner_account_name, dst_account_name, bucket_name))
    rc, stdout = s3_common.set_bucket_acl(bucket_name, owner_certificate_id, owner_account_id, owner_account_email,
                                          dst_account_id, dst_account_email, "READ_ACP", exe_node_ip=None)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "账户%s赋予账户%s对桶%s的READ_ACP权限时"
                           "失败" % (owner_account_name, dst_account_name, bucket_name))

    log.info("5> 验证账户%s对桶%s有READ_ACP权限是否设置成功" % (dst_account_name, bucket_name))
    rc = s3_common.get_bucket_acl(bucket_name, dst_certificate_id, exe_node_ip=None)
    judge_result(rc[0], FILE_NAME)
    common.judge_rc(rc[0], 0, "验证账户%s对桶%s有READ_ACP权限时，失败" % (bucket_name, dst_account_name))

    result.result(FILE_NAME, 0)
    log.info("%s success" % FILE_NAME)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, ACCOUNT_EMAIL_LST)
    case()
    prepare_clean.s3_test_clean(ACCOUNT_EMAIL_LST)
    log.info('%s finish!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

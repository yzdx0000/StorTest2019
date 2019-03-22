#!/usr/bin/python2.6
# -*- coding: utf-8 -*-


import os
import sys
import random

import utils_path
import common
import s3_common
import log
import get_config
import prepare_clean
import result

###################################################################################
#
# Author: liuyzhb
# date 2018-09-11
# @summary：
#    测试object允许设置的acl的上限，设置成功后验证在此极限值下，acl的读权限依然可以成功
# @steps:
#    1、创建账户；
#    2、给账户添加证书；
#    3、上传桶；
#    4、上传对象
#    5、创建目标账户及目标证书
#    6、设置对象的acl，设置100条
#    7、重新设置对象的acl，设置101条
#    8、删除目标账户
#    9、清理环境
#
# @changelog：
####################################################################################

# 全局变量
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"
des_account_num = 100
des_account_pre = FILE_NAME + "_des_acc_"
des_account_name_list = []
des_account_email_list = []

for i in range(1, des_account_num + 1):
    log.info("创建目标账户")
    des_account_name_tmp = des_account_pre + str(i)
    des_account_name_list.append(des_account_name_tmp)
    des_account_email_tmp = des_account_name_tmp + "@sugon.com"
    des_account_email_list.append(des_account_email_tmp)
for i in range(1, des_account_num + 1):
    log.info("创建目标账户")
    des_account_name_tmp = des_account_pre + str(i)
    des_account_name_list.append(des_account_name_tmp)
    des_account_email_tmp = des_account_name_tmp + "@sugon.com"
    des_account_email_list.append(des_account_email_tmp)


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, "-1")


def case():
    log.info("1> 创建账户")
    account_name = FILE_NAME + "_account1"
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create account failed!!!")

    log.info("2> 创建证书")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    log.info("3> 上传桶")
    obj_node = common.Node()
    ooss_node_lst = s3_common.get_ooss_node_ids()
    oossid = ooss_node_lst[0]
    oossip = obj_node.get_node_ip_by_id(oossid)
    bucket_name = FILE_NAME + '_bucket1'
    bucket_name = bucket_name.replace('_', '-')
    rc, stdout = s3_common.add_bucket(bucket_name, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add bucket failed!!!")

    log.info("4> 上传对象")
    # file_path = "/tmp/file%s" % FILE_NAME
    size = 3  # 以M为单位
    test_path = '/tmp/s3test'
    if os.path.exists(test_path):
        cmd = "rm -rf %s" % test_path
        common.run_command_shot_time(cmd)
    os.mkdir(test_path)
    file_path = os.path.join(test_path, 'file_10m')
    rc, stdout = s3_common.create_file_m(file_path, size)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create file failed!!!")

    object_name = FILE_NAME + '_object1'
    rc, stdout = s3_common.add_object(bucket_name, object_name, file_path, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "put object failed!!!")

    log.info("5> 创建目标账户及目标证书")
    global des_account_num
    global des_account_pre
    global des_account_name_list
    global des_account_email_list
    des_account_id_list = []
    for i in range(1, des_account_num + 1):
        log.info("创建目标账户")
        des_account_name_tmp = des_account_pre + str(i)
        des_account_name_list.append(des_account_name_tmp)
        des_account_email_tmp = des_account_name_tmp + "@sugon.com"
        des_account_email_list.append(des_account_email_tmp)

        rc, account_id_tmp = s3_common.add_account(des_account_name_tmp, des_account_email_tmp, 0)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "create destination account failed!!!")
        des_account_id_list.append(account_id_tmp)

        rc, certificate_id_tmp, certificate_tmp = s3_common.add_certificate(account_id_tmp)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "create certificate failed!!!")

    log.info("6> 设置对象的acl，设置100条")
    operation = "READ"
    des_account_info_list = []
    for i in range(0, des_account_num):
        account_id_curr = des_account_id_list[i]
        account_email_curr = des_account_email_list[i]
        des_account_info_list.append({'account_id': account_id_curr, 'account_email': account_email_curr})
    rc, output = s3_common.set_object_acl_multi(bucket_name, object_name, certificate_id, account_id, ACCOUNT_EMAIL,
                                                des_account_info_list, operation)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "set object multi acls failed!!!")

    log.info("7> 给每个目标节点创建一个certificate")
    certificateids = []
    for id in des_account_id_list:
        rc, certificate_id, certificate = s3_common.add_certificate(id)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "add certificate failed!!!")
        certificateids.append(certificate_id)

    # 步骤9：验证Object的读权限已经赋予成功
    log.info("8> 验证object的读权限已经赋予成功")
    for j in range(len(certificateids)):
        accountname = des_account_name_list[j]
        log.info('验证账户%s是否有对象的读权限' % accountname)
        certificate = certificateids[j]
        rc, stdout = s3_common.download_object_print(bucket_name, object_name, certificate)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "100个账户的读权限赋予失败 failed!!!")
        log.info('账户%s已经有对象的读权限' % accountname)
    log.info('object的读权限已经赋予成功!!!!!!!!!!!!')


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    prepare_clean.s3_test_prepare(FILE_NAME, des_account_email_list)
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    prepare_clean.s3_test_clean(des_account_email_list)
    log.info('%s finished!' % FILE_NAME)
    result.result(FILE_NAME, "0")


if __name__ == '__main__':
    common.case_main(main)

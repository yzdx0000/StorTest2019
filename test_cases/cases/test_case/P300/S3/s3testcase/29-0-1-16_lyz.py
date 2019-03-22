# -*- coding:utf-8 -*
####################################################################################
#
# Author: liuyzhb
# date 2018-01-19
# @summary：
#    给桶创建100条acl，分别赋予给100个账户，验证在此极限值下，桶的acl的读权限已经赋予成功
# @steps:
#    1、创建账户；
#    2、创建证书；
#    3、创建桶；
#    4、创建目标账户及目标证书；
#    5、设置桶的acl，设置100条
#    6、给每个目标节点创建一个certificate
#    7、验证桶的读权限设置成功

# @changelog：
####################################################################################
import os,sys,commands
#import imports3libpath
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

# 全局变量
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"
# ACCOUNT_EMAIL = FILE_NAME + "@1sugon.com"
des_account_email_list = []
des_account_num = 100
des_account_pre = FILE_NAME + "_des_acc_"
des_account_name_list = []
for i in range(1, des_account_num + 1):
    des_account_name_tmp = des_account_pre + str(i)
    des_account_name_list.append(des_account_name_tmp)
    des_account_email_tmp = des_account_name_tmp + "@sugon.com"
    des_account_email_list.append(des_account_email_tmp)
    # print 'des_account_email_list is '
    # print des_account_email_list


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, "-1")


def case():
    log.info("1> 创建账户")
    account_name = FILE_NAME + "_account1"
    # account_name = FILE_NAME + "_account11"
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
    # bucket_name = FILE_NAME + '_bucket11'
    rc, stdout = s3_common.add_bucket(bucket_name, certificate_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add bucket failed!!!")

    log.info("3> 上传对象")
    """创建10M文件"""
    test_path = '/tmp/s3test'
    if os.path.exists(test_path):
        cmd = "rm -rf %s" % test_path
        common.run_command_shot_time(cmd)
    os.mkdir(test_path)
    file_path = os.path.join(test_path, 'file_10m')
    rc, stdout = s3_common.create_file_m(file_path, 10)
    common.judge_rc(rc, 0, "create file %s failed!!!" % (file_path))
    object_name_lst_base = []
    object_name = FILE_NAME + '_object'
    rc, stdout = s3_common.add_object(bucket_name, object_name, file_path, certificate_id)
    common.judge_rc(rc, 0, "add object %s failed!!!" % object_name)
    object_name_lst_base.append(object_name)

    log.info("4> 创建目标账户及目标证书")
    global des_account_num
    global des_account_pre
    des_account_name_list = []
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

    log.info("5> 设置桶的acl，设置100条")
    operation = "READ"
    des_account_info_list = []
    for i in range(0, des_account_num):
        account_id_curr = des_account_id_list[i]
        account_email_curr = des_account_email_list[i]
        des_account_info_list.append({'account_id': account_id_curr, 'account_email': account_email_curr})

    rc, output = s3_common.set_bucket_acl_multi(bucket_name, certificate_id, account_id, ACCOUNT_EMAIL,
                                                des_account_info_list, operation)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "set bucket multi acls failed!!!")

    log.info("6> 给每个目标节点创建一个certificate")
    certificateids = []
    for id in des_account_id_list:
        rc, certificate_id, certificate = s3_common.add_certificate(id)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "add certificate failed!!!")
        certificateids.append(certificate_id)
    # 步骤7：验证桶的读权限设置成功了（测试对象相关的用例acl时，注释掉该步骤）
    log.info("7> 验证桶的读权限设置成功")
    for j in range(len(certificateids)):
        account_name = des_account_name_list[j]
        log.info("7>  验证账户 %s 对桶的读权限设置是否成功" % account_name)
    # for certificateidt in certificateids:
        rc, object_name_lst = s3_common.get_all_object_in_bucket(bucket_name, certificateids[j],
                                                                 exe_node_ip=None, retry=False)
        log.info('rc of getobjects in bucket is  %s' % rc)
        judge_result(rc, FILE_NAME)
        log.info('after juegeresult rc of getobjects in bucket is  %s' % rc)
        common.judge_rc(rc, 0, "验证桶的读权限设置失败!!!")


def main():
    global allaccountemais
    # global allaccountemais
    log.info('**************global emails is ********************** ')
    log.info(des_account_email_list)
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL], env_check=False)
    prepare_clean.s3_test_prepare(FILE_NAME, des_account_email_list)
    case()
    log.info('**************after case global emails is ********************** ')
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    log.info(des_account_email_list)
    prepare_clean.s3_test_clean(des_account_email_list)
    log.info('%s succeed!' % FILE_NAME)
    result.result('29-0-1-16_lyz', 0)


if __name__ == "__main__":
    common.case_main(main)


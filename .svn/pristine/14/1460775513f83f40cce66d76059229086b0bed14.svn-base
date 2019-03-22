#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import os
import sys
import time

import utils_path
import common
import s3_common
import log
import get_config
import prepare_clean
import shell
import make_fault
import result

##########################################################################
#
# Author: zhanghan
# date 2018-09-12
# @summary：
#    验证单个账户下允许创建的桶的个数上限
# @steps:
#    1、设置bucket上限为100，并重启oOms和oOss服务使设置生效
#    2、创建账户；
#    3、给账户添加证书；
#    4、上传多个桶，直至设定的上限值；
#    5、将bucket上限恢复为默认值10000，重启oOms和oOss服务使设置生效
#    6、清理环境
#
# @changelog：
##########################################################################

# 全局变量
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"
BUCKET_UPPER_LIMIT = 100
BUCKET_UPPER_LIMIT_DEFAULT = 10000


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, "-1")


def after_kill_recovery_process(node_ip, service_type):      # copied from liuping
    obj_node = common.Node()
    node_id = obj_node.get_node_id_by_ip(node_ip)
    rc, service_state = s3_common.get_node_service_state(node_id, service_type)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "%s get_node_service_state fail" % node_ip)
    if service_state == 'OK':
        # proc_name = ''
        # if service_type == 'oOss':
        #     proc_name = '/home/parastor/oss/oOss'
        # elif service_type == 'oOms':
        #     proc_name = '/home/parastor/oms/oOms'

        make_fault.kill_process(node_ip, service_type)
        while True:
            rc, service_state = s3_common.get_node_service_state(
                node_id, service_type)
            if service_state == 'OK':
                break
            else:
                time.sleep(2)
    else:
        time.sleep(5)


def case():
    log.info("1> 设置bucket上限为100，并重启oOms和oOss服务使设置生效")
    rc, output = common.update_param(section='oApp', name='pos_account_max_bucket_nr', current=BUCKET_UPPER_LIMIT)
    judge_result(rc, FILE_NAME)
    common.judge_rc(
        rc, 0, "set pos_account_max_bucket_nr to %d fail" %
        BUCKET_UPPER_LIMIT)

    ooms_node_lst = s3_common.get_ooms_node_ids()
    ooss_node_lst = s3_common.get_ooss_node_ids()
    obj_node = common.Node()

    service_type_list = ['oOms', 'oOss']
    for ooms_node_tmp, ooss_node_tmp in zip(ooms_node_lst, ooss_node_lst):
        killoomsip_tmp = obj_node.get_node_ip_by_id(ooms_node_tmp)
        after_kill_recovery_process(killoomsip_tmp, service_type_list[0])
        time.sleep(2)

        killoossip_tmp = obj_node.get_node_ip_by_id(ooss_node_tmp)
        after_kill_recovery_process(killoossip_tmp, service_type_list[1])
        time.sleep(2)

    time.sleep(60)
    log.info("2> 创建账户")
    account_name = FILE_NAME + "_account1"
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create account failed!!!")

    log.info("3> 创建证书")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    log.info("4> 上传桶")
    # obj_node = common.Node()
    # ooss_node_lst = s3_common.get_ooss_node_ids()
    # oossid = ooss_node_lst[0]
    # oossip = obj_node.get_node_ip_by_id(oossid)
    for i in range(1, BUCKET_UPPER_LIMIT + 1):
        bucket_name_tmp = FILE_NAME + '_bucket' + str(i)
        bucket_name_tmp.replace('_', '-')
        rc, stdout = s3_common.add_bucket(bucket_name_tmp, certificate_id)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "add bucket failed!!!")

    bucket_name_last = FILE_NAME + '_bucket' + str(BUCKET_UPPER_LIMIT + 1)
    bucket_name_last.replace('_', '-')
    rc, stdout = s3_common.add_bucket(bucket_name_last, certificate_id)
    if rc != -1:
        result.result(FILE_NAME, "-1")
        common.judge_rc(rc, -1, "failed, the bucket upper limit don't take effect!!!")
    else:
        log.info("success, the bucket upper limit take effect")

    log.info("5> 将bucket上限恢复为默认值10000，重启oOms和oOss服务使设置生效")
    rc, stdout = common.update_param(section='oApp', name='pos_account_max_bucket_nr',
                                     current=BUCKET_UPPER_LIMIT_DEFAULT)
    judge_result(rc, FILE_NAME)
    common.judge_rc(
        rc, 0, "set pos_account_max_bucket_nr to default %d fail" %
        BUCKET_UPPER_LIMIT_DEFAULT)
    ooms_node_lst = s3_common.get_ooms_node_ids()
    ooss_node_lst = s3_common.get_ooss_node_ids()
    obj_node = common.Node()

    service_type_list = ['oOms', 'oOss']
    for ooms_node_tmp, ooss_node_tmp in zip(ooms_node_lst, ooss_node_lst):
        killoomsip_tmp = obj_node.get_node_ip_by_id(ooms_node_tmp)
        after_kill_recovery_process(killoomsip_tmp, service_type_list[0])
        time.sleep(2)

        killoossip_tmp = obj_node.get_node_ip_by_id(ooss_node_tmp)
        after_kill_recovery_process(killoossip_tmp, service_type_list[1])
        time.sleep(2)
    time.sleep(60)

    log.info("6> 用例%s执行成功" % FILE_NAME)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s finished!' % FILE_NAME)
    result.result(FILE_NAME, "0")


if __name__ == '__main__':
    common.case_main(main)

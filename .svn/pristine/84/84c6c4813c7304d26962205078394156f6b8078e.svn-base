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
import make_fault
import time
import random
from multiprocessing import Process
import shell
###################################################################################
#
# Author: liuping
# date 2018-09-08
# @summary：
#    随机选择一个杀一个节点的oOms进程,恢复进程后下载对象
# @steps:
#    1、创建账户；
#    2、检查账户创建成功
#    3、创建证书；
#    4、上传桶
#    5、随机选择一个杀一个节点的oOms进程,恢复进程后下载对象
#    6、清理环境
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
current_path = os.path.abspath('')
current_uppath = os.path.dirname(current_path)
S3outputpath = os.path.join(current_uppath, 'S3output')
filepath = os.path.join(S3outputpath, FILE_NAME)
log_file_path = log.get_log_path(FILE_NAME)
log.init(log_file_path, True)

ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, -1)


def after_kill_recovery_process(node_ip, service_type, othername):
    obj_node = common.Node()
    node_id = obj_node.get_node_id_by_ip(node_ip)
    rc, service_state = s3_common.get_node_service_state(node_id, service_type)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "%s get_node_service_state fail" % node_ip)
    if service_state == 'OK':
        proc_name = ''
        if service_type == 'oOss':
            proc_name = '/home/parastor/oss/oOss'
        elif service_type == 'oOms':
            proc_name = '/home/parastor/oms/oOms'
        cmd = 'mv ' + proc_name + ' ' + proc_name + othername
        log.info(cmd)
        shell.ssh(node_ip, cmd)
        make_fault.kill_process(node_ip, service_type)
        while True:
            rc, service_state = s3_common.get_node_service_state(node_id, service_type)
            log.info('********the process %s of node %s is %s********' % (service_type, node_ip, service_state))
            if service_state == 'SHUTDOWN':
                break
            else:
                time.sleep(2)

        time.sleep(60)
        cmd = 'mv ' + proc_name + othername + ' ' + proc_name
        log.info(cmd)
        shell.ssh(node_ip, cmd)
        while True:
            rc, service_state = s3_common.get_node_service_state(node_id, service_type)
            if service_state == 'OK':
                break
            else:
                time.sleep(2)
    else:
        time.sleep(5)


def get_many_obj(bucket_name, object_name_lst, getpath, certificate_id):
    for object_name in object_name_lst:
        if os.path.exists(getpath + '/' + object_name):
            cmd = "rm -rf %s" % getpath + '/' + object_name
            log.info(cmd)
            shell.sh(cmd, raise_exception=True)
        rc, stdout = s3_common.download_object(bucket_name, object_name,  getpath + '/' + object_name,
                                               certificate_id, retry=True)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "download_object %s fail!!!" % object_name)


def case():
    object_num = 50
    service_type = 'oOms'
    othername = '.bak'
    getpath = S3outputpath

    log.info("1> 创建账户")
    account_name = FILE_NAME + "_account1"
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add_account %s failed!!!" % account_name)

    log.info("2> 检查账户是否存在")
    rc, stdout = s3_common.find_account(ACCOUNT_EMAIL)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "find account %s failed!!!" % ACCOUNT_EMAIL)

    log.info("3> 创建证书")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    log.info("4> 上传1个桶")
    bucket_name = FILE_NAME + '_bucket_1'
    bucket_name = bucket_name.replace('_','-')
    rc, stdout = s3_common.add_bucket(bucket_name, certificate_id, exe_node_ip=None)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)
    rc, stdout = s3_common.check_bucket(bucket_name, certificate_id, exe_node_ip=None)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "check bucket %s failed!!!" % bucket_name)

    if os.path.exists(filepath):
        cmd = "rm -rf %s" % filepath
        log.info(cmd)
        shell.sh(cmd)
    rc, stdout = s3_common.create_file_m(filepath, 1, exe_node_ip=None)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create_file_m fail!!!")
    rc, before_md5 = s3_common.get_file_md5(filepath)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "get file:%s md5 fail" % filepath)

    log.info("5> 上传对象")
    for i in range(object_num):
        i += 1
        object_name = bucket_name + '_obj_%d' % i
        rc, stdout = s3_common.add_object(bucket_name, object_name, filepath,
                                          certificate_id, exe_node_ip=None)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "add_object %s fail!!!" % object_name)

    rc, object_name_lst = s3_common.get_all_object_in_bucket(bucket_name, certificate_id,
                                                             exe_node_ip=None, retry=False)

    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "get_all_object_in_bucket: %s  fail!!!" % bucket_name)

    log.info("6> 随机选择一个节点杀其oOms进程，此过程执行5次")
    for i in range(5):
        i += 1
        obj_node = common.Node()
        ooms_node_lst = s3_common.get_ooms_node_ids()
        num = random.randint(0, len(ooms_node_lst)-1)
        killoomsid = ooms_node_lst[num]
        killoomsip = obj_node.get_node_ip_by_id(killoomsid)
        log.info('第%s次时，杀节点%s的oOms进程' % (i, killoomsip))
        after_kill_recovery_process(killoomsip, service_type, othername)
        log.info('第%s次执行杀节点%s的oOms进程，完成' % (i, killoomsip))

    log.info("7> oOms进程恢复后下载对象")
    get_many_obj(bucket_name, object_name_lst, getpath, certificate_id)

    log.info("8> 对象下载完成后，校验md5值")
    for object_name in object_name_lst:
        rc, stdout, stderr = shell.sh('ls -l ' + getpath + '/' + object_name, raise_exception=True, timeout=None)
        objsize = stdout.split()[4]
        if int(objsize) <= 100:
            pass
        else:
            rc, after_md5 = s3_common.get_file_md5(getpath + '/' + object_name)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "get file %s md5 fail!!!" % (getpath + '/' + object_name))
            if after_md5 != before_md5:
                judge_result(rc, FILE_NAME)
                common.judge_rc(-1, 0, 'the object:%s  md5 has changed' % object_name)

    result.result(FILE_NAME, 0)
    log.info('%s success!' % FILE_NAME)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s finish!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

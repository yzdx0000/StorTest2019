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
#    上传对象过程中，随机选择一个杀一个节点的oOms进程
# @steps:
#    1、创建账户；
#    2、检查账户创建成功
#    3、创建证书；
#    4、上传桶
#    5、上传对象过程中，随机选择一个杀一个节点的oOms进程
#    6、清理环境
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
current_path = os.path.abspath('')
current_uppath = os.path.dirname(current_path)
S3outputpath = os.path.join(current_uppath, 'S3output')
filepath = os.path.join(S3outputpath, FILE_NAME)

ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, -1)


def for_kill_process(node_ip, service_type, othername):
    time.sleep(2)
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
                log.info('the %s process of node %s is killed' % (service_type, node_ip))
                break
            else:
                time.sleep(2)


def put_obj_manycount(count, bucket_name, filepath, certificate_id):
    for j in range(count):
        j += 1
        object_name = bucket_name + '_obj_%d' % j
        rc, stdout = s3_common.add_object(bucket_name, object_name, filepath, certificate_id,
                                          exe_node_ip=None, retry=True)
        judge_result(rc, FILE_NAME)
        common.judge_rc(rc, 0, "add_object %s fail!!!" % object_name)
        time.sleep(1)


def case():
    othername = '.bak'
    object_num = 200
    service_type = 'oOms'

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

    rc, stdout = s3_common.create_file_m(filepath, 1, exe_node_ip=None)
    judge_result(rc, FILE_NAME)
    common.judge_rc(rc, 0, "create_file_m fail!!!")

    log.info("5> 随机选择一个节点，杀%s进程,不恢复" % service_type)
    obj_node = common.Node()
    ooms_node_lst = s3_common.get_ooms_node_ids()
    num = random.randint(0, len(ooms_node_lst)-1)
    killoomsid = ooms_node_lst[num]
    killoomsip = obj_node.get_node_ip_by_id(killoomsid)
    log.info('此次选择杀节点%s的%s进程' % (killoomsip, service_type))

    log.info("6> 杀节点%s的%s进程过程中，上传对象" % (killoomsip, service_type))
    p1 = Process(target=put_obj_manycount, args=(object_num, bucket_name, filepath, certificate_id,))
    p2 = Process(target=for_kill_process, args=(killoomsip, service_type, othername))
    p1.daemon = True
    p2.daemon = True
    p1.start()
    p2.start()

    p1.join()
    p2.terminate()
    p2.join()

    proc_name = ''
    if service_type == 'oOss':
        proc_name = '/home/parastor/oss/oOss'
    elif service_type == 'oOms':
        proc_name = '/home/parastor/oms/oOms'
    cmd = 'mv ' + proc_name + othername + ' ' + proc_name
    log.info(cmd)
    shell.ssh(killoomsip, cmd)
    time.sleep(60)
    if p1.exitcode == 0:
        result.result(FILE_NAME, 0)
        log.info('%s success!' % FILE_NAME)
    else:
        pass


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s finish!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)















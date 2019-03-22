# -*-coding:utf-8 -*

import os
import time

import utils_path
import common
import quota_common
import log

##########################################
#
# Author: baorb
# date 2017-08-21
# @summary：
#    配额功能:多客户端容量满了之后追加写
# @steps:
#    1、存储集群配额功能打开；
#    2、创建目录逻辑容量配额，容量硬阈值2G；
#    3、单客户端创建1个3G大文件；
#    4、第二个客户端对这个文件追加10M；
#    5、第二个客户端删除这个大文件；
#    6、第二个客户端重新创建2个1G文件；
# @changelog：
##########################################


def case():
    '''打开配额功能'''
    quota_common.open_quota_global_switch()

    '''创建目录，设置配额规则'''
    quota_common.creating_dir(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    quota_dir = os.path.basename(quota_common.QUOTA_PATH)
    rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                     logical_quota_cal_type='QUOTA_LIMIT',
                                                     logical_hard_threshold=2147483648)
    common.judge_rc(rc, 0, "create  quota failed")

    '''创建3g文件'''
    cmd = 'dd if=/dev/zero of=%s/file_1 bs=1M count=3000' % quota_common.QUOTA_PATH
    common.run_command(quota_common.CLIENT_IP_1, cmd)
    log.info("wait 10s")
    time.sleep(10)
    '''检查文件大小'''
    cmd = 'du %s/file_1 -b' % quota_common.QUOTA_PATH
    rc, stdout = common.run_command(quota_common.CLIENT_IP_2, cmd)
    if rc != 0:
        log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))

    if '2147483648' != stdout.split()[0]:
        log.error('file size is not logical_hard_threshold!!!')
        raise Exception('file size is not logical_hard_threshold!!!')

    '''通过get_quota检查配额数额'''
    rc, result = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    quotas_info = result['result']['quotas']
    for quota_info in quotas_info:
        if quota_info['path'] == '%s:/%s' % (quota_common.VOLUME_NAME, quota_dir):
            if 2147483648 != quota_info['logical_used_capacity']:
                log.error('get_quota logical_used_capacity is error!!!')
                raise Exception('get_quota logical_used_capacity is error!!!')

    '''追加写'''
    cmd = 'dd if=/dev/zero of=%s/file_1 bs=1M seek=2048 count=10' % quota_common.QUOTA_PATH
    common.run_command(quota_common.CLIENT_IP_2, cmd)
    log.info("wait 10s")
    time.sleep(10)
    '''检查文件大小'''
    cmd = 'du %s/file_1 -b' % quota_common.QUOTA_PATH
    rc, stdout = common.run_command(quota_common.CLIENT_IP_2, cmd)
    if rc != 0:
        log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))

    if '2147483648' != stdout.split()[0]:
        log.error('file size is not logical_hard_threshold!!!')
        raise Exception('file size is not logical_hard_threshold!!!')
    log.info("wait 5s")
    time.sleep(5)
    '''删除文件'''
    common.rm_exe(quota_common.CLIENT_IP_2, os.path.join(quota_common.QUOTA_PATH, 'file_1'))

    log.info("wait 15s")
    time.sleep(15)

    '''通过get_quota检查配额数额'''
    rc, result = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    quotas_info = result['result']['quotas']
    for quota_info in quotas_info:
        if quota_info['path'] == '%s:/%s' % (quota_common.VOLUME_NAME, quota_dir):
            if 0 != quota_info['logical_used_capacity']:
                log.error('get_quota logical_used_capacity is error!!!')
                raise Exception('get_quota logical_used_capacity is error!!!')

    '''创建两个1g文件'''
    cmd1 = 'dd if=/dev/zero of=%s/file_1 bs=1M count=1024' % quota_common.QUOTA_PATH
    cmd2 = 'dd if=/dev/zero of=%s/file_2 bs=1M count=1024' % quota_common.QUOTA_PATH
    rc, stdout = common.run_command(quota_common.CLIENT_IP_2, cmd1)
    if rc != 0:
        log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd1, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd1, stdout))
    rc, stdout = common.run_command(quota_common.CLIENT_IP_2, cmd2)
    if rc != 0:
        log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd2, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd2, stdout))

    log.info("wait 10s")
    time.sleep(10)

    '''检查文件大小'''
    cmd1 = 'du %s/file_1 -b' % quota_common.QUOTA_PATH
    cmd2 = 'du %s/file_2 -b' % quota_common.QUOTA_PATH
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd1)
    if rc != 0:
        log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd1, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd1, stdout))
    if '1073741824' != stdout.split()[0]:
        log.error('file size is not logical_hard_threshold!!!')
        raise Exception('file size is not logical_hard_threshold!!!')

    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd2)
    if rc != 0:
        log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd2, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd2, stdout))
    if '1073741824' != stdout.split()[0]:
        log.error('file size is not logical_hard_threshold!!!')
        raise Exception('file size is not logical_hard_threshold!!!')

    log.info("wait 10s")
    time.sleep(10)
    '''通过get_quota检查配额数额'''
    rc, result = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    quotas_info = result['result']['quotas']
    for quota_info in quotas_info:
        if quota_info['path'] == '%s:/%s' % (quota_common.VOLUME_NAME, quota_dir):
            if 2147483648 != quota_info['logical_used_capacity']:
                log.error('get_quota logical_used_capacity is error!!!')
                raise Exception('get_quota logical_used_capacity is error!!!')
    return


def main():
    file_name = os.path.basename(__file__)
    file_name = os.path.splitext(file_name)[0]
    log_file_path = log.get_log_path(file_name)
    stream = log.init(log_file_path, True)
    quota_common.cleaning_environment()
    case()
    quota_common.cleaning_environment()
    return


if __name__ == '__main__':
    common.case_main(main)

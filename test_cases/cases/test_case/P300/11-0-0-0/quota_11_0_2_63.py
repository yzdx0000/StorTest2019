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
#    配额功能:文件数满了之后追加写
# @steps:
#    1、存储集群配额功能打开；
#    2、创建目录配额，个数硬阈值3000；
#    3、单客户端创建3000个空文件；
#    4、同一个客户端对某个文件追加10M；
#    5、同一个客户端删除100个空文件；
#    6、同一个客户端重新创建100个1M大小文件；
# @changelog：
##########################################


def case():
    '''打开配额功能'''
    quota_common.open_quota_global_switch()

    '''创建目录，配置配额规则'''
    quota_common.creating_dir(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    quota_dir = os.path.basename(quota_common.QUOTA_PATH)
    rc, result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                               filenr_quota_cal_type='QUOTA_LIMIT',
                                               filenr_hard_threshold=3000)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    if result['err_no'] != 0:
        log.error('create_quota failed!!!')
        raise Exception('create_quota failed!!!')

    '''创建3000个空文件'''
    for i in range(3000):
        cmd = 'dd if=/dev/zero of=%s/file_%d bs=1M count=0' % (quota_common.QUOTA_PATH, i)
        rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
        if rc != 0:
            log.error('create_quota failed!!!')
            raise Exception('create_quota failed!!!')

    time.sleep(30)

    '''通过get_quota检查配额数额'''
    rc, result = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    quotas_info = result['result']['quotas']
    for quota_info in quotas_info:
        if quota_info['path'] == '%s:/%s' % (quota_common.VOLUME_NAME, quota_dir):
            if 3000 != quota_info['filenr_used_nr']:
                log.error('get_quota filenr_used_nr is error!!!')
                raise Exception('get_quota filenr_used_nr is error!!!')

    '''追加一个文件到10M'''
    cmd = 'dd if=/dev/zero of=%s/file_0 bs=1M count=10' % quota_common.QUOTA_PATH
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.error("Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))

    time.sleep(60)

    '''通过get_quota检查配额数额'''
    rc, result = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    quotas_info = result['result']['quotas']
    for quota_info in quotas_info:
        if quota_info['path'] == '%s:/%s' % (quota_common.VOLUME_NAME, quota_dir):
            if 10485760 != quota_info['logical_used_capacity']:
                log.error('get_quota logical_used_capacity is %s, not 10485760!!!'
                          % quota_info['logical_used_capacity'])
                raise Exception('get_quota logical_used_capacity is %s, not 10485760!!!'
                                % quota_info['logical_used_capacity'])

    '''删除100个文件'''
    for i in range(1, 101):
        common.rm_exe(quota_common.CLIENT_IP_1, os.path.join(quota_common.QUOTA_PATH, 'file_%d' % i))

    time.sleep(60)

    '''通过get_quota检查配额数额'''
    rc, result = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    quotas_info = result['result']['quotas']
    for quota_info in quotas_info:
        if quota_info['path'] == '%s:/%s' % (quota_common.VOLUME_NAME, quota_dir):
            if 2900 != quota_info['filenr_used_nr']:
                log.error('get_quota filenr_used_nr is %s, not 2900!!!' % quota_info['filenr_used_nr'])
                raise Exception('get_quota filenr_used_nr is %s, not 2900!!!' % quota_info['filenr_used_nr'])

    '''创建100个1m文件'''
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH, 100, 1, "a")

    time.sleep(60)

    '''通过get_quota检查配额数额'''
    rc, result = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    quotas_info = result['result']['quotas']
    for quota_info in quotas_info:
        if quota_info['path'] == '%s:/%s' % (quota_common.VOLUME_NAME, quota_dir):
            if 3000 != quota_info['filenr_used_nr']:
                log.error('get_quota filenr_used_nr is %s, not 3000!!!' % quota_info['filenr_used_nr'])
                raise Exception('get_quota filenr_used_nr is %s, not 3000!!!' % quota_info['filenr_used_nr'])

    '''通过get_quota检查配额数额'''
    rc, result = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    quotas_info = result['result']['quotas']
    for quota_info in quotas_info:
        if quota_info['path'] == '%s:/%s' % (quota_common.VOLUME_NAME, quota_dir):
            if 115343360 != quota_info['logical_used_capacity']:
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

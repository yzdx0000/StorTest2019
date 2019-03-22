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
#    配额功能关闭情况下的配额配置、修改、删除。
# @steps:
#    1、存储集群关闭配额功能；
#    2、配置20个目录配额，limit限制个数3000，容量2g；
#    3、每个目录创建3000个1M小文件（单客户端）；
#    4、修改这20个目录配额，limit限制个数5000，容量5g:
#    5、每个目录增加2000个1M小文件；
#    6、删除这20个目录配额；
# @changelog：
##########################################


def case():
    '''关闭配额'''
    quota_common.close_quota_global_switch()

    '''配置20个目录配额，limit限制个数3000，容量2g'''
    quota_dir_lst = []
    for i in range(100):
        dir_path = quota_common.BASE_QUOTA_PATH + '/quota_test_dir%d' % i
        quota_dir = 'quota_test_dir%d' % i
        quota_common.creating_dir(quota_common.CLIENT_IP_1, dir_path)
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_hard_threshold=3000,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_hard_threshold=2147483648)
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)
        if check_result['err_no'] != 0:
            log.error('create_quota failed!!!')
            raise Exception('create_quota failed!!!')
        quota_dir_lst.append(dir_path)

    '''每个创建3000个1M文件'''
    for dir_path in quota_dir_lst:
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir_path, 3000, 1, "a")
        '''检查文件个数'''
        cmd = 'ls -l %s |grep "^-"|wc -l' % dir_path
        rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
        if rc != 0:
            log.error("Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
        if '3000' != stdout.strip():
            log.error('there is not 3000 files!!!')
            raise Exception('there is not 3000 files!!!')

    time.sleep(10)

    '''修改配额规则'''
    quota_id_list = quota_common.get_quota_id_list()
    for quota_id in quota_id_list:
        rc, check_result = quota_common.update_one_quota(id=quota_id,
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_hard_threshold=5000,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_hard_threshold=5368709120)
        common.judge_rc(rc, 0, "update quota failed", exit_flag=False)
        if check_result['err_no'] != 0:
            log.error('update_quota failed!!!')
            raise Exception('update_quota failed!!!')

    '''每个目录追加2000个1M文件'''
    for quota_dir in quota_dir_lst:
        quota_common.creating_files(quota_common.CLIENT_IP_1, quota_dir, 2000, 1, "b")
        '''检查文件个数'''
        cmd = 'ls -l %s |grep "^-"|wc -l' % quota_dir
        rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
        if rc != 0:
            log.error("Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
        if '5000' != stdout.strip():
            log.error('there is not 5000 files!!!')
            raise Exception('there is not 5000 files!!!')
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
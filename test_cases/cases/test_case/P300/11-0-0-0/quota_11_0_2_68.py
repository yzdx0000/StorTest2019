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
#    配额功能:3个客户端，同时写入300个目录，每个客户端每个目录写入部分数据
# @steps:
#    1、创建300个目录配额，文件阈值10000，硬阈值100G；
#    2、3个客户端分别300个目录创建n个1m文件（n=quotaid）；
# @changelog：
##########################################


def case():
    '''打开配额功能'''
    quota_common.open_quota_global_switch()

    '''存储集群创建300个目录配额，逻辑容量硬阈值限制100G'''
    quota_dir_lst = []
    for i in range(300):
        dir_path = quota_common.BASE_QUOTA_PATH + '/quota_test_dir%d' % i
        quota_dir = 'quota_test_dir%d' % i
        quota_common.creating_dir(quota_common.CLIENT_IP_1, dir_path)
        rc, check_result = quota_common.create_one_quota(path=("%s:/%s" % (quota_common.VOLUME_NAME, quota_dir)),
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_hard_threshold=10000,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_hard_threshold=107374182400)
        common.judge_rc(rc, 0, "create quota failed")
        if check_result['err_no'] != 0:
            log.error('create_quota failed!!!')
            raise Exception('create_quota failed!!!')
        quota_dir_lst.append(dir_path)

    '''3个客户端分别300个目录创建n个1m文件'''
    for quota_dir in quota_dir_lst:
        num = quota_dir_lst.index(quota_dir) + 1
        quota_common.creating_files(quota_common.CLIENT_IP_1, quota_dir, num, 1, "a")
        quota_common.creating_files(quota_common.CLIENT_IP_2, quota_dir, num, 1, "b")
        quota_common.creating_files(quota_common.CLIENT_IP_3, quota_dir, num, 1, "c")

    time.sleep(30)

    '''通过get_quota检查配额数额'''
    for dir_path in quota_dir_lst:
        num = quota_dir_lst.index(dir_path) + 1
        quota_dir = os.path.basename(dir_path)
        rc, result = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        quotas_info = result['result']['quotas']
        for quota_info in quotas_info:
            if quota_info['path'] == '%s:/%s' % (quota_common.VOLUME_NAME, quota_dir):
                if 1024 * 1024 * num * 3 != quota_info['logical_used_capacity']:
                    log.error('path is %s, file_size is %d, logical_used_capacity is %d' %
                              (quota_info['path'], 1024 * 1024 * num, quota_info['logical_used_capacity']))
                    raise Exception('path is %s, file_size is %d, logical_used_capacity is %d' %
                                    (quota_info['path'], 1024 * 1024 * num, quota_info['logical_used_capacity']))
                if num * 3 != quota_info['filenr_used_nr']:
                    log.error('path is %s, file_size is %d, filenr_used_nr is %d' %
                              (quota_info['path'], 1024 * 1024 * num, quota_info['filenr_used_nr']))
                    raise Exception('path is %s, file_size is %d, filenr_used_nr is %d' %
                                    (quota_info['path'], 1024 * 1024 * num, quota_info['filenr_used_nr']))
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
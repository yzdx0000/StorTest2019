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
#    配额功能:配额策略目录下文件循环创建删除操作
# @steps:
#    1、创建目录配额，所有阈值不限制；
#    2、创建10000个目录/64k文件，get_quota查看统计值；
#    3、删除10000个目录/64k文件，get_quota查看统计值；
#    4、循环2-3步5次，删除所有文件，get_quota查看统计值；
#
# @changelog：
##########################################

NUM = 500


def case():
    '''打开配额功能'''
    quota_common.open_quota_global_switch()

    '''创建目录，设置配额规则'''
    quota_common.creating_dir(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                               logical_quota_cal_type='QUOTA_COMPUTE',
                                               physical_quota_cal_type='QUOTA_COMPUTE',
                                               filenr_quota_cal_type='QUOTA_COMPUTE')
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)
    if result['err_no'] != 0:
        log.error('create_quota failed!!!')
        raise Exception('create_quota failed!!!')

    for i in range(5):
        '''创建10000个目录'''
        for j in range(NUM):
            cmd = 'mkdir %s/quota_dir_%d' % (quota_common.QUOTA_PATH, j)
            rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
            if rc != 0:
                log.error("Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
                raise Exception(
                    "Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))

        '''创建10000个文件'''
        quota_common.creating_1k_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH, NUM, 64, 'a')

        time.sleep(30)

        '''通过get_quota检查配额数额'''
        rc, result = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        quotas_info = result['result']['quotas']
        for quota_info in quotas_info:
            if quota_info['path'] == '%s:/%s' % (quota_common.VOLUME_NAME, quota_dir):
                if NUM*2 != quota_info['filenr_used_nr']:
                    log.error('path is %s, file_size is %d, filenr_used_nr is %d' %
                              (quota_info['path'], NUM*2, quota_info['filenr_used_nr']))
                    raise Exception('path is %s, file_size is %d, filenr_used_nr is %d' %
                                    (quota_info['path'], NUM*2, quota_info['filenr_used_nr']))

        '''删除目录和文件'''
        common.rm_exe(quota_common.CLIENT_IP_1, os.path.join(quota_common.QUOTA_PATH, '*'))

        time.sleep(30)

        '''通过get_quota检查配额数额'''
        rc, result = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        quotas_info = result['result']['quotas']
        for quota_info in quotas_info:
            if quota_info['path'] == '%s:/%s' % (quota_common.VOLUME_NAME, quota_dir):
                if 0 != quota_info['filenr_used_nr']:
                    log.error('path is %s, file_size is %d, filenr_used_nr is %d' %
                              (quota_info['path'], 0, quota_info['filenr_used_nr']))
                    raise Exception('path is %s, file_size is %d, filenr_used_nr is %d' %
                                    (quota_info['path'], 0, quota_info['filenr_used_nr']))
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
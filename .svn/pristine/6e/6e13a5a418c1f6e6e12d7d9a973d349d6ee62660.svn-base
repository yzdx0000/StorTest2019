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
#    配额功能:500个目录，500个用户
# @steps:
#    1、存储集群创建500个目录配额，逻辑容量硬阈值限制10G；
#    2、每个目录创建n个1m文件（n=quotaid），观察统计结果；
# @changelog：
##########################################


def case():
    '''打开配额功能'''
    quota_common.open_quota_global_switch()
    quota_common.preparing_zone_nas()
    auth_provider_id = quota_common.get_auth_provider_id_with_access_zone_name(quota_common.QUOTA_ACCESS_ZONE)

    '''创建用户组和用户'''
    quota_info_lst = []
    for i in range(500):
        quota_info = []
        '''创建用户组'''
        quota_group_name = 'quota_group_%d' % (i)
        quota_info.append(quota_group_name)
        quota_common.create_designated_quota_group(quota_group_name, auth_provider_id)

        '''创建用户'''
        quota_user_name = 'quota_user_%d' % (i)
        quota_info.append(quota_user_name)

        quota_common.create_designated_quota_user(quota_user_name, quota_group_name, auth_provider_id)

        '''创建目录'''
        dir_path = quota_common.BASE_QUOTA_PATH + '/quota_test_dir%d' % i
        quota_info.append(dir_path)
        quota_dir = 'quota_test_dir%d' % i
        quota_common.creating_dir(quota_common.CLIENT_IP_1, dir_path)

        '''创建配额规则'''
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                         auth_provider_id=auth_provider_id,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_hard_threshold=10737418240,
                                                         user_type='USERTYPE_USER',
                                                         user_or_group_name=quota_user_name)
        common.judge_rc(rc, 0, "create quota failed", exit_flag=False)
        if check_result['err_no'] != 0:
            log.error('create_quota failed!!!')
            raise Exception('create_quota failed!!!')
        quota_info_lst.append(quota_info)

    # 防止刚创建的用户不能su 所以添加sleep40秒
    time.sleep(40)

    '''创建n个1m文件'''
    for quota_info in quota_info_lst:
        num = quota_info_lst.index(quota_info) + 1
        quota_user_name = quota_info[1]
        dir_path = quota_info[2]
        for i in range(1, num + 1):
            cmd = ('su %s -c "dd if=/dev/zero of=%s/file_a_%d bs=1M count=%s"') \
                  % (quota_user_name, dir_path, i, 1)
            rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
            if 0 != rc:
                log.error("Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
                raise Exception(
                    "Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))

    time.sleep(30)

    '''通过get_quota检查配额数额'''
    for quota_info in quota_info_lst:
        num = quota_info_lst.index(quota_info) + 1
        quota_user_name = quota_info[1]
        dir_path = quota_info[2]
        quota_dir = os.path.basename(dir_path)
        rc, result = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        quotas_info = result['result']['quotas']
        for quota_info in quotas_info:
            if quota_info['path'] == '%s:/%s' % (quota_common.VOLUME_NAME, quota_dir):
                if 1024*1024*num != quota_info['logical_used_capacity']:
                    log.error('path is %s, file_size is %d, logical_used_capacity is %d' %
                              (quota_info['path'], 1024*1024*num, quota_info['logical_used_capacity']))
                    raise Exception('path is %s, file_size is %d, logical_used_capacity is %d' %
                                    (quota_info['path'], 1024*1024*num, quota_info['logical_used_capacity']))
    '''删除用户和组'''
    '''
    for quota_info in quota_info_lst:
        quota_common.delete_designated_quota_user(quota_info[1])
        quota_common.delete_designated_quota_group(quota_info[0])
    '''
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
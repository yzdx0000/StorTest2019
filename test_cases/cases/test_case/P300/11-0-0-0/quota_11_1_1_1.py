# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-1-1-1 【性能】配额规则下发效率（百,千,万,十万）
#######################################################

import os
import time

import utils_path
import common
import quota_common
import log
import prepare_clean

auth_provider_id_global = 1
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
def create_quota(count):
    for i in range(1, count + 1):
        '''
        # 创建用户和用户组
        group_name = "quota_group_%s" % i
        user_name = "quota_user_%s" % i
        quota_common.create_quota_group(quota_common.NOTE_IP_1, group_name)
        quota_common.create_quota_user(quota_common.NOTE_IP_1, user_name, group_name)
        '''

        # 创建目录
        dir = "%s%s" % (quota_common.QUOTA_PATH, i)
        quota_common.creating_dir(quota_common.CLIENT_IP_1, dir)
    '''
    # 把创建的用户和用户组拷贝到其他节点
    quota_common.scp_passwd_and_group_to_all_other_nodes(quota_common.NOTE_IP_1)
    '''

    starttime = time.time()
    for i in range(1, count + 1):
        # 创建配额
        dir = "%s%s" % (quota_common.QUOTA_PATH, i)
        quota_dir = os.path.basename(dir)
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_hard_threshold=500,
                                                         filenr_soft_threshold=100,
                                                         filenr_grace_time=1,
                                                         filenr_suggest_threshold=10,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_hard_threshold=81920,
                                                         logical_soft_threshold=16384,
                                                         logical_grace_time=1,
                                                         logical_suggest_threshold=4096)
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                         auth_provider_id=auth_provider_id_global,
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_hard_threshold=500,
                                                         filenr_soft_threshold=100,
                                                         filenr_grace_time=1,
                                                         filenr_suggest_threshold=10,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_hard_threshold=81920,
                                                         logical_soft_threshold=16384,
                                                         logical_grace_time=1,
                                                         logical_suggest_threshold=4096,
                                                         user_type='USERTYPE_USER',
                                                         user_or_group_name=quota_common.QUOTA_USER)
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                         auth_provider_id=auth_provider_id_global,
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_hard_threshold=500,
                                                         filenr_soft_threshold=100,
                                                         filenr_grace_time=1,
                                                         filenr_suggest_threshold=10,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_hard_threshold=81920,
                                                         logical_soft_threshold=16384,
                                                         logical_grace_time=1,
                                                         logical_suggest_threshold=4096,
                                                         user_type='USERTYPE_GROUP',
                                                         user_or_group_name=quota_common.QUOTA_GROUP)
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)
    endtime = time.time()

    log.info("endtime - starttime = %s" % (endtime - starttime))

    # 查询配额下发个数
    rc, check_result2 = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    quota_count = check_result2["result"]["total"]
    log.info("quota_count = %s" % quota_count)

    # 结果检查
    if quota_count != count * 3:
        raise Exception("11-1-1-1 Failed")
    else:
        log.info("11-1-1-1 Succeed")

    quota_common.delete_all_quota_config()
    quota_common.delete_all_files_and_dir(quota_common.CLIENT_IP_1, quota_common.BASE_QUOTA_PATH)
    return endtime - starttime


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    log.info("（2）executing_case")

    '''
    1、测试执行
    2、结果检查
    '''
    # 底层分别下发1百条、1千条、1万条和10万条配额规则，统计用时
    '''
    ISOTIMEFORMAT = '%Y-%m-%d %X'
    print time.strftime(ISOTIMEFORMAT, time.gmtime(time.time()))
    time.sleep(5)
    print time.strftime(ISOTIMEFORMAT, time.gmtime(time.time()))

    starttime = datetime.datetime.now()
    print starttime
    time.sleep(5)
    endtime = datetime.datetime.now()
    print (endtime - starttime).seconds
    '''

    # 计算不同个数配额的下发效率
    time_99 = create_quota(33)
    log.info("time_99 = %s" % time_99)      # 虚拟机约650s
    log.info("time_99_average = %s" % (time_99 / 99))

    time_999 = create_quota(333)
    log.info("time_999 = %s" % time_999)
    log.info("time_999_average = %s" % (time_999 / 999))
    '''
    time_9999 = create_quota(3333)
    log.info("time_9999 = %s" % time_9999)
    log.info("time_9999_average = %s" % (time_9999 / 9999))

    time_99999 = create_quota(33333)
    print "time_99999 = %s" % (time_99999)
    print "time_99999_average = %s" % (time_99999 / 99999)
    '''

    '''
    svn53967上测试结果：
    time_99 = 66.5231149197
    time_99_average = 0.671950655754
    time_999 = 686.97905302
    time_999_average = 0.68766671974
    time_9999 = 6808.31826591
    time_9999_average = 0.680899916583
    '''
    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    log.info("（1）preparing_environment")

    '''
    1、下发配额相关的配置
    2、创建配额测试相关的目录和文件
    '''
    global auth_provider_id_global
    quota_common.preparing_zone_nas()
    auth_provider_id = quota_common.get_auth_provider_id_with_access_zone_name(quota_common.QUOTA_ACCESS_ZONE)
    # 创建用户和用户组
    quota_common.create_designated_quota_user_and_group_new(quota_common.NOTE_IP_1, auth_provider_id)
    auth_provider_id_global = auth_provider_id

    # 下面是之前的方式，上面是当前修改，修改时间：20181107
    '''
    # 创建用户和用户组
    quota_common.create_designated_quota_user_and_group_old(quota_common.NOTE_IP_1)

    # 把创建的用户和用户组拷贝到其他节点
    quota_common.scp_passwd_and_group_to_all_other_nodes(quota_common.NOTE_IP_1)
    '''
    return


#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def quota_main():
    prepare_clean.test_prepare(FILE_NAME)
    quota_common.cleaning_environment()
    preparing_environment()
    executing_case()
    if quota_common.DEBUG != "on":
        quota_common.cleaning_environment()
    return


class Quota_Class_11_1_1_1():
    def quota_method_11_1_1_1(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
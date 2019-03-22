# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-2-1-1 【规则】能否下发10万条配额规则
#######################################################

import os

import utils_path
import common
import quota_common
import log
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    print "（2）executing_case"

    '''
    1、测试执行
    2、结果检查
    '''
    # 测试执行
    # 创建10万条同时含inode、用户和用户组的配额，用户和用户组名称各不相同
    count = 333
    success_count = 0

    quota_common.preparing_zone_nas()
    auth_provider_id = quota_common.get_auth_provider_id_with_access_zone_name(quota_common.QUOTA_ACCESS_ZONE)
    for i in range(1, count + 1):
        # 创建用户和用户组
        group_name = "quota_group_%s" % i
        user_name = "quota_user_%s" % i
        quota_common.create_designated_quota_group(group_name, auth_provider_id)
        quota_common.create_designated_quota_user(user_name, group_name, auth_provider_id)

    for i in range(1, count + 1):
        group_name = "quota_group_%s" % i
        user_name = "quota_user_%s" % i

        # 创建目录
        dir = "%s%s" % (quota_common.QUOTA_PATH, i)
        # print dir
        quota_common.creating_dir(quota_common.CLIENT_IP_1, dir)

        # 创建配额
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
        if check_result["detail_err_msg"] != "":
            success_count = success_count + 1

        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                         auth_provider_id=auth_provider_id,
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
                                                         user_or_group_name=user_name)
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)
        if check_result["detail_err_msg"] != "":
            success_count = success_count + 1

        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                         auth_provider_id=auth_provider_id,
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
                                                         user_or_group_name=group_name)
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)
        if check_result["detail_err_msg"] != "":
            success_count = success_count + 1

    # 结果检查
    print success_count
    if success_count != count * 3:
        raise Exception("11-2-1-1 Failed")
    else:
        log.info("11-2-1-1 Succeed")
    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    print "（1）preparing_environment"

    '''
    1、下发配额相关的配置
    2、创建配额测试相关的目录和文件
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


class Quota_Class_11_2_1_1():
    def quota_method_11_2_1_1(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
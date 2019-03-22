# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-32_supp 增删改查配额目录下的文件，配额规则不受影响
#######################################################

import os
import time

import utils_path
import common
import quota_common
import log


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
    auth_provider_id = quota_common.get_auth_provider_id_with_access_zone_name(quota_common.QUOTA_ACCESS_ZONE)
    # 针对quota_test_dir配置目录配额规则
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                      auth_provider_id=auth_provider_id,
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_hard_threshold=2000,
                                                      user_type='USERTYPE_USER',
                                                      user_or_group_name=quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    log.info("check_result1 = %s" % (check_result1))

    # 使用quota_user身份在quota_test_dir目录下touch一个文件a、mkdir一个目录dir
    cmd = ("cd %s; su %s -c \"touch a; mkdir dir\"") % (quota_common.QUOTA_PATH, quota_common.QUOTA_USER)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))

    time.sleep(10)
    # get_quota查看filenr_used_nr值是否正确
    rc, check_result2 = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    filenr_used_nr1 = check_result2["result"]["quotas"][0]["filenr_used_nr"]
    log.info("filenr_used_nr1 = %s" % filenr_used_nr1)

    # 移动文件a和目录dir到上一级目录
    cmd = ("cd %s; mv * ..") % (quota_common.QUOTA_PATH)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))

    time.sleep(10)
    # get_quota查看filenr_used_nr值是否正确
    rc, check_result3 = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    filenr_used_nr2 = check_result3["result"]["quotas"][0]["filenr_used_nr"]
    log.info("filenr_used_nr2 = %s" % filenr_used_nr2)

    # 结果检查
    if (check_result1["detail_err_msg"] != "" or
            filenr_used_nr1 != 2 or
            filenr_used_nr2 != 0):
        rc, check_result3 = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-2-32_supp Failed")
        raise Exception("11-0-2-32_supp Failed")
    else:
        log.info("11-0-2-32_supp Succeed")
    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    print "（1）preparing_environment"
    quota_common.preparing_zone_nas()
    auth_provider_id = quota_common.get_auth_provider_id_with_access_zone_name(quota_common.QUOTA_ACCESS_ZONE)
    # 创建用户和用户组
    quota_common.create_designated_quota_user_and_group_new(quota_common.NOTE_IP_1, auth_provider_id)

    '''
    1、下发配额相关的配置
    2、创建配额测试相关的目录和文件
    '''
    # 创建配额目录
    quota_common.creating_dir(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    return


#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def quota_main():
    file_name = os.path.basename(__file__)
    file_name = os.path.splitext(file_name)[0]
    log_file_path = log.get_log_path(file_name)
    stream = log.init(log_file_path, True)
    quota_common.cleaning_environment()
    preparing_environment()
    executing_case()
    if quota_common.DEBUG != "on":
        quota_common.cleaning_environment()
    return


class Quota_Class_11_0_2_32_supp():
    def quota_method_11_0_2_32_supp(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
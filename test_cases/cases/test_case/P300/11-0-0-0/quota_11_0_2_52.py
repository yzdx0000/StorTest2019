# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-52 修改目录用户配额规则，使规则参数不合法
#######################################################

import os

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
    # 创建一个目录用户配额规则【临时--filenr_grace_time=600，--logical_grace_time=600】
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                      auth_provider_id=auth_provider_id,
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_suggest_threshold=1000,
                                                      filenr_soft_threshold=2000,
                                                      filenr_grace_time=600,
                                                      filenr_hard_threshold=3000,
                                                      logical_quota_cal_type='QUOTA_LIMIT',
                                                      logical_suggest_threshold=1073741824,
                                                      logical_soft_threshold=2147483648,
                                                      logical_grace_time=600,
                                                      logical_hard_threshold=3221225472,
                                                      user_type='USERTYPE_USER',
                                                      user_or_group_name='quota_user')
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    log.info("check_result1 = %s" % (check_result1["detail_err_msg"]))

    # 验证配额功能，实际写入3000个文件
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                            3001, 1, "a", quota_common.QUOTA_USER)
    total_inodes = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                  quota_common.QUOTA_USER)
    log.info("total_inodes = %s" % (total_inodes))

    # 修改配额规则为
    rc, check_result = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    quota_id = check_result["result"]["quotas"][0]["id"]

    # 修改成不合法的配额规则
    rc, check_result2 = common.update_quota(id=quota_id,
                                            filenr_quota_cal_type='QUOTA_LIMIT',
                                            filenr_suggest_threshold=4000,
                                            filenr_soft_threshold=3000,
                                            filenr_grace_time=5,
                                            filenr_hard_threshold=2000,
                                            logical_quota_cal_type='QUOTA_LIMIT',
                                            logical_suggest_threshold=2147483648,
                                            logical_soft_threshold=3221225472,
                                            logical_grace_time=10,
                                            logical_hard_threshold=4294967296)
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)
    check_result2 = common.json_loads(check_result2)
    log.info("check_result2 = %s" % (check_result2["detail_err_msg"]))

    # 结果检查
    log.info("total_inodes = %s" % (total_inodes))
    if (check_result1["detail_err_msg"] != "" or
            check_result2["err_no"] == 0 or
            total_inodes != 3000):
        rc, check_result = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-2-52 Failed")
        raise Exception("11-0-2-52 Failed")
    else:
        log.info("11-0-2-52 Succeed")
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
    quota_common.preparing_zone_nas()
    auth_provider_id = quota_common.get_auth_provider_id_with_access_zone_name(quota_common.QUOTA_ACCESS_ZONE)
    # 创建用户和用户组
    quota_common.create_designated_quota_user_and_group_new(quota_common.NOTE_IP_1, auth_provider_id)

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


class Quota_Class_11_0_2_52():
    def quota_method_11_0_2_52(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
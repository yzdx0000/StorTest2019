# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-53 修改目录用户配额规则之改变配额类型
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
    # （1）配置目录用户配额类型为QUOTA_LIMIT
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, check_result1 = common.create_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                            auth_provider_id=auth_provider_id,
                                            filenr_quota_cal_type='QUOTA_LIMIT',
                                            filenr_hard_threshold=1000,
                                            user_type=quota_common.TYPE_USER,
                                            user_or_group_name='quota_user')
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)
    check_result1 = common.json_loads(check_result1)

    # 验证配额功能，实际写入1000个文件
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                            1001, 1, "a", quota_common.QUOTA_USER)
    total_inodes1 = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                   quota_common.QUOTA_USER)
    log.info("total_inodes1 = %s" % (total_inodes1))

    # 获取配额id
    rc, check_result = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    quota_id = check_result["result"]["quotas"][0]["id"]

    # （2）修改目录用户配额类型为QUOTA_COMPUTE
    rc, check_result2 = common.update_quota(id=quota_id,
                                            filenr_quota_cal_type='QUOTA_COMPUTE')
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)
    check_result2 = common.json_loads(check_result2)
    log.info("check_result2 = %s" % (check_result2["detail_err_msg"]))

    # 验证配额功能，COMPUTE模式可任意写入文件，此处再写入5000个文件
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                            5000, 1, "b", quota_common.QUOTA_USER)
    total_inodes2 = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                   quota_common.QUOTA_USER)
    log.info("total_inodes2 = %s" % (total_inodes2))

    # （3）改回目录用户配额类型为QUOTA_LIMIT
    rc, check_result3 = common.update_quota(id=quota_id,
                                            filenr_quota_cal_type='QUOTA_LIMIT',
                                            filenr_hard_threshold=2000)
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)
    check_result3 = common.json_loads(check_result3)
    log.info("check_result3 = %s" % (check_result3["detail_err_msg"]))

    # 验证配额功能，已达到配额，无法继续写入
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                            1, 1, "c", quota_common.QUOTA_USER)
    total_inodes3 = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                   quota_common.QUOTA_USER)
    log.info("total_inodes3 = %s" % (total_inodes3))

    # 结果检查
    if (check_result1["detail_err_msg"] != "" or
            total_inodes1 != 1000 or
            check_result2["detail_err_msg"] != "" or
            total_inodes2 != 6000 or
            check_result3["detail_err_msg"] != "" or
            total_inodes3 != 6000):
        rc, check_result = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-2-53 Failed")
        raise Exception("11-0-2-53 Failed")
    else:
        log.info("11-0-2-53 Succeed")
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


class Quota_Class_11_0_2_53():
    def quota_method_11_0_2_53(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
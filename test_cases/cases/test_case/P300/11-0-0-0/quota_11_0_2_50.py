# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-50 修改目录用户配额规则之改大、改小宽限天数
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
    # （1）配置目录用户配额规则软阈值为1G ，宽限天数为1天【临时：--logical_grace_time=60】
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                      auth_provider_id=auth_provider_id,
                                                      logical_quota_cal_type='QUOTA_LIMIT',
                                                      logical_soft_threshold=1073741824,
                                                      logical_grace_time=60,
                                                      user_type='USERTYPE_USER',
                                                      user_or_group_name='quota_user')
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    log.info("check_result1 = %s" % (check_result1["detail_err_msg"]))

    # 验证配额是否生效，预期成功写入1G个文件触发宽限时间启动
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                            1024, 1, "a", quota_common.QUOTA_USER)
    total_file_size1_1 = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                                    quota_common.QUOTA_USER)
    log.info("total_file_size1_1 = %s" % (total_file_size1_1))

    # 宽限期限内可任意写入文件
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                            100, 1, "b", quota_common.QUOTA_USER)
    total_file_size1_2 = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                                    quota_common.QUOTA_USER)
    log.info("total_file_size1_2 = %s" % (total_file_size1_2))
#    time.sleep(3600)
    time.sleep(70)

    # 宽限期限外不能再写入文件
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                            1, 1, "c", quota_common.QUOTA_USER)
    total_file_size1_3 = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                                    quota_common.QUOTA_USER)
    log.info("total_file_size1_3 = %s" % (total_file_size1_3))

    # 获取配额id
    rc, check_result = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    quota_id = check_result["result"]["quotas"][0]["id"]
    log.info("quota_id = %s" % (quota_id))

    # （2）1天之后，马上修改目录用户配额规则宽限天数为2天，验证配额是否生效【临时：--logical_grace_time=180】
    rc, check_result2 = quota_common.update_one_quota(id=quota_id,
                                                      logical_quota_cal_type='QUOTA_LIMIT',
                                                      logical_soft_threshold=1073741824,
                                                      logical_grace_time=180)
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)
    log.info("check_result2 = %s" % (check_result2["detail_err_msg"]))

    # 验证配额是否生效，预期又争取来2-1天的宽限时间（因为宽限时间是从配额超过1000开始触发的），宽限期限内可任意写入文件
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                            100, 1, "d", quota_common.QUOTA_USER)
    total_file_size2_1 = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                                    quota_common.QUOTA_USER)
    log.info("total_file_size2_1 = %s" % (total_file_size2_1))

    #    time.sleep(3600)
    time.sleep(70)

    # 宽限期限外不能再写入文件
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                            1, 1, "e", quota_common.QUOTA_USER)
    total_file_size2_2 = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                                    quota_common.QUOTA_USER)
    log.info("total_file_size2_2 = %s" % (total_file_size2_2))

    # (3)修改宽限天数为1天，删除配额目录用户中所有文件【临时：--logical_grace_time=60】
    rc, check_result3 = quota_common.update_one_quota(id=quota_id,
                                                      logical_quota_cal_type='QUOTA_LIMIT',
                                                      logical_soft_threshold=1073741824,
                                                      logical_grace_time=60)
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)
    log.info("check_result3 = %s" % (check_result3["detail_err_msg"]))

    # 删除目录内所有文件
    common.rm_exe(quota_common.CLIENT_IP_1, os.path.join(quota_common.QUOTA_PATH, '*'))

    # 预期成功写入1G文件触发宽限时间启动
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                            1024, 1, "f", quota_common.QUOTA_USER)
    total_file_size3_1 = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                                    quota_common.QUOTA_USER)
    log.info("total_file_size3_1 = %s" % (total_file_size3_1))

    # 宽限期限内可任意写入文件
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                            100, 1, "g", quota_common.QUOTA_USER)
    total_file_size3_2 = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                                    quota_common.QUOTA_USER)
    log.info("total_file_size3_2 = %s" % (total_file_size3_2))

    #    time.sleep(3600)
    time.sleep(70)

    # 宽限期限外不能再写入文件
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                            1, 1, "h", quota_common.QUOTA_USER)
    total_file_size3_3 = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                                    quota_common.QUOTA_USER)
    log.info("total_file_size3_3 = %s" % (total_file_size3_3))

    # 结果检查
    if (check_result1["detail_err_msg"] != "" or
            total_file_size1_1 != quota_common.FILE_SIZE_1G or
            total_file_size1_2 != quota_common.FILE_SIZE_1G + 1024*1024*100 or  #1178599442
            total_file_size1_3 != quota_common.FILE_SIZE_1G + 1024*1024*100 or
            check_result2["detail_err_msg"] != "" or
            total_file_size2_1 != quota_common.FILE_SIZE_1G + 1024*1024*200 or  #1283457024
            total_file_size2_2 != quota_common.FILE_SIZE_1G + 1024*1024*200 or
            check_result3["detail_err_msg"] != "" or
            total_file_size3_1 != quota_common.FILE_SIZE_1G or
            total_file_size3_2 != quota_common.FILE_SIZE_1G + 1024*1024*100or
            total_file_size3_3 != quota_common.FILE_SIZE_1G + 1024*1024*100):
        rc, check_result = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-2-50 Failed")
        raise Exception("11-0-2-50 Failed")
    else:
        log.info("11-0-2-50 Succeed")
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


class Quota_Class_11_0_2_50():
    def quota_method_11_0_2_50(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
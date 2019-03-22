# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-1-47 目录用户逻辑空间配额混合阈值，建议阈值先生
#         效，软阈值其次生效，限期内硬阈值也生效之chown方式
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
    # 【chown方式】
    # 写入3G文件后开始计时
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                1536, 1, "a")
    quota_common.creating_files(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                1536, 1, "b")

    # 修改这3G文件的属主为quota_user
    user_file_list = quota_common.get_file_list(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH, "a")
    quota_common.change_file_user(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                  user_file_list, quota_common.QUOTA_USER)
    user_file_list = quota_common.get_file_list(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH, "b")
    quota_common.change_file_user(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                  user_file_list, quota_common.QUOTA_USER)

    # 在1天以内再写入1G文件
    # （1）先写500M属主为root的文件，预期写入成功
    quota_common.creating_files(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                512, 1, "c")
    # （2）再写500M属主为quota_other_user的文件，预期写入成功
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                512, 1, "d")
    user_file_list = quota_common.get_file_list(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH, "d")
    quota_common.change_file_user(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                  user_file_list, quota_common.QUOTA_OTHER_USER)
    # （3）再写1G属主为quota_user的文件，预期写入成功
    quota_common.creating_files(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                1024, 1, "e")
    user_file_list = quota_common.get_file_list(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH, "e")
    quota_common.change_file_user(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                  user_file_list, quota_common.QUOTA_USER)

    # 写入1G文件后，再尝试继续写入文件
    # （1）先写500M属主为root的文件，预期写入成功
    quota_common.creating_files(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                512, 1, "f")
    # （2）再写500M属主为quota_other_user的文件，预期写入成功
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                512, 1, "g")
    user_file_list = quota_common.get_file_list(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH, "g")
    quota_common.change_file_user(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                  user_file_list, quota_common.QUOTA_OTHER_USER)
    # （3）再写500M属主为quota_user的文件，预期写入失败
    quota_common.creating_files(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                512, 1, "h")
    user_file_list = quota_common.get_file_list(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH, "h")
    quota_common.change_file_user(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                  user_file_list, quota_common.QUOTA_USER)

    # 检查配额是否生效
    total_file_size = quota_common.user_or_group_total_file_size(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                                 quota_common.QUOTA_USER)
    if total_file_size != quota_common.FILE_SIZE_4G:
        rc, check_result = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-1-47 Failed")
        raise Exception("11-0-1-47 Failed")
    else:
        log.info("11-0-1-47 Succeed")
    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    log.info("（1）preparing_environment")
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

    # 针对目录用户配置逻辑空间为4G硬阈值、3G软阈值（宽限天数为1天）、2G建议阈值的配额【临时：--logical_grace_time=60】
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                     auth_provider_id=auth_provider_id,
                                                     logical_quota_cal_type='QUOTA_LIMIT',
                                                     logical_suggest_threshold=2147483648,
                                                     logical_soft_threshold=3221225472,
                                                     logical_grace_time=600,
                                                     logical_hard_threshold=4294967296,
                                                     user_type='USERTYPE_USER',
                                                     user_or_group_name='quota_user')
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)
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


class Quota_Class_11_0_1_47():
    def quota_method_11_0_1_47(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
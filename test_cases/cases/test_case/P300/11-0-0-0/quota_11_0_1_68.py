# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-1-68 目录用户组inode数配额混合阈值，建议阈值先生
#         效，软阈值其次生效，限期内硬阈值也生效之chgrp方式
#######################################################

import os

import utils_path
import common
import quota_common
import log

soft_val = 0
soft_val_2 = 0
if quota_common.flag_slow_machine is True:
    soft_val = 10
    soft_val_2 = 1000
else:
    soft_val = 100
    soft_val_2 = 1000


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

    # 【chgrp方式】
    # 针对该目录用户组写入3000文件后开始计时
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                3000, 1, "a")

    # 修改这3000个文件的属组为quota_group
    group_file_list = quota_common.get_file_list(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH, "a")
    quota_common.change_file_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                   group_file_list, quota_common.QUOTA_GROUP)

    # 在1天以内再写入1000个文件
    # （1）先写100个属组为root的文件，预期写入成功
    quota_common.creating_files(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                soft_val, 1, "b")
    # （2）再写100个属组为quota_other_group的文件，预期写入成功
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                soft_val, 1, "c")
    group_file_list = quota_common.get_file_list(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH, "c")
    quota_common.change_file_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                   group_file_list, quota_common.QUOTA_OTHER_GROUP)
    # （3）再写1000个属组为quota_group的文件，预期写入成功
    quota_common.creating_files(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                soft_val_2, 1, "d")
    group_file_list = quota_common.get_file_list(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH, "d")
    quota_common.change_file_group(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                   group_file_list, quota_common.QUOTA_GROUP)

    # 写入1000个文件后，再尝试继续写入文件
    # （1）先写100个属组为root的文件，预期写入成功
    quota_common.creating_files(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                soft_val, 1, "e")
    # （2）再写100个属组为quota_other_group的文件，预期写入成功
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                soft_val, 1, "f")
    group_file_list = quota_common.get_file_list(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH, "f")
    quota_common.change_file_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                   group_file_list, quota_common.QUOTA_OTHER_GROUP)
    # （3）最后尝试写100个属组为quota_group的文件，预期写入失败
    quota_common.creating_files(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                soft_val, 1, "g")
    group_file_list = quota_common.get_file_list(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH, "g")
    quota_common.change_file_group(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                   group_file_list, quota_common.QUOTA_GROUP)

    # 检查配额是否生效
    total_inodes = quota_common.group_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                   quota_common.QUOTA_GROUP)
    if total_inodes != (3000 + soft_val_2):
        rc, stdout = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-1-68 Failed")
        raise Exception("11-0-1-68 Failed")
    else:
        log.info("11-0-1-68 Succeed")
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

    # 针对目录用户组配置inode数为4000硬阈值、3000软阈值（宽限天数为1天）、2000建议阈值的配额【临时：--filenr_grace_time=60】
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                     auth_provider_id=auth_provider_id,
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_suggest_threshold=2000,
                                                     filenr_soft_threshold=3000,
                                                     filenr_grace_time=600,
                                                     filenr_hard_threshold=4000,
                                                     user_type='USERTYPE_GROUP',
                                                     user_or_group_name='quota_group')
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


class Quota_Class_11_0_1_68():
    def quota_method_11_0_1_68(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
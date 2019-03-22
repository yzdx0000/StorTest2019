# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-1-32 目录用户inode数配额软阈值之chown方式
#######################################################

import os
import time

import utils_path
import common
import quota_common
import log

soft_val = 0
if quota_common.flag_slow_machine is True:
    soft_val = 10
else:
    soft_val = 100


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
    quota_dir_for_id = "%s:/%s" % (quota_common.VOLUME_NAME, quota_common.QUOTA_PATH_BASENAME)
    ob_node = common.Node()
    rc, quota_id = quota_common.get_one_quota_id(quota_dir_for_id, quota_common.TYPE_USER, quota_common.QUOTA_USER)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc, qmgrid = quota_common.get_qmgr_id(quota_id)
    common.judge_rc(rc, 0, "get_qmgr_id failed")
    qmgr_ip = ob_node.get_node_ip_by_id(qmgrid)
    # 针对该目录用户写入2000个文件后开始计时
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                            2000, 1, "a", quota_common.QUOTA_USER)

    # 1天之内任意写入文件
    # （1）先写100个属主为root的文件，预期写入成功
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                                            soft_val, 1, "b", "root")

    # （2）之后写100个属主为quota_other_user的文件，预期写入成功
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                            soft_val, 1, "c", quota_common.QUOTA_OTHER_USER)

    # （3）最后尝试写100个属主为quota_user的文件，预期写入成功
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                                            soft_val, 1, "d", quota_common.QUOTA_USER)

    # 1天之后再次尝试写入文件，预期写入失败
#    time.sleep(86400)
    time.sleep(145)
    quota_common.wait_soft_threshold_over_time(qmgr_ip, quota_id, quota_common.SOFT_TIME_FILENR)
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                            1, 1, "e", quota_common.QUOTA_USER)
    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                                            1, 1, "f", quota_common.QUOTA_USER)

    # 检查配额是否生效
    total_inodes = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                                  quota_common.QUOTA_USER)
    if total_inodes != (2000 + soft_val):
        rc, check_result = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-1-32 Failed")
        raise Exception("11-0-1-32 Failed")
    else:
        log.info("11-0-1-32 Succeed")
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

    # 针对目录用户配置inode数为2000软阈值，宽限天数为1天的配额【临时：--filenr_grace_time=60】
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                     auth_provider_id=auth_provider_id,
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_soft_threshold=2000,
                                                     filenr_grace_time=120,
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


class Quota_Class_11_0_1_32():
    def quota_method_11_0_1_32(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
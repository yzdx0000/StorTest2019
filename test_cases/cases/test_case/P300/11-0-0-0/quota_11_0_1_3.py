# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-1-3 目录inode数配额建议阈值
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
    # 先写入2000个文件
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH, 2000, 1, "a")

    # 再尝试继续写入文件
    quota_common.creating_files(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH, 2000, 1, "b")
    time.sleep(5)
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH, 2000, 1, "c")
    time.sleep(5)
    quota_common.creating_files(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH, 2000, 1, "d")
    time.sleep(5)

    # 检查配额是否生效
    total_inodes = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    if total_inodes != 8000:
        rc, check_result3 = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-1-3 Failed")
        raise Exception("11-0-1-3 Failed")
    else:
        log.info("11-0-1-3 Succeed")
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
    # 创建配额目录
    quota_common.creating_dir(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)

    # 针对目录配置inode数为2000建议阈值的配额
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_suggest_threshold=2000)
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


class Quota_Class_11_0_1_3():
    def quota_method_11_0_1_3(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
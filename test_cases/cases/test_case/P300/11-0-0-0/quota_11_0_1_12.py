# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-1-12 目录逻辑空间配额建议阈值
#######################################################

import os
import time
import random
import commands

import utils_path
import common
import quota_common
import log
import shell
import get_config


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
    # 先写入2G文件
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                2048, 1, "a")

    # 再尝试继续写入文件
    quota_common.creating_files(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                2048, 1, "b")
    time.sleep(5)
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                2048, 1, "c")
    time.sleep(5)
    quota_common.creating_files(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                2048, 1, "d")
    time.sleep(5)

    # 检查配额是否生效
    total_file_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    if total_file_size != quota_common.FILE_SIZE_2G * 4:
        rc, stdout = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-1-12 Failed")
        raise Exception("11-0-1-12 Failed")
    else:
        log.info("11-0-1-12 Succeed")
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

    # 针对目录配置逻辑空间为2G建议阈值的配额
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    quota_path = "%s:/%s" % (quota_common.VOLUME_NAME, quota_dir)
    rc, pscli_info = quota_common.create_one_quota(path=quota_path,
                                                   filenr_quota_cal_type='QUOTA_LIMIT',
                                                   logical_suggest_threshold=quota_common.FILE_SIZE_2G)
    common.judge_rc(rc, 0, "create  quota failed")
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


class Quota_Class_11_0_1_12():
    def quota_method_11_0_1_12(self):
        common.case_main(quota_main)


if __name__ == '__main__':
#    print "__file__ = %s" %__file__
#    print "__name__ = %s" %__name__
    common.case_main(quota_main)
#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-1-26 目录物理空间配额混合阈值，建议阈值先生效，
#         软阈值其次生效，限期内硬阈值也生效
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
def cleaning_environment():
    print "（3）cleaning_environment"

    '''
    1、删除所有配额相关的配置信息
    2、删除所有配额测试相关的文件和目录
    '''
    quota_common.delete_all_quota_config()
    quota_common.delete_all_files_and_dir(quota_common.CLIENT_IP_1, quota_common.BASE_QUOTA_PATH)

    return

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
    # 在1天以内再写入1G文件
    quota_common.creating_files(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH, 1000, 1, "b")

    # 写入1G文件后，再尝试继续写入文件
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH, 1, 1, "b")

    # 检查配额是否生效
    if quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH) != "4016M":
        raise Exception("11-0-1-26 Failed")
    else:
        print "11-0-1-26 Succeed"

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
    # 针对目录配置物理空间为4G硬阈值、3G软阈值（宽限天数为1天）、2G建议阈值的配额
    quota_common.sending_quota_config("create_quota")

    # 写入3G文件后开始计时
    quota_common.creating_dir(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH, 3000, 1, "a")

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
    preparing_environment()
    executing_case()
    cleaning_environment()

    return

class Quota_Class_11_0_1_26():
    def quota_method_11_0_1_26(self):
        common.case_main(quota_main)

if __name__ == '__main__':
#    print "__file__ = %s" %__file__
#    print "__name__ = %s" %__name__
    common.case_main(quota_main)
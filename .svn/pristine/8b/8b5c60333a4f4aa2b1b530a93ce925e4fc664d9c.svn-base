#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-1 创建单个配额规则
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
    print "（2）executing_case"

    '''
    1、测试执行
    2、结果检查
    '''
    # 测试执行


    # 结果检查
    if (True):
        raise Exception("11-0-2-1 Failed")
    else:
        print "11-0-2-1 Succeed"

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


    return

#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def quota_main():

    quota_common.cleaning_environment()
    preparing_environment()
    executing_case()
#    quota_common.cleaning_environment()

    return

class Quota_Class_11_0_2_1():
    def quota_method_11_0_2_1(self):
        common.case_main(quota_main)

if __name__ == '__main__':
#    print "__file__ = %s" %__file__
#    print "__name__ = %s" %__name__
    common.case_main(quota_main)
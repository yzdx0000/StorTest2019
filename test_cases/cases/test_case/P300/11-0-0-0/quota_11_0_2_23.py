# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-23 开启配额全局开关
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
    # 开启配额全局开关
    quota_common.open_quota_global_switch()

    # 结果检查
    if int(quota_common.get_quota_global_switch()) != 1:
        rc, check_result = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-2-23 Failed")
        raise Exception("11-0-2-23 Failed")
    else:
        log.info("11-0-2-23 Succeed")
    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    log.info("（1）preparing_environment")
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
    return


class Quota_Class_11_0_2_23():
    def quota_method_11_0_2_23(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
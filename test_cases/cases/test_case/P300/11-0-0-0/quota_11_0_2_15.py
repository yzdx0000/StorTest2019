# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-15 大量数据的目录配额扫描
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
    # 目录quota_test_dir中有10万个1k的小文件
    # 针对该目录用户先写入10万个小文件
    quota_common.creating_1k_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                   100000, 1, "a")

    # 对目录quota_test_dir做目录统计配额
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                      logical_quota_cal_type='QUOTA_COMPUTE')
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    # 获取COMPUTE的结果
    time.sleep(30)
    rc, check_result2 = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    filenr_used_nr = check_result2["result"]["quotas"][0]["filenr_used_nr"]
    log.info("filenr_used_nr = %s" % (filenr_used_nr))

    # 结果检查
    if (check_result1["detail_err_msg"] != "" or
            filenr_used_nr != 100000):
        rc, stdout = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-2-15 Failed")
        raise Exception("11-0-2-15 Failed")
    else:
        log.info("11-0-2-15 Succeed")
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


class Quota_Class_11_0_2_15():
    def quota_method_11_0_2_15(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
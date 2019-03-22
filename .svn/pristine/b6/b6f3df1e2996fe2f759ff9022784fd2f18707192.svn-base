# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-33 创建一个不存在目录的配额
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
    # 尝试创建一个目录不存在的目录配额
    quota_dir = "no_exist_dir"
    rc, check_result = common.create_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                           filenr_quota_cal_type='QUOTA_LIMIT',
                                           filenr_suggest_threshold=1000,
                                           filenr_soft_threshold=2000,
                                           filenr_grace_time=1,
                                           filenr_hard_threshold=3000,
                                           logical_quota_cal_type='QUOTA_LIMIT',
                                           logical_suggest_threshold=1073741824,
                                           logical_soft_threshold=2147483648,
                                           logical_grace_time=1,
                                           logical_hard_threshold=3221225472)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)
    # 结果检查
    if common.json_loads(check_result)["err_no"] == 0:
        rc, stdout = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-2-33 Failed")
        raise Exception("11-0-2-33 Failed")
    else:
        log.info("11-0-2-33 Succeed")
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


class Quota_Class_11_0_2_33():
    def quota_method_11_0_2_33(self):
        common.case_main(quota_main)


if __name__ == '__main__':
#    print "__file__ = %s" %__file__
#    print "__name__ = %s" %__name__
    common.case_main(quota_main)
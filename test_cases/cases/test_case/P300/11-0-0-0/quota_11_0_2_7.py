# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-7 同一目录的同种配额规则仅可配置一条
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
    # （注：因未交付冗余统计和快照统计，脚本实现与用例不同）
    # 尝试配两个相同种类的配额规则，其中一个开启冗余统计，一个不开启冗余统计
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_suggest_threshold=1000,
                                                      filenr_soft_threshold=2000,
                                                      filenr_grace_time=1,
                                                      filenr_hard_threshold=3000)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    # 尝试配两个相同种类的配额规则，其中一个开启快照统计，一个不开启快照统计
    rc, check_result2 = common.create_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                            logical_quota_cal_type='QUOTA_LIMIT',
                                            logical_suggest_threshold=1073741824,
                                            logical_soft_threshold=2147483648,
                                            logical_grace_time=1,
                                            logical_hard_threshold=3221225472)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    # 结果检查
    err_msg = "Quota which path:%s:/%s and user/group: has been exist." % (quota_common.VOLUME_NAME, quota_dir)
    log.info(err_msg)
    if (check_result1["detail_err_msg"] != "" or
            common.json_loads(check_result2)["detail_err_msg"] != err_msg):
        rc, check_result = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-2-7 Failed")
        raise Exception("11-0-2-7 Failed")
    else:
        log.info("11-0-2-7 Succeed")
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


class Quota_Class_11_0_2_7():
    def quota_method_11_0_2_7(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
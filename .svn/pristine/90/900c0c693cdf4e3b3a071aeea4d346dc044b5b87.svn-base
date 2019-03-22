# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-1-18 目录逻辑空间配额混合阈值，建议阈值先生效，
#         软阈值其次生效，限期内硬阈值不生效
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
    soft_val = 1024


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
    rc, quota_id = quota_common.get_one_quota_id(quota_dir_for_id, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    rc, qmgrid = quota_common.get_qmgr_id(quota_id)
    common.judge_rc(rc, 0, "get_qmgr_id failed")
    qmgr_ip = ob_node.get_node_ip_by_id(qmgrid)

    # 写入3G文件后开始计时
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                3072, 1, "a")

    # 在1天以内再写入500M文件
    quota_common.creating_files(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                soft_val, 1, "b")

    # 1天之后再尝试继续写入文件，预期写入失败
#    time.sleep(86400)
    time.sleep(145)
    quota_common.wait_soft_threshold_over_time(qmgr_ip, quota_id, quota_common.SOFT_TIME_LOGICAL)
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                1, 1, "c")
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                1, 1, "d")

    # 检查配额是否生效
    total_file_size = quota_common.dir_total_file_size(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    if total_file_size != quota_common.FILE_SIZE_1M * (3072+soft_val):
        rc, check_result = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-1-18 Failed")
        raise Exception("11-0-1-18 Failed")
    else:
        log.info("11-0-1-18 Succeed")
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

    # 针对目录配置逻辑空间为4G硬阈值、3G软阈值（宽限天数为1天）、2G建议阈值的配额【临时：--logical_grace_time=60s】
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                     logical_quota_cal_type='QUOTA_LIMIT',
                                                     logical_suggest_threshold=2147483648,
                                                     logical_soft_threshold=3221225472,
                                                     logical_grace_time=120,
                                                     logical_hard_threshold=4294967296)
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


class Quota_Class_11_0_1_18():
    def quota_method_11_0_1_18(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-1-1-2 【性能】配额规则扫描效率
# 测试结果：
#       svn53967的扫描效率为：0:00:10.810081，即10.8s
#######################################################

import os
import time
import datetime

import utils_path
import common
import quota_common
import log
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
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
    # 测试执行
    # 创建配额目录
    quota_common.creating_dir(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)

    # 针对该目录用户先写入100万个1k小文件
    quota_common.creating_1k_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                   1000000, 1, "a")

    # 对目录quota_test_dir做目录统计配额
    quota_dir = quota_common.QUOTA_PATH_BASENAME

    starttime = datetime.datetime.now()
    log.info("starttime = %s" % (starttime))

    rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                      logical_quota_cal_type='QUOTA_COMPUTE')
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    log.info("check_result1 = %s" % (check_result1["detail_err_msg"]))

    count = 0
    while (True):
        # 获取COMPUTE的结果
        count = count + 1
        rc, check_result2 = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        if check_result2["result"]["quotas"][0]["state"] == "QUOTA_WORK":
            break
        log.info("count = %s" % (count))
    endtime = datetime.datetime.now()
    log.info("endtime = %s" % (endtime))
    # microseconds是微妙，10的-6次方
    log.info("endtime - starttime = %s" % (endtime - starttime))

    time.sleep(60)   # 等待底层获取准确的filenr
    rc, check_result3 = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    filenr_used_nr = check_result3["result"]["quotas"][0]["filenr_used_nr"]
    log.info("filenr_used_nr = %s" % (filenr_used_nr))

    # 结果检查（没有扫描时间的预估值，此处只判断扫描结果是否正确）
    if (check_result1["detail_err_msg"] != "" or
            filenr_used_nr != 1000000):
        raise Exception("11-1-1-2 Failed")
    else:
        log.info("11-1-1-2 Succeed")
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
    return


#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def quota_main():
    prepare_clean.test_prepare(FILE_NAME)
    quota_common.cleaning_environment()
    preparing_environment()
    executing_case()
    if quota_common.DEBUG != "on":
        quota_common.cleaning_environment()
    return


class Quota_Class_11_1_1_2():
    def quota_method_11_1_1_2(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
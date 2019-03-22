# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-42 修改目录配额规则之改大、改小硬阈值
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
    # （1）配置目录配额规则硬阈值为1000
    quota_dir = quota_common.QUOTA_PATH_BASENAME

    rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_hard_threshold=1000)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    log.info("check_result1 = %s" % (check_result1["detail_err_msg"]))

    # 验证配额是否生效，预期成功写入1000个文件
    cmd = "cd %s; for i in {1..1001}; do touch file_$i; done" % (quota_common.QUOTA_PATH)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))
    total_inodes1 = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    log.info("total_inodes1 = %s" % (total_inodes1))

    # 获取配额id
    rc, check_result = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    quota_id = check_result["result"]["quotas"][0]["id"]
    log.info("quota_id = %s" % (quota_id))

    # （2）修改目录配额规则硬阈值为2000
    rc, check_result2 = quota_common.update_one_quota(id=quota_id,
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_hard_threshold=2000)
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)
    log.info("check_result2 = %s" % (check_result2["detail_err_msg"]))

    # 验证配额是否生效，预期成功再写入1000个文件
    cmd = "cd %s; for i in {2001..3001}; do touch file_$i; done" % (quota_common.QUOTA_PATH)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))
    total_inodes2 = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    log.info("total_inodes2 = %s" % (total_inodes2))

    # （3）修改目录配额规则硬阈值为1000
    rc, check_result3 = quota_common.update_one_quota(id=quota_id,
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_hard_threshold=1000)
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)
    log.info("check_result3 = %s" % (check_result3["detail_err_msg"]))

    # 验证配额是否生效，预期无法继续写入文件
    cmd = "cd %s; for i in {4000..4001}; do touch file_$i; done" % (quota_common.QUOTA_PATH)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))
    total_inodes3 = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    log.info("total_inodes3 = %s" % (total_inodes3))

    # 结果检查
    if (check_result1["detail_err_msg"] != "" or
            total_inodes1 != 1000 or
            check_result2["detail_err_msg"] != "" or
            total_inodes2 != 2000 or
            check_result3["detail_err_msg"] != "" or
            total_inodes3 != 2000):
        rc, check_result = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-2-42 Failed")
        raise Exception("11-0-2-42 Failed")
    else:
        log.info("11-0-2-42 Succeed")
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


class Quota_Class_11_0_2_42():
    def quota_method_11_0_2_42(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
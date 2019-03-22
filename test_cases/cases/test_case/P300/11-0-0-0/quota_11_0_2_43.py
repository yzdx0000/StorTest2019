# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-43 修改目录配额规则之改大、改小软阈值
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
    # （1）配置目录配额规则软阈值为1000，宽限天数为1天【临时：--filenr_grace_time=60】
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_soft_threshold=1000,
                                                      filenr_grace_time=60)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    log.info("check_result1 = %s" % (check_result1["detail_err_msg"]))

    # 验证配额是否生效，预期成功写入1000个文件触发宽限时间启动
    cmd = "cd %s; for i in {1..1000}; do touch file_$i; done" % (quota_common.QUOTA_PATH)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))
    total_inodes1_1 = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    log.info("total_inodes1_1 = %s" % (total_inodes1_1))

    # 宽限期限内可任意写入文件
    cmd = "cd %s; for i in {1001..1100}; do touch file_$i; done" % (quota_common.QUOTA_PATH)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))
    total_inodes1_2 = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    log.info("total_inodes1_2 = %s" % (total_inodes1_2))

#    time.sleep(3600)
    time.sleep(70)

    # 宽限期限外不能再写入文件
    cmd = "cd %s; for i in {1101..1102}; do touch file_$i; done" % (quota_common.QUOTA_PATH)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))
    total_inodes1_3 = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    log.info("total_inodes1_3 = %s" % (total_inodes1_3))

    # 获取配额id
    rc, quota_id = quota_common.get_one_quota_id(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    log.info("quota_id = %s" % (quota_id))

    # （2）修改目录配额规则软阈值为2000，宽限天数为1天【临时：--filenr_grace_time=60】
    rc, check_result2 = quota_common.update_one_quota(id=quota_id,
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_soft_threshold=2000,
                                                      filenr_grace_time=60,)
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)
    log.info("check_result2 = %s" % (check_result2["detail_err_msg"]))

    # 验证配额是否生效，预期成功再写入900个文件触发宽限时间启动
    cmd = "cd %s; for i in {2001..2900}; do touch file_$i; done" % (quota_common.QUOTA_PATH)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))
    total_inodes2_1 = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    log.info("total_inodes2_1 = %s" % (total_inodes2_1))

    # 宽限期限内可任意写入文件
    cmd = "cd %s; for i in {3001..3100}; do touch file_$i; done" % (quota_common.QUOTA_PATH)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))
    total_inodes2_2 = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    log.info("total_inodes2_2 = %s" % (total_inodes2_2))

    #    time.sleep(3600)
    time.sleep(70)

    # 宽限期限外不能再写入文件
    cmd = "cd %s; for i in {3101..3102}; do touch file_$i; done" % (quota_common.QUOTA_PATH)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))
    total_inodes2_3 = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    log.info("total_inodes2_3 = %s" % (total_inodes2_3))

    # (3)修改目录配额规则软阈值为1000，宽限天数为1天【临时：--filenr_grace_time=60】
    rc, check_result3 = quota_common.update_one_quota(id=quota_id,
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_soft_threshold=1000,
                                                      filenr_grace_time=60)
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)
    log.info("check_result3 = %s" % (check_result3["detail_err_msg"]))

    # 预期无法继续写入文件，因为实际2000>1000的阈值，宽限起始时间不变，当前为宽限期限外，不能再写入文件
    cmd = "cd %s; for i in {4000..4001}; do touch file_$i; done" % (quota_common.QUOTA_PATH)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))
    total_inodes3_1 = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    log.info("total_inodes3_1 = %s" % (total_inodes3_1))

    # 结果检查
    if (check_result1["detail_err_msg"] != "" or
            total_inodes1_1 != 1000 or
            total_inodes1_2 != 1100 or
            total_inodes1_3 != 1100 or
            check_result2["detail_err_msg"] != "" or
            total_inodes2_1 != 2000 or
            total_inodes2_2 != 2100 or
            total_inodes2_3 != 2100 or
            check_result3["detail_err_msg"] != "" or
            total_inodes3_1 != 2100):
        rc, stdout = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-2-43 Failed")
        raise Exception("11-0-2-43 Failed")
    else:
        log.info("11-0-2-43 Succeed")
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


class Quota_Class_11_0_2_43():
    def quota_method_11_0_2_43(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
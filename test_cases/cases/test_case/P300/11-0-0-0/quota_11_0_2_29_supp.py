# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-29_supp 删除带配额规则的目录（补充测试）
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
    # （1）创建目录配额规则
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_hard_threshold=100)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    # （2）写103个文件，预期写成功100个
    cmd = "cd %s; for i in {1..103}; do touch file_$i; done" % (quota_common.QUOTA_PATH)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))
    total_inodes1 = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    log.info("total_inodes1 = %s" % (total_inodes1))

    # （3）删除配额目录
    quota_common.delete_all_files_and_dir(quota_common.CLIENT_IP_1, quota_common.BASE_QUOTA_PATH)

    # 查看配额规则
    rc, check_result2 = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")

    # （4）创建相同名称的配额目录
    quota_common.creating_dir(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)

    # （5）写103个文件验证配额是否限制成功，预期全部写入成功
    cmd = "cd %s; for i in {1..103}; do touch file_$i; done" % (quota_common.QUOTA_PATH)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))
    total_inodes2 = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    log.info("total_inodes2 = %s" % (total_inodes2))

    # 删除配额
    quota_common.delete_all_quota_config()

    # 创建配额
    rc, check_result3 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_hard_threshold=100)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    # 配额创建完成后time.sleep(10)再写数据
    time.sleep(10)
    
    # 写文件验证，预期写入失败
    cmd = "cd %s; for i in {201..210}; do touch file_$i; done" % (quota_common.QUOTA_PATH)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))
    total_inodes3 = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    log.info("total_inodes3 = %s" % (total_inodes3))

    # 结果检查
    if (check_result1["detail_err_msg"] != "" or
            total_inodes1 != 100 or
            len(check_result2["result"]["quotas"]) != 1 or
            total_inodes2 != 103 or
            check_result3["detail_err_msg"] != "" or
            total_inodes3 != 103):
        rc, stdout = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-2-29_supp Failed")
        raise Exception("11-0-2-29_supp Failed")
    else:
        print "11-0-2-29_supp Succeed"
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


class Quota_Class_11_0_2_29_supp():
    def quota_method_11_0_2_29_supp(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
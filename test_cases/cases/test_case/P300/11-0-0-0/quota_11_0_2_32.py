# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-32 增删改查配额目录下的文件，配额规则不受影响
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
    # 单客户端先写入1000个文件，预期写入成功
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                1000, 1, "a")

    # 针对目录配置inode数为2000硬阈值的配额
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_hard_threshold=2000)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    log.info("check_result = %s" % (check_result))

    time.sleep(10)  # 等待文件扫描完毕再写新文件，此处使用sleep 10s简单处理
    # 写100个文件1M的文件
    cmd = (("cd %s; for i in {1..100}; do dd if=/dev/zero of=100file1_$i bs=1M count=1; done")
           % (quota_common.QUOTA_PATH))
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))

    # 偏移写这100个文件为3M
    cmd = (("cd %s; for i in {1..100}; do dd if=/dev/zero of=100file1_$i bs=1M count=1 seek=2; done")
           % (quota_common.QUOTA_PATH))
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))

    # 删除后写入的100个文件
    common.rm_exe(quota_common.CLIENT_IP_1, os.path.join(quota_common.QUOTA_PATH, '100file1*'))

    # 写100个文件1M的文件
    cmd = (("cd %s; for i in {1..100}; do dd if=/dev/zero of=100file2_$i bs=1M count=1; done")
           % (quota_common.QUOTA_PATH))
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))

    # 偏移写这100个文件为3M
    cmd = (("cd %s; for i in {1..100}; do dd if=/dev/zero of=100file2_$i bs=1M count=1 seek=2; done")
           % (quota_common.QUOTA_PATH))
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))

    # 另一个客户端继续写入1000文件，预期成功写入900
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                1000, 1, "b")

    # 再尝试写入10个文件，预期写入失败
    quota_common.creating_files(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH,
                                10, 1, "c")

    total_inodes = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    log.info("total_inodes = %s" % (total_inodes))
    # 结果检查
    if (check_result["detail_err_msg"] != "" or
            total_inodes != 2000):
        rc, stdout = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        raise Exception("11-0-2-32 Failed")
    else:
        log.info("11-0-2-32 Succeed")
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


class Quota_Class_11_0_2_32():
    def quota_method_11_0_2_32(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
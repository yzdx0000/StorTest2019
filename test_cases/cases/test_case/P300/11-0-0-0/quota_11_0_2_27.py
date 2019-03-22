# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-27 路径最大深度255
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

    # 路径按/mnt/volume/dir...计算
    # （1）下面的路径深度为255，预期配置成功
    # 创建目录
    log.info('创建深度为255的路径')
    cmd = "cd %s; for i in {1..253}; do mkdir a; cd a; done; pwd" % (quota_common.BASE_QUOTA_PATH)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))
    check_path1 = stdout.split()[0]

    prefix_len = len(quota_common.BASE_QUOTA_PATH)  # len of /mnt/volume1

    dir1 = check_path1[(prefix_len + 1):]  # 从 '/dir1_$i'的'd'开始

    # 下发配额，预期配置成功
    log.info('路径深度为255，预计配额下发成功')
    rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, dir1)),
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_hard_threshold=2000)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    log.info("check_result1 = %s" % check_result1)

    # 写文件验证
    # 预期可成功写入2000个文件，第2001个文件写入失败
    quota_common.creating_files(quota_common.CLIENT_IP_1, check_path1,
                                2001, 1, "a")
    # 预期下面的文件写入失败
    quota_common.creating_files(quota_common.CLIENT_IP_2, check_path1,
                                1, 1, "b")

    total_inodes = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, check_path1)
    log.info("total_inodes = %s" % (total_inodes))

    # （2）下面的路径深度为256，预期配置失败
    # 创建目录
    log.info('创建深度为256路径')
    cmd = "cd %s; for i in {1..254}; do mkdir b; cd b; done; pwd" % (quota_common.BASE_QUOTA_PATH)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))
    check_path2 = stdout.split()[0]
    prefix_len2 = len(quota_common.BASE_QUOTA_PATH)  # len of /mnt/volume1
    dir2 = check_path2[(prefix_len2+1):]  # 从 '/dir1_$i'的'd'开始

    # 下发配额，预期配置失败
    log.info('路径深度为256，预计配额下发失败')
    rc, check_result2 = common.create_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, dir2)),
                                            filenr_quota_cal_type='QUOTA_LIMIT',
                                            filenr_hard_threshold=2000)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    log.info("check_result2 = %s" % check_result2)

    # 结果检查
    if (check_result1["detail_err_msg"] != "" or
            total_inodes != 2000 or
            common.json_loads(check_result2)["err_no"] == 0):
        rc, stdout = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-2-27 Failed")
        raise Exception("11-0-2-27 Failed")
    else:
        log.info("11-0-2-27 Succeed")
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


class Quota_Class_11_0_2_27():
    def quota_method_11_0_2_27(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
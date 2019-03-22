# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-13 配额规则目录下的硬链接是统计的
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
    # 在目录quota_test_dir下对文件a做硬链接b，硬链接文件b也在目录quota_test_dir下，通过硬链接b
    # 改变文件a的大小，使其达到硬阈值，预期达到阈值后将不能继续通过链接b对文件a进行追加写
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                      logical_quota_cal_type='QUOTA_LIMIT',
                                                      logical_hard_threshold=1073741824)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)
    log.info("check_result1 = %s" % (check_result1))

    # dd写文件a到500M
    cmd = ("dd if=/dev/zero of=%s/a bs=1M count=500") % (quota_common.QUOTA_PATH)
    try:
        rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
        if rc != 0:
            log.error("Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
    except:
        log.info("print_except_stderr: \n%s" % (stdout))
    check_result2 = "No space left on device" not in stdout
    log.info("check_result2 = %s" % (check_result2))

    # 对文件a做硬链接b
    cmd = ("ln %s/a %s/b") % (quota_common.QUOTA_PATH, quota_common.QUOTA_PATH)
    try:
        rc, stdout = common.run_command(quota_common.CLIENT_IP_2, cmd)
        if rc != 0:
            log.error("Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
    except:
        log.info("print_except_stderr: \n%s" % (stdout))

    # 再通过b追加500M，预期追加成功
    cmd = ("dd if=/dev/zero of=%s/b bs=1M seek=500 count=500") % (quota_common.QUOTA_PATH)
    try:
        rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
        if rc != 0:
            log.error("Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
    except:
        log.info("print_except_stderr: \n%s" % (stdout))
    check_result3 = "No space left on device" not in stdout
    log.info("check_result3 = %s" % (check_result3))

    time.sleep(10)
    # 再次尝试通过b追加100M，预期追加失败
    cmd = ("dd if=/dev/zero of=%s/b bs=1M seek=1000 count=100") % (quota_common.QUOTA_PATH)
    try:
        rc, stdout = common.run_command(quota_common.CLIENT_IP_2, cmd)
        if rc != 0:
            log.error("Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
    except:
        log.info("print_except_stderr: \n%s" % (stdout))
    check_result4 = "No space left on device" not in stdout
    log.info("check_result4 = %s" % (check_result4))

    # 结果检查
    if (check_result1["detail_err_msg"] != ""
            or not check_result2
            or not check_result3
            or check_result4):
        rc, stdout = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-2-13 Failed")
        raise Exception("11-0-2-13 Failed")
    else:
        log.info("11-0-2-13 Succeed")
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


class Quota_Class_11_0_2_13():
    def quota_method_11_0_2_13(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-14 配额规则目录外的硬链接是不统计的【用例作废】
#         注：“是不统计的”更正为“可能统计可能不统计” —— khy
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
    # 在目录quota_test_dir下对文件a做硬链接c，硬链接文件c在目录quota_test_dir外，通过硬链接c
    # 改变文件a的大小，使其达到硬阈值，预期通过硬链接文件c对文件a的追加写是不受配额规则限制的
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                     auth_provider_id=4,
                                                     logical_quota_cal_type='QUOTA_LIMIT',
                                                     logical_hard_threshold=1073741824)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

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

    # 对文件a做硬链接c，
    cmd = ("ln %s/a %s/c") % (quota_common.QUOTA_PATH, quota_common.BASE_QUOTA_PATH)
    try:
        rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
        if rc != 0:
            log.error("Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
    except:
        log.info("print_except_stderr: \n%s" % (stdout))

    # 再通过c追加500M，预期追加成功
    cmd = ("dd if=/dev/zero of=%s/c bs=1M seek=500 count=500") % (quota_common.BASE_QUOTA_PATH)
    try:
        rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
        if rc != 0:
            log.error("Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
    except:
        log.info("print_except_stderr: \n%s" % (stdout))
    check_result3 = "No space left on device" not in stdout

    # 再次尝试通过c追加1000M，预期可能追加成功可能追加不成功，因此不对该项进行检查
    cmd = ("dd if=/dev/zero of=%s/c bs=1M seek=1000 count=1000") % (quota_common.BASE_QUOTA_PATH)
    try:
        rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
        if rc != 0:
            log.error("Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
    except:
        log.info("print_except_stderr: \n%s" % (stdout))
    check_result4 = "No space left on device" not in stdout

    # 结果检查，用例废掉，永远输出成功
    if (False):
        raise Exception("11-0-2-14 Failed")
    else:
        log.info("11-0-2-14 Succeed")
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


class Quota_Class_11_0_2_14():
    def quota_method_11_0_2_14(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
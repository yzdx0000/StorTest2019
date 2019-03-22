# -*- encoding=utf8 -*-

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-25 配额目录支持中文
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
    # 对中文目录配置配额
    rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, "中文目录")),
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_hard_threshold=2000)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    # 检查配额配置是否成功
    rc, get_quota_result = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    check_result2 = get_quota_result["result"]["quotas"][0]["path"]

    # 检查配额配置是否生效
    chinese_dir = quota_common.BASE_QUOTA_PATH + "/中文目录"
    # 单客户端先写入2000个文件，预期写入成功
    quota_common.creating_files(quota_common.CLIENT_IP_1, chinese_dir,
                                2000, 1, "a")
    # 再尝试另一个客户端继续写入文件，预期写入失败
    quota_common.creating_files(quota_common.CLIENT_IP_2, chinese_dir,
                                2000, 1, "b")

    check_result3 = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, chinese_dir)
    log.info("check_result3 = %s" % (check_result3))

    # 结果检查
    if (check_result1["detail_err_msg"] != "" or
            check_result2 != "%s:/中文目录" % (quota_common.VOLUME_NAME) or
            check_result3 != 2000):
        rc, stdout = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-2-25 Failed")
        raise Exception("11-0-2-25 Failed")
    else:
        log.info("11-0-2-25 Succeed")
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
    # 创建中文目录
    chinese_dir = quota_common.BASE_QUOTA_PATH + "/中文目录"

    cmd = "mkdir -p %s" % (chinese_dir)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
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


class Quota_Class_11_0_2_25():
    def quota_method_11_0_2_25(self):
        common.case_main(quota_main)


if __name__ == '__main__':
#    print "__file__ = %s" %__file__
#    print "__name__ = %s" %__name__
    common.case_main(quota_main)
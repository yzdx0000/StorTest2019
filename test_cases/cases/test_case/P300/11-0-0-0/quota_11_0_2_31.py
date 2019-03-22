# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-31 重命名带配额规则的目录
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
    # 创建目录配额规则
    quota_dir = quota_common.QUOTA_PATH_BASENAME

    rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_hard_threshold=2000)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)
    log.info("check_result = %s" % (check_result))

    # 重命名带配额规则的目录
    new_name_dir = quota_common.BASE_QUOTA_PATH + "/rename_quota_test_dir"
    cmd = "mv %s %s" % (quota_common.QUOTA_PATH, new_name_dir)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if 0 != rc:
        log.info("rc = %s" % (rc))
        log.error("Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \n" % (cmd, stdout))

    # 验证移动位置后的目录配额规则是否依然生效，预期是依然生效
    # 单客户端先写入2000个文件，预期写入成功
    quota_common.creating_files(quota_common.CLIENT_IP_1, new_name_dir, 2000, 1, "a")

    # 再尝试另一个客户端继续写入文件，预期写入失败
    quota_common.creating_files(quota_common.CLIENT_IP_2, new_name_dir, 2000, 1, "b")

    total_inodes = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, new_name_dir)
    print "total_inodes = %s" % (total_inodes)
    # 结果检查
    if (check_result["detail_err_msg"] != "" or
            total_inodes != 2000):
        rc, stdout = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-2-31 Failed")
        raise Exception("11-0-2-31 Failed")
    else:
        log.info("11-0-2-31 Succeed")
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
    quota_common.creating_dir(quota_common.NOTE_IP_1, quota_common.QUOTA_PATH)
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


class Quota_Class_11_0_2_31():
    def quota_method_11_0_2_31(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
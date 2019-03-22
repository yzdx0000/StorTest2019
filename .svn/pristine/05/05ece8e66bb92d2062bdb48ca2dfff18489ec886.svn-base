# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-26 路径最大长度1024
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

    # （1）测试路径最大长度1024
    # 按/mnt/volume/dir...计算路径长度
    # 路径总长度 = 5 + len("quota_common.VOLUME_NAME") + 1 + 待构造的路径长度
    # 待构造的路径长度 = 1023 - 5 - len("quota_common.VOLUME_NAME") - 1

    cmd = "cd %s; for i in {1..50}; do mkdir aaaaaaaaaaaaaaaaaaa; \
    cd aaaaaaaaaaaaaaaaaaa; done; pwd" % (quota_common.BASE_QUOTA_PATH)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))
    check_path = stdout.split()[0]

    prefix_len = len(quota_common.BASE_QUOTA_PATH)  # len of /mnt/volume1
    path = check_path[(prefix_len+1):]  # 从 '/aaaa....'的'a'开始

    # 还需构造的路径长度
    # ( 5 + len(quota_common.VOLUME_NAME) + 1 )为/mnt/valume/的长度
    # len(fs_path)为已构造的长度
    # 最后面的减1为下面【fs_path + "/" + "b" * length】中“/”的长度
    construct_length = 1023 - (5 + len(quota_common.VOLUME_NAME) + 1) - len(path) - 1
    log.info("construct_length = %s" % construct_length)

    path_new = path + "/" + "b" * construct_length
    log.info("len(path_new) = %s" % len(path_new))

    # 在最深层aaa...目录中mkdir bbb...，以备下面下发配额使用
    path_bbb = "b" * construct_length
    cmd = "cd %s; mkdir %s" % (check_path, path_bbb)
    rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))

    # 下发配额，预期配置成功
    log.info('对长度为1023的路径下发配额,预计下发成功')
    rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_new)),
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_hard_threshold=2000)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    log.info("check_result1 = %s" % check_result1)

    '''
    # 写文件验证
    #【因/mnt/parastor + 构造的路径 > 4096，所以cd check_path1时报File name too long，
    # 可分多次cd进去写文件，下面的creating_files函数不可用，暂不验证写文件了】
    # 预期可成功写入2000个文件，第2001个文件写入失败
    check_path1 = quota_common.BASE_QUOTA_PATH + "/" + path_new
    quota_common.creating_files(quota_common.CLIENT_IP_1, check_path1,
                                2001, 1, "a")
    # 预期下面的文件写入失败
    quota_common.creating_files(quota_common.CLIENT_IP_2, check_path1,
                                1, 1, "b")

    total_inodes = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, check_path1)
    log.info("total_inodes = %s" % (total_inodes))
    '''

    # （2）测试路径最大长度1024
    path_new_2 = path + "/" + "b" * (construct_length + 1)
    log.info("len(path_new_2) = %s" % len(path_new_2))

    # 下发配额，预期配置失败
    log.info('对长度为1024的路径下发配额,预计下发失败')
    rc, check_result2 = common.create_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_new_2)),
                                            filenr_quota_cal_type='QUOTA_LIMIT',
                                            filenr_hard_threshold=2000)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)
    log.info("check_result2 = %s" % check_result2)

    # 结果检查
    if (check_result1["detail_err_msg"] != "" or
            common.json_loads(check_result2)["err_no"] == 0):
        rc, stdout = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-2-26 Failed")
        raise Exception("11-0-2-26 Failed")
    else:
        log.info("11-0-2-26 Succeed")
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


class Quota_Class_11_0_2_26():
    def quota_method_11_0_2_26(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
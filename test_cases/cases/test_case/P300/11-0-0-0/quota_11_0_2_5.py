# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-5 GUI或CLI批量删除配额规则
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
    count = 10

    # GUI或CLI批量删除10条已经存在的配额规则
    for i in range(1, count + 1):
        dir = quota_common.QUOTA_PATH_ABSPATH + "%s" % i

        log.info(dir)
        quota_common.creating_dir(quota_common.CLIENT_IP_1, dir)

        # 创建配额
        quota_dir = os.path.basename(dir)

        rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                          filenr_quota_cal_type='QUOTA_LIMIT',
                                                          filenr_hard_threshold=2000)
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

        # 验证配额，预期写入2000
        quota_common.creating_files(quota_common.CLIENT_IP_1, dir,
                                    2000, 1, "a")
        total_inodes1 = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir)

        # 写入文件检查
        print "total_inodes1 = %s" % (total_inodes1)
        if check_result1["detail_err_msg"] != "" or \
                total_inodes1 != 2000:
            log.error("11-0-2-5 Failed")
            raise Exception("11-0-2-5 Failed")

    # 批量删除配额
    check_result2 = quota_common.delete_all_quota_config()

    for i in range(1, count + 1):
        dir = quota_common.QUOTA_PATH_ABSPATH + "%s" % i

        # 验证删除配额规则后文件写入情况，预期可继续任意写入文件
        cmd = ("cd %s; for i in {1..%s}; do dd if=/dev/zero of=file_%s_%s_$i bs=1M count=%s; done") % (
            dir, 2000, quota_common.CLIENT_IP_2, "b", 1)
        rc, stdout = common.run_command(quota_common.CLIENT_IP_2, cmd)
        if rc != 0:
            log.info("rc = %s" % (rc))
            log.info("WARNING: \ncmd = %s\nstdout = %s\n" % (cmd, stdout))
        total_inodes2 = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir)

        # 写入文件检查
        print "total_inodes2 = %s" % (total_inodes2)
        if total_inodes2 != 4000:
            log.error("11-0-2-5 Failed")
            raise Exception("11-0-2-5 Failed")

    # 删除结果检查
    print "check_result2 = %s" % (check_result2)
    if check_result2["detail_err_msg"] != "":
        rc, check_result = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        log.error("11-0-2-5 Failed")
        raise Exception("11-0-2-5 Failed")
    else:
        log.info("11-0-2-5 Succeed")
    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    log.info("（1）preparing_environment")
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


class Quota_Class_11_0_2_5():
    def quota_method_11_0_2_5(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
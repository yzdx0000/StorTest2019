# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-0-2-72 同一目录创建1000个不同用户的配额
#######################################################

from multiprocessing import Process
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
N = 50  # 进程数


def create_group_and_user(start, end,auth_provider_id):
    for i in range(start, end):
        group_name = "myscript_quota_group_%s" % i
        user_name = "myscript_quota_user_%s" % i
        quota_common.create_designated_quota_group(group_name, auth_provider_id)
        quota_common.create_designated_quota_user(user_name, group_name, auth_provider_id)
    return


def judge_process(pro_lst):
    """判断状态"""
    stop_flag = False
    stat_lst = []
    for i in range(20):
        stat_lst.append(False)
    while True:
        log.info('wait 10s')
        time.sleep(10)
        for i, pro in enumerate(pro_lst):
            if pro.is_alive():
                continue
            else:
                if pro.exitcode != 0:
                    log.info('pricess id: %s failed' % i)
                    stop_flag = True
                    break
                else:
                    stat_lst[i] = True
        if stop_flag is True:
            for pro in pro_lst:
                pro.terminate()
                common.except_exit("failed")
        if False not in stat_lst:
            break


def executing_case():
    print "（2）executing_case"

    '''
    1、测试执行
    2、结果检查
    '''
    # 创建1000个用户和用户组，耗时3小时
    # 创建65个配额，耗时50分钟 --->1000个配额耗时18小时
    # 测试执行
    # 同一个目录创建1000个不同用户的配额
    count = 70
    quota_common.preparing_zone_nas()
    auth_provider_id = quota_common.get_auth_provider_id_with_access_zone_name(quota_common.QUOTA_ACCESS_ZONE)
    div = N
    process_lst = []

    """
    for i in range(div):
        start = i * (count/div) + 1
        end = start + (count/div) + 1
        process_lst.append(Process(target=create_group_and_user, args=(start, end, auth_provider_id,)))
        process_lst[i].daemon = True
    for pro in process_lst:
        pro.start()
    """


    for i in range(1, count + 1):

        # 创建用户和用户组
        group_name = "myscript_quota_group_%s" % i
        user_name = "myscript_quota_user_%s" % i

        quota_common.create_designated_quota_group(group_name, auth_provider_id)
        quota_common.create_designated_quota_user(user_name, group_name, auth_provider_id)

    for i in range(1, count + 1):
        user_name = "myscript_quota_user_%s" % i

        # 创建配额
        rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME,
                                                                            quota_common.QUOTA_PATH_BASENAME)),
                                                          auth_provider_id=auth_provider_id,
                                                          filenr_quota_cal_type='QUOTA_LIMIT',
                                                          filenr_hard_threshold=100,
                                                          filenr_soft_threshold=50,
                                                          filenr_grace_time=600,
                                                          filenr_suggest_threshold=10,
                                                          logical_quota_cal_type='QUOTA_LIMIT',
                                                          logical_hard_threshold=3221225472,
                                                          logical_grace_time=600,
                                                          logical_suggest_threshold=1073741824,
                                                          logical_soft_threshold=2147483648,
                                                          user_type='USERTYPE_USER',
                                                          user_or_group_name=user_name)
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

        log.info("i = %s, check_result1 = %s" % (i, check_result1))

        if check_result1["detail_err_msg"] != "":
            raise Exception("11-0-2-72 Failed")

        time.sleep(5)
        # 验证配额，预期写入500（使用su方式指定用户写）
        quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH, 101, 1, i, user_name)
        total_inodes = quota_common.user_total_inodes(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH, user_name)
        log.info("i = %s, total_inodes = %s" % (i, total_inodes))

        # 写入文件检查
        if total_inodes != 100:
            log.error("11-0-2-72 Failed")
            raise Exception("11-0-2-72 Failed")

    # 查询配额下发个数
    rc, stdout = common.get_quota(param_name='user_or_group_name', param_value='myscript_quota_user_')
    if rc != 0:
        common.judge_rc(rc, 0, 'get_quota failed')
    check_result2 = common.json_loads(stdout)
    quota_count = check_result2["result"]["total"]
    log.info("quota_count = %s" % (quota_count))

    '''
    for i in range(1, count + 1):
        # 删除用户和用户组
        group_name = "quota_group_%s" % i
        user_name = "quota_user_%s" % i
        quota_common.delete_designated_quota_user(user_name)
        quota_common.delete_designated_quota_group(group_name)
    '''

    # 结果检查
    if quota_count != count:
        raise Exception("11-0-2-72 Failed")
    else:
        log.info("11-0-2-72 Succeed")
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


class Quota_Class_11_0_2_72():
    def quota_method_11_0_2_72(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
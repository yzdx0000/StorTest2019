# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-3-1-3 【稳定性】配置修改过程中kill掉主oJob进程
#######################################################

import os
import time

import utils_path
import common
import quota_common
import log
import make_fault
import prepare_clean
from multiprocessing import Process, Value

alive = Value('b', False)

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
def update_quota_when_kill_process():
    # 创建一个目录配额规则
    dir = quota_common.QUOTA_PATH
    quota_common.creating_dir(quota_common.CLIENT_IP_1, dir)
    quota_dir = quota_common.QUOTA_PATH_BASENAME

    rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_suggest_threshold=1000,
                                                      filenr_soft_threshold=2000,
                                                      filenr_grace_time=1,
                                                      filenr_hard_threshold=3000,
                                                      logical_quota_cal_type='QUOTA_LIMIT',
                                                      logical_suggest_threshold=1073741824,
                                                      logical_soft_threshold=2147483648,
                                                      logical_grace_time=1,
                                                      logical_hard_threshold=3221225472)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    rc, quota_id = quota_common.get_one_quota_id(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")

    rc, check_result2 = quota_common.update_one_quota(id=quota_id,
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_suggest_threshold=2000,
                                                      filenr_soft_threshold=3000,
                                                      filenr_grace_time=5,
                                                      filenr_hard_threshold=4000,
                                                      logical_quota_cal_type='QUOTA_LIMIT',
                                                      logical_suggest_threshold=2147483648,
                                                      logical_soft_threshold=3221225472,
                                                      logical_grace_time=10,
                                                      logical_hard_threshold=4294967296)
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)

    rc, check_result3 = quota_common.update_one_quota(id=quota_id,
                                                      filenr_quota_cal_type='QUOTA_COMPUTE',
                                                      logical_quota_cal_type='QUOTA_LIMIT',
                                                      logical_suggest_threshold=1073741824,
                                                      logical_soft_threshold=2147483648,
                                                      logical_grace_time=1,
                                                      logical_hard_threshold=3221225472)
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)

    rc, check_result4 = quota_common.update_one_quota(id=quota_id,
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_suggest_threshold=1000,
                                                      filenr_soft_threshold=2000,
                                                      filenr_grace_time=1,
                                                      filenr_hard_threshold=3000,
                                                      logical_quota_cal_type='QUOTA_COMPUTE')
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)

    rc, check_result5 = quota_common.update_one_quota(id=quota_id,
                                                      filenr_quota_cal_type='QUOTA_COMPUTE',
                                                      logical_quota_cal_type='QUOTA_COMPUTE')
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)

    # 修改成不合法的配额规则
    rc, check_result6 = quota_common.update_one_quota(id=quota_id,
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_suggest_threshold=4000,
                                                      filenr_soft_threshold=3000,
                                                      filenr_grace_time=5,
                                                      filenr_hard_threshold=2000,
                                                      logical_quota_cal_type='QUOTA_LIMIT',
                                                      logical_suggest_threshold=2147483648,
                                                      logical_soft_threshold=3221225472,
                                                      logical_grace_time=10,
                                                      logical_hard_threshold=4294967296)
    # common.judge_rc(rc, 0, "update quota failed", exit_flag=False)

    # 结果检查
    if (check_result1["detail_err_msg"] != "" or
            check_result2["detail_err_msg"] != "" or
            check_result3["detail_err_msg"] != "" or
            check_result4["detail_err_msg"] != "" or
            check_result5["detail_err_msg"] != "" or
            check_result6 != {}):
        raise Exception("update_quota_when_kill_process is failed!")
    return


def kill_master_process_when_update_quota(alive, process_name):
    while alive.value:
        # 获取主进程所在节点的id
        process_node_id = quota_common.get_master_process_node_id(process_name)
        if process_node_id != 250:
            # 获取主进程所在的节点ip
            node_ip = quota_common.get_node_ip_by_id(process_node_id)

            make_fault.kill_process(node_ip, process_name)
        else:
            print "process_name is wrong!"

        time.sleep(120)
    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    print "（2）executing_case"

    '''
    1、测试执行
    2、结果检查
    '''
    # 测试执行

    p1 = Process(target=update_quota_when_kill_process, args=())
    p2 = Process(target=kill_master_process_when_update_quota, args=(alive, "oJob", ))

    alive.value = True
    p1.start()
    p2.start()

    p1.join()
    alive.value = False

    if p1.exitcode != 0:
        raise Exception("11-3-1-3 Failed")
    else:
        print "11-3-1-3 Succeed"
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
    return


#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def quota_main():
    prepare_clean.test_prepare(FILE_NAME)
    quota_common.cleaning_environment()
    preparing_environment()
    executing_case()
    if quota_common.DEBUG != "on":
        quota_common.cleaning_environment()
    return


class Quota_Class_11_3_1_3():
    def quota_method_11_3_1_3(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
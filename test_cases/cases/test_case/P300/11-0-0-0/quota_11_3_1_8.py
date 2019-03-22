# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-3-1-8 【稳定性】五节点三副本，down掉两个节点，再
#                  配置下发，配置下发成功
#######################################################

import os

import utils_path
import common
import quota_common
import prepare_clean
from multiprocessing import Process, Value

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
def create_quota_when_down_node():
    count = 10
    success_count = 0
    auth_provider_id = quota_common.get_auth_provider_id_with_access_zone_name(quota_common.QUOTA_ACCESS_ZONE)

    for i in range(1, count + 1):
        dir = "%s%s" % (quota_common.QUOTA_PATH, i)
        quota_common.creating_dir(quota_common.CLIENT_IP_1, dir)
        quota_dir = os.path.basename(dir)
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
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
        if check_result["err_no"] == 0:
            success_count = success_count + 1

        quota_dir = os.path.basename(dir)
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                         auth_provider_id=auth_provider_id,
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_suggest_threshold=1000,
                                                         filenr_soft_threshold=2000,
                                                         filenr_grace_time=1,
                                                         filenr_hard_threshold=3000,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_suggest_threshold=1073741824,
                                                         logical_soft_threshold=2147483648,
                                                         logical_grace_time=1,
                                                         logical_hard_threshold=3221225472,
                                                         user_type='USERTYPE_USER',
                                                         user_or_group_name='quota_user')
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)
        if check_result["err_no"] == 0:
            success_count = success_count + 1

        quota_dir = os.path.basename(dir)
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                         auth_provider_id=auth_provider_id,
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_suggest_threshold=1000,
                                                         filenr_soft_threshold=2000,
                                                         filenr_grace_time=1,
                                                         filenr_hard_threshold=3000,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_suggest_threshold=1073741824,
                                                         logical_soft_threshold=2147483648,
                                                         logical_grace_time=1,
                                                         logical_hard_threshold=3221225472,
                                                         user_type='USERTYPE_GROUP',
                                                         user_or_group_name='quota_group')
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)
        if check_result["err_no"] == 0:
            success_count = success_count + 1

    # 结果检查
    print success_count
    if success_count != 30:
        raise Exception("create_quota_when_down_node is failed")
    return


def down_second_node_when_create_quota():
    cmd = "echo b > /proc/sysrq-trigger"
    # 注意：down的节点不能是脚本执行的节点
    node = common.Node()
    node_ids = node.get_nodes_id()
    node_ip_last = node.get_node_ip_by_id(node_ids[4])
    rc, stdout = common.run_command(node_ip_last, cmd)
    print "print_except_stderr: \n%s" % stdout
    return


def down_third_node_when_create_quota():
    cmd = "echo b > /proc/sysrq-trigger"
    # 注意：down的节点不能是脚本执行的节点
    node = common.Node()
    node_ids = node.get_nodes_id()
    node_ip_last = node.get_node_ip_by_id(node_ids[3])
    rc, stdout = common.run_command(node_ip_last, cmd)
    print "print_except_stderr: \n%s" % stdout
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

    # 三副本，down后两个节点，第一个节点用于创建配额
    p1 = Process(target=create_quota_when_down_node, args=())
    p2 = Process(target=down_second_node_when_create_quota, args=())
    p3 = Process(target=down_third_node_when_create_quota, args=())

    p1.start()
    p2.start()
    p3.start()

    p1.join()

    if p1.exitcode != 0:
        raise Exception("11-3-1-8 Failed")
    else:
        print "11-3-1-8 Succeed"
    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    print "（1）preparing_environment"

    quota_common.preparing_zone_nas()
    auth_provider_id_1 = quota_common.get_auth_provider_id_with_access_zone_name(quota_common.QUOTA_ACCESS_ZONE)
    quota_common.create_designated_quota_user_and_group_new(quota_common.CLIENT_IP_1, auth_provider_id_1)

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


class Quota_Class_11_3_1_8():
    def quota_method_11_3_1_8(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
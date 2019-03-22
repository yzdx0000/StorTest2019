# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-3-1-9 【稳定性】配置下发过程中主oPara节点部分网
#                  络故障
# 修改时间：20181109 duyuli:修改多进程数据处理逻辑
#######################################################

import os
from multiprocessing import Process
import multiprocessing

import utils_path
import log
import common
import make_fault
import quota_common
import prepare_clean


FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字


def create_quota_when_partial_data_net_fault():
    count = 1
    success_count = 0
    auth_provider_id = quota_common.get_auth_provider_id_with_access_zone_name(quota_common.QUOTA_ACCESS_ZONE)

    for i in range(1, count + 1):
        dir = "%s%s" % (quota_common.QUOTA_PATH, i)
        log.info(dir)
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
    log.info(success_count)
    if success_count != 3:
        raise Exception("create_quota_when_partial_data_net_fault is failed")
    return


def partial_data_net_fault_when_create_quota(my_list, process_name):
    # 进程名 -> 节点id -> 节点管理ip -> 节点业务ip
    # 获取主oPara进程所在节点的id
    process_node_id = quota_common.get_master_process_node_id(process_name)
    if process_node_id != 250:
        # 获取主oPara进程所在的节点的管理ip
        node_manage_ip = quota_common.get_node_ip_by_id(process_node_id)
        my_list.append(node_manage_ip)
    else:
        log.info("process_name is wrong!")
        raise Exception("get_managerip_failed")

    # 获取故障节点的数据ip
    cmd = "ifconfig | grep \"inet 20.\""
    rc, stdout = common.run_command(node_manage_ip, cmd)
    common.judge_rc(rc, 0, "quota_11-3-1-9 failed", exit_flag=False)

    # 获取20网段的数据ip
    data_ip_20_net = stdout.split()[1]
    log.info(data_ip_20_net)

    # 根据ip获取网口名称
    cmd = "ip a| grep %s" % (data_ip_20_net)
    rc, stdout = common.run_command(node_manage_ip, cmd)
    common.judge_rc(rc, 0, "get_ifc_failed", exit_flag=False)

    eth_name = stdout.split()[-1]
    log.info(eth_name)
    my_list.append(eth_name)

    # 根据网口名称down网口
    rc = make_fault.down_eth(node_manage_ip, eth_name)
    common.judge_rc(rc, 0, "down_ifc_failed", exit_flag=False)

    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    log.info("（2）executing_case")
    mylist = multiprocessing.Manager().list()  # 多进程之间全局变量不共享
    '''
    1、测试执行
    2、结果检查
    '''
    # 测试执行

    p1 = Process(target=create_quota_when_partial_data_net_fault, args=())
    p2 = Process(target=partial_data_net_fault_when_create_quota, args=(mylist, "oPara"))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    # 根据网口名称up网口来恢复网络环境
    rc = make_fault.up_eth(mylist[0], mylist[1])
    common.judge_rc(rc, 0, "up_ifc_failed", exit_flag=False)

    # 结果检查
    if p1.exitcode != 0:
        raise Exception("11-3-1-9 Failed")
    else:
        log.info("11-3-1-9 Succeed")
    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    log.info("（1）preparing_environment")

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


class Quota_Class_11_3_1_9():
    def quota_method_11_3_1_9(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)
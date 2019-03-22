# -*-coding:utf-8 -*
import os
import utils_path
import log
import common
import get_config
import prepare_clean
import get_config_job_fault
import job_fault_common
from multiprocessing import Process

#######################################################
# 函数功能：高可用job故障测试
# 脚本作者：duyuli
# 日期：2019-01-11
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)
job_names = [
               # "create_node_pools_proportion",  # 4
               # "create_node_pools_replica",     # 5
               #"create_storage_pool",           # 7
               # "update_create_node_pools",      # 6
               # "expand_storage_pool",           # 8
               "create_volumes",                 # 10
               "create_client_auth",            # 13
               "update_client_auth",            # 16
               "delete_client_auth",            # 17
               "create_access_zone",            # 21
               "enable_nas",                    # 34
               "create_subnet",                 # 24
               "add_vip_address_pool",          # 27
               "create_auth_group",             # 30
               "create_auth_user",              # 30
               "create_ftp_export",             # 31
               "create_nfs_export",             # 32
               "create_smb_export",             # 33
               "update_vip_address_pool",       # 28
               "update_subnet",                 # 25
               "delete_vip_address_pool",       # 29
               "delete_subnet",                 # 26
               "update_access_zone",            # 22
               "disable_nas",                   # 34
               "delete_access_zone",            # 23
               "update_volume",                 # 11
               "delete_volumes",                # 12
               "delete_storage_pool",           # 9
            ]

def make_fault_1(job_name, stage, check_env=True):
    """拔数据盘故障，不触发被动重建"""
    log.info("start to make fault: %s:%s:%s" % (job_name, stage, 1))
    prepare_clean.test_prepare(FILE_NAME, env_check=check_env)

    p1 = Process(target=job_fault_common.job_pscli, args=(job_name,))

    # 添加job pending，并执行job
    job_fault_common.pscli_add_force_pending_strategy(job_name, stage)
    p1.start()
    job_fault_common.check_job_pending_phase(job_name, stage)
    disk_info_list = job_fault_common.make_fault_disk_pullout("DATA", rebuilding=False)
    job_fault_common.pscli_remove_force_pending_strategy(job_name)
    p1.join()

    # 恢复故障1的环境
    job_fault_common.make_fault_disk_insert(disk_info_list[0], disk_info_list[1],
                                            disk_info_list[2], disk_info_list[3],
                                            disk_info_list[4], "DATA", rebuilding=False)

    return p1.exitcode

def make_fault_2(job_name, stage, check_env=True):
    """拔数据盘故障，触发被动重建"""
    log.info("start to make fault: %s:%s:%s" % (job_name, stage, 2))
    prepare_clean.test_prepare(FILE_NAME, env_check=check_env)
    p2 = Process(target=job_fault_common.job_pscli, args=(job_name,))

    # 添加job pending，并执行job
    job_fault_common.pscli_add_force_pending_strategy(job_name, stage)
    p2.start()
    job_fault_common.check_job_pending_phase(job_name, stage)
    disk_info_list = job_fault_common.make_fault_disk_pullout("DATA")
    job_fault_common.pscli_remove_force_pending_strategy(job_name)
    p2.join()

    # 恢复故障2的环境
    job_fault_common.make_fault_disk_insert(disk_info_list[0], disk_info_list[1],
                                            disk_info_list[2], disk_info_list[3],
                                            disk_info_list[4], "DATA")

    return p2.exitcode

def make_fault_3(job_name, stage, check_env=True):
    """拔元数据盘故障，触发被动重建"""
    log.info("start to make fault: %s:%s:%s" % (job_name, stage, 3))
    prepare_clean.test_prepare(FILE_NAME, env_check=check_env)
    p3 = Process(target=job_fault_common.job_pscli, args=(job_name,))

    job_fault_common.pscli_add_force_pending_strategy(job_name, stage)
    p3.start()
    job_fault_common.check_job_pending_phase(job_name, stage)
    disk_info_list = job_fault_common.make_fault_disk_pullout("SHARED")
    job_fault_common.pscli_remove_force_pending_strategy(job_name)
    p3.join()

    # 恢复故障3的环境
    job_fault_common.make_fault_disk_insert(disk_info_list[0], disk_info_list[1],
                                            disk_info_list[2], disk_info_list[3],
                                            disk_info_list[4], "SHARED")

    return p3.exitcode

def make_fault_4(job_name, stage, check_env=True):
    """节点下电故障，控制虚拟机下电"""
    log.info("start to make fault: %s:%s:%s" % (job_name, stage, 4))
    prepare_clean.test_prepare(FILE_NAME, env_check=check_env)
    p4 = Process(target=job_fault_common.job_pscli, args=(job_name,))

    job_fault_common.pscli_add_force_pending_strategy(job_name, stage)
    p4.start()
    job_fault_common.check_job_pending_phase(job_name, stage)
    node_info_tuple_list = job_fault_common.make_fault_vir_down_node(
        get_config_job_fault.get_node_ip_power_off_list())
    job_fault_common.pscli_remove_force_pending_strategy(job_name)
    p4.join()

    # 恢复故障4的环境
    job_fault_common.make_fault_vir_up_node(node_info_tuple_list)

    return p4.exitcode

def make_fault_5(job_name, stage, check_env=True):
    """节点被动重建"""
    log.info("start to make fault: %s:%s:%s" % (job_name, stage, 5))
    prepare_clean.test_prepare(FILE_NAME, env_check=check_env)
    p5 = Process(target=job_fault_common.job_pscli, args=(job_name,))

    job_fault_common.pscli_add_force_pending_strategy(job_name, stage)
    p5.start()
    job_fault_common.check_job_pending_phase(job_name, stage)
    node_ip = get_config_job_fault.get_node_ip_remove_list()[0]
    job_fault_common.make_fault_remove_node_rebuilding(node_ip)
    job_fault_common.pscli_remove_force_pending_strategy(job_name)
    p5.join()

    # 恢复故障5的环境
    job_fault_common.make_fault_add_node(node_ip)

    return p5.exitcode

def make_fault_6(job_name, stage, check_env=True):
    """主oJmgs故障"""
    log.info("start to make fault: %s:%s:%s" % (job_name, stage, 6))
    prepare_clean.test_prepare(FILE_NAME, env_check=check_env)
    p6 = Process(target=job_fault_common.job_pscli, args=(job_name,))

    job_fault_common.pscli_add_force_pending_strategy(job_name, stage)
    p6.start()
    job_fault_common.check_job_pending_phase(job_name, stage)
    node_ip = job_fault_common.make_fault_master_ojmgs()
    job_fault_common.pscli_remove_force_pending_strategy(job_name)
    p6.join()

    # 恢复故障6的环境
    job_fault_common.make_fault_recover_master_ojmgs(node_ip)

    return p6.exitcode

def make_fault_7(job_name, stage, check_env=True):
    """zk异常"""
    log.info("start to make fault: %s:%s:%s" % (job_name, stage, 7))
    prepare_clean.test_prepare(FILE_NAME, env_check=check_env)
    p7 = Process(target=job_fault_common.job_pscli, args=(job_name,))

    job_fault_common.pscli_add_force_pending_strategy(job_name, stage)
    p7.start()
    job_fault_common.check_job_pending_phase(job_name, stage)
    job_fault_common.make_fault_zk(SYSTEM_IP_1)
    job_fault_common.pscli_remove_force_pending_strategy(job_name)
    p7.join()

    # 恢复故障7的环境
    job_fault_common.make_fault_recover_zk(SYSTEM_IP_1)

    return p7.exitcode

def make_fault_8(job_name, stage, check_env=True):
    """其它进程故障"""
    log.info("start to make fault: %s:%s:%s" % (job_name, stage, 8))
    prepare_clean.test_prepare(FILE_NAME, env_check=check_env)
    p8 = Process(target=job_fault_common.job_pscli, args=(job_name,))

    job_fault_common.pscli_add_force_pending_strategy(job_name, stage)
    p8.start()
    job_fault_common.check_job_pending_phase(job_name, stage)
    node_ip, process_name = job_fault_common.make_fault_other_process_random()
    job_fault_common.pscli_remove_force_pending_strategy(job_name)
    p8.join()

    # 恢复故障8的环境
    job_fault_common.make_fault_recover_other_process(node_ip, process_name)

    return p8.exitcode

def judge_rc(rc, stage_value, job_name, stage, fault_num):
    # 执行成功
    log.info("rc:%s job_name:%s  stage:%s fault_number:%s" % (rc, job_name, stage, fault_num))
    if 0 == rc:
        log.info("%s:%s:%s success" % (job_name, stage, fault_num))

    # 预期成功执行失败
    elif 0 != rc and stage_value.split(",")[1] == "0":
        raise Exception("%s:%s:%s failed !!!!!!!!" % (job_name, stage, fault_num))

    # 预期失败执行失败
    else:
        log.info("%s:%s:%s retry" % (job_name, stage, fault_num))
        prepare_clean.nas_test_clean(fault=True)
        job_fault_common.job_pscli(job_name)
    return


def case():
    stage = get_config_job_fault.get_stage_set()
    for job_name in job_names:
        stage_total = get_config_job_fault.get_job_stages_total(job_name)

        # 若不是高可用 or 阶段数超过总数 则跳过
        if stage_total == 0 or stage > stage_total:
            continue

        # 获取每个job下每个阶段的故障信息
        log.info("%s" % stage)
        stage_value_list = get_config_job_fault.get_job_fault_info(job_name, stage)

        # 开始做故障1(磁盘拔出)
        if stage_value_list[0].split(",")[0] == "YES":
            rc = make_fault_1(job_name, stage)
            judge_rc(rc, stage_value_list[0], job_name, stage, 1)

        # 开始做故障2(磁盘被动重建)
        if stage_value_list[1].split(",")[0] == "YES":
            rc = make_fault_2(job_name, stage)
            judge_rc(rc, stage_value_list[1], job_name, stage, 2)

        # 开始做故障3(元数据盘拔出)
        if stage_value_list[2].split(",")[0] == "YES":
            rc = make_fault_3(job_name, stage)
            judge_rc(rc, stage_value_list[2], job_name, stage, 3)

        # 开始做故障4(节点下电故障)
        if stage_value_list[3].split(",")[0] == "YES":
            rc = make_fault_4(job_name, stage)
            judge_rc(rc, stage_value_list[3], job_name, stage, 4)

        # 开始做故障5(节点被动重建)
        if stage_value_list[4].split(",")[0] == "YES":
            rc = make_fault_5(job_name, stage)
            judge_rc(rc, stage_value_list[4], job_name, stage, 5)

        # 开始做故障6(主oJmgs故障)
        if stage_value_list[5].split(",")[0] == "YES":
            rc = make_fault_6(job_name, stage)
            judge_rc(rc, stage_value_list[5], job_name, stage, 6)

        # 开始做故障7(zk故障)
        if stage_value_list[6].split(",")[0] == "YES":
            rc = make_fault_7(job_name, stage)
            judge_rc(rc, stage_value_list[6], job_name, stage, 7)

        # 开始做故障8(其它进程故障)
#        if stage_value_list[7].split(",")[0] == "YES":
#            rc = make_fault_8(job_name, stage)
#            judge_rc(rc, stage_value_list[7], job_name, stage, 8)

def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

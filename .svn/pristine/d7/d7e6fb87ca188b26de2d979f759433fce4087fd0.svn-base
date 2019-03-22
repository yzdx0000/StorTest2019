# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import make_fault
import get_config
import prepare_clean
import tool_use
import prepare_clean

#################################################################
#
# Author: chenjy1
# Date: 2018-08-27
# @summary：
#    物理机3节点，无业务情况下故障磁盘，无坏对象，触发修复任务
# @steps:
#    1.创建文件
#    2.创建完成后，故障一块盘，触发被动重建
#    3.检查是否有重建任务，是否有修复任务
#    4.恢复环境
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
VDBENCH_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)          # /mnt/volume1/defect_case/qc_436
get_node_stat_rc = 1


def wait_disk_remove(fault_node_id, fault_disk_id):
    """
    Author:                      chenjy1
    :date:                       2018.08.14
    :description:                等待盘被删除掉
    :param fault_node_id:       (int)故障节点ID
    :param fault_disk_id:       (int)故障磁盘ID
    :return:                    (bool)是否删除掉
    """
    obj_disk = common.Disk()
    flag_remove_disk = False
    start_time = time.time()
    while True:
        if obj_disk.check_disk_exist(fault_node_id, fault_disk_id):  # 盘存在则继续等，三分钟后仍存在则退出报错
            time.sleep(10)
            exist_time = int(time.time() - start_time)
            if exist_time > 1200:
                break
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            log.info('disk exist %dh:%dm:%ds' % (h, m, s))
        else:
            flag_remove_disk = True
            log.info("disk have been deleted!")
            break
    return flag_remove_disk


def case():
    log.info("case begin")
    ob_node = common.Node()
    ob_disk = common.Disk()
    ob_storage_pool = common.Storagepool()
    node_id_lst = ob_node.get_nodes_id()
    client_ip_lst = get_config.get_allclient_ip()
    """随机选一个节点"""
    fault_node_id = random.choice(node_id_lst)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)
    """获取故障节点内所有的共享硬盘和数据硬盘"""
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)
    """随机选择一个数据盘"""
    fault_disk_name_lst = random.sample(monopoly_disk_names, 1)
    fault_disk_name = fault_disk_name_lst[0]

    """获取故障盘的scsi id, id, uuid, 盘类型, 存储池id"""
    """物理id"""
    fault_disk_physicalid = ob_disk.get_physicalid_by_name(fault_node_ip, fault_disk_name)
    """id"""
    fault_disk_id = ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name)
    """uuid"""
    fault_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_disk_name)
    """usage"""
    fault_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_disk_name)
    """存储池id"""
    storage_pool_id = ob_disk.get_storage_pool_id_by_diskid(fault_node_id, fault_disk_id)
    log.info("fault_node_id : %s"
             "\nfault_disk_name : %s"
             "\nfault_disk_physicalid : %s"
             "\nfault_disk_uuid : %s"
             "\nfault_disk_usage : %s"
             "\nfault_disk_id : %s"
             "\nstorage_pool_id : %s"
             % (str(fault_node_id),
                fault_disk_name,
                fault_disk_physicalid,
                fault_disk_uuid,
                fault_disk_usage,
                str(fault_disk_id),
                str(storage_pool_id)))
    log.info("1> 创建文件")
    client_ip_lst = get_config.get_allclient_ip()
    ob_vdb = tool_use.Vdbenchrun(depth=1, width=1, files=20, size='500m', threads=15)
    rc = ob_vdb.run_create(VDBENCH_PATH, VDBENCH_PATH, client_ip_lst[0])
    common.judge_rc(rc, 0, "vdbench create file failed")

    log.info('wait 10s')
    time.sleep(10)

    log.info("2> 创建完成后，故障一块盘，触发被动重建")
    """修改重建超时参数"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')
    make_fault.pullout_disk(fault_node_ip, fault_disk_physicalid, fault_disk_usage)

    log.info('wait 50s')
    time.sleep(50)

    log.info("3> 检查是否有重建任务和修复任务")
    start_time = time.time()
    while True:
        disk_state = ob_disk.get_disk_state_by_id(fault_node_id, fault_disk_id)
        if disk_state == "DISK_STATE_REBUILDING_PASSIVE" or disk_state == "DISK_STATE_ZOMBIE":
            log.info('disk state is %s' % disk_state)
            break
        time.sleep(5)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('wait DISK_STATE_REBUILDING_PASSIVE or DISK_STATE_ZOMBIE exist %dh:%dm:%ds now is %s' % (h, m, s, disk_state))

    """等待没有坏对象"""
    prepare_clean.check_func("badobj")

    """查看修复任务"""
    faied_flag = False
    rc, stdout = common.get_jobengine_state()
    common.judge_rc(rc, 0, "get_jobengine_state failed")
    pscli_info = common.json_loads(stdout)
    for job in pscli_info['result']['job_engines']:
        if job['type'] == 'JOB_ENGINE_REPAIR':
            faied_flag = True

    log.info('4> 恢复环境')
    start_time = time.time()
    while True:
        disk_state = ob_disk.get_disk_state_by_id(fault_node_id, fault_disk_id)
        if disk_state == "DISK_STATE_ZOMBIE":
            log.info('disk state is %s' % disk_state)
            break
        time.sleep(5)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('wait DISK_STATE_ZOMBIE exist %dh:%dm:%ds now is %s' % (h, m, s, disk_state))
    """插入磁盘"""
    make_fault.insert_disk(fault_node_ip, fault_disk_physicalid, fault_disk_usage)
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '3600000')
    log.info('wait 60s')
    time.sleep(60)
    """删除磁盘"""
    ob_disk.remove_disks_asyn(fault_disk_id)  # 删除磁盘都用异步，然后检查
    flag_remove_disk = wait_disk_remove(fault_node_id, fault_disk_id)
    common.judge_rc(flag_remove_disk, True, "fault_disk_name: %s remove failed" % fault_disk_name)
    log.info('wait 180s')
    time.sleep(180)
    """加入磁盘并且加入到存储池"""
    ob_disk.add_disks(fault_node_id, fault_disk_uuid, fault_disk_usage)
    fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)
    ob_storage_pool.expand_storage_pool(storage_pool_id, fault_disk_id_new)

    rc, stdout = common.get_node_stat()
    common.judge_rc(rc, get_node_stat_rc, "get_node_stat  failed")

    if faied_flag:
        common.except_exit("JOB_ENGINE_REPAIR exist at that time!")

    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)

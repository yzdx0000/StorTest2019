# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import tool_use
import log
import prepare_clean
import get_config
import make_fault
import event_common
import quota_common


####################################################################################
#
# Author: liyao
# date 2018-08-02
# @summary：
#    硬盘拔出检测
# @steps:
#   1、部署3节点集群环境
#   2、使用echo scsi remove-single-device拔出一块硬盘,同时vdbench进行业务读写
#   3、get_alarms查看告警信息是否正确
#   4、不断检查快对象，等待重建完成后插入磁盘
#   5、删除磁盘再添加
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
EVENT_TRUE_PATH = os.path.join(event_common.EVENT_TEST_PATH, FILE_NAME)
DATA_DIR = os.path.join(EVENT_TRUE_PATH, 'data_dir')                  # /mnt/volume1/event/events_5_3_1_11/data_dir/
CREATE_EVENT_PATH = os.path.join('event', FILE_NAME)                   # /event/events_5_3_6_21
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


def case():
    '''函数执行主体'''
    '''2> 使用echo scsi remove-single-device拔出一块硬盘'''
    '''获取集群内所有节点的id'''
    ob_node = common.Node()
    ob_disk = common.Disk()
    ob_storage_pool = common.Storagepool()
    nodeid_list = ob_node.get_nodes_id()

    '''随机选一个节点'''
    fault_node_id = random.choice(nodeid_list)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    '''获取节点内的所有数据盘的物理id'''
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)
    """随机获取一个数据盘"""
    fault_disk_name = random.choice(monopoly_disk_names)
    fault_disk_physical_id = ob_disk.get_physicalid_by_name(fault_node_ip, fault_disk_name)
    fault_disk_id = ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name)
    fault_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_disk_name)
    fault_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_disk_name)
    storage_pool_id = ob_disk.get_storage_pool_id_by_diskid(fault_node_id, fault_disk_id)

    '''更新磁盘重建的等待时间'''
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')
    p1 = Process(target=tool_use.vdbench_run, args=(EVENT_TRUE_PATH, SYSTEM_IP_0, SYSTEM_IP_1),
                 kwargs={'run_create': True, 'run_check_write': True})
    p2 = Process(target=make_fault.pullout_disk, args=(fault_node_ip, fault_disk_physical_id, fault_disk_usage))
    p1.daemon = True
    p1.start()
    time.sleep(10)
    p2.start()

    # p1.join()  不需要等待p1完成，主进程结p1就退出
    p2.join()

    '''3> 循环检测告警信息是否正确'''
    code = '0x01020030'
    description = 'One or more disks are pulled out !!'
    event_common.check_alarms_result(code, description)

    # 恢复环境
    '''4> 不断检查坏对象，等待重建完成'''
    start_time = time.time()
    while True:
        if common.check_rebuild_job() is False:
            log.info('rebuild job finish!!!')
            break
        time.sleep(20)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('rebuild job exist %dh:%dm:%ds' % (h, m, s))

    """插入磁盘"""
    make_fault.insert_disk(fault_node_ip, fault_disk_physical_id, fault_disk_usage)
    '''
    log.info('wait 60s')
    time.sleep(60)

    # 5> 删除磁盘再添加
    """插入磁盘"""
    make_fault.insert_disk(fault_node_ip, fault_disk_physical_id, fault_disk_usage)

    log.info('wait 60s')
    time.sleep(60)
    '''

    log.info('wait 180s')
    time.sleep(180)

    # 恢复环境
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '3600000')
    '''
    if p1.exitcode != 0:
        raise Exception("vdbench is failed!!!!!!")
    '''

    """删除磁盘"""
    ob_disk.remove_disks(fault_disk_id)

    # 不断检查坏对象是否修复
    count = 0
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 60 seconds")
        time.sleep(60)
        if common.check_badjobnr():
            break

    """检查磁盘的状态是否正常"""
    if common.check_alldisks_health():
        raise Exception("some disks is not health")

    """加入磁盘,并且加入存储池"""
    ob_disk.add_disks(fault_node_id, fault_disk_uuid, fault_disk_usage)
    fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)
    rc, out = ob_storage_pool.expand_storage_pool(storage_pool_id, fault_disk_id_new)
    common.judge_rc(rc, 0, "expand storage pool failed")

    '''
    # 再跑检查数据的正确性
    tool_use.vdbench_run(EVENT_TRUE_PATH, SYSTEM_IP_1, SYSTEM_IP_2, run_check=True)
    '''

    '''检查系统'''
    common.ckeck_system()

    log.info("case succeed!")

    return


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=True)
    quota_common.creating_dir(SYSTEM_IP_0, EVENT_TRUE_PATH)
    case()
    prepare_clean.test_clean()
    common.rm_exe(SYSTEM_IP_0, os.path.join(quota_common.BASE_QUOTA_PATH, 'event'))
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

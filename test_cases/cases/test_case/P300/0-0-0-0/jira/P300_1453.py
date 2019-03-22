# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import tool_use
import make_fault
import get_config
import prepare_clean

#################################################################
#
# Author: baorb
# Date: 2018-08-07
# @summary：
#    本测试主要测试拔盘测试，进行重建并且同时kill oPara进程。
# @steps:
#    1, 修改磁盘重建等待时间
#    2，使用vdbench创建文件和数据校验
#    3，同时在一个节点上每隔5分钟随机拔出插入一块数据盘，同时kill oPara进程
#
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
DEFECT_TRUE_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)      # /mnt/volume1/defect_case/P300_1453

session_list = ['oJmgs', 'oMgcd', 'oPara', 'oStor', 'oJob', 'oRole', 'zk']


def kill_process(node_ip):
    """
    进行kill 进程故障
    :param node_ip:
    :return:
    """
    time.sleep(10)
    while True:
        session = 'oPara'
        make_fault.kill_process(node_ip, session)
        time.sleep(120)


def case():
    log.info("----------case----------")
    '''随机选取集群内的一个节点，获取节点的数据盘的物理id'''
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

    client_ip_lst = get_config.get_allclient_ip()

    '''更新磁盘重建的等待时间'''
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')

    p1 = Process(target=tool_use.vdbench_run, args=(DEFECT_TRUE_PATH, client_ip_lst[0], client_ip_lst[1]),
                 kwargs={'run_create': True, 'run_check_write': True})
    p2 = Process(target=make_fault.pullout_disk, args=(fault_node_ip, fault_disk_physical_id, fault_disk_usage))
    p3 = Process(target=kill_process, args=(fault_node_ip,))

    p1.start()
    time.sleep(10)
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.terminate()
    p3.join()

    log.info('wait 60s')
    time.sleep(60)

    """不断检查重建任务是否存在"""
    start_time = time.time()
    while True:
        if not common.check_rebuild_job():
            log.info('rebuild job finish!!!')
            break
        time.sleep(20)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('rebuild job exist %dh:%dm:%ds' % (h, m, s))

    """插入磁盘"""
    make_fault.insert_disk(fault_node_ip, fault_disk_physical_id, fault_disk_usage)

    log.info('wait 60s')
    time.sleep(60)

    """删除磁盘"""
    ob_disk.remove_disks(fault_disk_id)

    log.info('wait 180s')
    time.sleep(180)

    """加入磁盘,并且加入存储池"""
    ob_disk.add_disks(fault_node_id, fault_disk_uuid, fault_disk_usage)
    fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)
    ob_storage_pool.expand_storage_pool(storage_pool_id, fault_disk_id_new)

    '''将等待时间的参数修改回来'''
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '18000000')

    common.judge_rc(p1.exitcode, 0, 'vdbench_run')

    '''不断检查坏对象是否修复'''
    count = 0
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 60 seconds")
        time.sleep(60)
        if common.check_badjobnr():
            break

    '''再跑检查数据的正确性'''
    tool_use.vdbench_run(DEFECT_TRUE_PATH, client_ip_lst[0], client_ip_lst[1], run_check=True)

    """不断检查进程是否起来"""
    for i in range(9):
        log.info("wait 20 s")
        time.sleep(20)
        if make_fault.check_process(fault_node_ip, 'oPara'):
            log.info('node %s process oPara is not normal!!!' % fault_node_ip)
            break
    else:
        raise Exception("node %s process oPara is not normal 180s" % fault_node_ip)

    '''检查系统'''
    common.ckeck_system()
    log.info("case succeed!")


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)
# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import snap_common
import log
import tool_use
import prepare_clean
import get_config
import make_fault

####################################################################################
#
# author:baoruobing
# date 2018-07-17
# @summary：
#      对同一节点的两块数据盘进行拔盘操作，一块不等重建就插入，一块被动重建完成后将磁盘插回
# @steps:
#    1、部署3节点集群，配比4 2 1；
#    2、使用iozone创建多个文件；
#    3、vdbench创建数据过程中，拔出一个节点的两块数据盘；
#    4、被动重建完成后，将磁盘插回；
#    5、恢复等待重建的时间，清理数据；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
MINI_TRUE_PATH = os.path.join(prepare_clean.MINICASE_PATH, FILE_NAME)      # /mnt/volume1/mini_case/3_0015_truncate_test


def random_disk_fault(node_ip, disk_scsi_id):
    """
    :author:      baoruobing
    :date  :      2018.04.17
    :description: 随机拔出插入一块数据盘
    :param node_ip:
    :param disk_scsi_id:
    :return:
    """
    for i in range(3):
        make_fault.pullout_disk(node_ip, disk_scsi_id, 'DATA')
        time.sleep(10)
        make_fault.insert_disk(node_ip, disk_scsi_id, 'DATA')
        time.sleep(120)
    return


def case():
    """更新磁盘重建的等待时间"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')

    # 2> 使用iozone创建多个文件
    # 添加文件
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, str(i))
        cmd = ("iozone -s 1m -i 0 -f %s -w" % test_file)
        rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
        if rc != 0:
            log.error("Execute command: \"%s\" failed. \nstdout: %s " % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s " % (cmd, stdout))

    # 3> 拔出一个节点的两块数据盘
    ''' 随机选取集群内的一个节点，获取节点的数据盘的物理id'''
    '''获取集群内所有节点的id'''
    ob_node = common.Node()
    ob_disk = common.Disk()
    ob_storage_pool = common.Storagepool()
    node_id_lst = ob_node.get_nodes_id()

    client_ip_lst = get_config.get_allclient_ip()

    '''随机选一个节点'''
    fault_node_id = random.choice(node_id_lst)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    '''获取故障节点内所有的共享硬盘和数据硬盘'''
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)

    fault_disk_name_no_rebuild = random.choice(monopoly_disk_names)
    while True:
        fault_disk_name_tem = random.choice(monopoly_disk_names)
        if fault_disk_name_tem != fault_disk_name_no_rebuild:
            fault_disk_name_rebuild = fault_disk_name_tem
            break

    fault_disk_scsiid_no_rebuild = ob_disk.get_physicalid_by_name(fault_node_ip, fault_disk_name_no_rebuild)

    fault_disk_scsiid_rebuild = ob_disk.get_physicalid_by_name(fault_node_ip, fault_disk_name_rebuild)
    fault_disk_id_rebuild = ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name_rebuild)
    fault_disk_uuid_rebuild = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_disk_name_rebuild)
    fault_disk_usage_rebuild = ob_disk.get_disk_usage_by_name(fault_node_id, fault_disk_name_rebuild)
    storage_pool_id_rebuild = ob_disk.get_storage_pool_id_by_diskid(fault_node_id, fault_disk_id_rebuild)

    p1 = Process(target=tool_use.vdbench_run, args=(MINI_TRUE_PATH, client_ip_lst[0], client_ip_lst[1]),
                 kwargs={'run_create': True, 'run_check_write': True})
    p2 = Process(target=random_disk_fault, args=(fault_node_ip, fault_disk_scsiid_no_rebuild))
    p3 = Process(target=make_fault.pullout_disk, args=(fault_node_ip, fault_disk_scsiid_rebuild,
                                                       fault_disk_usage_rebuild))

    p1.start()
    time.sleep(10)
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()

    """不断检查重建任务是否存在"""
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
    make_fault.insert_disk(fault_node_ip, fault_disk_scsiid_rebuild, fault_disk_usage_rebuild)

    log.info('wait 60s')
    time.sleep(60)

    """删除磁盘"""
    ob_disk.remove_disks(fault_disk_id_rebuild)

    log.info('wait 180s')
    time.sleep(180)

    """加入磁盘,并且加入存储池"""
    rc, stdout = ob_disk.add_disks(fault_node_id, fault_disk_uuid_rebuild, fault_disk_usage_rebuild)
    common.judge_rc(rc, 0, 'add_disks failed')
    fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid_rebuild)
    rc, stdout = ob_storage_pool.expand_storage_pool(storage_pool_id_rebuild, fault_disk_id_new)
    common.judge_rc(rc, 0, 'expand_storage_pool failed')

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
        if common.check_badjobnr() is True:
            break

    '''再跑检查数据的正确性'''
    tool_use.vdbench_run(MINI_TRUE_PATH, client_ip_lst[0], client_ip_lst[1], run_check=True)
    '''检查系统'''
    common.ckeck_system()

    log.info("case succeed!")


def main():
    prepare_clean.minicase_test_prepare(FILE_NAME)
    case()
    prepare_clean.minicase_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
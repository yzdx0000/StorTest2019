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
import make_fault

####################################################################################
#
# author:liyao
# date 2018-07-17
# @summary：
#      对同一节点的两块数据盘进行拔盘操作，被动重建完成后将磁盘插回
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


def pullout_disks(node_ip, disk_id_lst):
    """
    随机拔出插入两块数据盘
    :param node_ip:
    :param disk_id_lst:
    :return:
    """
    log.info('waiting for 10s')
    time.sleep(10)
    for disk_id in disk_id_lst:
        make_fault.pullout_disk(node_ip, disk_id, 'DATA')
    log.info('waiting for 10s')
    time.sleep(10)
    return


def insert_disks(node_ip, disk_id_lst):
    log.info('waiting for 10s')
    time.sleep(10)
    for disk_id in disk_id_lst:
        make_fault.insert_disk(node_ip, disk_id, 'DATA')
    log.info('waiting for 10s')
    time.sleep(10)
    return


def case():
    """更新磁盘重建的等待时间"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')

    # 2> 使用iozone创建多个文件
    # 添加文件
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, '%d' % i)
        cmd = ("iozone -s 1m -i 0 -f %s -w" % test_file)
        log.info(cmd)
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

    '''随机选一个节点'''
    fault_node_id = random.choice(node_id_lst)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    '''获取故障节点内所有的共享硬盘和数据硬盘'''
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)
    """随机选择两个数据盘"""
    fault_disk_name_lst = random.sample(monopoly_disk_names, 2)
    """获取故障盘的scsi id, id, uuid, 盘类型, 存储池id"""
    fault_disk_physicalid_lst = []
    fault_disk_id_lst = []
    fault_disk_uuid_lst = []
    fault_disk_usage_lst = []
    storage_pool_id_lst = []
    for fault_disk_name in fault_disk_name_lst:
        """物理id"""
        fault_disk_physicalid = ob_disk.get_physicalid_by_name(fault_node_ip, fault_disk_name)
        fault_disk_physicalid_lst.append(fault_disk_physicalid)
        """id"""
        fault_disk_id = ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name)
        fault_disk_id_lst.append(fault_disk_id)
        """uuid"""
        fault_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_disk_name)
        fault_disk_uuid_lst.append(fault_disk_uuid)
        """usage"""
        fault_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_disk_name)
        fault_disk_usage_lst.append(fault_disk_usage)
        """存储池id"""
        storage_pool_id = ob_disk.get_storage_pool_id_by_diskid(fault_node_id, fault_disk_id)
        storage_pool_id_lst.append(storage_pool_id)

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

    '''随机拔除一个节点的两个数据盘 '''
    p1 = Process(target=tool_use.vdbench_run, args=(MINI_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2),
                 kwargs={'run_create': True, 'run_check_write': True})
    p2 = Process(target=pullout_disks, args=(fault_node_ip, fault_disk_physicalid_lst))
    p1.start()
    p2.start()

    p1.join()
    p2.join()

    common.judge_rc(p1.exitcode, 0, 'vdbench_run')

    # 4> 被动重建完成后，将磁盘插回；删除僵尸状态的磁盘，并再次添加
    log.info('wait 90s')
    time.sleep(90)

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

    """将磁盘重新插入"""
    insert_disks(fault_node_ip, fault_disk_physicalid_lst)

    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '3600000')

    """删除磁盘"""
    for fault_disk_id in fault_disk_id_lst:
        ob_disk.remove_disks(fault_disk_id)

    log.info('wait 180s')
    time.sleep(180)

    """加入磁盘,并且加入存储池"""
    for i in range(len(fault_disk_id_lst)):
        rc, stdout = ob_disk.add_disks(fault_node_id, fault_disk_uuid_lst[i], fault_disk_usage_lst[i])
        common.judge_rc(rc, 0, 'add_disks failed')
        fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid_lst[i])
        rc, stdout = ob_storage_pool.expand_storage_pool(storage_pool_id_lst[i], fault_disk_id_new)
        common.judge_rc(rc, 0, 'expand_storage_pool failed')

    '''再跑检查数据的正确性'''
    tool_use.vdbench_run(MINI_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_check=True)

    return


def main():
    prepare_clean.minicase_test_prepare(FILE_NAME)
    case()
    prepare_clean.minicase_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)

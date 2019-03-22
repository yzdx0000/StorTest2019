# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import log
import common
import tool_use
import snap_common
import prepare_clean
import make_fault

####################################################################################
#
# author:liyao
# date 2018-07-17
# @summary：
#      对同一节点的两块数据盘进行拔盘后直接插入的操作
# @steps:
#    1、部署3节点集群，配比4 2 1；
#    2、使用iozone创建多个文件；
#    3、使用vdbench创建数据过程中，拔出一个节点的两块数据盘，随后立刻插回（不触发被动重建）；
#    4、恢复等待重建的时间，清理数据；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
MINI_TRUE_PATH = os.path.join(prepare_clean.MINICASE_PATH, FILE_NAME)      # /mnt/volume1/mini_case/3_0015_truncate_test


def random_disk_fault(node_ip, disk_scsi_id_lst):
    """
    随机拔出插入一块数据盘
    :param node_ip:
    :param disk_scsi_id_lst:
    :return:
    """
    time.sleep(10)

    for i in range(5):
        for disk_scsi_id in disk_scsi_id_lst:
            make_fault.pullout_disk(node_ip, disk_scsi_id, 'DATA')
        time.sleep(30)
        for disk_scsi_id in disk_scsi_id_lst:
            make_fault.insert_disk(node_ip, disk_scsi_id, 'DATA')
        time.sleep(30)


def case():
    """更新磁盘重建的等待时间"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '18000000')

    # 2> 使用iozone创建多个文件
    """添加文件"""
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, '%d' % i)
        cmd = ("iozone -s 1m -i 0 -f %s -w" % test_file)
        log.info(cmd)
        rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
        common.judge_rc(rc, 0, 'iozone %s' % test_file)

    # 3> 拔出一个节点的两块数据盘，随后立刻插回（不触发被动重建）
    ''' 随机选取集群内的一个节点，获取节点的数据盘的物理id'''
    '''获取集群内所有节点的id'''
    ob_node = common.Node()
    ob_disk = common.Disk()
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
    for fault_disk_name in fault_disk_name_lst:
        """物理id"""
        fault_disk_physicalid = ob_disk.get_physicalid_by_name(fault_node_ip, fault_disk_name)
        fault_disk_physicalid_lst.append(fault_disk_physicalid)

        log.info("fault_node_id : %s"
                 "\nfault_disk_name : %s"
                 "\nfault_disk_physicalid : %s"
                 % (str(fault_node_id),
                    fault_disk_name,
                    fault_disk_physicalid))

    '''vdbench创建数据过程中，随机拔除一个节点的两个数据盘 '''
    p1 = Process(target=tool_use.vdbench_run, args=(MINI_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2),
                 kwargs={'run_create': True, 'run_check_write': True})
    p2 = Process(target=random_disk_fault, args=(fault_node_ip, fault_disk_physicalid_lst))
    p1.start()
    p2.start()

    p1.join()
    p2.join()

    common.judge_rc(p1.exitcode, 0, 'vdbench_run')
    common.judge_rc(p2.exitcode, 0, 'pullout disks')

    '''不断检查坏对象是否修复'''
    count = 0
    log.info("wait 60 seconds")
    time.sleep(60)
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 10 seconds")
        time.sleep(10)
        if common.check_badjobnr():
            break

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
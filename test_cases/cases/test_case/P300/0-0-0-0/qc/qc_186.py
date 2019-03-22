# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import subprocess
import random

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean
import tool_use
import make_fault


####################################################################################
#
# Author: chenjy1
# Date: 2018-07-12
# @summary：
#    iozone和vdbench读写过程中，拔一块数据盘，导致iozone和vdbench校验错误
# @steps:
#    1、跑iozone 3节点，分别执行50线程1g文件，执行所有-i操作
#    2、跑vdbench 3节点分别操作不同的目录总数据量500g，执行读写操作
#    3、读写过程中，通过lsscsi拔出一块数据盘后插入
#    4、vdbench检验数据
#  @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                      # 本脚本名字
# /mnt/volume1/defect_case/qc_186/vdbench
VDBENCH_PATH1 = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME, "vdbench1")
VDBENCH_PATH2 = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME, "vdbench2")
VDBENCH_PATH3 = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME, "vdbench3")
IOZONE_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME, "iozone")      # /mnt/volume1/defect_case/qc_186/iozone
N = 1  # 拔盘循环次数


def vdbench_3node_500g():
    """
    Author:           chenjy1
    :date:            018.08.22
    :description:     vdbench 3节点操作三目录总数据量500g
    :return:
    """
    anchor_path_lst = [VDBENCH_PATH1, VDBENCH_PATH2, VDBENCH_PATH3]
    journal_path_lst = ['/tmp', '/tmp', '/tmp']
    client_ip_lst = get_config.get_allclient_ip()
    # (64k,40,10m,50,15m,10)  depth=2,width=3,files=100,size=(64k,40,200m,50,1g,10)
    vdb = tool_use.Vdbenchrun(depth=2, width=3, files=10, size="(64k,40,10m,50,15m,10)")
    #vdb = tool_use.Vdbenchrun(depth=2, width=3, files=100, size="(64k,40,200m,50,1g,10)")
    rc = vdb.run_create_mulpath(anchor_path_lst, journal_path_lst, client_ip_lst)
    common.judge_rc(rc, 0, "run_create_mulpath failed")

    rc = vdb.run_check_write_mulpath(anchor_path_lst, journal_path_lst, client_ip_lst)
    common.judge_rc(rc, 0, "run_check_write_mulpath failed")
    return rc


def case():
    log.info("case begin")

    '''获取集群节点信息'''
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

    """确认重建超时参数为默认值"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '3600000')

    node_cnt = len(node_id_lst)
    line_per_node = 20
    thread_cnt = line_per_node * len(node_id_lst)
    cmd = "mkdir -p %s" % IOZONE_PATH
    rc, stdout = common.run_command(client_ip_lst[0], cmd)
    common.judge_rc(rc, 0, "IP : %s cmd %s failed" % (client_ip_lst[0], cmd))

    log.info("1> 跑iozone 3节点，分别执行50线程1g文件，执行所有-i操作")
    p1 = Process(target=tool_use.iozone_run, args=(node_cnt, line_per_node, IOZONE_PATH, thread_cnt, '100m', '128k'))
    p1.daemon = True
    p1.start()

    log.info("2、跑vdbench 3节点分别操作不通的目录总数据量500g，执行读写操作")
    p2 = Process(target=vdbench_3node_500g)
    p2.daemon = True
    p2.start()

    log.info('wait 30s')
    time.sleep(30)

    log.info("3> 读写过程中拔盘")
    """循环拔盘插盘"""
    for i in range(N):
        log.info("pullout_disk and insert_disk NO.%d" % i)
        make_fault.pullout_disk(fault_node_ip, fault_disk_physicalid, fault_disk_usage)
        log.info("wait 30s")
        time.sleep(30)
        make_fault.insert_disk(fault_node_ip, fault_disk_physicalid, fault_disk_usage)
        log.info("wait 30s")
        time.sleep(30)

    p1.join()
    p2.join()
    common.judge_rc(p1.exitcode, 0, "vdbench failed")
    common.judge_rc(p2.exitcode, 0, "iozone failed")
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)

# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import tool_use
import get_config
import prepare_clean

#################################################################
#
# author 陈津宇
# date 2018-07-14
# @summary：
#    拔盘故障：单节点一个共享盘一个数据盘，等待重建
# @steps:
#    1，随机选节点和两个盘
#    2，修改超时重建参数
#    3，同时执行：1.跑vdbench 2、拔出两块盘
#    4，检查坏对象和重建任务
#    5，插盘
#    6，删除盘+添加盘
#    7，修回超时重建参数
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
MINI_TRUE_PATH = os.path.join(prepare_clean.MINICASE_PATH, FILE_NAME)      # /mnt/volume1/mini_case/3_0015_truncate_test


def disk_fault_one_share_one_date(node_ip, share_disk_phyid, data_disk_phyid):
    cmd_pullout_share_disk = ("echo scsi remove-single-device %s > /proc/scsi/scsi" % share_disk_phyid)
    cmd_pullout_data_disk = ("echo scsi remove-single-device %s > /proc/scsi/scsi" % data_disk_phyid)
    common.run_command(node_ip, cmd_pullout_share_disk)
    common.run_command(node_ip, cmd_pullout_data_disk)
    time.sleep(10)
    return


def case():
    log.info("case begin")
    # 随机选取集群内的一个节点，获取节点的共享盘的物理id
    # 获取集群内所有节点的id
    ob_node = common.Node()
    ob_disk = common.Disk()
    node_id_lst = ob_node.get_nodes_id()
    # 随机选一个节点
    fault_node_id = random.choice(node_id_lst)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    # 获取一个节点内所有的共享硬盘和数据硬盘
    share_disk_name_list, data_disk_name_list = ob_disk.get_share_monopoly_disk_names(fault_node_id)

    fault_share_disk_name = random.choice(share_disk_name_list)
    fault_data_disk_name = random.choice(data_disk_name_list)

    # 两块故障盘的scsi id, id, uuid, 盘类型
    fault_share_disk_physicalid = ob_disk.get_physicalid_by_name(fault_node_ip, fault_share_disk_name)
    fault_share_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_share_disk_name)
    fault_share_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_share_disk_name)
    fault_share_disk_id = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_share_disk_uuid)

    fault_data_disk_physicalid = ob_disk.get_physicalid_by_name(fault_node_ip, fault_data_disk_name)
    fault_data_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_data_disk_name)
    fault_data_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_data_disk_name)
    fault_data_disk_id = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_data_disk_uuid)
    fault_data_disk_storage_id = ob_disk.get_storage_pool_id_by_diskid(fault_node_id, fault_data_disk_id)

    log.info("fault_node_id : %s"
             "\nfault_share_disk_name : %s"
             "\nfault_share_disk_physicalid : %s"
             "\nfault_share_disk_uuid : %s"
             "\nfault_share_disk_usage : %s"
             "\nfault_share_disk_id : %s"
             "\nfault_data_disk_name : %s"
             "\nfault_data_disk_physicalid : %s"
             "\nfault_data_disk_uuid : %s"
             "\nfault_data_disk_usage : %s"
             "\nfault_data_disk_id : %s"
             % (str(fault_node_id),
                fault_share_disk_name,
                fault_share_disk_physicalid,
                fault_share_disk_uuid,
                fault_share_disk_usage,
                str(fault_share_disk_id),
                fault_data_disk_name,
                fault_data_disk_physicalid,
                fault_data_disk_uuid,
                fault_data_disk_usage,
                str(fault_data_disk_id)))

    # 更新磁盘重建的等待时间
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')

    client_ip_lst = get_config.get_allclient_ip()
    p1 = Process(target=tool_use.vdbench_run, args=(MINI_TRUE_PATH, client_ip_lst[0], client_ip_lst[1]),
                 kwargs={'run_create': True, 'run_check_write': True})
    p2 = Process(target=disk_fault_one_share_one_date,
                 args=(fault_node_ip, fault_share_disk_physicalid, fault_data_disk_physicalid))
    p1.daemon = True
    p2.daemon = True
    p1.start()
    time.sleep(50)
    p2.start()

    p1.join()
    p2.join()

    log.info('wait 90s')
    time.sleep(90)

    # 不断检查重建任务是否存在
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

    # 插上磁盘
    cmd = ("echo scsi add-single-device %s > /proc/scsi/scsi" % fault_share_disk_physicalid)
    common.run_command(fault_node_ip, cmd)
    cmd = ("echo scsi add-single-device %s > /proc/scsi/scsi" % fault_data_disk_physicalid)
    common.run_command(fault_node_ip, cmd)

    log.info('wait 60s')
    time.sleep(60)

    # 更新磁盘重建的等待时间
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '3600000')

    # 删除磁盘
    share_disk_id = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_share_disk_uuid)
    ob_disk.remove_disks(share_disk_id)

    data_disk_id = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_data_disk_uuid)
    ob_disk.remove_disks(data_disk_id)

    log.info('wait 180s')
    time.sleep(180)
    # 磁盘加入到系统
    rc, stdout = ob_disk.add_disks(fault_node_id, fault_share_disk_uuid, "SHARED")
    common.judge_rc(rc, 0, 'add_disks failed')
    rc, stdout = ob_disk.add_disks(fault_node_id, fault_data_disk_uuid, "DATA")
    common.judge_rc(rc, 0, 'add_disks failed')
    fault_data_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_data_disk_uuid)
    ob_storage_pool = common.Storagepool()
    rc, stdout = ob_storage_pool.expand_storage_pool(fault_data_disk_storage_id, fault_data_disk_id_new)
    common.judge_rc(rc, 0, 'expand_storage_pool failed')

    # 检查vdbench运行是否出错
    common.judge_rc(p1.exitcode, 0, 'vdbenck')
    return


def main():
    prepare_clean.minicase_test_prepare(FILE_NAME, check_share_disk_num=True)
    case()
    prepare_clean.minicase_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
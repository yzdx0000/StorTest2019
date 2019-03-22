#!/usr/bin/python
# -*- encoding:utf8 -*-

import sys
import random
import utils_path
import log
import common
import fence_common
import make_fault
import time
import check_if_nextcase
import prepare_clean
import faultrun
import threading
#
# Author: liuyzhb
# date 2019/03/19
# @summary：
#           挑出两个非主zk节点，一个节点kill不影响冗余度的进程，另一个节点拔两块数据盘，zk不切换
# @steps:
#           1、获取一个zk非主节点id
#           2、获取节点的所有数据盘和共享盘信息
#           3、拔数据盘和共享盘
#           4、zk不切换
def prepare():
    prepare_clean.test_prepare(sys.argv[0])
def main():
    log_file_path = log.get_log_path(sys.argv[0])
    log.init(log_file_path, True)
    fence = fence_common.Fence()

    prepare()
    log.info("0> 进行环境准备")
    fence.fence_prepare()

    log.info("1> 获取zk主节点的id")
    rc, before_zkmaster_id= fence.get_master_of_zk()
    common.judge_rc(rc, 0, "get master of zk failed!!!")
    node = common.Node()
    master_ip = node.get_node_ip_by_id(before_zkmaster_id)
    '''
    disk = common.Disk()
    rc, stdout = disk.remove_disks(32)
    rc, stdout = disk.remove_disks(33)
    uuid1 = disk.get_disk_uuid_by_name(1, "/dev/sdd")
    uuid2 = disk.get_disk_uuid_by_name(2, "/dev/sdd")
    uuid3 = disk.get_disk_uuid_by_name(2, "/dev/sde")
    rc, stdout = disk.add_disks(1, uuid1, "DATA")
    rc, stdout = disk.add_disks(2, uuid2, "DATA")
    rc, stdout = disk.add_disks(2, uuid3, "DATA")
    '''
    log.info("2> 选定一个集群中两个非主节点的id")
    node = common.Node()
    node_list = node.get_nodes_id()
    log.info('node_list is %s' % node_list)
    log.info('before_zkmaster_id is %s' % before_zkmaster_id)
    node_list.remove(before_zkmaster_id)
    log.info('slave_node_list is %s' % node_list)
    slave_node_id_list = random.sample(node_list, 2)
    slave_node_ips = []
    for slave_node_id in slave_node_id_list:
        slave_node_ip = node.get_node_ip_by_id(slave_node_id)
        slave_node_ips.append(slave_node_ip)
    log.info('slave_node_id to fault is %s' %slave_node_id_list)
    log.info('slave_node_ips to fault is %s' % slave_node_ips)

    node = common.Node()
    disk= common.Disk()

    log.info("3> 获取非主节点1 的所有数据盘的disk_name，选出两块")
    share_disk_names, monopoly_disk_names = disk.get_share_monopoly_disk_names(slave_node_id_list[0])
    log.info('monopoly_disk_names is %s' % monopoly_disk_names)
    two_monopoly_disk_names = random.sample(monopoly_disk_names, 2)
    log.info('two_monopoly_disk_names is %s' % two_monopoly_disk_names)

    log.info("4> 根据非主节点1的two_monopoly_disk_names获取的disk_id\scsi_id\uuid")
    two_monopoly_disk_ids = []
    two_monopoly_disk_scsi_ids = []
    two_monopoly_uuids = []
    for disk_name in two_monopoly_disk_names:
        disk_id = disk.get_diskid_by_name(slave_node_id_list[0], disk_name)
        ph_scsi_id = disk.get_physicalid_by_name(slave_node_ips[0], disk_name)
        diskuuid = disk.get_disk_uuid_by_name(slave_node_id_list[0], disk_name)
        two_monopoly_disk_ids.append(disk_id)
        two_monopoly_disk_scsi_ids.append(ph_scsi_id)
        two_monopoly_uuids.append(diskuuid)
    log.info('two_monopoly_disk_ids is %s' % two_monopoly_disk_ids)
    log.info('two_monopoly_disk_scsi_ids is %s' % two_monopoly_disk_scsi_ids)
    log.info('two_monopoly_uuids is %s' % two_monopoly_uuids)
    
    t1 = threading.Thread(target=make_fault.data_disk_down_and_up, args=(slave_node_ips[0], two_monopoly_disk_scsi_ids, 2, 5, 300, 10))
    t2 = threading.Thread(target=make_fault.kill_process_and_rename_in_loop, args=(slave_node_ips[1], "oPara", 10, 10))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    log.info("11> 再次查询zk主节点的id")
    rc, after_zkmaster_id = fence.get_master_of_zk()
    common.judge_rc(rc, 0, "get master of zk failed!!!")

    log.info("12> 判断zk的主节点有没有更换")
    if before_zkmaster_id == after_zkmaster_id:
        log.info('id of zk_master not changed,case %s finish success!!!!!' %sys.argv[0])
    else:
        log.error('case %s finish failed,after fault,zk master have been changed,tha is wrong' % sys.argv[0])
        except_exit(None, 1)

    log.info('fence_enable case %s finish success!!!!!' % sys.argv[0])


if __name__=="__main__":
    common.case_main(main)

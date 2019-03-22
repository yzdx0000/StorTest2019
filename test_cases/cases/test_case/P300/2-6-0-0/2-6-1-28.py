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
#
# Author: liuyzhb
# date 2019/03/19
# @summary：
#           將非主节点的数据盘和共享盘全部拔光，zk不切换
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

    log.info("2> 选定一个集群中一个非主节点的id")
    node = common.Node()
    node_list = node.get_nodes_id()
    log.info('node_list is %s' % node_list)
    log.info('before_zkmaster_id is %s' % before_zkmaster_id)
    node_list.remove(before_zkmaster_id)
    log.info('slave_node_list is %s' % node_list)
    slave_node_id = random.sample(node_list, 1)[0]
    slave_node_ip = node.get_node_ip_by_id(slave_node_id)
    log.info('slave_node_id to fault is %d' %slave_node_id)
    '''
    slave_node_id = 2
    '''
    node = common.Node()
    disk= common.Disk()
    slave_node_ip = node.get_node_ip_by_id(slave_node_id)
    #rc, stdout = disk.remove_disks(slave_node_ip)

    log.info("3> 获取非主节点的所有共享盘和数据盘的disk_name")
    share_disk_names, monopoly_disk_names = disk.get_share_monopoly_disk_names(slave_node_id)
    log.info('share_disk_names is %s' %share_disk_names)
    log.info('monopoly_disk_names is %s' % monopoly_disk_names)

    log.info("4> 获取非主节点的所有共享盘和数据盘的disk_id")
    share_disk_ids = []
    monopoly_disk_ids = []
    for disk_name in share_disk_names:
        disk_id = disk.get_diskid_by_name(slave_node_id, disk_name)
        share_disk_ids.append(disk_id)
    for disk_name in monopoly_disk_names:
        disk_id = disk.get_diskid_by_name(slave_node_id, disk_name)
        monopoly_disk_ids.append(disk_id)
    log.info('share_disk_ids is %s' %share_disk_ids)
    log.info('monopoly_disk_ids is %s' % monopoly_disk_ids)

    log.info("5> 获取非主节点的所有共享盘和数据盘的lsscsi的id")
    disk = common.Disk()
    share_ids, ph_ids = disk.get_share_monopoly_disk_physicalid(slave_node_id)
    log.info('share_scsi_ids is %s' % share_ids)
    log.info('monopoly_scsi_ids is %s' % ph_ids)

    log.info("6> 获取非主节点的所有共享盘和数据盘的lsscsi的uuid")
    share_uuids = []
    monopoly_uuids = []
    for disk_name in share_disk_names:
        diskuuid = disk.get_disk_uuid_by_name(slave_node_id, disk_name)
        share_uuids.append(diskuuid)
    for disk_name in monopoly_disk_names:
        diskuuid = disk.get_disk_uuid_by_name(slave_node_id, disk_name)
        monopoly_uuids.append(diskuuid)
    log.info('share_uuids is %s' %share_uuids)
    log.info('monopoly_uuids is %s' % monopoly_uuids)

    log.info("7> 将选定节点上的所有在用的磁盘全部拔掉")
    disk_usage = "SHARED"
    for disk_scsi_id in share_ids:
        make_fault.pullout_disk(slave_node_ip, disk_scsi_id, disk_usage)
    disk_usage = "DATA"
    for disk_scsi_id in ph_ids:
        make_fault.pullout_disk(slave_node_ip, disk_scsi_id, disk_usage)

    log.info("8> 将选定节点上的所有拔掉的磁盘全部插回去")
    disk_usage = "SHARED"
    for disk_scsi_id in share_ids:
        make_fault.insert_disk(slave_node_ip, disk_scsi_id, disk_usage)
    disk_usage = "DATA"
    for disk_scsi_id in ph_ids:
        make_fault.insert_disk(slave_node_ip, disk_scsi_id, disk_usage)

    log.info("9> 将选定节点上的所有磁盘全部delete")
    for disk_id in share_disk_ids:
        rc, stdout = disk.remove_disks(disk_id)
        common.judge_rc(rc,0,"remove diskid %s in node_id %d failed" %(disk_id, slave_node_id ))
    for disk_id in monopoly_disk_ids:
        rc, stdout = disk.remove_disks(disk_id)
        common.judge_rc(rc,0,"remove diskid %s in node_id %d failed" %(disk_id, slave_node_id ))

    log.info("10> 将选定节点上的所有元数据磁盘全部add")
    for uuid in share_uuids:
        rc, stdout = disk.add_disks(slave_node_id, uuid, "SHARED")
        common.judge_rc(rc, 0, "add uuid %s in node_id %d failed" % (uuid, slave_node_id))
    for uuid in monopoly_uuids:
        rc, stdout = disk.add_disks(slave_node_id, uuid, "DATA")
        common.judge_rc(rc, 0, "add uuid %s in node_id %d failed" % (uuid, slave_node_id))
 #

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
    '''
    disk = common.Disk()
    rc, stdout = disk.remove_disks(3)
    rc, stdout = disk.remove_disks(4)
    uuid1 = disk.get_disk_uuid_by_name(1, "/dev/sdd")
    uuid2 = disk.get_disk_uuid_by_name(1, "/dev/sde")
    rc, stdout = disk.add_disks(1, uuid1, "DATA")
    rc, stdout = disk.add_disks(1, uuid2, "DATA")
    '''


if __name__=="__main__":
    common.case_main(main)

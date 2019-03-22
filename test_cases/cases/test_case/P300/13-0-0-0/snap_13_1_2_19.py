# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random
import json

import utils_path
import common
import snap_common
import log
import prepare_clean
import tool_use

####################################################################################
#
# Author: baorb
# date 2018-01-19
# @summary：
#    文件写的过程中删除磁盘，观察快照内容
# @steps:
#    1、部署3节点集群，配比4 2 1；
#    2、在文件目录下/mnt/parastor/snap_parent/创建文件snap_file（使用vdbench创建，文件大小100g）；
#    3、对文件/mnt/parastor/snap_parent/snap_file创建快照a1；
#    4、对文件/mnt/parastor/snap_parent/snap_file使用vdbench进行修改，删除一个节点的一块数据盘；
#    5、对文件/mnt/parastor/.snapshot/a1/snap_file使用vdbench进行数据校验；
#    6、删除快照；
#    7、检查是否有快照路径入口；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0


def case():
    # 2> 运行00脚本
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_create=True)

    #cmd1 = 'scp -r /tmp/vdb_control.file root@%s:/tmp' % snap_common.CLIENT_IP_2
    #cmd2 = 'scp -r /tmp/vdb_control.file root@%s:/tmp' % snap_common.CLIENT_IP_3
    #common.run_command(snap_common.CLIENT_IP_1, cmd1)
    #common.run_command(snap_common.CLIENT_IP_1, cmd2)

    # 3> 对目录创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    '''获取集群内的一个节点,获取节点的所有数据盘的id'''
    fault_node_id = random.choice(node_id_lst)
    ob_disk = common.Disk()
    ob_storage_pool = common.Storagepool()
    '''获取一个节点内所有的共享硬盘和数据硬盘'''
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)
    '''随机获取一个数据盘'''
    fault_disk_name = random.choice(monopoly_disk_names)
    fault_disk_id = ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name)
    fault_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_disk_name)
    storage_pool_id = ob_disk.get_storage_pool_id_by_diskid(fault_node_id, fault_disk_id)
    fault_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_disk_name)

    log.info("fault_node_id : %s"
             "\nfault_disk_name : %s"
             "\nfault_disk_uuid : %s"
             "\nfault_disk_usage : %s"
             "\nfault_disk_id : %s"
             "\nstorage_pool_id : %s"
             % (str(fault_node_id),
                fault_disk_name,
                fault_disk_uuid,
                fault_disk_usage,
                str(fault_disk_id),
                str(storage_pool_id)))

    '''异步删除硬盘'''
    ob_disk.remove_disks_asyn(fault_disk_id)

    # 4> 运行01脚本
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_write=True)

    num = 0
    '''检查硬盘是否删除'''
    while True:
        num += 1
        time.sleep(20)
        if ob_disk.check_disk_exist(fault_node_id, fault_disk_id):
            exist_time = num * 20
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            log.info("disk exist %dh:%dm:%ds!!!" % (h, m, s))
        else:
            log.info("disk deleted!")
            break

    # 加入磁盘
    ob_disk.add_disks(fault_node_id, fault_disk_uuid, fault_disk_usage)

    # 加入存储池
    fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)
    ob_storage_pool.expand_storage_pool(storage_pool_id, fault_disk_id_new)

    # 5> 运行02脚本
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    tool_use.vdbench_run(snap_path, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_check=True)

    # 6> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (path))
        raise Exception('%s delete snapshot failed!!!' % (path))

    time.sleep(10)

    # 7> 3个客户端检查快照路径入口是否存在
    snap_common.check_snap_entry(snap_path)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
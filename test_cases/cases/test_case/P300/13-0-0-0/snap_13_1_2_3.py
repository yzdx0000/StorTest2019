# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

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
#    创建文件快照，拔掉两块数据盘磁盘，观察快照内容创建文件快照，拔掉两块数据盘磁盘，观察快照内容
# @steps:
#    1、部署3节点集群，配比4 2 1；
#    2、客户端1在/mnt/parastor/snap/下跑vdbench 00脚本（vdbench创建文件）；
#    3、对文件/mnt/parastor/snap/snap_file创建快照a1，创建过程中拔出一个节点的两块数据盘；
#    4、对文件/mnt/parastor/snap/snap_file进行修改，内容改为2；
#    5、检查目录/mnt/parastor/.snapshot/下快照a1的数据是否是创建快照时的状态；
#    6、删除快照；
#    7、检查是否有快照路径入口；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0


'''随机拔出插入两块数据盘'''
def pullout_disks(node_ip, disk_id_lst):
    time.sleep(10)
    for disk_id in disk_id_lst:
        cmd = ('ssh %s \"echo scsi remove-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id))
        common.command(cmd)
    time.sleep(10)
    return

def insert_disks(node_ip, disk_id_lst):
    time.sleep(10)
    for disk_id in disk_id_lst:
        cmd = ('ssh %s \"echo scsi add-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id))
        common.command(cmd)
    time.sleep(10)
    return


def case():
    """更新磁盘重建的等待时间"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')

    # 2> 运行00脚本
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_create=True)

    #cmd1 = 'scp -r /tmp/vdb_control.file root@%s:/tmp' % snap_common.CLIENT_IP_2
    #cmd2 = 'scp -r /tmp/vdb_control.file root@%s:/tmp' % snap_common.CLIENT_IP_3
    #common.run_command(snap_common.CLIENT_IP_1, cmd1)
    #common.run_command(snap_common.CLIENT_IP_1, cmd2)

    '''随机选取集群内的一个节点，获取节点的数据盘的物理id'''
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

    pullout_disks(fault_node_ip, fault_disk_physicalid_lst)

    # 3> 对目录创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        #raise Exception('create_snapshot %s failed!!!' % snap_name)

    log.info('wait 90s')
    time.sleep(90)

    '''不断检查坏对象是否修复'''
    count = 0
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 60 seconds")
        time.sleep(60)
        if common.check_badjobnr():
            break

    """将磁盘重新插入"""
    insert_disks(fault_node_ip, fault_disk_physicalid_lst)

    """删除磁盘"""
    for fault_disk_id in fault_disk_id_lst:
        ob_disk.remove_disks(fault_disk_id)

    log.info('wait 180s')
    time.sleep(180)

    """加入磁盘,并且加入存储池"""
    for i in range(len(fault_disk_id_lst)):
        ob_disk.add_disks(fault_node_id, fault_disk_uuid_lst[i], fault_disk_usage_lst[i])
        fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid_lst[i])
        ob_storage_pool.expand_storage_pool(storage_pool_id_lst[i], fault_disk_id_new)

    """恢复磁盘重建的等待时间"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '18000000')

    # 4> 运行01脚本
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_write=True)

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
    path_check = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    snap_common.check_snap_entry(path_check)

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
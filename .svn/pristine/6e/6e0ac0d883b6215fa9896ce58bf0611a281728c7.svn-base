#-*-coding:utf-8 -*

import os
import time
import random
import json

import utils_path
import common
import snap_common
import log
import prepare_clean

####################################################################################
#
# Author: liyao
# date 2018-04-10
#@summary：
#    删除共享磁盘的过程中，创建快照，观察快照内容的正确性
#@steps:
#    1、部署3节点集群，配比4 2 1
#    2、删除一个节点的一块盘，删除过程中对目录/mnt/parastor/snap/和文件/mnt/parastor/snap/test_file1创建快照
#    3、检查文件/mnt/parastor/.snapshot/下快照的数据是否正确
#    4、删除快照
#    5、检查是否有快照路径入口
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/liyao/snap/snap_13_1_2_17
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_1_2_17

def case():
    # 在目录/mnt/liyao/snap_13_1_2_17下创建文件test_file1
    test_file1=os.path.join(SNAP_TRUE_PATH,'test_file1')
    cmd='echo 11111 > %s'% test_file1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 获取并随机拔除某个节点上的共享盘
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    '''获取集群内的一个节点,获取节点的所有数据盘的id'''
    fault_node_id = random.choice(node_id_lst)
    ob_disk = common.Disk()
    '''获取一个节点内所有的共享硬盘和数据硬盘'''
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)
    '''随机获取一个盘'''
    fault_disk_name = random.choice(share_disk_names)
    fault_disk_id = ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name)
    fault_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_disk_name)
    fault_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_disk_name)

    log.info("fault_node_id : %s"
             "\nfault_disk_name : %s"
             "\nfault_disk_uuid : %s"
             "\nfault_disk_usage : %s"
             "\nfault_disk_id : %s"
             % (str(fault_node_id),
                fault_disk_name,
                fault_disk_uuid,
                fault_disk_usage,
                str(fault_disk_id)))

    '''异步删除硬盘'''
    ob_disk.remove_disks_asyn(fault_disk_id)

    time.sleep(30)

    # 对目录/mnt/liyao/snap/snap_13_1_2_17创建快照
    snap_name1=FILE_NAME+'_snapshot1'
    path1=snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name1, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 对文件/mnt/liyao/snap/snap_13_1_2_17/test_file1创建快照
    snap_name2=FILE_NAME+'_snapshot2'
    CREATE_SNAP_PATH2=os.path.join(CREATE_SNAP_PATH,'test_file1')
    path2=snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH2
    rc, stdout = snap_common.create_snapshot(snap_name2, path2)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name2)
        raise Exception('create_snapshot %s failed!!!' % snap_name2)

    # 浏览快照内容
    snap_path1=os.path.join(snap_common.SNAPSHOT_PAHT, snap_name1)
    cmd = 'cat %s' % os.path.join(snap_path1, 'test_file1')
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if '11111' != stdout.strip():
        log.error('%s is not right!!!' % snap_name1)
        raise Exception('%s is not right!!!' % snap_name1)
    snap_path2=os.path.join(snap_common.SNAPSHOT_PAHT, snap_name2)
    cmd='cat %s'% snap_path2
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if '11111' != stdout.strip():
        log.error('%s is not right!!!' % snap_name2)
        raise Exception('%s is not right!!!' % snap_name2)

    num = 0
    '''检查硬盘是否删除'''
    while True:
        num += 1
        time.sleep(20)
        if True == ob_disk.check_disk_exist(fault_node_id, fault_disk_id):
            exist_time = num * 20
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            log.info("disk exist %dh:%dm:%ds!!!" % (h, m, s))
        else:
            log.info("disk deleted!")
            break

    # 加入磁盘
    ob_disk.add_disks(fault_node_id, fault_disk_uuid, fault_disk_usage)

    # 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path1)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (path1))
        raise Exception('%s delete snapshot failed!!!' % (path1))

    time.sleep(10)

    # 三个客户端检查快照入口是否存在
    snap_common.check_snap_entry(snap_path1)
    snap_common.check_snap_entry(snap_path2)

    return

def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
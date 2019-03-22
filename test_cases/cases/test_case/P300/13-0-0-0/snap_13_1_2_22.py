#-*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import snap_common
import log
import prepare_clean

####################################################################################
#
# Author: liyao
# date 2018-04-17
#@summary：
#    对文件创建多个快照，删除数据盘，观察快照内容正确性
#@steps:
#    1、部署3节点集群，配比4 2 1；
#    2、对文件/mnt/parastor/snap/snap_file1（文件大小为10g）创建10个快照，两个快照之间修改文件内容；
#    3、删除一个节点的一块数据盘；
#    4、到目录/mnt/parastor/.snapshot下检查各个快照的数据的正确性；
#    5、删除快照；
#    6、检查是否有快照路径入口；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/liyao/snap/snap_13_1_2_22
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_1_2_22


def case():
    # 创建1g文件
    file_test_1 = os.path.join(SNAP_TRUE_PATH, 'file_test_1')
    cmd = 'dd if=/dev/zero of=%s bs=1M count=1024' % file_test_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    sys_disk = snap_common.get_system_disk(snap_common.CLIENT_IP_1)
    md5_lst_1 = []
    # 2> 创建10个快照
    for i in range(10):
        cmd = 'dd if=%s of=%s bs=1M count=100 seek=%d' % (sys_disk, file_test_1, i*100)
        common.run_command(snap_common.CLIENT_IP_1, cmd)
        # 创建快照
        snap_name = FILE_NAME + '_snapshot_%d' % i
        path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'file_test_1')
        rc, stdout = snap_common.create_snapshot(snap_name, path)
        if 0 != rc:
            log.error('create_snapshot %s failed!!!' % snap_name)
            raise Exception('create_snapshot %s failed!!!' % snap_name)
        # 获取md5值
        md5 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, file_test_1)
        md5_lst_1.append(md5)

    # 3> 删除一块数据盘
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

    time.sleep(20)

    # 检查硬盘是否删除
    num = 0
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

    log.info('wait 60s')
    time.sleep(60)

    # 4> 获取每个快照的md5值
    md5_lst_2 = []
    for i in range(10):
        snap_file = os.path.join(snap_common.SNAPSHOT_PAHT, 'snap_13_1_2_22_snapshot_%d' % i)
        md5 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, snap_file)
        md5_lst_2.append(md5)

    # 加入磁盘
    ob_disk.add_disks(fault_node_id, fault_disk_uuid, fault_disk_usage)

    # 加入存储池
    fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)
    ob_storage_pool.expand_storage_pool(storage_pool_id, fault_disk_id_new)

    # 5> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (FILE_NAME))
        raise Exception('%s delete snapshot failed!!!' % (FILE_NAME))

    if md5_lst_1 != md5_lst_2:
        log.error('md5 is not right!!!')
        raise Exception('md5 is not right!!!')

    time.sleep(10)

    return

def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)

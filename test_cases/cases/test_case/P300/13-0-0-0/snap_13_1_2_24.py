#-*-coding:utf-8 -*
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

####################################################################################
#
# Author: baorb
# date 2018-04-12
#@summary：
#    快照revert的时候，删除数据盘，观察revert数据的正确性
#@steps:
#    1、部署3节点集群，配比4 2 1；
#    2、创建深度为10的目录，每层创建一个快照（每层都有文件）；
#    3、修改所有文件的内容；
#    4、删除一个节点的一块数据盘；
#    5、到目录/mnt/parastor/.snapshot下检查各个快照的数据的正确性；
#    6、删除快照；
#    7、检查是否有快照路径入口；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0


def case():
    # 2> 创建深度为10的目录，每层创建一个文件
    snap_true_path_mem = SNAP_TRUE_PATH
    create_snap_path_mem = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH

    md5_list = []
    for i in range(10):
        # 创建目录
        snap_true_path_mem = os.path.join(snap_true_path_mem, str(i))
        file_name = os.path.join(snap_true_path_mem, 'snap_file')
        cmd = 'mkdir %s' % snap_true_path_mem
        common.run_command(snap_common.CLIENT_IP_1, cmd)
        cmd = 'echo %s > %s' % (str(i)*6, file_name)
        common.run_command(snap_common.CLIENT_IP_1, cmd)
        create_snap_path_mem = os.path.join(create_snap_path_mem, str(i))

        # 获取md5码
        rc, md5sum = snap_common.get_file_md5(snap_common.CLIENT_IP_2, file_name)
        md5_list.append(md5sum)

        # 创建快照
        name = FILE_NAME + '_snapshot_%d' % i
        rc, stdout = snap_common.create_snapshot(name, create_snap_path_mem)
        if 0 != rc:
            log.error('create_snapshot %s failed!!!' % name)
            raise Exception('create_snapshot %s failed!!!' % name)

    # 4> 删除一块数据盘
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

    time.sleep(30)

    # 3> 修改文件内容
    snap_true_path_mem = SNAP_TRUE_PATH
    for i in range(10):
        snap_true_path_mem = os.path.join(snap_true_path_mem, str(i))
        file_name = os.path.join(snap_true_path_mem, 'snap_file')
        cmd = 'echo %s > %s' % (str(i)*20, file_name)
        common.run_command(snap_common.CLIENT_IP_1, cmd)

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

    # 5> 检查快照文件内容
    md5_check_list = []
    for i in range(10):
        snap_name = FILE_NAME + '_snapshot_%d' % i
        snap_file = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name, 'snap_file')
        # 获取md5码
        rc, md5sum = snap_common.get_file_md5(snap_common.CLIENT_IP_2, snap_file)
        md5_check_list.append(md5sum)

    # 加入磁盘
    ob_disk.add_disks(fault_node_id, fault_disk_uuid, fault_disk_usage)

    # 加入存储池
    fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)
    ob_storage_pool.expand_storage_pool(storage_pool_id, fault_disk_id_new)

    # 6> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (FILE_NAME))
        raise Exception('%s delete snapshot failed!!!' % (FILE_NAME))

    md5_list_str = 'source_md5_list: ', md5_list
    md5_check_list_str = 'snap_md5_list: ', md5_check_list
    log.info(md5_list_str)
    log.info(md5_check_list_str)
    if md5_list != md5_check_list:
        log.error('snap file is not right!!!')
        raise Exception('snap file is not right!!!')

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
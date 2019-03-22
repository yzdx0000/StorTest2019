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
# Author: liyao
# date 2018-04-17
#@summary：
#    嵌套目录创建快照，拔掉共享盘，观察快照内容的正确性
#@steps:
#    1、部署3节点集群，配比4 2 1；
#    2、创建深度为10的目录，每层创建一个快照（每层都有文件）；
#    3、修改所有文件的内容；
#    4、拔出一个节点的一块共享盘；
#    5、到目录/mnt/parastor/.snapshot下检查各个快照的数据的正确性；
#    6、删除快照；
#    7、检查是否有快照路径入口；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/liyao/snap/snap_13_1_2_16
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_1_2_16

"""随机拔出插入一块共享盘"""
def pullout_one_disk(node_ip, disk_id):
    time.sleep(10)
    cmd = ('ssh %s \"echo scsi remove-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id))
    common.command(cmd)
    time.sleep(10)
    return

def insert_one_disk(node_ip, disk_id):
    time.sleep(10)
    cmd = ('ssh %s \"echo scsi add-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id))
    common.command(cmd)
    time.sleep(10)
    return

def case():
    """更新磁盘重建的等待时间"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')

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

    '''随机选取集群内的一个节点，获取节点的数据盘的物理id'''
    '''获取集群内所有节点的id'''
    ob_node = common.Node()
    ob_disk = common.Disk()
    node_id_lst = ob_node.get_nodes_id()

    '''随机选一个节点'''
    fault_node_id = random.choice(node_id_lst)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    """获取一个节点内所有的共享硬盘和数据硬盘"""
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)
    """随机获取一个共享盘"""
    fault_disk_name = random.choice(share_disk_names)
    """故障盘的scsi id, id, uuid, 盘类型"""
    fault_disk_physicalid = ob_disk.get_physicalid_by_name(fault_node_ip, fault_disk_name)
    fault_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_disk_name)
    fault_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_disk_name)
    fault_disk_id = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)

    log.info("fault_node_id : %s"
             "\nfault_disk_name : %s"
             "\nfault_disk_physicalid : %s"
             "\nfault_disk_uuid : %s"
             "\nfault_disk_usage : %s"
             "\nfault_disk_id : %s"
             % (str(fault_node_id),
                fault_disk_name,
                fault_disk_physicalid,
                fault_disk_uuid,
                fault_disk_usage,
                str(fault_disk_id)))

    pullout_one_disk(fault_node_ip, fault_disk_physicalid)

    time.sleep(120)

    # 3> 修改文件内容
    snap_true_path_mem = SNAP_TRUE_PATH
    for i in range(10):
        snap_true_path_mem = os.path.join(snap_true_path_mem, str(i))
        file_name = os.path.join(snap_true_path_mem, 'snap_file')
        cmd = 'echo %s > %s' % (str(i)*20, file_name)
        common.run_command(snap_common.CLIENT_IP_1, cmd)


    # 5> 检查快照文件内容
    md5_check_list = []
    for i in range(10):
        snap_name = FILE_NAME + '_snapshot_%d' % i
        snap_file = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name, 'snap_file')
        # 获取md5码
        rc, md5sum = snap_common.get_file_md5(snap_common.CLIENT_IP_2, snap_file)
        md5_check_list.append(md5sum)

    log.info('wait 60s')
    time.sleep(60)

    '''不断检查坏对象是否修复'''
    count = 0
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 60 seconds")
        time.sleep(60)
        if True == common.check_badjobnr():
            break

    """将磁盘重新插入"""
    insert_one_disk(fault_node_ip, fault_disk_physicalid)

    """删除磁盘"""
    ob_disk.remove_disks(fault_disk_id)

    log.info('wait 180s')
    time.sleep(180)

    """磁盘加入到系统"""
    ob_disk.add_disks(fault_node_id, fault_disk_uuid, fault_disk_usage)

    """恢复磁盘重建的等待时间"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '18000000')

    md5_list_str = 'source_md5_list: ', md5_list
    md5_check_list_str = 'snap_md5_list: ', md5_check_list
    log.info(md5_list_str)
    log.info(md5_check_list_str)
    if md5_list != md5_check_list:
        log.error('snap file is not right!!!')
        raise Exception('snap file is not right!!!')

    # 6> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (FILE_NAME))
        raise Exception('%s delete snapshot failed!!!' % (FILE_NAME))

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
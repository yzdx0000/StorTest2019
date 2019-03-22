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
#    创建文件快照，拔掉一块共享盘磁盘，观察快照内容
#@steps:
#    1、部署3节点集群，配比4 2 1；
#    2、在/mnt/parastor/snap/下创建文件snap_file（大小1g，内容为1）；
#    3、对文件/mnt/parastor/snap/snap_file创建快照a1，创建过程中拔出一个节点的一块共享盘；
#    4、对文件/mnt/parastor/snap/snap_file进行修改，内容改为2；
#    5、检查目录/mnt/parastor/.snapshot/下快照a1的数据是否是创建快照时的状态；
#    6、删除快照；
#    7、检查是否有快照路径入口；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/liyao/snap/snap_13_1_2_2
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_1_2_2


def pullout_one_disk(node_ip, disk_id):
    """拔出一块盘"""
    time.sleep(10)
    cmd = ('ssh %s \"echo scsi remove-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id))
    common.command(cmd)
    time.sleep(10)
    return

def insert_one_disk(node_ip, disk_id):
    """插入一块盘"""
    time.sleep(10)
    cmd = ('ssh %s \"echo scsi add-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id))
    common.command(cmd)
    time.sleep(10)
    return


def case():
    """更新磁盘重建的等待时间"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')

    # 2> 创建1g文件
    file_test_1 = os.path.join(SNAP_TRUE_PATH, 'file_test_1')
    cmd = 'dd if=/dev/zero of=%s bs=1M count=1024' % file_test_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 获取md5值
    md5_file = snap_common.get_file_md5(snap_common.CLIENT_IP_1, file_test_1)

    '''随机选取集群内的一个节点，获取节点的共享盘的物理id'''
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

    """拔出共享盘"""
    pullout_one_disk(fault_node_ip, fault_disk_physicalid)

    # 3> 对文件创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH + '/'+ 'file_test_1'
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
        if True == common.check_badjobnr():
            break

    """将磁盘重新插入"""
    insert_one_disk(fault_node_ip, fault_disk_physicalid)

    """删除磁盘"""
    ob_disk.remove_disks(fault_disk_id)

    log.info('wait 180s')
    time.sleep(180)

    """恢复磁盘重建的等待时间"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '3600000')

    """磁盘加入到系统"""
    ob_disk.add_disks(fault_node_id, fault_disk_uuid, fault_disk_usage)

    # 4> 修改文件
    cmd = "echo 'nice to meet you'>> %s" % file_test_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)
    # 获取md5值
    snap_file = os.path.join(snap_common.SNAPSHOT_PAHT, 'snap_13_1_2_2_snapshot1')
    md5_snap = snap_common.get_file_md5(snap_common.CLIENT_IP_1, snap_file)

    # 5> 数据校验
    if md5_snap != md5_file:
        log.error('md5 is not right!!!')
        raise Exception('md5 is not right!!!')

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
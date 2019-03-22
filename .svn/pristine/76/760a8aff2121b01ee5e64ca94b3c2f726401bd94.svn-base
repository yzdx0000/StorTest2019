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
# date 2018-04-16
#@summary：
#    对文件创建多个快照，拔掉共享盘，观察快照内容正确性
#@steps:
#    1、部署3节点集群，配比4 2 1；
#    2、对文件/mnt/parastor/snap/snap_file1（文件大小为1g）创建10个快照，两个快照之间修改文件内容；
#    3、拔出一个节点的一块共享盘；
#    4、到目录/mnt/parastor/.snapshot下检查各个快照的数据的正确性；
#    5、删除快照；
#    6、检查是否有快照路径入口；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/liyao/snap/snap_13_1_2_14
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_1_2_14

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

    # 4> 获取每个快照的md5值
    md5_lst_2 = []
    for i in range(10):
        snap_file = os.path.join(snap_common.SNAPSHOT_PAHT, FILE_NAME + '_snapshot_%d' % i)
        md5 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, snap_file)
        md5_lst_2.append(md5)

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

    if md5_lst_1 != md5_lst_2:
        log.error('md5 is not right!!!')
        raise Exception('md5 is not right!!!')

    # 5> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (FILE_NAME))
        raise Exception('%s delete snapshot failed!!!' % (FILE_NAME))

    time.sleep(10)

    return

def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)

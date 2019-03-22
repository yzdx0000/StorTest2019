#-*-coding:utf-8 -*
from multiprocessing import Process
import os
import time

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean
import json
import random
import tool_use

####################################################################################
#
# Author: liyao
# date 2018-07-12
#@summary：
#    vdbench数据读写过程中，拔除一块数据盘，触发被动重建
#@steps:
#    1、部署3节点集群；
#    2、使用vdbench在目录/mnt/volume1/defect/qc_795/创建数据；
#    3、数据读写的同时随机拔除一个节点的一块数据盘，触发被动重建；
#    4、重新插入磁盘；
#    5、删除磁盘，等待，再添加磁盘
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]        # 本脚本名字
DEFECT_PATH = get_config.get_one_defect_test_path()                # "/mnt/volume1/defect_case"
DEFECT_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)            # "/mnt/volume1/defect_case/qc_795"
BASE_DEFECT_PATH = os.path.dirname(DEFECT_PATH)                    # "/mnt/volume1"
DEFECT_PATH_BASENAME = os.path.basename(DEFECT_PATH)               # "defect"
DEFECT_PATH_ABSPATH = os.path.abspath(DEFECT_PATH)                 # "/mnt/volume1/defect"
SNAPSHOT_PAHT = os.path.join(BASE_DEFECT_PATH, '.snapshot')      # "/mnt/volume1/.snapshot"
CREATE_SNAP_PATH = os.path.join(DEFECT_PATH_BASENAME, FILE_NAME)   # "/defect/qc_795"

# 随机拔出插入一块数据盘
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
    # 更新磁盘重建的等待时间
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')

    # 随机选取集群内的一个节点，获取节点的数据盘的物理id
    # 获取集群内所有节点的id
    ob_node = common.Node()
    ob_disk = common.Disk()
    node_id_lst = ob_node.get_nodes_id()

    # 随机选一个节点
    fault_node_id = random.choice(node_id_lst)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    # 获取一个节点内所有的共享硬盘和数据硬盘
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)
    # 随机获取一个数据盘
    fault_disk_name = random.choice(monopoly_disk_names)

    # 故障盘的scsi id, id, uuid, 盘类型
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

    # 2&3> 使用vdbench创建数据，同时拔除一块数据盘
    vdbench_tool_path = get_config.get_snap_vdbench_path()
    obj_vdb = tool_use.Vdbenchrun(size="(64k,30,128k,35,256k,30,1m,5)")
    p1 = Process(target=obj_vdb.run_create, args=(DEFECT_TRUE_PATH, DEFECT_TRUE_PATH, snap_common.CLIENT_IP_1))
    p2 = Process(target=pullout_one_disk, args=(fault_node_ip, fault_disk_physicalid))

    p1.start()
    log.info('waiting for 10s')
    time.sleep(10)
    p2.start()

    p1.join()
    p2.join()

    if p1.exitcode != 0:
        log.error("modify file failed!!!!!!")
        case_flag = False
        #raise Exception("vdbench is failed!!!!!!")

    log.info('wait 60s')
    time.sleep(60)

    # 不断检查坏对象是否修复
    count = 0
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 60 seconds")
        time.sleep(60)
        if True == common.check_badjobnr():
            break

    # 4>将磁盘重新插入
    insert_one_disk(fault_node_ip, fault_disk_physicalid)

    # 5>删除磁盘
    ob_disk.remove_disks(fault_disk_id)

    log.info('wait 180s')
    time.sleep(180)

    # 磁盘加入到系统
    ob_disk.add_disks(fault_node_id, fault_disk_uuid, fault_disk_usage)

    # 恢复磁盘重建的等待时间
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '18000000')


    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    create_snap_path = os.path.join(DEFECT_PATH_BASENAME, FILE_NAME)
    snap_true_path = os.path.join(DEFECT_PATH, FILE_NAME)
    snap_common.cleaning_environment(create_snap_path, snap_true_path)

    case()

    snap_common.cleaning_environment(create_snap_path, snap_true_path)
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)



if __name__ == '__main__':
    common.case_main(main)
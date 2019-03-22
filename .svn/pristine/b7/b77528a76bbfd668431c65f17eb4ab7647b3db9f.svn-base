#-*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean
import tool_use

####################################################################################
#
# author 刘俊鑫
# date 2018-07-12
#@summary：
#   qc_504,跑vdbench的同时进行随机插拔两块磁盘，间隔十分钟后恢复磁盘，产生了core
#@steps:
#   step1:跑vdbench
#   step2：随机插拔磁盘
#   step3：十分钟后恢复磁盘
#
#@changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]               #本脚本名字
DEFECT_PATH=get_config.get_one_defect_test_path()                         #DEFECT_PATH = "/mnt/volume1/defect_case
DEFECT_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)



'''随机获取集群内的一个节点,获取节点的所有数据盘的物理id'''

def get_random_node_monopoly_disks(node_id, node_ip):
    ob_disk = common.Disk()

    '''获取一个节点内所有的共享硬盘和数据硬盘'''
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(node_id)
    '''获取节点内数据盘的物理id, 2:0:0:1'''
    monopoly_disk_id_list = []
    for disk_name in monopoly_disk_names:
        id = ob_disk.get_physicalid_by_name(node_ip, disk_name)
        monopoly_disk_id_list.append(id)

    return monopoly_disk_id_list

'''在同一个节点上随机拔出插入两块数据盘'''

def random_disk_fault(node_ip, monopoly_disk_id_list):
    time.sleep(10)

    disk_id = random.sample(monopoly_disk_id_list, 2)
    while True:
        cmd2 = ('ssh %s \"echo scsi remove-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id[0]))
        cmd3 = ('ssh %s \"echo scsi remove-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id[1]))
        cmd4 = ('ssh %s \"echo scsi add-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id[0]))
        cmd5 = ('ssh %s \"echo scsi add-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id[1]))
        log.info(cmd2)
        common.command(cmd2)
        log.info(cmd3)
        common.command(cmd3)
        time.sleep(180)
        log.info(cmd4)
        common.command(cmd4)
        log.info(cmd5)
        common.command(cmd5)
        time.sleep(180)



def case():
    log.info("----------case----------")
    '''随机选取集群内的一个节点，获取节点的数据盘的物理id'''
    '''获取集群内所有节点的id'''
    ob_node = common.Node()
    nodeid_list = ob_node.get_nodes_id()

    '''随机选一个节点'''
    node_id = random.choice(nodeid_list)
    node_ip = ob_node.get_node_ip_by_id(node_id)

    '''获取节点内的所有数据盘的物理id'''
    monopoly_disk_id_list1 = get_random_node_monopoly_disks(node_id, node_ip)

    client_ip_lst = get_config.get_allclient_ip()

    """恢复重建时间为默认值"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '18000000')

    '''配置Vdbench'''
    VDBENCH_PATH=DEFECT_TRUE_PATH
    vdbench=tool_use.Vdbenchrun(depth=3, width=7, files=200, size="(4k,35,128k,30,1m,20,10m,10,200m,5)", threads=120, xfersize="(4k,30,32k,30,128k,30,1m,10)", elapsed=1800)
    #vdbench = tool_use.Vdbenchrun()

    '''vdbench进程'''
    p1 = Process(target=vdbench.run_create, args=(VDBENCH_PATH, VDBENCH_PATH, client_ip_lst[0], client_ip_lst[1],))
    '''随机拔插盘进程'''
    p2 = Process(target=random_disk_fault, args=(node_ip, monopoly_disk_id_list1,))

    p1.start()
    time.sleep(10)
    p2.start()

    p1.join()
    p2.terminate()
    p2.join()

    '''再获取一遍节点内的硬盘,防止进程停止的时候拔出了盘没有插入'''
    monopoly_disk_id_list2 = get_random_node_monopoly_disks(node_id, node_ip)
    disk_list = []
    for disk_id in monopoly_disk_id_list1:
        if disk_id not in monopoly_disk_id_list2:
            disk_list.append(disk_id)

    for disk in disk_list:
        cmd = ('ssh %s \"echo scsi add-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk))
        common.command(cmd)

    if p1.exitcode != 0:
        raise Exception("vdbench is failed!!!!!!")

    '''不断检查坏对象是否修复'''
    count = 0
    log.info("wait 60 seconds")
    time.sleep(60)
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 10 seconds")
        time.sleep(10)
        if True == common.check_badjobnr():
            break

    """检查所有的磁盘状态是否正确"""

    # if True != common.check_alldisks_health():
    #    raise Exception("some disks is not health")

    '''检查系统'''
    common.ckeck_system()

    log.info("case succeed!")


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)


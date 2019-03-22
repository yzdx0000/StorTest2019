#-*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common

import log
import get_config
import prepare_clean
import tool_use
import make_fault

####################################################################################
#
# author 刘俊鑫
# date 2018-07-13
#@summary：
#   qc_485,每隔15分钟，kill节点1的oPara进程，kill节点2的oStor，oJob进程，拔出插入节点3的一块数据盘
#@steps:
#   step1:删除磁盘并取消删除磁盘
#   step2：再次删除磁盘，并查看磁盘状态
#   step3：十分钟后恢复磁盘
#
#@changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]               #本脚本名字
DEFECT_PATH=get_config.get_one_defect_test_path()                         #DEFECT_PATH = "/mnt/volume1/defect_case
DEFECT_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)
VDBENCH_WRITE_PATH = os.path.join(DEFECT_TRUE_PATH, 'write')
VDBENCH_JN_PATH = os.path.join(DEFECT_TRUE_PATH, 'jn')

'''vdbench校验'''
def vdbench_check(path1, path2, *args):
    while True:
        log.info('---------vdbench_check_begin----------')
        vdbench=tool_use.Vdbenchrun(files=1000, elapsed=900)
        vdbench.run_check(path1, path2, *args)
        log.info('---------vdbench_check_end----------')


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

def fault_to_do():
    while True:
        time.sleep(900)

        '''kill 节点1上的oPara进程，节点2上的oStor和oJob进程'''
        parastor_ip_list = get_config.get_allparastor_ips
        make_fault.kill_process(parastor_ip_list[1], 'oPara')
        make_fault.kill_process(parastor_ip_list[2], 'oStor')
        make_fault.kill_process(parastor_ip_list[2], 'oJob')
        '''随机拔插一块节点3上的数据盘'''
        monopoly_disk_id_list=get_random_node_monopoly_disks(3, parastor_ip_list[3])
        disk_id = random.choice(monopoly_disk_id_list)
        cmd1 = ('ssh %s \"echo scsi remove-single-device %s > /proc/scsi/scsi\"' % (parastor_ip_list[3], disk_id))
        cmd2 = ('ssh %s \"echo scsi add-single-device %s > /proc/scsi/scsi\"' % (parastor_ip_list[3], disk_id))
        log.info(cmd1)
        common.command(cmd1)
        time.sleep(60)
        log.info(cmd2)
        common.command(cmd2)

def case():

    cmd1 = 'mkdir %s' % VDBENCH_WRITE_PATH
    cmd2 = 'mkdir %s' % VDBENCH_JN_PATH
    common.command(cmd1)
    common.command(cmd2)

    client_ip_lst = get_config.get_allclient_ip()

    vdbench=tool_use.Vdbenchrun(files=1000, elapsed=900)

    p1 = Process(target=vdbench.run_create, args=(VDBENCH_WRITE_PATH, VDBENCH_JN_PATH, client_ip_lst[1]))
    p2 = Process(target=vdbench_check, args=(VDBENCH_WRITE_PATH, VDBENCH_JN_PATH, client_ip_lst[1]))
    p3 = Process(target=fault_to_do, args=())
    #vdbench.run_create(DEFECT_TRUE_PATH, DEFECT_TRUE_PATH, client_ip_lst[1])

    p1.start()
    p1.join()
    time.sleep(10)
    p2.start()
    p3.start()
    time.sleep(4000)
    p2.terminate()
    p3.terminate()
    p2.join()
    p3.join()







def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
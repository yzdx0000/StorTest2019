# -*-coding:utf-8 -*
import os
from multiprocessing import Process
import time
import json
import subprocess
import random

import utils_path
import common
import log
import tool_use
import get_config

############################################################
#
# Author: baorb
# date 2017-08-21
# @summary：
#    本测试主要测试P300节点同时删除两个数据盘。
# @steps:
#    1，配置节点池
#    2，配置存储池
#    3，配置卷
#    4，vdbench创建文件
#    5，先后删除两块数据盘(触发修复后，再删除第二个硬盘)
#    6，vdbench进行数据检验
#
# @changelog：
############################################################


'''获取一个节点的所有数据盘的物理id'''
def get_one_node_monopoly_disks(node_id, node_ip):
    '''获取所有的共享硬盘池和数据硬盘池id'''
    ob_disk = common.Disk()

    '''获取一个节点内所有的共享硬盘和数据硬盘'''
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(node_id)

    '''获取节点内数据盘的物理id, 2:0:0:1'''
    monopoly_disk_id_list = []
    for disk_name in monopoly_disk_names:
        id = ob_disk.get_physicalid_by_name(node_ip, disk_name)
        monopoly_disk_id_list.append(id)

    return monopoly_disk_id_list


'''随机拔出插入两块数据盘'''
def random_pullout_two_disks(node_ip, monopoly_disk_id_list):
    time.sleep(10)

    disk_id_lst = random.sample(monopoly_disk_id_list, 2)

    for disk_id in disk_id_lst:
        cmd = ('ssh %s \"echo scsi remove-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id))
        time.sleep(120)
        common.command(cmd)
    time.sleep(300)

    for disk_id in disk_id_lst:
        cmd = ('ssh %s \"echo scsi add-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id))
        common.command(cmd)

    return


def case():
    log.info("-----------------------case begin-----------------------")

    '''获取客户端ip'''
    client_ip_lst = get_config.get_allclient_ip()

    '''先跑00.init.sh'''
    tool_use.vdbench_run(client_ip_lst[0], client_ip_lst[1], only_00 = True)

    '''随机选取集群内的一个节点，获取节点的数据盘的物理id'''
    '''获取集群内所有节点的id'''
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    node_ip_lst = ob_node.get_nodes_ip()

    '''随机选一个节点'''
    fault_node_id = random.choice(node_id_lst)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    '''获取节点内的所有数据盘的物理id'''
    monopoly_disk_id_list1 = get_one_node_monopoly_disks(fault_node_id, fault_node_ip)

    p1 = Process(target=tool_use.vdbench_run, args=(client_ip_lst[0], client_ip_lst[1], False, True))
    p2 = Process(target=random_pullout_two_disks, args=(fault_node_ip, monopoly_disk_id_list1,))

    p1.start()
    p2.start()

    p1.join()
    p2.terminate()
    p2.join()

    '''再获取一遍节点内的硬盘,防止进程停止的时候拔出了盘没有插入'''
    monopoly_disk_id_list2 = get_one_node_monopoly_disks(fault_node_id, fault_node_ip)
    disk_list = []
    for disk_id in monopoly_disk_id_list1:
        if disk_id not in monopoly_disk_id_list2:
            disk_list.append(disk_id)

    for disk in disk_list:
        cmd = ('ssh %s \"echo scsi add-single-device %s > /proc/scsi/scsi\"' % (fault_node_ip, disk))
        common.command(cmd)

    if p1.exitcode != 0:
        raise Exception("vdbench is failed!!!!!!")

    '''不断检查坏对象是否修复'''
    count = 0
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 60 seconds")
        time.sleep(60)
        if True == common.check_badjobnr():
            break

    '''再跑01检查数据的正确性'''
    tool_use.vdbench_run(client_ip_lst[0], client_ip_lst[1], only_01=True)

    '''检查系统'''
    common.ckeck_system()

    log.info("case succeed!")


def main():
    file_name = os.path.basename(__file__)
    file_name = os.path.splitext(file_name)[0]
    log_file_path = log.get_log_path(file_name)
    stream = log.init(log_file_path, True)
    case()
    log.info('succeed!')
    return


if __name__ == '__main__':
    main()
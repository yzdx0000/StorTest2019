# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import tool_use
import make_fault
import get_config
import prepare_clean

#################################################################
#
# author 张芳芳
# date 2018-07-03
# @summary：
#    本测试主要测试拔共享盘故障，同时kill进程。
# @steps:
#    1，使用vdbench创建文件和数据校验
#    2，同时在一个节点上每隔30s随机拔出插入一块共享盘，同时kill进程
#
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
MINI_TRUE_PATH = os.path.join(prepare_clean.MINICASE_PATH, FILE_NAME)      # /mnt/volume1/mini_case/3_0015_truncate_test

session_list = ['oJmgs', 'oMgcd', 'oPara', 'oStor', 'oJob', 'oRole', 'zk']


def kill_process(node_ip, pro_lst):
    """
    进行kill 进程故障
    :param node_ip:
    :return:
    """
    time.sleep(10)
    while True:
        '''随机选取进程'''
        ran_num = random.randint(1, len(pro_lst))
        tem_session_lst = random.sample(pro_lst, ran_num)
        for session in tem_session_lst:
            make_fault.kill_process(node_ip, session)
        time.sleep(120)


def get_random_node_share_disks(node_id, node_ip):
    """
    随机获取集群内的一个节点,获取节点的所有共享盘的物理id
    :param node_id:
    :param node_ip:
    :return:
    """
    ob_disk = common.Disk()

    '''获取一个节点内所有的共享硬盘和数据硬盘'''
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(node_id)
    '''获取节点内共享盘的物理id, 2:0:0:1'''
    share_disk_id_list = []
    for disk_name in share_disk_names:
        id = ob_disk.get_physicalid_by_name(node_ip, disk_name)
        share_disk_id_list.append(id)

    return share_disk_id_list


def random_disk_fault(node_ip, share_disk_id_list):
    """
    随机拔出插入一块共享盘
    :param node_ip:
    :param share_disk_id_list:
    :return:
    """
    disk_scsi_id = random.choice(share_disk_id_list)
    for i in range(5):
        make_fault.pullout_disk(node_ip, disk_scsi_id, 'SHARED')
        time.sleep(30)
        make_fault.insert_disk(node_ip, disk_scsi_id, 'SHARED')
        time.sleep(30)


def case():
    log.info("----------case----------")
    '''随机选取集群内的一个节点，获取节点的共享盘的物理id'''
    '''获取集群内所有节点的id'''
    ob_node = common.Node()
    nodeid_list = ob_node.get_nodes_id()

    '''随机选一个节点'''
    node_id = random.choice(nodeid_list)
    node_ip = ob_node.get_node_ip_by_id(node_id)
    rc, service_lst = ob_node.get_node_all_services(node_id=node_id)
    pro_lst = list(set(service_lst).intersection(set(session_list)))

    '''获取节点内的所有共享盘的物理id'''
    share_disk_id_list1 = get_random_node_share_disks(node_id, node_ip)

    client_ip_lst = get_config.get_allclient_ip()

    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '18000000')

    p1 = Process(target=tool_use.vdbench_run, args=(MINI_TRUE_PATH, client_ip_lst[0], client_ip_lst[1]),
                 kwargs={'run_create': True, 'run_check_write': True})
    p2 = Process(target=random_disk_fault, args=(node_ip, share_disk_id_list1))
    p3 = Process(target=kill_process, args=(node_ip, pro_lst))

    p1.start()
    time.sleep(10)
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.terminate()
    p3.join()

    time.sleep(10)

    common.judge_rc(p1.exitcode, 0, 'vdbench_run')

    '''不断检查坏对象是否修复'''
    count = 0
    log.info("wait 60 seconds")
    time.sleep(60)
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 10 seconds")
        time.sleep(10)
        if common.check_badjobnr():
            break

    '''再跑01检查数据的正确性'''
    tool_use.vdbench_run(MINI_TRUE_PATH, client_ip_lst[0], client_ip_lst[1], run_check=True)

    '''检查系统'''
    common.ckeck_system()

    """不断检查进程是否起来"""
    while True:
        log.info("wait 60 s")
        time.sleep(60)
        for process in pro_lst:
            if not make_fault.check_process(node_ip, process):
                log.info('node %s process %s is not normal!!!' % (node_ip, process))
                break
        else:
            break

    log.info("case succeed!")


def main():
    prepare_clean.minicase_test_prepare(FILE_NAME, check_share_disk_num=True)
    case()
    prepare_clean.minicase_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)
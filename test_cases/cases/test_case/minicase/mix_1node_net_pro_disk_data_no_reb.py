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
# Author: baorb
# date 2017-08-21
# @summary：
#    测试一个节点不断断网和拔数据盘。
# @steps:
#    1，随机选择一个集群节点
#    2，每隔随机时间down和up一个点的所有数据网
#    3，不断拔出插入数据盘
#    4，不断kill进程
#    5，同时用vdbench读写数据
#
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
MINI_TRUE_PATH = os.path.join(prepare_clean.MINICASE_PATH, FILE_NAME)      # /mnt/volume1/mini_case/FILE_NAME
Wait_Time = 50    # 断网故障间隔时间为50s内的一个随机值
session_list = ['oJmgs', 'oMgcd', 'oPara', 'oStor', 'oJob', 'oRole', 'zk']


def kill_process(node_ip):
    """
    进行kill 进程故障
    :param node_ip:
    :return:
    """
    time.sleep(10)
    while True:
        '''随机选取进程'''
        ran_num = random.randint(1, len(session_list))
        tem_session_lst = random.sample(session_list, ran_num)
        log.info("will kill {}".format(tem_session_lst))
        for session in tem_session_lst:
            make_fault.kill_process(node_ip, session)
        log.info("wait 60s kill process")
        time.sleep(60)


def disk_fault(node_ip, disk_scsi_id, disk_usage):
    """
    每隔随机时间拔出和插入一个点的所有数据网
    :param node_ip:
    :param disk_scsi_id:
    :return:
    """
    while True:
        """拔盘"""
        make_fault.pullout_disk(node_ip, disk_scsi_id, disk_usage)

        wait_time_tmp = random.randint(1, Wait_Time)
        log.info("wait %ss insert disk" % wait_time_tmp)
        time.sleep(wait_time_tmp)

        """加盘"""
        make_fault.insert_disk(node_ip, disk_scsi_id, disk_usage)

        wait_time_tmp = random.randint(1, Wait_Time)
        log.info("wait %ss pullout disk" % wait_time_tmp)
        time.sleep(wait_time_tmp)


def net_fault(node_ip, eth_lst, ip_mask_lst):
    """
    每隔随机时间down和up一个点的所有数据网
    :param node_ip:
    :param eth_lst:
    :return:
    """
    while True:
        """down net"""
        make_fault.down_eth(node_ip, eth_lst)

        wait_time_tmp = random.randint(1, Wait_Time)
        log.info("wait %ss up eth" % wait_time_tmp)
        time.sleep(wait_time_tmp)

        start_time = time.time()
        while True:
            time.sleep(20)
            if common.check_ping(node_ip):
                break
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            log.info('node %s cannot ping pass %dh:%dm:%ds' % (node_ip, h, m, s))
        log.info('wait 20s')
        time.sleep(20)

        """up net"""
        make_fault.up_eth(node_ip, eth_lst, ip_mask_lst)

        wait_time_tmp = random.randint(1, Wait_Time)
        log.info("wait %ss down eth" % wait_time_tmp)
        time.sleep(wait_time_tmp)


def case():
    log.info("1> 随机获取一个集群节点")
    obj_node = common.Node()
    node_id_lst = obj_node.get_nodes_id()
    fault_node_id = random.choice(node_id_lst)
    node_ctrl_ip = obj_node.get_node_ip_by_id(fault_node_id)
    node_eth_lst, node_data_ip_lst, node_ip_mask_lst = obj_node.get_node_eth(fault_node_id)
    if node_ctrl_ip in node_data_ip_lst:
        raise Exception("ctrl ip in data ip, this case can't run!!!")

    log.info("2> 集群中随机获取一个数据盘")
    ob_disk = common.Disk()
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)
    """随机获取一个数据盘"""
    fault_disk_name = random.choice(monopoly_disk_names)
    fault_disk_scsi_id = ob_disk.get_physicalid_by_name(node_ctrl_ip, fault_disk_name)
    fault_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_disk_name)

    log.info("3> 读写业务,同时不断down和up一个点的数据网")
    client_1_ip = get_config.get_client_ip(0)
    client_2_ip = get_config.get_client_ip(1)
    p1 = Process(target=tool_use.vdbench_run, args=(MINI_TRUE_PATH, client_1_ip, client_2_ip),
                 kwargs={'run_create': True, 'run_check_write': True, 'run_check': True})
    p2 = Process(target=net_fault, args=(node_ctrl_ip, node_eth_lst, node_ip_mask_lst))
    p3 = Process(target=disk_fault, args=(node_ctrl_ip, fault_disk_scsi_id, fault_disk_usage))
    p4 = Process(target=kill_process, args=(node_ctrl_ip,))

    p1.daemon = True
    p2.daemon = True
    p3.daemon = True
    p4.daemon = True

    p1.start()
    p2.start()
    p3.start()
    p4.start()

    p1.join()
    p2.terminate()
    p2.join()
    p3.terminate()
    p3.join()
    p4.terminate()
    p4.join()

    start_time = time.time()
    while True:
        time.sleep(20)
        if common.check_ping(node_ctrl_ip):
            break
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('node %s cannot ping pass %dh:%dm:%ds' % (node_ctrl_ip, h, m, s))
    log.info('wait 20s')
    time.sleep(20)

    """再up一遍故障节点的所有数据网"""
    make_fault.up_eth(node_ctrl_ip, node_eth_lst, node_ip_mask_lst)

    """再重新插入一回数据盘"""
    make_fault.insert_disk(node_ctrl_ip, fault_disk_scsi_id, fault_disk_usage)

    """不断检查进程是否起来"""
    while True:
        log.info("wait 60 s")
        time.sleep(60)
        for process in session_list:
            if not make_fault.check_process(node_ctrl_ip, process):
                log.info('node %s process %s is not normal!!!' % (node_ctrl_ip, process))
                break
        else:
            break

    """检查vdbench是否成功"""
    common.judge_rc(p1.exitcode, 0, 'vdbench run')
    return


def main():
    prepare_clean.minicase_test_prepare(FILE_NAME)
    case()
    prepare_clean.minicase_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)
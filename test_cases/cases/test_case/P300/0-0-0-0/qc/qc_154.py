# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import shell
import get_config
import prepare_clean
import tool_use
import commands
import make_fault
#################################################################
#
# Author: chenjy1
# Date: 2018-07-14
# @summary：
#        down掉似有客户端的所有数据网口，发现界面上显示的客户端连接的状态时正常
# @steps:
#       1、检查客户端连接状态，确认正常
#       2、down掉一个客户端所有数据网
#       3、查看客户端连接状态
#       4、恢复客户端数据网
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字


def get_client_date_ip(client_ip):
    """
    :author :             chenjy1
    :date:                2018.08.24
    :description:         获取一个客户端的所有数据网IP
    :param client_ip:    (str)客户端IP
    :return:
    """
    client_date_ip_lst = []
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    sys_node_ip = ob_node.get_node_ip_by_id(node_id_lst[0])
    eth_list, data_ip_list, ip_mask_lst = ob_node.get_node_eth(node_id_lst[0])
    clientnode_all_ip_lst = []

    cmd = 'ip addr | grep "inet "'
    rc, stdout = common.run_command(client_ip, cmd)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    lines = stdout.strip().split('\n')
    for line in lines:
        ip = line.split()[1].split('/')[0]
        clientnode_all_ip_lst.append(ip)

    for sys_date_ip in data_ip_list:
        for ip in clientnode_all_ip_lst:
            if ip != "127.0.0.1":
                cmd = "ping -c 2 -I %s %s" % (sys_date_ip, ip)
                rc, stdout = common.run_command(sys_node_ip, cmd, timeout=5)
                if rc == 0:
                    client_date_ip_lst.append(ip)
                    break
    return client_date_ip_lst


def get_dateip_eth(ip, dateip):
    """
    :author :             chenjy1
    :date:                2018.08.24
    :description:         获取对应数据网ip的网卡名
    :param ip:           (str)管理网ip
    :param dateip:       (str)数据网ip
    :return:
    """
    cmd = "ip addr |grep %s" % dateip
    rc, stdout = common.run_command(ip, cmd)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    dateip_eth = stdout.split()[-1]
    return dateip_eth


def get_one_client_intimestatus(client_ip):
    """
    :author :             chenjy1
    :date:                2018.08.24
    :description:         获取客户端状态
    :param client_ip:    (str)客户端ip
    :return:             (str)客户端状态
                          -1 :没找到此客户端
    """
    rc, stdout = common.get_clients()
    common.judge_rc(rc, 0, 'get_clients')
    pscli_info = common.json_loads(stdout)
    node_client_info_lst = pscli_info['result']
    for node_client_info in node_client_info_lst:
        if client_ip == node_client_info['ip']:
            return node_client_info['inTimeStatus']
    return -1


def case():
    log.info("case begin")
    ob_node = common.Node()
    ob_disk = common.Disk()
    ob_storage_pool = common.Storagepool()
    node_id_lst = ob_node.get_nodes_id()
    node_id_1 = ob_node.get_node_ip_by_id(node_id_lst[0])
    client_ip_lst = get_config.get_allclient_ip()

    """随机选取一个节点"""
    rc, stdout = common.get_clients()
    common.judge_rc(rc, 0, "get_clients ailed")
    pscli_info = common.json_loads(stdout)
    node_client_info_lst = pscli_info['result']
    client_info_list = []
    log.info("1> 检查客户端连接状态，确认正常")
    for client_info in node_client_info_lst:
        if 'EXTERNAL' == client_info['type'] and (client_info['ip'] in client_ip_lst) :
            client_info_list.append(client_info)
            if client_info['inTimeStatus'] != "SERV_STATE_OK":
                common.except_exit("ip:%s state is not SERV_STATE_OK " % client_info['ip'])

    log.info("2> down掉一个客户端所有数据网")
    client_ip_lst = []
    for client_info in client_info_list:
        client_ip_lst.append(client_info['ip'])
    fault_client_ip = random.choice(client_ip_lst)
    """ifdown被选中客户端的所有dataip"""
    fault_client_data_ip_lst = get_client_date_ip(fault_client_ip)
    fault_client_data_ip_eth_lst = []
    for ip in fault_client_data_ip_lst:
        ethname = get_dateip_eth(fault_client_ip, ip)
        fault_client_data_ip_eth_lst.append(ethname)
    rc = make_fault.down_eth(fault_client_ip, fault_client_data_ip_eth_lst)
    common.judge_rc(rc, 0, "ifdown client all data eth failed")

    log.info("3> 查看客户端连接状态")
    start_time = time.time()
    while True:
        intimestatus = get_one_client_intimestatus(fault_client_ip)
        if intimestatus == -1:
            common.except_exit("get_one_client_inTimeStatus not found ip : %s" % fault_client_ip)
        if "SERV_STATE_UNKNOWN" == intimestatus:
            log.info('client inTimeStatus correct!!!')
            break
        time.sleep(20)
        exist_time = int(time.time() - start_time)
        if exist_time >= 600:
            rc = make_fault.up_eth(fault_client_ip, fault_client_data_ip_eth_lst)  # 在报错前先将网卡恢复了
            common.judge_rc(rc, 0, "ifconfig up client all data eth failed")
            common.except_exit("wait client inTimeStatus SERV_STATE_UNKNOWN 10min")
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('wait client inTimeStatus %dh:%dm:%ds' % (h, m, s))

    log.info("4> 恢复客户端数据网")
    rc = make_fault.up_eth(fault_client_ip, fault_client_data_ip_eth_lst)
    common.judge_rc(rc, 0, "ifconfig up client all data eth failed")
    """等待状态正常"""
    start_time = time.time()
    while True:
        intimestatus = get_one_client_intimestatus(fault_client_ip)
        if intimestatus == -1:
            common.except_exit("get_one_client_inTimeStatus not found ip : %s" % fault_client_ip)
        if "SERV_STATE_OK" == intimestatus:
            log.info('client inTimeStatus SERV_STATE_OK')
            break
        time.sleep(20)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('wait client inTimeStatus SERV_STATE_OK %dh:%dm:%ds' % (h, m, s))

    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)

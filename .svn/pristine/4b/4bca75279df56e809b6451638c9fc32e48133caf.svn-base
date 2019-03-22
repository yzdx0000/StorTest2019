# -*-coding:utf-8 -*
# !/usr/bin/python

import os
import time
import commands
import json
import hashlib

import utils_path
import common
import snap_common
import nas_common

import random
import log
import shell
import get_config
import tool_use
import prepare_clean
from multiprocessing import Process

# =================================================================================
#  latest update:2018-08-07                                                    =
#  Author:wanggl                                                           =
# =================================================================================
# 2018-08-07:
# Author：wanggl
# @summary：
#   网络丢包
# @steps:
#   1、3节点集群，4+2:1配比，私有客户端挂载，通过vdbench写入数据；
#   2、模拟某个网络发送与接收丢包，执行20分钟；
#
#

# changelog:


######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
volume_path = os.path.join(nas_common.BASE_NAS_PATH, FILE_NAME)             # /mnt/wangguanglin/cus_6_1_0_44
Private_clientIP1 = get_config.get_client_ip(0)
Private_clientIP2 = get_config.get_client_ip(1)
Private_clientIP3 = get_config.get_client_ip(2)


def vdbench_run(anchor_path,  journal_path, *args):
    """
    :Author:            wanggl
    :date  :            2018.08.08
    :description:       运行vdbench,先创建，再读写
    :param anchor_path:  数据读写的路径
    :param journal_path:  校验文件创建的路径
    :param args:       运行vdbench的ip
    :return: 
    """
    vdb = tool_use.Vdbenchrun(depth=2, width=3, files=40, xfersize='4k', elapsed=1200)
    vdb.run_create(anchor_path, journal_path, *args)
    rc = vdb.run_check_write(anchor_path, journal_path, *args)
    common.judge_rc(rc, 0, 'vdbench run ')
    return


def package_loss(netcard, value, exe_ip):
    """
    :Author:            wanggl
    :date  :            2018.08.08
    :description:        设置网卡丢包率 20分钟后恢复之前的配置
    :param netcard:     网卡名
    :param value:       丢包率
    :param exe_ip:      外部的客户端
    :return: 
    """
    for eth_name in netcard:
        cmd = 'tc qdisc add dev %s root netem loss %s' % (eth_name, value)
        common.run_command(exe_ip, cmd)
    time.sleep(1200)
    for eth_name in netcard:
        cmd = 'tc qdisc del dev %s root netem loss %s' % (eth_name, value)
        common.run_command(exe_ip, cmd)

    return


def case():

    log.info('模拟网络丢包，执行20分钟')
    ob_node = common.Node()
    node_ids = []
    node_ids = ob_node.get_nodes_id()
    node_id = random.choice(node_ids)
    eth_lst, data_ip_lst, ip_mask_lst = ob_node.get_node_eth(node_id)
    common.mkdir_path(Private_clientIP1, volume_path)
    p1 = Process(target=vdbench_run, args=(volume_path, '/tmp', Private_clientIP1, Private_clientIP2,
                                           Private_clientIP3))
    p2 = Process(target=package_loss, args=(eth_lst, '40%',  snap_common.SYSTEM_IP))
    p1.start()
    time.sleep(60)
    p2.start()
    p1.join()
    p2.join()
    common.judge_rc(p1.exitcode, 0, 'p1 process')

    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    common.rm_exe(Private_clientIP1, volume_path)
    prepare_clean.test_clean(FILE_NAME)
    log.info('succeed!')


if __name__ == '__main__':
    common.case_main(main)

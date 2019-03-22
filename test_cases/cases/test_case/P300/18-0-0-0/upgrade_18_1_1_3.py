# -*-coding:utf-8 -*

import os
import time
from multiprocessing import Process


import utils_path
import log
import common
import tool_use
import make_fault
import get_config
import prepare_clean
import upgrade_common
import online_upgrade

####################################################################################
#
# author 刘俊鑫
# date 2018-07-30
# @summary：
#   执行在线升级操作时跑vdbench读写校验，并在还没升级的节点有断网操作（本脚本要在五节点集群上进行）
# @steps:
#   step1: vdvench创建文件
#   step2：执行在线升级
#   step3：断掉一个还未升级节点的数据网
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
DEFECT_PATH = get_config.get_one_defect_test_path()                         # DEFECT_PATH = /mnt/volume1/defect_case
DEFECT_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)                     # DEFECT_TRUE_PATH= volume:/defect_case/p300
VDBENCH_WRITE_PATH = os.path.join(DEFECT_TRUE_PATH, 'write')                # vdbench读写路径
VDBENCH_JN_PATH = os.path.join(DEFECT_TRUE_PATH, 'jn')                      # vdbench校验文件路径
client_ip_lst = get_config.get_allclient_ip()                               # 客户端ip列表

# todo:该脚本还没跑过，第一因为升级还不能测试，第二因为该脚本需要五节点环境


def network_fault(node_ip, eth_list):
    """
    :author           minicase:3_0020_nework_fault.py
    :param node_ip:
    :param eth_list:  netcard name list in node_ip
    :return:
    """
    time.sleep(10)

    for i in range(1, 4):
        make_fault.down_eth(node_ip, eth_list)

        time.sleep(120)

        make_fault.up_eth(node_ip, eth_list)

        time.sleep(20)


def case():
    """
    :author:         liujx
    :date            2018.07.30
    :description:
    :return:
    """
    """创建vebench读写路径与校验路径"""
    cmd1 = 'mkdir %s' % VDBENCH_WRITE_PATH
    cmd2 = 'mkdir %s' % VDBENCH_JN_PATH
    common.command(cmd1)
    common.command(cmd2)
    """初始化vdbench"""
    vdbench = tool_use.Vdbenchrun()
    p1 = Process(target=vdbench.run_create, args=(VDBENCH_WRITE_PATH, VDBENCH_JN_PATH, client_ip_lst[0]))
    p2 = Process(target=online_upgrade.case, args=())
    """等待vdbench create完文件"""
    p1.start()
    p1.join()
    """开始升级"""
    p2.start()
    """等待升级前检查与升级包分发完成"""
    time.sleep(120)
    """
    获取尚未升级的节点id和eth_list
    如果存在尚未升级的节点，则断其数据网
    如果不存在尚未升级的节点，则不进行故障
    """
    obj_node = common.Node()
    p3 = None
    eth_list = []
    network_fault_ip = ''
    network_fault_id = upgrade_common.get_nonupgrade_list()
    if network_fault_id != -1:
        network_fault_ip = obj_node.get_node_ip_by_id(node_id=network_fault_id[0])
        eth_list, data_ip_list, ip_mask_lst = obj_node.get_node_eth(network_fault_id)
        p3 = Process(target=network_fault, args=(network_fault_ip, eth_list))
    elif network_fault_id == -1:
        p3 = Process(target=time.sleep, args=(10,))
        log.info("becasue there is no nonupgrade node, so this case has no down net step")
    """开始断网操作"""
    p3.start()
    """开始读写并校验文件"""
    vdbench1 = tool_use.Vdbenchrun(elapsed=50)
    while p2.is_alive():
        log.info("##########vdbench check begin#############")
        rc = vdbench1.run_check(VDBENCH_WRITE_PATH, VDBENCH_JN_PATH, client_ip_lst[0])
        if rc != 0:
            raise Exception("vdbench check failed")
        log.info("##########vdbench write begin#############")
        vdbench.run_write_jn(VDBENCH_WRITE_PATH, VDBENCH_JN_PATH, client_ip_lst[0])
        if rc != 0:
            raise Exception("vdbench write failed")
    """升级结束后结束读写与校验文件"""
    p2.join()
    p3.join()

    make_fault.up_eth(network_fault_ip, eth_list, ip_mask_lst)


def main():
    upgrade_common.delete_upgrade()
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    upgrade_common.delete_upgrade()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

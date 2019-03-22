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
# Date: 2018-08-27
# @summary：
#       路径挂载后，发现get_services获取的oApp的状态是SHUTDOWN，get_nodes获取的oApp的状态是OK
# @steps:
#       1、执行get_services 查看所有服务状态
#       2、执行get_nodes 查看所有服务状态
#       3、进行比较
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字


def case():
    log.info("case begin")
    get_services_list = []  # 每个元素是一个节点的服务状态字典
    get_services_dict = {}
    get_nodes_list = []  # 每个元素是一个节点的服务状态字典
    get_nodes_dict = {}
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    log.info("nodeid_list")
    log.info(node_id_lst)
    log.info("1> 执行get_services 查看所有服务状态")
    for nodeid in node_id_lst:
        rc, stdout = common.get_services(node_ids=nodeid)
        pscli_info = common.json_loads(stdout)
        for service in pscli_info['result']['nodes'][0]['services']:
            get_services_dict[service['service_type']] = service['inTimeStatus']
        get_services_list.append(get_services_dict)

    log.info("2> 执行get_nodes 查看所有服务状态")
    for nodeid in node_id_lst:
        rc, stdout = common.get_nodes(ids=nodeid)
        pscli_info = common.json_loads(stdout)
        for service in pscli_info['result']['nodes'][0]['services']:
            get_nodes_dict[service['service_type']] = service['inTimeStatus']
        get_nodes_list.append(get_nodes_dict)
    log.info("3> 进行比较")
    for i in range(len(get_services_list)):
        for service_name in get_services_dict:
            log.info("%s  get_services %s ;get_nodes %s"
                     % (service_name, get_services_dict[service_name], get_nodes_dict[service_name]))
            if get_services_dict[service_name] != get_nodes_dict[service_name]:
                common.except_exit("service %s: get_services get_nodes not equal " % service_name)

    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)

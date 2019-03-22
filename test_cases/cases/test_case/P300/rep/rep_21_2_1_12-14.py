# -*-coding:utf-8 -*
import os
import time
import sys

import utils_path
import common
import snap_common
import log
import prepare_clean
import rep_common
import random

####################################################################################
#
# Author: chenjy1
# Date 20181218
# @summary：
#    有复制域，无节点时创建通道
#    从端复制域disable某节点后，输入此ip创建通道
#    不支持对虚ip
# @steps:
#    1、[主从]创建复制域(节点数>=4随机)
#    2、[主]创建对于从端虚ip的通道
#    3、[主]disable_rep某节点(剩余三个)
#    4、[主]创建对于disable_rep的节点的通道
#    5、[主]所有节点disable_rep
#    6、[主]创建对于从端的通道
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]

def case():
    log.info('case begin')
    rc, master_all_id_lst = rep_common.get_node_id_lst()
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    if len(master_all_id_lst) <= 3:
        log.warn('节点数不大于3个，未满足此脚本运行条件')
        sys.exit(-1)
    rc, slave_all_id_lst = rep_common.get_node_id_lst(run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    if len(slave_all_id_lst) <= 3:
        log.warn('节点数不大于3个，未满足此脚本运行条件')
        sys.exit(-1)
    master_id_lst = random.sample(master_all_id_lst, 4)
    slave_id_lst = random.sample(slave_all_id_lst, 4)

    log.info('1>[主从]创建4节点复制域')
    master_nodeid_str = rep_common.convert_lst_to_str(master_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=master_nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    slave_nodeid_str = rep_common.convert_lst_to_str(slave_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=slave_nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    log.info('2>[主]创建通道，ip为从端虚ip的通道')
    '''
    rc, stdout = common.get_virtual_ip()
    common.judge_rc(rc, 0, 'get_virtual_ip faield')
    pscli_info = common.json_loads(stdout)
    # todo 获取从端虚ip
    virt_ip =
    rc, pscli_info = rep_common.create_rep_channel(name=FILE_NAME, ip=virt_ip)
    common.judge_rc_unequal(rc, 0, 'enable_rep_server failed')
    '''

    log.info('3>[从]disable 某节点rep服务')
    rc, pscli_info = rep_common.disable_rep_server(master_id_lst[-1])
    common.judge_rc(rc, 0, 'disable_rep_server failed')

    log.info('4> [主]创建对于disable_rep的节点的通道')
    rc, stdout = common.get_nodes(master_id_lst[-1], run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'get_nodes failed')
    node_ip = common.json_loads(stdout)['result']['nodes'][0]['ctl_ips'][0]['ip_address']
    rc, pscli_info = rep_common.create_rep_channel(name=FILE_NAME, ip=node_ip)
    common.judge_rc_unequal(rc, 0, 'create_rep_channel failed')

    log.info('5> [主]所有节点disable_rep')
    rc = rep_common.disable_all_rep_server(run_cluster=rep_common.MASTER)
    common.judge_rc(rc, 0, 'disable_all_rep_server failed')

    log.info('6> [主]创建对于从端的通道')
    rc, stdout = common.get_nodes(master_id_lst[0], run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'get_nodes failed')
    node_ip = common.json_loads(stdout)['result']['nodes'][0]['ctl_ips'][0]['ip_address']

    rc, pscli_info = rep_common.create_rep_channel(name=FILE_NAME, ip=node_ip)
    common.judge_rc_unequal(rc, 0, 'create_rep_channel successful')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST, node_num=4)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

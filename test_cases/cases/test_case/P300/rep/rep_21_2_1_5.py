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
#    对多集群创建多个通道
# @steps:
#    1、判断是否有第三集群
#    2、[主从三]创建复制域(节点数=3)
#    3、[主]对从端和第三端创建通道
#    4、[从]对第三端创建通道
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]

def check_third_cluster_exist():
    '''
    author:      chenjy1
    date:        20190109
    descrioton:  获取主从端sysid
    :return:    sysid_lst
    '''
    get_ctlip = []
    rc, stdout = common.get_node_stat(print_flag=True, run_cluster=rep_common.THIRD)
    if rc !=0:
        log.warn('未发现第3集群，不满足此脚本测试条件')
        sys.exit(-1)
    common.judge_rc(rc, 0, 'get_node_stat failed')
    rc, stdout = common.get_nodes(print_flag=False, run_cluster=rep_common.THIRD)
    if rc !=0:
        log.warn('未发现第3集群，不满足此脚本测试条件')
        sys.exit(-1)
    pscli_info = common.json_loads(stdout)
    for node in pscli_info['result']['nodes']:
        get_ctlip.append(node['ctl_ips'][0]['ip_address'])

    if len(get_ctlip) != rep_common.THIRD_NODE_LST:
        log.warn('未发现第3集群，不满足此脚本测试条件')
        sys.exit(-1)
    for ip in get_ctlip:
        if ip not in rep_common.THIRD_NODE_LST:
            log.warn('未发现第3集群，不满足此脚本测试条件')
            sys.exit(-1)
    for ip in rep_common.THIRD_NODE_LST:
        if ip not in get_ctlip:
            log.warn('未发现第3集群，不满足此脚本测试条件')
            sys.exit(-1)



def case():
    log.info('case begin')
    log.info('1>判断是否有第三集群')
    check_third_cluster_exist()

    rc, master_all_id_lst = rep_common.get_node_id_lst()
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    rc, salve_all_id_lst = rep_common.get_node_id_lst(run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    rc, third_all_id_lst = rep_common.get_node_id_lst(run_cluster=rep_common.THIRD)
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    master_id_lst = random.sample(master_all_id_lst, 3)
    slave_id_lst = random.sample(salve_all_id_lst, 3)
    third_id_lst = random.sample(salve_all_id_lst, 3)

    log.info('2>[主从三]创建复制域(节点数=3)')
    master_nodeid_str = rep_common.convert_lst_to_str(master_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=master_nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    slave_nodeid_str = rep_common.convert_lst_to_str(slave_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=slave_nodeid_str,run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    third_nodeid_str = rep_common.convert_lst_to_str(third_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=third_nodeid_str, run_cluster=rep_common.THIRD)
    common.judge_rc(rc, 0, 'enable_rep_server failed')


    log.info('3>[主]对从端和第三端创建通道')
    rc, pscli_info = rep_common.create_rep_channel(name=FILE_NAME, ip=rep_common.SLAVE_NODE_LST[0])
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    rc, pscli_info = rep_common.create_rep_channel(name=FILE_NAME, ip=rep_common.THIRD_NODE_LST[0])
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    log.info('4>[从]对第三端创建通道')
    rc, pscli_info = rep_common.create_rep_channel(name=FILE_NAME, ip=rep_common.THIRD_NODE_LST[0],run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

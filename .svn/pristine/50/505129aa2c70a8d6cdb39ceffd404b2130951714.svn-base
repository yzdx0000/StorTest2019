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
#    不支持对sysid一样的集群创建通道（用例作废，因为假设不同集群的sysid是不同的）
# @steps:
#    1、判断主从sysid是否一样，不同则脚本退出
#    2、[主从]创建复制域(节点数>=3随机)
#    3、[主]创建通道(管理网数据网随机)
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]

def check_sysid():
    '''
    author:      chenjy1
    date:        20190109
    descrioton:  获取主从端sysid
    :return:    sysid_lst
    '''
    sysid_lst = []
    for cluster in [rep_common.MASTER, rep_common.SLAVE]:
        rc, stdout = common.get_cluster_overview(run_cluster=cluster)
        common.judge_rc(rc, 0, 'get_cluster_overview failed')
        pscli_info = common.json_loads(stdout)
        sysid_lst.append(pscli_info['result']['sysid'])
    return sysid_lst


def case():
    log.info('case begin')
    log.info('1>判断主从sysid是否一样，不同则脚本退出')
    sysid_lst = check_sysid()
    if sysid_lst[0] == sysid_lst[1]:
        log.warn('两集群的sysid不同，不满足此脚本测试条件')
        sys.exit(-1)

    rc, master_all_id_lst = rep_common.get_node_id_lst()
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    rc, salve_all_id_lst = rep_common.get_node_id_lst(run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    master_id_lst = random.sample(master_all_id_lst, 3)
    salve_id_lst = random.sample(salve_all_id_lst, 3)

    log.info('2>[主从]创建3节点复制域')
    master_nodeid_str = rep_common.convert_lst_to_str(master_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=master_nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    log.info('3>[主]创建通道，ip为从端某节点管理网')
    rc, pscli_info = rep_common.create_rep_channel(name=FILE_NAME, ip=rep_common.SLAVE_NODE_LST[0])
    common.judge_rc_unequal(rc, 0, 'enable_rep_server failed')


    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

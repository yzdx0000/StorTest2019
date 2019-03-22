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
#    创建通道相关测试
# @steps:
#    1、主端创建3节点复制域
#    2、主端创建通道，ip为从端某节点管理网
#    3、从端创建3节点复制域
#    4、主端创建通道，ip为从端域内某节点管理网
#    5、主端创建通道，ip为从端域内另一节点管理网
#    6、主端创建通道，ip为从端域外另一节点管理网
#    7、主端删除通道
#    8、主端创建通道，写不存在的ip
#    9、以上步骤，均get_rep_channel查看通道
#    10、清除环境
#
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
    rc, salve_all_id_lst = rep_common.get_node_id_lst(run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    if len(salve_all_id_lst) <= 3:
        log.warn('节点数不大于3个，未满足此脚本运行条件')
        sys.exit(-1)
    master_id_lst = random.sample(master_all_id_lst, 3)
    salve_id_lst = random.sample(salve_all_id_lst, 3)
    master_left_id_lst = master_all_id_lst
    salve_left_id_lst = salve_all_id_lst
    for i in master_all_id_lst:
        master_left_id_lst.remove(i)
    for i in salve_all_id_lst:
        salve_left_id_lst.remove(i)

    log.info('1>[主从]创建3节点复制域')
    master_nodeid_str = rep_common.convert_lst_to_str(master_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=master_nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    log.info('2>[主]创建通道，ip为从端某节点管理网')
    rc, pscli_info = rep_common.create_rep_channel(name=FILE_NAME, ip=rep_common.SLAVE_NODE_LST[0])
    common.judge_rc_unequal(rc, 0, 'enable_rep_server failed')

    log.info('3>[从]创建3节点复制域')
    master_nodeid_str = rep_common.convert_lst_to_str(salve_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=salve_id_lst)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    log.info('4>[主]创建通道，ip为从端域内某节点管理网')
    rc, create_channel_ip = rep_common.ip_for_create_channel(salve_id_lst, run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'ip_for_create_channel failed')
    rc, stdout = common.create_rep_channel(ip=create_channel_ip)
    common.judge_rc(rc, 0, 'create_rep_channel failed')

    log.info('5>[主]创建通道，ip为从端域内另一节点管理or数据网')
    same_cluster_ip = ''
    while True:
        rc, same_cluster_ip = rep_common.ip_for_create_channel(salve_id_lst, run_cluster=rep_common.SLAVE)
        common.judge_rc(rc, 0, 'ip_for_create_channel failed')
        if same_cluster_ip != create_channel_ip:
            break
    rc, stdout = common.create_rep_channel(ip=same_cluster_ip)
    common.judge_rc_unequal(rc, 0, 'create_rep_channel failed')

    log.info('6>[主]创建通道，ip为从端域外节点管理or数据网')
    rc, salve_other_ip = rep_common.ip_for_create_channel(salve_left_id_lst, run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'ip_for_create_channel failed')
    rc, stdout = common.create_rep_channel(ip=salve_other_ip)
    common.judge_rc_unequal(rc, 0, 'create_rep_channel failed')

    log.info('7>[主]删除通道')
    rc, channelid = rep_common.get_channel_id_by_ip(create_channel_ip)
    common.judge_rc(rc, 0, 'get_channel_id_by_ip failed')
    rc, pscli_info = rep_common.delete_rep_channel(channelid)
    common.judge_rc(rc, 0, 'delete_rep_channel failed')

    log.info('8>[主]创建通道，写不存在的ip')
    no_exist_ip = '80.80.80.80'
    rc, stdout = common.create_rep_channel(ip=no_exist_ip)
    common.judge_rc_unequal(rc, 0, 'create_rep_channel failed')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

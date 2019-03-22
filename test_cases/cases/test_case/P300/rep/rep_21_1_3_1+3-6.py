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
#    测试删除复制域的功能
# @steps:
#    1、3节点加入复制域
#    2、复制域逐个删除节点
#    3、3节点再次加入
#    4、同时删除所有节点
#    5、已无rep服务不能再次删除
#    6、已存在通道的情况下，不支持删除复制域
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
NEED_CLUSTER_LIST = [rep_common.MASTER,rep_common.SLAVE]


def case():
    log.info('case begin')

    rc, id_lst = rep_common.get_node_id_lst()
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    choose_node_id = random.choice(id_lst)
    nodeid_str = rep_common.convert_lst_to_str(id_lst)

    rc, slave_id_lst = rep_common.get_node_id_lst(run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    slave_id_str = rep_common.convert_lst_to_str(slave_id_lst)
    
    part_id_lst = id_lst[:-1]
    left_id = id_lst[-1]
    choose_node_id_in_part_lst = random.choice(part_id_lst)
    part_id_str = rep_common.convert_lst_to_str(part_id_lst)

    log.info('复制域修改节点')
    '''先加入部分节点'''
    rc, pscli_info = rep_common.enable_rep_server(node_ids=part_id_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')
    '''在删除一个节点'''
    rc, pscli_info = rep_common.disable_rep_server(node_ids=choose_node_id_in_part_lst)
    common.judge_rc(rc, 0, 'disable_rep_server failed')
    part_id_lst.append(choose_node_id_in_part_lst)
    '''加入另一个节点'''
    rc, pscli_info = rep_common.enable_rep_server(node_ids=left_id)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    part_id_lst.remove(choose_node_id_in_part_lst)
    part_id_lst.append(left_id)

    """删除所选参数即有域内也有域外"""
    rc, pscli_info = rep_common.disable_rep_server(node_ids=nodeid_str)
    common.judge_rc(rc, 0, 'disable_rep_server succeessful')

    '''恢复至域内无节点'''
    rc, pscli_info = rep_common.disable_rep_server(node_ids=left_id)
    common.judge_rc(rc, 0, 'disable_rep_server failed')

    log.info('双端所有节点（需>=3）加入复制域')
    rc, pscli_info = rep_common.enable_rep_server(node_ids=nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    log.info('复制域逐个删除节点')  # todo 开发实现会有变化
    for id in id_lst:
        rc, pscli_info = rep_common.disable_rep_server(node_ids=id)
        common.judge_rc(rc, 0, 'disable_rep_server failed')


    log.info('双端所有节点（需>=3）加入复制域')
    rc, pscli_info = rep_common.enable_rep_server(node_ids=nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    log.info('同时删除所有节点')
    rc, pscli_info = rep_common.disable_rep_server(node_ids=nodeid_str)
    common.judge_rc(rc, 0, 'disable_rep_server failed')

    log.info('已无rep服务再次删除')
    rc, pscli_info = rep_common.disable_rep_server(node_ids=nodeid_str)
    common.judge_rc(rc, 0, 'disable_rep_server failed')
    rc, pscli_info = rep_common.disable_rep_server(node_ids=choose_node_id)
    common.judge_rc(rc, 0, 'disable_rep_server failed')

    log.info('已存在通道的情况下，不支持删除复制域')
    """主端创建复制域"""
    rc, pscli_info = rep_common.enable_rep_server(node_ids=nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    """从端创建复制域"""
    rc, pscli_info = rep_common.enable_rep_server(node_ids=slave_id_str, run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    """创建通道"""
    rc, channelip = rep_common.ip_for_create_channel(slave_id_lst, run_cluster=rep_common.SLAVE)
    rc, pscli_info = rep_common.create_rep_channel(name=FILE_NAME, ip=channelip)
    common.judge_rc(rc, 0, 'create_rep_channel failed')

    """主端删除复制域"""
    rc, pscli_info = rep_common.disable_rep_server(node_ids=nodeid_str)
    common.judge_rc_unequal(rc, 0, 'disable_rep_server failed')

    """从端删除复制域"""
    rc, pscli_info = rep_common.disable_rep_server(node_ids=slave_id_str, run_cluster=rep_common.SLAVE)
    common.judge_rc_unequal(rc, 0, 'disable_rep_server failed')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

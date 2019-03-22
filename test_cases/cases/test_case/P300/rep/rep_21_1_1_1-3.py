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
#    不支持单个节点创建复制域
#    节点数>=3节点数随机加入复制域,
#    已有rep服务不支持再次添加
# @steps:
#    1、所有节点（需>=3）加入复制域
#    2、已有rep服务再次添加
#    3、单节点加入复制域
#    4、3节点加入复制域
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
NEED_CLUSTER_LIST = [rep_common.MASTER]

def case():
    rc, id_lst = rep_common.get_node_id_lst()
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    choose_node_id = random.choice(id_lst)


    log.info('1>所有节点（需>=3）加入复制域')
    nodeid_str = rep_common.convert_lst_to_str(id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    log.info('2>已有rep服务再次添加')
    rc, pscli_info = rep_common.enable_rep_server(node_ids=choose_node_id)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    nodeid_str = rep_common.convert_lst_to_str(id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    '''清除复制域'''
    rc, pscli_info = rep_common.disable_rep_server(node_ids=nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')


    log.info('3>单节点加入复制域')
    rc, pscli_info = rep_common.enable_rep_server(node_ids=choose_node_id)
    common.judge_rc_unequal(rc, 0, 'enable_rep_server successful')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

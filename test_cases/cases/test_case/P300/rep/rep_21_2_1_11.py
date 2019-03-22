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
#    不存在复制域时创建通道
# @steps:
#    1> [主]检查集群是否有复制域
#    2> [主]如无复制域，创建通道
#    3> 清理从端复制域
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]

def case():
    log.info('case begin')

    log.info('1> [主]检查集群是否有复制域')
    rc, pscli_info = rep_common.get_rep_area()
    common.judge_rc(rc, 0, 'get_rep_area failed')
    if pscli_info['result'] != '':
        log.warn('There are replication domains in the cluster, case will be skipped')
        sys.exit(-1)

    log.info('2> [主]如无复制域，创建通道')
    rc, s_node_id_lst = rep_common.get_node_id_lst(run_cluster=rep_common.MASTER)
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    nodeid_str = rep_common.convert_lst_to_str(s_node_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=nodeid_str, run_cluster=rep_common.MASTER)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    rc, channelip = rep_common.ip_for_create_channel(s_node_id_lst, run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'ip_for_create_channel failed')
    rc, pscli_info = rep_common.create_rep_channel(name=FILE_NAME, ip=channelip)
    common.judge_rc_unequal(rc, 0, 'create_rep_channel failed')

    log.info('3> 清理从端复制域')
    rc = rep_common.disable_all_rep_server(run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'disable_all_rep_server failed')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

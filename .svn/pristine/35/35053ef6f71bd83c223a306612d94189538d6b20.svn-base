# -*-coding:utf-8 -*
import os
import time

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
#    删除通道相关测试
# @steps:
#    1、不创建复制域，直接创建通道
#    2、双端创建3节点复制域
#    3、主端正常创建通道
#    4、主端正常创建pair
#    5、主端删除通道
#    6、主端删除pair
#    7、主端删除通道
#    8、清除环境
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(salve)parastor/(salve)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]

def case():
    log.info('case begin')
    master_id_lst = []
    salve_id_lst = []
    rc, master_all_id_lst = rep_common.get_node_id_lst()
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    rc, slave_all_id_lst = rep_common.get_node_id_lst(run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'get_node_id_lst failed')

    if rep_common.REP_DOMAIN == rep_common.THREE:
        master_id_lst = master_all_id_lst[0:3]
        slave_id_lst = slave_all_id_lst[0:3]
    else:
        master_id_lst = master_all_id_lst
        slave_id_lst = slave_all_id_lst

    log.info('1>[主]创建通道，ip为从端域内某节点管理网')
    rc, stdout = common.create_rep_channel(ip=rep_common.SLAVE_NODE_LST[0])
    common.judge_rc_unequal(rc, 0, 'create_rep_channel failed')

    log.info('2>[从]创建3节点复制域')
    slave_nodeid_str = rep_common.convert_lst_to_str(slave_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=slave_nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    rc, stdout = common.create_rep_channel(ip=rep_common.SLAVE_NODE_LST[0])
    common.judge_rc_unequal(rc, 0, 'create_rep_channel failed')

    log.info('3>[主]创建3节点复制域')
    master_nodeid_str = rep_common.convert_lst_to_str(master_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=master_nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    log.info('4>[主]创建通道，ip为从端域内某节点管理网')
    rc, create_channel_ip = rep_common.ip_for_create_channel(salve_id_lst, run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'ip_for_create_channel failed')
    rc, stdout = common.create_rep_channel(ip=create_channel_ip)
    common.judge_rc(rc, 0, 'create_rep_channel failed')

    log.info('5>[主]创建pair')
    rc, channelid = rep_common.get_channel_id_by_ip(create_channel_ip)
    common.judge_rc(rc, 0, 'get_channel_id_by_ip failed')
    rc, pscli_info = rep_common.create_rep_pair(rep_channel_id=channelid, source_directory=FILE_MASTER_PATH,
                                                destination_directory=FILE_SLAVE_PATH)
    common.judge_rc(rc, 0, 'create_rep_pair failed')

    log.info('6>[主]刪除通道')
    rc, pscli_info = rep_common.delete_rep_channel(channelid)
    common.judge_rc(rc, 0, 'delete_rep_channel failed')

    log.info('7>[主]刪除pair')
    rc, pair_id = rep_common.get_one_pair_id()
    common.judge_rc(rc, 0, 'get_one_pair_id failed')
    rc, pscli_info = rep_common.delete_rep_pair(id=pair_id)
    common.judge_rc_unequal(rc, 0, 'delete_rep_channel failed')

    log.info('8>[主]刪除通道')
    rc, pscli_info = rep_common.delete_rep_channel(channelid)
    common.judge_rc(rc, 0, 'delete_rep_channel failed')


    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

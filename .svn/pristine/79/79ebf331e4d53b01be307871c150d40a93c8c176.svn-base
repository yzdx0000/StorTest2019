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
import quota_common

####################################################################################
#
# Author: chenjy1
# Date 20181218
# @summary：
#    测试获取从端目录
# @steps:
#    1、从端创建3层目录：/a/b[1..100]/c[1..100]
#    2、双端创建3节点复制域
#    3、主端创建通道
#    4、主端逐层、分页获取从端目录
#    5、主端获取/a目录，从端删除/a/b1，主端获取/a/b1目录
#    6、从端/a/b2/c2下创建文件，主端获取/a/b2/c2
#    7、清除环境
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

    log.info('1>[从]创建3层目录：/a/b[1..100]/c[1..100]')
    rc = rep_common.create_dir_tree(rep_common.SLAVE_NODE_LST[0], anchor_path=FILE_SLAVE_PATH, depth=2, width=100)
    common.judge_rc(rc, 0, 'create_dir_tree failed')
    log.info('2>[主从]创建3节点复制域')
    master_nodeid_str = rep_common.convert_lst_to_str(master_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=master_nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')
    slave_nodeid_str = rep_common.convert_lst_to_str(slave_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=slave_nodeid_str, run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    log.info('3>[主]正常创建通道')
    rc, create_channel_ip = rep_common.ip_for_create_channel(salve_id_lst, run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'ip_for_create_channel failed')
    rc, stdout = common.create_rep_channel(ip=create_channel_ip)
    common.judge_rc(rc, 0, 'create_rep_channel failed')
    rc, channelid = rep_common.get_channel_id_by_ip(ip=create_channel_ip, run_cluster=rep_common.MASTER)
    common.judge_rc(rc, 0, 'get_channel_id_by_ip failed')

    log.info('4>主端逐层、分页获取从端目录')
    basedir = FILE_SLAVE_PATH
    rc, pscli_info = rep_common.get_rep_remote_dir(channel_id=channelid, parent_dir=basedir, page_number=1)
    common.judge_rc(rc, 0, 'get_rep_remote_dir failed')

    log.info('5>主端获取/a目录，从端删除/a/b1，主端获取/a/b1目录')
    '''获取basedir目录下的目录'''
    rc, pscli_info = rep_common.get_rep_remote_dir(channel_id=channelid, parent_dir=basedir, page_number=1)
    common.judge_rc(rc, 0, 'get_rep_remote_dir failed')
    '''从端删除basedir/vdb1_1.dir'''
    rc, stdout = common.rm_exe(rep_common.SLAVE_NODE_LST[0], os.path.join(basedir, 'vdb1_1.dir'))
    common.judge_rc(rc, 0, 'rm_exe failed')
    rc, pscli_info = rep_common.get_rep_remote_dir(channel_id=channelid, parent_dir=basedir, page_number=1)
    common.judge_rc(rc, 0, 'get_rep_remote_dir failed')
    '''判断vdb1_1.dir是否还在'''

    '''获取不存在的目录'''
    rc, pscli_info = rep_common.get_rep_remote_dir(channel_id=channelid, parent_dir=os.path.join(basedir, 'vdb1_1.dir'),
                                                   page_number=1)
    common.judge_rc(rc, 0, 'get_rep_remote_dir failed')

    log.info('6>从端/a/b2/c2下创建文件，主端获取/a/b2/c2')
    quota_common.creating_files(rep_common.SLAVE_NODE_LST[0], os.path.join(basedir, 'vdb1_2.dir'), 1, 1, 'test')
    rc, pscli_info = rep_common.get_rep_remote_dir(channel_id=channelid, parent_dir=basedir, page_number=1)
    common.judge_rc(rc, 0, 'get_rep_remote_dir failed')
    '''检查'''


    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

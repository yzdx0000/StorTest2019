# -*-coding:utf-8 -*
from multiprocessing import Process
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
#    创建pair相关
# @steps:
#    1、主从双端创建复制域
#    2、主端创建通道
#    3、主端创建单个pair
#    4、子进程N，同时创建N个pair
#    5、创建pair，主端目录不存在/为空
#    6、创建pair，从端目录非空/不存在
#    7、主端/a创建到从端/x   /y 的两个pair
#    8、主端/x、  /y 分别创建到从端 /a的两个pair
#    9、双端反向创建pair
#    10、创建一个已存在的pair
#    11、清除环境
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(slave)parastor/(slave)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]
THREADS_NUMBER = 20


def create_rep_pair(rep_channel_id=None, source_directory=None, destination_directory=None, print_flag=True,
                    fault_node_ip=None, run_cluster=rep_common.MASTER):
    rc, pscli_info = rep_common.create_rep_pair(rep_channel_id=rep_channel_id, source_directory=source_directory,
                                                destination_directory=destination_directory,print_flag=print_flag,
                                                fault_node_ip=fault_node_ip, run_cluster=run_cluster)
    common.judge_rc(rc, 0, 'create_rep_pair failed')


def case():
    log.info('case begin')
    master_id_lst = []
    slave_id_lst = []
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

    log.info('1>[主从]创建3节点复制域')
    master_nodeid_str = rep_common.convert_lst_to_str(master_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=master_nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')
    slave_nodeid_str = rep_common.convert_lst_to_str(slave_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=slave_nodeid_str, run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    log.info('2>[主]正常创建通道')
    rc, create_channel_ip = rep_common.ip_for_create_channel(slave_id_lst, run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'ip_for_create_channel failed')
    rc, stdout = common.create_rep_channel(ip=create_channel_ip)
    common.judge_rc(rc, 0, 'create_rep_channel failed')

    rc, channelid = rep_common.get_channel_id_by_ip(ip=create_channel_ip)
    common.judge_rc(rc, 0, 'get_rep_channels failed')

    log.info('3>[主]创建单个pair')
    '''先创建目录'''
    m_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, FILE_NAME, THREADS_NUMBER+1)
    s_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, FILE_NAME, THREADS_NUMBER + 1)
    rc, pscli_info = rep_common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[-1],
                                                destination_directory=s_dir_lst[-1])
    common.judge_rc(rc, 0, 'create_rep_pair failed')

    log.info('4>[主]子进程N，同时创建N个pair')
    pro_lst = []
    for i in range(THREADS_NUMBER):
        pro_lst.append(Process(target=create_rep_pair, args=(channelid, m_dir_lst[i], s_dir_lst[i])))
    for i in range(THREADS_NUMBER):
        pro_lst[i].start()
    for i in range(THREADS_NUMBER):
        pro_lst[i].join()
        common.judge_rc(0, pro_lst[i].exitcode,
                        'create_rep_pair failed  s_dir:%s ,d_dir:%s' % (m_dir_lst[i], s_dir_lst[i]))
    log.info('5>创建pair，主端目录不存在/为空')
    '''构造主从临时目录'''
    m_tmp_dir = os.path.join(FILE_MASTER_PATH, 'tmp_dir')
    common.mkdir_path(rep_common.MASTER_NODE_LST[0], m_tmp_dir)
    s_tmp_dir = os.path.join(FILE_SLAVE_PATH, 'tmp_dir')
    common.mkdir_path(rep_common.MASTER_NODE_LST[0], s_tmp_dir)
    '''不存在目录'''
    m_no_exist_dir = os.path.join(FILE_MASTER_PATH, 'no_exist')
    s_no_exist_dir = os.path.join(FILE_SLAVE_PATH, 'no_exist')
    rc, pscli_info = rep_common.create_rep_pair(rep_channel_id=channelid, source_directory=m_no_exist_dir,
                                                destination_directory=s_tmp_dir)
    common.judge_rc_unequal(rc, 0, 'create_rep_pair failed')
    '''为空'''
    rc, pscli_info = rep_common.create_rep_pair(rep_channel_id=channelid, source_directory=' ',
                                                destination_directory=s_tmp_dir)
    common.judge_rc_unequal(rc, 0, 'create_rep_pair failed')

    log.info('6>创建pair，从端目录非空/不存在')
    '''从端目录非空'''
    rep_common.create_file(rep_common.SLAVE_NODE_LST[0], s_tmp_dir, 'tmp', 1, 1)
    rc, pscli_info = rep_common.create_rep_pair(rep_channel_id=channelid, source_directory=m_tmp_dir,
                                                destination_directory=s_tmp_dir)
    common.judge_rc_unequal(rc, 0, 'create_rep_pair failed')
    '''从端目录不存在'''
    rc, pscli_info = rep_common.create_rep_pair(rep_channel_id=channelid, source_directory=m_tmp_dir,
                                                destination_directory=s_no_exist_dir)
    common.judge_rc_unequal(rc, 0, 'create_rep_pair failed')

    log.info('7>主端/a创建到从端/x   /y 的两个pair')
    s_mul_basename = FILE_NAME + 'mul'
    s_dir_mul_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, s_mul_basename, 2)
    for i in s_no_exist_dir:
        rc, pscli_info = rep_common.create_rep_pair(rep_channel_id=channelid, source_directory=m_tmp_dir,
                                                    destination_directory=i)
        common.judge_rc(rc, 0, 'create_rep_pair failed')
    log.info('8>主端/x、  /y 分别创建到从端 /a的两个pair')
    m_mul_basename = FILE_NAME + 'mul'
    m_dir_mul_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, m_mul_basename, 2)
    rc, pscli_info = rep_common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_mul_lst[0],
                                                destination_directory=s_tmp_dir)
    common.judge_rc(rc, 0, 'create_rep_pair failed')
    rc, pscli_info = rep_common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_mul_lst[1],
                                                destination_directory=s_tmp_dir)
    common.judge_rc_unequal(rc, 0, 'create_rep_pair failed')

    log.info('9>双端反向创建pair')
    m_two_way_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'two_way', 2)
    s_two_way_dir_lst = rep_common.create_dir(rep_common.SLAVE_NODE_LST[0], FILE_SLAVE_PATH, 'two_way', 2)
    rc, pscli_info = rep_common.create_rep_pair(rep_channel_id=channelid, source_directory=m_two_way_dir_lst[0],
                                                destination_directory=s_two_way_dir_lst[0])
    common.judge_rc(rc, 0, 'create_rep_pair failed')
    rc, pscli_info = rep_common.create_rep_pair(rep_channel_id=channelid, source_directory=m_two_way_dir_lst[1],
                                                destination_directory=s_two_way_dir_lst[1],
                                                run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'create_rep_pair failed')

    log.info('10>创建一个已经存在的pair')
    rc, pscli_info = rep_common.create_rep_pair(rep_channel_id=channelid, source_directory=m_two_way_dir_lst[1],
                                                destination_directory=s_two_way_dir_lst[1],
                                                run_cluster=rep_common.SLAVE)
    common.judge_rc_unequal(rc, 0, 'create_rep_pair failed')


    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

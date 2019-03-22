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
#    pair参数检测
# @steps:
#    1、双端创建3节点复制域，主端创建通道
#    2、创建pair，通道id非法/源目录非法/目的目录非法
#    3、主端正常创建pair，
#    4、主端删除pair id不存在/非法
#    5、查看pair id不存在/非法
#    6、恢复pair id不存在/非法
#    7、分裂pair id不存在/非法
#    8、清除环境
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(slave)parastor/(slave)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]
THREADS_NUMBER = 20
CHANNEL_ID_ZERO = 0
BUTTON = True


def delete_rep_pair(id=None, print_flag=True, fault_node_ip=None, run_cluster=rep_common.MASTER):
    rc, pscli_info = rep_common.delete_rep_pair(id=id, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                                run_cluster=run_cluster)
    common.judge_rc(rc, 0, 'create_rep_pair failed')


def case():
    log.info('case begin')
    master_id_lst = []
    slave_id_lst = []

    if BUTTON is True:
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

        log.info('1>创建复制域及通道')
        master_nodeid_str = rep_common.convert_lst_to_str(master_id_lst)
        rc, pscli_info = rep_common.enable_rep_server(node_ids=master_nodeid_str)
        common.judge_rc(rc, 0, 'enable_rep_server failed')
        slave_nodeid_str = rep_common.convert_lst_to_str(slave_id_lst)
        rc, pscli_info = rep_common.enable_rep_server(node_ids=slave_nodeid_str, run_cluster=rep_common.SLAVE)
        common.judge_rc(rc, 0, 'enable_rep_server failed')

        rc, create_channel_ip = rep_common.ip_for_create_channel(slave_id_lst, run_cluster=rep_common.SLAVE)
        common.judge_rc(rc, 0, 'ip_for_create_channel failed')
        rc, stdout = common.create_rep_channel(ip=create_channel_ip)
        common.judge_rc(rc, 0, 'create_rep_channel failed')

        rc, channelid = rep_common.get_channel_id_by_ip(ip=create_channel_ip)
        common.judge_rc(rc, 0, 'get_rep_channels failed')
    else:
        master_id_lst = [1, 2, 3]
        slave_id_lst = [1, 2, 3]
        channelid=0


    log.info('2>创建pair，通道id非法/源目录非法/目的目录非法')
    rep_common.generate_wrong_id()
    special_symbol = "~@#$%^*-=+?"
    wrong_id = random.choice(special_symbol)
    m_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir', 2)
    s_dir_lst = rep_common.create_dir(rep_common.SLAVE_NODE_LST[0], FILE_MASTER_PATH, 'dir', 2)
    '''通道id非法'''
    rc, stdout = common.create_rep_pair(rep_channel_id=wrong_id, source_directory=m_dir_lst[0],
                                        destination_directory=s_dir_lst[0])
    common.judge_rc_unequal(rc, 0, 'create_rep_pair successful')

    '''源目录非法'''
    wrong_symbol = random.choice(special_symbol)
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=wrong_symbol,
                                        destination_directory=s_dir_lst[0])
    common.judge_rc_unequal(rc, 0, 'create_rep_pair successful')

    '''目的目录非法'''
    wrong_symbol = random.choice(special_symbol)
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[0],
                                        destination_directory=wrong_symbol)
    common.judge_rc_unequal(rc, 0, 'create_rep_pair successful')

    log.info('3> 主端正常创建pair')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[0],
                                        destination_directory=s_dir_lst[0])
    common.judge_rc(rc, 0, 'create_rep_pair successful')

    log.info('4> 主端删除pair id不存在/非法')
    rc, stdout = common.delete_rep_pair(id=wrong_id)
    common.judge_rc_unequal(rc, 0, 'delete_rep_pair successful')

    rc, stdout = common.delete_rep_pair(id='')
    common.judge_rc_unequal(rc, 0, 'delete_rep_pair successful')

    log.info('5、查看pair ids不存在/非法')
    wrong_str = rep_common.generate_wrong_id()
    rc, stdout = common.get_rep_pairs(ids=wrong_str)
    common.judge_rc_unequal(rc, 0, 'get_rep_pairs successful')
    rc, stdout = common.get_rep_pairs(ids='')
    common.judge_rc_unequal(rc, 0, 'get_rep_pairs successful')

    log.info('6> 恢复pair id不存在/非法')
    wrong_str = rep_common.generate_wrong_id()
    rc, stdout = common.recover_rep_pair(id=wrong_str)
    common.judge_rc_unequal(rc, 0, 'recover_rep_pair successful')
    rc, stdout = common.recover_rep_pair(id='')
    common.judge_rc_unequal(rc, 0, 'recover_rep_pair successful')

    log.info('7、分裂pair id不存在/非法')
    wrong_str = rep_common.generate_wrong_id()
    rc, stdout = common.split_rep_pair(id=wrong_str)
    common.judge_rc_unequal(rc, 0, 'recover_rep_pair successful')
    rc, stdout = common.split_rep_pair(id='')
    common.judge_rc_unequal(rc, 0, 'recover_rep_pair successful')

    log.info('获取从端目录 参数非法/不存在')
    m_dir_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, FILE_SLAVE_PATH, 'dir', 70)
    s_dir_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, m_dir_lst[0], 'dir', 30)

    basedir = FILE_SLAVE_PATH
    '''channelid 错误'''
    wrong_id = rep_common.generate_wrong_id()
    rc, pscli_info = rep_common.get_rep_remote_dir(channel_id=wrong_id, parent_dir=basedir, page_number=2)
    common.judge_rc_unequal(rc, 0, 'get_rep_remote_dir successful')

    '''parent_dir 错误'''
    special_symbol_name = rep_common.generate_special_symbol_name()
    rc, pscli_info = rep_common.get_rep_remote_dir(channel_id=wrong_id, parent_dir=special_symbol_name, page_number=2)
    common.judge_rc_unequal(rc, 0, 'get_rep_remote_dir successful')

    '''page_number 错误'''
    special_symbol_name = rep_common.generate_special_symbol_name()
    rc, pscli_info = rep_common.get_rep_remote_dir(channel_id=wrong_id, parent_dir=basedir,
                                                   page_number=special_symbol_name)
    common.judge_rc_unequal(rc, 0, 'get_rep_remote_dir successful')


    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

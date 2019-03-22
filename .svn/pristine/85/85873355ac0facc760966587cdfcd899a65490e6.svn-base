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
#    中文路径，特殊字符创建pair
# @steps:
#    1、[主从]创建复制域和通道
#    2、[主从]构建中文路径和特殊字符路径
#    3、[主]创建pair，主端中文，从端非中文
#    4、[主]创建pair，主端非中文，从端中文
#    5、[主]创建pair，双端中文
#    5、[主]创建pair，主端特殊字符，从端非特殊字符
#    6、[主]创建pair，主端非特殊字符，从端特殊字符
#    7、[主]创建pair，双端特殊字符
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(salve)parastor/(salve)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]
CHANNEL_ID_ZERO = 0


def case():
    log.info('case begin')
    log.info('1>[主从]准备复制域和通道')
    rc, ready_info = rep_common.format_area_channel()
    common.judge_rc(rc, 0, 'format_area_channel failed')

    log.info('2>[主从]构建中文路径和特殊字符路径')
    special_symbol_name = rep_common.generate_special_symbol_name()
    special_symbol_name = "'" + special_symbol_name + "'"
    m_symbol_dir_lst = rep_common.create_dir(rep_common.MASTER_RANDOM_NODE, FILE_MASTER_PATH, special_symbol_name, 3)
    s_symbol_dir_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, FILE_SLAVE_PATH, special_symbol_name, 3)
    m_chinese_dir_lst = rep_common.create_dir(rep_common.MASTER_RANDOM_NODE, FILE_MASTER_PATH, '目录', 3)
    s_chinese_dir_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, FILE_SLAVE_PATH, '目录', 3)
    m_dir_lst = rep_common.create_dir(rep_common.MASTER_RANDOM_NODE, FILE_MASTER_PATH, 'dir', 3)
    s_dir_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, FILE_SLAVE_PATH, 'dir', 3)

    log.info('3>[主]创建pair，主端中文，从端非中文')
    rc, stdout = common.create_rep_pair(rep_channel_id=ready_info['channel']['result'][0]['id'],
                                        source_directory=m_chinese_dir_lst[0], destination_directory=s_dir_lst[0],
                                        print_flag=True)
    common.judge_rc(rc, 0, 'create_rep_pair failed')

    log.info('4>[主]创建pair，主端非中文，从端中文')
    rc, stdout = common.create_rep_pair(rep_channel_id=ready_info['channel']['result'][0]['id'],
                                        source_directory=m_dir_lst[1], destination_directory=s_chinese_dir_lst[1],
                                        print_flag=True)
    common.judge_rc(rc, 0, 'create_rep_pair failed')

    log.info('5>[主]创建pair，双端中文')
    rc, stdout = common.create_rep_pair(rep_channel_id=ready_info['channel']['result'][0]['id'],
                                        source_directory=m_chinese_dir_lst[2], destination_directory=s_chinese_dir_lst[2],
                                        print_flag=True)
    common.judge_rc(rc, 0, 'create_rep_pair failed')



    log.info('6>[主]创建pair，主端特殊字符，从端非特殊字符')
    rc, stdout = common.create_rep_pair(rep_channel_id=ready_info['channel']['result'][0]['id'],
                                        source_directory=m_dir_lst[0], destination_directory=s_symbol_dir_lst[0],
                                        print_flag=True)
    common.judge_rc(rc, 0, 'create_rep_pair failed')

    log.info('7>[主]创建pair，主端非特殊字符，从端特殊字符')
    rc, stdout = common.create_rep_pair(rep_channel_id=ready_info['channel']['result'][0]['id'],
                                        source_directory=m_symbol_dir_lst[1], destination_directory=s_dir_lst[1],
                                        print_flag=True)
    common.judge_rc(rc, 0, 'create_rep_pair failed')

    log.info('8>[主]创建pair，双端特殊字符')
    rc, stdout = common.create_rep_pair(rep_channel_id=ready_info['channel']['result'][0]['id'],
                                        source_directory=m_symbol_dir_lst[2], destination_directory=s_symbol_dir_lst[2],
                                        print_flag=True)
    common.judge_rc(rc, 0, 'create_rep_pair failed')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

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
#    测试获取从端目录支持中文特殊字符
# @steps:
#    1、[主从]创建复制域和通道
#    2、[从]构造目录/路径[1-70]/  路径1/路径[1-30]
#    3、[主]从第2页开始获取/下目录
#    4、[主]构造目录/特殊字符[1-70]/  特殊字符1/特殊字符[1-30]
#    5、[主]从第2页开始获取/下目录
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

    log.info('2>[从]构造目录/路径[1-70]/  路径1/路径[1-30]')
    first_dir_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, FILE_SLAVE_PATH, '目录', 70)
    second_dir_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, first_dir_lst[0], '目录', 30)

    log.info('3、[主]从第2页开始获取/下目录')
    basedir = FILE_SLAVE_PATH
    rc, pscli_info = rep_common.get_rep_remote_dir(channel_id=CHANNEL_ID_ZERO, parent_dir=basedir, page_number=2)
    common.judge_rc(rc, 0, 'get_rep_remote_dir failed')

    '''判断目录是否正确'''
    special_symbol_name = rep_common.generate_special_symbol_name()
    special_symbol_name = "'" + special_symbol_name + "'"
    log.info('4、[主]构造目录/特殊字符[1-70]/  特殊字符1/特殊字符[1-30]')
    first_dir_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, FILE_SLAVE_PATH, special_symbol_name, 70)
    second_dir_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, first_dir_lst[0], special_symbol_name, 30)
    log.info('5、[主]从第2页开始获取/下目录')
    basedir = FILE_SLAVE_PATH
    rc, pscli_info = rep_common.get_rep_remote_dir(channel_id=CHANNEL_ID_ZERO, parent_dir=basedir, page_number=2)
    common.judge_rc(rc, 0, 'get_rep_remote_dir failed')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

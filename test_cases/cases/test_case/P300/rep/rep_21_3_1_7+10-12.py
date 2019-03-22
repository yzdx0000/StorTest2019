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
#
# @steps:
#    1、[主从]创建复制域和通道
#    2、[主]获取从端/no_exist下的目录
#    3、[从]构造目录/dir[1-30]/  、/dir1/dir[1-30]、/dir1/diraaa...aaa(目录名长度255)、
#            /dir1/diraaaa...aa/dir[1-30](目录名长度255)]
#    4、[主]获取从端/diraaaa...aa下目录
#    5、[主]获取从端/dir1下能否发现diraaa...aaa
#    6、[主]查看从端软连接目录下的目录
#    7、[主]隐藏目录不展示
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(salve)parastor/(salve)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]
CHANNEL_ID_ZERO = 0
NO_EXIST_DIR = os.path.join(FILE_SLAVE_PATH, 'no_exist_dir')


def case():
    log.info('case begin')
    log.info('1>[主从]准备复制域和通道')
    rc, ready_info = rep_common.format_area_channel()
    common.judge_rc(rc, 0, 'format_area_channel failed')

    log.info('2>获取从端不存在的目录')
    #rc, pscli_info = rep_common.get_rep_remote_dir(channel_id=CHANNEL_ID_ZERO, parent_dir=NO_EXIST_DIR, page_number=0)
    #common.judge_rc_unequal(rc, 0, 'get_rep_remote_dir failed')

    log.info('3>[从]构造目录/路径[1-70]/  路径1/路径[1-30]  /dir1下的255长度目录  /下的255长度目录')
    first_dir_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, FILE_SLAVE_PATH, 'dir', 30)
    second_dir_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, first_dir_lst[0], 'dir', 30)
    long_dir_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, FILE_SLAVE_PATH, 'dir' + 'a' * (255-3-1), 1)
    if len(long_dir_lst[0].split('/')[-1]) != 255:
        common.except_exit('script error')
    third_dir_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, long_dir_lst[0], 'dir', 30)

    log.info('4、[主]获取从端/diraaaa...aa下目录')
    rc, pscli_info = rep_common.get_rep_remote_dir(channel_id=CHANNEL_ID_ZERO, parent_dir=long_dir_lst[0],
                                                   page_number=0)
    common.judge_rc(rc, 0, 'get_rep_remote_dir failed')
    # todo 待检查

    log.info('5> [主]获取从端/dir1下能否发现diraaa...aaa')
    rc, pscli_info = rep_common.get_rep_remote_dir(channel_id=CHANNEL_ID_ZERO, parent_dir=first_dir_lst[0],
                                                   page_number=0)
    common.judge_rc(rc, 0, 'get_rep_remote_dir failed')
    # todo 待检查

    log.info('6> [主]查看从端软连接目录下的目录')
    soft_link_src_dir = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, FILE_SLAVE_PATH, 'soft_link_src_dir', 1)
    soft_link_src_second_dir = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE,
                                                     soft_link_src_dir[0], 'dir', 30)
    softlink = os.path.join(FILE_SLAVE_PATH, 'soft')
    rc, stdout = rep_common.create_soft_link(rep_common.SLAVE_RANDOM_NODE, soft_link_src_dir, softlink)
    common.judge_rc(rc, 0, 'create_soft_link failed')

    rc, pscli_info = rep_common.get_rep_remote_dir(channel_id=CHANNEL_ID_ZERO, parent_dir=softlink,
                                                   page_number=0)
    common.judge_rc(rc, 0, 'get_rep_remote_dir failed')

    # todo 待检查

    log.info('7> [主]隐藏目录不展示')
    hide_dir_lst = rep_common.create_dir(rep_common.SLAVE_RANDOM_NODE, FILE_SLAVE_PATH, '.dir', 1)
    rc, pscli_info = rep_common.get_rep_remote_dir(channel_id=CHANNEL_ID_ZERO, parent_dir=FILE_SLAVE_PATH,
                                                   page_number=0)
    common.judge_rc(rc, 0, 'get_rep_remote_dir failed')
    #todo 待检查




    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, False, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, False, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

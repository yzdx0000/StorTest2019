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
#   创建pair的目录字符长度255测试 + 复制数据包含255长度文件名测试
# @steps:
#   - - 创建pair的目录字符长度255测试
#   1、[主从]创建复制域和通道
#   2、[主]创建一个pair，主目录名长度255，起pair任务
#   3、[主]创建一个pair，主目录名长度254，起pair任务
#   4、[主]创建一个pair，主目录名长度256
#   5、[主]创建一个pair，从目录名长度255，起pair任务
#   6、[主]创建一个pair，从目录名长度254，起pair任务
#   7、[主]创建一个pair，从目录名长度256
#   - - 复制数据包含255长度文件名测试
#   8、[主]正常创建pair，主目录下创建255字符长度的目录+文件，起pair任务
#   9、[主]正常创建pair，主目录下创建254字符长度的目录+文件，起pair任务
#   10、[主]正常创建pair，主目录下创建256字符长度的目录+文件，起pair任务
#   11、[主]正常创建pair，主目录下创建300字符长度的目录+文件，起pair任务
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(slave)parastor/(slave)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]
THREADS_NUMBER = 10


def task_and_check(m_dir, s_dir, pairid):
    rc = rep_common.vdb_create(m_dir, '/tmp', rep_common.MASTER_RANDOM_NODE)
    common.judge_rc(rc, 0, 'vdb_create failed ')
    rc, pscli_info = rep_common.start_rep_task_scp(pairid)
    common.judge_rc(rc, 0, 'start_rep_task failed')
    '''检验一致性'''
    rc = rep_common.check_data_consistency(s_dir, '/tmp', [rep_common.MASTER_RANDOM_NODE],
                                           [rep_common.SLAVE_RANDOM_NODE])
    common.judge_rc(rc, 0, 'check_data_consistency failed')


def case():
    log.info('case begin')
    log.info('1>[主从]准备复制域和通道')
    rc, ready_info = rep_common.format_area_channel()
    common.judge_rc(rc, 0, 'format_area_channel failed')
    channelid = ready_info['channel']
    m_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir', 20)
    s_dir_lst = rep_common.create_dir(rep_common.SLAVE_NODE_LST[0], FILE_SLAVE_PATH, 'dir', 20)
    m_255_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir' + 'a'*250, 1)
    s_255_dir_lst = rep_common.create_dir(rep_common.SLAVE_NODE_LST[0], FILE_SLAVE_PATH, 'dir' + 'a'*250, 1)
    m_254_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir' + 'a' * 249, 1)
    s_254_dir_lst = rep_common.create_dir(rep_common.SLAVE_NODE_LST[0], FILE_SLAVE_PATH, 'dir' + 'a' * 249, 1)
    m_256_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir' + 'a' * 251, 1)
    s_256_dir_lst = rep_common.create_dir(rep_common.SLAVE_NODE_LST[0], FILE_SLAVE_PATH, 'dir' + 'a' * 251, 1)


    log.info('2> [主]创建一个pair，主目录名长度255，起pair任务')
    pairid_lst = []
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_255_dir_lst[0],
                                        destination_directory=s_dir_lst[0])
    common.judge_rc(rc, 0, 'create_rep_pair failed')
    rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_255_dir_lst[0],
                                            destination_directory=s_dir_lst[0])
    common.judge_rc(rc, 0, 'get_one_pair_id failed')
    pairid_lst.append(pairid)

    task_and_check(m_255_dir_lst[0], s_dir_lst[0], pairid)

    log.info('3> [主]创建一个pair，主目录名长度254，起pair任务')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_254_dir_lst[0],
                                        destination_directory=s_dir_lst[1])
    common.judge_rc(rc, 0, 'create_rep_pair failed')
    rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_254_dir_lst[0],
                                            destination_directory=s_dir_lst[1])
    common.judge_rc(rc, 0, 'get_one_pair_id failed')
    pairid_lst.append(pairid)
    task_and_check(m_254_dir_lst[0], s_dir_lst[1], pairid)

    log.info('4> [主]创建一个pair，主目录名长度256，起pair任务')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_256_dir_lst[0],
                                        destination_directory=s_dir_lst[2])
    common.judge_rc_unequal(rc, 0, 'create_rep_pair successed')

    log.info('5> [主]创建一个pair，从目录名长度255，起pair任务')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[0],
                                        destination_directory=s_255_dir_lst[0])
    common.judge_rc(rc, 0, 'create_rep_pair failed')
    rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[0],
                                            destination_directory=s_255_dir_lst[0])
    common.judge_rc(rc, 0, 'get_one_pair_id failed')
    pairid_lst.append(pairid)

    task_and_check(m_dir_lst[0], s_255_dir_lst[0], pairid)

    log.info('6> [主]创建一个pair，从目录名长度254，起pair任务')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[1],
                                        destination_directory=s_254_dir_lst[0])
    common.judge_rc(rc, 0, 'create_rep_pair failed')
    rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[1],
                                            destination_directory=s_254_dir_lst[0])
    common.judge_rc(rc, 0, 'get_one_pair_id failed')
    pairid_lst.append(pairid)
    task_and_check(m_dir_lst[1], s_254_dir_lst[0], pairid)

    log.info('7> [主]创建一个pair，从目录名长度256，起pair任务')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[2],
                                        destination_directory=s_256_dir_lst[0])
    common.judge_rc_unequal(rc, 0, 'create_rep_pair successed')

    log.info('8、[主]正常创建pair，主目录下创建255字符长度的目录+文件，起pair任务')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[3],
                                        destination_directory=s_dir_lst[3])
    common.judge_rc(rc, 0, 'create_rep_pair failed')
    rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[3],
                               destination_directory=s_dir_lst[3])
    common.judge_rc(rc, 0, 'get_one_pair_id failed')
    pairid_lst.append(pairid)

    rc = rep_common.create_file(rep_common.MASTER_RANDOM_NODE, m_dir_lst[3], 'file' + 'a' * 249, 1, 1)
    common.judge_rc(rc, 0, 'create_file failed')
    tmp_255_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir' + 'a' * 250, 1)
    rc, pscli_info = rep_common.start_rep_task_scp(pairid)
    common.judge_rc(rc, 0, 'start_rep_task_scp failed')

    rep_common.compare_md5(rep_common.MASTER_RANDOM_NODE, os.path.join(m_dir_lst[3], 'file' + 'a' * 249 + '_1'),
                           rep_common.SLAVE_RANDOM_NODE, os.path.join(m_dir_lst[3], 'file' + 'a' * 249 + '_1'))
    cmd = 'ls %s' % (os.path.join(s_dir_lst[3], 'dir' + 'a' * 250 + '_1'))
    rc, stdout = common.run_command(rep_common.MASTER_RANDOM_NODE, cmd)
    common.judge_rc(rc, 0, cmd + 'failed')

    log.info('9、[主]正常创建pair，主目录下创建254字符长度的目录+文件，起pair任务')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[4],
                                        destination_directory=s_dir_lst[4])
    common.judge_rc(rc, 0, 'create_rep_pair failed')
    rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[4],
                                            destination_directory=s_dir_lst[4])
    common.judge_rc(rc, 0, 'get_one_pair_id failed')
    pairid_lst.append(pairid)

    rc = rep_common.create_file(rep_common.MASTER_RANDOM_NODE, m_dir_lst[4], 'file' + 'a' * 248, 1, 1)
    common.judge_rc(rc, 0, 'create_file failed')
    tmp_254_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir' + 'a' * 249, 1)
    rc, pscli_info = rep_common.start_rep_task_scp(pairid)
    common.judge_rc(rc, 0, 'start_rep_task_scp failed')

    rc = rep_common.compare_md5(rep_common.MASTER_RANDOM_NODE, os.path.join(m_dir_lst[4], 'file' + 'a' * 248 + '_1'),
                                rep_common.SLAVE_RANDOM_NODE, os.path.join(m_dir_lst[4], 'file' + 'a' * 248 + '_1'))
    common.judge_rc(rc, 0, 'md5sum check failed')
    cmd = 'ls %s' % (os.path.join(s_dir_lst[4], 'dir' + 'a' * 249 + '_1'))
    rc, stdout = common.run_command(rep_common.MASTER_RANDOM_NODE, cmd)
    common.judge_rc(rc, 0, cmd + 'failed')

    log.info('10、[主]正常创建pair，主目录下创建256字符长度的目录+文件，起pair任务')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[5],
                                        destination_directory=s_dir_lst[5])
    common.judge_rc(rc, 0, 'create_rep_pair failed')
    rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[5],
                                            destination_directory=s_dir_lst[5])
    common.judge_rc(rc, 0, 'get_one_pair_id failed')
    pairid_lst.append(pairid)

    rc = rep_common.create_file(rep_common.MASTER_RANDOM_NODE, m_dir_lst[5], 'file' + 'a' * 250, 1, 1)
    common.judge_rc(rc, 0, 'create_file failed')
    tmp_256_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir' + 'a' * 251, 1)
    rc, pscli_info = rep_common.start_rep_task_scp(pairid)
    common.judge_rc(rc, 0, 'start_rep_task_scp failed')

    #todo 待开发实现查看pair历史任务

    '''只查看，不检查'''
    rc = rep_common.compare_md5(rep_common.MASTER_RANDOM_NODE, os.path.join(m_dir_lst[5], 'file' + 'a' * 250 + '_1'),
                                rep_common.SLAVE_RANDOM_NODE, os.path.join(m_dir_lst[5], 'file' + 'a' * 250 + '_1'))

    cmd = 'ls %s' % (os.path.join(s_dir_lst[4], 'dir' + 'a' * 251 + '_1'))
    rc, stdout = common.run_command(rep_common.MASTER_RANDOM_NODE, cmd)


    log.info('11、[主]正常创建pair，主目录下创建300字符长度的目录+文件，起pair任务')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[6],
                                        destination_directory=s_dir_lst[6])
    common.judge_rc(rc, 0, 'create_rep_pair failed')
    rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[6],
                                            destination_directory=s_dir_lst[6])
    common.judge_rc(rc, 0, 'get_one_pair_id failed')
    pairid_lst.append(pairid)

    rc = rep_common.create_file(rep_common.MASTER_RANDOM_NODE, m_dir_lst[6], 'file' + 'a' * 300, 1, 1)
    common.judge_rc(rc, 0, 'create_file failed')
    tmp_256_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir' + 'a' * 300, 1)
    rc, pscli_info = rep_common.start_rep_task_scp(pairid)
    common.judge_rc(rc, 0, 'start_rep_task_scp failed')

    # todo 待开发实现查看pair历史任务
    '''只查看，不检查'''
    rc = rep_common.compare_md5(rep_common.MASTER_RANDOM_NODE, os.path.join(m_dir_lst[5], 'file' + 'a' * 300 + '_1'),
                                rep_common.SLAVE_RANDOM_NODE, os.path.join(m_dir_lst[5], 'file' + 'a' * 300 + '_1'))

    cmd = 'ls %s' % (os.path.join(s_dir_lst[4], 'dir' + 'a' * 300 + '_1'))
    rc, stdout = common.run_command(rep_common.MASTER_RANDOM_NODE, cmd)

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

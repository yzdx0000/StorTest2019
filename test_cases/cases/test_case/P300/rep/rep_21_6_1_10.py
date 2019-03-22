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
import get_config

####################################################################################
#
# Author: chenjy1
# Date 20181218
# @summary：
#   目录类复制
# @steps:
#   1、[主从]创建复制域和通道
#   2、[主从]新创建一个卷
#   3、[主]创建一个根目录到根目录的pair
#   4、[主从]集群创建快照
#   5、[主]创建目录+文件，起pair任务
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(slave)parastor/(slave)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]
THREADS_NUMBER = 10


def create_volumes():
    volume_id_lst = []
    for cluster in [rep_common.MASTER, rep_common.SLAVE]:
        same_name_volume_id_lst = []
        rc, stdout = common.get_volumes(run_cluster=cluster)
        common.judge_rc(rc, 0, 'get_volumes failed')
        pscli_info = common.json_loads(stdout)
        same_name_volume_id = 0
        for volume in pscli_info['result']['volumes']:
            if FILE_NAME in volume['name']:
                same_name_volume_id = volume['id']
                same_name_volume_id_lst.append(same_name_volume_id)
        for id in same_name_volume_id_lst:
            rc, stdout = common.delete_volumes(id)
            common.judge_rc(rc, 0, 'delete_volumes filed')

        m_nodeip_lst = rep_common.MASTER_NODE_LST
        s_nodeip_lst = rep_common.SLAVE_NODE_LST

        rc, stdout = common.get_storage_pools(run_cluster=cluster)
        common.judge_rc(rc, 0, 'get_storage_pools failed')
        pscli_info = common.json_loads(stdout)

        storagepool_id = 0
        storagepool_name = ''
        for storage_pool in pscli_info['result']['storage_pools']:
            if storage_pool['name'] != 'shared_storage_pool' and storage_pool['type'] == 'FILE':
                storagepool_id = storage_pool['id']
                storagepool_name = storage_pool['name']
                break

        """获取此存储池上一个已有的卷的信息"""
        one_volume = {}

        rc, stdout = common.get_volumes(run_cluster=cluster)
        common.judge_rc(rc, 0, 'get_volumes failed')
        pscli_info = common.json_loads(stdout)
        for volume in pscli_info['result']['volumes']:
            if volume['storage_pool_name'] == 'system_volume':
                continue
            if volume['storage_pool_name'] == storagepool_name:
                one_volume = volume
                break

        log.info("1> 创建一个新卷 ,不指定total_bytes")
        rc, json_info = common.create_volume(FILE_NAME, storagepool_id, one_volume['layout']['stripe_width'],
                                                one_volume['layout']['disk_parity_num'],
                                                one_volume['layout']['node_parity_num'],
                                                one_volume['layout']['replica_num'],run_cluster=cluster)
        common.judge_rc(rc, 0, "create volume failed")

        rc, stdout = common.get_volumes(run_cluster=cluster)
        common.judge_rc(rc, 0, 'get_volumes failed')
        pscli_info = common.json_loads(stdout)
        my_volume_id = 0
        for volume in pscli_info['result']['volumes']:
            if volume['name'] == FILE_NAME:
                my_volume_id = volume['id']
                volume_id_lst.append(my_volume_id)
                break

    return volume_id_lst


def case():
    log.info('case begin')

    log.info('1>[主从]准备复制域和通道')
    rc, ready_info = rep_common.format_area_channel()
    common.judge_rc(rc, 0, 'format_area_channel failed')
    channelid = ready_info['channel']
    #m_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir', 20)
    #s_dir_lst = rep_common.create_dir(rep_common.SLAVE_NODE_LST[0], FILE_SLAVE_PATH, 'dir', 20)

    log.info('2> [主从]新创建一个卷')
    volume_id_lst = create_volumes()

    log.info('3> [主]创建一个根目录到根目录的pair')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=os.path.join('/mnt', FILE_NAME),
                                        destination_directory=os.path.join('/mnt', FILE_NAME))
    common.judge_rc(rc, 0, 'create_rep_pair faled')
    rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=os.path.join('/mnt', FILE_NAME),
                                            destination_directory=os.path.join('/mnt', FILE_NAME))
    common.judge_rc(rc, 0, 'get_one_pair_id failed')


    log.info('')
    path = FILE_NAME + ':/'
    rc, stdout = common.create_snapshot('tmp_snap', path)
    common.judge_rc(rc, 0, 'create_snapshot failed')

    rc = rep_common.vdb_create(os.path.join('/mnt', FILE_NAME), '/tmp', rep_common.MASTER_RANDOM_NODE)
    common.judge_rc(rc, 0, 'vdb_create failed ')
    rc, pscli_info = rep_common.start_rep_task_scp(pairid)
    common.judge_rc(rc, 0, 'start_rep_task failed')
    dir_lst = rep_common.create_dir(rep_common.MASTER_RANDOM_NODE, os.path.join('/mnt', FILE_NAME), 'dir', 3)
    '''检验一致性'''
    rc = rep_common.check_data_consistency(os.path.join('/mnt', FILE_NAME), '/tmp', [rep_common.MASTER_RANDOM_NODE],
                                           [rep_common.SLAVE_RANDOM_NODE])
    common.judge_rc(rc, 0, 'check_data_consistency failed')

    cmd = 'ls -a %s' % os.path.join('/mnt', FILE_NAME, '.snapshot')
    rc, stdout = common.run_command(rep_common.SLAVE_RANDOM_NODE, cmd)
    common.judge_rc_unequal(rc, 0, cmd + 'failed')


    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

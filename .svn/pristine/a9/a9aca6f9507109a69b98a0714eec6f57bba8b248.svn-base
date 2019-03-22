# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random
import sys

import utils_path
import common
import log
import shell
import get_config
import prepare_clean
import tool_use
import commands
import quota_common
#################################################################
#
# Author: chenjy1
# Date: 2018-09-03
# @summary：
#    创建多个卷，再删除
# @steps:
#    1.创建多个新卷，
#    2.清理环境
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
TIMEOUT_RC = 255   # 超时返回值,默认255
TOTAL_BYTES = 10737418240  # 设定指定total_byte时的大小为10G
N = 20


def case():
    log.info("case begin")
    rc_lst = {}
    nodeip_lst = get_config.get_allparastor_ips()
    ob_volume = common.Volume()
    ob_storagepool = common.Storagepool()
    same_name_volume_id_lst = []
    rc, pscli_info = ob_volume.get_all_volumes()
    common.judge_rc(rc, 0, "get_all_volumes failed")
    same_name_volume_id = 0
    log.info(FILE_NAME)
    for volume in pscli_info['result']['volumes']:
        log.info(volume['name'])
        if FILE_NAME in volume['name']:
            same_name_volume_id = volume['id']
            same_name_volume_id_lst.append(same_name_volume_id)
    log.info("same_name_volume_id_lst=:")
    log.info(same_name_volume_id_lst)
    for id in same_name_volume_id_lst:
        rc, stdout = common.delete_volumes(id)
        common.judge_rc(rc, 0, 'delete_volumes filed')

    rc, pscli_info = ob_storagepool.get_storagepool_info()
    common.judge_rc(rc, 0, "get_all_storagepools failed")

    storagepool_id = 0
    storagepool_name = ''
    for storage_pool in pscli_info['result']['storage_pools']:
        if storage_pool['name'] != 'shared_storage_pool' and storage_pool['type'] == 'FILE':
            storagepool_id = storage_pool['id']
            storagepool_name = storage_pool['name']
            break

    """获取此存储池上一个已有的卷的信息"""
    one_volume = {}
    rc, pscli_info = ob_volume.get_all_volumes()
    common.judge_rc(rc, 0, "get_all_volumes failed")
    for volume in pscli_info['result']['volumes']:
        if volume['storage_pool_name'] == 'system_volume':
            continue
        if volume['storage_pool_name'] == storagepool_name:
            one_volume = volume
            break

    log.info("1> 创建10个新卷 ,不指定total_bytes")
    my_volume_size_byte_lst = []
    my_volume_id_lst = []
    for i in range(N):
        create_volume_name = FILE_NAME + '%s' % i
        rc, json_info = ob_volume.create_volume(create_volume_name, storagepool_id, one_volume['layout']['stripe_width'],
                                one_volume['layout']['disk_parity_num'], one_volume['layout']['node_parity_num'],
                                one_volume['layout']['replica_num'])
        common.judge_rc(rc, 0, "create volume failed")
        rc, pscli_info = ob_volume.get_all_volumes()
        common.judge_rc(rc, 0, "get_all_volumes failed")
        for volume in pscli_info['result']['volumes']:
            if volume['name'] == create_volume_name:
                if volume['quota_cal_type'] != 'QUOTA_COMPUTE':
                    rc_lst[sys._getframe().f_lineno] = '2> quota_cal_type != QUOTA_COMPUTE'
                my_volume_size_byte_lst.append(volume['total_bytes'])
                my_volume_id_lst.append(volume['id'])
                break

        ret_lst = common.wait_df_find_volume(nodeip_lst, create_volume_name, 300, 1800)
        log.info(nodeip_lst)
        log.info(ret_lst)
        flag_get_volume_ok = True
        for i, val in enumerate(ret_lst):
            if val == 0:
                log.info('IP : %s can find volume %s' % (nodeip_lst[i], create_volume_name))
            if val == -1:
                flag_get_volume_ok = False
                log.info('IP : %s ssh failed' % (nodeip_lst[i]))
            if val == -2:
                flag_get_volume_ok = False
                log.info('IP :%s df block up' % (nodeip_lst[i]))
            if val == -3:
                flag_get_volume_ok = False
                log.info('IP : %s can not find volume %s after wait %d s' % (nodeip_lst[i], create_volume_name, 1800))
        if flag_get_volume_ok == False:
            rc_lst[sys._getframe().f_lineno] = 'some node get volume failed'
            common.except_exit("some node get volume failed")

    log.info('wait 5s')
    time.sleep(5)

    """删除卷"""
    for i in range(N):
        rc = ob_volume.delete_volume(my_volume_id_lst[i])
        common.judge_rc(rc, 0, "delete_volume failed")

    """判断rc_lst"""
    if rc_lst != {}:
        log.info(rc_lst)
        for i in rc_lst:
            log.info("check point in line : %s is about :%s " % (i, rc_lst[i]))
        log.info('If there are many lines, you may only need to look at the first line.')
        common.except_exit("some check point failed")

    return


def main():
    prepare_clean.minicase_test_prepare(FILE_NAME)
    case()
    prepare_clean.minicase_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)

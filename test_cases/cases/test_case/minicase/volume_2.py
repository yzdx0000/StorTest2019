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
#################################################################
#
# Author: chenjy1
# Date: 2018-09-03
# @summary：
#    创建卷时，指定total_bytes	查看卷为QUOTA_LIMIT，df显示存储池容量
# @steps:
#    1.创建一个新卷,指定total_bytes
#    2.get_volumes,查看卷
#    3.df看容量
#    4.更新卷，不指定total_bytes(需求就是不可以改变限制容量或不限制容量，pscli不填写total_bytes也是fs配额限制类型，符合)
#      始终为QUOTA_LIMIT卷
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
TIMEOUT_RC = 255   # 超时返回值,默认255
TOTAL_BYTES = 10737418240  # 设定指定total_byte时的大小为10G


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
    for volume in pscli_info['result']['volumes']:
        if FILE_NAME in volume['name']:
            same_name_volume_id = volume['id']
            same_name_volume_id_lst.append(same_name_volume_id)
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

    log.info("1> 创建一个新卷 ,指定total_bytes")
    rc, json_info = ob_volume.create_volume(FILE_NAME, storagepool_id, one_volume['layout']['stripe_width'],
                            one_volume['layout']['disk_parity_num'], one_volume['layout']['node_parity_num'],
                            one_volume['layout']['replica_num'], total_bytes=TOTAL_BYTES)
    common.judge_rc(rc, 0, "create volume failed")
    log.info('2> get_volumes 查看卷')
    rc, pscli_info = ob_volume.get_all_volumes()
    common.judge_rc(rc, 0, "get_all_volumes failed")
    my_volume_size_byte = 0
    my_volume_id = 0
    for volume in pscli_info['result']['volumes']:
        if volume['name'] == FILE_NAME:
            if volume['quota_cal_type'] != 'QUOTA_LIMIT':
                rc_lst[sys._getframe().f_lineno] = '2> quota_cal_type != QUOTA_LIMIT'
            my_volume_size_byte = volume['total_bytes']
            my_volume_id = volume['id']
            break

    log.info('3> df查看容量')
    '''检查是否能发现挂载卷'''

    ret_lst = common.wait_df_find_volume(nodeip_lst, FILE_NAME, 300, 1800)
    log.info(nodeip_lst)
    log.info(ret_lst)
    flag_get_volume_ok = True
    for i, val in enumerate(ret_lst):
        if val == 0:
            log.info('IP : %s can find volume %s' % (nodeip_lst[i], FILE_NAME))
        if val == -1:
            flag_get_volume_ok = False
            log.info('IP : %s ssh failed' % (nodeip_lst[i]))
        if val == -2:
            flag_get_volume_ok = False
            log.info('IP :%s df block up' % (nodeip_lst[i]))
        if val == -3:
            flag_get_volume_ok = False
            log.info('IP : %s can not find volume %s after wait %d s' % (nodeip_lst[i], FILE_NAME, 1800))
    if flag_get_volume_ok == False:
        rc_lst[sys._getframe().f_lineno] = 'some node get volume failed'
        common.except_exit("some node get volume failed")

    log.info('wait 5s')
    time.sleep(5)

    cmd = 'df -k'
    rc, stdout = common.run_command(common.SYSTEM_IP, cmd, timeout=300)
    if rc == TIMEOUT_RC:
        common.except_exit('df block up')
    common.judge_rc(rc, 0, "ip :%s cmd: %s failed" % (common.SYSTEM_IP, cmd))
    for line in stdout.splitlines():
        if FILE_NAME in line:
            str_lst = line.split()
            log.info('volume-totalbytes/1024 : %s  df :%s' % (my_volume_size_byte / 1024, str_lst[1]))
            if (my_volume_size_byte/1024) != int(str_lst[1]):
                rc_lst[sys._getframe().f_lineno] = '3> df size != volume-totalbytes'
            break

    log.info("4> 更新卷，不指定total_bytes，始终为QUOTA_LIMIT卷")
    rc, pscli_info = ob_volume.update_volume(my_volume_id, remark="'not set totalbytes'")
    if rc != 0:
        rc_lst[sys._getframe().f_lineno] = '4> updata_volume failed'
    rc, pscli_info = ob_volume.get_volumeinfo_by_id(my_volume_id)
    if rc != 0:
        rc_lst[sys._getframe().f_lineno] = '4> get_volumeinfo_by_id'
    if pscli_info['result']['volumes'][0]['quota_cal_type'] != 'QUOTA_LIMIT':
        rc_lst[sys._getframe().f_lineno] = '4> quota_cal_type != QUOTA_LIMIT'

    log.info('5> 恢复环境')
    """恢复前再df一下"""
    cmd = 'df -k'
    rc, stdout = common.run_command(common.SYSTEM_IP, cmd, timeout=300)
    if rc == TIMEOUT_RC:
        rc_lst[sys._getframe().f_lineno] = 'df blockup'
    if rc != 0:
        rc_lst[sys._getframe().f_lineno] = 'cmd df -k failed'
    """删除卷"""
    rc, stdout = common.rm_exe(nodeip_lst[0], '/mnt/%s/*' % FILE_NAME)
    common.judge_rc(rc, 0, 'rm_exe faileld')
    rc = ob_volume.delete_volume(my_volume_id)
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

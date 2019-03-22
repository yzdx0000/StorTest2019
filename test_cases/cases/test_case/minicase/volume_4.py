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
#    创建卷时，指定total_bytes，再update把total_bytes改大 ，看是否可以限制住
# @steps:
#    1.创建一个新卷,指定total_bytes，大小2G
#    2.创建1G文件
#    3.换客户端写2G文件
#    4.检查是否2G
#    5.updata改大 为3G
#    6.再创建1G文件，
#    7.换客户端写1M文件，看是否被限制
#    9.清理环境
# @changelog：
#################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
TIMEOUT_RC = 255   # 超时返回值,默认255
TOTAL_BYTES_1G = 1073741824
TOTAL_BYTES_2G = 2147483648  # 设定指定total_byte时的大小为2G
TOTAL_BYTES_3G = 3221225472
TEST_PATH = os.path.join('/mnt', FILE_NAME)


def case():
    log.info("case begin")
    rc_lst = {}
    nodeip_lst = get_config.get_allparastor_ips()
    clientip_lst = get_config.get_allclient_ip()
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

    log.info("1> 1.创建一个新卷,指定total_bytes，大小2G")
    rc, json_info = ob_volume.create_volume(FILE_NAME, storagepool_id, one_volume['layout']['stripe_width'],
                            one_volume['layout']['disk_parity_num'], one_volume['layout']['node_parity_num'],
                            one_volume['layout']['replica_num'], total_bytes=TOTAL_BYTES_2G)
    common.judge_rc(rc, 0, "create volume failed")
    """获取此卷信息"""
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

    log.info('2> 创建1G文件')
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

    """先创建1G"""
    quota_common.creating_files_for_volume_capacity(nodeip_lst[0], TEST_PATH, 1024, 1, "a", volume_id=my_volume_id)
    total_file_size = quota_common.dir_total_file_size(nodeip_lst[0], TEST_PATH)
    log.info('total_file_size_1g=%s' % total_file_size)
    if total_file_size != TOTAL_BYTES_1G:
        rc_lst[sys._getframe().f_lineno] = ' total_file_size not equal to 1G'

    log.info("3> 换客户端创建2G")
    quota_common.creating_files_for_volume_capacity(nodeip_lst[2], TEST_PATH, 2048, 1, "b", volume_id=my_volume_id)

    log.info('4> 检查是否2G')
    total_file_size = quota_common.dir_total_file_size(nodeip_lst[0], TEST_PATH)
    log.info('total_file_size_2g=%s' % total_file_size)
    if total_file_size != TOTAL_BYTES_2G:
        rc_lst[sys._getframe().f_lineno] = ' total_file_size not equal to 2G'

    log.info("5> 更新卷，改大total_bytes为3G")
    rc, pscli_info = ob_volume.update_volume(my_volume_id, total_bytes=TOTAL_BYTES_3G)
    if rc != 0:
        rc_lst[sys._getframe().f_lineno] = '4> updata_volume failed'
    rc, pscli_info = ob_volume.get_volumeinfo_by_id(my_volume_id)
    if rc != 0:
        rc_lst[sys._getframe().f_lineno] = '4> get_volume failed'
    if pscli_info['result']['volumes'][0]['total_bytes'] != TOTAL_BYTES_3G:
        rc_lst[sys._getframe().f_lineno] = '4> get_volume failed'

    log.info('wait 5s')
    time.sleep(5)

    log.info('6> 再创建1G')
    quota_common.creating_files_for_volume_capacity(nodeip_lst[0], TEST_PATH, 1024, 1, "c", volume_id=my_volume_id)

    log.info('7> 再换客户端创建1M')
    quota_common.creating_files_for_volume_capacity(nodeip_lst[1], TEST_PATH, 1, 1, "d", volume_id=my_volume_id)

    log.info('8> 检查是否3G')
    total_file_size = quota_common.dir_total_file_size(nodeip_lst[0], TEST_PATH)
    log.info('total_file_size_3g=%s' % total_file_size)
    if total_file_size != TOTAL_BYTES_3G:
        rc_lst[sys._getframe().f_lineno] = ' total_file_size not equal to 3G'

    """最后df查一下是否3G"""
    cmd = 'df -k'
    rc, stdout = common.run_command(common.SYSTEM_IP, cmd, timeout=300)
    if rc == TIMEOUT_RC:
        rc_lst[sys._getframe().f_lineno] = 'df blockup'
    if rc != 0:
        rc_lst[sys._getframe().f_lineno] = 'cmd df -k failed'
    for line in stdout.splitlines():
        if FILE_NAME in line:
            str_lst = line.split()
            log.info('volume-totalbytes/1024 : %s  df :%s' % (TOTAL_BYTES_3G / 1024, str_lst[1]))
            if (TOTAL_BYTES_3G/1024) != int(str_lst[1]):
                rc_lst[sys._getframe().f_lineno] = ' df size != volume-totalbytes'
            break

    log.info('9> 恢复环境')
    """删除卷"""
    rc, stdout = common.rm_exe(nodeip_lst[0], '/mnt/%s/*' % FILE_NAME)
    common.judge_rc(rc, 0, 'rm_exe faileld')
    rc = ob_volume.delete_volume(my_volume_id)
    common.judge_rc(rc, 0, 'delete_volume failed')

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

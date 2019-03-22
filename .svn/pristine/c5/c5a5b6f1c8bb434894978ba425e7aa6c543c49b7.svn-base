#-*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import snap_common
import log
import prepare_clean
import get_config
import tool_use
import commands
import logging
import event_common

####################################################################################
#
# Author: liyao
# date 2018-08-07
# @summary：
#    添加客户端授权成功
# @steps:
#   1、部署3节点集群环境
#   2、执行create_volume命令，创建名称为FILE_NAME的存储卷（参数正确，预期成功）
#   3、执行create_client_auth添加客户端授权，输入参数正确，预期添加成功
#   4、执行get_events查看操作信息显示是否正确
#   5、删除授权
#   6、删除上述存储卷
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
EVENT_TRUE_PATH = os.path.join(event_common.EVENT_TEST_PATH, FILE_NAME)
DATA_DIR = os.path.join(EVENT_TRUE_PATH, 'data_dir')                  # /mnt/volume1/event/events_5_3_1_11/data_dir/
CREATE_EVENT_PATH = os.path.join('event', FILE_NAME)                   # /event/events_5_3_6_21
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


def case():
    '''函数执行主体'''
    '''获取当前时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_1, cmd)
    start_time = int(stdout)   # 获取操作事件信息的起始时间

    ''' 2> 执行create_volume命令，创建名称为FILE_NAME的存储卷（参数正确，预期成功）'''
    '''获取存储池id{type:FILE}'''
    ob_storage = common.Storagepool()
    rc, json_info = ob_storage.get_storagepool_info()
    stdout = json_info
    pools_info = stdout['result']['storage_pools']
    file_pool_ids = []      # FILE类型存储池的ids
    for pool in pools_info:
        if pool['type'] == 'FILE':
            file_pool_ids.append(pool['id'])
    '''选取一个存储池，在其上创建存储卷'''
    select_pool_id = random.choice(file_pool_ids)
    volume_name = 'liliyao_' + FILE_NAME
    obj_volume = common.Volume()
    rc, stdout = common.get_node_pools()
    common.judge_rc(rc, 0, "get node pool failed")
    node_pool_info = common.json_loads(stdout)["result"]["node_pools"][0]
    obj_volume.create_volume(volume_name, file_pool_ids[0],
                             stripe_width=node_pool_info["stripe_width"],
                             disk_parity_num=node_pool_info["disk_parity_num"],
                             node_parity_num=node_pool_info["node_parity_num"],
                             replica_num=node_pool_info["replica_num"])

    log.info('waiting for 10s')
    time.sleep(10)

    '''3> 执行create_client_auth添加客户端授权，输入参数正确，预期添加成功'''
    client_ip_list = [snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_3]
    client_ip_str = ','.join(client_ip_list)
    rc, stdout = obj_volume.get_all_volumes()
    common.judge_rc(rc, 0, 'get volumes')
    volumes_info = stdout['result']['volumes']   # 获取新建存储卷信息（volume_id）
    for volume in volumes_info:
        if volume['name'] == volume_name:
            new_volume_info = volume
            new_volume_id = new_volume_info['id']
            break
    else:
        common.except_exit('get new volume id failed !!!')

    obj_client_auth = common.Clientauth()
    rc, stdout = obj_client_auth.create_client_auth(client_ip_str, new_volume_id)
    common.judge_rc(rc, 0, 'create client auth')

    log.info('waiting for 10s')
    time.sleep(10)

    '''4> 执行get_events查看操作信息显示是否正确'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)

    code = '0x02060067'
    description = 'add client auth'
    event_common.check_events_result(start_time, code, description)

    '''5> 删除授权'''
    rc, client_auth_ids = obj_client_auth.get_all_client_auth_ids(new_volume_id)
    common.judge_rc(rc, 0, 'get client auth')
    rc = obj_client_auth.delete_client_auth(client_auth_ids[0])
    common.judge_rc(rc, 0, 'delete client auth')

    '''6> 删除上述存储卷'''
    volume_id = obj_volume.get_volume_id(volume_name)
    obj_volume.delete_volume(volume_id)
    log.info('waiting for 30s')
    time.sleep(30)

    return


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=True)
    case()
    prepare_clean.test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
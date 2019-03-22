# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import snap_common
import nas_common
import log
import prepare_clean
import get_config
import tool_use
import commands
import logging
import event_common

####################################################################################
#
# author liyi
# date 2018-08-16
# @summary：
#           创建本地用户组失败
# @steps:
#   准备：
#           1>部署集群环境
#           2>创建访问分区，访问分区自带本地认证服务
#           3>获取本地认证服务器
#   执行：
#           1>创建本地用户组失败
#           2>执行get_events查看创建本地用户组失败的结果显示
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
SYSTEM_IP_0 = get_config.get_parastor_ip(0)


def case():
    """

    :return:
    """

    '''准备'''
    '''1>部署集群环境'''
    '''2>创建访问分区'''
    obj_node = common.Node()
    node_id_list = obj_node.get_nodes_id()
    node_ids = ','.join(str(i) for i in node_id_list)
    access_zone_name = FILE_NAME+"_Access_zone"
    check_result = nas_common.create_access_zone(node_ids=node_ids,
                                                 name=access_zone_name)
    if check_result["detail_err_msg"] != "":
        common.except_exit("create access zone failed!!")

    '''3>获取认证服务器'''
    check_result = nas_common.get_auth_providers_local()
    if check_result["detail_err_msg"] != "":
        common.except_exit("get local provider failed!!")
    auth_provider_local_id = check_result["result"]["auth_providers"][0]["id"]

    '''执行'''
    '''获取操作事件信息的起始时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    start_time = int(stdout)

    '''1> 创建本地用户组'''
    '''使认证服务id非法，预计创建用户组失败'''
    fault_auth_provider_local_id = auth_provider_local_id + 1000
    nas_common.create_auth_group(auth_provider_id=fault_auth_provider_local_id,
                                 name=FILE_NAME+"_group")

    '''2> 执行get_events查看结果显示'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)               # 创建本地用户组失败，延时

    code = '0x02030508'                # 创建本地用户组失败对应编号
    description = 'create_auth_group_failed'

    '''创建本地用户组失败事件码是否在事件列表中'''
    event_common.check_events_result(start_time, code, description)

    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    prepare_clean.nas_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)


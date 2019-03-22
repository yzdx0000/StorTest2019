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
# date 2018-08-15
# @summary：
#           删除本地用户成功
# @steps:
#   准备：
#           1>部署集群环境
#           2>创建访问分区，访问分区自带本地认证服务
#           3>创建本地用户
#   执行：
#           1>删除本地用户成功
#           2>执行get_events查看删除本地用户成功的结果显示
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
    access_zone_id = check_result['result']

    check_result = nas_common.enable_nas(access_zone_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("create access zone failed!!")

    '''3>创建本地用户'''

    '''获取认证服务器id'''
    check_result = nas_common.get_auth_providers_local()
    if check_result["detail_err_msg"] != "":
        common.except_exit("get local provider failed!!")
    auth_provider_local_id = check_result["result"]["auth_providers"][0]["id"]
    '''创建本地用户组'''
    check_result = nas_common.create_auth_group(auth_provider_id=auth_provider_local_id,
                                                name=FILE_NAME+"_group")
    if check_result["detail_err_msg"] != "":
        common.except_exit("create_auth_group failed!!")
    group_id = check_result["result"]
    '''在该用户组下创建本地用户'''
    check_result = nas_common.create_auth_user(auth_provider_id=auth_provider_local_id,
                                               name=FILE_NAME+"_user",
                                               password=111111,
                                               primary_group_id=group_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("create_auth_user failed!!")

    '''执行'''
    '''获取操作事件信息的起始时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    start_time = int(stdout)

    '''1>删除用户'''
    '''获取用户id'''
    rc, check_result = nas_common.get_auth_users(auth_provider_id=auth_provider_local_id,
                                                 group_id=group_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("get_auth_users failed!!")
    user_id = check_result["result"]["auth_users"][0]["id"]
    '''删除用户'''
    check_result = nas_common.delete_auth_users(ids=user_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("delete_auth_user failed!!")

    '''2> 执行get_events查看结果显示'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)               # 删除本地用户成功，延时
    code = '0x02030505'                # 删除本地用户成功对应编号
    description = 'delete_auth_user'

    '''删除本地用户成功事件码是否在事件列表中'''
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


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
# date 2018-08-9
# @summary：
#           创建业务子网失败
# @steps:
#   准备
#           1>部署集群环境
#           2>创建访问分区
#   执行:
#           1>制作创建业务子网失败事件
#           2>执行get_events查看创建业务子网失败的结果显示
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
    access_zone_name = FILE_NAME + "Access_zone"
    check_result = nas_common.create_access_zone(node_ids, access_zone_name)
    if check_result["detail_err_msg"] != "":
        log.error("create access zone failed!!")
        raise Exception("create access zone failed!!")
    access_zone_id = check_result["result"]

    '''执行'''
    '''获取操作事件信息的起始时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    start_time = int(stdout)

    '''制作创建业务子网失败事件'''
    access_zone_fault_id = access_zone_id + 1000       # 制作错误的访问区id，从而生成创建业务子网失败事件
    nas_common.create_subnet(access_zone_id=access_zone_fault_id,
                             name=FILE_NAME + "_SUBNET",
                             ip_family="IPv4",
                             svip=nas_common.SUBNET_SVIP,
                             subnet_mask=nas_common.SUBNET_MASK,
                             subnet_gateway=nas_common.SUBNET_GATEWAY,
                             network_interfaces=nas_common.SUBNET_NETWORK_INTERFACES)
    '''2>执行get_events查看结果显示'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s'% delay_time)
    time.sleep(delay_time)    # 创建业务子网后延时
    code = '0x02030202'     # 创建业务子网失败对应的编号
    description = 'create_subnet_failed'
    '''创建业务子网失败事件码是否在事件列表中'''
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

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
# date 2018-08-8
# @summary：
#           修改访问分区成功
# @steps:
#   准备：
#        1> 部署3节点集群环境
#        2> 创建访问分区
#   执行：
#        1> 制作修改访问分区成功事件
#        2> 查看修改访问分区成功事件是否在事件列表中
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
SYSTEM_IP_0 = get_config.get_parastor_ip(0)


def case():
    """

    :return:
    """
    '''准备'''

    '''1>部署3节点集群环境'''
    '''2>创建访问分区'''
    obj_node = common.Node()
    node_id_list = obj_node.get_nodes_id()
    node_ids = ','.join(str(i) for i in node_id_list)
    access_zone_name = FILE_NAME+"_Access_zone"
    check_result = nas_common.create_access_zone(node_ids=node_ids,
                                                 name=access_zone_name)
    if check_result["detail_err_msg"] != "":
        common.except_exit("create access zone failed!!")
    access_zone_id = check_result["result"]

    '''执行'''
    '''获取操作事件信息的起始时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    start_time = int(stdout)
    '''1>制作修改访问分区成功事件'''
    update_node_ids = random.choice(node_id_list)   # 修改3节点访问区为1节点访问区
    nas_common.update_access_zone(access_zone_id,
                                  node_ids=update_node_ids)
    if check_result["detail_err_msg"] != "":
        common.except_exit("update_access_zone failed!!")
    '''2>执行get_events查看结果显示'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s'% delay_time)
    time.sleep(delay_time)    # 修改访问分区后，延时一段时间
    code = '0x02030105'     # 修改访问分区成功的事件码
    description = 'update_access_zone'
    '''查看修改访问分区成功的事件码是否在事件列表中'''
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

#!/usr/bin/python
# -*- encoding=utf8 -*-
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
# author duyuli
# date 2018-08-20
# @summary：
#           节点NFS管理服务异常
# @steps:
#           1> 部署集群环境
#           2> 创建访问分区
#           3> 启动nas服务（包括ftp，nfs，smb）
#           4> 只停止NFS服务
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
SYSTEM_IP_0 = get_config.get_parastor_ip(0)


def case():
    '''1>部署3节点集群环境'''
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

    ''' 执行启动nas操作'''
    log.info("----enable nas need approximate 70s----")
    pscli_info = nas_common.enable_nas(access_zone_id)
    common.judge_rc(pscli_info['err_no'], 0, "enable nas failed!!!")

    '''获取操作事件信息的起始时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    start_time = int(stdout)

    ''' 执行停用nas操作'''
    log.info("----disable nas need approximate 5s----")
    nas_common.disable_nas(access_zone_id, "NFS")

    cmd = "systemctl start nfs-server.service"
    common.run_command(SYSTEM_IP_0, cmd)

    '''2>执行get_events查看结果显示'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    # time.sleep(delay_time)    # 延时查看事件结果

    code = '0x01030006'     # 停用nas服务的操作码
    description = 'NFS alarm check right'

    '''查看停用nas服务事件码是否在事件列表中'''
    event_common.check_alarms_result(code, description)
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    prepare_clean.nas_test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

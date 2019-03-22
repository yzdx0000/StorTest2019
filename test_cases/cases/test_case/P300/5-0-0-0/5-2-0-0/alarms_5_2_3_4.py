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
import make_fault

####################################################################################
#
# author duyuli
# date 2018-08-17
# @summary：
#           节点NAS管理服务异常(节点接口服务异常)
# @steps:
#           1> 部署集群环境
#           2> 创建访问分区
#           3> 启动nas服务（包括ftp，fns，smb）
#           4> mv掉oCnas二进制后，kill掉oCnas进程
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
SYSTEM_IP_0 = get_config.get_parastor_ip(0)


def case():
    """1>部署3节点集群环境"""
    '''2>创建访问分区'''
    obj_node = common.Node()
    node_id_list = obj_node.get_nodes_id()
    node_ids = ','.join(str(i) for i in node_id_list)
    access_zone_name = FILE_NAME + "Access_zone"
    check_result = nas_common.create_access_zone(node_ids, access_zone_name)
    if check_result["detail_err_msg"] != "":
        common.except_exit("create access_zone failed!!!")
    access_zone_id = check_result["result"]
    
    ''' 执行启动nas操作'''
    log.info("----enable nas need approximate 70s----")
    pscli_info = nas_common.enable_nas(access_zone_id)
    common.judge_rc(pscli_info['err_no'], 0, "enable nas failed!!!")

    process_name = "oCnas"
    code = '0x01030005'     # nas管理服务的操作码
    description = 'check alarm success'

    cmd = "mv /home/parastor/bin/oCnas /home/parastor/bin/oCnas_bk"
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    common.judge_rc(rc, 0, "mv oCnas wrong")

    # kill掉oCnas进程
    make_fault.kill_process(SYSTEM_IP_0, process_name)

    # 循环检查实时告警是否生效
    event_common.check_alarms_result(code, description)

    # 恢复环境
    cmd1 = "mv /home/parastor/bin/oCnas_bk /home/parastor/bin/oCnas"
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd1)
    common.judge_rc(rc, 0, "mv oCnas wrong")

    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    prepare_clean.nas_test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

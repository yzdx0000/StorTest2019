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
# date 2018-08-21
# @summary：
#           修改SMB全局配置失败
# @steps:
#   准备：
#           1>部署集群环境
#           2>创建访问分区
#           3>创建共享目录
#           4>创建导出SMB共享目录
#           5>获取SMB全局配置信息
#   执行：
#           1>修改SMB全局配置信息
#           2>执行get_events查看修改SMB全局配置失败的结果显示
#           3>清理工作
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
smb_path = nas_common.ROOT_DIR + "SMB_" + FILE_NAME                     # parastor:/nas/SMB_events_5_3_3_68


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
    access_zone_id = check_result["result"]
    '''3>创建共享目录'''
    check_result = nas_common.create_file(smb_path)
    if check_result["detail_err_msg"] != "":
        common.except_exit("create %s Failed" % smb_path)
    '''4>创建导出SMB共享目录'''
    check_result = nas_common.create_smb_export(access_zone_id=access_zone_id,
                                                export_name="smb_export_"+FILE_NAME,
                                                export_path=smb_path)
    if check_result["detail_err_msg"] != "":
        common.except_exit("create_smb_export is failed!!")
    smb_export_id = check_result["result"]
    '''5>获取SMB全局配置信息'''
    check_result = nas_common.get_smb_global_configs()
    if check_result["detail_err_msg"] != "":
        common.except_exit("get_smb_global_configs failed!!")
    config = check_result["result"]["configs"][0]
    id = config["id"]

    '''执行'''
    '''获取操作事件信息的起始时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    start_time = int(stdout)
    '''1>修改SMB全局配置信息'''
    '''令全局id配置不合法，预计修改失败'''
    fault_id = id + 1000
    nas_common.update_smb_global_config(smb_global_config_id=fault_id,
                                        enable_change_notify="false")
    '''2> 执行get_events查看结果显示'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)               # 修改SMB全局配置失败，延时
    code = '0x02030714'                # 修改SMB全局配置失败对应编号
    description = 'update_smb_global_config_failed'
    '''修改SMB全局配置失败事件码是否在事件列表中'''
    event_common.check_events_result(start_time, code, description)
    '''3> 清理工作'''
    '''3.1> 清理导出'''
    check_result = nas_common.delete_smb_exports(smb_export_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("delete_smb_exports is failed!!")
    '''3.2> 清理目录'''
    check_result = nas_common.delete_file(smb_path)
    if check_result["detail_err_msg"] != "":
        common.except_exit("delete_file is failed!!")
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    prepare_clean.nas_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)


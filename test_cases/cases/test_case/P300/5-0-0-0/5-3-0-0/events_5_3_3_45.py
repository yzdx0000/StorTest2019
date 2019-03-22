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
# date 2018-08-20
# @summary：
#           修改NFS共享成功
# @steps:
#   准备：
#           1>部署集群环境
#           2>创建访问分区
#           3>创建共享目录
#           4>创建NFS共享
#   执行：
#           1>修改NFS共享
#           2>执行get_events查看修改NFS共享成功的结果显示
#           3>清理工作
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
nfs_path = nas_common.ROOT_DIR + "NFS_" + FILE_NAME                     # parastor:/NFS_events_5_3_3_45.py


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
    check_result = nas_common.create_file(nfs_path)    # /mnt/parastor/events_5_3_3_45.py
    if check_result["detail_err_msg"] != "":
        common.except_exit("create %s Failed" % nfs_path)

    '''4>创建NFS共享'''
    check_result = nas_common.create_nfs_export(access_zone_id=access_zone_id,
                                                export_name=FILE_NAME,
                                                export_path=nfs_path,
                                                description="update_nfs_before")
    if check_result["detail_err_msg"] != "":
        common.except_exit("create_nfs_export is failed!!")
    nfs_export_id = check_result["result"]

    '''执行'''
    '''获取操作事件信息的起始时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    start_time = int(stdout)

    '''1> 修改导出NFS共享目录'''
    '''NFS共享允许修改description部分'''
    check_result = nas_common.update_nfs_export(export_id=nfs_export_id,
                                                description="update_nfs_export_finished!")
    if check_result["detail_err_msg"] != "":
        common.except_exit("update_nfs_export is failed!!")

    '''2> 执行get_events查看结果显示'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)               # 修改NFS共享成功，延时
    code = '0x02030603'                # 修改NFS共享成功对应编号
    description = 'update_nfs_export'
    '''修改NFS共享成功事件码是否在事件列表中'''
    event_common.check_events_result(start_time, code, description)

    '''3> 清理工作'''
    '''3.1> 清理导出'''
    check_result = nas_common.delete_nfs_exports(nfs_export_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("delete_nfs_exports is failed!!")
    '''3.2> 清理目录'''
    check_result = nas_common.delete_file(nfs_path)
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











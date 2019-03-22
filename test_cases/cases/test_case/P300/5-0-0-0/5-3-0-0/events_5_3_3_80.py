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
# date 2018-08-17
# @summary：
#           删除目录失败
# @steps:
#   准备：
#           1>部署集群环境
#           2>创建目录
#   执行：
#           1>删除目录
#           2>执行get_events查看删除NFS客户端授权失败的结果显示
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
file_path = nas_common.ROOT_DIR + FILE_NAME                  # parastor:/nas/events_5_3_3_80


def case():
    """

    :return:
    """

    '''准备'''
    '''1>部署集群环境'''
    '''2>创建目录'''
    check_result = nas_common.create_file(file_path)
    if check_result["detail_err_msg"] != "":
        common.except_exit("create %s Failed" % file_path)

    '''执行'''
    '''获取操作事件信息的起始时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    start_time = int(stdout)
    '''1> 删除目录'''
    '''删除不存在的路径，预计失败'''
    fault_file_path = file_path + "_fault"
    nas_common.delete_file(fault_file_path)
    '''2> 执行get_events查看结果显示'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)  # 删除目录失败，延时
    code = '0x02031206'   # 删除目录失败对应编号
    description = 'delete_file'
    '''删除目录失败事件码是否在事件列表中'''
    event_common.check_events_result(start_time, code, description)
    '''3>清理目录'''
    check_result = nas_common.delete_file(file_path)
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

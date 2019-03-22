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
# date 2018-08-14
# @summary：
#           添加NIS认证服务器失败
# @steps:
#   准备：
#           部署集群环境
#   执行：
#           1>制作添加NIS认证服务器失败事件
#           2>执行get_events查看添加NIS认证服务器失败的结果显示
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
SYSTEM_IP_0 = get_config.get_parastor_ip(0)


def case():
    """

    :return:
    """

    '''准备'''
    '''部署集群环境'''

    '''执行'''
    '''获取操作事件信息的起始时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    start_time = int(stdout)

    '''1> 添加NIS认证服务器失败'''
    '''令名称长度为33，超过名称最大限长32，预期创建失败'''
    fault_name = "aaaabbbb1_aaaabbbb2_aaaabbbb3_aaa"
    nas_common.add_auth_provider_nis(name=fault_name,
                                     domain_name=nas_common.NIS_DOMAIN_NAME,
                                     ip_addresses=nas_common.NIS_IP_ADDRESSES)

    '''2> 执行get_events查看结果显示'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)               # 添加NIS认证服务失败后，延时

    code = '0x02030406'                # 添加NIS认证服务器失败对应编号
    description = 'add_nis_provider_fault'

    '''添加NIS认证服务器失败事件码是否在事件列表中'''
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






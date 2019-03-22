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
# date 2018-08-13
# @summary：
#           添加AD认证服务器成功
# @steps:
#   准备：
#           部署集群环境
#   执行：
#           1>制作添加AD认证服务器成功事件
#           2>执行get_events查看添加AD认证服务器成功的结果显示
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
    '''1> 添加AD认证服务器'''
    check_result = nas_common.add_auth_provider_ad(name=FILE_NAME+"_ad_provider",
                                                   domain_name=nas_common.AD_DOMAIN_NAME,
                                                   dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                                   username=nas_common.AD_USER_NAME,
                                                   password=nas_common.AD_PASSWORD,
                                                   services_for_unix="RFC2307")

    if check_result["detail_err_msg"] != "":
        common.except_exit("add ad provider failed!!")
    '''2> 执行get_events查看结果显示'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)     # 添加AD认证服务器后，延时
    code = '0x02030401'     # 添加AD认证服务器成功对应编号
    description = 'add_ad_provider'
    '''添加AD认证服务器成功事件码是否在事件列表中'''
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


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
#           添加ldap认证服务器失败
# @steps:
#   准备：
#           部署集群环境
#   执行：
#           1>制作添加ldap认证服务器失败事件
#           2>执行get_events查看添加ldap认证服务器失败的结果显示
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

    '''1> 添加ldap认证服务器'''
    nas_common.add_auth_provider_ldap(name="LDAP_" + FILE_NAME,
                                      base_dn=nas_common.LDAP_BASE_DN,
                                      ip_addresses=nas_common.LDAP_IP_ADDRESSES,
                                      port=65538,    # 超出端口号范围（最大655535），预计失败
                                      bind_dn=nas_common.LDAP_BIND_DN,
                                      bind_password=nas_common.LDAP_BIND_PASSWORD,
                                      user_search_path=nas_common.LDAP_USER_SEARCH_PATH,
                                      group_search_path=nas_common.LDAP_GROUP_SEARCH_PATH)

    '''2> 执行get_events查看结果显示'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)               # 添加ldap认证服务器失败后，延时

    code = '0x02030410'                # 添加ldap认证服务器失败对应编号
    description = 'add_ldap_provider_failed'

    '''添加ldap认证服务器失败事件码是否在事件列表中'''
    event_common.check_events_result(start_time, code, description)

    return


def main():
    prepare_clean.nas_test_clean(FILE_NAME)
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    prepare_clean.nas_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)







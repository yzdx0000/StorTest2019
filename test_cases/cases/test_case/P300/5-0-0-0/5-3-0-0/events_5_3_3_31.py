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
#           删除认证服务器成功
# @steps:
#   准备：
#           1>部署集群环境
#           2>创建认证服务
#   执行：
#           1>删除认证服务
#           2>执行get_events查看删除服务器成功的结果显示
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
    '''2>添加LDAP认证服务器'''
    check_result = nas_common.add_auth_provider_ldap(name="LDAP_" + FILE_NAME,
                                                     base_dn=nas_common.LDAP_BASE_DN,
                                                     ip_addresses=nas_common.LDAP_IP_ADDRESSES,
                                                     port=389,
                                                     domain_password=nas_common.LDAP_DOMAIN_PASSWORD,
                                                     bind_dn=nas_common.LDAP_BIND_DN,
                                                     bind_password=nas_common.LDAP_BIND_PASSWORD,
                                                     user_search_path=nas_common.LDAP_USER_SEARCH_PATH,
                                                     group_search_path=nas_common.LDAP_GROUP_SEARCH_PATH)
    if check_result["detail_err_msg"] != "":
        common.except_exit("add ldap provider failed!!")
    auth_provider_ldap_id = check_result["result"]

    '''执行'''
    '''获取操作事件信息的起始时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    start_time = int(stdout)

    '''1> 删除认证服务器'''
    check_result = nas_common.delete_auth_providers(auth_provider_ldap_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("delete provider failed!!")

    '''2> 执行get_events查看结果显示'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)               # 删除LDAP认证服务器成功后，延时

    code = '0x02030413'                # 删除LDAP认证服务器成功对应编号
    description = 'delete_provider'

    '''删除认证服务器成功事件码是否在事件列表中'''
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


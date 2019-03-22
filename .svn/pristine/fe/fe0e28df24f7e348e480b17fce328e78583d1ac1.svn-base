# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-24
# @summary：
#   正常连接AD认证服务器
# @steps:
#   1、集群添加ad认证,填写正确的域名、dnsIP、管理员账户和管理员密码；
#   pscli --command=add_auth_provider_ad --name=ADtest --domain_name=xxx --dns_addresses=x.x.x.x --username=adminstrator --password=xxx --services_for_unix=NONE --unix_id_range=10000-20000
#   2、通过命令pscli --command=get_auth_providers_ad查看ad认证配置信息是否正确；
#   3、通过命令行pscli --command=check_auth_providers --ids=x查看认证配置信息是否能够正确的连接AD认证；
# @changelog：
#   None
######################################################

import os

import utils_path
import log
import common
import nas_common
import prepare_clean

# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]


def executing_case():
    """测试执行
    :return:无
    """
    log.info("（2）executing_case")

    # for add_auth_provider_ad
    auth_provider_ad_name = "nas_16_0_0_1_ad_auth_name"
    domain_name = nas_common.AD_DOMAIN_NAME
    dns_addresses = nas_common.AD_DNS_ADDRESSES
    username = nas_common.AD_USER_NAME
    password = nas_common.AD_PASSWORD
    services_for_unix = "NONE"
    unix_id_range = [20000000, 2147483645]
    other_unix_id_range = [2147483646, 2147483647]
    # for create_access_zone
    node_ids = nas_common.get_node_ids()
    access_zone_name = 'nas_16_0_0_1_access_zone_name'

    msg = nas_common.add_auth_provider_ad(name=auth_provider_ad_name,
                                          domain_name=domain_name,
                                          dns_addresses=dns_addresses,
                                          username=username,
                                          password=password,
                                          services_for_unix=services_for_unix)
    if msg["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    result = msg["result"]

    msg = nas_common.get_auth_providers_ad(ids=result)
    if msg["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    auth_provider = msg["result"]["auth_providers"][0]
    if cmp(auth_provider, {
                "dns_addresses": [
                    dns_addresses
                ],
                "domain_name": domain_name,
                "id": int(result),
                "key": int(result),
                "name": auth_provider_ad_name,
                "other_unix_id_range": other_unix_id_range,
                "services_for_unix": services_for_unix,
                "type": "AD",
                "unix_id_range": unix_id_range,
                "username": username,
                "version": auth_provider['version']
            }):
        raise Exception("%s Failed" % FILE_NAME)

    msg = nas_common.check_auth_provider(provider_id=result)
    if msg["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)

    """创建访问区"""
    msg = nas_common.create_access_zone(node_ids=node_ids,
                                        name=access_zone_name,
                                        auth_provider_id=result)
    if msg['detail_err_msg'] != '':
        raise Exception('%s Failed' % FILE_NAME)
    access_zone_id = msg['result']

    """使能访问区"""
    msg = nas_common.enable_nas(access_zone_id=access_zone_id)
    if msg['detail_err_msg'] != '':
        raise Exception('%s Failed' % FILE_NAME)

    """检查nas状态，查看集群连接域是否成功"""
    rc = nas_common.check_nas_status()
    common.judge_rc(rc, 0, 'check_nas_status failed')

    return


def nas_main():
    """脚本入口函数
    :return:无
    """
    prepare_clean.nas_test_prepare(FILE_NAME)
    executing_case()
    if nas_common.DEBUG != 'on':
        prepare_clean.nas_test_clean()
    return


if __name__ == '__main__':
    common.case_main(nas_main)

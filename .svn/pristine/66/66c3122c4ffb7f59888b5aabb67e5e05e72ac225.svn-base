# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-24
# @summary：
#   域管理员密码错误连接测试
# @steps:
#   1、集群添加ad认证,输入错误的域管理员密码；
#   pscli --command=add_auth_provider_ad --name=ADtest --domain_name=xxx --dns_addresses=x.x.x.x
#   --username=adminstrator --password=xxx --services_for_unix=NONE --unix_id_range=10000-20000
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
    wrong_password = "WrongPassword123"
    unix_id_range = [20000000, 2147483645]
    other_unix_id_range = [2147483646, 2147483647]
    # for create_access_zone
    node_ids = nas_common.get_node_ids()
    access_zone_name = 'nas_16_0_0_12_access_zone_name'

    msg = nas_common.add_auth_provider_ad(name="nas_16_0_0_12_ad_auth_name",
                                          domain_name=nas_common.AD_DOMAIN_NAME,
                                          dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                          username=nas_common.AD_USER_NAME,
                                          password=wrong_password,
                                          services_for_unix="NONE")
    if msg["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    result = msg["result"]

    msg = nas_common.get_auth_providers_ad(ids=result)
    if msg["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    auth_provider = msg["result"]["auth_providers"][0]
    if cmp(auth_provider, {
                "dns_addresses": [
                    nas_common.AD_DNS_ADDRESSES
                ],
                "domain_name": nas_common.AD_DOMAIN_NAME,
                "id": int(result),
                "key": int(result),
                "name": "nas_16_0_0_12_ad_auth_name",
                "other_unix_id_range": other_unix_id_range,
                "services_for_unix": "NONE",
                "type": "AD",
                "unix_id_range": unix_id_range,
                "username": nas_common.AD_USER_NAME,
                "version": auth_provider['version']
            }):
        raise Exception("%s Failed" % FILE_NAME)

    msg = nas_common.check_auth_provider(provider_id=result)
    if msg["detail_err_msg"].find("Connect to the authentication provider failed") == -1:
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
    if msg['detail_err_msg'].find('Wait for nas service ok timeout') == -1:
        raise Exception('%s Failed' % FILE_NAME)

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

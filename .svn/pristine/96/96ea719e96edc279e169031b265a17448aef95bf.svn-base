# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-24
# @summary：
#   错误的域名连接AD认证服务器
# @steps:
#   1、集群添加ad认证，输入错误的域名，观察是否配置是否可以下发成功；
#   pscli --command=add_auth_provider_ad --name=ad_test --domain_name=xxx --dns_addresses=x.x.x.x --username=adminstrator --password=xxx --services_for_unix=NONE --unix_id_range=10000-20000
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

    # domain_name合法但不正确
    auth_provider_ad_name = "nas_16_0_0_6_ad_auth_name"
    wrong_domain_name = "wrong-ad-domain-name"
    dns_addresses = nas_common.AD_DNS_ADDRESSES
    username = nas_common.AD_USER_NAME
    password = nas_common.AD_PASSWORD
    services_for_unix = "NONE"
    unix_id_range = [20000000, 2147483645]
    other_unix_id_range = [2147483646, 2147483647]

    check_result1 = nas_common.add_auth_provider_ad(name=auth_provider_ad_name,
                                                    domain_name=wrong_domain_name,
                                                    dns_addresses=dns_addresses,
                                                    username=username,
                                                    password=password,
                                                    services_for_unix=services_for_unix)
    if check_result1["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    result = check_result1["result"]

    check_result2 = nas_common.get_auth_providers_ad(ids=result)
    if check_result2["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    auth_provider = check_result2["result"]["auth_providers"][0]
    if cmp(auth_provider, {
                "dns_addresses": [
                    dns_addresses
                ],
                "domain_name": wrong_domain_name,
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

    check_result3 = nas_common.check_auth_provider(provider_id=result)
    if check_result3["detail_err_msg"].find("Connect to the authentication provider failed") == -1:
        raise Exception("%s Failed" % FILE_NAME)

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

# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-24
# @summary：
#   名称重复检测
# @steps:
#   1、集群添加第一个ad认证,填写正确的域名、dnsIP、管理员账户和管理员密码；
#   pscli --command=add_auth_provider_ad --name=ADtest --domain_name=xxx --dns_addresses=x.x.x.x
#   --username=adminstrator --password=xxx --services_for_unix=NONE --unix_id_range=10000-20000
#   2、集群添加第二个ad认证,名称相同，填写正确的域名、dnsIP、管理员账户和管理员密码；
#   pscli --command=add_auth_provider_ad --name=ADtest --domain_name=xxx --dns_addresses=x.x.x.x
#   --username=adminstrator --password=xxx --services_for_unix=NONE --unix_id_range=10000-20000
#   3、通过命令pscli --command=get_auth_providers_ad查看ad认证配置信息是否正确；
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

    # name重复性检查
    duplicate_name = "nas_16_0_0_4_ad_auth_name"
    domain_name = nas_common.AD_DOMAIN_NAME
    dns_addresses = nas_common.AD_DNS_ADDRESSES
    username = nas_common.AD_USER_NAME
    password = nas_common.AD_PASSWORD
    services_for_unix = "NONE"
    unix_id_range = [20000000, 30000000]
    other_unix_id_range = [2147483646, 2147483647]

    check_result1 = nas_common.add_auth_provider_ad(name=duplicate_name,
                                                    domain_name=domain_name,
                                                    dns_addresses=dns_addresses,
                                                    username=username,
                                                    password=password,
                                                    services_for_unix=services_for_unix,
                                                    unix_id_range="%s-%s" % (unix_id_range[0],
                                                                             unix_id_range[1]),
                                                    other_unix_id_range="%s-%s" % (other_unix_id_range[0],
                                                                                   other_unix_id_range[1]))
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
                "domain_name": domain_name,
                "id": int(result),
                "key": int(result),
                "name": duplicate_name,
                "other_unix_id_range": other_unix_id_range,
                "services_for_unix": services_for_unix,
                "type": "AD",
                "unix_id_range": unix_id_range,
                "username": username,
                "version": auth_provider['version']
            }):
        raise Exception("%s Failed" % FILE_NAME)

    check_result3 = nas_common.add_auth_provider_ad(name=duplicate_name,
                                                    domain_name=domain_name,
                                                    dns_addresses=dns_addresses,
                                                    username=username,
                                                    password=password,
                                                    services_for_unix=services_for_unix)
    if check_result3["detail_err_msg"].find("already exist") == -1:
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

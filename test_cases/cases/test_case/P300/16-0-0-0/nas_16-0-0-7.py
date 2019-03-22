# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-24
# @summary：
#   域名边界长度测试
# @steps:
#   1、集群添加ad认证，输入127个字符的域名，观察是否配置是否可以下发成功；
#   2、通过命令pscli --command=get_auth_providers_ad查看ad认证配置信息是否正确；
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

    # It must has 1 levels at least.
    # Domain name consists of letters, digits, and hyphens (-), and cannot start or end with a hyphen (-).
    # Each part contains a maximum of 63 characters
    # and the domain names of different levels must be separated by periods (.)
    # 各级域名加一起（算中间的点(.)）不能超过127个字符。

    # domain_name边界值检查
    auth_provider_ad_name_1 = "nas_16_0_0_7_ad_auth_name_1"
    auth_provider_ad_name_2 = "nas_16_0_0_7_ad_auth_name_2"
    illegal_domain_name1 = "wrong-ad-domain-name00000000000000000000000000000000000000000064.com"   # 某一部分超过63个字符
    illegal_domain_name2 = "wrong-ad-domain-name0000000000000000000000000000000000000000000" \
                           ".000000000000000000000000000000000000000000000000000000000000.128"      # 总长度超过127
    illegal_domain_name_list = [illegal_domain_name1, illegal_domain_name2]
    legal_domain_name = "wrong-ad-domain-name0000000000000000000000000000000000000000000" \
                        ".00000000000000000000000000000000000000000000000000000000000.127"       # 长度分别为63和127
    dns_addresses = nas_common.AD_DNS_ADDRESSES
    username = nas_common.AD_USER_NAME
    password = nas_common.AD_PASSWORD
    services_for_unix = "NONE"
    unix_id_range = [20000000, 2147483645]
    other_unix_id_range = [2147483646, 2147483647]

    for illegal_domain_name in illegal_domain_name_list:
        log.info("illegal_domain_name = %s" % illegal_domain_name)
        check_result = nas_common.add_auth_provider_ad(name=auth_provider_ad_name_1,
                                                       domain_name=illegal_domain_name,
                                                       dns_addresses=dns_addresses,
                                                       username=username,
                                                       password=password,
                                                       services_for_unix=services_for_unix)
        if illegal_domain_name == illegal_domain_name1:
            if check_result["detail_err_msg"].find("Each part contains a maximum of 63 characters") == -1:
                raise Exception("%s Failed" % FILE_NAME)
        elif illegal_domain_name == illegal_domain_name2:
            if check_result["detail_err_msg"].find("exceed the max length:127") == -1:
                raise Exception("%s Failed" % FILE_NAME)

    check_result1 = nas_common.add_auth_provider_ad(name=auth_provider_ad_name_2,
                                                    domain_name=legal_domain_name,
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
                "domain_name": legal_domain_name,
                "id": int(result),
                "key": int(result),
                "name": auth_provider_ad_name_2,
                "other_unix_id_range": other_unix_id_range,
                "services_for_unix": services_for_unix,
                "type": "AD",
                "unix_id_range": unix_id_range,
                "username": username,
                "version": auth_provider['version']
            }):
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

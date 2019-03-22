# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-24
# @summary：
#   域名特殊字符测试
# @steps:
#   1、集群添加ad认证，输入特殊字符的域名，观察是否配置是否可以下发成功；
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

    # domain_name非法性检查，含特殊字符
    illegal_domain_name_1 = "-adtest.com"
    illegal_domain_name_2 = "adtest.com-"
    illegal_domain_name_3 = "adtest_1.com"
    illegal_domain_name_4 = "adtest!.com"
    illegal_domain_name_5 = "adtest@.com"
    illegal_domain_name_6 = "adtest#.com"
    illegal_domain_name_7 = "adtest\$.com"
    illegal_domain_name_8 = "adtest%.com"
    illegal_domain_name_9 = "adtest^.com"
    illegal_domain_name_10 = "adtest\&.com"
    illegal_domain_name_11 = "adtest*.com"
    illegal_domain_name_12 = "adtest\(.com"
    illegal_domain_name_13 = "adtest\).com"
    illegal_domain_name_14 = "adtest\+.com"
    illegal_domain_name_15 = "adtest\=.com"
    illegal_domain_name_16 = "adtest\/.com"
    illegal_domain_name_list = [illegal_domain_name_1, illegal_domain_name_2, illegal_domain_name_3,
                                illegal_domain_name_4, illegal_domain_name_5, illegal_domain_name_6,
                                illegal_domain_name_7, illegal_domain_name_8, illegal_domain_name_9,
                                illegal_domain_name_10, illegal_domain_name_11, illegal_domain_name_12,
                                illegal_domain_name_13, illegal_domain_name_14, illegal_domain_name_15,
                                illegal_domain_name_16]
    legal_domain_name = "1-adtest.com"
    unix_id_range = [20000000, 2147483645]
    other_unix_id_range = [2147483646, 2147483647]

    for illegal_domain_name in illegal_domain_name_list:
        log.info("illegal_domain_name = %s" % illegal_domain_name)
        check_result1 = nas_common.add_auth_provider_ad(name="nas_16_0_0_8_ad_auth_name_1",
                                                        domain_name=illegal_domain_name,
                                                        dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                                        username=nas_common.AD_USER_NAME,
                                                        password=nas_common.AD_PASSWORD,
                                                        services_for_unix="NONE")
        if check_result1["detail_err_msg"].find("Domain name consists of letters, digits, and hyphens") == -1:
            raise Exception("%s Failed" % FILE_NAME)

    check_result2 = nas_common.add_auth_provider_ad(name="nas_16_0_0_8_ad_auth_name_2",
                                                    domain_name=legal_domain_name,
                                                    dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                                    username=nas_common.AD_USER_NAME,
                                                    password=nas_common.AD_PASSWORD,
                                                    services_for_unix="NONE")
    if check_result2["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    result = check_result2["result"]

    check_result3 = nas_common.get_auth_providers_ad(ids=result)
    auth_provider = check_result3["result"]["auth_providers"][0]
    if cmp(auth_provider, {
                "dns_addresses": [
                    nas_common.AD_DNS_ADDRESSES
                ],
                "domain_name": legal_domain_name,
                "id": int(result),
                "key": int(result),
                "name": "nas_16_0_0_8_ad_auth_name_2",
                "other_unix_id_range": other_unix_id_range,
                "services_for_unix": "NONE",
                "type": "AD",
                "unix_id_range": unix_id_range,
                "username": nas_common.AD_USER_NAME,
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

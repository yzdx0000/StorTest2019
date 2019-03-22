# -*- coding:utf-8 -*-

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-0-27 查询域认证服务器信息
#######################################################

import os

import utils_path
import log
import common
import nas_common
import prepare_clean

# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]


def executing_case():
    """
        1、显示参数信息
                "auth_providers": [
                    {
                        "dns_addresses": [----------DNSserver地址
                            "10.2.41.251"
                        ],
                        "domain_name": "adtest.com", -------域名
                        "id": 1,       ------认证id号
                        "key": 1,
                        "name": "ad_test_upd_1", ------认证名称
                        "other_unix_id_range": [
                            70000,
                            80000
                        ],
                        "rfc2307_unix_id_range": [
                            50000,
                            60000
                        ],
                        "services_for_unix": "RFC2307", -------映射类型
                        "type": "AD", ----认证类型
                        "username": "administrator", ------域管理员用户名
                        "version": 0
                    }
    :return:
    """
    log.info("（2）executing_case")

    legal_rfc2307_unix_id_range = "10001-20000"
    legal_other_unix_id_range = "20001-30000"

    check_result1 = nas_common.add_auth_provider_ad(name="nas_16_0_0_27_ad_auth_name",
                                                    domain_name=nas_common.AD_DOMAIN_NAME,
                                                    dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                                    username=nas_common.AD_USER_NAME,
                                                    password=nas_common.AD_PASSWORD,
                                                    services_for_unix="RFC2307")
    if check_result1["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    result = check_result1["result"]

    check_result2 = nas_common.get_auth_providers_ad(ids=result)
    if check_result2["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    auth_provider = check_result2["result"]["auth_providers"][0]
    if cmp(auth_provider, {
                "dns_addresses": [
                    "10.2.41.251"
                ],
                "domain_name": "adtest.com",
                "id": int("%s" % result),
                "key": int("%s" % result),
                "name": "nas_16_0_0_27_ad_auth_name",
                "other_unix_id_range": [
                    2147483646,
                    2147483647
                ],
                "services_for_unix": "RFC2307",
                "type": "AD",
                "unix_id_range": [
                    1000,
                    2147483645
                ],
                "username": "administrator",
                "version": 0
            }) != 0:
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

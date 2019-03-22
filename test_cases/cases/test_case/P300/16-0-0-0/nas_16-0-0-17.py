# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-28
# @summary：
#   规格外ad认证服务器连接ad认证服务器测试
# @steps:
#   1、创建第128个认证，观察是否创建成功；
#   2、创建第129个认证，观察是否创建成功；
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

    auth_provider_num = 129
    # for add_auth_provider_ad
    domain_name = nas_common.AD_DOMAIN_NAME
    dns_addresses = nas_common.AD_DNS_ADDRESSES
    username = nas_common.AD_USER_NAME
    password = nas_common.AD_PASSWORD
    services_for_unix = "RFC2307"

    for i in range(0, auth_provider_num):
        log.info("count = %s" % (i+1))
        auth_provider_ad_name = "nas_16_0_0_17_ad_auth_name_" + "%s" % (i+1)
        unix_id_range = 1000 * (i+1)
        other_unix_id_range = unix_id_range + 500
        if i < 128:
            msg = nas_common.add_auth_provider_ad(name=auth_provider_ad_name,
                                                  domain_name=domain_name,
                                                  dns_addresses=dns_addresses,
                                                  username=username,
                                                  password=password,
                                                  services_for_unix=services_for_unix,
                                                  unix_id_range="%s-%s" % (unix_id_range,
                                                                           unix_id_range + 499),
                                                  other_unix_id_range="%s-%s" % (other_unix_id_range,
                                                                                 other_unix_id_range + 499))
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
                    "other_unix_id_range": [other_unix_id_range, other_unix_id_range + 499],
                    "services_for_unix": services_for_unix,
                    "type": "AD",
                    "unix_id_range": [unix_id_range, unix_id_range + 499],
                    "username": username,
                    "version": auth_provider['version']
                    }):
                raise Exception("%s Failed" % FILE_NAME)

            msg = nas_common.check_auth_provider(provider_id=result)
            if msg["detail_err_msg"] != "":
                raise Exception("%s Failed" % FILE_NAME)
        else:
            """第129个创建失败"""
            msg = nas_common.add_auth_provider_ad(name=auth_provider_ad_name,
                                                  domain_name=domain_name,
                                                  dns_addresses=dns_addresses,
                                                  username=username,
                                                  password=password,
                                                  services_for_unix=services_for_unix,
                                                  unix_id_range="%s-%s" % (unix_id_range,
                                                                           unix_id_range + 499),
                                                  other_unix_id_range="%s-%s" % (other_unix_id_range,
                                                                                 other_unix_id_range + 499))
            if msg["detail_err_msg"].find("has reached limit:128") == -1:
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

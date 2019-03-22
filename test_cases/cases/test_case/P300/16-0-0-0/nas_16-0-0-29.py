# -*- coding:utf-8 -*-

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-0-29 删除认证服务器（使用中）
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
        1、集群添加ad认证,填写正确的域名、dnsIP、管理员账户和管理员密码；
        pscli --command=add_auth_provider_ad --name=ADtest --domain_name=xxx --dns_addresses=x.x.x.x --username=adminstrator --password=xxx --services_for_unix=NONE --unix_id_range=10000-20000
        2、通过命令pscli --command=get_auth_providers_ad查看ad认证配置信息是否正确；
        3、通过命令行pscli --command=check_auth_providers --ids=x查看认证配置信息是否能够正确的连接AD认证；
        4、配置访问区分，使用上面创建的认证；
        5、删除认证；
        pscli --command=delete_auth_providers --id=x
    :return:
    """
    log.info("（2）executing_case")

    node_ids = "1,2,3"  # 创建访问区，引用auth_provider_id

    check_result1 = nas_common.add_auth_provider_ad(name="nas_16_0_0_29_ad_auth_name",
                                                    domain_name=nas_common.AD_DOMAIN_NAME,
                                                    dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                                    username=nas_common.AD_USER_NAME,
                                                    password=nas_common.AD_PASSWORD,
                                                    services_for_unix="NONE")
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
            "domain_name": nas_common.AD_DOMAIN_NAME,
            "id": int("%s" % result),
            "key": int("%s" % result),
            "name": "nas_16_0_0_29_ad_auth_name",
            "other_unix_id_range": [
                2147483646,
                2147483647
            ],
            "services_for_unix": "NONE",
            "type": "AD",
            "unix_id_range": [
                20000000,
                2147483645
            ],
            "username": nas_common.AD_USER_NAME,
            "version": 0
            }) != 0:
        raise Exception("%s Failed" % FILE_NAME)

    check_result3 = nas_common.check_auth_provider(provider_id=result)
    if check_result3["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)

    check_result4 = nas_common.create_access_zone(node_ids=node_ids,
                                                  name="nas_16_0_0_29_access_zone_name",
                                                  auth_provider_id=result)
    if check_result4["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)

    check_result5 = nas_common.delete_auth_providers(ids=result)
    if check_result5["detail_err_msg"].find("is being used") == -1:
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

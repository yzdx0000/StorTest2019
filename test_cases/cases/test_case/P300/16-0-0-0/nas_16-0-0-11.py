# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-24
# @summary：
#   非域管理员连接测试【为验证连接域是否成功，需在访问区中引用增加的鉴权服务器】
# @steps:
#   1、集群添加ad认证,填写非管理员账户和管理员，密码填写正确的域名、dnsIP；
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
    not_domain_admins_username = nas_common.AD_ADMIN_USER_NAME_2    # autoadminuser2是AD域的用户，但不在Domain Admins安全组中
    services_for_unix_1 = "NONE"
    unix_id_range_1 = [20000000, 2147483645]
    other_unix_id_range_1 = [2147483646, 2147483647]
    # for create_access_zone
    node_ids = nas_common.get_node_ids()
    access_zone_name = 'nas_16_0_0_11_access_zone_name'

    msg = nas_common.add_auth_provider_ad(name="nas_16_0_0_11_ad_auth_name_1",
                                          domain_name=nas_common.AD_DOMAIN_NAME,
                                          dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                          username=not_domain_admins_username,
                                          password=nas_common.AD_PASSWORD,
                                          services_for_unix=services_for_unix_1,
                                          unix_id_range="%s-%s" % (unix_id_range_1[0],
                                                                   unix_id_range_1[1]),
                                          other_unix_id_range="%s-%s" % (other_unix_id_range_1[0],
                                                                         other_unix_id_range_1[1]))
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
                "name": "nas_16_0_0_11_ad_auth_name_1",
                "other_unix_id_range": other_unix_id_range_1,
                "services_for_unix": services_for_unix_1,
                "type": "AD",
                "unix_id_range": unix_id_range_1,
                "username": not_domain_admins_username,
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
    if msg['detail_err_msg'].find('Wait for nas service ok timeout') == -1:     # 加域不成功，enable nas失败
        raise Exception('%s Failed' % FILE_NAME)

    """【补充测试】username名称合法性测试"""
    legal_username = "admini-123_*strator"      # username可有特殊字符;
    services_for_unix_2 = "RFC2307"
    unix_id_range_2 = [1000, 2000]
    other_unix_id_range_2 = [3000, 4000]
    """"【补充测试】username中可含有特殊字符"""
    msg = nas_common.add_auth_provider_ad(name="nas_16_0_0_11_ad_auth_name_2",
                                          domain_name=nas_common.AD_DOMAIN_NAME,
                                          dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                          username=legal_username,
                                          password=nas_common.AD_PASSWORD,
                                          services_for_unix=services_for_unix_2,
                                          unix_id_range="%s-%s" % (unix_id_range_2[0],
                                                                   unix_id_range_2[1]),
                                          other_unix_id_range="%s-%s" % (other_unix_id_range_2[0],
                                                                         other_unix_id_range_2[1]))
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
                "name": "nas_16_0_0_11_ad_auth_name_2",
                "other_unix_id_range": other_unix_id_range_2,
                "services_for_unix": services_for_unix_2,
                "type": "AD",
                "unix_id_range": unix_id_range_2,
                "username": legal_username,
                "version": auth_provider['version']
            }):
        raise Exception("%s Failed" % FILE_NAME)

    msg = nas_common.check_auth_provider(provider_id=result)
    if msg["detail_err_msg"].find("Connect to the authentication provider failed") == -1:
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

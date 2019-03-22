# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-24
# @summary：
#   映射值边界测试
# @steps:
#   1、集群添加ad认证，映射输入超过2147483647的值，观察是否配置是否可以下发成功；
#   pscli --command=add_auth_provider_ad --name=a*1 --domain_name=xxx --dns_addresses=x.x.x.x
#   --username=adminstrator --password=xxx --services_for_unix=NONE --unix_id_range=10000-20000
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

    count = 6
    # for add_auth_provider_ad
    domain_name = nas_common.AD_DOMAIN_NAME
    dns_addresses = nas_common.AD_DNS_ADDRESSES
    username = nas_common.AD_USER_NAME
    password = nas_common.AD_PASSWORD
    services_for_unix = "NONE"
    unix_id_range_1 = [999, 2147483645]                 # 最小值非法
    other_unix_id_range_1 = [2147483646, 2147483647]
    unix_id_range_2 = [1000, 2147483645]
    other_unix_id_range_2 = [2147483646, 2147483648]    # 最大值非法
    unix_id_range_3 = [1000, 2147483646]                # 有交叉
    other_unix_id_range_3 = [2147483646, 2147483647]
    unix_id_range_4 = [2147483646, 2147483647]          # other大于unix
    other_unix_id_range_4 = [1000, 2147483645]
    unix_id_range_5 = [1000, 2147483645]                # 合法边界测试
    other_unix_id_range_5 = [2147483646, 2147483647]
    unix_id_range_list = [unix_id_range_1, unix_id_range_2, unix_id_range_3,
                          unix_id_range_4, unix_id_range_5]
    other_unix_id_range_list = [other_unix_id_range_1, other_unix_id_range_2, other_unix_id_range_3,
                                other_unix_id_range_4, other_unix_id_range_5]
    # for create_access_zone
    node_ids = nas_common.get_node_ids()
    access_zone_name = 'nas_16_0_0_13_access_zone_name'

    for i in range(1, count, 1):
        auth_provider_ad_name = "nas_16_0_0_13_ad_auth_name_" + str(i)
        if i < 5:
            msg = nas_common.add_auth_provider_ad(name=auth_provider_ad_name,
                                                  domain_name=domain_name,
                                                  dns_addresses=dns_addresses,
                                                  username=username,
                                                  password=password,
                                                  services_for_unix=services_for_unix,
                                                  unix_id_range="%s-%s" % (unix_id_range_list[i-1][0],
                                                                           unix_id_range_list[i-1][1]),
                                                  other_unix_id_range="%s-%s" % (other_unix_id_range_list[i-1][0],
                                                                                 other_unix_id_range_list[i-1][1]))
            if msg["detail_err_msg"].find('minimum value should be equal or greater than 1000') == -1 \
                    and msg["detail_err_msg"].find('cannot be parsed.') == -1 \
                    and msg["detail_err_msg"].find('cannot equal or greater than other unix id range the start') == -1:
                raise Exception("%s Failed" % FILE_NAME)
        else:
            msg = nas_common.add_auth_provider_ad(name=auth_provider_ad_name,
                                                  domain_name=domain_name,
                                                  dns_addresses=dns_addresses,
                                                  username=username,
                                                  password=password,
                                                  services_for_unix=services_for_unix,
                                                  unix_id_range="%s-%s" % (unix_id_range_list[i-1][0],
                                                                           unix_id_range_list[i-1][1]),
                                                  other_unix_id_range="%s-%s" % (other_unix_id_range_list[i-1][0],
                                                                                 other_unix_id_range_list[i-1][1]))
            if msg["detail_err_msg"] != "":
                raise Exception("%s Failed" % FILE_NAME)
            result = msg['result']

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
                "other_unix_id_range": other_unix_id_range_list[i-1],
                "services_for_unix": services_for_unix,
                "type": "AD",
                "unix_id_range": unix_id_range_list[i-1],
                "username": username,
                "version": auth_provider['version']
            }):
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

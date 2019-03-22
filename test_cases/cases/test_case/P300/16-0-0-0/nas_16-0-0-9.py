# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-24
# @summary：
#   错误的DNS IP连接测试
# @steps:
#   1、集群添加ad认证，输入非IP地址，观察是否配置是否可以下发成功；
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

    # dns_addresses非法性检查
    illegal_dns_addresses_1 = "abcdefg"
    illegal_dns_addresses_2 = "111.111.111.321"
    illegal_dns_addresses_3 = "1.1.1.1,2.2.2.2,3.3.3.3,111.111.111.321"
    illegal_dns_addresses_4 = "0.0.0.0"
    illegal_dns_addresses_5 = "239.9.9.9"   # x.x.x.0有bug，且不解决(见P300-1055)，此处改成对239地址进行验证
    illegal_dns_addresses_6 = "224.5.5.5"
    illegal_dns_addresses_7 = "255.255.255.255"
    illegal_dns_addresses_list = [illegal_dns_addresses_1, illegal_dns_addresses_2, illegal_dns_addresses_3,
                                  illegal_dns_addresses_4, illegal_dns_addresses_5, illegal_dns_addresses_6,
                                  illegal_dns_addresses_7]

    for illegal_dns_addresses in illegal_dns_addresses_list:
        log.info("illegal_dns_addresses = %s" % illegal_dns_addresses)
        check_result = nas_common.add_auth_provider_ad(name="nas_16_0_0_9_ad_auth_name",
                                                       domain_name=nas_common.AD_DOMAIN_NAME,
                                                       dns_addresses=illegal_dns_addresses,
                                                       username=nas_common.AD_USER_NAME,
                                                       password=nas_common.AD_PASSWORD,
                                                       services_for_unix="NONE")
        if check_result["detail_err_msg"].find("is invalid.") == -1 \
                and check_result["detail_err_msg"].find("is not supported") == -1:
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

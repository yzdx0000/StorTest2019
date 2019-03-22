# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-24
# @summary：
#   名称的特殊字符测试
# @steps:
#   1、集群添加ad认证，名称输入特殊字符，观察是否配置是否可以下发成功；
#   pscli --command=add_auth_provider_ad --name=a*1 --domain_name=xxx --dns_addresses=x.x.x.x --username=adminstrator
#   --password=xxx --services_for_unix=NONE --unix_id_range=10000-20000
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

    """name非法性检查，包括特殊字符"""
    illegal_name_1 = "1_nas_16_0_0_2_ad_auth_name"
    illegal_name_2 = "_nas_16_0_0_2_ad_auth_name"
    illegal_name_3 = "nas_16_0_0_2_ad-auth_name"
    illegal_name_4 = "nas_16_0_0_2_ad!_auth_name"
    illegal_name_5 = "nas_16_0_0_2_ad@_auth_name"
    illegal_name_6 = "nas_16_0_0_2_ad#_auth_name"
    illegal_name_7 = "nas_16_0_0_2_ad\$_auth_name"
    illegal_name_8 = "nas_16_0_0_2_ad%_auth_name"
    illegal_name_9 = "nas_16_0_0_2_ad^_auth_name"
    illegal_name_10 = "nas_16_0_0_2_ad\&_auth_name"
    illegal_name_11 = "nas_16_0_0_2_ad*_auth_name"
    illegal_name_12 = "nas_16_0_0_2_ad\(_auth_name"
    illegal_name_13 = "nas_16_0_0_2_ad\)_auth_name"
    illegal_name_14 = "nas_16_0_0_2_ad\+_auth_name"
    illegal_name_15 = "nas_16_0_0_2_ad\=_auth_name"
    illegal_name_16 = "nas_16_0_0_2_ad\/_auth_name"
    illegal_name_list = [illegal_name_1, illegal_name_2, illegal_name_3, illegal_name_4, illegal_name_5,
                         illegal_name_6, illegal_name_7, illegal_name_8, illegal_name_9, illegal_name_10,
                         illegal_name_11, illegal_name_12, illegal_name_13, illegal_name_14, illegal_name_15,
                         illegal_name_16]

    for illegal_name in illegal_name_list:
        log.info("illegal_name = %s" % illegal_name)
        check_result = nas_common.add_auth_provider_ad(name=illegal_name,
                                                       domain_name=nas_common.AD_DOMAIN_NAME,
                                                       dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                                       username=nas_common.AD_USER_NAME,
                                                       password=nas_common.AD_PASSWORD,
                                                       services_for_unix="RFC2307")
        if check_result["detail_err_msg"].find("can only consist of letters, "
                                               "numbers and underlines, begin with a letter.") == -1:
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

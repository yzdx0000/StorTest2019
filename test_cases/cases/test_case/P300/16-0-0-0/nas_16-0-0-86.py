# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-0-86 查询nis认证服务器配置信息正确
# 2018.11.03， zhangcy, 1.修改清理环境为prepare_clean的内容
#######################################################

import os

import utils_path
import commands
import common
import log
import nas_common
import prepare_clean

# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    """
    NA
    :return:
    """
    log.info("（2）executing_case")

    # 同nas_16-0-0-72.py
    check_result1 = nas_common.add_auth_provider_nis(name="nas_16_0_0_86_nis_auth_name",
                                                     domain_name=nas_common.NIS_DOMAIN_NAME,
                                                     ip_addresses=nas_common.NIS_IP_ADDRESSES)
    if check_result1["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result = check_result1["result"]

    check_result2 = nas_common.get_auth_providers_nis(ids=result)
    if check_result2["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    auth_provider = check_result2["result"]["auth_providers"][0]
    if cmp(auth_provider,{
                "domain_name": nas_common.NIS_DOMAIN_NAME,
                "id": int("%s" % result),
                "ip_addresses": [
                    nas_common.NIS_IP_ADDRESSES
                ],
                "key": int("%s" % result),
                "name": "nas_16_0_0_86_nis_auth_name",
                "type": "NIS",
                "version": 0
            }) != 0:
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    else:
        log.info(("%s Succeed") % FILE_NAME)

    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    log.info("（1）preparing_environment")

    '''
    1、下发nas相关的配置
    2、创建nas测试相关的目录和文件
    '''

    return


#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def nas_main():
    preparing_environment()
    prepare_clean.nas_test_prepare(FILE_NAME)
    executing_case()
    if nas_common.DEBUG != "on":
        prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
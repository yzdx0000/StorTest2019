# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-0-88 规格外连接nis认证服务器
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
        1、创建第128个认证，观察是否创建成功；
        2、创建第129个认证，观察是否创建成功；
    :return:
    """
    log.info("（2）executing_case")

    auth_provider_num = 128

    # 1、创建第128个认证，观察是否创建成功；
    for i in range(0, auth_provider_num):
        log.info("i = %s" % (i+1))
        nas_16_0_0_88_nis_auth_name = "nas_16_0_0_88_nis_auth_name" + "_%s" % (i+1)
        check_result = nas_common.add_auth_provider_nis(name=nas_16_0_0_88_nis_auth_name,
                                                        domain_name=nas_common.NIS_DOMAIN_NAME,
                                                        ip_addresses=nas_common.NIS_IP_ADDRESSES)
        if check_result["detail_err_msg"] != "":
            log.error(("%s Failed") % FILE_NAME)
            raise Exception(("%s Failed") % FILE_NAME)
        result = check_result["result"]

        check_result2 = nas_common.get_auth_providers_nis(ids=result)
        if check_result2["detail_err_msg"] != "":
            log.error(("%s Failed") % FILE_NAME)
            raise Exception(("%s Failed") % FILE_NAME)
        auth_provider = check_result2["result"]["auth_providers"][0]
        if cmp(auth_provider, {
                    "domain_name": nas_common.NIS_DOMAIN_NAME,
                    "id": int("%s" % result),
                    "ip_addresses": [
                        nas_common.NIS_IP_ADDRESSES,
                    ],
                    "key": int("%s" % result),
                    "name": nas_16_0_0_88_nis_auth_name,
                    "type": "NIS",
                    "version": 0
        }):
            log.error(("%s Failed") % FILE_NAME)
            raise Exception(("%s Failed") % FILE_NAME)

        check_result3 = nas_common.check_auth_provider(provider_id=result)
        if check_result3["detail_err_msg"] != "":
            log.error(("%s Failed") % FILE_NAME)
            raise Exception(("%s Failed") % FILE_NAME)

    # 第129个创建失败；
    check_result1 = nas_common.add_auth_provider_nis(name="nas_16_0_0_88_nis_auth_name_129",
                                                     domain_name=nas_common.NIS_DOMAIN_NAME,
                                                     ip_addresses=nas_common.NIS_IP_ADDRESSES)
    if check_result1["detail_err_msg"].find("has reached limit:128") == -1:
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

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

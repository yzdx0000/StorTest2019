#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-0-74 名称的边界值测试
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
        1、集群添加nis认证，名称输入超过范围，观察是否配置是否可以下发成功；
        pscli --command=add_auth_provider_nis --name=aaaaabbbbbcccccdddddeeeeefffff12
        --domain_name=xxx --ip_addresses=x.x.x.x
    """
    log.info("（2）executing_case")

    # name边界值检查
    illegal_name = "nas_16_0_0_74_nis_auth_name00032"
    legal_name = "nas_16_0_0_74_nis_auth_name0031"

    # 32个字符添加失败
    check_result1 = nas_common.add_auth_provider_nis(name=illegal_name,
                                                     domain_name=nas_common.NIS_DOMAIN_NAME,
                                                     ip_addresses=nas_common.NIS_IP_ADDRESSES)
    if check_result1["detail_err_msg"].find("exceed the max length:31") == -1:
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    # 31个字符添加成功；
    check_result2 = nas_common.add_auth_provider_nis(name=legal_name,
                                                     domain_name=nas_common.NIS_DOMAIN_NAME,
                                                     ip_addresses=nas_common.NIS_IP_ADDRESSES)
    if check_result2["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result = check_result2["result"]

    check_result3 = nas_common.get_auth_providers_nis(ids=result)
    if check_result3["detail_err_msg"] != "":
        log.error("%s Failed" % FILE_NAME)
        raise Exception("%s Failed" % FILE_NAME)
    auth_provider = check_result3["result"]["auth_providers"][0]
    if cmp(auth_provider,{
                "domain_name": nas_common.NIS_DOMAIN_NAME,
                "id": int("%s" % result),
                "ip_addresses": [
                    nas_common.NIS_IP_ADDRESSES
                ],
                "key": int("%s" % result),
                "name": "nas_16_0_0_74_nis_auth_name0031",
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
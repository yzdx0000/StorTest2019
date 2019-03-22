#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-0-80 修改名称测试
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
        1、集群添加nis认证，填写正确的IP地址、端口号和基准DN；
        pscli --command=add_auth_provider_nis --name=nis_test --domain_name=xxx --ip_addresses=x.x.x.x
        2、通过命令pscli --command=get_auth_provider_nis查看nis认证配置信息是否正确；
        3、通过命令行pscli --command=check_auth_provider --ids=x查看认证配置信息是否能够正确的连接nis认证；
        4、修改认证名称；
        pscli --command=update_auth_provider_nis --name=nis_test1
        5、通过命令pscli --command=get_auth_provider_nis查看nis认证配置是否修改成功；
        6、通过命令行pscli --command=check_auth_provider --ids=x查看认证配置信息是否能够正确的连接nis认证；
    :return:
    """
    log.info("（2）executing_case")

    old_auth_provider_name = "nas_16_0_0_80_nis_auth_name"
    new_auth_provider_name = "nas_16_0_0_80_nis_auth_new_name"

    check_result1 = nas_common.add_auth_provider_nis(name=old_auth_provider_name,
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
                    nas_common.NIS_IP_ADDRESSES,
                ],
                "key": int("%s" % result),
                "name": old_auth_provider_name,
                "type": "NIS",
                "version": 0
            }):
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result3 = nas_common.check_auth_provider(provider_id=result)
    if check_result3["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result4 = nas_common.update_auth_provider_nis(provider_id=result, name=new_auth_provider_name)
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result5 = nas_common.get_auth_providers_nis(ids=result)
    if check_result5["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    auth_provider = check_result5["result"]["auth_providers"][0]
    if cmp(auth_provider,{
                "domain_name": nas_common.NIS_DOMAIN_NAME,
                "id": int("%s" % result),
                "ip_addresses": [
                    nas_common.NIS_IP_ADDRESSES,
                ],
                "key": int("%s" % result),
                "name": new_auth_provider_name,
                "type": "NIS",
                "version": 0
            }):
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result6 = nas_common.check_auth_provider(provider_id=result)
    if check_result6["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

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
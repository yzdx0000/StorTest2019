#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-0-76 认证服务重复检测
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
        1、集群添加第一个nis认证，填写正确的IP地址、端口号和基准DN；
        pscli --command=add_auth_provider_nis --name=nis_test1 --ip_addresses=x.x.x.x --base_dn=dc=xxx,dc=com --port=389
        2、集群添加第二个nis认证，填写正确的IP地址、端口号和基准DN；
        pscli --command=add_auth_provider_nis --name=nis_test2 --ip_addresses=x.x.x.x --base_dn=dc=xxx,dc=com --port=389
        2、通过命令pscli --command=get_auth_provider_nis查看nis认证配置信息是否正确；
    :return:
    """
    log.info("（2）executing_case")

    # 不对domain_name、ip_addresses重复性检查
    duplicate_domain_name = nas_common.NIS_DOMAIN_NAME
    duplicate_ip_addresses = nas_common.NIS_IP_ADDRESSES

    check_result1 = nas_common.add_auth_provider_nis(name="nas_16_0_0_76_nis_auth_name_1",
                                                     domain_name=duplicate_domain_name,
                                                     ip_addresses=duplicate_ip_addresses)
    if check_result1["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result1 = check_result1["result"]

    check_result2 = nas_common.get_auth_providers_nis(ids=result1)
    if check_result2["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    auth_provider = check_result2["result"]["auth_providers"][0]
    if cmp(auth_provider,{
                "domain_name": duplicate_domain_name,
                "id": int("%s" % result1),
                "ip_addresses": [
                    duplicate_ip_addresses
                ],
                "key": int("%s" % result1),
                "name": "nas_16_0_0_76_nis_auth_name_1",
                "type": "NIS",
                "version": 0
            }) != 0:
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result3 = nas_common.add_auth_provider_nis(name="nas_16_0_0_76_nis_auth_name_2",
                                                     domain_name=duplicate_domain_name,
                                                     ip_addresses=duplicate_ip_addresses)
    if check_result3["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result2 = check_result3["result"]

    check_result4 = nas_common.get_auth_providers_nis(ids=result2)
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    auth_provider = check_result4["result"]["auth_providers"][0]
    if cmp(auth_provider,{
                "domain_name": duplicate_domain_name,
                "id": int("%s" % result2),
                "ip_addresses": [
                    duplicate_ip_addresses
                ],
                "key": int("%s" % result2),
                "name": "nas_16_0_0_76_nis_auth_name_2",
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
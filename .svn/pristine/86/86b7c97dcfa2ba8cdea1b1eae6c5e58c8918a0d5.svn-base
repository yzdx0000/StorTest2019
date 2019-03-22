#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-0-78 主nisIP地址错误连接测试
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
        1、集群添加nis认证服务器，主nisIP地址错误；
        pscli --command=add_auth_provider_nis --name=nis_test --domain_name=xxx --ip_addresses=x.x.x.x
        2、通过命令pscli --command=get_auth_provider_nis查看nis认证服务器配置信息是否正确；
        3、通过命令行pscli --command=check_auth_provider --ids=x查看认证配置信息是否能够正确的连接nis认证服务器；
    :return:
    """
    log.info("（2）executing_case")

    wrong_active_ip_addresses = "1.1.1.1,%s" % nas_common.NIS_IP_ADDRESSES
    # ip_addresses非法性检查
    illegal_dns_addresses_1 = "111.111.111.321"
    illegal_dns_addresses_2 = "1.1.1.1,2.2.2.2,3.3.3.3,111.111.111.321"
    illegal_dns_addresses_3 = "0.0.0.0"
    illegal_dns_addresses_4 = "255.255.255.255"   # 有bug 100.100.100.0
    illegal_dns_addresses_5 = "224.5.5.5"
    illegal_dns_addresses_6 = "255.255.255.255"
    illegal_dns_addresses_list = [illegal_dns_addresses_1, illegal_dns_addresses_2, illegal_dns_addresses_3,
                                  illegal_dns_addresses_4, illegal_dns_addresses_5, illegal_dns_addresses_6]
    # 重复ip_addresses检查
    duplicate_ip_addresses = "%s,%s" % (nas_common.NIS_IP_ADDRESSES, nas_common.NIS_IP_ADDRESSES)

    check_result1 = nas_common.add_auth_provider_nis(name="nas_16_0_0_78_nis_auth_name_1",
                                                     domain_name=nas_common.NIS_DOMAIN_NAME,
                                                     ip_addresses=wrong_active_ip_addresses)
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
                    "1.1.1.1",
                    "%s" % nas_common.NIS_IP_ADDRESSES
                ],
                "key": int("%s" % result),
                "name": "nas_16_0_0_78_nis_auth_name_1",
                "type": "NIS",
                "version": 0
            }):
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result3 = nas_common.check_auth_provider(provider_id=result)
    if check_result3["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    # ip_addresses非法性检查
    for illegal_dns_addresses in illegal_dns_addresses_list:
        log.info("illegal_dns_addresses = %s" % illegal_dns_addresses)
        check_result4 = nas_common.add_auth_provider_nis(name="nas_16_0_0_78_nis_auth_name_2",
                                                         domain_name=nas_common.NIS_DOMAIN_NAME,
                                                         ip_addresses=illegal_dns_addresses)
        if check_result4["err_msg"].find("ILLEGAL_ARGUMENT") == -1:
            log.error(("%s Failed") % FILE_NAME)
            raise Exception(("%s Failed") % FILE_NAME)

    # 重复ip_addresses检查
    check_result5 = nas_common.add_auth_provider_nis(name="nas_16_0_0_78_nis_auth_name_1",
                                                     domain_name=nas_common.NIS_DOMAIN_NAME,
                                                     ip_addresses=duplicate_ip_addresses)
    if check_result5["detail_err_msg"].find("already exist") == -1:
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
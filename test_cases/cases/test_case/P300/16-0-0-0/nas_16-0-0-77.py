#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-0-77 错误域名连接测试
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
        1、集群添加nis认证服务器，填写错误的域名；
        pscli --command=add_auth_provider_nis --name=nis_test --domain_name=xxx --ip_addresses=x.x.x.x
        2、通过命令pscli --command=get_auth_provider_nis查看nis认证服务器配置信息是否正确；
        3、通过命令行pscli --command=check_auth_provider --ids=x查看认证配置信息是否能够正确的连接nis认证服务器；
    :return:
    """
    log.info("（2）executing_case")

    # 注：NIS domain_name也可以分级（如：xxx.com），但每一级和总长度的限制都是最大63字节，和AD domain_name限制不一样
    # domain_name合法但不正确
    wrong_domain_name = "wrong-nis-domain-name"

    # domain_name边界值检查
    illegal_domain_name1 = "wrong-nis-domain-name000000000000000000000000000000000000064.com"       # 总长度超过63
    illegal_domain_name2 = "wrong-nis-domain-name0000000000000000000000000000000000000000064"       # 单级长度超过63
    illegal_domain_name_list_1 = [illegal_domain_name1,illegal_domain_name2]
    legal_domain_name_1 = "right-nis-domain-name00000000000000000000000000000000000063.com"         # 总长度为63
    legal_domain_name_2 = "right-nis-domain-name000000000000000000000000000000000000000063"         # 单级长度为63

    # domain_name非法性检查，含特殊字符
    illegal_domain_name_1 = "-nistest.com"
    illegal_domain_name_2 = "nistest.com-"
    illegal_domain_name_3 = "nistest_1.com"
    illegal_domain_name_4 = "nistest!.com"
    illegal_domain_name_5 = "nistest@.com"
    illegal_domain_name_6 = "nistest#.com"
    illegal_domain_name_7 = "nistest\$.com"
    illegal_domain_name_8 = "nistest%.com"
    illegal_domain_name_9 = "nistest^.com"
    illegal_domain_name_10 = "nistest\&.com"
    illegal_domain_name_11 = "nistest*.com"
    illegal_domain_name_12 = "nistest\(.com"
    illegal_domain_name_13 = "nistest\).com"
    illegal_domain_name_14 = "nistest\+.com"
    illegal_domain_name_15 = "nistest\=.com"
    illegal_domain_name_16 = "nistest\/.com"
    illegal_domain_name_list_2 = [illegal_domain_name_1, illegal_domain_name_2, illegal_domain_name_3,
                                  illegal_domain_name_4, illegal_domain_name_5, illegal_domain_name_6,
                                  illegal_domain_name_7, illegal_domain_name_8, illegal_domain_name_9,
                                  illegal_domain_name_10, illegal_domain_name_11, illegal_domain_name_12,
                                  illegal_domain_name_13, illegal_domain_name_14, illegal_domain_name_15,
                                  illegal_domain_name_16]
    legal_domain_name_3 = "1-nistest.com"

    """ domain_name合法但不正确"""
    check_result1 = nas_common.add_auth_provider_nis(name="nas_16_0_0_77_nis_auth_name_1",
                                                     domain_name=wrong_domain_name,
                                                     ip_addresses=nas_common.NIS_IP_ADDRESSES)
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
                "domain_name": wrong_domain_name,
                "id": int("%s" % result1),
                "ip_addresses": [
                    nas_common.NIS_IP_ADDRESSES
                ],
                "key": int("%s" % result1),
                "name": "nas_16_0_0_77_nis_auth_name_1",
                "type": "NIS",
                "version": 0
            }) != 0:
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result3 = nas_common.check_auth_provider(provider_id=result1)
    if check_result3["detail_err_msg"].find("Connect to the authentication provider failed") == -1:
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    """domain_name边界值检查 """
    # 分段长度或总长度大于63
    for illegal_domain_name in illegal_domain_name_list_1:
        log.info("illegal_domain_name = %s" % illegal_domain_name)
        check_result4 = nas_common.add_auth_provider_nis(name="nas_16_0_0_77_nis_auth_name_2",
                                                         domain_name=illegal_domain_name,
                                                         ip_addresses=nas_common.NIS_IP_ADDRESSES)
        if illegal_domain_name == illegal_domain_name1:
            if check_result4["detail_err_msg"].find("exceed the max length:63") == -1:
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)

    # 总长度等于63
    check_result5 = nas_common.add_auth_provider_nis(name="nas_16_0_0_77_nis_auth_name_3",
                                                     domain_name=legal_domain_name_1,
                                                     ip_addresses=nas_common.NIS_IP_ADDRESSES)
    if check_result5["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result2 = check_result5["result"]

    check_result6 = nas_common.get_auth_providers_nis(ids=result2)
    if check_result6["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    auth_provider = check_result6["result"]["auth_providers"][0]
    if cmp(auth_provider,{
                "domain_name": legal_domain_name_1,
                "id": int("%s" % result2),
                "ip_addresses": [
                    nas_common.NIS_IP_ADDRESSES
                ],
                "key": int("%s" % result2),
                "name": "nas_16_0_0_77_nis_auth_name_3",
                "type": "NIS",
                "version": 0
            }) != 0:
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    # 单级长度等于63
    check_result7 = nas_common.add_auth_provider_nis(name="nas_16_0_0_77_nis_auth_name_4",
                                                     domain_name=legal_domain_name_2,
                                                     ip_addresses=nas_common.NIS_IP_ADDRESSES)
    if check_result7["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result3 = check_result7["result"]

    check_result8 = nas_common.get_auth_providers_nis(ids=result3)
    if check_result8["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    auth_provider = check_result8["result"]["auth_providers"][0]
    if cmp(auth_provider,{
                "domain_name": legal_domain_name_2,
                "id": int("%s" % result3),
                "ip_addresses": [
                    nas_common.NIS_IP_ADDRESSES
                ],
                "key": int("%s" % result3),
                "name": "nas_16_0_0_77_nis_auth_name_4",
                "type": "NIS",
                "version": 0
            }) != 0:
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    """domain_name非法性检查，含特殊字符 """
    for illegal_domain_name in illegal_domain_name_list_2:
        log.info("illegal_domain_name = %s" % illegal_domain_name)
        check_result9 = nas_common.add_auth_provider_nis(name="nas_16_0_0_77_nis_auth_name_5",
                                                         domain_name=illegal_domain_name,
                                                         ip_addresses=nas_common.NIS_IP_ADDRESSES)
        if check_result9["detail_err_msg"].find("Domain name consists of letters, digits, and hyphens") == -1:
            log.error(("%s Failed") % FILE_NAME)
            raise Exception(("%s Failed") % FILE_NAME)

    # 数字开头
    check_result10 = nas_common.add_auth_provider_nis(name="nas_16_0_0_77_nis_auth_name_6",
                                                      domain_name=legal_domain_name_3,
                                                      ip_addresses=nas_common.NIS_IP_ADDRESSES)
    if check_result10["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result4 = check_result10["result"]

    check_result11 = nas_common.get_auth_providers_nis(ids=result4)
    if check_result11["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    auth_provider = check_result11["result"]["auth_providers"][0]
    if cmp(auth_provider,{
                "domain_name": legal_domain_name_3,
                "id": int("%s" % result4),
                "ip_addresses": [
                    nas_common.NIS_IP_ADDRESSES
                ],
                "key": int("%s" % result4),
                "name": "nas_16_0_0_77_nis_auth_name_6",
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
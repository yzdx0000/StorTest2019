# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-0-85 删除nis服务器测试（使用中）
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
        1、集群添加nis认证服务器，填写正确的域名、IP地址；
        pscli --command=add_auth_provider_nis --name=nis_test --domain_name=xxx --ip_addresses=x.x.x.x
        2、通过命令pscli --command=get_auth_provider_nis查看nis认证服务器配置信息是否正确；
        3、通过命令行pscli --command=check_auth_provider --ids=x查看认证配置信息是否能够正确的连接nis认证服务器；
        4、配置访问区分，使用上面创建的认证；
        5、删除认证；
        pscli --command=delete_auth_providers --id=x
    :return:
    """
    log.info("（2）executing_case")
    node = common.Node()
    ids = node.get_nodes_id()
    node_ids = ','.join(str(p) for p in ids)
    # node_ids = "1,2,3"

    check_result1 = nas_common.add_auth_provider_nis(name="nas_16_0_0_85_nis_auth_name",
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
    if cmp(auth_provider, {
                "domain_name": nas_common.NIS_DOMAIN_NAME,
                "id": int("%s" % result),
                "ip_addresses": [
                    nas_common.NIS_IP_ADDRESSES,
                ],
                "key": int("%s" % result),
                "name": "nas_16_0_0_85_nis_auth_name",
                "type": "NIS",
                "version": 0
            }):
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result3 = nas_common.check_auth_provider(provider_id=result)
    if check_result3["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result4 = nas_common.create_access_zone(node_ids=node_ids,
                                                  name="nas_16_0_0_85_access_zone_name",
                                                  auth_provider_id=result)
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    
    check_result5 = nas_common.delete_auth_providers(ids=result)
    if check_result5["detail_err_msg"].find("is being used by access zone") == -1:
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
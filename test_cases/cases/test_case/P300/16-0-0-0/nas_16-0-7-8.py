#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-x-x 修改base_dn
# 2018.11.2， zhangcy, 1.修改node_ids =1,2,3为通过pscli --command=get_nodes获取；
#                       2.修改清理环境为prepare_clean的内容
#######################################################

import os

import utils_path
import common
import shell
import log
import nas_common
import get_config
import prepare_clean

# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
node_ip = get_config.get_parastor_ip()


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    """
    1、增加LDAP鉴权服务器；
    pscli --command=add_auth_provider_ldap --name=ldapname --base_dn="dc=test,dc=com" --ip_addresses=10.2.41.150
    2、创建访问区，并使用步骤1中的鉴权服务器；
    pscli --command=create_access_zone --node_ids=1,2,3 --name=azname --auth_provider_id=x
    3、启动nas；
    pscli --command=enable_nas --access_zone_id=x
    4、修改base_dn；
    pscli --command=update_auth_provider_ldap --id=x --base_dn="dc=newtest,dc=com"
    :return:
    """
    log.info("（2）executing_case")

    # for add_auth_provider_ldap
    auth_provider_ldap_name = "nas_16_0_7_8_ldap_auth_name"
    base_dn = nas_common.LDAP_BASE_DN
    ip_addresses = nas_common.LDAP_IP_ADDRESSES

    # for create_access_zone
    node = common.Node()
    ids = node.get_nodes_id()
    node_ids = ','.join(str(p) for p in ids)
    # node_ids = "1,2,3"
    access_zone_name = "nas_16_0_7_8_access_zone_name"

    # for update_auth_provider_ldap
    new_base_dn = "dc=newtest,dc=com"

    check_result1 = nas_common.add_auth_provider_ldap(name=auth_provider_ldap_name,
                                                      base_dn=base_dn,
                                                      ip_addresses=ip_addresses)
    if check_result1["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    auth_provider_id = check_result1["result"]

    check_result2 = nas_common.create_access_zone(node_ids=node_ids,
                                                  name=access_zone_name,
                                                  auth_provider_id=auth_provider_id)
    if check_result2["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    access_zone_id = check_result2["result"]

    check_result3 = nas_common.enable_nas(access_zone_id=access_zone_id)
    if check_result3["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result4 = nas_common.update_auth_provider_ldap(provider_id=auth_provider_id,
                                                         base_dn=new_base_dn)
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result5 = nas_common.get_auth_providers_ldap(ids=auth_provider_id)
    if check_result5["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    auth_provider = check_result5["result"]["auth_providers"][0]
    if cmp(auth_provider,{
                "base_dn": new_base_dn,
                "id": int("%s" % auth_provider_id),
                "ip_addresses": [
                    nas_common.LDAP_IP_ADDRESSES
                ],
                "key": int("%s" % auth_provider_id),
                "name": auth_provider_ldap_name,
                "port": 389,
                "protocol": "ldap",
                "type": "LDAP",
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
    prepare_clean.nas_test_clean()
    if nas_common.DEBUG != "on":
        prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)

# -*-coding:utf-8 -*
import os

import utils_path
import common
import nas_common
import log
import get_config
import prepare_clean

####################################################################################
#
# author 李一
# date 2018-07-26
# @summary：
#       关闭NAS服务,修改认证服务id后，启动NAS服务时卡住
# @steps:
#     1、添加ldap认证服务器(使用命令pscli --command=add_auth_provider_ldap)；
#     2、创建访问区(使用命令pscli --command=create_access_zone)；
#     3、启动该访问区的nas服务(使用命令pscli --command=enable_nas)；
#     4、关闭nas服务(使用命令pscli --command=disable_nas)；
#     5、修改访问区认证服务器的id号(pscli --command=update_access_zone)
#     6、启动NAS服务卡住（使用命令pscli --command=enable_nas）
# @changelog：
####################################################################################

system_ip = get_config.get_parastor_ip(0)
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]       # 本脚本名字


def case():
    # 1> 添加ldap认证服务器
    check_result = nas_common.add_auth_provider_ldap(name="LDAP_"+FILE_NAME,
                                                     base_dn=nas_common.LDAP_BASE_DN,
                                                     ip_addresses=nas_common.LDAP_IP_ADDRESSES,
                                                     port=389,
                                                     user_search_path=nas_common.LDAP_USER_SEARCH_PATH,
                                                     group_search_path=nas_common.LDAP_GROUP_SEARCH_PATH)
    if check_result["detail_err_msg"] != "":
        common.except_exit("add_auth_provider_ldap failed!!")
    ldap_id = check_result["result"]

    check_result = nas_common.check_auth_provider(ldap_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("check_auth_provider failed!!")

    # 2> 创建访问区
    obj_node = common.Node()
    node_id_list = obj_node.get_nodes_id()
    node_ids = ','.join(str(i) for i in node_id_list)
    check_result = nas_common.create_access_zone(node_ids=node_ids,
                                                 name="LdapAccessZone"+FILE_NAME,
                                                 auth_provider_id=ldap_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("create_access_zone failed")
    access_zone_id = check_result["result"]

    # 3> 启动该访问区的nas服务
    check_result = nas_common.enable_nas(access_zone_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("enable_nas failed!!")

    # 4> 关闭访问区的nas服务
    check_result = nas_common.disable_nas(access_zone_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("disable_nas failed!!")

    # 5> 修改访问区认证服务器id号
    auth_providers_id_str = nas_common.get_auth_providers_id_list()
    auth_providers_id_list = auth_providers_id_str.split(',')
    """
    遍历认证服务id，找到一个和现在ldap_id号不同的认证服务id
    将找到的id作为要更新的id
    """
    for i in range(len(auth_providers_id_list)):
        if ldap_id != auth_providers_id_list[i]:
            update_auth_provider_id = auth_providers_id_list[i]
            break
    check_result = nas_common.update_access_zone(access_zone_id=access_zone_id,
                                                 node_ids=node_ids,
                                                 auth_provider_id=update_auth_provider_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("update_access_zone Failed!!")

    # 6> 启动该访问区的nas服务
    check_result = nas_common.enable_nas(access_zone_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("enable_nas failed!!")


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    prepare_clean.nas_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)


# -*-coding:utf-8 -*
import os
import time
import random
import commands
import utils_path
import common
import nas_common
import log
import shell
import get_config
import json
import prepare_clean

####################################################################################
#
# author liyi
# date 2018-07-19
# @summary：
#       ldap访问区启动nas服务
# @steps:
#     1、添加ldap认证服务器(使用命令pscli --command=add_auth_provider_ldap)；
#     2、使用该ldap认证服务器创建访问区(pscli --command=create_access_zone)
#     3、启动该访问区的nas服务(pscli --command=enable_nas)
# @changelog：
####################################################################################

system_ip = get_config.get_parastor_ip(0)
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字


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

    # 2> 使用该ldap认证服务器创建访问区
    obj_node = common.Node()
    node_id_list = obj_node.get_nodes_id()
    node_ids = ','.join(str(i) for i in node_id_list)
    check_result = nas_common.create_access_zone(node_ids=node_ids,
                                                 name=FILE_NAME+"_LdapAccessZone",
                                                 auth_provider_id=ldap_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("create_access_zone failed!")
    access_zone_id = check_result["result"]

    # 3> 启动该访问区的nas服务
    check_result = nas_common.enable_nas(access_zone_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("enalbe_nas failed!!")


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    prepare_clean.nas_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)





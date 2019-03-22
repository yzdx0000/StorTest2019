# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random
import re

import utils_path
import common
import log
import prepare_clean
import get_config
import nas_common
import make_fault
import snap_common
import tool_use

"""
 Author: liangxy
 date 2018-11-16
 @summary：
    修改访问分区，使其包含的节点依次减少，直至访问区内只有一个节点
 @steps:
    1、清除环境
    2、创建访问区，要求使用集群所有节点，启动smb/nfs/ftp服务，并检查
    3、按照节点列表，使用update_access_zone命令将节点依次踢出访问区，同时，
       每个踢出的访问区建立新的单节点访问区，启动smb/nfs/ftp服务
    4、检查所有访问区的服务状态是否正常

 @changelog：
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字
NAS_PATH = get_config.get_one_nas_test_path()                            # /mnt/volume/nas_test_dir
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/volume/nas_test_dir/nas_16_6_0_16
BASE_NAS_PATH = os.path.dirname(NAS_PATH)                                # /mnt/volume
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)                           # nas_test_dir


def create_all_kind_of_provider():
    """1 创建认证"""
    auth_provider_id_list = []
    ad_name = "ad_auth_provider"
    msg2 = nas_common.add_auth_provider_ad(name=ad_name,
                                           domain_name=nas_common.AD_DOMAIN_NAME,
                                           dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                           username=nas_common.AD_USER_NAME,
                                           password=nas_common.AD_PASSWORD,
                                           services_for_unix="NONE")

    common.judge_rc(msg2["err_no"], 0, "add_auth_provider_ad failed")
    ad_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(ad_auth_provider_id)
    log.info("ad认证：{}".format(ad_auth_provider_id))

    ldap_name = "ldap_auth_provider"
    msg2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_BASE_DN,
                                             ip_addresses=nas_common.LDAP_IP_ADDRESSES, port=389)
    common.judge_rc(msg2["err_no"], 0, "ldap_auth_provider failed")

    ldap_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(ldap_auth_provider_id)
    log.info("ldap认证：{}".format(ldap_auth_provider_id))

    ldap_name = "ldap_pdc_auth_provider"
    msg2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_2_BASE_DN,
                                             ip_addresses=nas_common.LDAP_2_IP_ADDRESSES, port=389,
                                             bind_dn=nas_common.LDAP_2_BIND_DN,
                                             bind_password=nas_common.LDAP_2_BIND_PASSWORD,
                                             domain_password=nas_common.LDAP_2_DOMAIN_PASSWORD)
    common.judge_rc(msg2["err_no"], 0, "ldap_pdc_auth_provider failed")

    ldap_pdc_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(ldap_pdc_auth_provider_id)
    log.info("ldap_pdc认证：{}".format(ldap_pdc_auth_provider_id))

    nis_name = "nis_auth_provider"
    msg2 = nas_common.add_auth_provider_nis(name=nis_name,
                                            domain_name=nas_common.NIS_DOMAIN_NAME,
                                            ip_addresses=nas_common.NIS_IP_ADDRESSES)

    common.judge_rc(msg2["err_no"], 0, "nis_auth_provider failed")
    nis_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(nis_auth_provider_id)
    log.info("nis认证：{}".format(nis_auth_provider_id))
    return auth_provider_id_list


def case():

    """函数主体"""
    log.info("1> 清理环境完成，访问区节点数量等步长减少")
    log.info("2> 创建访问区，要求使用集群所有节点，启动smb/nfs/ftp服务，并检查")
    node_obj = common.Node()
    node_list_all = node_obj.get_nodes_id()
    node_list_string = []
    for node_id_int in node_list_all:
        node_list_string.append(str(node_id_int))
    nodes_lenth = len(node_list_all)
    index_max = nodes_lenth-1
    case_ip = node_obj.get_node_ip_by_id(node_list_all[index_max])
    az_name_lst = []
    for i in node_list_all:
        az_name = "az_" + str(i)
        az_name_lst.append(az_name)
    if len(az_name_lst) != nodes_lenth:
        log.info("Warning:num of name != num of nodes<{} v.s. {}>".format(len(az_name_lst), nodes_lenth))
    all_nodes_id_param = ",".join(node_list_string)
    all_nodes_az_name = "az_" + "0"
    if all_nodes_az_name in az_name_lst:
        common.except_exit("nodes id has 0")
    msg_crt_az_all = nas_common.create_access_zone(node_ids=all_nodes_id_param, name=all_nodes_az_name)
    common.judge_rc(msg_crt_az_all["err_no"], 0, "created az include all nodes")
    id_az_all_nodes = msg_crt_az_all["result"]
    msg_enabel_nas_all = nas_common.enable_nas(id_az_all_nodes, "NFS,SMB,FTP")
    common.judge_rc(msg_enabel_nas_all["err_no"], 0, "created az include all nodes")

    log.info("3> 使用update_access_zone命令将节点依次踢出访问区,建立新的单节点访问区")
    '''更新的列表在pop前拿到值，pop后的列表只作为for循环的条件'''
    node_list_string_pop = node_list_string[:]
    if len(node_list_string_pop) > 1:
        daemon_node = random.choice(node_list_string_pop)
        node_list_string_pop.remove(daemon_node)
        log.info("list lenth > 1,pop {} to be a daemon_node,result:{} to dele".format(daemon_node, node_list_string_pop))
    node_list_update = node_list_string[:]
    for_loop_time = 0
    # 默认环境完整，有四种provider
    provider_flag = False
    provider_lst = []
    provider_id = None
    """provider_flag为True，进行认证服务器切换"""
    if provider_flag:
        provider_lst = create_all_kind_of_provider()
    for node_id in node_list_string_pop:
        for_loop_time += 1
        node_list_update.remove(node_id)
        # log.info("dele {} from {},left is {}".format(node_id, node_list_string, node_list_update))
        node_id_param = ",".join(node_list_update)
        log.info("3-{}> 从 {} 中踢出节点 {}，剩下的节点群是 {}".format(for_loop_time, node_list_string, node_id, node_list_update))
        if provider_flag:
            log.info("默认参数完整，更新时一并更新访问区的鉴权服务器")
            provider_id = random.choice(provider_lst)
            msg_update = nas_common.update_access_zone(access_zone_id=id_az_all_nodes, node_ids=node_id_param, auth_provider_id=provider_id)

        else:
            msg_update = nas_common.update_access_zone(access_zone_id=id_az_all_nodes, node_ids=node_id_param)
        common.judge_rc(msg_update["err_no"], 0, "update az,delete nodes:{},left id:{}".format(node_id, node_id_param))

        az_name = "az_" + str(node_id)
        msg_crt_az = nas_common.create_access_zone(node_ids=node_id, name=az_name)
        id_az = msg_crt_az["result"]
        common.judge_rc(msg_crt_az["err_no"], 0, "created az use new nodes:{},id:{}".format(node_id, id_az))

        msg_enabel_nas = nas_common.enable_nas(id_az, "NFS,SMB,FTP")
        common.judge_rc(msg_enabel_nas["err_no"], 0, "enable nas on new az:".format(id_az))

    log.info("4> 检查所有节点[{}]的访问区服务状态是否正常".format(node_list_all))
    #for node in node_list_all:
        #log.info("check node [{}]".format(node))
    nas_check = nas_common.check_nas_status()
    common.judge_rc(nas_check, 0, "nas status of node is wrong")
    log.info("case passed!")
    return


def nas_main():
    log_file_path = log.get_log_path(FILE_NAME)
    log.init(log_file_path, True)
    prepare_clean.nas_test_clean()
    case()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    nas_main()

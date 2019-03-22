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
 date 2018-11-22
 @summary：
    修改访问分区，顺序/随机替换访问区节点的认证服务器
 @steps:
    1、清除环境
    2、按照节点列表，随机选取其中节点创建访问区，启动smb/nfs/ftp服务，随机添加认证服务器
    3、打乱认证服务器列表，使用update_access_zone命令替换访问区节点的认证服务器
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
    log.info("1> 清理环境完成，访问区节点随机添加认证服务器")
    log.info("2> 按照节点列表，随机选取其中节点创建访问区，启动smb/nfs/ftp服务")
    node_obj = common.Node()
    node_list_all = node_obj.get_nodes_id()
    # log.info("验证error，必选4")
    # node_list_all.remove(4)
    node_list_string = []
    for node_id_int in node_list_all:
        node_list_string.append(str(node_id_int))

    lenth_nodes_up = len(node_list_string)
    lenth_max = lenth_nodes_up + 1
    node_nums = random.choice(range(1, lenth_max))
    node_id_choosen = random.sample(node_list_string, node_nums)
    provider_list = create_all_kind_of_provider()

    # init_nodes_id_param = "4," + ",".join(node_id_choosen)
    init_nodes_id_param = ",".join(node_id_choosen)

    log.info("2-0> 创建初始访问区节点为 {}".format(init_nodes_id_param))

    all_nodes_az_name = "az_" + str(time.localtime().tm_hour) + str(time.localtime().tm_min) + str(time.localtime().tm_sec)
    provider_id_1st = random.choice(provider_list)
    msg_crt_az_all = nas_common.create_access_zone(node_ids=init_nodes_id_param, name=all_nodes_az_name, auth_provider_id=provider_id_1st)
    common.judge_rc(msg_crt_az_all["err_no"], 0, "created az include all nodes")
    id_az_all_nodes = msg_crt_az_all["result"]
    msg_enabel_nas_all = nas_common.enable_nas(id_az_all_nodes, "NFS,SMB,FTP")
    common.judge_rc(msg_enabel_nas_all["err_no"], 0, "created az include all nodes")
    log.info("2-1> 创建访问区{}的初始节点为 {},认证服务器{}".format(id_az_all_nodes, init_nodes_id_param, provider_id_1st))
    # provider_list.remove(provider_id_1st)
    random.shuffle(provider_list)
    while provider_list[0] == provider_id_1st:
        random.shuffle(provider_list)
    for_loop_time = 0
    for pro_id in provider_list:
        for_loop_time += 1
        log.info("3-{} > 使用update_access_zone命令替换访问区节点的认证服务器为：{}".format(for_loop_time, pro_id))
        msg_update = nas_common.update_access_zone(access_zone_id=id_az_all_nodes, auth_provider_id=pro_id)
        common.judge_rc(msg_update["err_no"], 0, "update az provider id:{}".format(pro_id))
    log.info("4> 检查访问区内所有节点{}的服务状态是否正常".format(node_id_choosen))
    node_id_choosen_lst_string = []
    for idd in node_id_choosen:
        node_id_choosen_lst_string.append(str(idd))
    node_id_choosen_string = ",".join(node_id_choosen)
    nas_check = nas_common.check_nas_status(get_node_id=node_id_choosen_string)
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

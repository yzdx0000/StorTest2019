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
 date 2018-11-21
 @summary：
    修改访问分区，使用其他访问区的节点部分替换本访问区节点
 @steps:
    1、清除环境
    2、按照节点列表，随机分为两组，选取其中节点数较多的一组创建待替换访问区，另一组创建提供节点的访问区，启动smb/nfs/ftp服务
    3、使用update_access_zone命令选取不在节点替换部分本访问区节点
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


def decompose_az_with_different_num(nodes_update, lenth_min, lenth_now):
    """
    author:JiangXiaoguang, LiangXiaoyu
    summit:对n个节点的列表分解为长度随机的两个子列表：
            1、每次选择的子列表长度为开区间[lenth_min,lenth_now)的一个随机数；
            2、分解为两部分，对分解后的长度无要求
    :param nodes_update: 输入的节点列表信息，随更新而改变
    :param lenth_min:待选节点列表的左值；lenth_now：长度的最大值+1
    :return: 选完新节点之后的剩余节点列表，更新访问区
    """
    nodes_chosen = []
    num_choose = 0
    if lenth_now < lenth_min:
        common.except_exit("left node number {} is less than {}, can not be decomposed".format(lenth_now, lenth_min))
    else:
        if lenth_now == lenth_min:
            nodes_chosen = nodes_update[:]
            nodes_update = []
        else:
            num_choose = random.choice(range(lenth_min, lenth_now))

            nodes_chosen = random.sample(nodes_update, num_choose)
            # 减去选出的节点就是更新后的节点列表
            nodes_update = list(set(nodes_update) - set(nodes_chosen))
    # 选出的节点列表，转为逗号字符串即可
    node_id_choosen_param = ",".join(nodes_chosen)

    log.info("total: {} node(s) {} choosen; leave: {} for next iteration and operation".format(num_choose, nodes_chosen, nodes_update))
    return nodes_chosen, node_id_choosen_param, nodes_update


def case():

    """函数主体"""
    log.info("1> 清理环境完成，部分访问区节点被其他访问区节点替换")
    log.info("2> 按照节点列表，随机分为两组，选取其中节点数较少的一组创建访问区，启动smb/nfs/ftp服务")
    node_obj = common.Node()
    node_list_all = node_obj.get_nodes_id()
    node_list_string = []
    for node_id_int in node_list_all:
        node_list_string.append(str(node_id_int))

    lenth_nodes_up = len(node_list_string)
    if lenth_nodes_up < 2:
        common.except_exit("节点数少于3，不适用于本用例")
    # 部分替换的起始节点数大于3，否则变成了完全替换

    # random为左闭右开区间，待替换访问区节点数一定要大于2，否则无法进行二次分解：1与2两组之间互相无法部分替换；右端点不能覆盖全部取值，否则没有剩余节点以替换
    node_id_choosen, node_id_choosen_param, nodes_update = decompose_az_with_different_num(node_list_string, 2, lenth_nodes_up)

    log.info("2-0> 创建初始访问区节点为 {},创建第二访问区的节点为{}".format(node_id_choosen, nodes_update))

    init_nodes_id_param = node_id_choosen_param
    all_nodes_az_name = "az_" + str(time.localtime().tm_hour) + str(time.localtime().tm_min) + str(time.localtime().tm_sec)
    msg_crt_az_all = nas_common.create_access_zone(node_ids=init_nodes_id_param, name=all_nodes_az_name)
    common.judge_rc(msg_crt_az_all["err_no"], 0, "created az include all nodes")
    id_az_all_nodes = msg_crt_az_all["result"]
    msg_enabel_nas_all = nas_common.enable_nas(id_az_all_nodes, "NFS,SMB,FTP")
    common.judge_rc(msg_enabel_nas_all["err_no"], 0, "created az include all nodes")
    log.info("2-1> 创建访问区{}的初始节点为 {}".format(id_az_all_nodes, node_id_choosen_param))

    update_param = ",".join(nodes_update)
    scd_nodes_az_name = "az_" + str(time.localtime().tm_hour) + str(time.localtime().tm_min) + str(time.localtime().tm_sec)
    msg_crt_az_scd = nas_common.create_access_zone(node_ids=update_param, name=scd_nodes_az_name)
    common.judge_rc(msg_crt_az_scd["err_no"], 0, "created az include all nodes")
    id_az_scd_nodes = msg_crt_az_scd["result"]
    msg_enabel_nas_all = nas_common.enable_nas(id_az_scd_nodes, "NFS,SMB,FTP")
    common.judge_rc(msg_enabel_nas_all["err_no"], 0, "created az include all nodes")
    log.info("2-2> 创建访问区{}的节点为{}".format(id_az_scd_nodes, update_param))
    # 二次分解待替换访问区
    replace_lenth = min(len(node_id_choosen), len(nodes_update))
    # 最多不能大于两个访问区中节点数最小的值
    replace_lenth_random = replace_lenth + 1
    node_id_1st_mv, node_1st_mv_para, nodes_1st_left = decompose_az_with_different_num(node_id_choosen, 1, replace_lenth_random)
    if len(node_id_1st_mv) > len(nodes_update):
        common.except_exit("待替换节点数过多，不能替换，请检查脚本")

    log.info("3> 初始状态，访问区{}：{}，访问区{}:{}".format(id_az_all_nodes, node_id_choosen, id_az_scd_nodes, nodes_update))
    node_id_1st_update_param = ",".join(nodes_1st_left)
    # 默认环境完整，有四种provider
    provider_flag = False
    provider_lst = []
    provider_id = None
    """provider_flag为True，进行认证服务器切换"""
    if provider_flag:
        log.info("默认参数完整，更新时一并更新访问区的鉴权服务器")
        provider_lst = create_all_kind_of_provider()
        provider_id = random.choice(provider_lst)
        msg_update = nas_common.update_access_zone(access_zone_id=id_az_all_nodes, node_ids=node_id_1st_update_param, auth_provider_id=provider_id)

    else:
        msg_update = nas_common.update_access_zone(access_zone_id=id_az_all_nodes, node_ids=node_id_1st_update_param)
    common.judge_rc(msg_update["err_no"], 0, "update az:{},used node id:{}".format(id_az_all_nodes, node_id_1st_update_param))
    log.info("3-1 > 使用update_access_zone命令选取节点{}释放待替换换访问区中的{}".format(nodes_1st_left, node_id_1st_mv))

    nodes_replace = random.sample(nodes_update, len(node_id_1st_mv))
    nodes_2nd_replace = list(set(nodes_update) - set(nodes_replace))
    nodes_2nd_replace_param = ",".join(nodes_2nd_replace + node_id_1st_mv)
    msg_update = nas_common.update_access_zone(access_zone_id=id_az_scd_nodes, node_ids=nodes_2nd_replace_param)
    common.judge_rc(msg_update["err_no"], 0, "update az,nodes:{},release id:{}".format(node_id_1st_mv, nodes_replace))
    log.info("3-2 > 使用update_access_zone命令选取节点{}补充访问区{}，以防访问区节点数为 1，无法释放；释放节点{}".format
             (node_id_1st_mv, id_az_scd_nodes, nodes_replace))

    nodes_3rd_replace_param = ",".join(nodes_replace + nodes_1st_left)
    msg_update = nas_common.update_access_zone(access_zone_id=id_az_all_nodes, node_ids=nodes_3rd_replace_param)
    common.judge_rc(msg_update["err_no"], 0, "update az:{},used node id:{}".format(id_az_all_nodes, nodes_3rd_replace_param))
    log.info("3-3 > 使用update_access_zone命令选取节点{}替换为节点{}，替换个数为{}".format(node_id_1st_mv, nodes_replace, len(node_id_1st_mv)))

    log.info("4> 结束状态：访问区{}：{}，访问区{}:{};检查所有节点的服务状态是否正常".format
             (id_az_all_nodes, nodes_3rd_replace_param, id_az_scd_nodes, nodes_2nd_replace_param))
    nas_check = nas_common.check_nas_status()
    common.judge_rc(nas_check, 0, "nas status of node is wrong")
    log.info("need add touch && case passed!")
    return


def nas_main():
    log_file_path = log.get_log_path(FILE_NAME)
    log.init(log_file_path, True)
    prepare_clean.nas_test_clean()
    case()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    nas_main()

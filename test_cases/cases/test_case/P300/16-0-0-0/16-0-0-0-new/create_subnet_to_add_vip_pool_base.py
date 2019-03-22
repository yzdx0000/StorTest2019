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
 date 2018-11-30
 @summary：
    创建业务子网，添加vip池，参数为基本参数，覆盖常见测试场景
 @steps:
    1、根据是否继承的标志位决定是否清除环境
    2、为访问区创建业务子网
    3、添加vip池
    4、检查所有访问区的服务状态/子网状态是否正常
    5、根据遗传标志位决定是或否清除环境

 @changelog：
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字
NAS_PATH = get_config.get_one_nas_test_path()                            # /mnt/volume/nas_test_dir
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/volume/nas_test_dir/nas_16_6_0_16
BASE_NAS_PATH = os.path.dirname(NAS_PATH)                                # /mnt/volume
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)                           # nas_test_dir


def case():

    """函数主体"""
    node_obj = common.Node()
    node_list_all = node_obj.get_nodes_id()
    node_list_string = []
    for node_id_int in node_list_all:
        node_list_string.append(str(node_id_int))

    lenth_nodes_up = len(node_list_string)
    """默认继承True，遗留（不删除）子网True"""
    flag_inherit = True
    flag_genetic = True
    log.info("1> 根据是否继承的标志位{}决定是(False)否(True)清除并创建新的nas环境".format(flag_inherit))
    access_zone_id = '0'
    access_zone_id_lst = []
    az_new_name = '_'
    all_nodes_string = ",".join(node_list_string)

    if flag_inherit:
        log.info("inherit, would not delete")
        msg_get_az = nas_common.get_access_zones(print_flag=False)
        common.judge_rc(msg_get_az['err_no'], 0, "get access zone ")
        if len(msg_get_az['result']['access_zones']) < 1:
            log.info("There is no access zone to inherit:{}".format(msg_get_az['result']))
            flag_inherit = False
        else:
            for az in msg_get_az['result']['access_zones']:
                access_zone_id_lst.append(az['id'])

    if not flag_inherit:
        log.info("no access zone to inherit,create a new one")
        prepare_clean.nas_test_clean()
        az_new_name = "az_" + str(time.localtime().tm_hour) + str(time.localtime().tm_min) + str(time.localtime().tm_sec)
        msg_crt_az = nas_common.create_access_zone(node_ids=all_nodes_string, name=az_new_name)
        common.judge_rc(msg_crt_az['err_no'], 0, "create new access zone")
        access_zone_id = msg_crt_az["result"]
        access_zone_id_lst.append(access_zone_id)
    for idd in access_zone_id_lst:
        msg_enable_nas = nas_common.enable_nas(access_zone_id=idd, print_flag=False)
        common.judge_rc(msg_enable_nas['err_no'], 0, "if it was enable?", False)
    access_zone_id = random.choice(access_zone_id_lst)
    log.info("aceess_zone_id list is {}".format(access_zone_id_lst))
    log.info("2> 为访问区{}创建业务子网".format(access_zone_id))
    sub_net_name = "sub_" + str(time.localtime().tm_hour) + str(time.localtime().tm_min) + str(time.localtime().tm_sec)
    msg_crt_subnet = nas_common.create_subnet(access_zone_id=access_zone_id, name=sub_net_name, ip_family="IPv4", svip=nas_common.SUBNET_SVIP,
                                              subnet_mask=nas_common.SUBNET_MASK, subnet_gateway=nas_common.SUBNET_GATEWAY, network_interfaces=nas_common.SUBNET_NETWORK_INTERFACES)
    common.judge_rc(msg_crt_subnet['err_no'], 0, "create subnet")
    sub_net_id = msg_crt_subnet['result']

    log.info("3> 为业务子网{}添加vip池".format(sub_net_id))

    msg_get_az_node_id = nas_common.get_access_zones(ids=access_zone_id)
    common.judge_rc(msg_get_az_node_id['err_no'], 0, "get access zone ")
    node_id_lst_in_az = msg_get_az_node_id['result']['access_zones'][0]['node_ids']

    node_count = len(node_id_lst_in_az)
    vip_count = node_count * 4

    vip_org = str(nas_common.VIP_3_ADDRESSES)
    vip_org_lst = vip_org.split(",")
    if vip_count > len(vip_org_lst):
        common.except_exit("conf file wrong;{} vips {} less than nodes*4 {}".format(len(vip_org_lst), vip_org_lst, vip_count))
    vip_add = random.sample(vip_org_lst, vip_count)
    """
    print vip_add
    str_null = "\'\'"
    for iip in vip_add:
        if iip == str_null:
            vip_add.remove(iip)
            print "aaa"
            print iip
    """
    vip_add_string = ",".join(vip_add)
    """
    print vip_add_string
    print vip_add
    print str_null
    raw_input()
    """
    msg_add_ip_pool = nas_common.add_vip_address_pool(subnet_id=sub_net_id, domain_name=nas_common.VIP_DOMAIN_NAME, vip_addresses=vip_add_string,
                                                      supported_protocol=nas_common.NAS, allocation_method=nas_common.DYNAMIC)
    common.judge_rc(msg_add_ip_pool['err_no'], 0, "add vip pool")
    vip_pool_id = msg_add_ip_pool['result']

    log.info("4> 检查所有访问区{}的服务状态/子网状态是否正常".format(node_id_lst_in_az))
    node_id_lst_in_az_str = []
    for nid in node_id_lst_in_az:
        node_id_lst_in_az_str.append(str(nid))
    node_id_str = ",".join(node_id_lst_in_az_str)
    nas_service_check = nas_common.check_nas_status(get_node_id=node_id_str)
    common.judge_rc(nas_service_check, 0, "nas service check")
    vip_service_check = nas_common.check_svip_in_eth(sub_svip=nas_common.SUBNET_SVIP, sub_subnet_mask=nas_common.SUBNET_MASK, sub_network_interfaces=nas_common.SUBNET_NETWORK_INTERFACES)
    common.judge_rc(vip_service_check, 0, "vip service check", False)

    log.info("5> 根据遗传标志位{}决定是(True)否(False)删除子网".format(flag_genetic))
    if not flag_genetic:
        dele_vip_info = "delete vip {}".format(vip_pool_id)
        dele_sub_info = "delete subnet {}".format(sub_net_id)
        log.info(dele_vip_info)
        msg_dele_vip = nas_common.delete_vip_address_pool(vip_address_pool_id=vip_pool_id, print_flag=False)
        common.judge_rc(msg_dele_vip['err_no'], 0, dele_vip_info)

        log.info(dele_sub_info)
        msg_dele_subnet = nas_common.delete_subnet(subnet_id=sub_net_id, print_flag=False)
        common.judge_rc(msg_dele_subnet['err_no'], 0, dele_sub_info)
    log.info("case passed!")
    return


def nas_main():
    log_file_path = log.get_log_path(FILE_NAME)
    log.init(log_file_path, True)
    case()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    nas_main()

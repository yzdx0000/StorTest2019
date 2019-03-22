# -*-coding:utf-8 -*
import os
import time

import utils_path
import random
import commands
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
# date 2018-07-18
# @summary：
# 验证enable_nas是否成功
# @steps:
#    1、创建访问分区(使用命令pscli --command=create_access_zone)；
#    2、创建业务子网(使用pscli --command=create_subnet )；
#    3、创建vip(使用命令pscli --command=add_vip_address_pool)；
#    4、执行enalbe_nas指令(pscli --command=enalbe_nas)
# @changelog：
####################################################################################
VOLUME_NAME = get_config.get_one_volume_name()
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
NAS_PATH = get_config.get_one_nas_test_path()                            # /mnt/volume/nas_test_dir
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/volume/nas_test_dir/nas_16_6_0_22
BASE_NAS_PATH = os.path.dirname(NAS_PATH)                                # /mnt/volume
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)                           # nas_test_dir
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


def case():
    '''

    :return:
    '''

    '''1>创建访问分区'''
    obj_node = common.Node()
    node_id_list = obj_node.get_nodes_id()
    node_ids = ','.join(str(i) for i in node_id_list)
    check_result = nas_common.create_access_zone(node_ids=node_ids,
                                                 name=FILE_NAME)
    if check_result["detail_err_msg"] != "":
        common.except_exit("create_access_zone failed!!")
    access_zone_id = check_result["result"]

    '''2>创建业务子网'''
    check_result = nas_common.create_subnet(access_zone_id=access_zone_id,
                                            name=FILE_NAME+"_SUBNET",
                                            ip_family="IPv4",
                                            svip=nas_common.SUBNET_SVIP,
                                            subnet_mask=nas_common.SUBNET_MASK,
                                            subnet_gateway=nas_common.SUBNET_GATEWAY,
                                            network_interfaces=nas_common.SUBNET_NETWORK_INTERFACES)
    if check_result["detail_err_msg"] != "":
        common.except_exit("create_subnet failed!!")
    subnet_id = check_result["result"]

    '''3>创建vip'''
    check_result = nas_common.add_vip_address_pool(subnet_id=subnet_id,
                                                   domain_name="www.domiantest.com",
                                                   vip_addresses=nas_common.VIP_ADDRESSES,
                                                   supported_protocol="NAS",
                                                   allocation_method="DYNAMIC")
    if check_result["detail_err_msg"] != "":
        common.except_exit("add_vip_address_pool failed!!")

    '''4>启动nas'''
    check_result = nas_common.enable_nas(access_zone_id=access_zone_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("enable_nas failed!!")
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    prepare_clean.nas_test_clean(FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
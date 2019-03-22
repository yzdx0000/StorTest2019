#-*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean
import random
import nas_common
import json
"""
author@liangxy
date 2018-08-03
@summary：
     缺陷自动化：更新子网设置时并未更改subnet_mask，subnet_mask误更改为0
@steps:
    1、在节点上创建访问区FILE_NAME_az并返回访问区id
    2、添加subnet，d获取subnet中的result值，返回i
    3、更新subnet的mtu值
    4、再次获取subnet的result值
    5、比较两个result值，除更新的mtu外，各项内容应对应相同
    6、删除访问区、删除subnet
    7、返回测试结果
@changelog：
    最后修改时间：2018-0804
    修改内容：根据nas交付进度，更新删除函数
    todo：子网更新暂未交付
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
"""目前和nas_common中SUBNET网卡相关联,可拟通过节点id获取全部网络设置"""
SUBNET_ETH_NODES = 2


def case():
    log.info("case begin")
    """节点列表"""
    ob_node = common.Node()
    case_node_id = SUBNET_ETH_NODES
    """id_az_add_del为添加后要删除的访问区列表"""
    id_az_add_del = []
    info_snet_for_cmp = []

    """
    添加第一个节点上访问分区,注意以脚本名命名，方便清理环境
    """
    msg_add_az1 = nas_common.create_access_zone(case_node_id, FILE_NAME + "az")
    if "" != msg_add_az1["detail_err_msg"]:
        raise Exception("create az in node %s failed" % case_node_id)
    msg_az1_id = msg_add_az1["result"]
    id_az_add_del.append(msg_az1_id)

    """创建第一个访问区上的子网"""
    msg_crt_subnet = nas_common.create_subnet(msg_az1_id, FILE_NAME+"snet", "IPv4", nas_common.SUBNET_SVIP,
                                              nas_common.SUBNET_MASK,
                                              nas_common.SUBNET_NETWORK_INTERFACES, nas_common.SUBNET_GATEWAY,
                                              nas_common.SUBNET_MTU)

    if "" != msg_crt_subnet["detail_err_msg"]:
        raise Exception("create subnet in node %s failed" % msg_az1_id)
    subnet_id = msg_crt_subnet["result"]
    msg_get_subnet = nas_common.get_subnets(subnet_id)
    if "" != msg_get_subnet["detail_err_msg"]:
        raise Exception("get subent in node %s failed" % msg_az1_id)
    info_snet_for_cmp.append(msg_get_subnet["result"]["subnets"][0]["subnet_mask"])
    """更新子网的mtu值"""
    mtu_update = msg_get_subnet["result"]["subnets"][0]["mtu"] + 100
    msg_update_snet = nas_common.update_subnet(subnet_id=subnet_id, mtu=mtu_update)
    if "" != msg_update_snet["detail_err_msg"]:
        raise Exception("update subent in node %s failed" % msg_az1_id)
    """再次获取subnet的参数值"""
    msg_get_subnet = nas_common.get_subnets(subnet_id)
    if "" != msg_get_subnet["detail_err_msg"]:
        raise Exception("get subent in node %s failed" % msg_az1_id)
    info_snet_for_cmp.append(msg_get_subnet["result"]["subnets"][0]["subnet_mask"])
    cmp_update_info = cmp(info_snet_for_cmp[0], info_snet_for_cmp[1])
    if 0 != cmp_update_info:
        raise Exception("Err:%s is not update,but changed(%d -> %d)" %
        ("subnet_mask", info_snet_for_cmp[0], info_snet_for_cmp[1]))

    log.info("case succeed!")

    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
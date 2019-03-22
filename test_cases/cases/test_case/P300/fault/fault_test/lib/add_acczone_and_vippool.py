# -*-coding:utf-8 -*
# /user/bin/python
import os
import time
import random

import utils_path
import common
import nas_common
import log
import get_config
import prepare_clean

def add_accesszone_and_enableservice(access_zone_node_ids,access_zone_name,auth_provider_id=None,enable_NAS=True,
                                     protocol_types=None,enable_S3=True):
    """创建访问区并激活S3和NAS服务
    :param access_zone_node_ids: Required:True   Type:string  Help:The node id list in access zone, e.g. 1,2,3
    :param access_zone_name: Required:True   Type:string  Help:The name of access zone to create, e.g. AccessZone1
    :param auth_provider_id: Required:False  Type:int     Help:The authentication provider id, if not specified,
    then will use the LOCAL authentication provider.
    :param enable_NAS: required:True Type:string  Help:Whether to enable NAS
    :param :param protocol_types:Required:False  Type:string  Help:The NAS export protocol that you want to operate on.
    Available protocol type:['NFS', 'SMB', 'FTP'] e.g. NFS,SMB,FTP,If not exist, operate on all protocol type.
    :param enable_S3: required:True Type:string  Help:Whether to enable S3
    :return: access_zone_id(访问区id)
    """
    log.info("\t[ create_access_zone ]")
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_ids, name=access_zone_name,
                                         auth_provider_id=auth_provider_id)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('create_access_zone failed!!!')
    access_zone_id = msg1["result"]

    if enable_NAS == True:
        log.info("\t[ enable NAS ]")
        msg2 = nas_common.enable_nas(access_zone_id=access_zone_id, protocol_types=protocol_types)
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit('enable_nas failed!!!')
    else:
        pass
    if enable_S3 == True:
        log.info("\t[ enable S3 ]")
        msg3 = nas_common.enable_s3(access_zone_id=access_zone_id)
        if msg3["err_msg"] != "" or msg3["detail_err_msg"] != "":
            common.except_exit('enable_s3 failed!!!')
    else:
        pass
    return access_zone_id

def create_svip_and_vippool(access_zone_id, svip, subnet_mask, network_interfaces,vip_domain_name,
                            vip_vip_addresses, vip_supported_protocol, vip_load_balance_policy="LB_CONNECTION_COUNT",
                            vip_ip_failover_policy="IF_ROUND_ROBIN",vip_rebalance_policy="RB_AUTOMATIC",
                            subnet_gateway=None, mtu=None):
    """
    :创建业务子网并添加vip池
    :return vip_domain_name
    """
    log.info("\t[  创建业务子网 ]")
    sub_name = "%s_subnet_%s" % (vip_supported_protocol, access_zone_id)
    msg1 = nas_common.create_subnet(access_zone_id=access_zone_id,
                                    name= sub_name,
                                    ip_family=nas_common.IPv4,
                                    svip=svip,
                                    subnet_mask=subnet_mask,
                                    subnet_gateway=subnet_gateway,
                                    network_interfaces=network_interfaces,
                                    mtu=mtu)

    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('create_subnet failed!!!')
    subnet_id = msg1["result"]

    if vip_supported_protocol == 'S3':
        vip_load_balance_policy = "LB_ROUND_ROBIN"
        vip_ip_failover_policy = "IF_ROUND_ROBIN"
    log.info("\t[  创建vip地址池 ]")
    msg1 = nas_common.add_vip_address_pool(subnet_id=subnet_id,
                                           domain_name=vip_domain_name,
                                           vip_addresses=vip_vip_addresses,
                                           supported_protocol=vip_supported_protocol,
                                           allocation_method='DYNAMIC',
                                           load_balance_policy=vip_load_balance_policy,
                                           ip_failover_policy=vip_ip_failover_policy,
                                           rebalance_policy = vip_rebalance_policy)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('add_vip_address_pool failed!!!')
    vip_address_pool_id =  msg1['result']
    msg1 = nas_common.get_vip_address_pools(ids=vip_address_pool_id)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('get_vip_address_pools failed!!!')
    domain_name = msg1['result']['ip_address_pools'][0]['domain_name']
    return domain_name

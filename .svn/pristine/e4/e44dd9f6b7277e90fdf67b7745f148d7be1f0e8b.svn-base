#!/usr/bin/python
# -*- coding:utf-8 -*-

from multiprocessing import Process
import os
import time
import json
import log
import random
import get_config
import common
import remote
import snap_common

DEBUG = "on"    # on: 测试后不清理环境，off: 测试后清理环境

"""节点IP信息"""
NODE_IP_LIST = get_config.get_allparastor_ips()
RANDOM_NODE_IP = NODE_IP_LIST[random.randint(0, len(NODE_IP_LIST) - 1)]

"""客户端IP信息"""
CLIENT_IP_1 = get_config.get_client_ip(0)
CLIENT_IP_2 = get_config.get_client_ip(1)
CLIENT_IP_3 = get_config.get_client_ip(2)

"""卷名称"""
VOLUME_NAME = get_config.get_one_volume_name()

"""测试全路径，注意：nas_test_dir右侧不要加"/" """
NAS_PATH = get_config.get_one_nas_test_path()       # /mnt/volume/nas_test_dir
LAST_PART = os.path.basename(NAS_PATH)              # /mnt/volume
ROOT_DIR = "%s:/%s/" % (VOLUME_NAME, LAST_PART)     # volume:/nas_test_dir/
BASE_NAS_PATH = os.path.dirname(NAS_PATH)           # /mnt/volume"
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)      # nas_test_dir
NAS_PATH_ABSPATH = os.path.abspath(NAS_PATH)        # /mnt/volume/nas_test_dir


"""可以做故障的网卡信息，节点数据网卡名列表"""
ETH_LIST = ["ens192", "ens224", "ens256"]
ETH_IP = "10.2.42.133"

"""可以做故障的IP列表"""
FAULT_NODE_IP_LST = ["10.2.42.137"]

"""SUBNET和VIP地址池信息"""
"""不用分组参数"""
IPv4 = get_config.get_ip_family()[0]
IPv6 = get_config.get_ip_family()[1]
NAS = get_config.get_vip_supported_protocol()[0]                            # supported_protocol之NAS
ISCSI = get_config.get_vip_supported_protocol()[1]                          # supported_protocol之ISCSI
STATIC = get_config.get_vip_allocation_methods()[0]                         # allocation_method之STATIC
DYNAMIC = get_config.get_vip_allocation_methods()[1]                        # allocation_method之DYNAMIC
BALANCE_LB_ROUND_ROBIN = get_config.get_vip_load_balance_policy()[0]        # load_balance_policy之LB_ROUND_ROBIN
BALANCE_LB_CONNECTION_COUNT = get_config.get_vip_load_balance_policy()[1]   # load_balance_policy之LB_CONNECTION_COUNT
BALANCE_LB_THROUGHPUT = get_config.get_vip_load_balance_policy()[2]         # load_balance_policy之LB_THROUGHPUT
BALANCE_LB_CPU_USAGE = get_config.get_vip_load_balance_policy()[3]          # load_balance_policy之LB_CPU_USAGE
IP_IF_ROUND_ROBIN = get_config.get_ip_failover_policy()[0]             # ip_failover_policy之LB_ROUND_ROBIN
IP_IF_CONNECTION_COUNT = get_config.get_ip_failover_policy()[1]        # ip_failover_policy之LB_CONNECTION_COUNT
IP_IF_THROUGHPUT = get_config.get_ip_failover_policy()[2]              # ip_failover_policy之LB_THROUGHPUT
IP_IF_CPU_USAGE = get_config.get_ip_failover_policy()[3]               # ip_failover_policy之LB_CPU_USAGE
IP_RB_DISABLED = get_config.get_rebalance_policy()[0]                       # rebalance_policy之IP_RB_DISABLED
IP_RB_AUTOMATIC = get_config.get_rebalance_policy()[1]                      # rebalance_policy之IP_RB_AUTOMATIC
"""第一组"""
SUBNET_SVIP = get_config.get_subnet_svip()[0]
SUBNET_MASK = get_config.get_subnet_mask()[0]
SUBNET_GATEWAY = get_config.get_subnet_gateway()[0]
SUBNET_NETWORK_INTERFACES = get_config.get_subnet_network_interface()[0]    # 一张网卡名
SUBNET_MTU = get_config.get_subnet_mtu()[0]
VIP_DOMAIN_NAME = get_config.get_vip_domain_name()[0]
VIP_ADDRESSES = get_config.get_vip_addresses()[0]                           # 连续型vip池地址
"""第二组"""
SUBNET_2_SVIP = get_config.get_subnet_svip()[1]
SUBNET_2_MASK = get_config.get_subnet_mask()[0]
SUBNET_2_GATEWAY = get_config.get_subnet_gateway()[0]
SUBNET_2_NETWORK_INTERFACES = get_config.get_subnet_network_interface()[1]  # 多张网卡名
SUBNET_2_MTU = get_config.get_subnet_mtu()[0]
VIP_2_DOMAIN_NAME = get_config.get_vip_domain_name()[1]
VIP_2_ADDRESSES = get_config.get_vip_addresses()[1]                         # 连续型vip池地址
"""第三组"""
VIP_3_ADDRESSES = get_config.get_vip_addresses()[2]                         # 离散型vip池地址


"""NFS客户端IP"""
NFS_1_CLIENT_IP = get_config.get_nfs_client_ip()[0]                  # 10.2.42.135
NFS_2_CLIENT_IP = get_config.get_nfs_client_ip()[1]                  # 10.2.42.136
NFS_3_CLIENT_IP = get_config.get_nfs_client_ip()[2]                  # 10.2.42.137

"""FTP客户端IP"""
FTP_1_CLIENT_IP = get_config.get_ftp_client_ip()[0]                  # 10.2.42.135
FTP_2_CLIENT_IP = get_config.get_ftp_client_ip()[1]                  # 10.2.42.135

"""SMB客户端IP和端口"""
SMB_CLIENT_IP_AND_PORT_250 = '10.2.42.242:8270'
SMB_CLIENT_IP_AND_PORT_253 = '10.2.41.253:8270'
DEFAULT_SMB_CLIENT_IP_AND_PORT = SMB_CLIENT_IP_AND_PORT_253

"""LDAP服务器信息"""
"""第一组"""
LDAP_IP_ADDRESSES = get_config.get_ldap_ip_addresses()[0]        # 10.2.41.181
LDAP_BASE_DN = get_config.get_ldap_base_dn()[0]                  # dc=test,dc=com
LDAP_BIND_DN = get_config.get_ldap_bind_dn()[0]                  # cn=root,dc=test,dc=com
LDAP_BIND_PASSWORD = get_config.get_ldap_bind_passwd()[0]                # 111111
LDAP_DOMAIN_PASSWORD = get_config.get_ldap_domain_passwd()[0]            # 111111
LDAP_USER_SEARCH_PATH = get_config.get_ldap_user_search_path()[0]        # ou=People,dc=test,dc=com
LDAP_GROUP_SEARCH_PATH = get_config.get_ldap_group_search_path()[0]      # ou=Group,dc=test,dc=com
LDAP_USER_1_NAME = get_config.get_ldap_user_name()[0]                    # ldapuser1  可使用su登录的用户
LDAP_USER_2_NAME = get_config.get_ldap_user_name()[1]                    # ldapuser2  有附属组的用户
LDAP_USER_3_NAME = get_config.get_ldap_user_name()[2]                    # 用户@a  有特殊字符与中文的用户
LDAP_USER_1_PASSWORD = get_config.get_ldap_user_passwd()[0]              # 111111 ldap第一个用户的密码
LDAP_USER_2_PASSWORD = get_config.get_ldap_user_passwd()[1]              # 111111
LDAP_USER_3_PASSWORD = get_config.get_ldap_user_passwd()[2]              # 111111
LDAP_GROUP_1_NAME = get_config.get_ldap_group_name()[0]                  # ldapgroup1  ldap_user_name第一个用户的用户组
LDAP_GROUP_2_NAME = get_config.get_ldap_group_name()[1]                  # 用户组1  有中文的用户组
LDAP_GROUP_3_NAME = get_config.get_ldap_group_name()[2]                  # group@a1  有特殊字符的用户组
"""第二组"""
LDAP_2_IP_ADDRESSES = get_config.get_ldap_ip_addresses()[1]              # 10.2.41.239
LDAP_2_BASE_DN = get_config.get_ldap_base_dn()[1]                        # dc=ldap-pdc,dc=com
LDAP_2_BIND_DN = get_config.get_ldap_bind_dn()[1]                        # cn=Manager,dc=ldap-pdc,dc=com
LDAP_2_BIND_PASSWORD = get_config.get_ldap_bind_passwd()[1]              # 111111
LDAP_2_DOMAIN_PASSWORD = get_config.get_ldap_domain_passwd()[1]          # 111111
LDAP_2_USER_SEARCH_PATH = get_config.get_ldap_user_search_path()[1]      # ou=People,dc=ldap-pdc,dc=com
LDAP_2_GROUP_SEARCH_PATH = get_config.get_ldap_group_search_path()[1]    # ou=Group,dc=ldap-pdc,dc=com
LDAP_2_USER_1_NAME = get_config.get_ldap_user_name()[3]                  # user A  可使用su登录的用户
LDAP_2_GROUP_1_NAME = get_config.get_ldap_group_name()[3]                # Domain Users  用户user A的组
"""第三组"""
LDAP_3_IP_ADDRESSES = "10.2.41.185"  # 原10.2.41.148
LDAP_3_BASE_DN = "dc=admintest1,dc=com"
LDAP_3_BIND_DN = "cn=root,dc=admintest1,dc=com"
LDAP_3_BIND_PASSWORD = "111111"
LDAP_3_USER_SEARCH_PATH = "ou=People,dc=admintest1,dc=com"
LDAP_3_GROUP_SEARCH_PATH = "ou=Group,dc=admintest1,dc=com"

"""NIS服务器信息"""
NIS_IP_ADDRESSES = get_config.get_nis_ip_address()[0]
NIS_DOMAIN_NAME = get_config.get_nis_domain_name()[0]
NIS_USER_1 = get_config.get_nis_users()[0]
NIS_USER_2 = get_config.get_nis_users()[1]
NIS_USER_PW = get_config.get_nis_user_pw()[0]
NIS_GROUP_1 = get_config.get_nis_groups()[0]
NIS_GROUP_2 = get_config.get_nis_groups()[1]

"""AD服务器信息"""
AD_DNS_ADDRESSES = get_config.get_ad_dns_address()[0]
AD_DOMAIN_NAME = get_config.get_ad_domain_name()[0]
AD_USER_NAME = get_config.get_ad_user_name()[0]                 # 服务器管理员用户名
AD_ADMIN_USER_NAME_1 = get_config.get_ad_user_name()[1]         # autoadminuser1是AD域的用户，也在Domain Admins安全组中
AD_ADMIN_USER_NAME_2 = get_config.get_ad_user_name()[2]         # autoadminuser2是AD域的用户，但不在Domain Admins安全组中
AD_PASSWORD = get_config.get_ad_password()[0]           # 服务器管理员用户密码
AD_USER_1 = get_config.get_ad_users()[0]                # 登录用户1
AD_USER_2 = get_config.get_ad_users()[1]                # 登录用户2
AD_USER_3 = get_config.get_ad_users()[2]                # 登录用户3
AD_USER_4 = get_config.get_ad_users()[3]                # ad域特殊用户1，有附属组
AD_USER_PW = get_config.get_ad_user_pw()[0]             # 登录用户的密码
AD_GROUP = get_config.get_ad_groups()[0]                # 登录用户组
AD_USER_1st_GROUP = get_config.get_ad_groups()[1]       # ad域特殊用户1的其中一个组
AD_USER_2nd_GROUP = get_config.get_ad_groups()[2]       # ad域特殊用户1的其中一个组


def create_nas_path(path):
    """
    创建NAS路径
    :Author: zhangchengyu
    :Date: 2018-08-22
    :param path: NAS的路径
    :return: 无
    """
    # 创建NAS总路径
    mkdir_nas_path()

    # 创建本用例的NAS路径
    cmd = 'mkdir %s' % path
    rc, stdout = common.run_command(RANDOM_NODE_IP, cmd)
    if 0 != rc:
        log.error('%s failed!!!' % cmd)
        raise Exception('%s failed!!!' % cmd)
    return


def mkdir_nas_path():
    """创建NAS总路径
    :Author: zhangchengyu
    :Date: 2018-08-22
    :return: 100或0,0为顺利创建，100为目录存在
    ：changelog：增加-p参数，日志打印mkdir的rc值--by liangxy
    """
    cmd = 'ls %s' % NAS_PATH
    rc, stdout = common.run_command(RANDOM_NODE_IP, cmd)
    if 0 == rc:
        log.info('%s is exist!' % NAS_PATH)
        return 100
    cmd = 'mkdir -p %s' % NAS_PATH
    rc, stdout = common.run_command(RANDOM_NODE_IP, cmd)
    if rc != 0:
        raise Exception('{} mkdir faild!!!rc is {}'.format(NAS_PATH, rc))
    return 0


def create_access_zone(node_ids, name, auth_provider_id=None, isns_address=None, print_flag=True, fault_node_ip=None):
    """创建访问区
    :param node_ids: Required:True   Type:string  Help:The node id list in access zone, e.g. 1,2,3
    :param name: Required:True   Type:string  Help:The name of access zone to create, e.g. AccessZone1
    :param auth_provider_id: Required:False  Type:int     Help:The authentication provider id, if not specified,
    then will use the LOCAL authentication provider.
    :param isns_address: equired:False  Type:string  Help:The iSNS ip address.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ create_access_zone ]")
    rc, stdout = common.create_access_zone(node_ids=node_ids, name=name, auth_provider_id=auth_provider_id,
                                           isns_address=isns_address, print_flag=print_flag,
                                           fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, "create_access_zone failed", exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def delete_access_zone(access_zone_id, print_flag=True, fault_node_ip=None):
    """删除访问区
    :Author: jiangxiaoguang
    :Date: 2018-08-06
    :param access_zone_id: Required:True   Type:int     Help:The access zone id
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ delete_access_zone ]")
    rc, stdout = common.delete_access_zone(id=access_zone_id, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'delete_access_zone failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def update_access_zone(access_zone_id, name=None, node_ids=None, auth_provider_id=None, isns_address=None,
                       print_flag=True, fault_node_ip=None):
    """修改访问区
    :Author: jiangxiaoguang
    :Date: 2018-08-06
    :param access_zone_id: Required:True   Type:int     Help:Access zone id.
    :param name: Required:False  Type:string  Help:Access zone name.
    :param node_ids: Required:False  Type:string  Help:The node id list in access zone.
    :param auth_provider_id: Required:False  Type:int     Help:The authentication provider id.
    :param isns_address: Required:False  Type:string  Help:The isns ip address.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ update_access_zone ]")
    rc, stdout = common.update_access_zone(id=access_zone_id, name=name, node_ids=node_ids,
                                           auth_provider_id=auth_provider_id, isns_address=isns_address,
                                           print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'update_access_zone failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_access_zones(ids=None, print_flag=True, fault_node_ip=None):
    """查询访问区
    :param ids: Required:False  Type:string  Help:The access zone id list to get, e.g. 1,2,3
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_access_zones ]")
    rc, stdout = common.get_access_zones(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_access_zones failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_access_zones_ids_list():
    """
    Author: zhangchengyu
    Date :2018-08-6
    Description：获取access_zones的id列表
    :return: access_zones的id列表，格式为：1,2,3
    """
    log.info("\t[ access_zones_ids_list ]")
    msg = get_access_zones()
    access_zones = msg['result']['access_zones']
    id_list = []
    for access_zone in access_zones:
        id_list.append(access_zone['id'])
    access_zones_ids = ','.join(str(i) for i in id_list)

    return access_zones_ids


def record_info_for_enablenas(iplst):
    """
    Author:         chenjy1
    Date :          2018-11-20
    Description：   在enable_nas期间，7分钟未成功则记录一些信息，方便定位
    :param iplst:  记录信息的节点
    :return:       无
    """
    enable_nas_timeout_minutes = 10
    time.sleep((enable_nas_timeout_minutes-3)*60)
    cmd_lst = []
    cmd_lst.append('df /')
    cmd_lst.append('mount |grep system_volume')
    cmd_lst.append('ps aux |grep nas')
    cmd_lst.append('pstack $(pidof oCnas)')
    for ip in iplst:
        for cmd in cmd_lst:
            common.run_command(ip, cmd, print_flag=True)  # 仅看信息不判断
    return


def enable_nas(access_zone_id, protocol_types=None, print_flag=True, fault_node_ip=None):
    """启用协议
    :param access_zone_id: Required:True   Type:int     Help:The access zone id that you want to operate on.
    :param protocol_types: Required:False  Type:string  Help:The NAS export protocol that you want to operate on.
    Available protocol type:['NFS', 'SMB', 'FTP'] e.g. NFS,SMB,FTP
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ enable_nas ]")
    p1 = Process(target=record_info_for_enablenas, args=(get_config.get_allparastor_ips(),))
    p1.daemon = True
    p1.start()
    rc, stdout = common.enable_nas(access_zone_id=access_zone_id, protocol_types=protocol_types, print_flag=print_flag,
                                   fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'enable_nas failed', exit_flag=False)
    msg = common.json_loads(stdout)
    p1.terminate()
    p1.join()
    return msg


def disable_nas(access_zone_id, protocol_types=None, print_flag=True, fault_node_ip=None):
    """关闭协议
    :param access_zone_id: Required:True   Type:int     Help:The access zone id that you want to operate on.
    :param protocol_types:Required:False  Type:string  Help:The NAS export protocol that you want to operate on.
    Available protocol type:['NFS', 'SMB', 'FTP'] e.g. NFS,SMB,FTP
    :param node_ip:Required:False  执行cmd命令的节点ip
    :return:执行cmd命令的字典格式返回值
    """
    log.info("\t[ disable_nas ]")
    rc, stdout = common.disable_nas(access_zone_id=access_zone_id, protocol_types=protocol_types, print_flag=print_flag,
                                    fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'disable_nas failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def enable_s3(access_zone_id, print_flag=True, fault_node_ip=None):
    """
    启动S3
    :author zhangchengyu
    :date  2018.12.05
    :param access_zone_id: Required:True   Type:string  Help:access zone id
    :param print_flag:是否打印结果，True为打印，False为不打印
    :param fault_node_ip:故障节点的ip
    :return:执行cmd命令的字典格式返回值
    """
    log.info("\t[ enable_s3 ]")
    p1 = Process(target=record_info_for_enablenas, args=(get_config.get_allparastor_ips(),))
    p1.daemon = True
    p1.start()
    rc, stdout = common.enable_s3(access_zone_id=access_zone_id, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'enable_s3', exit_flag=False)
    msg = common.json_loads(stdout)
    p1.terminate()
    p1.join()
    return msg


def disable_s3(access_zone_id, print_flag=True, fault_node_ip=None):
    """
    关闭S3
    :author zhangchengyu
    :date  2018.12.05
    :param access_zone_id: Required:True   Type:string  Help:access zone id
    :param print_flag:是否打印结果，True为打印，False为不打印
    :param fault_node_ip:故障节点的ip
    :return:执行cmd命令的字典格式返回值
    """
    log.info("\t[ disable_s3 ]")
    rc, stdout = common.disable_s3(access_zone_id=access_zone_id, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'disable_s3 failed', exit_flag=False)
    msg = common.json_loads(stdout)
    return msg


def create_subnet(access_zone_id, name, ip_family, svip, subnet_mask, network_interfaces, subnet_gateway=None, mtu=None,
                  description=None, print_flag=True, fault_node_ip=None):
    """创建业务子网
    :param access_zone_id: Required:True   Type:int     Help:The access zone id in which create the subnet.
    :param name: Required:True   Type:string  Help:The subnet name
    :param ip_family: Required:True   Type:string  Help:The ip family, eg: [IPv4,IPv6]
    :param svip: Required:True   Type:string  Help:Service vip address of the subnet. Be called svip for short.
    :param subnet_mask: Required:True   Type:int     Help:Subnet mask of the subnet, range:(0, 32]. e.g. 16
    :param subnet_gateway: Required:True   Type:string  Help:Subnet mask of the subnet. e.g. 10.10.0.1
    :param network_interfaces: Required:True   Type:string  Help:Network interface list of the subnet. e.g. eth0,eth1
    :param mtu: Required:False  Type:int     Help:Maximum transfer unit of network interface. Default 1500,
    range: 576~9000
    :param description: Required:False  Help:Subnet description
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ create_subnet ]")
    rc, stdout = common.create_subnet(access_zone_id=access_zone_id, name=name, ip_family=ip_family, svip=svip,
                                      subnet_mask=subnet_mask, subnet_gateway=subnet_gateway,
                                      network_interfaces=network_interfaces, mtu=mtu, description=description,
                                      print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'create_subnet failed', exit_flag=False)

    msg = common.json_loads(stdout)

    return msg


def delete_subnet(subnet_id, print_flag=True, fault_node_ip=None):
    """修改子网
    :Author: jiangxiaoguang
    :Date: 2018-08-06
    :param subnet_id: Required:True   Type:int     Help:The subnet id.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值

    """
    log.info("\t[ delete_subnet ]")
    rc, stdout = common.delete_subnet(id=subnet_id, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'delete_subnet failed', exit_flag=False)

    msg = common.json_loads(stdout)

    return msg


def update_subnet(subnet_id, name=None, svip=None, subnet_mask=None, subnet_gateway=None, network_interfaces=None,
                  mtu=None, description=None, print_flag=True, fault_node_ip=None):
    """修改子网
    :Author: jiangxiaoguang
    :Date: 2018-08-06
    :param subnet_id: Required:True   Type:int     Help:The subnet id.
    :param name: Required:False  Type:string  Help:The subnet name.
    :param svip: Required:False  Type:string  Help:Service vip address of the subnet. Be called svip for short.
    :param subnet_mask: Required:False  Type:int     Help:Subnet mask of the subnet, range:(0, 32]. e.g. 16
    :param subnet_gateway: Required:False  Type:string  Help:Subnet mask of the subnet. e.g. 10.10.0.1
    :param network_interfaces: Required:False  Type:string  Help:Network interface list of the subnet. e.g. eth0,eth1
    :param mtu: Required:False  Type:int     Help:Maximum transfer unit of the subnet. Default 1500, range: 576~9000
    :param description: Required:False  Type:string  Help:Subnet description
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ update_subnet ]")
    rc, stdout = common.update_subnet(id=subnet_id, name=name, svip=svip, subnet_mask=subnet_mask,
                                      subnet_gateway=subnet_gateway, network_interfaces=network_interfaces,
                                      mtu=mtu, description=description, print_flag=print_flag,
                                      fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'update_subnet failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_subnets(ids=None, print_flag=True, fault_node_ip=None):
    """查询业务子网
    :param ids: Required:False  Type:string  Help:The subnet id list, e.g. 1,2,3
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_subnets ]")
    rc, stdout = common.get_subnets(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_subnets failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_subnets_ids_list():
    """
    Author: zhangchengyu
    Date :2018-08-6
    Description：获取subnets 的id列表
    :return: subnets的id列表，格式为：1,2,3
    """
    log.info("\t[ get_subnets_ids_list ]")

    msg = get_subnets()
    subnets = msg['result']['subnets']
    id_list = []
    for subnet in subnets:
        id_list.append(subnet['id'])
    subnet_ids = ','.join(str(i) for i in id_list)

    return subnet_ids


def add_vip_address_pool(subnet_id, domain_name, vip_addresses, supported_protocol, allocation_method,
                         load_balance_policy=None, ip_failover_policy=None, rebalance_policy=None, print_flag=True,
                         fault_node_ip=None):
    """增加vip地址池
    :param subnet_id: Required:True   Type:int     Help:The subnet id that the vip address pool add to.
    :param domain_name: Required:True   Type:string  Help:The domain name of vip address pool.
    :param vip_addresses: Required:True   Type:string  Help:Allow single IP and IP segment, separate by comma.
    e.g.10.0.0.1-5,10.0.0.10
    :param supported_protocol: Required:True   Type:string  Help:Supported protocol of the vip address pool.
    Available supported protocol: ['NAS', 'ISCSI']
    :param allocation_method: Required:True   Type:string  Help:Allocation method of vip address.
    Available allocation method: ['STATIC', 'DYNAMIC']
    :param load_balance_policy: Required:False  Type:string  Help:Load balance policy of vip address.
    Available load balance policy: ['LB_ROUND_ROBIN', 'LB_CONNECTION_COUNT', 'LB_THROUGHPUT', 'LB_CPU_USAGE'].
    Default is LB_ROUND_ROBIN
    :param ip_failover_policy: Required:False  Type:string  Help:IP failover policy of vip address.
    Available IP failover policy protocol: ['IF_ROUND_ROBIN', 'IF_CONNECTION_COUNT', 'IF_THROUGHPUT', 'IF_CPU_USAGE'].
    Default is IF_ROUND_ROBIN
    :param rebalance_policy: Required:False  Type:string  Help:Rebalance policy of vip address.
    Available rebalance policy: ['RB_DISABLED', 'RB_AUTOMATIC']. Default is RB_DISABLED
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ add_vip_address_pool ]")
    rc, stdout = common.add_vip_address_pool(subnet_id=subnet_id, domain_name=domain_name,
                                             vip_addresses=vip_addresses, supported_protocol=supported_protocol,
                                             allocation_method=allocation_method,
                                             load_balance_policy=load_balance_policy,
                                             ip_failover_policy=ip_failover_policy, rebalance_policy=rebalance_policy,
                                             print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'add_vip_address_pool failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def delete_vip_address_pool(vip_address_pool_id, print_flag=True, fault_node_ip=None):
    """删除vip地址池
    :Author: jiangxiaoguang
    :Date: 2018-08-06
    :param vip_address_pool_id: Required:True   Type:int     Help:The vip address pool.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ delete_vip_address_pool ]")
    rc, stdout = common.delete_vip_address_pool(id=vip_address_pool_id, print_flag=print_flag,
                                                fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'delete_vip_address_pool failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def update_vip_address_pool(vip_address_pool_id, domain_name=None, vip_addresses=None, load_balance_policy=None,
                            ip_failover_policy=None, rebalance_policy=None, print_flag=True, fault_node_ip=None):
    """修改vip地址池
    :Author: jiangxiaoguang
    :Date: 2018-08-06
    :param vip_address_pool_id: Required:True   Type:int     Help:The vip address pool id.
    :param domain_name: Required:False  Type:string  Help:The domain name of vip pool, e.g. www.domain.com
    :param vip_addresses: Required:False  Type:string  Help:Allow single IP and IP segment, separate by comma.
    e.g.10.0.0.1-5,10.0.0.10
    :param load_balance_policy: Required:False  Type:string  Help:Load balance policy of vip address.
    Available load balance policy: ['LB_ROUND_ROBIN', 'LB_CONNECTION_COUNT', 'LB_THROUGHPUT', 'LB_CPU_USAGE'].
    Default is LB_ROUND_ROBIN
    :param ip_failover_policy: Required:False  Type:string  Help:IP failover policy of vip address.
    Available IP failover policy protocol: ['IF_ROUND_ROBIN', 'IF_CONNECTION_COUNT', 'IF_THROUGHPUT', 'IF_CPU_USAGE'].
    Default is IF_ROUND_ROBIN
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ update_vip_address_pool ]")
    rc, stdout = common.update_vip_address_pool(id=vip_address_pool_id, domain_name=domain_name,
                                                vip_addresses=vip_addresses, load_balance_policy=load_balance_policy,
                                                ip_failover_policy=ip_failover_policy, rebalance_policy=rebalance_policy,
                                                print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'update_vip_address_pool failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_vip_address_pools(ids=None, print_flag=True, fault_node_ip=None):
    """查询vip地址池
    :param ids: Required:False  Type:string  Help:The vip address pool id list, e.g. 1,2,3
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_vip_address_pools ]")
    rc, stdout = common.get_vip_address_pools(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_vip_address_pools failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_vip_address_pool_ids_list():
    """
    Author: zhangchengyu
    Date :2018-08-6
    Description：获取vip_address_pools的id列表
    :return: vip_address_pools的id列表，格式为：1,2,3
    """
    log.info("\t[ get_vip_address_pool_ids_list ]")

    msg = get_vip_address_pools()
    ip_address_pools = msg['result']['ip_address_pools']
    id_list = []
    for ip_address_pool in ip_address_pools:
        id_list.append(ip_address_pool['id'])

    ip_address_pool_ids = ','.join(str(i) for i in id_list)

    return ip_address_pool_ids


def create_auth_user(auth_provider_id, name, password, primary_group_id, secondary_group_ids=None, home_dir=None,
                     print_flag=True, fault_node_ip=None):
    """创建本地认证用户
    :param auth_provider_id: Required:True   Type:int     Help:The ID of LOCAL type authentication provider
    :param name: Required:True   Type:string  Help:User name.
    :param password: Required:True   Type:string  Help:User password
    :param primary_group_id: Required:True   Type:int     Help:The primary group ID where this user in.
    :param secondary_group_ids: Required:False  Type:string  Help:The secondary group ID list where this user in.
    :param home_dir: Required:False  Type:string  Help:The home directory where this user log in.
    Default is /home/${name}
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ create_auth_user ]")
    rc, stdout = common.create_auth_user(auth_provider_id=auth_provider_id, name=name, password=password,
                                         primary_group_id=primary_group_id, secondary_group_ids=secondary_group_ids,
                                         home_dir=home_dir, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'create_auth_user failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def delete_auth_users(ids, print_flag=True, fault_node_ip=None):
    """删除本地认证用户
    :param ids: Required:True   Type:string  Help:The user ID list
    :param node_ip: Required:True   执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ delete_auth_users ]")
    rc, stdout = common.delete_auth_users(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'delete_auth_users failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def update_auth_user(user_id, password=None, primary_group_id=None, secondary_group_ids=None, print_flag=True,
                     fault_node_ip=None):
    """修改本地认证用户
    :param user_id: Required:True   Type:int     Help:The user ID
    :param password: Required:False  Type:string  Help:User password
    :param primary_group_id: Required:False  Type:int     Help:The primary group ID where this user in.
    :param secondary_group_ids: Required:False  Type:string  Help:The secondary group ID list where this user in.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ update_auth_user ]")
    rc, stdout = common.update_auth_user(id=user_id, password=password, primary_group_id=primary_group_id,
                                         secondary_group_ids=secondary_group_ids, print_flag=print_flag,
                                         fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'update_auth_user failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_auth_users(auth_provider_id, group_id=None, start=None, limit=None, print_flag=True, fault_node_ip=None):
    """查询认证用户
    :param auth_provider_id: Required:True   Type:int     Help:The ID of authentication provider
    :param group_id: Required:False  Type:int     Help:The group ID of authentication users.
    :param start: Required:False  Type:int     Help:The start index in the query result.
    :param limit: Required:False  Type:int     Help:The record numbers to display in once query.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_auth_users ]")
    rc, stdout = common.get_auth_users(auth_provider_id=auth_provider_id, group_id=group_id, start=start, limit=limit,
                                       print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_auth_users failed', exit_flag=False)
    if rc != 0:
        return rc, stdout
    msg = common.json_loads(stdout)

    return rc, msg


def create_auth_group(auth_provider_id, name, print_flag=True, fault_node_ip=None):
    """创建本地认证用户组
    :param auth_provider_id: Required:True   Type:int     Help:The ID of LOCAL type authentication provider
    :param name: Required:True   Type:string  Help:Group name.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ create_auth_group ]")
    rc, stdout = common.create_auth_group(auth_provider_id=auth_provider_id, name=name, print_flag=print_flag,
                                          fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'create_auth_group failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def delete_auth_groups(ids, print_flag=True, fault_node_ip=None):
    """删除本地认证用户组
    :param ids: Required:True   Type:string  Help:The group ID list
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ delete_auth_groups ]")
    rc, stdout = common.delete_auth_groups(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'delete_auth_groups failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_auth_groups(auth_provider_id, start=None, limit=None, print_flag=True, fault_node_ip=None):
    """查询本地认证用户组
    :param auth_provider_id: Required:True   Type:int     Help:The ID of authentication provider
    :param start: Required:False  Type:int     Help:The start index in the query result.
    :param limit: Required:False  Type:int     Help:The record numbers to display in once query.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_auth_groups ]")
    rc, stdout = common.get_auth_groups(auth_provider_id=auth_provider_id, start=start, limit=limit,
                                        print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_auth_groups failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def create_file(path, posix_permission=None, print_flag=True, fault_node_ip=None):
    """创建目录
    :param path: Required:True   Type:string  Help:The path to be created. e.g. volume:/dir
    :param posix_permission: Required:False  Type:string  Help:POSIX file permission, e.g. rwxr-xr-x
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ create_file ]")
    rc, stdout = common.create_file(path=path, posix_permission=posix_permission, print_flag=print_flag,
                                    fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'create_file failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def delete_file(path, print_flag=True, fault_node_ip=None):
    """删除目录
    :param path: Required:True   Type:string  Help:The path to be deleted. e.g. volume:/dir
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ delete_file ]")
    rc, stdout = common.delete_file(path=path, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'delete_file failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def update_file(path, posix_permission, print_flag=True, fault_node_ip=None):
    """修改目录
    :param path: Required:True   Type:string  Help:The path to be deleted. e.g. volume:/dir
    :param posix_permission: Required:True   Type:string  Help:POSIX file permission, e.g. rwxr-xr-x
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ update_file ]")
    rc, stdout = common.update_file(path=path, posix_permission=posix_permission, print_flag=print_flag,
                                    fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'update_file failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_file_list(path, file_type=None, display_details=None, start=None, limit=None, print_flag=True,
                  fault_node_ip=None):
    """查询目录（文件系统浏览）
    :param path: Required:True   Type:string  Help:The path to be listed. e.g. volume:/dir
    :param file_type: Required:False  Type:string  Help:File type, available file type:['FILE', 'DIR']
    :param display_details: Required:False  Type:bool    Help:Display detail messages, like 'ls -l' in the Linux.
    :param start: Required:False  Type:int     Help:The start index in the result.
    :param limit: Required:False  Type:int     Help:The records size in each query.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_file_list ]")
    rc, stdout = common.get_file_list(path=path, type=file_type, display_details=display_details, start=start,
                                      limit=limit, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_file_list failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def create_smb_export(access_zone_id, export_name, export_path,
                      description=None, enable_ntfs_acl=None, allow_create_ntfs_acl=None,
                      enable_alternative_datasource=None, enable_dos_attributes=None,
                      enable_os2style_ex_attrs=None, enable_guest=None, enable_oplocks=None,
                      authorization_ip=None, print_flag=True, fault_node_ip=None):
    """创建SMB共享
    :param access_zone_id: Required:True   Type:int     Help:The access zone id where this export in.
    :param export_name: Required:True   Type:string  Help:The export name.
    :param export_path: Required:True   Type:string  Help:The export path. e.g. volume:/export/dir
    :param description: Required:False  Type:string  Help:The export description.
    :param enable_ntfs_acl: Required:False  Type:bool    Help:Enable NTFS ACL, default is false
    :param allow_create_ntfs_acl: Required:False  Type:bool    Help:Allow create NTFS ACL, t
    ake effect after setting the "enable_ntfs_acl" true
    :param enable_alternative_datasource: Required:False  Type:bool    Help:Enable alternative data source,
    Default is false.
    :param enable_dos_attributes: Required:False  Type:bool    Help:Enable DOS attributes, default is true
    :param enable_os2style_ex_attrs: Required:False  Type:bool    Help:Enable OS/2 style extended attributes,
    default is false
    :param enable_guest: Required:False  Type:bool    Help:Enable guest, default is true.
    :param enable_oplocks: Required:False  Type:bool    Help:Enable opportunistic lock, default is true
    :param authorization_ip: Required:False  Type:string  Help:Authorization IP, all hosts are allowed if not set.
    e.g. 1.1.1.1,2.2.2.2 multi IP, split by comma; or 1.1.1.1/24; or 1.1.1. EXCEPT 1.1.1.2,1.1.1.3
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ create_smb_export ]")
    rc, stdout = common.create_smb_export(access_zone_id=access_zone_id, export_name=export_name,
                                          export_path=export_path, description=description,
                                          enable_ntfs_acl=enable_ntfs_acl, allow_create_ntfs_acl=allow_create_ntfs_acl,
                                          enable_alternative_datasource=enable_alternative_datasource,
                                          enable_dos_attributes=enable_dos_attributes,
                                          enable_os2style_ex_attrs=enable_os2style_ex_attrs,
                                          enable_guest=enable_guest, enable_oplocks=enable_oplocks,
                                          authorization_ip=authorization_ip, print_flag=print_flag,
                                          fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'create_smb_export failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def delete_smb_exports(ids, print_flag=True, fault_node_ip=None):
    """删除SMB共享
    :param ids: Required:True   Type:string  Help:The smb export id list.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ delete_smb_exports ]")
    rc, stdout = common.delete_smb_exports(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'delete_smb_exports failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def update_smb_export(export_id, description=None, enable_ntfs_acl=None, allow_create_ntfs_acl=None,
                      enable_alternative_datasource=None, enable_dos_attributes=None,
                      enable_os2style_ex_attrs=None, enable_guest=None, enable_oplocks=None,
                      authorization_ip=None, print_flag=True, fault_node_ip=None):
    """修改SMB共享
    :param export_id: Required:True   Type:int     Help:The smb export id.
    :param description: Required:False  Type:string  Help:The export description.
    :param enable_ntfs_acl: Required:False  Type:bool    Help:Enable NTFS ACL, default is false
    :param allow_create_ntfs_acl: Required:False  Type:bool    Help:Allow create NTFS ACL,
    take effect after setting the "enable_ntfs_acl" true
    :param enable_alternative_datasource: Required:False  Type:bool    Help:Enable alternative data source,
    Default is false.
    :param enable_dos_attributes: Required:False  Type:bool    Help:Enable DOS attributes, default is true
    :param enable_os2style_ex_attrs: Required:False  Type:bool    Help:Enable OS/2 style extended attributes,
    default is false
    :param enable_guest: Required:False  Type:bool    Help:Enable guest, default is true.
    :param enable_oplocks: Required:False  Type:bool    Help:Enable opportunistic lock, default is true
    :param authorization_ip: Required:False  Type:string  Help:Authorization IP, e.g. 1.1.1.1,2.2.2.2 multi IP,
    split by comma; or 1.1.1.1/24; or 1.1.1. EXCEPT 1.1.1.2,1.1.1.3
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ update_smb_export ]")
    rc, stdout = common.update_smb_export(id=export_id, description=description, enable_ntfs_acl=enable_ntfs_acl,
                                          allow_create_ntfs_acl=allow_create_ntfs_acl,
                                          enable_alternative_datasource=enable_alternative_datasource,
                                          enable_dos_attributes=enable_dos_attributes,
                                          enable_os2style_ex_attrs=enable_os2style_ex_attrs,
                                          enable_guest=enable_guest, enable_oplocks=enable_oplocks,
                                          authorization_ip=authorization_ip, print_flag=print_flag,
                                          fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'update_smb_export failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_smb_exports(ids=None, print_flag=True, fault_node_ip=None):
    """查询SMB共享
    :param ids: Required:False  Type:string  Help:The id list of smb exports
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_smb_exports ]")
    rc, stdout = common.get_smb_exports(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_smb_exports failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_smb_exports_id_list():
    """获取smb exports的id列表
    :return: 导出smb的id列表，格式为：1,2,3
    """
    log.info("\t[ get_smb_exports_id_list ]")
    msg = get_smb_exports()
    exports = msg['result']['exports']
    id_list = []
    for export in exports:
        id_list.append(export['id'])
    smb_ids = ','.join(str(i) for i in id_list)

    return smb_ids


def add_smb_export_auth_clients(export_id, name, user_type, run_as_root, permission_level=None, print_flag=True,
                                fault_node_ip=None):
    """增加SMB用户/用户组
    :param export_id: Required:True   Type:int     Help:The smb export id that you want to add to
    :param name: Required:True   Type:string  Help:The authorization user/group name
    :param user_type: Required:True   Type:string  Help:The authorization client type, available types:['USER', 'GROUP']
    :param run_as_root: Required:True   Type:bool    Help:Run as root, you should set this "permission_level"
    property when run_as_root=false
    :param permission_level: Required:False  Type:string  Help:The client permission level,
    available permission level:['ro', 'rw']; ro: read only; rw: read write
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ add_smb_export_auth_clients ]")
    rc, stdout = common.add_smb_export_auth_clients(export_id=export_id, name=name, type=user_type,
                                                    run_as_root=run_as_root, permission_level=permission_level,
                                                    print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'add_smb_export_auth_clients failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def remove_smb_export_auth_clients(ids, print_flag=True, fault_node_ip=None):
    """移除SMB用户/用户组
    :param ids: Required:True   Type:string  Help:The authorization client id list.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ remove_smb_export_auth_clients ]")
    rc, stdout = common.remove_smb_export_auth_clients(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'remove_smb_export_auth_clients failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def update_smb_export_auth_client(auth_client_id, run_as_root, permission_level=None, print_flag=True,
                                  fault_node_ip=None):
    """修改SMB用户/用户组,
    :param auth_client_id: Required:True   Type:int     Help:The authorization client id.
    :param run_as_root: Required:True   Type:bool    Help:Run as root, you should set this "permission_level"
    property when run_as_root=false
    :param permission_level: Required:False  Type:string  Help:The client permission level,
    available permission level:['ro', 'rw']; ro: read only; rw: read write
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ update_smb_export_auth_client ]")
    rc, stdout = common.update_smb_export_auth_client(id=auth_client_id, run_as_root=run_as_root,
                                                      permission_level=permission_level, print_flag=print_flag,
                                                      fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'update_smb_export_auth_client failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_smb_export_auth_clients(export_ids=None, print_flag=True, fault_node_ip=None):
    """查询SMB用户/用户组列表
    :param export_ids: Required:False  Type:string  Help:The smb export id list.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_smb_export_auth_clients ]")
    rc, stdout = common.get_smb_export_auth_clients(export_ids=export_ids, print_flag=print_flag,
                                                    fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_smb_export_auth_clients failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_smb_export_auth_clients_id_list():
    """获取SMB导出用户的id列表
    :return: smb导出用户的id列表，格式为：1,2,3
    """
    log.info("\t[ get_smb_export_auth_clients_id_list ]")
    msg = get_smb_export_auth_clients()
    smb_export_auth_clients = msg['result']['smb_export_auth_clients']
    id_list = []
    for smb_export_auth_client in smb_export_auth_clients:
        id_list.append(smb_export_auth_client['id'])
    smb_export_auth_clients_ids = ','.join(str(i) for i in id_list)

    return smb_export_auth_clients_ids


def get_smb_global_configs(ids=None, print_flag=True, fault_node_ip=None):
    """查询SMB公共属性
    :param ids: Required:False  Type:string  Help:The smb global configuration id list.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_smb_global_configs ]")
    rc, stdout = common.get_smb_global_configs(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_smb_global_configs failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def update_smb_global_config(smb_global_config_id, enable_change_notify=None, enable_guest=None,
                             enable_send_ntlmv2=None, home_dir=None, enable_alternative_datasource=None,
                             enable_dos_attributes=None, enable_os2style_ex_attrs=None,
                             enable_ntfs_acl=None, allow_create_ntfs_acl=None, enable_oplocks=None, print_flag=True,
                             fault_node_ip=None):
    """配置SMB公共属性
    :param smb_global_config_id: Required:True   Type:int     Help:The smb global configuration id.
    :param enable_change_notify: Required:False  Type:bool    Help:Enable change notify.
    :param enable_guest: Required:False  Type:bool    Help:Enable guest account.
    :param enable_send_ntlmv2: Required:False  Type:bool    Help:Enable send NTLMv2.
    :param home_dir: Required:False  Type:string  Help:After enabled,
    the user can directly access its proprietary directory under specified directory. e.g. volume:/dir
    :param enable_alternative_datasource: Required:False  Type:bool    Help:Enable alternative data source,
    take effect after set "home_dir".
    :param enable_dos_attributes: Required:False  Type:bool    Help:Enable DOS attributes,
    take effect after set "home_dir".
    :param enable_os2style_ex_attrs: Required:False  Type:bool    Help:Enable OS/2 style data source,
    take effect after set "home_dir".
    :param enable_ntfs_acl: Required:False  Type:bool    Help:Enable NTFS ACL, take effect after set "home_dir".
    :param allow_create_ntfs_acl: Required:False  Type:bool    Help:Allow create NTFS ACL,
    take effect after enabled "enable_ntfs_acl".
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ update_smb_global_config ]")
    rc, stdout = common.update_smb_global_config(id=smb_global_config_id, enable_change_notify=enable_change_notify,
                                                 enable_guest=enable_guest, enable_send_ntlmv2=enable_send_ntlmv2,
                                                 home_dir=home_dir,
                                                 enable_alternative_datasource=enable_alternative_datasource,
                                                 enable_dos_attributes=enable_dos_attributes,
                                                 enable_ntfs_acl=enable_ntfs_acl,
                                                 enable_os2style_ex_attrs=enable_os2style_ex_attrs,
                                                 allow_create_ntfs_acl=allow_create_ntfs_acl,
                                                 enable_oplocks=enable_oplocks, print_flag=print_flag,
                                                 fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'update_smb_global_config failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def create_nfs_export(access_zone_id, export_name, export_path, description=None, print_flag=True, fault_node_ip=None):
    """创建NFS共享
    :param access_zone_id: Required:True   Type:int     Help:The access zone id where this export in.
    :param export_name: Required:True   Type:string  Help:The export name.
    :param export_path: Required:True   Type:string  Help:The export path. e.g. volume:/export/dir
    :param description: Required:False  Type:string  Help:The export description.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ create_nfs_export ]")
    rc, stdout = common.create_nfs_export(access_zone_id=access_zone_id, export_name=export_name,
                                          export_path=export_path, description=description, print_flag=print_flag,
                                          fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'create_nfs_export failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def delete_nfs_exports(ids, print_flag=True, fault_node_ip=None):
    """删除NFS共享
    :param ids:  Required:True   Type:string  Help:The nfs export id list.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ delete_nfs_exports ]")
    rc, stdout = common.delete_nfs_exports(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'delete_nfs_exports failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def update_nfs_export(export_id, description=None, print_flag=True, fault_node_ip=None):
    """修改NFS共享
    :param export_id: Required:True   Type:int     Help:The nfs export id.
    :param description: Required:False  Type:string  Help:The export description.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ update_nfs_export ]")
    rc, stdout = common.update_nfs_export(id=export_id, description=description, print_flag=print_flag,
                                          fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'update_nfs_export failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_nfs_exports(ids=None, print_flag=True, fault_node_ip=None):
    """查询NFS共享
    :param ids: Required:False  Type:string  Help:The id list of nfs exports
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_nfs_exports ]")
    rc, stdout = common.get_nfs_exports(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_nfs_exports failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_nfs_exports_id_list():
    """获取nfs exports的id列表
    :return: nfs导出的id列表，格式为：1,2,3
    """
    log.info("\t[ get_nfs_exports_id_list ]")
    msg = get_nfs_exports()
    exports = msg['result']['exports']
    id_list = []
    for export in exports:
        id_list.append(export['id'])
    nfs_ids = ','.join(str(i) for i in id_list)

    return nfs_ids


def add_nfs_export_auth_clients(export_id, name, permission_level, write_mode=None, port_constraint=None,
                                permission_constraint=None, anonuid=None, anongid=None, print_flag=True,
                                fault_node_ip=None):
    """增加NFS客户端
    :param export_id: Required:True   Type:int     Help:The nfs export id that you want to add to
    :param name: Required:True   Type:string  Help:The nfs export authorization client IP address,
    support */single IP/ sub-network; e.g. 192.168.1.0/24
    :param permission_level: Required:True   Type:string  Help:The nfs export authorization client permission level,
    available permission level:['ro', 'rw']
    :param write_mode: Required:False  Type:string  Help:The nfs export authorization client write model,
    available write model:['sync', 'async'], default is "async"
    :param port_constraint: Required:False  Type:string  Help:The nfs export port constraint,
    available port constraint:['secure', 'insecure'], default is "insecure"
    :param permission_constraint: Required:False  Type:string  Help:The nfs export permission constraint,
    available permission constraint:['all_squash', 'root_squash', 'no_root_squash'], default is "root_squash"
    :param anonuid: Required:False  Type:int     Help:Set the uid of the anonymous account.
    :param anongid: Required:False  Type:int     Help:Set the gid of the anonymous account.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ add_nfs_export_auth_clients ]")
    rc, stdout = common.add_nfs_export_auth_clients(export_id=export_id, name=name, permission_level=permission_level,
                                                    write_mode=write_mode, port_constraint=port_constraint,
                                                    permission_constraint=permission_constraint, anonuid=anonuid,
                                                    anongid=anongid, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'add_nfs_export_auth_clients failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def remove_nfs_export_auth_clients(ids, print_flag=True, fault_node_ip=None):
    """移除NFS客户端
    :param ids: Required:True   Type:string  Help:The authorization client id list.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ remove_nfs_export_auth_clients ]")
    rc, stdout = common.remove_nfs_export_auth_clients(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'remove_nfs_export_auth_clients failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def update_nfs_export_auth_client(auth_client_id, permission_level=None, write_mode=None, port_constraint=None,
                                  permission_constraint=None, anonuid=None, anongid=None, print_flag=True,
                                  fault_node_ip=None):
    """修改NFS客户端
    :param auth_client_id: Required:True   Type:int     Help:The authorization client id.
    :param permission_level: Required:False  Type:string  Help:The nfs export authorization client permission level,
    available permission level:['ro', 'rw']
    :param write_mode: Required:False  Type:string  Help:The nfs export authorization client write model,
    available write model:['sync', 'async'], default is "async"
    :param port_constraint:  Required:False  Type:string  Help:The nfs export port constraint,
    available port constraint:['secure', 'insecure'], default is "insecure"
    :param permission_constraint: Required:False  Type:string  Help:The nfs export permission constraint,
    available permission constraint:['all_squash', 'root_squash', 'no_root_squash'], default is "root_squash"
    :param anonuid: Required:False  Type:int     Help:Set the uid of the anonymous account.
    :param anongid: Required:False  Type:int     Help:Set the gid of the anonymous account.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ update_nfs_export_auth_client ]")
    rc, stdout = common.update_nfs_export_auth_client(id=auth_client_id, permission_level=permission_level,
                                                      write_mode=write_mode, port_constraint=port_constraint,
                                                      permission_constraint=permission_constraint, anonuid=anonuid,
                                                      anongid=anongid, print_flag=print_flag,
                                                      fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'update_nfs_export_auth_client failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_nfs_export_auth_clients(export_ids=None, print_flag=True, fault_node_ip=None):
    """查询NFS客户端列表
    :param export_ids: Required:False  Type:string  Help:The nfs export id list.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_nfs_export_auth_clients ]")
    rc, stdout = common.get_nfs_export_auth_clients(export_ids=export_ids, print_flag=print_flag,
                                                    fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_nfs_export_auth_clients failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_nfs_export_auth_clients_id_list():
    """获取NFS导出用户的id列表
    :return: nfs导出的用户的id列表，格式为：1,2,3
    """
    log.info("\t[ get_nfs_export_auth_clients_id_list ]")
    msg = get_nfs_export_auth_clients()
    nfs_export_auth_clients = msg['result']['nfs_export_auth_clients']
    id_list = []
    for nfs_export_auth_client in nfs_export_auth_clients:
        id_list.append(nfs_export_auth_client['id'])
    nfs_export_auth_clients_ids = ','.join(str(i) for i in id_list)

    return nfs_export_auth_clients_ids


def create_ftp_export(access_zone_id, user_name, export_path, enable_dirlist=None, enable_create_folder=None,
                      enable_delete_and_rename=None, enable_upload=None, upload_local_max_rate=None,
                      enable_download=None, download_local_max_rate=None, print_flag=True, fault_node_ip=None):
    """
    创建FTP导出
    :param access_zone_id:        Required:True   Type:int     Help:The access zone id where this export in.
    :param user_name:             Required:True   Type:string  Help:The user name.
    :param export_path:           Required:True   Type:string  Help:The export path, e.g. volume:/export/dir.
    :param enable_dirlist:        Required:False  Type:bool    Help:View file list, default value is true.
    :param enable_create_folder:  Required:False  Type:bool    Help:Create folder, default value is false.
    :param enable_delete_and_rename: Required:False  Type:bool    Help:Delete file and rename, default value is false.
    :param enable_upload:         Required:False  Type:bool    Help:Upload file, default value is false. After this
    item is true, the maximum upload speed (bandwidth) needs to be set for users.
    :param upload_local_max_rate: Required:False  Type:int     Help:The upload speed (bandwidth) ranges from 0 to
    1000 (unit: MB/s); default is 0, no limit.
    :param enable_download:       Required:False  Type:bool    Help:Download file, default value is true.
    After this item is true, the maximum download speed (bandwidth) needs to be set for users.
    :param download_local_max_rate: Required:False  Type:int     Help:The download speed (bandwidth) ranges from
    0 to 1000 (unit: MB/s); default is 0, no limit.
    :param node_ip: 执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ create_ftp_export ]")
    rc, stdout = common.create_ftp_export(access_zone_id=access_zone_id, user_name=user_name, export_path=export_path,
                                          enable_dirlist=enable_dirlist, enable_create_folder=enable_create_folder,
                                          enable_delete_and_rename=enable_delete_and_rename, enable_upload=enable_upload,
                                          upload_local_max_rate=upload_local_max_rate, enable_download=enable_download,
                                          download_local_max_rate=download_local_max_rate, print_flag=print_flag,
                                          fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'create_ftp_export failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def delete_ftp_exports(ids, print_flag=True, fault_node_ip=None):
    """删除FTP共享
    :param ids: Required:True   Type:string  Help:The ftp export id list.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ delete_ftp_exports ]")
    rc, stdout = common.delete_ftp_exports(ids=ids, print_flag=print_flag)
    common.judge_rc(rc, 0, 'delete_ftp_exports failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def update_ftp_export(export_id, export_path=None, enable_dirlist=None,
                      enable_create_folder=None, enable_delete_and_rename=None, enable_upload=None,
                      upload_local_max_rate=None, enable_download=None, download_local_max_rate=None,
                      print_flag=True, fault_node_ip=None):
    """
    修改FTP导出
    :param export_id:            Required:True   Type:int     Help:The ftp export id.
    :param access_zone_id:       Required:True   Type:int     Help:The access zone id where this export in.
    :param user_name:            Required:True   Type:string  Help:The user name.
    :param export_path:          Required:False  Type:string  Help:The export path, e.g. volume:/export/dir.
    :param enable_dirlist:       Required:False  Type:bool    Help:View file list, default value is true.
    :param enable_create_folder: Required:False  Type:bool    Help:Create folder, default value is false.
    :param enable_delete_and_rename: Required:False  Type:bool    Help:Delete file and rename, default value is false.
    :param enable_upload:        Required:False  Type:bool    Help:Upload file, default value is false. After this
    item is true, the maximum upload speed (bandwidth) needs to be set for users.
    :param upload_local_max_rate: Required:False  Type:int     Help:The upload speed (bandwidth) ranges from 0 to
    1000 (unit: MB/s); default is 0, no limit.
    :param enable_download:      Required:False  Type:bool    Help:Download file, default value is true. After this
    item is true, the maximum download speed (bandwidth) needs to be set for users.
    :param download_local_max_rate: Required:False  Type:int     Help:The download speed (bandwidth) ranges from 0
    to 1000 (unit: MB/s); default is 0, no limit.
    :param node_ip: 执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ update_ftp_export ]")
    rc, stdout = common.update_ftp_export(id=export_id, export_path=export_path, enable_dirlist=enable_dirlist,
                                          enable_create_folder=enable_create_folder,
                                          enable_delete_and_rename=enable_delete_and_rename, enable_upload=enable_upload,
                                          upload_local_max_rate=upload_local_max_rate, enable_download=enable_download,
                                          download_local_max_rate=download_local_max_rate, print_flag=print_flag,
                                          fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'update_ftp_export failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_ftp_exports(ids=None, print_flag=True, fault_node_ip=None):
    """查询FTP共享
    :param ids: Required:False  Type:string  Help:The id list of ftp exports
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_ftp_exports ]")
    rc, stdout = common.get_ftp_exports(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_ftp_exports failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_ftp_exports_id_list():
    """获取ftp exports的id列表
    :return: ftp导出的id列表，格式为：1,2,3
    """
    log.info("\t[ get_ftp_exports_id_list ]")
    msg = get_ftp_exports()
    exports = msg['result']['exports']
    id_list = []
    for export in exports:
        id_list.append(export['id'])
    ftp_ids = ','.join(str(i) for i in id_list)

    return ftp_ids


def update_param(section, name, current, print_flag=True, fault_node_ip=None):
    """（通过修改参数进行）数据访问控制
    :param section: Required:True   Type:string  Help:The section of this parameter,
    e.g. NAL,MGR,oPara,oStor,oApp,oCnas,CUSTOM
    :param name: Required:True   Type:string  Help:The name of this parameter
    :param current: Required:True   Type:string  Help:Current value of this parameter
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ update_param ]")
    rc, stdout = common.update_param(section=section, name=name, current=current, print_flag=print_flag,
                                     fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'update_param failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def delete_nas_protocol_param(protocol_type, access_zone_id, param_key, print_flag=True, fault_node_ip=None):
    """删除协议配置参数
    :param protocol_type: Required:True   Type:string  Help:Available protocol type:['NFS', 'SMB', 'FTP'],
    select one from them.
    :param access_zone_id: Required:True   Type:int     Help:Access zone id
    :param param_key: Required:True   Type:string  Help:The parameter key that to be update
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ delete_nas_protocol_param ]")
    rc, stdout = common.delete_nas_protocol_param(protocol_type=protocol_type, access_zone_id=access_zone_id,
                                                  param_key=param_key, print_flag=print_flag,
                                                  fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'delete_nas_protocol_param failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def update_nas_protocol_param(protocol_type, access_zone_id, param_key, param_value, force=None, print_flag=True,
                              fault_node_ip=None):
    """更新协议配置参数
    :param protocol_type: Required:True   Type:string  Help:Available protocol type:['NFS', 'SMB', 'FTP'],
    select one from them.
    :param access_zone_id: Required:True   Type:int     Help:Access zone id
    :param param_key: Required:True   Type:string  Help:The parameter key that to be update
    :param param_value: Required:True   Type:string  Help:The parameter value that to be update
    :param force: Required:False  Type:bool    Help:If the updated parameter key does not exist,
    and you want to add it, set the "force=true"
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ update_nas_protocol_param ]")
    rc, stdout = common.update_nas_protocol_param(protocol_type=protocol_type, access_zone_id=access_zone_id,
                                                  param_key=param_key, param_value=param_value, force=force,
                                                  print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'update_nas_protocol_param failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_nas_protocol_params(protocol_type, access_zone_id=None, print_flag=True, fault_node_ip=None):
    """查询协议配置参数
    :param protocol_type: Required:True   Type:string  Help:Available protocol type:['NFS', 'SMB', 'FTP'],
    select one from them.
    :param access_zone_id: Required:False  Type:int     Help:Access zone id
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_nas_protocol_params ]")
    rc, stdout = common.get_nas_protocol_params(protocol_type=protocol_type, access_zone_id=access_zone_id,
                                                print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_nas_protocol_params failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_auth_providers_summary(ids=None, print_flag=True, fault_node_ip=None):
    """查询认证服务器概览
    :param ids: Required:False  Type:string  Help:The authentication provider id list to get, e.g. 1,2,3
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_auth_providers_summary ]")
    rc, stdout = common.get_auth_providers_summary(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_auth_providers_summary failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_auth_providers_id_list():
    """查询认证服务器id列表
    :return: 认证服务器id列表，格式为：1,2,3
    """
    log.info("\t[ get_auth_providers_id_list ]")

    msg = get_auth_providers_summary()
    if msg["detail_err_msg"] != "":
        log.error("%s Failed" % get_auth_providers_summary)
        return None
    else:
        auth_providers = msg["result"]["auth_providers"]
        id_list = []
        for auth_provider in auth_providers:
            id_list.append(auth_provider['id'])

        auth_provider_ids = ','.join(str(i) for i in id_list)
        return auth_provider_ids


def delete_auth_providers(ids, print_flag=True, fault_node_ip=None):
    """删除认证服务器
    :param ids: Required:True   Type:string  Help:The authentication provider ids. e.g. 1,2,3,4
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ delete_auth_providers ]")
    rc, stdout = common.delete_auth_providers(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'delete_auth_providers failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def add_auth_provider_ad(name, domain_name, dns_addresses, username, password, services_for_unix, unix_id_range=None,
                         other_unix_id_range=None, check=None, print_flag=True, fault_node_ip=None):
    """添加AD认证服务器
    :param name: Required:True   Type:string  Help:The name of authentication provider.
    :param domain_name: Required:True   Type:string  Help:The domain name of AD provider.
    :param dns_addresses: Required:True   Type:string  Help:IP addresses of DNS that to resolve the domain name.
    :param username: Required:True   Type:string  Help:The administrator username in this AD domain
    :param password: Required:True   Type:string  Help:The administrator password in this AD domain
    :param services_for_unix: Required:True   Type:string  Help:Services of UNIX type.
    Available services for UNIX type:['NONE', 'RFC2307']
    :param unix_id_range: Required:False  Type:string  Help:When set services_for_unix "NONE", you need set it.
    Minimum value 1000, e.g. 5000-6000
    :param other_unix_id_range: Required:False  Type:string  Help:When set services_for_unix "RFC2307",
    you need set it.Minimum value 1000, e.g. 6001-7000
    :param check: Required:False  Type:bool    Help:Check the authentication provider's connection availability.
    Default is false, no check. If set check true, wont persistent the parameters.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ add_auth_provider_ad ]")
    """设置集群节点与AD鉴权服务器时间同步"""
    set_ntp(is_enabled='true', ntp_servers=AD_DNS_ADDRESSES, sync_period=5)
    rc, stdout = common.add_auth_provider_ad(name=name, domain_name=domain_name, dns_addresses=dns_addresses,
                                             username=username, password=password, services_for_unix=services_for_unix,
                                             unix_id_range=unix_id_range, other_unix_id_range=other_unix_id_range,
                                             check=check, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'add_auth_provider_ad failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def update_auth_provider_ad(provider_id, name=None, domain_name=None, dns_addresses=None, username=None, password=None,
                            check=None, print_flag=True, fault_node_ip=None):
    """修改AD认证服务器
    :param provider_id: Required:True   Type:int     Help:The ID of authentication provider.
    :param name: Required:False  Type:string  Help:The name of authentication provider.
    :param domain_name: Required:False  Type:string  Help:The domain name of AD provider.
    :param dns_addresses: Required:False  Type:string  Help:IP addresses of DNS that to resolve the domain name.
    :param username: Required:False  Type:string  Help:The administrator username in this AD domain
    :param password: Required:False  Type:string  Help:The administrator password in this AD domain
    :param check: Required:False  Type:bool    Help:Check the authentication provider's connection availability.
    Default is false, no check. If set check true, wont persistent the parameters.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ update_auth_provider_ad ]")
    rc, stdout = common.update_auth_provider_ad(id=provider_id, name=name, domain_name=domain_name,
                                                dns_addresses=dns_addresses, username=username, password=password,
                                                check=check, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'update_auth_provider_ad failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_auth_providers_ad(ids=None, print_flag=True, fault_node_ip=None):
    """查询AD认证服务器
    :param ids: Required:False  Type:string  Help:The authentication provider id list to get, e.g. 1,2,3
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_auth_providers_ad ]")
    rc, stdout = common.get_auth_providers_ad(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_auth_providers_ad failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def add_auth_provider_ldap(name, base_dn, ip_addresses, port=None, bind_dn=None, bind_password=None,
                           domain_password=None, user_search_path=None, group_search_path=None, check=None,
                           print_flag=True, fault_node_ip=None):
    """添加LDAP认证服务器
    :param name: Required:True   Type:string  Help:The name of authentication provider.
    :param base_dn: Required:True   Type:string  Help:The base DN of LDAP provider. e.g. dc=abc,dc=com
    :param ip_addresses: Required:True   Type:string  Help:IP addresses of LDAP provider.
    :param port: Required:False  Type:int     Help:Port used by the system to communicate with the LDAP provider.
    Default is 389, a valid port range from 1 to 65535.
    :param bind_dn: Required:False  Type:string  Help:The DN used by the system to login to the LDAP provider.
    e.g. cn=root, dc=abc,dc=com
    :param bind_password: Required:False  Type:string  Help:Password by the system to login to the LDAP provider.
    :param user_search_path: Required:False  Type:string  Help:User DN configured by the LDAP provider.
    e.g. ou=user,dc=abc,dc=com
    :param group_search_path: Required:False  Type:string  Help:User group DN configured by the LDAP provider.
    e.g. ou=group,dc=abc,dc=com
    :param check: Required:False  Type:bool    Help:Check the authentication provider's connection availability.
    Default is false, no check. If set check true, wont persistent the parameters.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ add_auth_provider_ldap ]")
    rc, stdout = common.add_auth_provider_ldap(name=name, base_dn=base_dn, ip_addresses=ip_addresses, port=port,
                                               bind_dn=bind_dn, bind_password=bind_password,
                                               domain_password=domain_password, user_search_path=user_search_path,
                                               group_search_path=group_search_path, check=check, print_flag=print_flag,
                                               fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'add_auth_provider_ldap failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def update_auth_provider_ldap(provider_id, name=None, base_dn=None, ip_addresses=None, port=None,
                              bind_dn=None, bind_password=None, domain_password=None, user_search_path=None,
                              group_search_path=None, check=None, print_flag=True, fault_node_ip=None):
    """修改LDAP认证服务器
    :param provider_id: Required:True   Type:int     Help:The ID of authentication provider.
    :param name: Required:False  Type:string  Help:The name of authentication provider.
    :param base_dn: Required:False  Type:string  Help:The base DN of LDAP provider. e.g. dc=abc,dc=com
    :param ip_addresses: Required:False  Type:string  Help:IP addresses of LDAP provider.
    :param port: Required:False  Type:int     Help:Port used by the system to communicate with the LDAP provider.
    Default is 389, a valid port range from 1 to 65535.
    :param bind_dn: Required:False  Type:string  Help:The DN used by the system to login to the LDAP provider.
    e.g. cn=root, dc=abc,dc=com
    :param bind_password: Required:False  Type:string  Help:Password by the system to login to the LDAP provider.
    :param domain_password: Required:False  Type:string  Help:Password to join samba domain for LDAP-PDC mode.
    :param user_search_path: Required:False  Type:string  Help:User DN configured by the LDAP provider.
    e.g. ou=user,dc=abc,dc=com
    :param group_search_path: Required:False  Type:string  Help:User group DN configured by the LDAP provider.
    e.g. ou=group,dc=abc,dc=com
    :param check: Required:False  Type:bool    Help:Check the authentication provider's connection availability.
    Default is false, no check. If set check true, wont persistent the parameters.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ update_auth_provider_ldap ]")
    rc, stdout = common.update_auth_provider_ldap(id=provider_id, name=name, base_dn=base_dn, ip_addresses=ip_addresses,
                                                  port=port, bind_dn=bind_dn, bind_password=bind_password,
                                                  domain_password=domain_password, user_search_path=user_search_path,
                                                  group_search_path=group_search_path, check=check,
                                                  print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'update_auth_provider_ldap failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_auth_providers_ldap(ids=None, print_flag=True, fault_node_ip=None):
    """查询LDAP认证服务器
    :param ids: Required:False  Type:string  Help:The authentication provider id list to get, e.g. 1,2,3
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_auth_providers_ldap ]")
    rc, stdout = common.get_auth_providers_ldap(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_auth_providers_ldap failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def add_auth_provider_nis(name, domain_name, ip_addresses, check=None, print_flag=True, fault_node_ip=None):
    """添加NIS认证服务器
    :param name: Required:True   Type:string  Help:The name of authentication provider.
    :param domain_name: Required:True   Type:string  Help:The domain name of NIS provider.
    :param ip_addresses: Required:True   Type:string  Help:IP addresses of NIS provider.
    :param check: Required:False  Type:bool    Help:Check the authentication provider's connection availability.
    Default is false, no check. If set check true, wont persistent the parameters.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ add_auth_provider_nis ]")
    rc, stdout = common.add_auth_provider_nis(name=name, domain_name=domain_name, ip_addresses=ip_addresses, check=check,
                                              print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'add_auth_provider_nis failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def update_auth_provider_nis(provider_id, name=None, domain_name=None, ip_addresses=None, check=None, print_flag=True,
                             fault_node_ip=None):
    """修改NIS认证服务器
    :param provider_id: Required:True   Type:int     Help:The ID of authentication provider.
    :param name: Required:False  Type:string  Help:The name of authentication provider.
    :param domain_name: Required:False  Type:string  Help:The domain name of NIS provider.
    :param ip_addresses: Required:False  Type:string  Help:IP addresses of NIS provider.
    :param check: Required:False  Type:bool    Help:Check the authentication provider's connection availability.
    Default is false, no check. If set check true, wont persistent the parameters.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ update_auth_provider_nis ]")
    rc, stdout = common.update_auth_provider_nis(id=provider_id, name=name, domain_name=domain_name,
                                                 ip_addresses=ip_addresses, check=check, print_flag=print_flag,
                                                 fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'update_auth_provider_nis failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_auth_providers_nis(ids=None, print_flag=True, fault_node_ip=None):
    """查询NIS认证服务器
    :param ids: Required:False  Type:string  Help:The authentication provider id list to get, e.g. 1,2,3
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_auth_providers_nis ]")
    rc, stdout = common.get_auth_providers_nis(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_auth_providers_nis failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def get_auth_providers_local(ids=None, print_flag=True, fault_node_ip=None):
    """查询本地认证服务器
    :param ids: Required:False  Type:string  Help:The authentication provider id list to get, e.g. 1,2,3
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_auth_providers_local ]")
    rc, stdout = common.get_auth_providers_local(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'get_auth_providers_local failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def check_auth_provider(provider_id, print_flag=True, fault_node_ip=None):
    """查询已有认证服务器是否可用
    :param provider_id: Required:True   Type:int     Help:The ID of authentication provider.
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ check_auth_provider ]")
    rc, stdout = common.check_auth_provider(id=provider_id, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'check_auth_provider failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def delete_all_nas_config():
    """删除所有NAS配置
    :return: 无
    :change:
    ======================================================
    2018-08-06:
    change:zhangchengyu
    description:增加删除VIP池、关闭NAS服务、删除子网、删除访问分区的内容
    ===================================================
    2018-08-08:
    change:jiangxiaoguang
    description:增加去挂载部分代码
    ======================================================
    2018-11-22:
    change:zhangchengyu
    description:增加关闭S3服务（否则无法删除访问区）
    ======================================================
    """
    log.info("\t[ delete_all_nas_config ]")

    # # 去挂载
    # disk_symbol_list = get_smb_mount_disk_symbol_info()
    # for disk_symbol in disk_symbol_list:
    #     if disk_symbol != 'Z:':
    #         smb_umount(disk_symbol)

    # 删除导出用户
    smb_export_auth_clients_ids = get_smb_export_auth_clients_id_list()
    if smb_export_auth_clients_ids != "":
        check_result = remove_smb_export_auth_clients(smb_export_auth_clients_ids)
        if check_result["detail_err_msg"] != "":
            log.error("remove_smb_export_auth_clients Failed")
            raise Exception("remove_smb_export_auth_clients Failed")
    else:
        log.info("smb_export_auth_clients_ids is Empty.")

    nfs_export_auth_clients_ids = get_nfs_export_auth_clients_id_list()
    if nfs_export_auth_clients_ids != "":
        check_result = remove_nfs_export_auth_clients(nfs_export_auth_clients_ids)
        if check_result["detail_err_msg"] != "":
            log.error("remove_nfs_export_auth_clients Failed")
            raise Exception("remove_nfs_export_auth_clients Failed")
    else:
        log.info("nfs_export_auth_clients_ids is Empty.")

    # 删除导出策略
    smb_ids = get_smb_exports_id_list()
    if smb_ids != "":
        check_result = delete_smb_exports(smb_ids)
        if check_result["detail_err_msg"] != "":
            log.error("delete_smb_exports Failed")
            raise Exception("delete_smb_exports Failed")
    else:
        log.info("smb_ids is Empty.")

    nfs_ids = get_nfs_exports_id_list()
    if nfs_ids != "":
        check_result = delete_nfs_exports(nfs_ids)
        if check_result["detail_err_msg"] != "":
            log.error("delete_nfs_exports Failed")
            raise Exception("delete_nfs_exports Failed")
    else:
        log.info("nfs_ids is Empty.")

    ftp_ids = get_ftp_exports_id_list()
    if ftp_ids != "":
        check_result = delete_ftp_exports(ftp_ids)
        if check_result["detail_err_msg"] != "":
            log.error("delete_ftp_exports Failed")
            raise Exception("delete_ftp_exports Failed")
    else:
        log.info("ftp_ids is Empty.")

    # 删除vip地址池
    msg = get_vip_address_pools()
    ip_address_pools = msg['result']['ip_address_pools']
    if ip_address_pools != "":
        for ip_address_pool in ip_address_pools:
            check_result = delete_vip_address_pool(ip_address_pool['id'])
            if check_result["detail_err_msg"] != "":
                log.error("delete_vip_address_pool Failed")
                raise Exception("delete_vip_address_pool Failed")
    else:
        log.info("vip_address_pool_id is Empty.")

    # 删除子网
    msg = get_subnets()
    subnets = msg['result']['subnets']
    if subnets != "":
        for subnet in subnets:
            check_result = delete_subnet(subnet['id'])
            if check_result["detail_err_msg"] != "":
                log.error("delete_subnet Failed")
                raise Exception("delete_subnet Failed")
    else:
        log.info("subnet_id is Empty.")

    # 关闭NAS服务（否则无法删除访问区）
    msg = get_access_zones()
    access_zones = msg['result']['access_zones']
    if access_zones != "":
        for access_zone in access_zones:
            nas_service_enabled = access_zone["nas_service_enabled"]
            if nas_service_enabled is True:
                access_zone_id = access_zone["id"]
                check_result = disable_nas(access_zone_id)
                if check_result["detail_err_msg"] != "":
                    log.error("disable_nas Failed")
                    raise Exception("disable_nas Failed")

    # 关闭S3服务（否则无法删除访问区）
    msg = get_access_zones()
    access_zones = msg['result']['access_zones']
    if access_zones != "":
        for access_zone in access_zones:
            s3_service_enabled = access_zone["enable_s3"]
            if s3_service_enabled is True:
                access_zone_id = access_zone["id"]
                rc, stdout = common.disable_s3(access_zone_id=access_zone_id, print_flag=True)
                check_result = common.json_loads(stdout)
                if check_result["detail_err_msg"] != "":
                    log.error("disable_s3 Failed")
                    raise Exception("disable_s3 Failed")

    # 删除访问区
    msg = get_access_zones()
    access_zones = msg['result']['access_zones']
    for access_zone in access_zones:
        print access_zone['id']
        check_result = delete_access_zone(access_zone['id'])
        if check_result["detail_err_msg"] != "":
            log.error("delete_access_zone Failed")
            raise Exception("delete_access_zone Failed")
    else:
        log.info("access_zone_id is Empty.")

    # 删除鉴权服务器
    auth_provider_ids = get_auth_providers_id_list()
    if auth_provider_ids != "":
        check_result = delete_auth_providers(auth_provider_ids)
        if check_result["detail_err_msg"] != "":
            log.error("delete_auth_providers Failed")
            raise Exception("delete_auth_providers Failed")
    else:
        log.info("auth_provider_ids is Empty.")

    return


def delete_all_files_and_dir(node_ip=RANDOM_NODE_IP):
    """删除所有文件及目录
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 无
    """
    log.info("\t[ delete_all_files_and_dir ]")

    # 清空目录
    rc, stdout = common.rm_exe(node_ip, os.path.join(get_config.get_one_nas_test_path(), '*'))
    # rc, stdout = common.rm_exe(node_ip, os.path.join(BASE_NAS_PATH, '*'))
    common.judge_rc(rc, 0, 'delete_all_files_and_dir', exit_flag=False)

    return


def get_node_ids():
    """获取集群全部节点的id，id间以逗号连接
    :Author: jiangxiaoguang
    :Date: 2018-08-21
    :return: node_ids: 返回全部节点的id，格式为1,2,3
    """
    obj_node = common.Node()
    node_id_list = obj_node.get_nodes_id()
    node_ids = ','.join(str(i) for i in node_id_list)
    return node_ids


def get_nodes(ids=None):
    """获得节点信息
    :param ids:       Required:False  Type:string  Help:The node id list, e.g. 1,2,3,4
    :param node_ip:   Required:False  执行cmd命令的节点ip
    :return:          执行cmd命令的字典格式返回值
    """
    log.info("\t[ get_nodes ]")
    rc, stdout = common.get_nodes(ids=ids)
    if rc != 0:
        log.error("rc = %s" % rc)
        log.error("Execute command: \"%s\" failed. \nstdout: %s" % ("get_nodes", stdout))
    msg = common.json_loads(stdout)

    return msg


def get_node_name_list(node_id_list):
    """get_nodes中取出和node_id_list对应的node_name_list
    :param node_id_list: node id列表
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: node_name_list，node_name列表，格式为：["node1", "node2", "node3"]
    """
    log.info("\t[ get_node_name ]")
    rc, stdout = common.get_nodes()
    stdout = json.loads(stdout)
    nodes = stdout['result']['nodes']
    node_name_list = []
    for node in nodes:
        if node["node_id"] in node_id_list:
            node_name_list.append(node["node_name"])

    return node_name_list


def set_ntp(is_enabled=None, ntp_servers=None, sync_period=None, print_flag=True, fault_node_ip=None):
    """设置ntp
    :Author: jiangxiaoguang
    :Date: 2018-08-06
    :param is_enabled:    Required:True   Type:bool    Help:ntp server is enables or not, e.g. true
    :param ntp_servers:   Required:True   Type:string  Help:ntp server list, e.g. 10.0.0.1,10.0.0.2
    :param sync_period:   Required:False  Type:int     Help:ntp server sync period(minute), e.g. 5; we will not change
                                                             sync_period when no sync_period is not given
    :param node_ip: Required:False  执行cmd命令的节点ip
    :return: 执行cmd命令的字典格式返回值
    """
    log.info("\t[ set_ntp ]")
    rc, stdout = common.set_ntp(is_enabled=is_enabled, ntp_servers=ntp_servers, sync_period=sync_period,
                                print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'set_ntp failed', exit_flag=False)
    msg = common.json_loads(stdout)

    return msg


def judge_vip_layinfo(ip_dict, xml_ip_list, eth_ip_list):
    """判断vip分布到各网卡是否正确
    :Author: jiangxiaoguang
    :Date: 2018-08-17
    :param ip_dict: 网卡上查到的vip分布信息的字典形式
    :param xml_ip_list: xml文件中获取的vip信息
    :param eth_ip_list: 网卡上查到的vip信息的列表形式
    :return: 0代表vip分布正确，-1代表vip分布异常
    """
    log.info("\t[ judge_vip_layinfo ]")
    log.info("eth_ip_lst:")
    log.info(eth_ip_list)
    log.info("xml_ip_list:")
    log.info(xml_ip_list)
    count_list = []
    if ip_dict or eth_ip_list:
        """判断从xml获取的vip个数是否等于从网卡获取的vip个数"""
        if len(xml_ip_list) != len(eth_ip_list):
            log.error('len(xml_ip_list) = %s' % len(xml_ip_list))
            log.error('len(eth_ip_list) = %s' % len(eth_ip_list))
            return -1

        """判断从xml获取的vip是否都落到了网卡上"""
        for ip in xml_ip_list:
            if ip not in eth_ip_list:
                log.error('%s is not in eth_ip_list: %s' % ip, eth_ip_list)
                return -1

        """判断落到各网卡上的vip是否均衡"""
        for value in ip_dict.values():
            count_list.append(len(value))
        if max(count_list) - min(count_list) != 0 and max(count_list) - min(count_list) != 1:
            log.error('layout is wrong.')
            return -1
        else:
            return 0
    else:
        log.error("ip_dict or eth_ip_list is Empty.")
        return -1


def get_vip_from_eth(subnet_network_interfaces=SUBNET_NETWORK_INTERFACES,
                     vip_addresses=VIP_ADDRESSES,
                     subnet_mask=SUBNET_MASK):
    """获取网卡vip分布信息的字典形式
    :Author: jiangxiaoguang
    :Date: 2018-08-17
    :param subnet_network_interfaces: 从xml获取的网卡信息
    :param vip_addresses: 从xml获取的vip地址信息
    :param subnet_mask: 从xml获取的掩码信息
    :return: ip_dict: 网卡上查到的vip分布信息的字典形式
             xml_ip_list: xml文件中获取的vip信息
             eth_ip_list: 网卡上查到的vip信息的列表形式
    ####################################################
    :changelog:
    date: 2018-12-13
    author:zhangchengyu
    description: 修改nodes_ips的获取方式，原始为从get_config.get_allparastor_ips()中获取，
    现在改为从common.Node()中获取集群id，再根据node.get_node_ip_by_id(node_id)获取ip
    ####################################################
    """
    log.info("\t[ get_vip_from_eth ]")

    ip_dict = {}
    xml_ip_list = []
    eth_ip_list = []
    nodes_ips = []
    node = common.Node()
    node_ids = node.get_nodes_id()
    for node_id in node_ids:
        node_ip_i = node.get_node_ip_by_id(node_id)
        nodes_ips.append(node_ip_i)
    # nodes_ips = get_config.get_allparastor_ips()
    eths = subnet_network_interfaces.split(',')
    if '-' not in vip_addresses:
        vips = vip_addresses + '/' + subnet_mask
        xml_ip_list = [vips]
    else:
        vips = vip_addresses.split('.')
        for i in range(int(vips[3].split('-')[0]), int(vips[3].split('-')[1])+1):
            xml_ip_list.append(vips[0] + '.' + vips[1] + '.' + vips[2] + '.' + str(i) + '/' + subnet_mask)

    for node_ip in nodes_ips:
        for eth in eths:
            cmd = 'ip addr | grep %s | grep inet' % eth
            rc, stdout = common.run_command(node_ip, cmd, print_flag=False)
            # common.judge_rc(rc, 0, 'ip addr failed')
            tmp_list = []
            for line in stdout.split('\n'):
                if line:
                    if line.split()[1] in xml_ip_list:
                        tmp_list.append(line.split()[1])
                        eth_ip_list.append(line.split()[1])
            dict_key = node_ip + ',' + eth
            ip_dict[dict_key] = tmp_list

    return ip_dict, xml_ip_list, eth_ip_list


def check_svip_in_eth(sub_svip, sub_subnet_mask, sub_network_interfaces):
    """判断svip是否落到了集群内节点的网卡上
    :Author: zhangchengyu
    :Date: 2018-08-20
    :param sub_svip: svip的ip地址（一个ip地址）
    :param sub_subnet_mask: 配置svip是的掩码（支持IPv4）
    :param sub_network_interfaces: 所配置的网卡名
    :return:"-1" svip不在集群内任何网卡上
            "0" svip落到了某张网卡上
    """
    obj_node = common.Node()
    node_ip_list = obj_node.get_nodes_ip()
    svip_judge = sub_svip + '/' + sub_subnet_mask
    svip_is_on_eth = False
    num = 0
    for node_ip in node_ip_list:
        cmd = 'ip addr | grep %s ' % svip_judge
        rc, stdout = common.run_command(node_ip, cmd)
        sub_network_interfaces_list = sub_network_interfaces.split(',')
        for sub_network_interface in sub_network_interfaces_list:
            if stdout.find(str(svip_judge)) != -1:
                if stdout.find(str(sub_network_interface)) != -1:
                    print stdout.find(str(sub_network_interface))
                    svip_is_on_eth = True
                    num = num + 1
                    log.info("svip is on %s %s" % (sub_network_interface, node_ip))
    if svip_is_on_eth is False:
        return -1
    elif num > 1:
        return -1
    else:
        return 0


def check_nas_status(timeout=180, get_node_id=None):
    """检查NAS相关服务状态（auth_provider_server_status，ftp_status，ctdb_status，smb_status，
    nfs_status，dns_status，auth_provider_client_status）
    :Author: jiangxiaoguang
    :Date: 2018-08-20
    :param timeout:判断超时的最长时间，超过该时间后，认为NAS相关服务一直存在问题，需要检查环境
    :return: "-1" 超过timeout的时间后，NAS状态依然有异常，需要检查环境
             "0" timeout的时间内，NAS状态正常
    ：description: 启动NAS服务后，才可调用该函数
    change: 2018-11-23 修改对node['reported_info']['service']的判断方式
    """
    log.info("\t[ check_nas_status ]")

    flag = True
    time_start = time.time()
    while flag:
        msg = get_nodes(get_node_id)
        nodes = msg['result']['nodes']

        time_end = time.time()
        if time_end - time_start > timeout:
            return -1

        not_ok_flag = False
        for node in nodes:
            log.info('check_nas_status on node %s' % node['ctl_ips'][0]['ip_address'])
            server_status = node['reported_info']['nas_protocol']['server_status']
            for key, value in server_status.items():
                log.info("key=%s, value=%s" % (key, value))
                if value != 'SERV_STATE_OK':
                    not_ok_flag = True
                    log.error("key=%s, value=%s" % (key, value))
                    break
            if not_ok_flag is True:
                time.sleep(30)
                break

            service = node['reported_info']['service']
            for tmp in service:
                if 'service_type' in tmp and tmp['service_type'] == 'oCnas' and tmp['state'] != 'SERV_STATE_OK':
                    log.error("key=%s, value=%s" % (tmp['service_type'], tmp['state']))
                    not_ok_flag = True
                    break
            # for key, value in service[-3].items():
            #     print key, value
            #     if value != 'SERV_STATE_OK' and value != 'oCnas':
            #         log.error("key=%s, value=%s" % (key, value))
            #         not_ok_flag = True
            #         break
            if not_ok_flag is True:
                time.sleep(30)
                break

        # 正常结束
        if not_ok_flag is False:
            flag = False

    return 0


def smb_mount(disk_symbol, mount_path, password, user, uri=DEFAULT_SMB_CLIENT_IP_AND_PORT):
    """smb挂载
    :Author: jiangxiaoguang
    :Date: 2018-08-04
    :param disk_symbol: 盘符，类似:'x:'
    :param mount_path: 挂载路径
    :param password: 用户登录密码
    :param user: 用户登录名称
    :param uri: 做nas客户端的Windows设备的IP和端口号，类似：'10.2.41.250:8270'
    :return: retcode, output
        retcode 命令返回码（注：因为recode对失败无法细区分，固除0以外均不是返回命令的recode本身）：
            0 - 挂载成功
            53 - mount_path错误
            59 - ip不在授权范围
            85 - mount_path错误
            86 - user或passwd错误
        output 命令输出
    """
    log.info("\t[ smb_mount ]")

    # 连接Windows端
    a = remote.Remote(uri=uri)
    log.info(a.get_keyword_names())

    # 调用Windows端函数
    retcode, output = a.run_keyword('smb_mount', [disk_symbol, mount_path, password, user])
    log.info('retcode = %s' % retcode)
    if retcode == 0:                                    # 命令成功完成。（挂载成功）
        return 0, output
    elif retcode != 0 and output.find(' 53') != -1:     # 找不到网络路径。（mount_path错误）
        return 53, output
    elif retcode != 0 and output.find(' 59') != -1:     # 出现了意外的网络错误。（ip不在授权范围）
        return 59, output
    elif retcode != 0 and output.find(' 85') != -1:     # 本地设备名已在使用中。（mount_path错误）
        return 85, output
    elif retcode != 0 and output.find(' 86') != -1:     # 指定的网络密码不正确。（user或passwd错误）
        return 86, output
    else:
        return retcode, output


def smb_umount(disk_symbol, uri=DEFAULT_SMB_CLIENT_IP_AND_PORT):
    """smb去挂载
    :Author: jiangxiaoguang
    :Date: 2018-08-04
    :param disk_symbol: 盘符，类似:'x:'
    :param uri: 做nas客户端的Windows设备的IP和端口号，类似：'10.2.41.250:8270'
    :return: retcode:命令返回码：
                0 - 去挂载成功

    """
    log.info("\t[ smb_umount ]")

    # 连接Windows端
    a = remote.Remote(uri=uri)
    log.info(a.get_keyword_names())
    # 调用Windows端函数
    retcode, output = a.run_keyword('smb_umount', [disk_symbol])
    log.info('retcode = %s' % retcode)
    # todo: 待完成
    # >去挂载失败<
    # retcode=2, 找不到网络连接
    # if retcode != 2:
    #     raise Exception("%s Failed" % FILE_NAME)
    # >去挂载成功<
    # if output.find('已经删除') == -1:
    #     raise Exception("%s Failed" % FILE_NAME)

    return


def get_smb_mount_info(uri=DEFAULT_SMB_CLIENT_IP_AND_PORT):
    """查询挂载信息
    :Author: jiangxiaoguang
    :Date: 2018-08-04
    :param uri: 做nas客户端的Windows设备的IP和端口号，类似：'10.2.41.250:8270'
    :return: retcode, output
        :retcode 命令返回码
        :output 命令输出
    """
    log.info("\t[ get_smb_mount_info ]")

    # 连接Windows端
    a = remote.Remote(uri=uri)
    log.info(a.get_keyword_names())

    # 调用Windows端函数
    retcode, output = a.run_keyword('net_use')
    log.info('retcode = %s' % retcode)

    return retcode, output


def get_smb_mount_disk_symbol_info(mount_path=None, uri=DEFAULT_SMB_CLIENT_IP_AND_PORT):
    """查询已挂载信息
    :Author: jiangxiaoguang
    :Date: 2018-08-04
    :param mount_path: 挂载路径，若为None则查询所有挂载路径的盘符，类似：'\\10.2.40.49\smb_export_name'
    :param uri: 做nas客户端的Windows设备的IP和端口号，类似：'10.2.41.250:8270'
    :return: disk_symbol_list: 已挂载的盘符列表
        (1)、指定路径查找，若查到了，则返回查到的盘符，类似：['x:']；若没查到，则返回空列表[]
        (2)、不指定路径查找，则返回查到的全部盘符列表，类似['x:', 'y:', 'z:']；若没查到，则返回空列表[]
    """
    log.info("\t[ get_smb_mount_disk_symbol_info ]")

    disk_symbol_list = []

    # 连接Windows端
    a = remote.Remote(uri=uri)
    log.info(a.get_keyword_names())

    # 调用Windows端函数
    retcode, output = a.run_keyword('net_use')
    log.info('retcode = %s' % retcode)
    if retcode != 0:
        raise Exception('net_use Failed.')

    output_lines = output.split('\n')
    # 未对状态为“已断开”情况做处理
    if mount_path:
        for line in output_lines:
            if 'OK ' in line and mount_path in line:
                disk_symbol_list.append(line.split()[1])
    else:
        for line in output_lines:
            if 'OK ' in line:
                disk_symbol_list.append(line.split()[1])
    log.info('disk_symbol_list = %s' % disk_symbol_list)

    return disk_symbol_list


def create_file_by_smb_client(disk_symbol, filename, uri=DEFAULT_SMB_CLIENT_IP_AND_PORT):
    # 连接Windows端
    a = remote.Remote(uri=uri)
    log.info(a.get_keyword_names())

    # 调用Windows端函数
    # retcode, output = a.run_keyword('create_file', [disk_symbol, filename])
    # log.info('retcode = %s' % retcode)
    # print output
    a.run_keyword('create_file', [disk_symbol, filename])
    return


def modify_files(path, create_file_count, modify_file_count, ext_node_ip):
    """
    :date: 2018-09-05
    :author: liyao
    :param file_path: 创建文件所在的目录
    :param create_file_count: 指定创建文件的数目
    :param modify_file_count: 指定修改文件的数目
    :param ext_node_ip: 执行命令的节点
    :return: 返回原始文件的md5值，如有校验需要可以使用
    """

    """在指定目录下创建子目录，作为移动文件的目标目录"""
    sub_dir = os.path.join(path, 'test_dir')
    cmd = 'mkdir -p %s' % sub_dir
    rc, stdout = common.run_command(ext_node_ip, cmd)
    common.judge_rc(rc, 0, 'create sub_dir %s failed !!!' % sub_dir)
    whole_dir = os.path.join(path, sub_dir)  # 包含所创建子目录的绝对路径

    """创建指定数目的文件"""
    file_name_list = []  # 文件名称列表
    file_path_list = []  # 文件所在的绝对路径
    file_md5_list = []
    for i in range(create_file_count):
        file_name = 'test_' + str(i)
        file_name_list.append(file_name)
        file_path = os.path.join(path, file_name)
        file_path_list.append(file_path)
        cmd = 'dd if=%s of=%s bs=1M count=100' % (snap_common.get_system_disk(ext_node_ip), file_path)
        common.run_command(ext_node_ip, cmd)
        rc, md5 = snap_common.get_file_md5(ext_node_ip, file_path)
        file_md5_list.append(md5)

    log.info('waiting for 10s')
    time.sleep(10)

    """对指定数目的文件进行修改等操作"""
    '''截断文件'''
    modify_path_list = random.sample(file_path_list, modify_file_count)  # 被选中进行修改的文件所在位置的绝对路径
    for i in range(modify_file_count):
        cmd = 'truncate %s -s 1M' % modify_path_list[i]
        rc, stdout = common.run_command(ext_node_ip, cmd)
        common.judge_rc(rc, 0, 'truncate execution failed !!!')

    '''修改文件内容'''
    modify_path_list = random.sample(file_path_list, modify_file_count)
    for i in range(modify_file_count):
        cmd = 'echo 1111111111 > %s' % modify_path_list[i]
        rc, stdout = common.run_command(ext_node_ip, cmd)
        common.judge_rc(rc, 0, 'modify file failed !!!')

    '''复制文件'''
    modify_path_list = random.sample(file_path_list, modify_file_count)
    move_path_list = []  # 复制到子目录下之后，文件及其绝对路径列表
    for i in range(modify_file_count):
        tmp_path = os.path.join(whole_dir, 'cp_test_' + str(i))
        move_path_list.append(tmp_path)
    for i in range(modify_file_count):
        cmd = 'cp %s %s' % (modify_path_list[i], move_path_list[i])
        rc, stdout = common.run_command(ext_node_ip, cmd)
        common.judge_rc(rc, 0, 'copy file failed !!!')

    '''修改文件名称'''
    modify_path_list = random.sample(file_path_list, modify_file_count)
    rename_path_list = []
    for i in range(modify_file_count):
        tmp_path = os.path.join(path, 'rename_test_' + str(i))
        rename_path_list.append(tmp_path)
    for i in range(modify_file_count):
        cmd = 'mv %s %s' % (modify_path_list[i], rename_path_list[i])
        rc, stdout = common.run_command(ext_node_ip, cmd)
        common.judge_rc(rc, 0, 'rename file failed !!!')

    '''删除文件'''
    modify_path_list = random.sample(file_path_list, modify_file_count)
    for i in range(modify_file_count):
        rc, stdout = common.rm_exe(ext_node_ip, modify_path_list[i])
        common.judge_rc(rc, 0, 'delete file failed !!!')

    return file_md5_list


def mount(server_ip, server_path, client_ip, client_path, mount_type="nfs"):
    """
    :date: 2018-12-04
    :author: zhangchengyu
    :description: 检查客户端的mount路径是否存在，存在则强制umount并删除；mount服务端的路径到客户端的路径上
    :param server_ip: 服务端的ip
    :param server_path: 服务端的路径，全路径 /mnt/a/nfs
    :param client_ip: 客户端的ip
    :param client_path: 客户端的类型,全路径 /mnt/a/
    :param mount_type: mount的类型，比如nfs
    :return: flag_info，flag_info=0正常，否则为错误
    """
    log.info("\t[ 客户端创建mount路径 ]")
    flag_info = 0
    cmd = "ls %s" % client_path
    rc, stdout = common.run_command(client_ip, cmd)
    log.info("mode_ip=%s, cmd=%s, stdout=%s" % (client_ip, cmd, stdout))
    if stdout == "" or "No such file or directory" not in stdout:
        cmd = "umount -l %s" % client_path
        common.run_command(client_ip, cmd)
        cmd = "rm -rf %s" % client_path
        rc, stdout = common.run_command(client_ip, cmd)
        log.info("mode_ip=%s, cmd=%s, stdout=%s" % (client_ip, cmd, stdout))
        if rc != 0:
            flag_info = 1
            log.error('%s rm -rf client file failed!!!' % client_ip)
    cmd = "mkdir -p %s" % client_path
    rc, stdout = common.run_command(client_ip, cmd)
    log.info("mode_ip=%s, cmd=%s, stdout=%s" % (client_ip, cmd, stdout))
    if rc != 0:
        flag_info = 2
        log.error('%s create_file failed!!!' % client_ip)

    log.info("\t[ 客户端mount ]")
    begin_time = time.time()
    rc = 1
    while rc != 0 and flag_info != 3:
        cmd1 = "mount -t %s %s:%s %s" % (mount_type, server_ip, server_path, client_path)
        rc, stdout = common.run_command(client_ip, cmd1)
        log.info("mode_ip=%s, cmd=%s, stdout=%s" % (client_ip, cmd, stdout))
        last_time = time.time()
        during_time = last_time - begin_time
        if int(during_time) >= 30:
            log.error('%s mount file failed and timeout 30s!!!' % client_ip)
            flag_info = 3
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (client_ip, cmd1, stdout))
        time.sleep(5)
    return flag_info


def umount(client_ip, client_path):
    """
    :date: 2018-12-04
    :author: zhangchengyu
    :description: umount客户端的路径，并删除
    :param client_ip: 客户端的ip
    :param client_path: 客户端的类型
    :return: flag_info，flag_info=0正常，否则为错误
    """
    log.info("\t[ 客户端umount共享路径 ]")
    flag_info = 0
    cmd1 = "umount -fl %s" % client_path
    rc, stdout = common.run_command(client_ip, cmd1)
    log.info("mode_ip=%s, cmd=%s, stdout=%s" % (client_ip, cmd1, stdout))
    if rc != 0:
        flag_info = 1
        log.error('%s umount file failed!!!' % client_ip)

    log.info("\t[ 客户端删除mount路径 ]")
    cmd1 = "rm -rf %s " % client_path
    rc, stdout = common.run_command(client_ip, cmd1)
    log.info("mode_ip=%s, cmd=%s, stdout=%s" % (client_ip, cmd1, stdout))
    if rc != 0:
        flag_info = 1
        log.error('%s rm file failed!!!' % client_ip)
    return flag_info

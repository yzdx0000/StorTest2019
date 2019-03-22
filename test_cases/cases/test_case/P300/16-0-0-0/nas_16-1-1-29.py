# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-09-3
# @summary：
# 16_1_1_29     配置虚ip后，oJob进程换主对业务的影响
# @steps:
# 1、配置vip地址池分配方式为动态，nfs客户端成功挂载到某机头节点并进行读写业务；
# 包含：创建AD认证——>创建访问分区——>启动NAS——>创建Rsubnet——>创建vip池——>创建NFS导出——>
# NFS客户端挂载——>NFS客户端进行读写业务
# 2、oJob进程换主；
# 3、观察客户业务（比如读写）是否受到影响；
# 4、清理环境
# @changelog：
#
#######################################################
from multiprocessing import Process
import re
import os
import time
import random
import commands
import utils_path
import common
import nas_common
import log
import get_config
import tool_use
import shell
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_1_1_29
SYSTEM_IP = get_config.get_parastor_ip()
AD_IP = nas_common.AD_DNS_ADDRESSES
ad_name = "ad_16_1_1_29"
AD_DOMAIN_NAME = nas_common.AD_DOMAIN_NAME
AD_USER_NAME = nas_common.AD_USER_NAME
AD_PASSWORD = nas_common.AD_PASSWORD


def executing_case1():
    """1、配置vip地址池分配方式为动态，nfs客户端成功挂载到某机头节点并进行读写业务；"""
    """同步NTP"""
    log.info("\t[ 1.set_ntp ]")
    node_ip = SYSTEM_IP
    msg2 = nas_common.set_ntp(is_enabled="true", ntp_servers=AD_IP)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s set_ntp failed!!!' % node_ip)

    """创建AD认证"""
    log.info("\t[ 1.add_auth_provider_ad ]")
    msg4 = nas_common.add_auth_provider_ad(name=ad_name,
                                           domain_name=AD_DOMAIN_NAME,
                                           dns_addresses=AD_IP,
                                           username=AD_USER_NAME,
                                           password=AD_PASSWORD,
                                           services_for_unix="NONE",
                                           unix_id_range="%s-%s" % (1000, 200000),
                                           other_unix_id_range="%s-%s" % (200001, 200002))
    if msg4["err_msg"] != "" or msg4["detail_err_msg"] != "":
        common.except_exit('%s add_auth_provider_ad failed!!!' % node_ip)
    ad_id_16_1_1_29 = msg4["result"]

    """get_auth_providers_ad"""
    log.info("\t[ 1.get_auth_provider_ad ]")
    msg2 = nas_common.get_auth_providers_ad(ids=ad_id_16_1_1_29)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s get_auth_providers_ad failed!!!' % node_ip)
    dns_addresses = msg2["result"]["auth_providers"][0]["dns_addresses"][0]
    domain_name = msg2["result"]["auth_providers"][0]["domain_name"]
    id = msg2["result"]["auth_providers"][0]["id"]
    key = msg2["result"]["auth_providers"][0]["key"]
    name = msg2["result"]["auth_providers"][0]["name"]
    other_unix_id_range = msg2["result"]["auth_providers"][0]["other_unix_id_range"]
    services_for_unix = msg2["result"]["auth_providers"][0]["services_for_unix"]
    type = msg2["result"]["auth_providers"][0]["type"]
    unix_id_range = msg2["result"]["auth_providers"][0]["unix_id_range"]
    username = msg2["result"]["auth_providers"][0]["username"]
    if dns_addresses != AD_IP:
        common.except_exit('%s dns_addresses error %s != %s!!!' % (node_ip, dns_addresses, AD_IP))
    if domain_name != AD_DOMAIN_NAME:
        common.except_exit('%s domain_name error %s != %s!!!' % (node_ip, domain_name, AD_DOMAIN_NAME))
    if id != ad_id_16_1_1_29:
        common.except_exit('%s id error %s != %s!!! ' % (node_ip, id, ad_id_16_1_1_29))
    if key != ad_id_16_1_1_29:
        common.except_exit('%s key error %s != %s!!!' % (node_ip, key, ad_id_16_1_1_29))
    if name != ad_name:
        common.except_exit('%s name error %s != %s!!!' % (node_ip, name, ad_name))
    if other_unix_id_range != [
        200001,
        200002
    ]:
        common.except_exit('%s other_unix_id_range error!!!' % node_ip)
    if services_for_unix != "NONE":
        common.except_exit('%s services_for_unix error %s != NONE!!!' % (node_ip, services_for_unix))
    if type != "AD":
        common.except_exit('%s type error %s != AD!!!' % (node_ip, type))
    if unix_id_range != [
        1000,
        200000
    ]:
        common.except_exit('%s unix_id_range error!!!' % node_ip)
    if username != AD_USER_NAME:
        common.except_exit('%s username error %s != %s!!!' % (node_ip, username, AD_USER_NAME))

    """ check_auth_provider """
    log.info("\t[4.check_auth_provider AD]")
    msg2 = nas_common.check_auth_provider(provider_id=ad_id_16_1_1_29)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s check_auth_provider ad failed!!!' % node_ip)

    """创建访问分区"""
    log.info("\t[1 create_access_zone ]")
    node_ip = SYSTEM_IP
    access_zone_name = "access_zone_16_1_1_29"
    cmd = 'pscli --command=get_nodes'
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "get_nodes failed")
    outtext = common.json_loads(stdout)
    nodes = outtext['result']['nodes']
    ids = []
    for node in nodes:
        ids.append(node['data_disks'][0]['nodeId'])
    print ids
    access_zone_node_id_16_1_1_29 = ','.join(str(p) for p in ids)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_1_1_29,
                                         name=access_zone_name,
                                         auth_provider_id=ad_id_16_1_1_29)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s create_access_zone failed!!!' % node_ip)
    access_zone_id_16_1_1_29 = msg1["result"]

    """获取访问分区信息"""
    log.info("\t[1 get_access_zones ]")
    msg1 = nas_common.get_access_zones(ids=access_zone_id_16_1_1_29)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s get_access_zones failed!!!' % node_ip)
    name = msg1["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        raise Exception('%s get_access_zones failed!!!' % node_ip)

    """启动NAS"""
    log.info("\t[ 1 enable_nas ]")
    msg2 = nas_common.enable_nas(access_zone_id=access_zone_id_16_1_1_29)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s enable_nas failed!!!' % node_ip)

    """创建业务子网"""
    log.info("\t[1 create_subnet ]")
    sub_name = "subnet_16_1_1_29"
    sub_network_interfaces = nas_common.SUBNET_NETWORK_INTERFACES
    sub_svip = nas_common.SUBNET_SVIP
    sub_subnet_mask = nas_common.SUBNET_MASK
    sub_subnet_gateway = nas_common.SUBNET_GATEWAY
    sub_mtu = nas_common.SUBNET_MTU
    sub_ip_family = nas_common.IPv4
    check_result1 = nas_common.create_subnet(access_zone_id=access_zone_id_16_1_1_29,
                                             name=sub_name,
                                             ip_family=sub_ip_family,
                                             svip=sub_svip,
                                             subnet_mask=sub_subnet_mask,
                                             subnet_gateway=sub_subnet_gateway,
                                             network_interfaces=sub_network_interfaces,
                                             mtu=sub_mtu)
    if check_result1["err_msg"] != "" or check_result1["detail_err_msg"] != "":
        common.except_exit('%s create_subnet failed!!!' % node_ip)
    subnet_id_16_1_1_29 = check_result1["result"]

    """获取子网信息"""
    log.info("\t[1 get_subnets ]")
    msg1 = nas_common.get_subnets(ids=subnet_id_16_1_1_29)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s get_subnets failed!!!' % node_ip)
    access_zone_id = msg1["result"]["subnets"][0]["access_zone_id"]
    if access_zone_id != access_zone_id_16_1_1_29:
        common.except_exit('%s access_zone_id failed %s != %s !!!'
                           % (node_ip, access_zone_id, access_zone_id_16_1_1_29))
    idd = msg1["result"]["subnets"][0]["id"]
    if idd != subnet_id_16_1_1_29:
        common.except_exit('%s id failed %s != %s !!!' % (node_ip, idd, subnet_id_16_1_1_29))
    ip_family = msg1["result"]["subnets"][0]["ip_family"]
    if ip_family != sub_ip_family:
        common.except_exit('%s ip_family failed %s != %s !!!' % (node_ip, ip_family, sub_ip_family))
    mtu = msg1["result"]["subnets"][0]["mtu"]
    if mtu != int(sub_mtu):
        common.except_exit('%s mtu failed %s != %s !!!' % (node_ip, mtu, sub_mtu))
    name = msg1["result"]["subnets"][0]["name"]
    if name != sub_name:
        common.except_exit('%s name failed %s != %s !!!' % (node_ip, name, sub_name))
    network_interfaces = msg1["result"]["subnets"][0]["network_interfaces"]
    for network_interface in network_interfaces:
        if network_interface not in sub_network_interfaces:
            common.except_exit(
                '%s network_interfaces failed %s != %s !!!' % (node_ip, network_interface, sub_network_interfaces))
    subnet_gateway = msg1["result"]["subnets"][0]["subnet_gateway"]
    if subnet_gateway != sub_subnet_gateway:
        common.except_exit('%s subnet_gateway failed %s != %s !!!' % (node_ip, subnet_gateway, sub_subnet_gateway))
    subnet_mask = msg1["result"]["subnets"][0]["subnet_mask"]
    if subnet_mask != int(sub_subnet_mask):
        common.except_exit('%s subnet_mask failed %s != %s !!!' % (node_ip, subnet_mask, sub_subnet_mask))
    subnet_mask = msg1["result"]["subnets"][0]["subnet_mask"]
    if subnet_mask != int(sub_subnet_mask):
        common.except_exit('%s subnet_mask failed %s != %s !!!' % (node_ip, subnet_mask, sub_subnet_mask))
    subnet_state = msg1["result"]["subnets"][0]["subnet_state"]
    if subnet_state != "SUBNET_READY":
        common.except_exit('%s subnet_state failed %s != SUBNET_READY !!!' % (node_ip, subnet_state))
    svip = msg1["result"]["subnets"][0]["svip"]
    if svip != sub_svip:
        common.except_exit('%s svip failed %s != %s !!!' % (node_ip, svip, sub_svip))

    '''通过命令行ip addr观察SVIP绑定到哪个节点ethx上'''
    log.info("\t[1 check_svip_in_eth ]")
    rc = nas_common.check_svip_in_eth(sub_svip, sub_subnet_mask, sub_network_interfaces)
    common.judge_rc(rc, 0, "svip没有落到集群内节点的网卡上")

    """添加vip池"""
    log.info("\t[1 add_vip_address_pool ]")
    vip_domain_name = nas_common.VIP_DOMAIN_NAME
    vip_vip_addresses = nas_common.VIP_ADDRESSES
    vip_supported_protocol = "NAS"
    vip_allocation_method = "DYNAMIC"
    vip_load_balance_policy = "LB_ROUND_ROBIN"
    vip_ip_failover_policy = "IF_ROUND_ROBIN"
    msg1 = nas_common.add_vip_address_pool(subnet_id=subnet_id_16_1_1_29,
                                           domain_name=vip_domain_name,
                                           vip_addresses=vip_vip_addresses,
                                           supported_protocol=vip_supported_protocol,
                                           allocation_method=vip_allocation_method,
                                           load_balance_policy=vip_load_balance_policy,
                                           ip_failover_policy=vip_ip_failover_policy)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s add_vip_address_pool failed!!!' % node_ip)
    vip_address_pool_id_16_1_1_29 = msg1["result"]

    """ 通过pscli --command=get_vip_address_pools查看与配置的信息是否匹配"""
    log.info("\t[1 get_vip_address_pools ]")
    msg1 = nas_common.get_vip_address_pools(ids=vip_address_pool_id_16_1_1_29)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s get_vip_address_pools!!!' % node_ip)
    allocation_method = msg1["result"]["ip_address_pools"][0]["allocation_method"]
    if allocation_method != vip_allocation_method:
        common.except_exit(
            '%s allocation_method failed %s != %s !!!' % (node_ip, allocation_method, vip_allocation_method))
    domain_name = msg1["result"]["ip_address_pools"][0]["domain_name"]
    if domain_name != vip_domain_name:
        common.except_exit('%s domain_name failed %s != %s !!!' % (node_ip, domain_name, vip_domain_name))
    idd = msg1["result"]["ip_address_pools"][0]["id"]
    if idd != vip_address_pool_id_16_1_1_29:
        common.except_exit('%s id failed %s != %s !!!' % (node_ip, idd, vip_address_pool_id_16_1_1_29))
    ip_failover_policy = msg1["result"]["ip_address_pools"][0]["ip_failover_policy"]
    if ip_failover_policy != vip_ip_failover_policy:
        common.except_exit(
            '%s ip_failover_policy failed %s != %s !!!' % (node_ip, ip_failover_policy, vip_ip_failover_policy))
    ipaddr_pool_state = msg1["result"]["ip_address_pools"][0]["ipaddr_pool_state"]
    if ipaddr_pool_state != "IPADDR_POOL_READY":
        common.except_exit('%s ipaddr_pool_state failed %s != "IPADDR_POOL_READY" !!!' % (node_ip, ipaddr_pool_state))
    load_balance_policy = msg1["result"]["ip_address_pools"][0]["load_balance_policy"]
    if load_balance_policy != vip_load_balance_policy:
        common.except_exit(
            '%s load_balance_policy failed %s != %s !!!' % (node_ip, load_balance_policy, vip_load_balance_policy))
    subnet_id = msg1["result"]["ip_address_pools"][0]["subnet_id"]
    if subnet_id != subnet_id_16_1_1_29:
        common.except_exit('%s subnet_id failed %s != %s !!!' % (node_ip, subnet_id, subnet_id_16_1_1_29))
    supported_protocol = msg1["result"]["ip_address_pools"][0]["supported_protocol"]
    if supported_protocol != vip_supported_protocol:
        common.except_exit(
            '%s supported_protocol failed %s != %s !!!' % (node_ip, supported_protocol, vip_supported_protocol))
    vip_addresses = msg1["result"]["ip_address_pools"][0]["vip_addresses"][0]
    if vip_addresses != vip_vip_addresses:
        common.except_exit('%s vip_addresses failed %s != %s !!!' % (node_ip, vip_addresses, vip_vip_addresses))

    """命令行通过IP addr观察VIP是否绑定到3个节点到对应的网卡上（相同网段的网卡）"""
    log.info("\t[1 ip addr ]")
    ip_dict, xml_ip_list, eth_ip_list = nas_common.get_vip_from_eth(subnet_network_interfaces=sub_network_interfaces,
                                                                    vip_addresses=vip_vip_addresses,
                                                                    subnet_mask=sub_subnet_mask)
    rc = nas_common.judge_vip_layinfo(ip_dict, xml_ip_list, eth_ip_list)
    common.judge_rc(rc, 0, "通过IP addr观察VIP绑定情况有误")

    """创建文件"""
    log.info("\t[ 1.create_file ]")
    nfs_user = nas_common.AD_USER_1
    nfs_client_ip = nas_common.NFS_1_CLIENT_IP
    nfs_path = nas_common.ROOT_DIR + "nfs_dir_16_1_1_29"
    global NAS_PATH
    NAS_PATH = get_config.get_one_nas_test_path() + "/nfs_dir_16_1_1_29"
    nfs_export_name = "nfs_16_1_1_29"
    msg2 = nas_common.create_file(path=nfs_path)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s create_file failed!!!' % node_ip)

    """创建NFS导出"""
    log.info("\t[ 1.create_nfs_export ]")
    msg2 = nas_common.create_nfs_export(access_zone_id=access_zone_id,
                                        export_name=nfs_export_name,
                                        export_path=nfs_path)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s create_nfs_export failed!!!' % node_ip)
    nfs_export_id = msg2["result"]

    """get_nfs_exports"""
    log.info("\t[ 1.get_nfs_exports]")
    msg2 = nas_common.get_nfs_exports(ids=nfs_export_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s get_nfs_exports failed!!!' % node_ip)
    export_name = msg2["result"]["exports"][0]["export_name"]
    export_path = msg2["result"]["exports"][0]["export_path"]
    if export_name != nfs_export_name:
        common.except_exit('%s export_name failed!!!' % node_ip)
    if export_path != nfs_path:
        common.except_exit('%s export_path failed!!!' % node_ip)

    """创建NFS客户端授权"""
    log.info("\t[ 1 add_nfs_export_auth_clients ]")
    auth_clients_name = nas_common.NFS_1_CLIENT_IP
    auth_clients_name_a = sub_svip.split(".")[0] + "." + auth_clients_name.split(".")[1] + "." + \
                          auth_clients_name.split(".")[2] + "." + auth_clients_name.split(".")[3]
    print auth_clients_name_a
    time.sleep(5)
    auth_clients_permission_level = 'rw'
    msg = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id,
                                                 name=auth_clients_name_a,
                                                 permission_level=auth_clients_permission_level)
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        common.except_exit('%s add_nfs_export_auth_clients failed!!!' % node_ip)
    nfs_export_clients_id_16_1_1_29 = msg["result"][0]

    """get_nfs_export_auth_clients"""
    log.info("\t[ 1 get_nfs_export_auth_clients ]")
    check_result = nas_common.get_nfs_export_auth_clients(export_ids=nfs_export_id)
    if check_result["err_msg"] != "" or check_result["detail_err_msg"] != "":
        common.except_exit('%s get_nfs_export_auth_clients failed!!!' % node_ip)

    """2> 对比设置参数"""
    anongid = check_result["result"]["nfs_export_auth_clients"][0]["anongid"]
    anonuid = check_result["result"]["nfs_export_auth_clients"][0]["anonuid"]
    id = check_result["result"]["nfs_export_auth_clients"][0]["id"]
    export_id = check_result["result"]["nfs_export_auth_clients"][0]["export_id"]
    name = check_result["result"]["nfs_export_auth_clients"][0]["name"]
    permission_constraint = check_result["result"]["nfs_export_auth_clients"][0]["permission_constraint"]
    permission_level = check_result["result"]["nfs_export_auth_clients"][0]["permission_level"]
    port_constraint = check_result["result"]["nfs_export_auth_clients"][0]["port_constraint"]
    write_mode = check_result["result"]["nfs_export_auth_clients"][0]["write_mode"]
    if anongid != 65534:
        common.except_exit('%s anongid failed!!!' % node_ip)
    if anonuid != 65534:
        common.except_exit('%s anonuid failed!!!' % node_ip)
    if id != nfs_export_clients_id_16_1_1_29:
        common.except_exit('%s id failed!!!' % node_ip)
    if export_id != nfs_export_id:
        common.except_exit('%s export_id failed!!!' % node_ip)
    if name != auth_clients_name_a:
        common.except_exit('%s name failed!!!' % node_ip)
    if permission_constraint != "root_squash":
        common.except_exit('%s permission_constraint failed!!!' % node_ip)
    if permission_level != auth_clients_permission_level:
        common.except_exit('%s permission_level failed!!!' % node_ip)
    if port_constraint != "secure":
        common.except_exit('%s port_constraint failed!!!' % node_ip)
    if write_mode != "async":
        common.except_exit('%s write_mode failed!!!' % node_ip)

    """确认用户存在"""
    log.info("\t[ 1.get_auth_users ]")
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=ad_id_16_1_1_29)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s get_auth_users  failed!!!' % node_ip)
    totalnumber = msg2["result"]["total"]
    name_list = []
    for i in range(0, totalnumber):
        name_list.append(msg2["result"]["auth_users"][i]["name"])
    if nfs_user not in name_list:
        log.error('node_ip = %s, ADserver中用户没有被正确获取' % node_ip)
        common.except_exit('%s ADserver中用户没有被正确获取!!!' % node_ip)

    """ 查看NAS服务状态"""
    log.info("\t[ 1.check NAS status ]")
    rc = nas_common.check_nas_status()
    common.judge_rc(rc, 0, "Please check nas status")

    """找oJob的主ip"""
    log.info("\t[ 1.nfs server find the master of oJob ]")
    cmd = "/home/parastor/tools/nWatch -t oJob -i 1 -c RCVR#jobinfo"
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, '/home/parastor/tools/nWatch -t oJob -i 1 -c RCVR#jobinfo failed!!!')
    ojob_node_id_1 = re.split('[: ]', stdout)[-1]
    ojob_node_id = ojob_node_id_1.split("\n")[0]
    print ojob_node_id
    node = common.Node()
    ojob_node_ip = node.get_node_ip_by_id(ojob_node_id)
    print ojob_node_ip

    """nfs客户端修改resolv.conf文件"""
    log.info("\t[ 1.nfs client vim  /etc/resolv.conf]")
    cmd = "echo 'nameserver %s' >> /etc/resolv.conf" % sub_svip
    rc, stdout = common.run_command(auth_clients_name, cmd)
    common.judge_rc(rc, 0, '%s nfs client update resolv.conf failed!!!' % auth_clients_name)

    """客户端创建mount路径"""
    log.info("\t[ 1 客户端创建mount路径 ]")
    auth_clients_mount_dir = "/mnt/nfs_dir_16_1_1_29"
    cmd = "ssh %s ls /mnt/nfs_dir_16_1_1_29" % auth_clients_name
    rc, stdout, stderr = shell.ssh(node_ip, cmd)
    if stdout == "":
        cmd = "ssh %s umount -l /mnt/nfs_dir_16_1_1_29" % auth_clients_name
        shell.ssh(node_ip, cmd)
        cmd = "ssh %s rm -rf /mnt/nfs_dir_16_1_1_29" % auth_clients_name
        rc, stdout, stderr = shell.ssh(node_ip, cmd)
        if rc != 0:
            log.error("WARNING: \ncmd = %s\nstdout = %s\nstderr = %s" % (cmd, stdout, stderr))
            raise Exception('%s rm -rf client file failed!!!' % node_ip)

    cmd = "mkdir %s" % auth_clients_mount_dir
    rc, stdout = common.run_command(auth_clients_name, cmd)
    common.judge_rc(rc, 0, "nfs client mkdir file failed!!!")

    """客户端mount共享路径"""
    log.info("\t[ 1 客户端mount共享路径 ]")
    wait_time1 = random.randint(15, 16)
    time.sleep(wait_time1)
    cmd1 = " mount -t nfs %s:%s %s" % (vip_domain_name, NAS_PATH, auth_clients_mount_dir)
    rc, stdout = common.run_command(auth_clients_name, cmd1)
    common.judge_rc(rc, 0, '%s mount file failed!!!' % auth_clients_name)

    """2.vdbench子进程开启"""
    log.info("\t[ 2 nfs client run vebench]")
    obj_vdb = tool_use.Vdbenchrun(size="(64k,30,256k,35,1m,30,2m,5)", elapsed=60)
    p1 = Process(target=obj_vdb.run_create, args=(auth_clients_mount_dir, auth_clients_mount_dir, nfs_client_ip))
    p1.daemon = True
    p1.start()

    """2.在oJob主节点上kill oJob"""
    log.info("\t[ 2 nfs server master kill oJob]")
    cmd = "ps -ef|grep oJob | grep -v grep"
    rc, stdout = common.run_command(ojob_node_ip, cmd)
    common.judge_rc(rc, 0, "ps -ef|grep oJob | grep -v grep failed!!!")
    pid = stdout.split()[1]
    cmd = "kill -9 %s " % pid
    rc, stdout = common.run_command(ojob_node_ip, cmd)
    common.judge_rc(rc, 0, "%s failed!!!" % cmd)

    time_limitation = 90
    time_used = 0
    while p1.is_alive() is True:
        log.info('waiting for 10s')
        time.sleep(10)
        time_used = time_used + 10
        if time_used > time_limitation:
            common.except_exit('vdbench is timeout !!!')

    """3.客户端umount挂载目录"""
    log.info("\t[ 3 nfs clinet umount file]")
    cmd1 = " umount -l %s" % auth_clients_mount_dir
    rc, stdout = common.run_command(auth_clients_name, cmd1)
    common.judge_rc(rc, 0, '%s umount file failed!!!' % auth_clients_name)

    """客户端清理环境"""
    log.info("\t[ 3 nfs clinet rm -rf file]")
    cmd1 = " rm -rf %s" % auth_clients_mount_dir
    rc, stdout = common.run_command(auth_clients_name, cmd1)
    common.judge_rc(rc, 0, '%s nfs clinet rm -rf file failed!!!' % auth_clients_name)

    """客户端恢复 /etc/resolv.conf文件"""
    log.info("\t[ 3 nfs clinet 恢复 /etc/resolv.conf文件]")
    cmd = "sed -i '/%s/d' /etc/resolv.conf" % sub_svip
    rc, stdout = common.run_command(auth_clients_name, cmd)
    common.judge_rc(rc, 0, "%s 恢复/etc/resolv.conf文件失败" % auth_clients_name)

    """delete_nfs_exports"""
    log.info("\t[ 3 delete_nfs_exports]")
    msg2 = nas_common.delete_nfs_exports(ids=nfs_export_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s delete_nfs_exports failed!!!' % node_ip)

    """清理server"""
    log.info("\t[ 3 nfs server rm -rf file]")
    cmd = "rm -rf %s" % NAS_PATH
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "nfs server rm -rf file failed")
    return


#######################################################
# @function：清理环境
# @parameter：
# @return：
# @steps:
#######################################################
def clearing_environment():
    log.info("（3）clearing_environment")

    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    log.info("（1）preparing_environment")

    '''
    1、下发nas相关的配置
    2、创建nas测试相关的目录和文件
    '''

    return


#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def nas_main():
    preparing_environment()
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("（2）executing_case")
    executing_case1()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)

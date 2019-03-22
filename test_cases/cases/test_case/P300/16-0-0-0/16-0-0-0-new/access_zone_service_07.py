# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-11-21
# @summary：
# x-x-x-x     服务设置，smb/nfs/ftp与S3的相互影响       注意：需要提前在环境中创建一个对象类型的存储池
# @steps:
# 1.创建ad，ldap，ldap-pdc，nis认证
# 2.随机选取认证服务创建访问分区
# 3.创建子网、vip地址池
# 4.启动NAS/S3，创建SMB、NFS、FTP协议导出，查看NAS服务状态，关闭S3/NAS（循环操作）
# @changelog：
#
#######################################################
import os
import time
import random

import utils_path
import common
import nas_common
import log
import get_config
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_4_104
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP

times = 5  # 控制NAS启停的次数


def executing_case1():
    """1 创建认证"""
    auth_provider_id_list = []
    """a.创建ad认证"""
    log.info("\t[1 add_auth_provider_ad]")
    ad_name = "ad_auth_provider"
    msg2 = nas_common.add_auth_provider_ad(name=ad_name,
                                           domain_name=nas_common.AD_DOMAIN_NAME,
                                           dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                           username=nas_common.AD_USER_NAME,
                                           password=nas_common.AD_PASSWORD,
                                           services_for_unix="NONE")

    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("add_auth_provider_ad failed")
    ad_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(ad_auth_provider_id)

    """b.创建ldap认证"""
    log.info("\t[1 add_auth_provider_ldap]")
    ldap_name = "ldap_auth_provider"
    msg2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_BASE_DN,
                                             ip_addresses=nas_common.LDAP_IP_ADDRESSES, port=389)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("add_auth_provider_ldap failed")
    ldap_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(ldap_auth_provider_id)

    """c.创建ldap_pdc认证"""
    log.info("\t[1 add_auth_provider_ldap_pdc]")
    ldap_name = "ldap_pdc_auth_provider"
    msg2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_2_BASE_DN,
                                             ip_addresses=nas_common.LDAP_2_IP_ADDRESSES, port=389,
                                             bind_dn=nas_common.LDAP_2_BIND_DN,
                                             bind_password=nas_common.LDAP_2_BIND_PASSWORD,
                                             domain_password=nas_common.LDAP_2_DOMAIN_PASSWORD)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("add_auth_provider_ldap_pdc failed")
    ldap_pdc_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(ldap_pdc_auth_provider_id)

    """d.创建nis认证"""
    log.info("\t[1 add_auth_provider_nis]")
    nis_name = "nis_auth_provider"
    msg2 = nas_common.add_auth_provider_nis(name=nis_name,
                                            domain_name=nas_common.NIS_DOMAIN_NAME,
                                            ip_addresses=nas_common.NIS_IP_ADDRESSES)

    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("add_auth_provider_nis failed")
    nis_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(nis_auth_provider_id)

    """2.创建访问分区"""
    log.info("\t[2 create_access_zone ]")
    access_zone_name = "access_zone"
    auth_provider_id = random.choice(auth_provider_id_list)
    # auth_provider_id_a = random.sample(auth_provider_id_list, 1)
    # auth_provider_id_b = [str(p) for p in auth_provider_id_a]
    # auth_provider_id = ''.join(auth_provider_id_b)
    node = common.Node()
    ids = node.get_nodes_id()
    access_zone_node_ids = ','.join(str(p) for p in ids)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_ids, name=access_zone_name,
                                         auth_provider_id=auth_provider_id)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('create_access_zone failed!!!')
    access_zone_id = msg1["result"]

    """3.创建子网、vip地址池"""
    log.info("\t[ 3 创建子网 ]")
    sub_name = "subnet_%s" % access_zone_id
    sub_network_interfaces = nas_common.SUBNET_NETWORK_INTERFACES
    print sub_network_interfaces
    sub_svip = nas_common.SUBNET_SVIP
    sub_subnet_mask = nas_common.SUBNET_MASK
    sub_subnet_gateway = nas_common.SUBNET_GATEWAY
    sub_mtu = nas_common.SUBNET_MTU
    msg1 = nas_common.create_subnet(access_zone_id=access_zone_id,
                                    name=sub_name,
                                    ip_family=nas_common.IPv4,
                                    svip=sub_svip,
                                    subnet_mask=sub_subnet_mask,
                                    subnet_gateway=sub_subnet_gateway,
                                    network_interfaces=sub_network_interfaces,
                                    mtu=sub_mtu)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('create_subnet failed!!!')
    subnet_id = msg1["result"]

    log.info("\t[ 3 创建vip地址池 ]")
    vip_domain_name = nas_common.VIP_DOMAIN_NAME
    vip_vip_addresses = nas_common.VIP_ADDRESSES
    vip_supported_protocol = "NAS"
    vip_allocation_method = "DYNAMIC"
    vip_load_balance_policy = "LB_ROUND_ROBIN"
    vip_ip_failover_policy = "IF_ROUND_ROBIN"
    msg1 = nas_common.add_vip_address_pool(subnet_id=subnet_id,
                                           domain_name=vip_domain_name,
                                           vip_addresses=vip_vip_addresses,
                                           supported_protocol=vip_supported_protocol,
                                           allocation_method=vip_allocation_method,
                                           load_balance_policy=vip_load_balance_policy,
                                           ip_failover_policy=vip_ip_failover_policy)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('add_vip_address_pool failed!!!')

    for i in range(1, times+1):
        log.info("\t[this is %s/%s time ]" % (i, times))
        protocol_types_list = ["NFS", "SMB", "FTP"]
        protocol_types = ",".join(random.sample(protocol_types_list,
                                                random.choice(range(1, len(protocol_types_list) + 1))))
        """随机选择先启动 NAS or s3 服务"""
        a = [1, 2]
        b = random.choice(a)
        if b == 1:
            log.info("\t[4 enable_nas_%s/%s ]" % (i, times))
            enable_nas(access_zone_id=access_zone_id, protocol_types=protocol_types)
            log.info("\t[4 enable_s3_%s/%s ]" % (i, times))
            enable_s3(access_zone_id=access_zone_id)
        elif b == 2:
            log.info("\t[4 enable_s3_%s/%s ]" % (i, times))
            enable_s3(access_zone_id=access_zone_id)
            log.info("\t[4 enable_nas_%s/%s ]" % (i, times))
            enable_nas(access_zone_id=access_zone_id, protocol_types=protocol_types)

        """创建协议的导出与授权客户端"""
        log.info("\t[4 创建导出协议 %s/%s 次]" % (i, times))
        if "NFS" in protocol_types:
            nfs_export(access_zone_id=access_zone_id, d=i)
            # access_zone_id：访问分区的id；d：一个数字，为区别路导出径名称
        if "FTP" in protocol_types:
            ftp_export(access_zone_id=access_zone_id, d=i)
        if "SMB" in protocol_types:
            smb_export(access_zone_id=access_zone_id, d=i)

        time.sleep(5)

        """检查NAS服务是否正常"""
        log.info("\t[4. 检查NAS服务是否正常_%s/%s]" % (i, times))
        nas_common.check_nas_status()

        """检查ctdb状态"""
        log.info("\t[4. 查看ctdb状态_%s/%s]" % (i, times))
        cmd = 'ctdb status'
        rc, stdout = common.run_command(node_ip, cmd)
        log.info(stdout)
        if stdout.find("UNHEALTHY") != -1 or stdout.find("DISCONNECTED") != -1 or stdout.find("INACTIVE") != -1:
            common.except_exit("ctdb状态不正常，请检查节点状态")

        """随机选择先关闭 NAS or s3 服务"""
        a = [1, 2]
        b = random.choice(a)
        if b == 1:
            log.info("\t[4. disable_nas_%s/%s]" % (i, times))
            disable_nas(access_zone_id=access_zone_id)
            log.info("\t[4. disable_s3_%s/%s]" % (i, times))
            disable_s3(access_zone_id=access_zone_id)
        elif b == 2:
            log.info("\t[4. disable_s3_%s/%s]" % (i, times))
            disable_s3(access_zone_id=access_zone_id)
            log.info("\t[4. disable_nas_%s/%s]" % (i, times))
            disable_nas(access_zone_id=access_zone_id)
        time.sleep(5)

    return


def enable_nas(access_zone_id, protocol_types):
    msg2 = nas_common.enable_nas(access_zone_id=access_zone_id, protocol_types=protocol_types)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('enable_nas failed!!!')
    return


def enable_s3(access_zone_id):
    msg2 = nas_common.enable_s3(access_zone_id=access_zone_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('enable_s3 failed!!!')
    return


def disable_nas(access_zone_id):
    msg2 = nas_common.disable_nas(access_zone_id=access_zone_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('disable_nas failed!!!')
    return


def disable_s3(access_zone_id):
    msg2 = nas_common.disable_s3(access_zone_id=access_zone_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('disable_s3 failed!!!')
    return


def nfs_export(access_zone_id, d=None):
    # access_zone_id为访问分区的id，d为一个数字，为了区别路导出径名称
    log.info("\t[ 创建nfs导出 ]")
    """创建目录"""
    log.info("\t[ create_file ]")
    m = access_zone_id + d
    nfs_path = nas_common.ROOT_DIR + "nfs_dir_%s" % m
    nas_nfs_path = get_config.get_one_nas_test_path() + "/nfs_dir_%s" % m
    msg6 = nas_common.create_file(path=nfs_path, posix_permission="rwxr-xr-x")
    if msg6["err_msg"] != "" or msg6["detail_err_msg"] != "":
        common.except_exit('create_file failed!!!')

    """ 检查file是否创建成功"""
    log.info("\t[ get_file_list ]")
    msg7 = nas_common.get_file_list(path=nfs_path)
    if msg7["err_msg"] != "" or msg7["detail_err_msg"] != "":
        common.except_exit('get_file_list failed!!!')

    """创建导出路径"""
    log.info("\t[ create_nfs_export ]")
    nfs_export_name = "nfs_export_%s" % m
    description_nfs = 'old_export_description'
    msg1 = nas_common.create_nfs_export(access_zone_id=access_zone_id, export_name=nfs_export_name,
                                        export_path=nfs_path, description=description_nfs)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('create_nfs_export failed!!!')
    nfs_export_id = msg1["result"]

    """添加NFS客户端"""
    log.info("\t[ add_nfs_export_auth_clients ]")
    auth_clients_name = nas_common.NFS_1_CLIENT_IP
    auth_clients_permission_level = 'rw'
    msg = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id, name=auth_clients_name,
                                                 permission_level=auth_clients_permission_level)
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        common.except_exit('add_nfs_export_auth_clients failed!!!')

    """创建一个文件，并写入内容"""
    log.info("\t[ create_file ]")
    cmd = "touch %s/test && echo 'test' > %s/test" % (nas_nfs_path, nas_nfs_path)
    rc, stdout = common.run_command(node_ip, cmd)
    if rc != 0:
        common.except_exit('%s create_file failed!!!' % node_ip)

    """客户端mount共享路径"""
    log.info("\t[ 客户端mount共享路径 ]")
    """2-1> 客户端创建mount路径"""
    log.info("\t[ 客户端创建mount路径 ]")
    auth_clients_path = "/mnt/nfs_dir_client_%s" % m
    cmd = "ls %s" % auth_clients_path
    rc, stdout = common.run_command(auth_clients_name, cmd)
    if stdout == "" or "No such file or directory" not in stdout:
        cmd = "umount -l %s" % auth_clients_path
        common.run_command(auth_clients_name, cmd)
        time.sleep(5)
        cmd = "rm -rf %s" % auth_clients_path
        rc, stdout = common.run_command(auth_clients_name, cmd)
        if rc != 0:
            common.except_exit('%s rm -rf client file failed!!!' % auth_clients_name)
    cmd = "mkdir %s" % auth_clients_path
    rc, stdout = common.run_command(auth_clients_name, cmd)
    if rc != 0:
        common.except_exit('%s create_file failed!!!' % auth_clients_name)

    """2-2> 客户端mount共享路径"""
    log.info("\t[ 客户端mount共享路径 ]")
    begin_time = time.time()
    rc = 1
    while rc != 0:
        cmd1 = "mount -t nfs %s:%s %s" % (node_ip, nas_nfs_path, auth_clients_path)
        rc, stdout = common.run_command(auth_clients_name, cmd1)
        log.info(stdout)
        last_time = time.time()
        during_time = last_time - begin_time
        if int(during_time) >= 31:
            common.except_exit('%s mount file failed and timeout 31s!!!' % auth_clients_name)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (auth_clients_name, cmd1, stdout))
        time.sleep(10)

    """3> 测试r"""
    log.info("\t[ test-r ]")
    cmd1 = "ls %s" % auth_clients_path
    rc, stdout = common.run_command(auth_clients_name, cmd1)
    print stdout
    if rc != 0 or stdout == "":
        common.except_exit('%s test-r failed!!!' % auth_clients_name)

    """4> 测试w"""
    log.info("\t[ test-w ]")
    cmd2 = "touch %s/test2" % auth_clients_path
    rc, stdout = common.run_command(auth_clients_name, cmd2)
    if rc != 0:
        common.except_exit('%s test-w failed!!!' % auth_clients_name)

    """5> 删除test-w的文件"""
    log.info("\t[ 删除test-w的文件 ]")
    cmd1 = "rm -rf %s/test2" % auth_clients_path
    rc, stdout = common.run_command(auth_clients_name, cmd1)
    print stdout
    if rc != 0:
        common.except_exit('%s rm file failed!!!' % auth_clients_name)

    """6> 客户端umount共享路径"""
    log.info("\t[ 客户端umount共享路径 ]")
    cmd1 = "umount -fl %s" % auth_clients_path
    rc, stdout = common.run_command(auth_clients_name, cmd1)
    print stdout
    if rc != 0:
        common.except_exit('%s umount file failed!!!' % auth_clients_name)

    """7> 客户端删除mount路径"""
    log.info("\t[ 客户端删除mount路径 ]")
    cmd1 = "rm -rf %s " % auth_clients_path
    rc, stdout = common.run_command(auth_clients_name, cmd1)
    print stdout
    if rc != 0:
        common.except_exit('%s rm file failed!!!' % auth_clients_name)
    return


def ftp_export(access_zone_id, d=None):
    # access_zone_id为访问分区的id，d为一个数字，为了区别路导出径名称
    log.info("\t[ 创建ftp导出 ]")
    """创建目录"""
    log.info("\t[ create_file ]")
    m = access_zone_id + d
    ftp_path = nas_common.ROOT_DIR + "ftp_dir_%s" % m
    msg6 = nas_common.create_file(path=ftp_path, posix_permission="rwxr-xr-x")
    if msg6["err_msg"] != "" or msg6["detail_err_msg"] != "":
        common.except_exit('create_file failed!!!')

    """ 检查file是否创建成功"""
    log.info("\t[ get_file_list ]")
    msg7 = nas_common.get_file_list(path=ftp_path)
    if msg7["err_msg"] != "" or msg7["detail_err_msg"] != "":
        common.except_exit('get_file_list failed!!!')

    """创建导出路径"""
    log.info("\t[ create_ftp_export ]")
    msg = nas_common.get_access_zones(ids=access_zone_id)
    access_zone_type = msg["result"]["access_zones"][0]["auth_provider"]["type"]
    ftp_user_name = ""
    if access_zone_type == "LDAP":
        ftp_user_name = nas_common.LDAP_USER_1_NAME
    elif access_zone_type == "AD":
        ftp_user_name = nas_common.AD_USER_1
    elif access_zone_type == "NIS":
        ftp_user_name = nas_common.NIS_USER_1
    msg1 = nas_common.create_ftp_export(access_zone_id=access_zone_id, user_name=ftp_user_name, export_path=ftp_path)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('create_ftp_export failed!!!')
    return


def smb_export(access_zone_id, d=None):
    # access_zone_id为访问分区的id，d为一个数字，为了区别路导出径名称
    log.info("\t[ 创建smb导出 ]")
    """创建目录"""
    log.info("\t[ create_file ]")
    m = access_zone_id + d
    smb_path = nas_common.ROOT_DIR + "smb_dir_%s" % m
    msg6 = nas_common.create_file(path=smb_path, posix_permission="rwxr-xr-x")
    if msg6["err_msg"] != "" or msg6["detail_err_msg"] != "":
        common.except_exit('create_file failed!!!')

    """ 检查file是否创建成功"""
    log.info("\t[ get_file_list ]")
    msg7 = nas_common.get_file_list(path=smb_path)
    if msg7["err_msg"] != "" or msg7["detail_err_msg"] != "":
        common.except_exit('get_file_list failed!!!')

    """创建导出路径"""
    log.info("\t[ create_smb_export ]")
    export_name = "smb_export_%s" % m
    msg1 = nas_common.create_smb_export(access_zone_id=access_zone_id, export_name=export_name, export_path=smb_path)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('create_nfs_export failed!!!')
    smb_export_id = msg1["result"]

    """添加SMB客户端"""
    log.info("\t[ add_smb_export_auth_clients ]")
    msg = nas_common.get_access_zones(ids=access_zone_id)
    access_zone_type = msg["result"]["access_zones"][0]["auth_provider"]["type"]
    smb_user_name = ""
    if access_zone_type == "LDAP":
        smb_user_name = nas_common.LDAP_USER_1_NAME
    elif access_zone_type == "AD":
        smb_user_name = nas_common.AD_USER_1
    elif access_zone_type == "NIS":
        smb_user_name = nas_common.NIS_USER_1
    msg = nas_common.add_smb_export_auth_clients(export_id=smb_export_id, name=smb_user_name, user_type="USER",
                                                 run_as_root="true")
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        common.except_exit('add_smb_export_auth_clients failed!!!')
    return


#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    executing_case1()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
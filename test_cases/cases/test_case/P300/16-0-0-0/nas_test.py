# -*- coding:utf-8 -*-

import os
import time

import utils_path
import log
import common
import nas_common
import prepare_clean

# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]


def executing_case():
    """调试专用脚本
    :return:
    """

    # for access_zone
    node_ids = nas_common.get_node_ids()
    access_zone_name = "access_zone_name"
    # for subnet
    subnet_name = "subnet_name"
    ip_family = nas_common.IPv4
    svip = nas_common.SUBNET_SVIP
    subnet_mask = nas_common.SUBNET_MASK
    subnet_gateway = nas_common.SUBNET_GATEWAY
    network_interfaces = nas_common.SUBNET_NETWORK_INTERFACES
    # for vip_pool
    domain_name = nas_common.VIP_DOMAIN_NAME
    vip_addresses = nas_common.VIP_ADDRESSES
    supported_protocol = nas_common.NAS
    allocation_method = nas_common.DYNAMIC
    # for create_dir
    dir_name_list = ["smb", "nfs", "ftp"]
    # for export
    smb_export_name = "smb_export_name"
    nfs_export_name = "nfs_export_name"
    # ftp_export_name = "ftp_export_name"   # 命令中已删除
    smb_export_path = nas_common.ROOT_DIR + dir_name_list[0]
    nfs_export_path = nas_common.ROOT_DIR + dir_name_list[1]
    ftp_export_path = nas_common.ROOT_DIR + dir_name_list[2]
    # for user and group
    auth_group_name = "auth_group_name"
    smb_auth_user_name = "smb_auth_user_name"
    nfs_auth_user_name = "nfs_auth_user_name"
    ftp_auth_user_name = "ftp_auth_user_name"
    auth_user_name_list = [smb_auth_user_name, nfs_auth_user_name, ftp_auth_user_name]
    password = "111111"
    # for export_auth_clients
    smb_export_auth_clients_name = "smb_auth_user_name"   # The authorization user/group name
    smb_run_as_root = "true"
    smb_type = "USER"
    nfs_export_auth_clients_name = "*"
    nfs_permission_level = "rw"

    ###################################################################################

    # 添加鉴权服务器
    check_result = nas_common.add_auth_provider_ad(name="nas_test_ad_auth_name",
                                                   domain_name=nas_common.AD_DOMAIN_NAME,
                                                   dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                                   username=nas_common.AD_USER_NAME,
                                                   password=nas_common.AD_PASSWORD,
                                                   services_for_unix="NONE")
    ad_auth_provider_id = check_result["result"]

    check_result = nas_common.add_auth_provider_ldap(name="nas_test_ldap_auth_name",
                                                     base_dn=nas_common.LDAP_BASE_DN,
                                                     ip_addresses=nas_common.LDAP_IP_ADDRESSES)
    ldap_auth_provider_id = check_result["result"]

    check_result = nas_common.add_auth_provider_nis(name="nas_test_nis_auth_name",
                                                    domain_name=nas_common.NIS_DOMAIN_NAME,
                                                    ip_addresses=nas_common.NIS_IP_ADDRESSES)
    nis_auth_provider_id = check_result["result"]

    # 创建访问区
    check_result = nas_common.create_access_zone(node_ids=node_ids,
                                                 name=access_zone_name)
    if check_result["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    access_zone_id = check_result["result"]

    # 创建子网
    check_result = nas_common.create_subnet(access_zone_id=access_zone_id,
                                            name=subnet_name,
                                            ip_family=ip_family,
                                            svip=svip,
                                            subnet_mask=subnet_mask,
                                            subnet_gateway=subnet_gateway,
                                            network_interfaces=network_interfaces)
    if check_result["detail_err_msg"] != "":
        log.error("%s Failed" % FILE_NAME)
        raise Exception("%s Failed" % FILE_NAME)
    subnet_id = check_result["result"]

    # 创建vip池
    check_result = nas_common.add_vip_address_pool(subnet_id=subnet_id,
                                                   domain_name=domain_name,
                                                   vip_addresses=vip_addresses,
                                                   supported_protocol=supported_protocol,
                                                   allocation_method=allocation_method)
    if check_result["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)

    # enable_nas
    enable_start_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    log.info(enable_start_time)
    check_result = nas_common.enable_nas(access_zone_id=access_zone_id)
    if check_result["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    enable_end_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    log.info(enable_end_time)

    # 创建目录
    for dir_name in dir_name_list:
        create_file_path = nas_common.ROOT_DIR + dir_name
        check_result = nas_common.create_file(path=create_file_path)
        if check_result["detail_err_msg"] != "":
            log.error("%s Failed" % FILE_NAME)
            # raise Exception(("%s Failed") % FILE_NAME)

    # 导出目录
    check_result = nas_common.create_smb_export(access_zone_id=access_zone_id,
                                                export_name=smb_export_name,
                                                export_path=smb_export_path)
    if check_result["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    smb_export_id = check_result["result"]

    check_result = nas_common.create_nfs_export(access_zone_id=access_zone_id,
                                                export_name=nfs_export_name,
                                                export_path=nfs_export_path)
    if check_result["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    nfs_export_id = check_result["result"]

    check_result = nas_common.create_ftp_export(access_zone_id=access_zone_id,
                                                user_name=ftp_auth_user_name,
                                                export_path=ftp_export_path)
    if check_result["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)

    # 获取local_auth_provider_id
    msg = nas_common.get_access_zones(ids=access_zone_id)
    if msg["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    local_auth_provider_id = msg['result']['access_zones'][0]['local_auth_provider_id']

    # 创建本地用户、用户组
    check_result = nas_common.create_auth_group(auth_provider_id=local_auth_provider_id,
                                                name=auth_group_name)
    if check_result["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    group_id = check_result["result"]

    for name in auth_user_name_list:
        check_result = nas_common.create_auth_user(auth_provider_id=local_auth_provider_id,
                                                   name=name,
                                                   password=password,
                                                   primary_group_id=group_id)
        if check_result["detail_err_msg"] != "":
            raise Exception("%s Failed" % FILE_NAME)

    # 添加NAS客户端
    check_result = nas_common.add_smb_export_auth_clients(export_id=smb_export_id,
                                                          name=smb_export_auth_clients_name,
                                                          run_as_root=smb_run_as_root,
                                                          user_type=smb_type)
    if check_result["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)

    check_result = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id,
                                                          name=nfs_export_auth_clients_name,
                                                          permission_level=nfs_permission_level)
    if check_result["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)

    # # nfs客户端挂载
    # time.sleep(60)
    # node_ip = "10.2.40.77"
    # cmd = "mount -t nfs 20.10.10.49:/mnt/a/nfs /mnt/jiangxg"
    # rc, stdout, stderr = shell.ssh(node_ip, cmd)
    # if rc != 0:
    #     log.info("rc = %s" % (rc))
    #     log.info("WARNING: \ncmd = %s\nstdout = %s\nstderr = %s" % (cmd, stdout, stderr))
    # log.info(stdout)
    # if stdout != "" or stderr != "":
    #     raise Exception("%s Failed" % FILE_NAME)

    return


def nas_main():
    """脚本入口函数
    :return:无
    """
    prepare_clean.nas_test_prepare(FILE_NAME)
    executing_case()
    if nas_common.DEBUG != 'on':
        prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)

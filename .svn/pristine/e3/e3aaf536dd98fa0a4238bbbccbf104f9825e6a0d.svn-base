#!/usr/bin/python
# -*-coding:utf-8 -*

import os
import subprocess
import sys
import traceback
import datetime

import requests
import time
import logging
import inspect

import utils_path
import get_config
import common
import nas_common
import prepare_clean
import create_s3_xml


##########################################################################
#
# Author: zhanghan
# date 2019-02-17
# @summary：
#    可靠性测试环境准备工作
# @steps:
#    1、添加文件系统
#    2、添加访问区（启动相关服务）
#    3、添加业务子网（包含nas和s3的域名）
#    4、配置私有客户端和nfs客户端协议，并在相应的客户端进行挂载；

#
# @changelog：
##########################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]                 # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
log_prepare = None

# 类实例化
posix_auth = common.Clientauth()
vol = common.Volume()
storpool = common.Storagepool()
node = common.Node()

# 公用函数


def excute_command(cmd):
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    while True:
        line = process.stdout.readline()
        if '' == line:
            break
        log_prepare.debug(line.rstrip())
    process.wait()
    if process.returncode == 0:
        return 0
    else:
        return -1


def except_exit(info=None, error_code=1):
    """
    :author:            zhanghan
    :date  :            2019.02.17
    :description:       异常退出脚本
    :param error_code:  异常退出码
    :return:
    """
    if info is not None:
        log_error(info)
    log_error(''.join(traceback.format_stack()))
    sys.exit(error_code)


def log_init(case_log_path):
    """
    日志解析
    """
    global log_prepare

    file_name = os.path.basename(__file__)
    file_name = file_name.split('.')[0]
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    log_file_name = now_time + '_' + file_name + '.log'
    log_file_path = os.path.join(case_log_path, log_file_name)

    log_prepare = logging.getLogger(name='log_prepare')
    log_prepare.setLevel(level=logging.INFO)

    handler = logging.FileHandler(log_file_path, mode='a')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(levelname)s][%(asctime)s]   %(message)s',
        '%y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(levelname)s][%(asctime)s]   %(message)s',
        '%y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)

    log_prepare.addHandler(console)
    log_prepare.addHandler(handler)

    return


def log_error(msg, exc_info=True):
    global log_prepare
    if log_prepare is None:
        return
    current_time = datetime.datetime.now()
    currenttime = current_time.strftime('%y-%m-%d %H:%M:%S')

    caller_frame = inspect.stack()[1]
    frame = caller_frame[0]
    info = inspect.getframeinfo(frame)
    prefix_str = '[ERROR][%s]%s:%d:%s()' % \
                 (currenttime,
                  os.path.basename(info.filename),
                  info.lineno,
                  info.function)
    msg = '%-70s%s' % (prefix_str, msg)
    log_prepare.error(msg, exc_info=exc_info)


def create_dir(ip, dir_name):
    cmd = "ssh %s \"if [ ! -d \"%s\" ];then mkdir -p %s;fi \"" % (
        ip, dir_name, dir_name)
    rc = excute_command(cmd)
    return rc


# posix客户端
def get_volume_id(volume_name):
    volume_id = vol.get_volume_id(volume_name)
    return volume_id


def authorize_posix_client(
        volume_name,
        ip,
        auto_mount='true',
        atime='false',
        acl='true',
        user_xattr='true',
        sync='true',
        desc=None):
    volume_id = get_volume_id(volume_name)
    (rc, stdout) = posix_auth.create_client_auth(
        ip, volume_id, auto_mount, atime, acl, user_xattr, sync, desc)
    return (rc, stdout)


def mount_posix_client(
        client_ip,
        posix_scripts_dir,
        posix_install_script,
        cluster_ip):
    cmd = "ssh %s \"cd %s;python %s --ips=%s\"" % (
        client_ip, posix_scripts_dir, posix_install_script, cluster_ip)
    rc = excute_command(cmd)
    return rc


def posix_authorize_and_mount(
        cluster_ip,
        volume_name,
        posix_ip,
        posix_scripts_dir,
        posix_install_script):
    """
    :param cluster_ip: Required:True   Type:str     Help:ip of one of cluster node
    :param volume_name: Required:True   Type:str     Help:name of volume to be authorize
    :param posix_ip: Required:True   Type:str     Help:ip of posix client to be authorize
    :param posix_scripts_dir: Required:True   Type:str     Help:the dir path of the script that used to install posix client
    :param posix_install_script: Required:True   Type:str     Help:the script name that used to install posix client
    :return:
    """

    log_prepare.info("\t[ add posix authorization ]")
    (rc_auth_posix, stdout_auth_posix) = authorize_posix_client(volume_name, posix_ip)
    if 0 != rc_auth_posix:
        except_exit("\t authorize posix client %s failed" % posix_ip)
    else:
        log_prepare.info("\t authorize posix client %s success" % posix_ip)

    log_prepare.info("\t[ mount posix client ]")
    rc_mount_posix = mount_posix_client(
        posix_ip,
        posix_scripts_dir,
        posix_install_script,
        cluster_ip)
    if 0 != rc_mount_posix:
        except_exit("\t mount posix client %s failed" % posix_ip)
    else:
        log_prepare.info("\t mount posix client %s success" % posix_ip)

    return


# nfs客户端
def get_access_zone_id(access_zone_name):
    access_zone_info = nas_common.get_access_zones()
    access_zone_info = access_zone_info["result"]["access_zones"]
    access_zone_id = ''
    for access_zone_tmp in access_zone_info:
        if access_zone_name in access_zone_tmp["name"]:
            access_zone_id = access_zone_tmp["id"]
    if '' == access_zone_id:
        except_exit("\t get access_zone_id failed")
    return access_zone_id


def get_nfs_export_id(export_name):
    nfs_export_msg = nas_common.get_nfs_exports()
    nfs_export_msg = nfs_export_msg["result"]["exports"]
    nfs_export_id = ""
    for nfs_info in nfs_export_msg:
        if export_name in nfs_info["export_name"]:
            nfs_export_id = nfs_info["id"]
    if '' == nfs_export_id:
        except_exit("\t get access_zone_id failed")
    return nfs_export_id


def authorize_nfs_client(
        cluster_ip,
        access_zone_name,
        export_name,
        export_path):
    access_zone_id = get_access_zone_id(access_zone_name)
    volume_name = export_path.split(":")[0]
    dir_path = export_path.split(":")[1][1:]
    mount_path = os.path.join("/mnt", volume_name)
    final_path = os.path.join(mount_path, dir_path)
    rc = create_dir(cluster_ip, final_path)
    if 0 != rc:
        except_exit("\t ip:%s, create %s failed" % (cluster_ip, final_path))
    res = nas_common.create_nfs_export(
        access_zone_id,
        export_name,
        export_path,
        description=None,
        print_flag=True,
        fault_node_ip=None)
    return_code = 0
    if '' == res["err_msg"]:
        pass
    else:
        return_code = 1
    return return_code


def add_nfs_client(
        export_name,
        name="*",
        permission_level="rw",
        write_mode="sync",
        port_constraint="secure",
        permission_constraint="no_root_squash"):
    nfs_export_id = get_nfs_export_id(export_name)
    msg = nas_common.add_nfs_export_auth_clients(
        nfs_export_id,
        name,
        permission_level,
        write_mode,
        port_constraint,
        permission_constraint)
    return msg


def nfs_mount(nfs_ip, vip_domain_name, mount_path, nfs_mount_path):
    rc = create_dir(nfs_ip, nfs_mount_path)
    if 0 != rc:
        except_exit("\t ip:%s, create %s failed" % (nfs_ip, nfs_mount_path))
    cmd = "ssh %s \"mount -t nfs %s:%s %s\"" % (
        nfs_ip, vip_domain_name, mount_path, nfs_mount_path)
    rc = excute_command(cmd)
    return rc


def nfs_authorize_and_mount(
        cluster_ip,
        nfs_ip,
        vip_domain_name,
        access_zone_name,
        export_path,
        nfs_export_name,
        nfs_mount_path):
    """
    :param cluster_ip: Required:True   Type:str     Help:ip of one of cluster node
    :param nfs_ip: Required:True   Type:str     Help:the ip of nfs client that to be authorize and mount
    :param vip_domain_name: Required:True   Type:str     Help:domain name of nas vip pools
    :param access_zone_name: Required:True   Type:str     Help:access zone name
    :param export_path: Required:True   Type:str     Help:export path. e.g. volume:/export/dir
    :param nfs_export_name: Required:True   Type:str     Help:nfs export name
    :param nfs_mount_path: Required:True   Type:str     Help:nfs mount path
    :return:
    """

    log_prepare.info("\t[ add nfs authorization ]")
    rc_auth = authorize_nfs_client(
        cluster_ip,
        access_zone_name,
        nfs_export_name,
        export_path)
    if 0 != rc_auth:
        except_exit("\t add nfs authorization '%s' failed" % nfs_export_name)
    log_prepare.info(
        "\t add nfs authorization success, nfs_export_name is %s, export_path is %s" %
        (nfs_export_name, export_path))

    log_prepare.info("\t[ add nfs client ]")
    msg_add_client = add_nfs_client(nfs_export_name)
    if '' != msg_add_client["err_msg"]:
        except_exit("\t add nfs client failed")
    else:
        log_prepare.info(
            "\t add nfs client success, nfs_export_name is %s " %
            nfs_export_name)

    log_prepare.info("\t[ mount nfs client ]")
    time.sleep(5)
    subdir = export_path.split(':')[-1][1:]
    volume_name = export_path.split(':')[0]
    parastor_export_path = os.path.join("/mnt", volume_name, subdir)
    rc_mount = nfs_mount(
        nfs_ip,
        vip_domain_name,
        parastor_export_path,
        nfs_mount_path)
    if 0 != rc_mount:
        except_exit("\t mount nfs client failed")
    log_prepare.info(
        "\t nfs mount success, nfs_ip is %s, nfs_mount_path is %s, parastor_export_path is %s, vip_domain_name is %s" %
        (nfs_ip, nfs_mount_path, parastor_export_path, vip_domain_name))

    return

# 添加文件系统


def create_volume(
        volume_name,
        storage_pool_id,
        stripe_width,
        disk_parity_num,
        node_parity_num,
        replica_num):
    log_prepare.info("\t[ create volume ]")
    (rc, json_info) = vol.create_volume(volume_name, storage_pool_id,
                                        stripe_width, disk_parity_num, node_parity_num, replica_num)
    if 0 != rc:
        except_exit("\t create volume %s failed" % volume_name)
    else:
        log_prepare.info("\t create volume '%s' success" % volume_name)
    return (rc, json_info)

# 创建访问区并激活nas


def add_accesszone_and_enableservice(
        access_zone_node_ids,
        access_zone_name,
        auth_provider_id=None,
        enable_NAS=True,
        protocol_types=None,
        enable_S3=True):
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
    log_prepare.info("\t[ create access zone ]")
    msg1 = nas_common.create_access_zone(
        node_ids=access_zone_node_ids,
        name=access_zone_name,
        auth_provider_id=auth_provider_id)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        except_exit('\t create_access_zone failed!!!')
    log_prepare.info("\t create access zone '%s' success" % access_zone_name)
    access_zone_id = msg1["result"]

    if enable_NAS:
        log_prepare.info("\t[ enable NAS ]")
        msg2 = nas_common.enable_nas(
            access_zone_id=access_zone_id,
            protocol_types=protocol_types)
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            except_exit('\t enable_nas failed!!!')
        log_prepare.info(
            "\t access zone '%s', enable NAS success" %
            access_zone_name)
    else:
        pass
    if enable_S3:
        log_prepare.info("\t[ enable S3 ]")
        msg3 = nas_common.enable_s3(access_zone_id=access_zone_id)
        if msg3["err_msg"] != "" or msg3["detail_err_msg"] != "":
            except_exit('\t enable_s3 failed!!!')
        log_prepare.info(
            "\t access zone '%s', enable S3 success" %
            access_zone_name)
    else:
        pass
    return access_zone_id


# 创建svip和ip池
def create_svip_and_vippool(
        access_zone_id,
        svip,
        subnet_mask,
        network_interfaces,
        vip_domain_name,
        vip_vip_addresses,
        vip_supported_protocol,
        vip_load_balance_policy="LB_CONNECTION_COUNT",
        vip_ip_failover_policy="IF_ROUND_ROBIN",
        vip_rebalance_policy="RB_AUTOMATIC",
        subnet_gateway=None,
        mtu=None):
    """
    :创建业务子网并添加vip池
    :return vip_domain_name
    """
    log_prepare.info("\t[  create subnet ]")
    sub_name = "%s_subnet_%s" % (vip_supported_protocol, access_zone_id)
    msg1 = nas_common.create_subnet(access_zone_id=access_zone_id,
                                    name=sub_name,
                                    ip_family=nas_common.IPv4,
                                    svip=svip,
                                    subnet_mask=subnet_mask,
                                    subnet_gateway=subnet_gateway,
                                    network_interfaces=network_interfaces,
                                    mtu=mtu)

    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        except_exit('\t create_subnet failed!!!')
    log_prepare.info("\t create subnet '%s' success" % svip)
    subnet_id = msg1["result"]

    if vip_supported_protocol == 'S3':
        vip_load_balance_policy = "LB_ROUND_ROBIN"
        vip_ip_failover_policy = "IF_ROUND_ROBIN"
    log_prepare.info("\t[  create vip pool ]")
    msg1 = nas_common.add_vip_address_pool(
        subnet_id=subnet_id,
        domain_name=vip_domain_name,
        vip_addresses=vip_vip_addresses,
        supported_protocol=vip_supported_protocol,
        allocation_method='DYNAMIC',
        load_balance_policy=vip_load_balance_policy,
        ip_failover_policy=vip_ip_failover_policy,
        rebalance_policy=vip_rebalance_policy)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        except_exit('\t add_vip_address_pool failed!!!')
    log_prepare.info(
        "\t create vip_pool '%s:%s' success" %
        (vip_domain_name, vip_vip_addresses))
    vip_address_pool_id = msg1['result']
    msg1 = nas_common.get_vip_address_pools(ids=vip_address_pool_id)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        except_exit('\t get_vip_address_pools failed!!!')
    domain_name = msg1['result']['ip_address_pools'][0]['domain_name']
    return domain_name


def prepare_environment(
        log_path,
        file_storage_pool_name,
        nfs_export_name=None,
        volume_name_nas=None,
        volume_name_posix=None,
        access_zone_name=None,
        svip_s3=None,
        svip_nas=None,
        subnet_mask=None,
        network_interfaces_s3=None,
        network_interfaces_nas=None,
        vip_domain_name_s3=None,
        vip_domain_name_nas=None,
        vip_vip_addresses_s3=None,
        vip_vip_addresses_nas=None,
        vip_supported_protocol=None,
        nfs_ip=None,
        nfs_mount_path=None,
        cluster_ip=None,
        export_path=None,
        client_ip=None,
        stripe_width=4,
        disk_parity_num=2,
        node_parity_num=1,
        replica_num=1):
    """
    :param log_path: Required:True   Type:string  Help:The log path of this script, e.g. 1,2,3
    :param file_storage_pool_name: Required:True   Type:string  Help:The name of FILE type storage pool, e.g. filestorage
    :param nfs_export_name: Required:False   Type:string  Help:The name of nfs export, e.g. nfsexport
    :param volume_name_nas: Required:False   Type:string  Help:The name of nas volume, e.g. parastor_nas
    :param volume_name_posix: Required:False   Type:string  Help:The name of posix volume, e.g. parastor_posix
    :param access_zone_name: Required:False   Type:string  Help:The name of access zone, e.g. access_zone
    :param svip_s3: Required:False   Type:string  Help:svip for s3, e.g. 10.2.42.100
    :param svip_nas: Required:False   Type:string  Help:svip for nas, e.g. 10.2.42.100
    :param subnet_mask: Required:False   Type:int  Help:Subnet mask of the subnet, range:(0, 32]. e.g. 22
    :param network_interfaces_s3: Required:False   Type:string  Help:Network interface list of the s3 subnet. e.g. eth0,eth1
    :param network_interfaces_nas: Required:False   Type:string  Help:Network interface list of the nas subnet. e.g. eth2,eth3
    :param vip_domain_name_s3: Required:False   Type:string  Help:The domain name of s3 vip address pool.
    :param vip_domain_name_nas: Required:False   Type:string  Help:The domain name of nas vip address pool.
    :param vip_vip_addresses_s3: Required:False   Type:string  Help:Allow single IP and IP segment, separate by comma. e.g.10.0.0.1-5,10.0.0.10
    :param vip_vip_addresses_nas: Required:False   Type:string  Help:Allow single IP and IP segment, separate by comma. e.g.20.0.0.1-5,20.0.0.10
    :param vip_supported_protocol: Required:False   Type:string  Help:Supported protocol of the vip address pool. Available supported protocol: ['S3', 'NAS', 'ISCSI']
    :param nfs_ip: Required:False   Type:string  Help:the ip of nfs client. e.g. 10.2.42.79
    :param nfs_mount_path: Required:False   Type:string  Help:the mount path of nfs client. e.g. /mnt/nfs
    :param cluster_ip: Required:False   Type:string  Help:ip of one cluster node. e.g. 10.2.42.65
    :param export_path: Required:False   Type:string  Help:The nfs export path. e.g. parastor_nas:/
    :param client_ip: Required:False   Type:string  Help:posix client ip. Should be in the same network segment with data network. e.g. 20.2.42.80
    :param stripe_width: Required:False   Type:int  Help:stripe_width. e.g. 4
    :param disk_parity_num: Required:False   Type:int  Help:disk_parity_num. e.g. 2
    :param node_parity_num: Required:False   Type:int  Help:node_parity_num. e.g. 1
    :param replica_num: Required:False   Type:int  Help:replica_num. e.g. 1
    :return:
    """

    # 日志初始化
    log_init(log_path)

    # 参数获取
    if None == nfs_ip:
        nfs_ip = get_config.get_nfs_client_ip()[0]
    if None == vip_domain_name_s3:
        vip_domain_name_s3 = get_config.get_vip_domain_name()[0]
    if None == vip_domain_name_nas:
        vip_domain_name_nas = get_config.get_vip_domain_name()[1]
    if None == cluster_ip:
        cluster_ip = get_config.get_parastor_ip()
    if None == access_zone_name:
        access_zone_name = get_config.get_access_zone_name()[0]
    if None == volume_name_nas:
        volume_name_nas = "parastor_nas"
    if None == volume_name_posix:
        volume_name_posix = "parastor_posix"
    if None == export_path:
        export_path = volume_name_nas + ':' + '/'
    if None == nfs_export_name:
        nfs_export_name = "nfs_export"
    if None == nfs_mount_path:
        nfs_mount_path = os.path.join('/mnt', volume_name_nas)
    if None == client_ip:
        client_ip = get_config.get_client_ip()
    if None == svip_s3:
        svip_s3 = get_config.get_subnet_svip()[0]
    if None == svip_nas:
        svip_nas = get_config.get_subnet_svip()[1]
    if None == subnet_mask:
        subnet_mask = int(get_config.get_subnet_mask()[0])
    if None == network_interfaces_s3:
        network_interfaces_s3 = get_config.get_subnet_network_interface()[0]
    if None == network_interfaces_nas:
        network_interfaces_nas = get_config.get_subnet_network_interface()[1]
    if None == vip_vip_addresses_s3:
        vip_vip_addresses_s3 = get_config.get_vip_addresses()[-1]
    if None == vip_vip_addresses_nas:
        vip_vip_addresses_nas = get_config.get_vip_addresses()[-2]
    if None == vip_supported_protocol:
        vip_supported_protocol = get_config.get_vip_supported_protocol()[0]

    # 其它参数
    posix_scripts_dir = get_config.get_client_install_path()
    posix_install_script = "install.py"
    storage_pool_id = storpool.get_storagepool_id(file_storage_pool_name)[1]
    access_zone_node_id_list = node.get_nodes_id()
    access_zone_node_ids = ''
    for item in access_zone_node_id_list:
        access_zone_node_ids = access_zone_node_ids + str(item) + ','
    access_zone_node_ids = access_zone_node_ids[:-1]

    ##########函数执行##########
    # 步骤1：创建文件系统
    log_prepare.info("Step 1> 添加文件系统（nas文件系统和posix文件系统）")
    create_volume(
        volume_name_nas,
        storage_pool_id,
        stripe_width,
        disk_parity_num,
        node_parity_num,
        replica_num)

    create_volume(
        volume_name_posix,
        storage_pool_id,
        stripe_width,
        disk_parity_num,
        node_parity_num,
        replica_num)

    # 步骤2：创建访问区并启动相关服务（nas/s3服务）
    log_prepare.info("Step 2> 添加访问区（启动相关服务）")
    add_accesszone_and_enableservice(access_zone_node_ids, access_zone_name)

    # 步骤3：添加业务子网
    log_prepare.info("Step 3> 添加业务子网（包含nas和s3的域名）")
    access_zone_id = get_access_zone_id(access_zone_name)
    create_svip_and_vippool(
        access_zone_id,
        svip_s3,
        subnet_mask,
        network_interfaces_s3,
        vip_domain_name_s3,
        vip_vip_addresses_s3,
        vip_supported_protocol,
        vip_load_balance_policy="LB_CONNECTION_COUNT",
        vip_ip_failover_policy="IF_ROUND_ROBIN",
        vip_rebalance_policy="RB_AUTOMATIC")

    create_svip_and_vippool(
        access_zone_id,
        svip_nas,
        subnet_mask,
        network_interfaces_nas,
        vip_domain_name_nas,
        vip_vip_addresses_nas,
        vip_supported_protocol='NAS',
        vip_load_balance_policy="LB_CONNECTION_COUNT",
        vip_ip_failover_policy="IF_ROUND_ROBIN",
        vip_rebalance_policy="RB_AUTOMATIC")

    # 步骤4：配置私有客户端和nfs客户端协议，并在相应的客户端进行挂载
    log_prepare.info("Step 4> 配置私有客户端和nfs客户端协议，并在相应的客户端进行挂载")
    nfs_authorize_and_mount(
        cluster_ip,
        nfs_ip,
        vip_domain_name_nas,
        access_zone_name,
        export_path,
        nfs_export_name,
        nfs_mount_path)

    posix_authorize_and_mount(
        cluster_ip,
        volume_name_posix,
        client_ip,
        posix_scripts_dir,
        posix_install_script)


def main():
    log_path = "/home/StorTest/test_cases/log/case_log"
    file_storage_pool_name = "storage"
    nfs_export_name = "nfsfinal"

    prepare_environment(log_path, file_storage_pool_name, nfs_export_name)


if __name__ == '__main__':
    common.case_main(main)

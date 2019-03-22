#!/usr/bin/python
# -*-coding:utf-8 -*

import os
import subprocess
import sys
import traceback
import datetime

import time
import logging
import inspect

import utils_path
import get_config
import common
import nas_common
import P300_AutoInstall
import log
import shell

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


class Prepare_all(object):
    def __init__(self,):

        self.nfs_ip = get_config.get_nfs_client_ip()[0]
        self.vip_domain_name_s3 = get_config.get_vip_domain_name()[0]
        self.vip_domain_name_nas = get_config.get_vip_domain_name()[1]
        self.cluster_ip = get_config.get_parastor_ip()
        self.access_zone_name = get_config.get_access_zone_name()[0]
        self.volume_name_nas = get_config.get_volume_names()[0]
        self.export_path = self.volume_name_nas + ':' + '/'
        self.nfs_export_name = "nfs_export"
        self.nfs_mount_path = os.path.join('/mnt', self.volume_name_nas)
        self.client_ip = get_config.get_client_ip()
        self.svip_s3 = get_config.get_subnet_svip()[0]
        self.subnet_mask = int(get_config.get_subnet_mask()[0])
        self.network_interfaces_s3 = get_config.get_subnet_network_interface()[0]
        self.vip_vip_addresses_s3 = get_config.get_vip_addresses()[-1]
        self.vip_vip_addresses_nas = get_config.get_vip_addresses()[-2]
        self.ip_family = get_config.get_ip_family()[0]
        self.svip_num = get_config.get_svip_num_param()
        if 2 == self.svip_num:
            self.svip_nas = get_config.get_subnet_svip()[1]
            self.network_interfaces_nas = get_config.get_subnet_network_interface()[1]
        else:
            self.svip_nas = None
            self.network_interfaces_nas = None

    # 公用函数

    def excute_command(self, cmd):
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

    def run_command(self, node_ip, cmd, print_flag=True, timeout=None):
        """
        :author:           baoruobing
        :date  :           2018.07.28
        :description:      执行命令的函数
        :param node_ip:    节点ip
        :param cmd:        要执行的命令
        :param print_flag: 是否需要打印执行的命令和命令执行的结果,默认值:打印
        :param timeout:    命令超时时间
        :return:
        """
        info_str = "node: %s   cmd: %s" % (node_ip, cmd)
        log_prepare.info(info_str)
        rc, stdout, stderr = shell.ssh(node_ip, cmd, timeout)
        if 0 != rc:
            log_prepare.info(
                "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" %
                (cmd, stdout, stderr))
            if stdout != '':
                return rc, stdout
            else:
                return rc, stderr
        elif '' != stdout and print_flag is True:
            log_prepare.info(stdout)
        return rc, stdout

    def except_exit(self, info=None, error_code=1):
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

    def create_dir(self, ip, dir_name):
        cmd = "ssh %s \"if [ ! -d \"%s\" ];then mkdir -p %s;fi \"" % (
            ip, dir_name, dir_name)
        rc = self.excute_command(cmd)
        return rc

    # posix客户端

    def get_volume_id(self, volume_name):
        volume_id = vol.get_volume_id(volume_name)
        return volume_id

    def authorize_posix_client(
            self,
            volume_name,
            ip,
            auto_mount='true',
            atime='false',
            acl='true',
            user_xattr='true',
            sync='true',
            desc=None):
        volume_id = self.get_volume_id(volume_name)
        (rc, stdout) = posix_auth.create_client_auth(
            ip, volume_id, auto_mount, atime, acl, user_xattr, sync, desc)
        return (rc, stdout)

    def mount_posix_client(
            self,
            client_ip,
            posix_scripts_dir,
            posix_install_script,
            cluster_ip):
        cmd = "ssh %s \"cd %s;python %s --ips=%s\"" % (
            client_ip, posix_scripts_dir, posix_install_script, cluster_ip)
        rc = self.excute_command(cmd)
        return rc

    def posix_authorize_and_mount(
            self,
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
        (rc_auth_posix, stdout_auth_posix) = self.authorize_posix_client(
            volume_name, posix_ip)
        if 0 != rc_auth_posix:
            self.except_exit("\t authorize posix client %s failed" % posix_ip)
        else:
            log_prepare.info("\t authorize posix client %s success" % posix_ip)

        log_prepare.info("\t[ mount posix client ]")
        rc_mount_posix = self.mount_posix_client(
            posix_ip,
            posix_scripts_dir,
            posix_install_script,
            cluster_ip)
        if 0 != rc_mount_posix:
            self.except_exit("\t mount posix client %s failed" % posix_ip)
        else:
            log_prepare.info("\t mount posix client %s success" % posix_ip)

        return

    # nfs客户端

    def get_access_zone_id(self, access_zone_name):
        access_zone_info = nas_common.get_access_zones()
        access_zone_info = access_zone_info["result"]["access_zones"]
        access_zone_id = ''
        for access_zone_tmp in access_zone_info:
            if access_zone_name in access_zone_tmp["name"]:
                access_zone_id = access_zone_tmp["id"]
        if '' == access_zone_id:
            self.except_exit("\t get access_zone_id failed")
        return access_zone_id

    def get_nfs_export_id(self, export_name):
        nfs_export_msg = nas_common.get_nfs_exports()
        nfs_export_msg = nfs_export_msg["result"]["exports"]
        nfs_export_id = ""
        for nfs_info in nfs_export_msg:
            if export_name in nfs_info["export_name"]:
                nfs_export_id = nfs_info["id"]
        if '' == nfs_export_id:
            self.except_exit("\t get access_zone_id failed")
        return nfs_export_id

    def authorize_nfs_client(
            self,
            cluster_ip,
            access_zone_name,
            export_name,
            export_path):
        access_zone_id = self.get_access_zone_id(access_zone_name)
        volume_name = export_path.split(":")[0]
        dir_path = export_path.split(":")[1][1:]
        mount_path = os.path.join("/mnt", volume_name)
        final_path = os.path.join(mount_path, dir_path)
        rc = self.create_dir(cluster_ip, final_path)
        if 0 != rc:
            self.except_exit(
                "\t ip:%s, create %s failed" %
                (cluster_ip, final_path))
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
            self,
            export_name,
            name="*",
            permission_level="rw",
            write_mode="sync",
            port_constraint="secure",
            permission_constraint="no_root_squash"):
        nfs_export_id = self.get_nfs_export_id(export_name)
        msg = nas_common.add_nfs_export_auth_clients(
            nfs_export_id,
            name,
            permission_level,
            write_mode,
            port_constraint,
            permission_constraint)
        return msg

    def umount_nfs(self, nfs_ip, nfs_mount_path):
        cmd = "umount -l %s" % nfs_mount_path
        rc, stdout = self.run_command(nfs_ip, cmd, print_flag=True)
        return rc, stdout

    def nfs_mount(self, nfs_ip, vip_domain_name, mount_path, nfs_mount_path):
        rc = self.create_dir(nfs_ip, nfs_mount_path)
        if 0 != rc:
            self.except_exit(
                "\t ip:%s, create %s failed" %
                (nfs_ip, nfs_mount_path))
        cmd = "mount -t nfs %s:%s %s" % (vip_domain_name,
                                         mount_path, nfs_mount_path)
        rc, stdout = self.run_command(nfs_ip, cmd, print_flag=True, timeout=60)
        return rc, stdout

    def nfs_authorize_and_mount(
            self,
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
        rc_auth = self.authorize_nfs_client(
            cluster_ip,
            access_zone_name,
            nfs_export_name,
            export_path)
        if 0 != rc_auth:
            self.except_exit(
                "\t add nfs authorization '%s' failed" %
                nfs_export_name)
        log_prepare.info(
            "\t add nfs authorization success, nfs_export_name is %s, export_path is %s" %
            (nfs_export_name, export_path))

        log_prepare.info("\t[ add nfs client ]")
        msg_add_client = self.add_nfs_client(nfs_export_name)
        if '' != msg_add_client["err_msg"]:
            self.except_exit("\t add nfs client failed")
        else:
            log_prepare.info(
                "\t add nfs client success, nfs_export_name is %s " %
                nfs_export_name)

        log_prepare.info("\t[ mount nfs client ]")
        time.sleep(5)
        subdir = export_path.split(':')[-1][1:]
        volume_name = export_path.split(':')[0]
        parastor_export_path = os.path.join("/mnt", volume_name, subdir)
        self.umount_nfs(nfs_ip, nfs_mount_path)
        time.sleep(5)
        rc_mount, stdout = self.nfs_mount(
            nfs_ip,
            vip_domain_name,
            parastor_export_path,
            nfs_mount_path)
        if 0 != rc_mount:
            self.except_exit("\t mount nfs client failed")
        log_prepare.info(
            "\t nfs mount success, nfs_ip is %s, nfs_mount_path is %s, parastor_export_path is %s, vip_domain_name is %s" %
            (nfs_ip, nfs_mount_path, parastor_export_path, vip_domain_name))

        return


    # 创建访问区并激活nas
    def add_accesszone_and_enableservice(
            self,
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
            self.except_exit('\t create_access_zone failed!!!')
        log_prepare.info(
            "\t create access zone '%s' success" %
            access_zone_name)
        access_zone_id = msg1["result"]

        if enable_NAS:
            log_prepare.info("\t[ enable NAS ]")
            msg2 = nas_common.enable_nas(
                access_zone_id=access_zone_id,
                protocol_types=protocol_types)
            if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
                self.except_exit('\t enable_nas failed!!!')
            log_prepare.info(
                "\t access zone '%s', enable NAS success" %
                access_zone_name)
        else:
            pass
        if enable_S3:
            log_prepare.info("\t[ enable S3 ]")
            msg3 = nas_common.enable_s3(access_zone_id=access_zone_id)
            if msg3["err_msg"] != "" or msg3["detail_err_msg"] != "":
                self.except_exit('\t enable_s3 failed!!!')
            log_prepare.info(
                "\t access zone '%s', enable S3 success" %
                access_zone_name)
        else:
            pass
        return access_zone_id

    def create_svip(
            self,
            access_zone_id,
            sub_name,
            ip_family,
            svip,
            subnet_mask,
            network_interfaces,
            subnet_gateway=None,
            mtu=None):
        log_prepare.info("\t[  create subnet ]")
        msg1 = nas_common.create_subnet(
            access_zone_id,
            sub_name,
            ip_family,
            svip,
            subnet_mask,
            network_interfaces)
        if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
            self.except_exit('\t create_subnet failed!!!')
        log_prepare.info("\t create subnet '%s' success" % svip)
        return msg1

    def create_vip_address_pool(
            self,
            subnet_id,
            vip_domain_name,
            vip_vip_addresses,
            vip_supported_protocol,
            allocation_method='DYNAMIC',
            vip_load_balance_policy='LB_ROUND_ROBIN',
            vip_ip_failover_policy="IF_ROUND_ROBIN",
            vip_rebalance_policy="RB_AUTOMATIC"):
        log_prepare.info("\t[  create vip pool ]")
        msg1 = nas_common.add_vip_address_pool(
            subnet_id,
            vip_domain_name,
            vip_vip_addresses,
            vip_supported_protocol,
            allocation_method)
        if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
            self.except_exit('\t add_vip_address_pool failed!!!')
        log_prepare.info(
            "\t create vip_pool '%s:%s' success" %
            (vip_domain_name, vip_vip_addresses))
        return msg1


    def prepare_environment(
            self,
            svip_num=None,
            nfs_export_name=None,
            volume_name_nas=None,
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
            nfs_ip=None,
            nfs_mount_path=None,
            cluster_ip=None,
            export_path=None,
            ip_family=None):
        """
        :param svip_num: Required:True   Type:int  Help:The number of svips, e.g. 1/2
        :param nfs_export_name: Required:False   Type:string  Help:The name of nfs export, e.g. nfsexport
        :param volume_name_nas: Required:False   Type:string  Help:The name of nas volume, e.g. parastor_nas
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
        :param nfs_ip: Required:False   Type:string  Help:the ip of nfs client. e.g. 10.2.42.79
        :param nfs_mount_path: Required:False   Type:string  Help:the mount path of nfs client. e.g. /mnt/nfs
        :param cluster_ip: Required:False   Type:string  Help:ip of one cluster node. e.g. 10.2.42.65
        :param export_path: Required:False   Type:string  Help:The nfs export path. e.g. parastor_nas:/
        :param ip_family: Required:False   Type:string  Help:The ip family name. e.g. IPv4/IPv6
        :return:
        """

        # 参数获取
        if None == nfs_ip:
            nfs_ip = self.nfs_ip
        if None == vip_domain_name_s3:
            vip_domain_name_s3 = self.vip_domain_name_s3
        if None == vip_domain_name_nas:
            vip_domain_name_nas = self.vip_domain_name_nas
        if None == cluster_ip:
            cluster_ip = self.cluster_ip
        if None == access_zone_name:
            access_zone_name = self.access_zone_name
        if None == volume_name_nas:
            volume_name_nas = self.volume_name_nas
        if None == export_path:
            export_path = volume_name_nas + ':' + '/'
        if None == nfs_export_name:
            nfs_export_name = "nfs_export"
        if None == nfs_mount_path:
            nfs_mount_path = os.path.join('/mnt', volume_name_nas)
        if None == svip_s3:
            svip_s3 = self.svip_s3
        if None == svip_nas:
            svip_nas = self.svip_nas
        if None == subnet_mask:
            subnet_mask = self.subnet_mask
        if None == network_interfaces_s3:
            network_interfaces_s3 = self.network_interfaces_s3
        if None == network_interfaces_nas:
            network_interfaces_nas = self.network_interfaces_nas
        if None == vip_vip_addresses_s3:
            vip_vip_addresses_s3 = self.vip_vip_addresses_s3
        if None == vip_vip_addresses_nas:
            vip_vip_addresses_nas = self.vip_vip_addresses_nas
        if None == ip_family:
            ip_family = self.ip_family
        if None == svip_num:
            svip_num = self.svip_num

        # 其它参数
        access_zone_node_id_list = node.get_nodes_id()
        access_zone_node_ids = ''
        for item in access_zone_node_id_list:
            access_zone_node_ids = access_zone_node_ids + str(item) + ','
        access_zone_node_ids = access_zone_node_ids[:-1]

        # 步骤1：创建访问区并启动相关服务（nas/s3服务）
        log_prepare.info("添加访问区（启动相关服务）")
        self.add_accesszone_and_enableservice(
            access_zone_node_ids, access_zone_name)

        # 步骤2：添加业务子网和vip池
        log_prepare.info("添加业务子网（包含nas和s3的域名）和vip池")
        access_zone_id = self.get_access_zone_id(access_zone_name)

        if 2 == svip_num:
            msg1 = self.create_svip(access_zone_id, "subnet_1", ip_family, svip_s3, subnet_mask, network_interfaces_s3)
            subnet_id_1 = msg1["result"]
            self.create_vip_address_pool(subnet_id_1, vip_domain_name_s3, vip_vip_addresses_s3, "S3")

            msg2 = self.create_svip(access_zone_id, "subnet_2", ip_family, svip_nas, subnet_mask, network_interfaces_nas)
            subnet_id_2 = msg2["result"]
            self.create_vip_address_pool(subnet_id_2, vip_domain_name_nas, vip_vip_addresses_nas, "NAS")
        elif 1 == svip_num:
            msg = self.create_svip(access_zone_id, "subnet", ip_family, svip_s3, subnet_mask, network_interfaces_s3)
            subnet_id = msg["result"]
            self.create_vip_address_pool(subnet_id, vip_domain_name_s3, vip_vip_addresses_s3, "S3")
            self.create_vip_address_pool(subnet_id, vip_domain_name_nas, vip_vip_addresses_nas, "NAS")
        else:
            self.except_exit('\t the svip numbers %d is wrong(correct value is 1 or 2)' % svip_num)

        # 步骤3：配置私有客户端和nfs客户端协议，并在相应的客户端进行挂载
        log_prepare.info("配置nfs客户端协议，并在相应的客户端进行挂载")
        self.nfs_authorize_and_mount(
            cluster_ip,
            nfs_ip,
            vip_domain_name_nas,
            access_zone_name,
            export_path,
            nfs_export_name,
            nfs_mount_path)


def auto_install_and_prepare(log_path):
    """
    :param log_path: Required:True   Type:string  Help:The log path. e.g. /home/StorTest/test_cases/log/case_log
    :param svip_num: Required:False   Type:int  Help:The number of svips. e.g. 1 or 2
    :return:
    """

    # 第一步：P300_AutoInstall.py执行：1 卸载环境；2 重新部署环境
    log_file_path = log.get_log_path(FILE_NAME)
    log.init(log_file_path, True)

    obj_parastor = P300_AutoInstall.Parastor()

    log.info("start uninstall system")
    obj_parastor.uninstall_system()
    log.info("uninstall system success")

    log.info("start install system")
    obj_parastor.install_system()
    log.info("install system success")

    # prepare_all.py执行操作：
    log_init(log_path)
    prepare_obj = Prepare_all()
    # 第二步：创建访问区并激活服务、添加业务子网与vip池、授权nfs客户端并挂载
    prepare_obj.prepare_environment()

    # 第三部：将StorTest节点作为nfs客户端，进行授权并挂载
    nfs_ip = get_config.get_nfs_client_ip()[1]
    vip_domain_name = prepare_obj.vip_domain_name_nas
    export_path = prepare_obj.export_path
    nfs_mount_path = prepare_obj.nfs_mount_path

    log_prepare.info("\t[ mount nfs client ]")
    time.sleep(5)
    subdir = export_path.split(':')[-1][1:]
    volume_name = export_path.split(':')[0]
    parastor_export_path = os.path.join("/mnt", volume_name, subdir)
    prepare_obj.umount_nfs(nfs_ip, nfs_mount_path)
    time.sleep(5)
    rc_mount, stdout = prepare_obj.nfs_mount(
        nfs_ip,
        vip_domain_name,
        parastor_export_path,
        nfs_mount_path)
    if 0 != rc_mount:
        prepare_obj.except_exit("\t mount nfs client failed")
    log_prepare.info(
        "\t nfs mount success, nfs_ip is %s, nfs_mount_path is %s, parastor_export_path is %s, vip_domain_name is %s" %
        (nfs_ip, nfs_mount_path, parastor_export_path, vip_domain_name))

    return 0


def main():
    log_path = "/home/StorTest/test_cases/log/case_log"
    auto_install_and_prepare(log_path)


if __name__ == '__main__':
    common.case_main(main)

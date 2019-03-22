#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import sys
import json
import time

import utils_path
import common
import nas_common
import snap_common
import log
import get_config
import P300_AutoInstall


class Base:
    def __init__(self,
                 node_name=None,
                 stor_name=None,
                 stripe_width=None,
                 disk_parity_num=None,
                 node_parity_num=None,
                 replica_num=None):
        print sys.path
        self.parastor_ip_lst = get_config.get_allparastor_ips()     # 集群节点ip
        client_ip_lst = get_config.get_allclient_ip()               # 私有客户端节点ip
        self.client_ip_lst = []
        for client_ip in client_ip_lst:
            self.client_ip_lst.append(client_ip)
        self.pkg_path = get_config.get_client_install_path()        # 安装包目录
        self.parastor = P300_AutoInstall.Parastor()
        self.node_name = node_name
        self.stor_name = stor_name
        self.stripe_width = stripe_width
        self.disk_parity_num = 0 if disk_parity_num is None else disk_parity_num
        self.node_parity_num = 0 if node_parity_num is None else node_parity_num
        self.replica_num = replica_num

        return

    def uninstall_parastor(self):
        """
        卸载parastor
        :return:
        """
        self.parastor.uninstall_parastor()

    def check_if_installed(self):
        bflag = False
        cmd = 'lsmod |grep para'
        rc, stdout = common.run_command(self.parastor_ip_lst[0], cmd)
        if "parastor" in stdout:
            bflag = True
        return bflag

    def install_parastor(self):
        """
        安装parastor
        :return:
        """
        # self.parastor.check_pkg_exist()
        # self.parastor.check_config_file()
        node_ip = self.parastor_ip_lst[0]
        deploy_dir_path = os.path.join(self.pkg_path, self.parastor.sys_pkg_name).strip(".tar.xz")
        deploy_abs_path = os.path.join(deploy_dir_path, 'deploy')
        config_abs_path = os.path.join(self.pkg_path, 'deploy_config_p300.xml')
        cmd = 'ssh %s "python %s --deploy_config=%s"' % (node_ip, deploy_abs_path, config_abs_path)
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "parastor install failed!!!")

    def create_node_pool(self):
        """配置节点池"""
        obj_node = common.Node()
        self.node_id_lst = obj_node.get_nodes_id()
        obj_node_pool = common.Nodepool()
        node_ids_str = ','.join([str(node_id) for node_id in self.node_id_lst])
        obj_node_pool.create_node_pool(self.node_name,
                                       node_ids_str,
                                       self.stripe_width,
                                       self.disk_parity_num,
                                       self.node_parity_num,
                                       self.replica_num)

    def create_stor_pool(self):
        """配置存储池"""
        node_id_lst = self.get_node_id_lst_by_name(self.node_name)
        disk_id_lst = []
        for node_id in node_id_lst:
            rc, stdout = common.get_disks(node_ids=node_id)
            common.judge_rc(rc, 0, "node_id: %s, get_disks failed!!!" % node_id)
            stdout = common.json_loads(stdout)

            disk_info_lst = stdout['result']['disks']
            for disk_info in disk_info_lst:
                if disk_info['usage'] == 'DATA' and disk_info['id'] != 0:
                    disk_id_lst.append(disk_info['id'])

        file_storage_pool_disk_id_str = ','.join([str(disk_id) for disk_id in disk_id_lst])

        rc, stdout = common.create_storage_pool(self.stor_name, 'FILE', disk_ids=file_storage_pool_disk_id_str)
        common.judge_rc(rc, 0, "create_storage_pool file failed!!! stdout: %s" % stdout)

    def create_volume(self, volume_name_lst):
        """配置存储卷"""
        obj_storage_pool = common.Storagepool()
        rc, storage_pool_id = obj_storage_pool.get_storagepool_id(self.stor_name)
        common.judge_rc(rc, 0, "get_storagepool_id failed!!! stdout: %s" % storage_pool_id)

        volume_id_lst = []
        obj_volume = common.Volume()
        for volume_name in volume_name_lst:
            rc, stdout = common.create_volume(volume_name,
                                              storage_pool_id,
                                              self.stripe_width,
                                              self.disk_parity_num,
                                              self.node_parity_num,
                                              self.replica_num)
            common.judge_rc(rc, 0, "create_volume %s failed, stdout: %s" % (volume_name, stdout))

            volume_id = obj_volume.get_volume_id(volume_name)
            volume_id_lst.append(volume_id)

    def start_system(self):
        """启动系统"""
        rc, stdout = common.startup()
        common.judge_rc(rc, 0, "startup failed!!! stdout: %s" % stdout)

    def get_node_id_lst_by_name(self, node_pool_name):
        """
        获取节点id列表
        :param node_pool_name:
        :return:
        """
        rc, stdout = common.get_node_pools()
        node_pools = stdout
        node_pools = common.json_loads(node_pools)
        node_pools = node_pools.get('result')
        node_pools = node_pools.get('node_pools')
        for node_pool in node_pools:
            if node_pool.get('name') == node_pool_name:
                return node_pool.get('node_ids')
        return None

    def create_ad(self, ad_name):
        """
        添加AD认证服务器
        :param ad_name:
        :return:
        """
        msg = nas_common.add_auth_provider_ad(name=ad_name,
                                              domain_name=nas_common.AD_DOMAIN_NAME,
                                              dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                              username=nas_common.AD_USER_NAME,
                                              password=nas_common.AD_PASSWORD,
                                              services_for_unix="NONE")

        if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
            raise common.except_exit('add_auth_provider_ad failed!!!')

        auth_provider_id = msg["result"]
        return auth_provider_id

    def create_ldp(self, ldap_name):
        """
        添加LDAP认证服务器
        :param ldap_name:
        :return:
        """
        msg = nas_common.add_auth_provider_ldap(name=ldap_name,
                                                base_dn=nas_common.LDAP_2_BASE_DN,
                                                bind_dn=nas_common.LDAP_2_BIND_DN,
                                                ip_addresses=nas_common.LDAP_2_IP_ADDRESSES,
                                                bind_password=nas_common.LDAP_BIND_PASSWORD,
                                                domain_password=nas_common.LDAP_DOMAIN_PASSWORD,
                                                port=389)

        if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
            raise common.except_exit('add_auth_provider_ldap failed!!!')
        auth_provider_id = msg["result"]
        return auth_provider_id

    def create_nis(self, nis_name):
        """
        添加nis认证服务器
        :param nis_name:
        :return:
        """
        msg = nas_common.add_auth_provider_nis(name=nis_name,
                                               domain_name=nas_common.NIS_DOMAIN_NAME,
                                               ip_addresses=nas_common.NIS_IP_ADDRESSES)

        if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
            common.except_exit("add_auth_provider_nis failed")

        auth_provider_id = msg["result"]
        return auth_provider_id

    def create_zone(self, access_zone_name, auth_provider_id=None):
        """
        创建访问区
        :param access_zone_name:
        :param auth_provider_id:
        :return:
        """
        node = common.Node()
        ids = node.get_nodes_id()
        access_zone_node_ids = ','.join(str(p) for p in ids)
        msg = nas_common.create_access_zone(node_ids=access_zone_node_ids,
                                            auth_provider_id=auth_provider_id,
                                            name=access_zone_name)
        if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
            common.except_exit('create_access_zone failed!!!')
        access_zone_id = msg["result"]
        return access_zone_id

    def enable_nas(self, access_zone_id, protocol_types):
        """
        启动nas服务
        :param access_zone_id:
        :param protocol_types:
        :return:
        """
        msg = nas_common.enable_nas(access_zone_id=access_zone_id, protocol_types=protocol_types)
        if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
            common.except_exit('enable_nas failed!!!')

    def create_subnet(self, access_zone_id, subnet_name):
        """创建子网"""
        msg = nas_common.create_subnet(access_zone_id=access_zone_id,
                                       name=subnet_name,
                                       ip_family=nas_common.IPv4,
                                       svip=nas_common.SUBNET_SVIP,
                                       subnet_mask=nas_common.SUBNET_MASK,
                                       subnet_gateway=nas_common.SUBNET_GATEWAY,
                                       network_interfaces=nas_common.SUBNET_NETWORK_INTERFACES)
        if msg['detail_err_msg'] != '':
            common.except_exit('create subnet failed')
        subnet_id = msg['result']
        return subnet_id

    def create_vip_pool(self, subnet_id):
        """增加vip地址池"""
        msg = nas_common.add_vip_address_pool(subnet_id=subnet_id,
                                              domain_name=nas_common.VIP_DOMAIN_NAME,
                                              vip_addresses=nas_common.VIP_ADDRESSES,
                                              supported_protocol=nas_common.NAS,
                                              allocation_method=nas_common.DYNAMIC,
                                              rebalance_policy=nas_common.IP_RB_AUTOMATIC)
        if msg['detail_err_msg'] != '':
            common.except_exit('create vip pool failed')
        vip_address_pool_id = msg['result']
        return vip_address_pool_id

    def create_auth_group(self, provider_id, group_name):
        """
        创建用户组
        :param provider_id:
        :param group_name:
        :return:
        """
        msg = nas_common.create_auth_group(auth_provider_id=provider_id, name=group_name)

        if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
            common.except_exit('create_auth_group failed!!!')
        group_id = msg["result"]
        return group_id

    def create_auth_user(self, provider_id, group_id, user_name):
        """
        创建用户
        :param provider_id:
        :param group_id:
        :param user_name:
        :return:
        """
        msg = nas_common.create_auth_user(auth_provider_id=provider_id,
                                          name=user_name,
                                          password='111111',
                                          primary_group_id=group_id,
                                          home_dir="/home/%s" % user_name)

        if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
            common.except_exit('create_auth_user failed!!!')

        user_id = msg["result"]
        return user_id

    def get_auth_provider_id_by_zone_name(self, zone_name):
        """
        获取auth provider id
        :param zone_name:
        :return:
        """
        stdout = nas_common.get_access_zones()
        access_zones = stdout["result"]["access_zones"]
        auth_provider_id = None
        for zone in access_zones:
            if zone['name'] == zone_name:
                auth_provider_id = zone['auth_provider_id']
                break
        return auth_provider_id

    def update_acl(self, name, volue):
        """
        更新ACL策略
        :param name:
        :param volue:
        :return:
        """
        # dac_nfs3_set_posix_acl
        # dac_treat_rwx
        common.update_param(section='oApp', name=name, current=volue)

    def create_smb_export(self, access_zone_id, export_name, volume_name):
        """
        创建smba导出
        :param access_zone_id:
        :param export_name:
        :param volume_name:
        :return:
        """
        msg = nas_common.create_smb_export(access_zone_id=access_zone_id,
                                           export_name=export_name,
                                           export_path="%s:/" % volume_name)
        if msg["detail_err_msg"] != "":
            common.except_exit("create_smb_export is failed!!")
        smb_export_id = msg["result"]
        return smb_export_id

    def add_smb_auth(self, smb_export_id, user_or_group_name, type):
        """
        smba授权
        :param smb_export_id:
        :param user_or_group_name:
        :param type:
        :return:
        """
        msg = nas_common.add_smb_export_auth_clients(export_id=smb_export_id,
                                                     name=user_or_group_name,
                                                     user_type=type,
                                                     run_as_root="true")
        if msg["detail_err_msg"] != "":
            common.except_exit("add_smb_export_auth_clients is failed!!")
        auth_clients_id = msg["result"][0]
        return auth_clients_id

    def create_ftp_export(self, access_zone_id, ftp_user_name, ftp_path):
        """
        创建FTP导出
        :param access_zone_id:
        :param ftp_user_name:
        :param ftp_path:
        :return:
        """
        msg = nas_common.create_ftp_export(access_zone_id=access_zone_id,
                                           user_name=ftp_user_name,
                                           export_path="%s:/" % ftp_path)
        if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
            common.except_exit('create_ftp_export failed!!!')

        ftp_export_id = msg["result"]
        return ftp_export_id

    def update_jobengine(self, type, enable_type):
        """
        更新任务配置
        :param type: REPAIR,REBUILD,BALANCE,CONCHK,BBS,RMFS,SNAPSHOT_REVERT,DIRQUOTA,RMSTOREPOOL
        :param enable_type: USER,SYSTEM,NONE
        :return:
        """
        rc, stdout = common.update_jobengine(type=type, enable_type=enable_type)
        msg = common.json_loads(stdout)
        if msg["detail_err_msg"] != "":
            common.except_exit('update_jobengine failed!!!')

    def create_jobengine_impact(self, job_name):
        """
        创建影响度
        :param job_name:
        :return:
        """
        impact_json = {}
        impact_json['name'] = job_name
        impact_json['desc'] = ""

        intervals_json = {}
        intervals_json['link_id'] = 1

        start_time_json = {}
        start_time_json['week_day'] = 1
        start_time_json['hour'] = 0
        start_time_json['minute'] = 0
        intervals_json['start_time'] = start_time_json

        end_time_json = {}
        end_time_json['week_day'] = 1
        end_time_json['hour'] = 0
        end_time_json['minute'] = 0
        intervals_json['end_time'] = end_time_json

        intervals_lst = []
        intervals_lst.append(intervals_json)
        impact_json['intervals'] = intervals_lst

        impact_info = json.dumps(impact_json)
        impact_info = "'" + impact_info + "'"
        impact_info = impact_info.replace('"', "\\\"")
        rc, stdout = common.create_jobengine_impact(impact_info)
        common.judge_rc(rc, 0, 'create jobengine impact')

    def update_node_timeout(self, current_volue):
        """
        更新节点变坏时间参数
        :param current_volue:
        :return:
        """
        common.update_param("MGR", "node_isolate_timeout", current_volue)

    def update_param(self, param_section, param_name, current_volue):
        """
        更新配置参数
        :param param_section:
        :param param_name:
        :param current_volue:
        :return:
        """
        common.update_param(section=param_section, name=param_name, current=current_volue)

    def open_snapshot(self):
        """
        开启快照
        :return:
        """
        self.update_param(param_section='MGR', param_name='snapshot_license', current_volue=1)

    def create_snapshot(self, snap_name, path):
        """
        创建快照
        :param snap_name:
        :param path:
        :return:
        """
        rc, stdout = snap_common.create_snapshot(snap_name, "%s:/" % path)
        common.judge_rc(rc, 0, 'create snapshot failed')

    def create_snapshot_strategy(self, strategy_name, volume):
        """
        创建快照策略
        :param strategy_name:
        :param volume:
        :return:
        """
        rc, stdout = common.create_snapshot_strategy(name=strategy_name,
                                                     path="%s:/" % volume,
                                                     period_type='BY_DAY',
                                                     hours=0,
                                                     minute=0,
                                                     expire_time=0)

        common.judge_rc(rc, 0, 'create snapshot strategy failed')

    def install_webui(self):
        """安装webui"""
        parastor_ip_one = get_config.get_parastor_ip()
        vir_ip = get_config.get_web_ip()
        if not common.check_ping(vir_ip):
            webui_path = get_config.get_web_pkg_position()   # /home/deploy
            cmd = "ls %s | grep parastor_gui_installer | grep tar" % webui_path
            rc, webui_name_tar = common.run_command(parastor_ip_one, cmd)
            common.judge_rc(rc, 0, "no webui tar")

            cmd1 = "cd %s;tar -xf %s" % (webui_path, webui_name_tar.strip())
            virt_ip = get_config.get_web_ip()
            netcard_name = get_config.get_web_eth_name_ctrl()
            subnet_mask = get_config.get_web_network_mask()
            parameter = "--virt_ip=%s --netcard_name=%s --subnet_mask=%s" % (virt_ip, netcard_name, subnet_mask)
            cmd2 = "python %s/parastor_gui_installer/webui/deployment/install_local_webui.py %s" % (webui_path, parameter)
            rc1, stdout = common.run_command(parastor_ip_one, cmd1)
            common.judge_rc(rc1, 0, "tar -xf webui")
            rc2, stdout = common.run_command(parastor_ip_one, cmd2)
            common.judge_rc(rc2, 0, "install webui")

        # 检查ping
        for i in range(600):
            log.info("ping %s" % vir_ip)
            if common.check_ping(vir_ip):
                break
            if i == 599:
                raise Exception("check ping vir ip failed")
            time.sleep(1)
        time.sleep(60)
        return

    def uninstall_webui(self):
        """卸载webui"""
        parastor_ips = get_config.get_allparastor_ips()
        for ip in parastor_ips:
            webui_path = "/opt/gridview/webui/deployment/uninstall_local_webui.py"
            if os.path.exists(webui_path):
                rc, stdout = common.run_command(ip, "ls %s" % webui_path)
                if rc == 0:
                    rc1, stdout = common.run_command(ip, "python %s" % webui_path)
                    common.judge_rc(rc1, 0, "uninstall webui")
        return

    def get_snapshot_id_by_name(self, snap_name):
        """
        通过快照name获取快照id
        :param snap_name:
        :return:
        """
        snap_info = snap_common.get_snapshot_by_name(snap_name)
        snap_id = snap_info['id']
        return snap_id

    def revert_snapshot(self, snap_id):
        """
        快照回滚
        :param snap_id:
        :return:
        """
        rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
        common.judge_rc(rc, 0, "revert snapshot")

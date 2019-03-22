#!/usr/bin/python
# -*-coding:utf-8 -*
import os
import commands
import sys
import json

import utils_path
import common
import get_config
import log


class ProcessConf:
    def __init__(self,
                 file_name=None,
                 timestamp=None,
                 lef_timestamp=None,
                 right_timestamp=None,
                 cmd_lst=None):
        self.base_url = 'https://%s:6080' % get_config.get_web_ip()
        if file_name is None and timestamp is not None:
            # log.info("timestamp is specified, file_name must be specified")
            common.except_exit("timestamp is specified, file_name must be specified")
        if file_name is not None and timestamp is None:
            # log.info("file_name is specified, timestamp must be specified")
            common.except_exit("file_name is specified, timestamp must be specified")
        self.file_name = file_name
        self.timestamp = timestamp
        if lef_timestamp is not None and right_timestamp is None:
            # log.info("lef_file is specified, right_file must be specified")
            common.except_exit("lef_file is specified, right_file must be specified")
        if right_timestamp is not None and lef_timestamp is None:
            # log.info("right_file is specified, lef_file must be specified")
            common.except_exit("right_file is specified, lef_file must be specified")
        self.lef_file = lef_timestamp
        self.right_file = right_timestamp
        self.path_lst = []
        if lef_timestamp is not None and right_timestamp is not None:
            self.iscompare = True
            self.path_lst.append(lef_timestamp)
            self.path_lst.append(right_timestamp)
        else:
            self.iscompare = False

        default_cmd_lst = ['get_nodes',
                           'get_jobengines',
                           'get_events --event_code=0x03010001',
                           'get_jobengine_impact',
                           'get_params',
                           'get_events',
                           'get_node_pools',
                           'get_storage_pools',
                           'get_volumes',
                           'get_quota',
                           'get_auth_providers_ad',
                           'get_auth_providers_ldap',
                           'get_auth_providers_nis',
                           'get_auth_providers_local',
                           'get_access_zones',
                           'get_subnets',
                           'get_vip_address_pools',
                           'get_vip_distribution',
                           'get_auth_users',
                           'get_auth_groups',
                           'get_client_auth',
                           'get_smb_global_configs',
                           'get_smb_exports',
                           'get_smb_export_auth_clients',
                           'get_nfs_exports',
                           'get_nfs_export_auth_clients',
                           'get_ftp_exports',
                           'get_ftp_global_config',
                           'get_alarm_metrics',
                           'get_ntp',
                           'get_snmp',
                           'get_snmp_usmuser',
                           'get_email_config',
                           'get_smsmodem',
                           'get_recipients',
                           'get_alert_strategies',
                           'get_webui_info',
                           'get_file_list']
        self.cmd_lst = default_cmd_lst if cmd_lst is None else cmd_lst

        self.check_package_install()
        self.install_and_load()

    def http_login(self):
        """
        http登陆
        :return:
        """
        import requests
        url = "%s/login/loginAuth.action" % self.base_url

        values = {}
        values['strUserName'] = 'optadmin'
        values['strPassword'] = 'adminadmin'
        values['language'] = 'zh_CN'

        response = requests.post(url, values, verify=False)
        cookies = response.cookies

        return cookies

    def process_alarm_metrics(self):
        """
        处理告警阈值信息
        :return:
        """
        std_json = self.process_http_request('get_alarm_metrics')
        return std_json

    def process_webui_info(self):
        """
        处理webUI节点信息
        :return:
        """
        std_json = self.process_http_request('getWebUINodeInfo')
        return std_json

    def http_connect_cluster(self):
        """
        webUI连接集群
        :return:
        """
        import requests
        cookies = self.http_login()
        # uuid = self.get_uuid()
        url_con = self.base_url + "/install/connectToExistCluster.action?user_name=optadmin"
        values = {}
        values['rand'] = ''
        values['oJmgsIPs'] = get_config.get_web_ip()
        response = requests.post(url_con, values, verify=False, cookies=cookies)
        log.info(response.text)

    def http_clean_connect(self):
        """
        webUI断开集群连接
        :return:
        """
        import requests
        cookies = self.http_login()
        uuid = self.get_uuid()
        url = self.base_url + "/install/cleanConnectFromDB.action?user_name=optadmin"

        values = {}
        values['rand'] = ''
        values['uuid'] = uuid

        response = requests.post(url, values, verify=False, cookies=cookies)
        log.info(response.text)

    def process_http_request(self, cmd):
        """
        处理http请求
        :param cmd:
        :return:
        """
        self.check_package_install()
        self.install_and_load()
        import requests

        cookies = self.http_login()
        url = '%s/commands/%s.action' % (self.base_url, cmd)

        values = {}
        values['user_name'] = 'optadmin'
        uuid = self.get_uuid()
        values['uuid'] = uuid

        response = requests.get(url, values, verify=False, cookies=cookies)
        stdout = response.text
        std_json = self.json_loads(stdout)
        if 'trace_id' in std_json.keys():
            del std_json['trace_id']

        if 'time_stamp' in std_json.keys():
            del std_json['time_stamp']

        return std_json

    def get_uuid(self):
        """
        获取uuid
        :return:
        """
        cmd = "get_cluster_overview"
        rc, stdout = common.run_pscli(cmd)
        std_json = self.json_loads(stdout)
        uuid = std_json['result']['uuid']

        return uuid

    def json_loads(self, json_str):
        json_str = json.loads(json_str)
        return json_str

    def check_package_install(self):
        """
        检查是否安装requests
        :return:
        """
        count = 2
        while count:
            try:
                import requests
                log.info('requests has been installed')
                break
            except:
                log.info('requests is not installed, begin to install......')
                package_list = ['certifi-2019.3.9',
                                'urllib3-1.24.1',
                                'idna-2.8',
                                'chardet-3.0.4',
                                'requests-2.21.0']
                third_packge_path = get_config.get_third_package_path()
                os.chdir(third_packge_path)
                for package in package_list:
                    cmd = 'tar -xvf %s.tar.gz' % package
                    rc, stdout = commands.getstatusoutput(cmd)

                for package in package_list:
                    requests_path = os.path.join('%s' % third_packge_path, package)
                    # cmd = 'cd %s' % requests_path
                    os.chdir(requests_path)
                    # rc, stdout = commands.getstatusoutput('pwd')
                    # print stdout
                    cmd = 'python setup.py install'
                    rc, stdout = commands.getstatusoutput(cmd)
                    # print stdout
                # os.system('pip install requests')
                count -= 1
            continue

    def install_and_load(self):
        """
        将requests路径加入path
        :return:
        """
        path1 = '/usr/lib/python2.7/site-packages/requests-2.21.0-py2.7.egg'
        if path1 not in sys.path:
            sys.path.append(path1)

    def process_node_info(self, std_json2):
        """
        处理集群节点信息
        :param std_json2:
        :return:
        """
        node_infos = std_json2['result']['nodes']

        for node in node_infos:
            del node['avail_bytes']
            del node['used_bytes']
            del node['upgrade_package_time']
            del node['node_package_time']
            data_disks = node['data_disks']
            for disk in data_disks:
                del disk['iostat']
                del disk['avail_bytes']
                del disk['used_bytes']
                del disk['util']
                physical_disks = disk['physical_disks']
                for physical_disk in physical_disks:
                    del physical_disk['temperature']

            cpus = node['reported_info']['hardware']['cpu']
            for cpu in cpus:
                del cpu['temperature']

            mgc_disks = node['reported_info']['hardware']['mgc_disk']
            for mgc_disk in mgc_disks:
                disks = mgc_disk['disks']
                for disk in disks:
                    usages = disk['usages']
                    for usage in usages:
                        del usage['avail_bytes']
                        del usage['free_bytes']
                        del usage['used_bytes']

            mgcd_disks = node['reported_info']['hardware']['mgcd_disk']
            for mgcd_disk in mgcd_disks:
                del mgcd_disk['iostat']
                del mgcd_disk['util']
                del mgcd_disk['system_usage_rate']
                physical_disks = mgcd_disk['physical_disks']
                for physical_disk in physical_disks:
                    del physical_disk['temperature']

            del node['reported_info']['hardware']['netdev']
            del node['reported_info']['summary']

            services = node['reported_info']['service']
            for service in services:
                if "RSS" in service:
                    del service['RSS']
                if 'cpu_usage' in service:
                    del service['cpu_usage']
                if 'iops' in service:
                    del service['iops']
                if 'mem_usage' in service:
                    del service['mem_usage']
                if 'rw_throughput' in service:
                    del service['rw_throughput']

            client_connections = node['reported_info']['nas_protocol']
            del client_connections['client_connections']

            vip_connections = node['reported_info']['nas_protocol']
            del vip_connections['vip_connections']

            services = node['services']
            for service in services:
                if 'iops' in service:
                    del service['iops']
                if 'throughput' in service:
                    del service['throughput']

            share_disks = node['shared_disks']
            for share_disk in share_disks:
                del share_disk['iostat']
                del share_disk['used_bytes']
                del share_disk['util']
                del share_disk['avail_bytes']

                physical_disks = share_disk['physical_disks']
                for physical_disk in physical_disks:
                    del physical_disk['temperature']

        return std_json2

    def process_node_pool(self, std_json2):
        """
        处理节点池信息
        :param std_json2:
        :return:
        """
        node_pools = std_json2['result']['node_pools']
        for node_pool in node_pools:
            nodes = node_pool['nodes']
            del node_pool['used_bytes']
            for node in nodes:
                del node['avail_bytes']
                del node['iostat']
                del node['throughput']
                del node['used_bytes']

        return std_json2

    def process_storage_pool(self, std_json):
        """
        处理存储池信息
        :param std_json:
        :return:
        """
        storage_pools = std_json['result']['storage_pools']
        for storage_pool in storage_pools:
            del storage_pool['avail_bytes']
            del storage_pool['avail_bytes_percentage']
            del storage_pool['used_bytes']
            del storage_pool['used_ratio']

        return std_json

    def process_volumes(self, std_json):
        """
        处理卷信息
        :param std_json:
        :return:
        """
        volumes = std_json['result']['volumes']
        for volume in volumes:
            del volume['usedBytes']
            del volume['qos']
            del volume['layout']

        return std_json

    def process_subnets(self, std_json):
        """
        处理sub-net信息
        :param std_json:
        :return:
        """
        subnets = std_json['result']['subnets']
        subnet_id_lst = []
        for subnet in subnets:
            subnet_id_lst.append(subnet['id'])

        return subnet_id_lst

    def process_auth_providers(self, std_json):
        """
        处理auth provider信息
        :param std_json:
        :return:
        """
        auth_providers = std_json['result']['auth_providers']
        auth_providers_lst = []
        for provider in auth_providers:
            auth_providers_lst.append(provider['id'])

        return auth_providers_lst

    def process_ftp_exports(self, std_json):
        """
        处理FTP导出信息
        :param std_json:
        :return:
        """
        exports = std_json['result']['exports']
        exports_lst = []
        for export in exports:
            exports_lst.append(export['access_zone_id'])

        return exports_lst

    def process_quota(self, std_json):
        """
        处理quota信息
        :param std_json:
        :return:
        """
        quotas = std_json['result']['quotas']
        for quota in quotas:
            del quota['filenr_used_nr']
            del quota['logical_used_capacity']

        return std_json

    def get_file_lst(self):
        """
        获取文件列表
        :return:
        """
        file_lst = []
        base_name = 'base'
        base_path = '/'
        file_lst.append((base_name,) + (base_path,))

        rc, stdout = common.get_file_list('/', display_details='true')
        std_json = self.json_loads(stdout)
        detail_files = std_json['result']['detail_files']
        for file in detail_files:
            file_lst.append((file['name'],) + (file['path'],))

        return file_lst

    def process_diff(self):

        base_path = "/home/result/"
        if self.iscompare:
            for cmd in self.cmd_lst:
                if 'get_file_list' not in cmd:
                    if 'get_events' in cmd and 'event_code' in cmd:
                        cmd = 'job_config'

                    file_lst_base = []
                    for p_path in self.path_lst:
                        path = os.path.join(base_path, p_path, cmd)
                        cmds = 'ls %s' % path
                        rc, stdout = commands.getstatusoutput(cmds)
                        file_lst_base.append(os.path.join(path, stdout))
                    cmd_dif = 'diff %s %s -s' % (file_lst_base[0], file_lst_base[1])
                    log.info(cmd_dif)
                    rc1, stdout1 = commands.getstatusoutput(cmd_dif)
                    log.info(stdout1)
                    log.info("\n")
                else:
                    file_lst_base = []
                    for p_path in self.path_lst:
                        path = os.path.join(base_path, p_path, cmd)
                        cmds = "ls -l %s -t|tac |grep -v total |awk '{print $9}'" % path
                        # print cmds
                        rc, stdout = commands.getstatusoutput(cmds)
                        f_names = stdout.split("\n")
                        f_lst_base = []
                        for f_name in f_names:
                            f_path = os.path.join(path, f_name)
                            f_lst_base.append(f_path)
                            # print f_path
                        file_lst_base.append(f_lst_base)
                        # print '\n'
                    l_lst = file_lst_base[0]
                    r_lst = file_lst_base[1]
                    for (l_file, r_file) in zip(l_lst, r_lst):
                        l_cmd = 'ls %s' % l_file
                        rc, stdout = commands.getstatusoutput(l_cmd)
                        l_file_name = stdout
                        r_cmd = 'ls %s' % r_file
                        rc, stdout = commands.getstatusoutput(r_cmd)
                        r_file_name = stdout

                        l_file_path = os.path.join(l_file, l_file_name)
                        r_file_path = os.path.join(r_file, r_file_name)

                        cmd_dif = 'diff %s %s -s' % (l_file_path, r_file_path)
                        log.info(cmd_dif)
                        rc1, stdout1 = commands.getstatusoutput(cmd_dif)
                        log.info(stdout1)
                        log.info("\n")
        else:
            for cmd in self.cmd_lst:
                log.info("begin to %s" % cmd)
                if 'get_vip_distribution' in cmd:
                    sub_cmd = 'get_subnets'
                    rc, stdout = common.run_pscli(sub_cmd)
                    std_json = self.json_loads(stdout)
                    subnet_id = self.process_subnets(std_json)[0]
                    cmd += ' --subnet_id=%d' % subnet_id

                if 'get_auth_users' in cmd or 'get_auth_groups' in cmd:
                    sub_cmd = 'get_auth_providers_ad'
                    rc, stdout = common.run_pscli(sub_cmd)
                    std_json = self.json_loads(stdout)
                    auth_provider_id = self.process_auth_providers(std_json)[0]
                    cmd += ' --auth_provider_id=%d' % auth_provider_id

                if 'get_ftp_global_config' in cmd:
                    sub_cmd = 'get_ftp_exports'
                    rc, stdout = common.run_pscli(sub_cmd)
                    std_json = self.json_loads(stdout)
                    access_zone_id = self.process_ftp_exports(std_json)[0]
                    cmd += ' --access_zone_id=%d' % access_zone_id

                if 'get_file_list' not in cmd:
                    if 'get_alarm_metrics' in cmd:
                        std_json = self.process_alarm_metrics()
                    elif 'get_webui_info' in cmd:
                        std_json = self.process_webui_info()
                    else:
                        rc, stdout = common.run_pscli(cmd)
                        std_json = self.json_loads(stdout)
                        del std_json['trace_id']
                        if cmd == "get_nodes":
                            std_json = self.process_node_info(std_json)
                        if cmd == 'get_node_pools':
                            std_json = self.process_node_pool(std_json)
                        if cmd == 'get_storage_pools':
                            std_json = self.process_storage_pool(std_json)
                        if cmd == 'get_volumes':
                            std_json = self.process_volumes(std_json)
                        if cmd == 'get_quota':
                            std_json = self.process_quota(std_json)
                        if 'get_events' in cmd and 'event_code' in cmd:
                            cmd = 'job_config'
                        if 'get_vip_distribution' in cmd:
                            cmd = 'get_vip_distribution'
                        if 'get_auth_users' in cmd or 'get_auth_groups' in cmd:
                            cmd = cmd.split(" ")[0]
                        if 'get_ftp_global_config' in cmd:
                            cmd = 'get_ftp_global_config'
                    path = os.path.join(base_path, self.timestamp, cmd)
                    if not os.path.exists(path):
                        os.makedirs(path)
                    with open(path + "/%s" % self.file_name, 'w+') as f:
                        f.write(json.dumps(std_json, sort_keys=True, indent=2))
                else:
                    file_lst = self.get_file_lst()
                    for f_name, f_path in file_lst:
                        log.info("process %s" % f_name)
                        rc, stdout = common.get_file_list(f_path, display_details='true')
                        std_json = self.json_loads(stdout)
                        del std_json['trace_id']
                        detail_files = std_json['result']['detail_files']
                        for file in detail_files:
                            del file['access_time']
                            del file['modify_time']
                            del file['create_time']
                            del file['size']

                        path = os.path.join(base_path, self.timestamp, cmd, f_name)
                        if not os.path.exists(path):
                            os.makedirs(path)
                        with open(path + "/%s" % self.file_name, 'w+') as f:
                            f.write(json.dumps(std_json, sort_keys=True, indent=2))

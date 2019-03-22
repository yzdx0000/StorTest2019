#!/usr/bin/python
# -*- coding:utf-8 -*-

from multiprocessing import Process
import os
import log
import time
import random

import common
import get_config
import remote


class NAS(object):
    def __init__(self, print_flag=True, fault_node_ip=None, *args, **kwargs):
        """
        :param print_flag: 是否打印执行结果
        :param fault_node_ip: 故障点的ip
        :param args:
        :param kwargs:
        """
        self.print_flag = print_flag
        self.fault_node_ip = fault_node_ip
        self.args = args
        self.kwargs = kwargs


class AuthProvider(NAS):
    def __init__(self, print_flag=True, fault_node_ip=None):
        """
        :param print_flag:
        :param fault_node_ip:
        """
        NAS.__init__(self, print_flag, fault_node_ip)
        self._all_ids = None    # 所有认证服务器id。格式如下：e.g. 1,2,3,4

    @property
    def all_ids(self):
        msg = self.get_auth_providers_summary()
        ids = []
        for auth_provider in msg['result']['auth_providers']:
            ids.append(auth_provider['id'])
        self._all_ids = ','.join(str(i) for i in ids)
        return self._all_ids

    def delete_auth_providers(self, ids=None, exit_flag=False):
        """删除认证服务器
        :param ids: 不输入则删除全部认证服务器，输入则删除指定认证服务器。格式如下：e.g. 1,2,3,4
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ delete_auth_providers ]")
        ids = self.all_ids if ids is None else ids
        rc, stdout = common.delete_auth_providers(ids=ids, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'delete_auth_providers failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def check_auth_provider(self, exit_flag=False):
        pass

    def get_auth_providers_summary(self, ids=None, exit_flag=False):
        """查询认证服务器概览
        :param ids: Required:False  Type:string  Help:The authentication provider id list to get, e.g. 1,2,3
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ get_auth_providers_summary ]")
        rc, stdout = common.get_auth_providers_summary(ids=ids, print_flag=self.print_flag,
                                                       fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'get_auth_providers_summary failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg


class AuthProviderAD(AuthProvider):
    def __init__(self, name=None, domain_name=None, dns_addresses=None, username=None, password=None,
                 services_for_unix=None, unix_id_range=None, other_unix_id_range=None,
                 print_flag=True, fault_node_ip=None):
        """AD认证服务器
        :param name: Required:True. 如果不输入，则使用这个名字：default_name
        :param domain_name: Required:True. 如果不输入，则读配置文件
        :param dns_addresses: Required:True. 如果不输入，则读配置文件
        :param username: Required:True. 如果不输入，则读配置文件
        :param password: Required:True. 如果不输入，则读配置文件
        :param services_for_unix: Required:True. 如果不输入，则在'NONE'和'RFC2307'中随机选一个
        :param unix_id_range:
        :param other_unix_id_range:
        :param print_flag:
        :param fault_node_ip:
        """
        AuthProvider.__init__(self, print_flag, fault_node_ip)
        self.name = 'default_name' if name is None else name
        self.domain_name = ad_domain_name() if domain_name is None else domain_name
        self.dns_addresses = ad_dns_address() if dns_addresses is None else dns_addresses
        self.username = ad_admin_user_name() if username is None else username
        self.password = ad_password() if password is None else password
        self.services_for_unix = random.choice(['NONE', 'RFC2307']) if services_for_unix is None else services_for_unix
        self.unix_id_range = unix_id_range
        self.other_unix_id_range = other_unix_id_range
        self.p_id = None        # 本AD认证服务器id
        self._ad_ids = None     # 全部AD认证服务器id，格式：1,2,3

    def __str__(self):
        return '[name: %s, domain_name: %s, dns_addresses: %s, ' \
               'username: %s, password: %s, services_for_unix: %s, ' \
               'unix_id_range: %s, other_unix_id_range: %s, p_id: %s, ' \
               'print_flag: %s, fault_node_ip: %s]' % (self.name, self.domain_name, self.dns_addresses,
                                                       self.username, self.password, self.services_for_unix,
                                                       self.unix_id_range, self.other_unix_id_range,
                                                       self.p_id, self.print_flag, self.fault_node_ip)

    @property
    def ad_ids(self):
        msg = self.get_auth_providers_ad()
        ids = []
        for auth_provider in msg['result']['auth_providers']:
            ids.append(auth_provider['id'])
        self._ad_ids = ','.join(str(i) for i in ids)
        return self._ad_ids

    def add_auth_provider_ad(self, check=None, exit_flag=False):
        """添加AD认证服务器
        :param check:
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ add_auth_provider_ad ]")
        """设置集群节点与AD鉴权服务器时间同步"""
        # set_ntp(is_enabled='true', ntp_servers=AD_DNS_ADDRESSES, sync_period=5)
        rc, stdout = common.add_auth_provider_ad(name=self.name, domain_name=self.domain_name,
                                                 dns_addresses=self.dns_addresses, username=self.username,
                                                 password=self.password, services_for_unix=self.services_for_unix,
                                                 unix_id_range=self.unix_id_range,
                                                 other_unix_id_range=self.other_unix_id_range, check=check,
                                                 print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'add_auth_provider_ad failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0 and check is not 'true':
            self.p_id = msg['result']
        return msg

    def update_auth_provider_ad(self, name=None, domain_name=None, dns_addresses=None,
                                username=None, password=None, check=None, exit_flag=False):
        """修改AD认证服务器
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ update_auth_provider_ad ]")
        rc, stdout = common.update_auth_provider_ad(id=self.p_id, name=name, domain_name=domain_name,
                                                    dns_addresses=dns_addresses, username=username,
                                                    password=password, check=check,
                                                    print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'update_auth_provider_ad failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0 and check is not 'true':
            if name is not None:
                self.name = name
            if domain_name is not None:
                self.domain_name = domain_name
            if dns_addresses is not None:
                self.dns_addresses = dns_addresses
            if username is not None:
                self.username = username
            if password is not None:
                self.password = password
        return msg

    def delete_auth_providers_ad(self, ids=None, exit_flag=False):
        """删除认证服务器
        :param ids: 若不输入则删除全部AD认证服务器，输入则删除指定认证服务器。格式如下：e.g. 1,2,3,4
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ delete_auth_providers ]")
        ids = self.ad_ids if ids is None else ids
        rc, stdout = common.delete_auth_providers(ids=ids, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'delete_auth_providers failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def get_auth_providers_ad(self, ids=None, exit_flag=False):
        """查询AD认证服务器
        :param ids: Required:False  Type:string  Help:The authentication provider id list to get, e.g. 1,2,3
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ get_auth_providers_ad ]")
        rc, stdout = common.get_auth_providers_ad(ids=ids, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'get_auth_providers_ad failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def check_auth_provider(self, exit_flag=False):
        """查询已有认证服务器是否可用
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ check_auth_provider ]")
        rc, stdout = common.check_auth_provider(id=self.p_id,
                                                print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'check_auth_provider failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg


class AuthProviderNIS(AuthProvider):
    def __init__(self, name=None, domain_name=None, ip_addresses=None,
                 print_flag=True, fault_node_ip=None):
        """NIS认证服务器
        :param name: Required:True. 如果不输入，则使用这个名字：default_name
        :param domain_name: Required:True. 如果不输入，则读配置文件
        :param ip_addresses: Required:True. 如果不输入，则读配置文件
        :param print_flag:
        :param fault_node_ip:
        """
        AuthProvider.__init__(self, print_flag, fault_node_ip)
        self.name = 'default_name' if name is None else name
        self.domain_name = nis_domain_name() if domain_name is None else domain_name
        self.ip_addresses = nis_ip_address() if ip_addresses is None else ip_addresses
        self.p_id = None        # 本NIS认证服务器id
        self._nis_ids = None    # 全部NIS认证服务器id，格式：1,2,3

    def __str__(self):
        return '[name: %s, domain_name: %s, ip_addresses: %s, p_id: %s, ' \
               'print_flag: %s, fault_node_ip: %s]' % (self.name, self.domain_name, self.ip_addresses, self.p_id,
                                                       self.print_flag, self.fault_node_ip)

    @property
    def nis_ids(self):
        msg = self.get_auth_providers_nis()
        ids = []
        for auth_provider in msg['result']['auth_providers']:
            ids.append(auth_provider['id'])
        self._nis_ids = ','.join(str(i) for i in ids)
        return self._nis_ids

    def add_auth_provider_nis(self, check=None, exit_flag=False):
        """添加NIS认证服务器
        :param check:
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ add_auth_provider_nis ]")
        rc, stdout = common.add_auth_provider_nis(name=self.name, domain_name=self.domain_name,
                                                  ip_addresses=self.ip_addresses, check=check,
                                                  print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'add_auth_provider_nis failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0 and check is not 'true':
            self.p_id = msg['result']
        return msg

    def update_auth_provider_nis(self, name=None, domain_name=None, ip_addresses=None, check=None, exit_flag=False):
        """修改NIS认证服务器
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ update_auth_provider_nis ]")
        rc, stdout = common.update_auth_provider_nis(id=self.p_id, name=name, domain_name=domain_name,
                                                     ip_addresses=ip_addresses, check=check,
                                                     print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'update_auth_provider_nis failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0 and check is not 'true':
            if name is not None:
                self.name = name
            if domain_name is not None:
                self.domain_name = domain_name
            if ip_addresses is not None:
                self.ip_addresses = ip_addresses
        return msg

    def delete_auth_providers_nis(self, ids=None, exit_flag=False):
        """删除认证服务器
        :param ids: 不输入则删除全部NIS认证服务器，输入则删除指定认证服务器。格式如下：e.g. 1,2,3,4
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ delete_auth_providers ]")
        ids = self.nis_ids if ids is None else ids
        rc, stdout = common.delete_auth_providers(ids=ids, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'delete_auth_providers failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def get_auth_providers_nis(self, ids=None, exit_flag=False):
        """查询NIS认证服务器
        :param ids: Required:False  Type:string  Help:The authentication provider id list to get, e.g. 1,2,3
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ get_auth_providers_nis ]")
        rc, stdout = common.get_auth_providers_nis(ids=ids, print_flag=self.print_flag,
                                                   fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'get_auth_providers_nis failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def check_auth_provider(self, exit_flag=False):
        """查询已有认证服务器是否可用
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ check_auth_provider ]")
        rc, stdout = common.check_auth_provider(id=self.p_id,
                                                print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'check_auth_provider failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg


class AuthProviderLDAP(AuthProvider):
    def __init__(self, name=None, base_dn=None, ip_addresses=None, port=None, bind_dn=None, bind_password=None,
                 domain_password=None, user_search_path=None, group_search_path=None,
                 print_flag=True, fault_node_ip=None):
        """LDAP认证服务器
        :param name: Required:True. 如果不输入，则使用这个名字：default_name
        :param base_dn: Required:True. 如果不输入，则读配置文件
        :param ip_addresses: Required:True. 如果不输入，则读配置文件
        :param port:
        :param bind_dn: 如果不输入，则为None
        :param bind_password: 如果不输入，则为None
        :param domain_password: 如果不输入，则为None
        :param user_search_path: 如果不输入，则为None
        :param group_search_path: 如果不输入，则为None
        :param print_flag:
        :param fault_node_ip:
        """
        AuthProvider.__init__(self, print_flag, fault_node_ip)
        self.name = 'default_name' if name is None else name
        self.base_dn = ldap_base_dn() if base_dn is None else base_dn
        self.ip_addresses = ldap_ip_address() if ip_addresses is None else ip_addresses
        self.bind_dn = bind_dn
        self.bind_password = bind_password
        self.domain_password = domain_password
        self.user_search_path = user_search_path
        self.group_search_path = group_search_path
        self.port = port
        self.p_id = None        # 本LDAP认证服务器id
        self._ldap_ids = None   # 全部LDAP认证服务器id，格式：1,2,3

    def __str__(self):
        return '[name: %s, base_dn: %s, ip_addresses: %s, port: %s, bind_dn: %s, bind_password: %s, ' \
               'domain_password: %s, user_search_path: %s, group_search_path: %s, p_id: %s, ' \
               'print_flag: %s, fault_node_ip: %s]' % (self.name, self.base_dn, self.ip_addresses,
                                                       self.port, self.bind_dn, self.bind_password,
                                                       self.domain_password, self.user_search_path,
                                                       self.group_search_path, self.p_id,
                                                       self.print_flag, self.fault_node_ip)

    @property
    def ldap_ids(self):
        msg = self.get_auth_providers_ldap()
        ids = []
        for auth_provider in msg['result']['auth_providers']:
            ids.append(auth_provider['id'])
        self._ldap_ids = ','.join(str(i) for i in ids)
        return self._ldap_ids

    def add_auth_provider_ldap(self, check=None, exit_flag=False):
        """添加LDAP认证服务器
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ add_auth_provider_ldap ]")
        rc, stdout = common.add_auth_provider_ldap(name=self.name, base_dn=self.base_dn, ip_addresses=self.ip_addresses,
                                                   port=self.port, bind_dn=self.bind_dn,
                                                   bind_password=self.bind_password,
                                                   domain_password=self.domain_password,
                                                   user_search_path=self.user_search_path,
                                                   group_search_path=self.group_search_path, check=check,
                                                   print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'add_auth_provider_ldap failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0 and check is not 'true':
            self.p_id = msg['result']
        return msg

    def update_auth_provider_ldap(self, name=None, base_dn=None, ip_addresses=None, port=None, bind_dn=None,
                                  bind_password=None, domain_password=None, user_search_path=None,
                                  group_search_path=None, check=None, exit_flag=False):
        """修改LDAP认证服务器
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ update_auth_provider_ldap ]")
        rc, stdout = common.update_auth_provider_ldap(id=self.p_id, name=name, base_dn=base_dn,
                                                      ip_addresses=ip_addresses, port=port,
                                                      bind_dn=bind_dn, bind_password=bind_password,
                                                      domain_password=domain_password,
                                                      user_search_path=user_search_path,
                                                      group_search_path=group_search_path, check=check,
                                                      print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'update_auth_provider_ldap failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0 and check is not 'true':
            if name is not None:
                self.name = name
            if base_dn is not None:
                self.base_dn = base_dn
            if ip_addresses is not None:
                self.ip_addresses = ip_addresses
            if port is not None:
                self.port = port
            if bind_dn is not None:
                self.bind_dn = bind_dn
            if bind_password is not None:
                self.bind_password = bind_password
            if domain_password is not None:
                self.domain_password = domain_password
            if user_search_path is not None:
                self.user_search_path = user_search_path
            if group_search_path is not None:
                self.group_search_path = group_search_path
        return msg

    def delete_auth_providers_ldap(self, ids=None, exit_flag=False):
        """删除认证服务器
        :param ids: 不输入则删除全部LDAP认证服务器，输入则删除指定认证服务器。格式如下：e.g. 1,2,3,4
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ delete_auth_providers ]")
        ids = self.ldap_ids if ids is None else ids
        rc, stdout = common.delete_auth_providers(ids=ids, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'delete_auth_providers failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def get_auth_providers_ldap(self, ids=None, exit_flag=False):
        """查询LDAP认证服务器
        :param ids: Required:False  Type:string  Help:The authentication provider id list to get, e.g. 1,2,3
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ get_auth_providers_ldap ]")
        rc, stdout = common.get_auth_providers_ldap(ids=ids, print_flag=self.print_flag,
                                                    fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'get_auth_providers_ldap failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def check_auth_provider(self, exit_flag=False):
        """查询已有认证服务器是否可用
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ check_auth_provider ]")
        rc, stdout = common.check_auth_provider(id=self.p_id,
                                                print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'check_auth_provider failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg


class AuthProviderLdapPDC(AuthProviderLDAP):
    def __init__(self, name=None, base_dn=None, ip_addresses=None, port=None, bind_dn=None, bind_password=None,
                 domain_password=None, user_search_path=None, group_search_path=None,
                 print_flag=True, fault_node_ip=None):
        """LDAP-PDC认证服务器
        :param name: Required:True. 如果不输入，则使用这个名字：default_name
        :param base_dn: Required:True. 如果不输入，则读配置文件
        :param ip_addresses: Required:True. 如果不输入，则读配置文件
        :param port:
        :param bind_dn: 如果不输入，则读配置文件
        :param bind_password: 如果不输入，则读配置文件
        :param domain_password: 如果不输入，则读配置文件
        :param user_search_path: 如果不输入，则为None
        :param group_search_path: 如果不输入，则为None
        :param print_flag:
        :param fault_node_ip:
        """
        AuthProviderLDAP.__init__(self, name=name, base_dn=base_dn, ip_addresses=ip_addresses, port=port,
                                  bind_dn=bind_dn, bind_password=bind_password, domain_password=domain_password,
                                  user_search_path=user_search_path, group_search_path=group_search_path,
                                  print_flag=print_flag, fault_node_ip=fault_node_ip)
        self.bind_dn = ldap_pdc_bind_dn() if bind_dn is None else bind_dn
        self.bind_password = ldap_pdc_bind_password() if bind_password is None else bind_password
        self.domain_password = ldap_pdc_domain_password() if domain_password is None else domain_password
        self.user_search_path = user_search_path
        self.group_search_path = group_search_path


class AccessZone(NAS):
    def __init__(self, node_ids=None, name=None, auth_provider_id=None, isns_address=None,
                 print_flag=True, fault_node_ip=None):
        """访问区
        :param node_ids: Required:True. 若不输入，则使用全部节点
        :param name: Required:True.  若不输入，则使用这个名字：default_name
        :param auth_provider_id: 若不输入，则使用None，即本地认证服务器
        :param isns_address:
        :param print_flag:
        :param fault_node_ip:
        """
        NAS.__init__(self, print_flag, fault_node_ip)
        self.node_ids = get_node_ids() if node_ids is None else node_ids
        self.name = 'default_name' if name is None else name
        self.p_id = auth_provider_id
        self.isns_address = isns_address
        self.a_id = None
        self._a_ids = None

    def __str__(self):
        return '[node_ids: %s, name: %s, auth_provider_id: %s, ' \
               'isns_address: %s, a_id: %s, print_flag: %s, ' \
               'fault_node_ip: %s]' % (self.node_ids, self.name, self.p_id, self.isns_address, self.a_id,
                                       self.print_flag, self.fault_node_ip)

    @property
    def a_ids(self):
        msg = self.get_access_zones()
        ids = []
        for access_zone in msg['result']['access_zones']:
            ids.append(access_zone['id'])
        self._a_ids = ','.join(str(i) for i in ids)
        return self._a_ids

    def create_access_zone(self, exit_flag=False):
        """创建访问区
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ create_access_zone ]")
        rc, stdout = common.create_access_zone(node_ids=self.node_ids, name=self.name,
                                               auth_provider_id=self.p_id, isns_address=self.isns_address,
                                               print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, "create_access_zone failed", exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            self.a_id = msg['result']
        return msg

    def update_access_zone(self, name=None, node_ids=None, auth_provider_id=None, isns_address=None, exit_flag=False):
        """修改访问区
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ update_access_zone ]")
        rc, stdout = common.update_access_zone(id=self.a_id, name=name, node_ids=node_ids,
                                               auth_provider_id=auth_provider_id, isns_address=isns_address,
                                               print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'update_access_zone failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            if name is not None:
                self.name = name
            if node_ids is not None:
                self.node_ids = node_ids
            if auth_provider_id is not None:
                self.p_id = auth_provider_id
            if isns_address is not None:
                self.isns_address = isns_address
        return msg

    def delete_access_zone(self, exit_flag=False):
        """删除访问区
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ delete_access_zone ]")
        rc, stdout = common.delete_access_zone(id=self.a_id,
                                               print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'delete_access_zone failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def get_access_zones(self, ids=None, exit_flag=False):
        """查询访问区
        :param ids: Required:False  Type:string  Help:The access zone id list to get, e.g. 1,2,3
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ get_access_zones ]")
        rc, stdout = common.get_access_zones(ids=ids, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'get_access_zones failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def enable_nas(self, protocol_types=None, exit_flag=False):
        """启用协议
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ enable_nas ]")
        p1 = Process(target=record_info_for_enablenas, args=(get_config.get_allparastor_ips(),))
        p1.daemon = True
        p1.start()
        rc, stdout = common.enable_nas(access_zone_id=self.a_id, protocol_types=protocol_types,
                                       print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'enable_nas failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        p1.terminate()
        p1.join()
        return msg

    def disable_nas(self, protocol_types=None, exit_flag=False):
        """关闭协议
        :return:执行cmd命令的字典格式返回值
        """
        log.info("\t[ disable_nas ]")
        rc, stdout = common.disable_nas(access_zone_id=self.a_id, protocol_types=protocol_types,
                                        print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'disable_nas failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg


class Subnet(NAS):
    def __init__(self, access_zone_id, name=None, ip_family=None, svip=None, mask=None, gateway=None,
                 network_interfaces=None, mtu=None, description=None, print_flag=True, fault_node_ip=None):
        """子网
        :param access_zone_id: Required:True.
        :param name: Required:True. 若不输入，则使用这个名字：default_name
        :param ip_family: Required:True. 若不输入，则使用IPv4
        :param svip: Required:True. 若不输入，则读取配置文件
        :param mask: Required:True. 若不输入，则读取配置文件
        :param gateway:
        :param network_interfaces: Required:True. 如果不输入，则读取配置文件
        :param mtu:
        :param description:
        :param print_flag:
        :param fault_node_ip:
        """
        NAS.__init__(self, print_flag, fault_node_ip)
        self.access_zone_id = access_zone_id
        self.name = 'default_name' if name is None else name
        self.ip_family = 'IPv4' if ip_family is None else ip_family
        self.svip = subnet_svip() if svip is None else svip
        self.subnet_mask = subnet_mask() if mask is None else mask
        self.subnet_gateway = gateway
        self.network_interfaces = subnet_network_interfaces() if network_interfaces is None else network_interfaces
        self.mtu = mtu
        self.description = description
        self.subnet_id = None

    def __str__(self):
        return '[access_zone_id: %s, name: %s, ip_family: %s, svip: %s, subnet_mask: %s, subnet_gateway: %s, ' \
               'network_interfaces: %s, mtu: %s, description: %s, subnet_id: %s, ' \
               'print_flag: %s, fault_node_ip: %s]' % (self.access_zone_id, self.name, self.ip_family, self.svip,
                                                       self.subnet_mask, self.subnet_gateway, self.network_interfaces,
                                                       self.mtu, self.description, self.subnet_id,
                                                       self.print_flag, self.fault_node_ip)

    def create_subnet(self, exit_flag=False):
        """创建业务子网
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ create_subnet ]")
        rc, stdout = common.create_subnet(access_zone_id=self.access_zone_id, name=self.name, ip_family=self.ip_family,
                                          svip=self.svip, subnet_mask=self.subnet_mask,
                                          subnet_gateway=self.subnet_gateway,
                                          network_interfaces=self.network_interfaces, mtu=self.mtu,
                                          description=self.description,
                                          print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'create_subnet failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            self.subnet_id = msg['result']
        return msg

    def update_subnet(self, name=None, svip=None, mask=None, gateway=None, network_interfaces=None,
                      mtu=None, description=None, exit_flag=False):
        """修改子网
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ update_subnet ]")
        rc, stdout = common.update_subnet(id=self.subnet_id, name=name, svip=svip, subnet_mask=mask,
                                          subnet_gateway=gateway, network_interfaces=network_interfaces,
                                          mtu=mtu, description=description, print_flag=self.print_flag,
                                          fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'update_subnet failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            if name is not None:
                self.name = name
            if svip is not None:
                self.svip = svip
            if subnet_mask is not None:
                self.subnet_mask = mask
            if subnet_gateway is not None:
                self.subnet_gateway = gateway
            if network_interfaces is not None:
                self.network_interfaces = network_interfaces
            if mtu is not None:
                self.mtu = mtu
            if description is not None:
                self.description = description
        return msg

    def delete_subnet(self, exit_flag=False):
        """修改子网
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ delete_subnet ]")
        rc, stdout = common.delete_subnet(id=self.subnet_id,
                                          print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'delete_subnet failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def get_subnets(self, ids=None, exit_flag=False):
        """查询业务子网
        :param ids: Required:False  Type:string  Help:The subnet id list, e.g. 1,2,3
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ get_subnets ]")
        rc, stdout = common.get_subnets(ids=ids, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'get_subnets failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg


class VipAddressPool(NAS):
    def __init__(self, subnet_id, domain_name=None, vip_adds=None, supported_protocol=None,
                 allocation_method=None, load_balance_policy=None, ip_failover_policy=None, rebalance_policy=None,
                 print_flag=True, fault_node_ip=None):
        """vip地址池
        :param subnet_id: Required:True.
        :param domain_name: Required:True. 若不输入，则读取配置文件
        :param vip_adds: Required:True. 若不输入，则读取配置文件
        :param supported_protocol: Required:True. 若不输入，则默认为'NAS'
        :param allocation_method: Required:True. 若不输入，则默认为'DYNAMIC'
        :param load_balance_policy:
        :param ip_failover_policy:
        :param rebalance_policy:
        :param print_flag:
        :param fault_node_ip:
        """
        NAS.__init__(self, print_flag, fault_node_ip)
        self.subnet_id = subnet_id
        self.domain_name = vip_domain_name() if domain_name is None else domain_name
        self.vip_addresses = vip_addresses() if vip_adds is None else vip_adds
        self.supported_protocol = 'NAS' if supported_protocol is None else supported_protocol
        self.allocation_method = 'DYNAMIC' if allocation_method is None else allocation_method
        self.load_balance_policy = load_balance_policy
        self.ip_failover_policy = ip_failover_policy
        self.rebalance_policy = rebalance_policy
        self.subnet_id = subnet_id
        self.vip_address_pool_id = None

    def __str__(self):
        return '[subnet_id: %s, domain_name: %s, vip_addresses: %s, supported_protocol: %s, allocation_method: %s, ' \
               'load_balance_policy: %s, ip_failover_policy: %s, rebalance_policy: %s, vip_address_pool_id: %s, ' \
               'print_flag: %s, fault_node_ip: %s]' % (self.subnet_id, self.domain_name, self.vip_addresses,
                                                       self.supported_protocol, self.allocation_method,
                                                       self.load_balance_policy, self.ip_failover_policy,
                                                       self.rebalance_policy, self.vip_address_pool_id,
                                                       self.print_flag, self.fault_node_ip)

    def add_vip_address_pool(self, exit_flag=False):
        """增加vip地址池
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ add_vip_address_pool ]")
        rc, stdout = common.add_vip_address_pool(subnet_id=self.subnet_id, domain_name=self.domain_name,
                                                 vip_addresses=self.vip_addresses,
                                                 supported_protocol=self.supported_protocol,
                                                 allocation_method=self.allocation_method,
                                                 load_balance_policy=self.load_balance_policy,
                                                 ip_failover_policy=self.ip_failover_policy,
                                                 rebalance_policy=self.rebalance_policy,
                                                 print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'add_vip_address_pool failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            self.vip_address_pool_id = msg['result']
        return msg

    def update_vip_address_pool(self, domain_name=None, vip_adds=None, load_balance_policy=None,
                                ip_failover_policy=None, rebalance_policy=None, exit_flag=False):
        """修改vip地址池
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ update_vip_address_pool ]")
        rc, stdout = common.update_vip_address_pool(id=self.vip_address_pool_id, domain_name=domain_name,
                                                    vip_addresses=vip_adds,
                                                    load_balance_policy=load_balance_policy,
                                                    ip_failover_policy=ip_failover_policy,
                                                    rebalance_policy=rebalance_policy,
                                                    print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'update_vip_address_pool failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            if domain_name is not None:
                self.domain_name = domain_name
            if vip_adds is not None:
                self.vip_addresses = vip_adds
            if load_balance_policy is not None:
                self.load_balance_policy = load_balance_policy
            if rebalance_policy is not None:
                self.rebalance_policy = rebalance_policy
        return msg

    def delete_vip_address_pool(self, exit_flag=False):
        """删除vip地址池
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ delete_vip_address_pool ]")
        rc, stdout = common.delete_vip_address_pool(id=self.vip_address_pool_id, print_flag=self.print_flag,
                                                    fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'delete_vip_address_pool failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def get_vip_address_pools(self, ids=None, exit_flag=False):
        """查询vip地址池
        :param ids: Required:False  Type:string  Help:The vip address pool id list, e.g. 1,2,3
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ get_vip_address_pools ]")
        rc, stdout = common.get_vip_address_pools(ids=ids, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'get_vip_address_pools failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg


class File(NAS):
    def __init__(self, path, posix_permission=None, print_flag=True, fault_node_ip=None):
        """目录
        :param path: Required:True   Type:string  Help:The path to be created. e.g. volume:/dir
        :param posix_permission: Required:False  Type:string  Help:POSIX file permission, e.g. rwxr-xr-x
        :param print_flag:
        :param fault_node_ip:
        """
        NAS.__init__(self, print_flag, fault_node_ip)
        self.path = path
        self.posix_permission = posix_permission

    def __str__(self):
        return '[path: %s, posix_permission: %s, ' \
               'print_flag: %s, fault_node_ip: %s]' % (self.path, self.posix_permission,
                                                       self.print_flag, self.fault_node_ip)

    def create_file(self, exit_flag=False):
        """创建目录
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ create_file ]")
        rc, stdout = common.create_file(path=self.path, posix_permission=self.posix_permission,
                                        print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'create_file failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def update_file(self, posix_permission, exit_flag=False):
        """修改目录
        :param posix_permission: Required:True   Type:string  Help:POSIX file permission, e.g. rwxr-xr-x
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ update_file ]")
        rc, stdout = common.update_file(path=self.path, posix_permission=posix_permission, print_flag=self.print_flag,
                                        fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'update_file failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            self.posix_permission = posix_permission
        return msg

    def delete_file(self, path, exit_flag=False):
        """删除目录
        :param path: Required:True   Type:string  Help:The path to be deleted. e.g. volume:/dir
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ delete_file ]")
        rc, stdout = common.delete_file(path=path, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'delete_file failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def get_file_list(self, path, file_type=None, display_details=None, start=None, limit=None, exit_flag=False):
        """查询目录（文件系统浏览）
        :param path: Required:True   Type:string  Help:The path to be listed. e.g. volume:/dir
        :param file_type: Required:False  Type:string  Help:File type, available file type:['FILE', 'DIR']
        :param display_details: Required:False  Type:bool    Help:Display detail messages, like 'ls -l' in the Linux.
        :param start: Required:False  Type:int     Help:The start index in the result.
        :param limit: Required:False  Type:int     Help:The records size in each query.
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ get_file_list ]")
        rc, stdout = common.get_file_list(path=path, type=file_type, display_details=display_details, start=start,
                                          limit=limit, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'get_file_list failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg


class AuthUser(NAS):
    def __init__(self, auth_provider_id, primary_group_id, secondary_group_ids=None, name=None, password=None,
                 home_dir=None, print_flag=True, fault_node_ip=None):
        """用户
        :param auth_provider_id: Required:True   Type:int     Help:The ID of LOCAL type authentication provider
        :param primary_group_id: Required:True   Type:int     Help:The primary group ID where this user in.
        :param secondary_group_ids: Required:False  Type:string  Help:The secondary group ID list where this user in.
        :param name: Required:True  Type:string  若不输入，则使用这个名字：default_name
        :param password: Required:True  Type:string  若不输入，则默认为：111111
        :param home_dir:
        :param print_flag:
        :param fault_node_ip:
        """
        NAS.__init__(self, print_flag, fault_node_ip)
        self.auth_provider_id = auth_provider_id
        self.primary_group_id = primary_group_id
        self.secondary_group_ids = secondary_group_ids
        self.name = 'default_name' if name is None else name
        self.password = '111111' if password is None else password
        self.home_dir = home_dir
        self.u_id = None      # 本用户
        self._u_ids = None    # self.auth_provider_id内全部用户

    def __str__(self):
        return '[auth_provider_id: %s, primary_group_id: %s, secondary_group_ids: %s, ' \
               'name: %s, password: %s, home_dir: %s, u_id: %s, ' \
               'print_flag: %s, fault_node_ip: %s]' % (self.auth_provider_id, self.primary_group_id,
                                                       self.secondary_group_ids, self.name, self.password,
                                                       self.home_dir, self.u_id, self.print_flag, self.fault_node_ip)

    @property
    def u_ids(self):
        msg = self.get_auth_users()
        ids = []
        for auth_user in msg['result']['auth_users']:
            ids.append(auth_user['id'])
        self._u_ids = ','.join(str(i) for i in ids)
        return self._u_ids

    def create_auth_user(self, exit_flag=False):
        """创建本地认证用户
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ create_auth_user ]")
        rc, stdout = common.create_auth_user(auth_provider_id=self.auth_provider_id, name=self.name,
                                             password=self.password, primary_group_id=self.primary_group_id,
                                             secondary_group_ids=self.secondary_group_ids, home_dir=self.home_dir,
                                             print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'create_auth_user failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            self.u_id = msg['result']
        return msg

    def update_auth_user(self, password=None, primary_group_id=None, secondary_group_ids=None, print_flag=True,
                         fault_node_ip=None, exit_flag=False):
        """修改本地认证用户
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ update_auth_user ]")
        rc, stdout = common.update_auth_user(id=self.u_id, password=password, primary_group_id=primary_group_id,
                                             secondary_group_ids=secondary_group_ids, print_flag=print_flag,
                                             fault_node_ip=fault_node_ip)
        common.judge_rc(rc, 0, 'update_auth_user failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            if password is not None:
                self.password = password
            if primary_group_id is not None:
                self.primary_group_id = primary_group_id
            if secondary_group_ids is not None:
                self.secondary_group_ids = secondary_group_ids
        return msg

    def delete_auth_users(self, ids=None, exit_flag=False):
        """删除本地认证用户
        :param ids: 不输入则删除本认证服务器(self.auth_provider_id)内的全部用户，输入则删除指定用户。格式如下：e.g. 1,2,3,4
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ delete_auth_users ]")
        ids = self.u_ids if ids is None else ids
        rc, stdout = common.delete_auth_users(ids=ids, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'delete_auth_users failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def get_auth_users(self, group_id=None, start=None, limit=None, exit_flag=False):
        """查询认证用户
        :param group_id: Required:False  Type:int     Help:The group ID of authentication users.
        :param start: Required:False  Type:int     Help:The start index in the query result.
        :param limit: Required:False  Type:int     Help:The record numbers to display in once query.
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ get_auth_users ]")
        rc, stdout = common.get_auth_users(auth_provider_id=self.auth_provider_id, group_id=group_id,
                                           start=start, limit=limit,
                                           print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'get_auth_users failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg


class AuthGroup(NAS):
    def __init__(self, auth_provider_id, name=None, print_flag=True, fault_node_ip=None):
        """用户组
        :param auth_provider_id: Required:True   Type:int     Help:The ID of LOCAL type authentication provider
        :param name: Required:True   Type:string  Help:Group name. 若不输入，则使用这个名字：default_name
        :param print_flag:
        :param fault_node_ip:
        """
        NAS.__init__(self, print_flag, fault_node_ip)
        self.auth_provider_id = auth_provider_id
        self.name = 'default_name' if name is None else name
        self.g_id = None    # 本用户组
        self._g_ids = None  # self.auth_provider_id中全部用户

    def __str__(self):
        return '[auth_provider_id: %s, name: %s, g_id: %s, ' \
               'print_flag: %s, fault_node_ip: %s]' % (self.auth_provider_id, self.name, self.g_id,
                                                       self.print_flag, self.fault_node_ip)

    @property
    def g_ids(self):
        msg = self.get_auth_groups()
        ids = []
        for auth_user in msg['result']['auth_groups']:
            ids.append(auth_user['id'])
        self._g_ids = ','.join(str(i) for i in ids)
        return self._g_ids

    def create_auth_group(self, exit_flag=False):
        """创建本地认证用户组
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ create_auth_group ]")
        rc, stdout = common.create_auth_group(auth_provider_id=self.auth_provider_id, name=self.name,
                                              print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'create_auth_group failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            self.g_id = msg['result']
        return msg

    def delete_auth_groups(self, ids=None, exit_flag=False):
        """删除本地认证用户组
        :param ids: 不输入则删除本认证服务器(self.auth_provider_id)内的全部用户组，输入则删除指定用户组。格式如下：e.g. 1,2,3,4
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ delete_auth_groups ]")
        ids = self.g_ids if ids is None else ids
        rc, stdout = common.delete_auth_groups(ids=ids, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'delete_auth_groups failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def get_auth_groups(self, start=None, limit=None, exit_flag=False):
        """查询本地认证用户组
        :param start: Required:False  Type:int     Help:The start index in the query result.
        :param limit: Required:False  Type:int     Help:The record numbers to display in once query.
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ get_auth_groups ]")
        rc, stdout = common.get_auth_groups(auth_provider_id=self.auth_provider_id, start=start, limit=limit,
                                            print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'get_auth_groups failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg


class ExportProtocol(NAS):
    def __init__(self, export_path=None, print_flag=True, fault_node_ip=None):
        """
        :param export_path: 如果不输入，则读配置文件（值为NAS测试的根目录：/mnt/volume/nas_test_dir）
        :param print_flag:
        :param fault_node_ip:
        """
        NAS.__init__(self, print_flag, fault_node_ip)
        self.export_path = root_dir() if export_path is None else export_path


class SmbExport(ExportProtocol):
    def __init__(self, access_zone_id, export_name=None, export_path=None, description=None,
                 enable_ntfs_acl=None, allow_create_ntfs_acl=None, enable_alternative_datasource=None,
                 enable_dos_attributes=None, enable_os2style_ex_attrs=None, enable_guest=None,
                 enable_oplocks=None, authorization_ip=None, print_flag=True, fault_node_ip=None):
        """SMB导出
        :param access_zone_id: Required:True.
        :param export_name: Required:True. 如果不输入，则使用这个名字：default_name
        :param export_path: Required:True.
        :param description:
        :param enable_ntfs_acl:
        :param allow_create_ntfs_acl:
        :param enable_alternative_datasource:
        :param enable_dos_attributes:
        :param enable_os2style_ex_attrs:
        :param enable_guest:
        :param enable_oplocks:
        :param authorization_ip:
        :param print_flag:
        :param fault_node_ip:
        """
        ExportProtocol.__init__(self, export_path, print_flag, fault_node_ip)
        self.access_zone_id = access_zone_id
        self.export_name = 'default_name' if export_name is None else export_name
        self.description = description
        self.enable_ntfs_acl = enable_ntfs_acl
        self.allow_create_ntfs_acl = allow_create_ntfs_acl
        self.enable_alternative_datasource = enable_alternative_datasource
        self.enable_dos_attributes = enable_dos_attributes
        self.enable_os2style_ex_attrs = enable_os2style_ex_attrs
        self.enable_guest = enable_guest
        self.enable_oplocks = enable_oplocks
        self.authorization_ip = authorization_ip
        self.export_id = None   # 本smb导出
        self._smb_ids = None    # 全部smb导出

    def __str__(self):
        return '[access_zone_id: %s, export_name: %s, export_path: %s, ' \
               'description: %s, enable_ntfs_acl: %s, allow_create_ntfs_acl: %s, ' \
               'enable_alternative_datasource: %s, enable_dos_attributes: %s, enable_os2style_ex_attrs: %s, ' \
               'enable_guest: %s, enable_oplocks: %s, authorization_ip: %s, export_id: %s, ' \
               'print_flag: %s, fault_node_ip: %s]' % (self.access_zone_id, self.export_name, self.export_path,
                                                       self.description, self.enable_ntfs_acl,
                                                       self.allow_create_ntfs_acl, self.enable_alternative_datasource,
                                                       self.enable_dos_attributes, self.enable_os2style_ex_attrs,
                                                       self.enable_guest, self.enable_oplocks, self.authorization_ip,
                                                       self.export_id, self.print_flag, self.fault_node_ip)

    @property
    def smb_ids(self):
        msg = self.get_smb_exports()
        ids = []
        for export in msg['result']['exports']:
            ids.append(export['id'])
        self._smb_ids = ','.join(str(i) for i in ids)
        return self._smb_ids

    def create_smb_export(self, exit_flag=False):
        """创建SMB共享
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ create_smb_export ]")
        rc, stdout = common.create_smb_export(access_zone_id=self.access_zone_id, export_name=self.export_name,
                                              export_path=self.export_path, description=self.description,
                                              enable_ntfs_acl=self.enable_ntfs_acl,
                                              allow_create_ntfs_acl=self.allow_create_ntfs_acl,
                                              enable_alternative_datasource=self.enable_alternative_datasource,
                                              enable_dos_attributes=self.enable_dos_attributes,
                                              enable_os2style_ex_attrs=self.enable_os2style_ex_attrs,
                                              enable_guest=self.enable_guest, enable_oplocks=self.enable_oplocks,
                                              authorization_ip=self.authorization_ip, print_flag=self.print_flag,
                                              fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'create_smb_export failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            self.export_id = msg['result']
        return msg

    def update_smb_export(self, description=None, enable_ntfs_acl=None, allow_create_ntfs_acl=None,
                          enable_alternative_datasource=None, enable_dos_attributes=None,
                          enable_os2style_ex_attrs=None, enable_guest=None, enable_oplocks=None,
                          authorization_ip=None, exit_flag=False):
        """修改SMB共享
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ update_smb_export ]")
        rc, stdout = common.update_smb_export(id=self.export_id, description=description,
                                              enable_ntfs_acl=enable_ntfs_acl,
                                              allow_create_ntfs_acl=allow_create_ntfs_acl,
                                              enable_alternative_datasource=enable_alternative_datasource,
                                              enable_dos_attributes=enable_dos_attributes,
                                              enable_os2style_ex_attrs=enable_os2style_ex_attrs,
                                              enable_guest=enable_guest, enable_oplocks=enable_oplocks,
                                              authorization_ip=authorization_ip,
                                              print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'update_smb_export failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            if description is not None:
                self.description = description
            if enable_ntfs_acl is not None:
                self.enable_ntfs_acl = enable_ntfs_acl
            if allow_create_ntfs_acl is not None:
                self.allow_create_ntfs_acl = allow_create_ntfs_acl
            if enable_alternative_datasource is not None:
                self.enable_alternative_datasource = enable_alternative_datasource
            if enable_dos_attributes is not None:
                self.enable_dos_attributes = enable_dos_attributes
            if enable_os2style_ex_attrs is not None:
                self.enable_os2style_ex_attrs = enable_os2style_ex_attrs
            if enable_guest is not None:
                self.enable_guest = enable_guest
            if enable_oplocks is not None:
                self.enable_oplocks = enable_oplocks
            if authorization_ip is not None:
                self.authorization_ip = authorization_ip
        return msg

    def delete_smb_exports(self, ids=None, exit_flag=False):
        """删除SMB共享
        :param ids: Required:True   Type:string  Help:The smb export id list.
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ delete_smb_exports ]")
        ids = self.smb_ids if ids is None else ids
        rc, stdout = common.delete_smb_exports(ids=ids, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'delete_smb_exports failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def get_smb_exports(self, ids=None, exit_flag=False):
        """查询SMB共享
        :param ids: Required:False  Type:string  Help:The id list of smb exports
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ get_smb_exports ]")
        rc, stdout = common.get_smb_exports(ids=ids, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'get_smb_exports failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg


class NfsExport(ExportProtocol):
    def __init__(self, access_zone_id, export_name=None, export_path=None, description=None,
                 print_flag=True, fault_node_ip=None):
        """NFS导出
        :param access_zone_id: Required:True.
        :param export_name: Required:True. 如果不输入，则使用这个名字：default_name
        :param export_path: Required:True.
        :param description:
        :param print_flag:
        :param fault_node_ip:
        """
        ExportProtocol.__init__(self, export_path, print_flag, fault_node_ip)
        self.access_zone_id = access_zone_id
        self.export_name = 'default_name' if export_name is None else export_name
        self.description = description
        self.export_id = None   # 本nfs导出
        self._nfs_ids = None    # 全部nfs导出

    def __str__(self):
        return '[access_zone_id: %s, export_name: %s, export_path: %s, description: %s, export_id: %s, ' \
               'print_flag: %s, fault_node_ip: %s]' % (self.access_zone_id, self.export_name, self.export_path,
                                                       self.description, self.export_id,
                                                       self.print_flag, self.fault_node_ip)

    @property
    def nfs_ids(self):
        msg = self.get_nfs_exports()
        ids = []
        for export in msg['result']['exports']:
            ids.append(export['id'])
        self._nfs_ids = ','.join(str(i) for i in ids)
        return self._nfs_ids

    def create_nfs_export(self, exit_flag=False):
        """创建NFS共享
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ create_nfs_export ]")
        rc, stdout = common.create_nfs_export(access_zone_id=self.access_zone_id, export_name=self.export_name,
                                              export_path=self.export_path, description=self.description,
                                              print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'create_nfs_export failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            self.export_id = msg['result']
        return msg

    def update_nfs_export(self, description=None, exit_flag=False):
        """修改NFS共享
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ update_nfs_export ]")
        rc, stdout = common.update_nfs_export(id=self.export_id, description=description,
                                              print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'update_nfs_export failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0 and description is not None:
            self.description = description
        return msg

    def delete_nfs_exports(self, ids=None, exit_flag=False):
        """删除NFS共享
        :param ids:  Required:True   Type:string  Help:The nfs export id list.
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ delete_nfs_exports ]")
        ids = self.nfs_ids if ids is None else ids
        rc, stdout = common.delete_nfs_exports(ids=ids, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'delete_nfs_exports failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def get_nfs_exports(self, ids=None, exit_flag=False):
        """查询NFS共享
        :param ids: Required:False  Type:string  Help:The id list of nfs exports
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ get_nfs_exports ]")
        rc, stdout = common.get_nfs_exports(ids=ids, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'get_nfs_exports failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg


def get_ftp_user_by_type(provider_type):
    ftp_user_name = ''
    if provider_type == 'AD':
        ftp_user_name = ad_user_1_name()
    elif provider_type == 'NIS':
        ftp_user_name = nis_user_1_name()
    elif provider_type == 'LOCAL':
        ftp_user_name = 'default_local_user'
    return ftp_user_name


def get_ftp_user(access_zone_id, provider_type):
    """从配置文件中获取ftp用户
    :param access_zone_id:
    :param provider_type:
    :return:
    """
    if provider_type is None:
        msg = common.get_access_zones(ids=access_zone_id)
        provider_type = msg['result']['access_zones'][0]['auth_provider']['type']
        if provider_type == 'LDAP':
            provider_id = msg['result']['access_zones'][0]['auth_provider']['id']
            msg = common.get_auth_providers_ldap(ids=provider_id)
            auth_provider = msg['result']['auth_providers'][0]
            ftp_user_name = ldap_user_1_name() if 'bind_dn' not in auth_provider else ldap_pdc_user_1_name()
        else:
            ftp_user_name = get_ftp_user_by_type(provider_type)
    else:   # 用户主动输入的认证服务器类型
        if provider_type == 'LDAP':
            ftp_user_name = ldap_user_1_name()
        elif provider_type == 'LDAP-PDC':
            ftp_user_name = ldap_pdc_user_1_name()
        else:
            ftp_user_name = get_ftp_user_by_type(provider_type)
    return ftp_user_name


class FtpExport(ExportProtocol):
    def __init__(self, access_zone_id, provider_type=None, user_name=None, export_path=None, enable_dirlist=None,
                 enable_create_folder=None, enable_delete_and_rename=None, enable_upload=None,
                 upload_local_max_rate=None, enable_download=None, download_local_max_rate=None,
                 print_flag=True, fault_node_ip=None):
        """FTP导出
        :param access_zone_id: Required:True
        :param provider_type: Required:True. 使用的认证服务器类型，可选值：LDAP, LDAP-PDC, AD, NIS, LOCAL，不输入则通过get命令获取
        :param user_name: Required:True. 不输入，则根据provider_type类型，从配置文件中获取
        :param export_path: Required:True
        :param enable_dirlist:
        :param enable_create_folder:
        :param enable_delete_and_rename:
        :param enable_upload:
        :param upload_local_max_rate:
        :param enable_download:
        :param download_local_max_rate:
        :param print_flag:
        :param fault_node_ip:
        """
        ExportProtocol.__init__(self, export_path, print_flag, fault_node_ip)
        self.access_zone_id = access_zone_id
        self.provider_type = provider_type
        self.user_name = get_ftp_user(self.access_zone_id, self.provider_type) if user_name is None else user_name
        self.enable_dirlist = enable_dirlist
        self.enable_create_folder = enable_create_folder
        self.enable_delete_and_rename = enable_delete_and_rename
        self.enable_upload = enable_upload
        self.upload_local_max_rate = upload_local_max_rate
        self.enable_download = enable_download
        self.download_local_max_rate = download_local_max_rate
        self.export_id = None   # 本ftp导出
        self._ftp_ids = None    # 全部ftp导出

    def __str__(self):
        return '[access_zone_id: %s, provider_type: %s, user_name: %s, export_path: %s, ' \
               'enable_dirlist: %s, enable_create_folder: %s, enable_delete_and_rename: %s, ' \
               'enable_upload: %s, upload_local_max_rate: %s, enable_download: %s, ' \
               'download_local_max_rate: %s, export_id: %s, print_flag: %s, ' \
               'fault_node_ip: %s]' % (self.access_zone_id, self.provider_type, self.user_name, self.export_path,
                                       self.enable_dirlist, self.enable_create_folder, self.enable_delete_and_rename,
                                       self.enable_upload, self.upload_local_max_rate, self.enable_download,
                                       self.download_local_max_rate, self.export_id,
                                       self.print_flag, self.fault_node_ip)

    @property
    def ftp_ids(self):
        msg = self.get_ftp_exports()
        ids = []
        for export in msg['result']['exports']:
            ids.append(export['id'])
        self._ftp_ids = ','.join(str(i) for i in ids)
        return self._ftp_ids

    def create_ftp_export(self, exit_flag=False):
        """创建FTP导出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ create_ftp_export ]")
        rc, stdout = common.create_ftp_export(access_zone_id=self.access_zone_id, user_name=self.user_name,
                                              export_path=self.export_path, enable_dirlist=self.enable_dirlist,
                                              enable_create_folder=self.enable_create_folder,
                                              enable_delete_and_rename=self.enable_delete_and_rename,
                                              enable_upload=self.enable_upload,
                                              upload_local_max_rate=self.upload_local_max_rate,
                                              enable_download=self.enable_download,
                                              download_local_max_rate=self.download_local_max_rate,
                                              print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'create_ftp_export failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            self.export_id = msg['result']
        return msg

    def update_ftp_export(self, export_path=None, enable_dirlist=None, enable_create_folder=None,
                          enable_delete_and_rename=None, enable_upload=None, upload_local_max_rate=None,
                          enable_download=None, download_local_max_rate=None, exit_flag=False):
        """修改FTP导出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ update_ftp_export ]")
        rc, stdout = common.update_ftp_export(id=self.export_id, export_path=export_path, enable_dirlist=enable_dirlist,
                                              enable_create_folder=enable_create_folder,
                                              enable_delete_and_rename=enable_delete_and_rename,
                                              enable_upload=enable_upload,
                                              upload_local_max_rate=upload_local_max_rate,
                                              enable_download=enable_download,
                                              download_local_max_rate=download_local_max_rate,
                                              print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'update_ftp_export failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            if export_path is not None:
                self.export_path = export_path
            if enable_dirlist is not None:
                self.enable_dirlist = enable_dirlist
            if enable_create_folder is not None:
                self.enable_create_folder = enable_create_folder
            if enable_delete_and_rename is not None:
                self.enable_delete_and_rename = enable_delete_and_rename
            if enable_upload is not None:
                self.enable_upload = enable_upload
            if upload_local_max_rate is not None:
                self.upload_local_max_rate = upload_local_max_rate
            if enable_download is not None:
                self.enable_download = enable_download
            if download_local_max_rate is not None:
                self.download_local_max_rate = download_local_max_rate
        return msg

    def delete_ftp_exports(self, ids=None, exit_flag=False):
        """删除FTP共享
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ delete_ftp_exports ]")
        ids = self.ftp_ids if ids is None else ids
        rc, stdout = common.delete_ftp_exports(ids=ids, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'delete_ftp_exports failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def get_ftp_exports(self, ids=None, exit_flag=False):
        """查询FTP共享
        :param ids: Required:False  Type:string  Help:The id list of ftp exports
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ get_ftp_exports ]")
        rc, stdout = common.get_ftp_exports(ids=ids, print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'get_ftp_exports failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg


def get_smb_user_by_type(user_type, provider_type):
    smb_user_name = ''
    if provider_type == 'AD':
        smb_user_name = ad_user_1_name() if user_type == 'USER' else ad_group_1_name()
    elif provider_type == 'NIS':
        smb_user_name = nis_user_1_name() if user_type == 'USER' else nis_group_1_name()
    elif provider_type == 'LOCAL':
        smb_user_name = 'default_local_user' if user_type == 'USER' else 'default_local_group'
    return smb_user_name


def get_smb_user(export_id, user_type, provider_type):
    """从配置文件获取smb用户
    :param export_id:
    :param user_type:
    :param provider_type:
    :return:
    """
    if provider_type is None:
        msg = common.get_smb_exports(ids=export_id)
        access_zone_id = msg['result']['exports'][0]['access_zone_id']
        msg = common.get_access_zones(ids=access_zone_id)
        provider_type = msg["result"]["access_zones"][0]["auth_provider"]["type"]
        if provider_type == "LDAP":
            provider_id = msg["result"]["access_zones"][0]["auth_provider"]["id"]
            msg = common.get_auth_providers_ldap(ids=provider_id)
            auth_provider = msg['result']['auth_providers'][0]
            if user_type == 'USER':
                smb_user_name = ldap_user_1_name() if 'bind_dn' not in auth_provider else ldap_pdc_user_1_name()
            else:
                smb_user_name = ldap_group_1_name() if 'bind_dn' not in auth_provider else ldap_pdc_group_1_name()
        else:
            smb_user_name = get_smb_user_by_type(user_type, provider_type)
    else:   # 用户主动输入的认证服务器类型
        if provider_type == 'LDAP':
            smb_user_name = ldap_user_1_name() if user_type == 'USER' else ldap_group_1_name()
        elif provider_type == 'LDAP-PDC':
            smb_user_name = ldap_pdc_user_1_name() if user_type == 'USER' else ldap_pdc_group_1_name()
        else:
            smb_user_name = get_smb_user_by_type(user_type, provider_type)
    return smb_user_name


class SmbExportAuthClient(NAS):
    def __init__(self, export_id, provider_type=None, name=None, user_type=None, run_as_root=None,
                 permission_level=None, print_flag=True, fault_node_ip=None):
        """SMB授权用户
        :param export_id: Required:True.
        :param provider_type: 使用的认证服务器类型，输入则为下值中的一个：LDAP, LDAP-PDC, AD, NIS, LOCAL，不输入则通过get_xxx命令获取
        :param name: Required:True. 不输入，则根据provider_type和user_type类型，从配置文件中获取
        :param user_type: Required:True. 不输入，则从['USER', 'GROUP']中随机选取一个
        :param run_as_root: Required:True. 不输入，则从['true', 'false']中随机选取一个
        :param permission_level:
        :param print_flag:
        :param fault_node_ip:
        """
        NAS.__init__(self, print_flag, fault_node_ip)
        self.export_id = export_id
        self.provider_type = provider_type
        self.user_type = random.choice(['USER', 'GROUP']) if user_type is None else user_type
        self.name = get_smb_user(self.export_id, self.user_type, self.provider_type) if name is None else name
        self.run_as_root = random.choice(['true', 'false']) if run_as_root is None else run_as_root
        if self.run_as_root is 'true':
            self.permission_level = permission_level
        else:
            self.permission_level = 'full_control' if permission_level is None else permission_level
        self.auth_client_id = None      # 本smb授权策略
        self._auth_client_ids = None    # 全部smb授权策略

    def __str__(self):
        return '[export_id: %s, provider_type: %s, name: %s, user_type: %s, ' \
               'run_as_root: %s, permission_level: %s, auth_client_id: %s, ' \
               'print_flag: %s, fault_node_ip: %s]' % (self.export_id, self.provider_type, self.name, self.user_type,
                                                       self.run_as_root, self.permission_level, self.auth_client_id,
                                                       self.print_flag, self.fault_node_ip)

    @property
    def auth_client_ids(self):
        msg = self.get_smb_export_auth_clients()
        ids = []
        for smb_export_auth_client in msg['result']['smb_export_auth_clients']:
            ids.append(smb_export_auth_client['id'])
        self._auth_client_ids = ','.join(str(i) for i in ids)
        return self._auth_client_ids

    def add_smb_export_auth_clients(self, exit_flag=False):
        """增加SMB用户/用户组
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ add_smb_export_auth_clients ]")
        rc, stdout = common.add_smb_export_auth_clients(export_id=self.export_id, name=self.name, type=self.user_type,
                                                        run_as_root=self.run_as_root,
                                                        permission_level=self.permission_level,
                                                        print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'add_smb_export_auth_clients failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            self.auth_client_id = msg['result'][0]
        return msg

    def update_smb_export_auth_client(self, run_as_root=None, permission_level=None, exit_flag=False):
        """修改SMB用户/用户组,
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ update_smb_export_auth_client ]")
        rc, stdout = common.update_smb_export_auth_client(id=self.auth_client_id, run_as_root=run_as_root,
                                                          permission_level=permission_level,
                                                          print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'update_smb_export_auth_client failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            if run_as_root is not None:
                self.run_as_root = run_as_root
            if permission_level is not None:
                self.permission_level = permission_level
        return msg

    def remove_smb_export_auth_clients(self, ids=None, exit_flag=False):
        """移除SMB用户/用户组
        :param ids: Required:True   Type:string  Help:The authorization client id list.
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ remove_smb_export_auth_clients ]")
        ids = self.auth_client_ids if ids is None else ids
        rc, stdout = common.remove_smb_export_auth_clients(ids=ids,
                                                           print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'remove_smb_export_auth_clients failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def get_smb_export_auth_clients(self, export_ids=None, exit_flag=False):
        """查询SMB用户/用户组列表
        :param export_ids: Required:False  Type:string  Help:The smb export id list.
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ get_smb_export_auth_clients ]")
        rc, stdout = common.get_smb_export_auth_clients(export_ids=export_ids, print_flag=self.print_flag,
                                                        fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'get_smb_export_auth_clients failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg


class NfsExportAuthClient(NAS):
    def __init__(self, export_id, name=None, permission_level=None, write_mode=None, port_constraint=None,
                 permission_constraint=None, anonuid=None, anongid=None, print_flag=True, fault_node_ip=None):
        """NFS授权用户
        :param export_id: Required:True
        :param name: Required:True. 不输入则默认为*，即授权全部客户端
        :param permission_level: Required:True. 不输入则默认为rw，即有读写（包括delete和rename）权限
        :param write_mode:
        :param port_constraint:
        :param permission_constraint:
        :param anonuid:
        :param anongid:
        :param print_flag:
        :param fault_node_ip:
        """
        NAS.__init__(self, print_flag, fault_node_ip)
        self.export_id = export_id
        self.name = '*' if name is None else name
        self.permission_level = 'rw' if permission_level is None else permission_level
        self.write_mode = write_mode
        self.port_constraint = port_constraint
        self.permission_constraint = permission_constraint
        self.anonuid = anonuid
        self.anongid = anongid
        self.auth_client_id = None      # 本nfs授权策略
        self._auth_client_ids = None    # 全部nfs授权策略

    def __str__(self):
        return '[export_id: %s, name: %s, permission_level: %s, write_mode: %s, port_constraint: %s, ' \
               'permission_constraint: %s, anonuid: %s, anongid: %s, auth_client_id: %s, ' \
               'print_flag: %s, fault_node_ip: %s]' % (self.export_id, self.name, self.permission_level,
                                                       self.write_mode, self.port_constraint,
                                                       self.permission_constraint,
                                                       self.anonuid, self.anongid, self.auth_client_id,
                                                       self.print_flag, self.fault_node_ip)

    @property
    def auth_client_ids(self):
        msg = self.get_nfs_export_auth_clients()
        ids = []
        for nfs_export_auth_client in msg['result']['nfs_export_auth_clients']:
            ids.append(nfs_export_auth_client['id'])
        self._auth_client_ids = ','.join(str(i) for i in ids)
        return self._auth_client_ids

    def add_nfs_export_auth_clients(self, exit_flag=False):
        """增加NFS客户端
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ add_nfs_export_auth_clients ]")
        rc, stdout = common.add_nfs_export_auth_clients(export_id=self.export_id, name=self.name,
                                                        permission_level=self.permission_level,
                                                        write_mode=self.write_mode,
                                                        port_constraint=self.port_constraint,
                                                        permission_constraint=self.permission_constraint,
                                                        anonuid=self.anonuid, anongid=self.anongid,
                                                        print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'add_nfs_export_auth_clients failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            self.auth_client_id = msg['result'][0]
        return msg

    def update_nfs_export_auth_client(self, permission_level=None, write_mode=None,
                                      port_constraint=None, permission_constraint=None,
                                      anonuid=None, anongid=None, exit_flag=False):
        """修改NFS客户端
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
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ update_nfs_export_auth_client ]")
        rc, stdout = common.update_nfs_export_auth_client(id=self.auth_client_id, permission_level=permission_level,
                                                          write_mode=write_mode, port_constraint=port_constraint,
                                                          permission_constraint=permission_constraint, anonuid=anonuid,
                                                          anongid=anongid, print_flag=self.print_flag,
                                                          fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'update_nfs_export_auth_client failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        if rc is 0:
            if permission_level is not None:
                self.permission_level = permission_level
            if write_mode is not None:
                self.write_mode = write_mode
            if port_constraint is not None:
                self.port_constraint = port_constraint
            if permission_constraint is not None:
                self.permission_constraint = permission_constraint
            if anonuid is not None:
                self.anonuid = anonuid
            if anongid is not None:
                self.anongid = anongid
        return msg

    def remove_nfs_export_auth_clients(self, ids=None, exit_flag=False):
        """移除NFS客户端
        :param ids: Required:True   Type:string  Help:The authorization client id list.
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ remove_nfs_export_auth_clients ]")
        ids = self.auth_client_ids if ids is None else ids
        rc, stdout = common.remove_nfs_export_auth_clients(ids=ids,
                                                           print_flag=self.print_flag, fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'remove_nfs_export_auth_clients failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    def get_nfs_export_auth_clients(self, export_ids=None, exit_flag=False):
        """查询NFS客户端列表
        :param export_ids: Required:False  Type:string  Help:The nfs export id list.
        :param exit_flag: 当实际返回码和期望的不同时，是否退出脚本，默认不退出
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ get_nfs_export_auth_clients ]")
        rc, stdout = common.get_nfs_export_auth_clients(export_ids=export_ids, print_flag=self.print_flag,
                                                        fault_node_ip=self.fault_node_ip)
        common.judge_rc(rc, 0, 'get_nfs_export_auth_clients failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg


class SmbGlobalConfig(object):
    def __init__(self):
        pass

    @staticmethod
    def update_smb_global_config(smb_global_config_id, enable_change_notify=None, enable_guest=None,
                                 enable_send_ntlmv2=None, home_dir=None, enable_alternative_datasource=None,
                                 enable_dos_attributes=None, enable_os2style_ex_attrs=None,
                                 enable_ntfs_acl=None, allow_create_ntfs_acl=None, enable_oplocks=None,
                                 print_flag=True, fault_node_ip=None, exit_flag=False):
        """配置SMB公共属性
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
        common.judge_rc(rc, 0, 'update_smb_global_config failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    @staticmethod
    def get_smb_global_configs(ids=None, print_flag=True, fault_node_ip=None, exit_flag=False):
        """查询SMB公共属性
        :return: 执行cmd命令的字典格式返回值
        """
        log.info("\t[ get_smb_global_configs ]")
        rc, stdout = common.get_smb_global_configs(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip)
        common.judge_rc(rc, 0, 'get_smb_global_configs failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg


class FtpGlobalConfig(object):
    def __init__(self):
        pass

    @staticmethod
    def update_ftp_global_config(access_zone_id, anonymous_enable=None, anon_root=None,
                                 anon_upload_enable=None, anon_upload_max_rate=None, anon_download_enable=None,
                                 anon_download_max_rate=None, print_flag=True, fault_node_ip=None, exit_flag=False):
        log.info("\t[ update_ftp_global_config ]")
        rc, stdout = common.update_ftp_global_config(access_zone_id=access_zone_id, anonymous_enable=anonymous_enable,
                                                     anon_root=anon_root, anon_upload_enable=anon_upload_enable,
                                                     anon_upload_max_rate=anon_upload_max_rate,
                                                     anon_download_enable=anon_download_enable,
                                                     anon_download_max_rate=anon_download_max_rate,
                                                     print_flag=print_flag, fault_node_ip=fault_node_ip)
        common.judge_rc(rc, 0, 'update_ftp_global_config failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg

    @staticmethod
    def get_ftp_global_config(access_zone_id, print_flag=True, fault_node_ip=None, exit_flag=False):
        log.info("\t[ get_ftp_global_config ]")
        rc, stdout = common.get_ftp_global_config(access_zone_id=access_zone_id,
                                                  print_flag=print_flag, fault_node_ip=fault_node_ip)
        common.judge_rc(rc, 0, 'get_ftp_global_config failed', exit_flag=exit_flag)
        msg = common.json_loads(stdout)
        return msg


class ClientMountAndUmount(object):
    def __init__(self):
        pass

    def nfs_mount(self, client_ip, client_path, ):
        pass

    def nfs_umount(self):
        pass

    def smb_mount(self):
        pass

    def smb_umount(self):
        pass


class Tools(object):
    def __init__(self):
        pass

    def vdbench(self):
        pass

    def iozone(self):
        pass

    def mdtest(self):
        pass

    def dd(self):
        pass

    def touch(self):
        pass

    def mkdir(self):
        pass













"""***************************************节点IP信息***************************************"""


def node_ip_list():
    """
    author: zhangcy
    description: 从配置文件中获取所有集群节点的ip
    date: 20190315
    :return: stdout为所有集群节点的ip
    """
    stdout = get_config.get_allparastor_ips()
    return stdout


def random_node_ip():
    """
    author: zhangcy
    description: 从配置文件中获取所有集群节点的ip中，随机抽取一个
    date: 20190315
    :return: stdout为从集群中随机抽取一个节点的ip
    """
    node_ip_list_a = node_ip_list()
    stdout = node_ip_list_a[random.randint(0, len(node_ip_list_a) - 1)]
    return stdout


"""***************************************客户端IP信息***************************************"""


def client_ip_1():
    """
    author: zhangcy
    description: 从配置文件中获取私有客户端ip
    date: 20190315
    :return: stdout私有客户端ip
    """
    stdout = get_config.get_client_ip(0)
    return stdout


def client_ip_2():
    """
    author: zhangcy
    description: 从配置文件中获取私有客户端ip
    date: 20190315
    :return: stdout私有客户端ip
    """
    stdout = get_config.get_client_ip(1)
    return stdout


def client_ip_3():
    """
    author: zhangcy
    description: 从配置文件中获取私有客户端ip
    date: 20190315
    :return: stdout私有客户端ip
    """
    stdout = get_config.get_client_ip(2)
    return stdout


"""***************************************卷名称***************************************"""


def volume_name():
    """
    author: zhangcy
    description: 从配置文件中获取文件系统的卷名
    date: 20190315
    :return: stdout为文件系统的卷名
    """
    stdout = get_config.get_one_volume_name()
    return stdout


"""**********************************测试全路径，注意：nas_test_dir右侧不要加"/" **********************************"""


def nas_path():
    """
    author: zhangcy
    description: 从配置文件中获取测试路径
    date: 20190315
    :return: stdout为测试路径
    """
    stdout = get_config.get_one_nas_test_path()  # /mnt/volume/nas_test_dir
    return stdout


def last_path():
    """
    author: zhangcy
    description: 从配置文件中获取测试路径
    date: 20190315
    :return: stdout为测试路径
    """
    nas_path_a = nas_path()
    stdout = os.path.basename(nas_path_a)  # /mnt/volume
    return stdout


def root_dir():
    """
    author: zhangcy
    description: 从配置文件中获取测试路径
    date: 20190315
    :return: stdout为测试路径
    """
    volume_name_a = volume_name()
    last_path_a = last_path()
    stdout = "%s:/%s/" % (volume_name_a, last_path_a)  # volume:/nas_test_dir/
    return stdout


def base_nas_path():
    """
    author: zhangcy
    description: 从配置文件中获取测试路径
    date: 20190315
    :return: stdout为测试路径
    """
    nas_path_a = nas_path()
    stdout = os.path.dirname(nas_path_a)  # /mnt/volume"
    return stdout


def nas_path_basename():
    """
    author: zhangcy
    description: 从配置文件中获取测试路径
    date: 20190315
    :return: stdout为测试路径
    """
    nas_path_a = nas_path()
    stdout = os.path.basename(nas_path_a)  # 结果为/mnt/volume/nas_test_dir中的nas_test_dir
    return stdout


def nas_path_abspath():
    """
    author: zhangcy
    description: 从配置文件中获取测试路径
    date: 20190315
    :return: stdout为测试路径
    """
    nas_path_a = nas_path()
    stdout = os.path.abspath(nas_path_a)  # ******/mnt/volume/nas_test_dir
    return stdout


"""***************************************AD服务器信息***************************************"""


def ad_dns_address():
    """
    author: zhangcy
    description: 从配置文件中获取AD服务器的ip
    date: 20190313
    :return: stdout为AD服务器的ip
    """
    stdout = get_config.get_ad_dns_address()[0]
    return stdout


def ad_domain_name():
    """
    author: zhangcy
    description: 从配置文件中获取AD服务器的域名
    date: 20190313
    :return: stdout为AD服务器的域名
    """
    stdout = get_config.get_ad_domain_name()[0]
    return stdout


def ad_admin_user_name():
    """
    author: zhangcy
    description: 从配置文件中获取AD服务器管理员用户名
    date: 20190313
    :return: stdout为AD服务器管理员用户名
    """
    stdout = get_config.get_ad_user_name()[0]  # 服务器管理员用户名
    return stdout


def ad_admin_user_name_1():
    """
    author: zhangcy
    description: 从配置文件中获取AD服务器管理员用户名
    date: 20190313
    :return: stdout为AD服务器管理员用户名
    """
    stdout = get_config.get_ad_user_name()[1]  # autoadminuser1是AD域的用户，也在Domain Admins安全组中
    return stdout


def ad_admin_user_name_2():
    """
    author: zhangcy
    description: 从配置文件中获取AD服务器管理员用户名
    date: 20190313
    :return: stdout为AD服务器管理员用户名
    """
    stdout = get_config.get_ad_user_name()[2]  # autoadminuser2是AD域的用户，但不在Domain Admins安全组中
    return stdout


def ad_password():
    """
    author: zhangcy
    description: 从配置文件中获取AD服务器管理员密码
    date: 20190313
    :return: stdout为AD服务器管理员密码
    """
    stdout = get_config.get_ad_password()[0]  # 服务器管理员用户密码
    return stdout


def ad_users_name_list():
    """
    author: zhangcy
    description: 从配置文件中获取AD普通用户
    date: 20190313
    :return: stdout为AD普通用户
    """
    users_list = []
    for i in range(0, len(get_config.get_ad_users())):
        user = get_config.get_ad_users()[i]
        users_list.append(user)
    stdout = users_list
    return stdout


def ad_user_1_name():
    """
    author: zhangcy
    description: 从配置文件中获取AD普通用户
    date: 20190313
    :return: stdout为AD普通用户
    """
    stdout = get_config.get_ad_users()[0]  # 登录用户1
    return stdout


def ad_user_2_name():
    """
    author: zhangcy
    description: 从配置文件中获取AD普通用户
    date: 20190313
    :return: stdout为AD普通用户
    """
    stdout = get_config.get_ad_users()[1]  # 登录用户2
    return stdout


def ad_user_3_name():
    """
    author: zhangcy
    description: 从配置文件中获取AD普通用户
    date: 20190313
    :return: stdout为AD普通用户
    """
    stdout = get_config.get_ad_users()[2]  # 登录用户3
    return stdout


def ad_user_4_name():
    """
    author: zhangcy
    description: 从配置文件中获取AD特殊用户
    date: 20190313
    :return: stdout为AD特殊用户
    """
    stdout = get_config.get_ad_users()[3]  # ad域特殊用户1，有附属组
    return stdout


def ad_user_pw():
    """
    author: zhangcy
    description: 从配置文件中获取AD用户的密码
    date: 20190313
    :return: stdout为AD用户的密码
    """
    stdout = get_config.get_ad_user_pw()[0]  # 登录用户的密码
    return stdout


def ad_groups_name_list():
    """
    author: zhangcy
    description: 从配置文件中获取AD用户组列表
    date: 20190313
    :return: stdout为AD用户组列表
    """
    groups_list = []
    for i in range(0, len(get_config.get_ad_groups())):
        group = get_config.get_ad_groups()[i]
        groups_list.append(group)
    stdout = groups_list
    return stdout


def ad_group_1_name():
    """
    author: zhangcy
    description: 从配置文件中获取AD用户组
    date: 20190313
    :return: stdout为AD用户组
    """
    stdout = get_config.get_ad_groups()[0]  # 登录用户组
    return stdout


def ad_user_1st_group():
    """
    author: zhangcy
    description: 从配置文件中获取AD特殊用户1的其中一个组
    date: 20190313
    :return: stdout为AD特殊用户1的其中一个组
    """
    stdout = get_config.get_ad_groups()[1]  # ad域特殊用户1的其中一个组
    return stdout


def ad_user_2nd_group():
    """
    author: zhangcy
    description: 从配置文件中获取AD特殊用户1的其中一个组
    date: 20190313
    :return: stdout为AD特殊用户1的其中一个组
    """
    stdout = get_config.get_ad_groups()[2]  # ad域特殊用户1的其中一个组
    return stdout


"""***************************************NIS服务器信息***************************************"""


def nis_ip_address():
    """
    author: zhangcy
    description: 从配置文件中获取NIS服务器的ip
    date: 20190313
    :return: stdout为NIS服务器的ip
    """
    stdout = get_config.get_nis_ip_address()[0]
    return stdout


def nis_domain_name():
    """
    author: zhangcy
    description: 从配置文件中获取NIS服务器的域名
    date: 20190313
    :return: stdout为NIS服务器的域名
    """
    stdout = get_config.get_nis_domain_name()[0]
    return stdout


def nis_users_name_list():
    """
    author: zhangcy
    description: 从配置文件中获取NIS普通用户名列表
    date: 20190313
    :return: stdout为NIS普通用户名列表
    """
    users_list = []
    for i in range(0, len(get_config.get_nis_users())):
        user = get_config.get_nis_users()[i]
        users_list.append(user)
    stdout = users_list
    return stdout


def nis_user_1_name():
    """
    author: zhangcy
    description: 从配置文件中获取NIS普通用户名
    date: 20190313
    :return: stdout为NIS普通用户名
    """
    stdout = get_config.get_nis_users()[0]
    return stdout


def nis_user_2_name():
    """
    author: zhangcy
    description: 从配置文件中获取NIS普通用户名
    date: 20190313
    :return: stdout为NIS普通用户名
    """
    stdout = get_config.get_nis_users()[1]
    return stdout


def nis_user_pw():
    """
    author: zhangcy
    description: 从配置文件中获取NIS普通用户密码
    date: 20190313
    :return: stdout为NIS普通用户密码
    """
    stdout = get_config.get_nis_user_pw()[0]
    return stdout


def nis_groups_name_list():
    """
    author: zhangcy
    description: 从配置文件中获取NIS普通用户组列表
    date: 20190313
    :return: stdout为NIS普通用户组列表
    """
    groups_list = []
    for i in range(0, len(get_config.get_nis_groups())):
        group = get_config.get_nis_groups()[i]
        groups_list.append(group)
    stdout = groups_list
    return stdout


def nis_group_1_name():
    """
    author: zhangcy
    description: 从配置文件中获取NIS普通用户组
    date: 20190313
    :return: stdout为NIS普通用户组
    """
    stdout = get_config.get_nis_groups()[0]
    return stdout


def nis_group_2_name():
    """
    author: zhangcy
    description: 从配置文件中获取NIS普通用户组
    date: 20190313
    :return: stdout为NIS普通用户组
    """
    stdout = get_config.get_nis_groups()[1]
    return stdout


"""***************************************LDAP服务器信息***************************************"""


def ldap_ip_address():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP服务器的ip
    date: 20190314
    :return: stdout为LDAP服务器的ip
    """
    stdout = get_config.get_ldap_ip_addresses()[0]  # 10.2.41.181
    return stdout


def ldap_base_dn():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP服务器的base_dn
    date: 20190314
    :return: stdout为LDAP服务器的base_dn
    """
    stdout = get_config.get_ldap_base_dn()[0]  # dc=test,dc=com
    return stdout


def ldap_bind_dn():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP服务器的bind_dn
    date: 20190314
    :return: stdout为LDAP服务器的bind_dn
    """
    stdout = get_config.get_ldap_bind_dn()[0]  # cn=root,dc=test,dc=com
    return stdout


def ldap_bind_password():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP服务器的bind_password
    date: 20190314
    :return: stdout为LDAP服务器的bind_password
    """
    stdout = get_config.get_ldap_bind_passwd()[0]  # 111111
    return stdout


def ldap_domain_password():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP服务器的domain_password
    date: 20190314
    :return: stdout为LDAP服务器的domain_password
    """
    stdout = get_config.get_ldap_domain_passwd()[0]  # 111111
    return stdout


def ldap_user_search_path():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP服务器的user_search_path
    date: 20190314
    :return: stdout为LDAP服务器的user_search_path
    """
    stdout = get_config.get_ldap_user_search_path()[0]  # ou=People,dc=test,dc=com
    return stdout


def ldap_group_search_path():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP服务器的group_search_path
    date: 20190314
    :return: stdout为LDAP服务器的group_search_path
    """
    stdout = get_config.get_ldap_group_search_path()[0]  # ou=Group,dc=test,dc=com
    return stdout


def ldap_users_name_list():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP服务器的普通用户列表
    date: 20190320
    :return: stdout为LDAP服务器的普通用户列表，形如[u'ldapuser1', u'ldapuser2', u'\u7528\u6237@a', u'user A']
    """
    users_list = []
    for i in range(0, len(get_config.get_ldap_user_name())):
        user = get_config.get_ldap_user_name()[i]
        users_list.append(user)
    stdout = users_list
    return stdout


def ldap_user_1_name():
    """
    author: zhangcy
    description: 从配置文件中随机获取一个LDAP服务器的普通用户
    date: 20190320
    :return: stdout为随机获取一个LDAP服务器的普通用户，形如ldapuser1
    """
    # users_list = ldap_users_name_list()
    # stdout = random.choice(users_list)
    stdout = get_config.get_ldap_user_name()[0]
    return stdout


def ldap_user_1_password():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP服务器的普通用户密码
    date: 20190315
    :return: stdout为LDAP服务器的普通用户密码
    """
    stdout = get_config.get_ldap_user_passwd()[0]  # 111111 ldap第一个用户的密码
    return stdout


def ldap_groups_name_list():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP服务器的普通用户组列表
    date: 20190315
    :return: stdout为LDAP服务器的普通用户组列表，形如
             [u'ldapgroup1', u'\u7528\u6237\u7ec41', u'group@a1', u'Domain Users']
    """
    groups_list = []
    for i in range(0, len(get_config.get_ldap_group_name())):
        user = get_config.get_ldap_group_name()[i]
        groups_list.append(user)
    stdout = groups_list
    return stdout


def ldap_group_1_name():
    """
    author: zhangcy
    description: 从配置文件中随机获取一个LDAP服务器的普通用户组
    date: 20190315
    :return: stdout为随机获取一个LDAP服务器的普通用户组，形如Domain Users
    """
    # groups_list = ldap_groups_name_list()
    # stdout = random.choice(groups_list)
    stdout = get_config.get_ldap_group_name()[0]
    return stdout


"""***************************************LDAP_PDC服务器信息***************************************"""


def ldap_pdc_ip_address():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP带域服务器的ip
    date: 20190315
    :return: stdout为LDAP带域服务器的ip
    """
    stdout = get_config.get_ldappdc_ip_addresses()[0]  # 10.2.41.239
    return stdout


def ldap_pdc_base_dn():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP带域服务器的base_dn
    date: 20190315
    :return: stdout为LDAP带域服务器的base_dn
    """
    stdout = get_config.get_ldappdc_base_dn()[0]  # dc=ldap-pdc,dc=com
    return stdout


def ldap_pdc_bind_dn():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP带域服务器的bind_dn
    date: 20190315
    :return: stdout为LDAP带域服务器的bind_dn
    """
    stdout = get_config.get_ldappdc_bind_dn()[0]  # cn=Manager,dc=ldap-pdc,dc=com
    return stdout


def ldap_pdc_bind_password():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP带域服务器的bind_passwd
    date: 20190315
    :return: stdout为LDAP带域服务器的bind_passwd
    """
    stdout = get_config.get_ldappdc_bind_passwd()[0]  # 111111
    return stdout


def ldap_pdc_domain_password():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP带域服务器的domain_passwd
    date: 20190315
    :return: stdout为LDAP带域服务器的domain_passwd
    """
    stdout = get_config.get_ldappdc_domain_passwd()[0]  # 111111
    return stdout


def ldap_pdc_user_search_path():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP带域服务器的user_search_path
    date: 20190315
    :return: stdout为LDAP带域服务器的user_search_path
    """
    stdout = get_config.get_ldappdc_user_search_path()[0]  # ou=People,dc=ldap-pdc,dc=com
    return stdout


def ldap_pdc_group_search_path():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP带域服务器的group_search_path
    date: 20190315
    :return: stdout为LDAP带域服务器的group_search_path
    """
    stdout = get_config.get_ldappdc_group_search_path()[0]  # ou=Group,dc=ldap-pdc,dc=com
    return stdout


def ldap_pdc_users_name_list():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP带域服务器的普通用户列表
    date: 20190315
    :return: stdout为LDAP带域服务器的普通用户列表
    """
    users_list = []
    for i in range(0, len(get_config.get_ldappdc_user_name())):
        user = get_config.get_ldappdc_user_name()[i]
        users_list.append(user)
    stdout = users_list
    return stdout


def ldap_pdc_user_1_name():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP带域服务器的普通用户
    date: 20190315
    :return: stdout为LDAP带域服务器的普通用户
    """
    stdout = get_config.get_ldappdc_user_name()[0]  # ldapuser1  可使用su登录的用户
    return stdout


def ldap_pdc_user_2_name():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP带域服务器的普通用户
    date: 20190315
    :return: stdout为LDAP带域服务器的普通用户
    """
    stdout = get_config.get_ldappdc_user_name()[2]  # user A  可使用su登录的用户
    return stdout


def ldap_user_pdc_password():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP带域服务器的普通用户密码
    date: 20190315
    :return: stdout为LDAP带域服务器的普通用户密码
    """
    stdout = get_config.get_ldap_user_passwd()[0]  # 111111
    return stdout


def ldap_pdc_groups_name_list():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP带域服务器的普通用户组列表
    date: 20190315
    :return: stdout为LDAP带域服务器的普通用户组列表
    """
    groups_list = []
    for i in range(0, len(get_config.get_ldappdc_group_name())):
        group = get_config.get_ldappdc_group_name()[i]
        groups_list.append(group)
    stdout = groups_list
    return stdout


def ldap_pdc_group_1_name():
    """
    author: zhangcy
    description: 从配置文件中获取LDAP带域服务器的普通用户组
    date: 20190315
    :return: stdout为LDAP带域服务器的普通用户组
    """
    stdout = get_config.get_ldappdc_group_name()[0]  # Domain Users  用户user A的组
    return stdout


"""***************************************NFS客户端IP***************************************"""


def nfs_1_client_ip():
    """
    author: zhangcy
    description: 从配置文件中获取nfs客户端ip
    date: 20190315
    :return: stdout为nfs客户端ip
    """
    stdout = get_config.get_nfs_client_ip()[0]  # 比如10.2.42.135
    return stdout


def nfs_2_client_ip():
    """
    author: zhangcy
    description: 从配置文件中获取nfs客户端ip
    date: 20190315
    :return: stdout为nfs客户端ip
    """
    stdout = get_config.get_nfs_client_ip()[1]  # 比如10.2.42.136
    return stdout


def nfs_3_client_ip():
    """
    author: zhangcy
    description: 从配置文件中获取nfs客户端ip
    date: 20190315
    :return: stdout为nfs客户端ip
    """
    stdout = get_config.get_nfs_client_ip()[2]  # 比如10.2.42.137
    return stdout


"""***************************************FTP客户端IP***************************************"""


def ftp_1_client_ip():
    """
    author: zhangcy
    description: 从配置文件中获取ftp客户端ip
    date: 20190315
    :return: stdout为ftp客户端ip
    """
    stdout = get_config.get_ftp_client_ip()[0]  # 比如10.2.42.135
    return stdout


def ftp_2_client_ip():
    """
    author: zhangcy
    description: 从配置文件中获取ftp客户端ip
    date: 20190315
    :return: stdout为ftp客户端ip
    """
    stdout = get_config.get_ftp_client_ip()[1]  # 比如10.2.42.135
    return stdout


"""***************************************SMB客户端IP***************************************"""


def win_1_client_ip():
    """
    author: zhangcy
    description: 从配置文件中获取win客户端ip
    date: 20190315
    :return: stdout为win客户端ip
    """
    stdout = get_config.get_win_client_ips()[0]
    return stdout


def win_1_client_disk_symbol():
    """
    author: zhangcy
    description: 从配置文件中获取win客户端盘符
    date: 20190315
    :return: stdout为win客户端盘符
    """
    stdout = get_config.get_win_disk_symbols()[0]
    return stdout


"""***************************************SUBNET和VIP地址池信息***************************************"""
"""第一组"""


def subnet_svip():
    """
    author: zhangcy
    description: 从配置文件中获取svip
    date: 20190315
    :return: stdout为svip
    """
    stdout = get_config.get_subnet_svip()[0]
    return stdout


def subnet_mask():
    """
    author: zhangcy
    description: 从配置文件中获取子网掩码subnet_mask
    date: 20190315
    :return: stdout为子网掩码subnet_mask
    """
    stdout = get_config.get_subnet_mask()[0]
    return stdout


def subnet_gateway():
    """
    author: zhangcy
    description: 从配置文件中获取子网网关subnet_gateway
    date: 20190315
    :return: stdout为子网网关subnet_gateway
    """
    stdout = get_config.get_subnet_gateway()[0]
    return stdout


def subnet_network_interfaces():
    """
    author: zhangcy
    description: 从配置文件中获取子网网卡
    date: 20190315
    :return: stdout为子网网卡
    """
    stdout = get_config.get_subnet_network_interface()[0]  # 一张网卡名
    return stdout


def subnet_mtu():
    """
    author: zhangcy
    description: 从配置文件中获取子网mtu
    date: 20190315
    :return: stdout为子网mtu
    """
    stdout = get_config.get_subnet_mtu()[0]
    return stdout


def vip_domain_name():
    """
    author: zhangcy
    description: 从配置文件中获取子网域名
    date: 20190315
    :return: stdout为子网域名
    """
    stdout = get_config.get_vip_domain_name()[0]
    return stdout


def vip_addresses():
    """
    author: zhangcy
    description: 从配置文件中获取子网vip地址池
    date: 20190315
    :return: stdout为子网vip地址池
    """
    stdout = get_config.get_vip_addresses()[0]  # 连续型vip池地址
    return stdout


"""第二组"""


def subnet_2_svip():
    """
    author: zhangcy
    description: 从配置文件中获取第二个svip
    date: 20190315
    :return: stdout为第二个svip
    """
    stdout = get_config.get_subnet_svip()[1]
    return stdout


def subnet_2_mask():
    """
    author: zhangcy
    description: 从配置文件中获取第二个掩码
    date: 20190315
    :return: stdout为第二个掩码
    """
    stdout = get_config.get_subnet_mask()[0]
    return stdout


def subnet_2_gateway():
    """
    author: zhangcy
    description: 从配置文件中获取第二个网关
    date: 20190315
    :return: stdout为第二个网关
    """
    stdout = get_config.get_subnet_gateway()[0]
    return stdout


def subnet_2_network_interfaces():
    """
    author: zhangcy
    description: 从配置文件中获取第二个网卡
    date: 20190315
    :return: stdout为第二个网卡
    """
    stdout = get_config.get_subnet_network_interface()[1]  # 多张网卡名
    return stdout


def subnet_2_mtu():
    """
    author: zhangcy
    description: 从配置文件中获取第二个mtu
    date: 20190315
    :return: stdout为第二个mtu
    """
    stdout = get_config.get_subnet_mtu()[0]
    return stdout


def vip_2_domain_name():
    """
    author: zhangcy
    description: 从配置文件中获取第二个域名
    date: 20190315
    :return: stdout为第二个域名
    """
    stdout = get_config.get_vip_domain_name()[1]
    return stdout


def vip_2_addresses():
    """
    author: zhangcy
    description: 从配置文件中获取第二个vip地址池
    date: 20190315
    :return: stdout为第二个vip地址池
    """
    stdout = get_config.get_vip_addresses()[1]
    return stdout


"""第三组"""


def vip_3_addresses():
    """
    author: zhangcy
    description: 从配置文件中获取第三个vip地址池
    date: 20190315
    :return: stdout为第三个vip地址池
    """
    stdout = get_config.get_vip_addresses()[2]  # 离散型vip池地址
    return stdout


"""---------------------------> 读取配置文件结束 <---------------------------"""


def get_node_ids():
    """获取集群全部节点的id，id间以逗号连接
    :Author:
    :Date:
    :return: node_ids: 返回全部节点的id，格式为1,2,3
    """
    obj_node = common.Node()
    node_id_list = obj_node.get_nodes_id()
    node_ids = ','.join(str(i) for i in node_id_list)
    return node_ids


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

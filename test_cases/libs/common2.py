#!/usr/bin/python
# -*- encoding=utf8 -*-

import os
import json
import shell
import time
import subprocess
import commands
import log
import get_config
import sys
import re
import random
import datetime
import ReliableTest
import common
import remote

reload(sys)
sys.setdefaultencoding('utf-8')

CONF_FILE = get_config.CONFIG_FILE
node_ips_list = get_config.get_env_ip_info(CONF_FILE)
CLEAN_ENV = "No"
deploy_ips = get_config.get_env_ip_info(CONF_FILE)
client_ips = get_config.get_allclient_ip()
node = common.Node()

# 与windows主机端发起连接
windows_host_ip = get_config.get_windows_host_ip()
port = get_config.get_windows_host_port()
conf = get_config.get_windows_host_conf()
windows_tag = 1
if conf == 'on':
    try:
        windows_host_ip = get_config.get_windows_host_ip()
        port = get_config.get_windows_host_port(CONF_FILE)
        win_host = ('%s:%s' % (windows_host_ip, port))
        vdb_test = remote.Remote(uri=win_host)
        vdb_test.run_keyword('test_connect')
    except Exception:
        windows_tag = 1
        print ("The winodws host is not conneted.")
    else:
        windows_tag = 0
        print ("The winodws host has been conneted.windows host:%s" % windows_host_ip)

class oSan():
    '''
    x1000相关操作
    create_access_zone
    create_storage_pool
    set_vip
    create_subnet
    add_vip_address_pool
    enable_san
    create_host_group
    add_host
    add_initiator
    create_lun
    map_lun
    write_iqn
    delete_lun_map
    delete_lun
    remove_initiator

    get_node_pool_disks
    get_vip_address_pools
    get_svip
    get_vip_address_pools_id
    discover_scsi
    iscsi_login
    iscsi_logout
    ls_scsi_dev
    get_nodes
    get_storage_id
    get_subnet_id
    get_access_zone_id
    get_hosts
    get_host_groups
    get_lun
    get_lun_maps
    get_lun_maps_by_lunid
    get_iqn
    get_initiators
    analysis_vip
    get_los

    gen_vdb_xml
    run_vdb
    auto_gen_vdb_xml
    auto_gen_vdb_jn_xml
    vdb_write
    vdb_check
    save_vdb_log

    run_cmd
    get_node_by_vip
    get_same_jnl_group
    '''

    def __init__(self):
        pass

    ###########################    创建相关操作    ####################
    def create_access_zone(self, s_ip=None, node_id=None, name=None):
        '''
        date    :   2018-05-23
        Description :   创建访问区
        param   :   s_ip : iscsi服务端IP; node_id : 节点ID; name : 访问区名称
        return  :   Access zone ID,INT
        '''
        if None == s_ip or None == node_id or None == name:
            log.error("Got wrong parameters.")
            log.error("I need s_ip(server ip),node_id(string) and name(accesee zone name).")
            os._exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=create_access_zone --node_ids=%s --name=%s\"" % (s_ip, str(node_id), name))
            (res, final) = commands.getstatusoutput(cmd)
            log.info(cmd)
            if 0 != res:
                log.error(final)
                log.error("Create access zone error.")
                os._exit(1)
            else:
                final = json.loads(final)
        return final['result']

    def create_storage_pool(self, s_ip=None, name=None, node_pool_ids=None, disk_ids=None):
        '''
        date    :   2018-06-05
        Description :   创建存储池
        param   :
        return  :   storage_pool ID
        '''
        if None == name or None == node_pool_ids or s_ip == None:
            log.error("I need storage name= and node_pool_ids=")
            os._exit(1)
        elif None == disk_ids:
            cmd = ("ssh %s \" pscli --command=create_storage_pool --type=BLOCK --name=%s --node_pool_ids=%s\"" % (
                s_ip, name, str(node_pool_ids)))
        else:
            cmd = (
                    "ssh %s \" pscli --command=create_storage_pool --disk_ids=%s --type=BLOCK --name=%s --node_pool_ids=%s\"" % (
                s_ip, str(disk_ids), name, str(node_pool_ids)))
        log.info(cmd)
        (res, prefix) = commands.getstatusoutput(cmd)
        if res != 0:
            log.error(prefix)
            log.error("Create storage pool error.")
            os._exit(1)
        else:
            log.info("Create storage pool success.")
        prefix = json.loads(prefix)
        return prefix['result']['storage_pool_id']

    def set_vip(self, s_ip=None, v_ip=None):
        '''
        date    :   2018-05-29
        Description :   设置vip
        param   :   s_ip : iscsi服务端IP
        return  :   vip
        '''
        if None == s_ip:
            log.error("I need s_ip=server ip to set svip,or s_ip=server ip,v_ip=virtual ip to set virtual ip")
            os._exit(1)
        cmd = ("echo %s | sed -r 's/(.*)(.[0-9]+)/\\1/g'" % (s_ip))
        log.info(cmd)
        (res, prefix) = commands.getstatusoutput(cmd)
        for i in range(200, 254):
            test_ip = ("%s.%d" % (prefix, i))
            if test_ip == v_ip:
                continue
            cmd = ("ping -c 1 %s >& /dev/null" % (test_ip))
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                return test_ip
            if i == 253:
                log.error("Sorry,I can not find the ip you can use.")
                os._exit(1)

    def create_subnet(self, s_ip=None, sv_ip=None, access_zone_id="1", name="subnet1"):
        '''
        date    :     2018-05-29
        Description : create subnet
        param   :     s_ip : iscsi服务端IP
        return  :     subnet ID
        '''

        if None == s_ip or None == sv_ip:
            log.error(
                "I need s_ip=server ip,sv_ip=svip at least,access_zone_id default value is 1,name default value is subnet1")
            os._exit(1)
        log.info("Get_network_interface")
        cmd = ("echo %s | sed -r 's/(.*)(\.[0-9]+)/\\1/g'" % (sv_ip))
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        prefix = final.strip("[|]|u")
        log.info("Get gateway.")
        gate_way = prefix + '.254'
        cmd = ("ssh %s \"ip addr | grep -w %s | sed -r 's/^ +//g' | cut -d ' ' -f 7 | uniq\"" % (s_ip, prefix))
        log.info(cmd)
        network_interface = None
        network_interface_ls = []
        (res, final) = commands.getstatusoutput(cmd)
        if 0 != res:
            log.error("Get_network_interface error.")
        else:
            if len(final) == 0:
                cmd = ("echo %s | sed -r 's/(.*)(\.[0-9]+)(\.[0-9]+)/\\1/g'" % (sv_ip))
                log.info(cmd)
                (res, final) = commands.getstatusoutput(cmd)
                prefix = final.strip("[|]|u")
                cmd = ("ssh %s \"ip addr | grep -w %s | sed -r 's/^ +//g' | cut -d ' ' -f 7 | uniq\"" % (s_ip, prefix))
                log.info(cmd)
                (res, final) = commands.getstatusoutput(cmd)
            log.info("network_interface: %s" % final)
            network_interface_ls = final.split('\n')
            if len(network_interface_ls) > 1:
                network_interface_conf = ','.join(network_interface_ls)
            else:
                network_interface_conf = network_interface_ls[0]
        # check network interfaces in each node
        for node_ip in node_ips_list:
            cmd = ("ssh root@%s 'ip a' | grep '^[0-9]' | awk '{print $2}' | cut -f1 -d ':'" % node_ip)
            stdout = commands.getoutput(cmd)
            net_list = stdout.split('\n')
            for network_interface in network_interface_ls:
                if network_interface not in net_list:
                    log.error("error!the The business network interfaces %s is not in node %s" % (network_interface, node_ip))
                    os._exit(1)
        log.info("Get mask.")
        cmd = ("ssh %s \"ip addr | grep -w %s | sed -r 's/^ +//g' | cut -d ' ' -f 2 | sed -r 's/.*\///g' | uniq\""
               % (s_ip, prefix))
        log.info(cmd)
        mask = 24
        (res, final) = commands.getstatusoutput(cmd)
        if 0 != res:
            log.error("Get mask error.")
            os._exit(1)
        else:
            log.info("Get mask is : %s" % (final))
            mask = final
        log.info("Get svip.")
        for node_ip in node_ips_list:
            cmd = ("ssh root@%s 'ip a | grep \"inet .*/\"' | awk '{print $2}' | awk -F '/' '{print $1}'" % node_ip)
            stdout = commands.getoutput(cmd)
            ips_info = stdout.split('\n')
            if sv_ip in ips_info:
                log.error("svip conflicts with IP of business network interfaces")
                os._exit(1)
        cmd = ( "ssh %s \"pscli --command=create_subnet --access_zone_id=%s --name=%s --svip=%s --subnet_mask=%s --subnet_gateway=%s --network_interfaces=%s --ip_family=IPv4\""
                 % (s_ip, str(access_zone_id), name, sv_ip, mask, gate_way, network_interface_conf))
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        if 0 != res:
            log.error(final)
            log.error("Create_subnet error.")
            os._exit(1)
        else:
            log.info("Create_subnet success.")
            final = json.loads(final)
            return final['result']

    def update_subnet(self, s_ip, subnet_id, svip=None, subnet_name=None, subnet_mask=None, subnet_gateway=None,
                      network_interfaces=None, mtu=None, need_judge=None):
        """
        Author:wangxiang
        :param s_ip:
        :param subnet_id:
        :param svip:
        :param subnet_name:
        :param subnet_mask:
        :param subnet_gateway:
        :param network_interfaces:
        :param mtu:
        :param need_judge:
        :return:
        """
        if not all([s_ip, subnet_id]):
            log.error("get error arg!")
            exit(1)
        else:
            init_cmd = "pscli   --command=update_subnet  --id={}".format(subnet_id)
            if subnet_name:
                init_cmd = "{}  --name={}".format(init_cmd, subnet_name)
            if svip:
                init_cmd = "{} --svip={}".format(init_cmd, svip)
            if subnet_mask:
                init_cmd = "{} --subnet_mask={}".format(init_cmd, subnet_mask)
            if subnet_gateway:
                init_cmd = "{}  --subnet_gateway={}".format(init_cmd, subnet_gateway)
            if network_interfaces:
                init_cmd = "{} --network_interfaces={}".format(init_cmd, network_interfaces)
            if mtu:
                init_cmd = "{}  --mtu={}".format(init_cmd, mtu)
            cmd = "ssh {}  \"{}\"".format(s_ip, init_cmd)
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res:
                if need_judge:
                    result = json.loads(final)
                    return result['err_msg']
                else:
                    log.error("update subnet fail")
                    os._exit(1)
            else:
                log.info("update subnet success.")
                final = json.loads(final)
                return final['result']
        time.sleep(30)

    def add_vip_address_pool(self, subnet_id, s_ip,vip_addresses=None, domain_name=None, supported_protocol='ISCSI',
                              allocation_method='DYNAMIC', load_balance_policy=None,ip_failover_policy=None,rebalance_policy='RB_AUTOMATIC', need_judge=None):
        """
        add vip地址段
        :Author:wangxiang
        :Date:2019/3/15
        :param id: 子网id
        :param s_ip: 节点ip
        :param vip_addresses:
        :return:
        """
        if not all([s_ip, subnet_id,domain_name,vip_addresses,supported_protocol,allocation_method]):
            log.error("get error  arg!")
            exit(1)
        init_cmd = "pscli   --command=add_vip_address_pool  --subnet_id={}  --domain_name={}  --vip_addresses={}".format(subnet_id,domain_name,vip_addresses)
        if load_balance_policy:
            init_cmd = "{} --load_balance_policy={}".format(init_cmd, load_balance_policy)
        if ip_failover_policy:
            init_cmd = "{}  --ip_failover_policy={}".format(init_cmd, ip_failover_policy)
        if rebalance_policy:
            init_cmd = "{}   --rebalance_policy={}".format(init_cmd, rebalance_policy)
        if supported_protocol:
            init_cmd = "{}   --supported_protocol={}".format(init_cmd, supported_protocol)
        if allocation_method:
            init_cmd = "{}   --allocation_method={}".format(init_cmd, allocation_method)

        cmd = "timeout 300 ssh {} \"{}\"".format(s_ip, init_cmd)
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        if res == 0:
            log.info("add vip_address sucess")
        else:
            if need_judge:
                result = json.loads(final)
                return (result['err_msg'])
            else:
                log.info(final)
                os._exit(1)

    def check_vip_balance(self,need_judge=None,need_wait=None,wait_time=150):
        '''
        date:   2019-01-17
        Author: wuyuqiao
        return: vip is balanced or not: return True or False
        '''
        if need_wait:
            import decorator_func
            decorator_func.timer(wait_time, 25, log_interval=0)
        if need_judge:
            vips_list = get_config.get_vip(CONF_FILE)
            vips = self.analysis_vip(vips_list)
            vips_nums = []
            node_ids = self.get_jnl_node_id()
            node_ips = [node.get_node_ip_by_id(id) for id in node_ids]
            for node_ip in node_ips:
                cmd = ("ssh root@%s 'ip a | grep \"inet .*/\"' | awk '{print $2}' | awk -F '/' '{print $1}'" % node_ip)
                stdout = commands.getoutput(cmd)
                ips_info = stdout.split('\n')
                vip_list = []
                for ip in ips_info:
                    if ip in vips:
                        vip_list.append(ip)
                log.info("node %s vips is: %s" % (node_ip, vip_list))
                vips_nums.append(len(vip_list))
            if len(set(vips_nums)) == 1 and sum(vips_nums) == len(vips):
                log.info("VIPs in all nodes is balanced.")
                return True
            elif max(vips_nums) - min(vips_nums) == 1 and sum(vips_nums) == len(vips):
                log.info("VIPs in all nodes is balanced.")
                return True
            else:
                log.info("VIPs in all nodes is not balanced.vips nums:%s" % vips_nums)
                import env_manage_lun_manage
                node_ids_list = env_manage_lun_manage.osan.get_nodes(deploy_ips[0])
                cur_jnl_rep = env_manage_lun_manage.break_down.get_jnl_replica(s_ip=deploy_ips[0])
                if len(node_ids_list) != cur_jnl_rep:
                    log.info("节点副本数:{}和节点数:{}不一致的情况,vip均衡做检测,但不退出!".format(len(node_ids_list), cur_jnl_rep))
                    return
                else:
                    log.info("节点副本数:{}和节点数:{}一致的情况,vip均衡做检测,将会退出!".format(len(node_ids_list), cur_jnl_rep))
                    os._exit(1)
        else:
            vips_list = get_config.get_vip(CONF_FILE)
            vips = self.analysis_vip(vips_list)
            vips_nums = []
            node_ids = self.get_jnl_node_id()
            node_ips = [node.get_node_ip_by_id(id) for id in node_ids]
            for node_ip in node_ips:
                cmd = ("ssh root@%s 'ip a | grep \"inet .*/\"' | awk '{print $2}' | awk -F '/' '{print $1}'" % node_ip)
                stdout = commands.getoutput(cmd)
                ips_info = stdout.split('\n')
                vip_list = []
                for ip in ips_info:
                    if ip in vips:
                        vip_list.append(ip)
                log.info("node %s vips is: %s" % (node_ip, vip_list))
                vips_nums.append(len(vip_list))
            if len(set(vips_nums)) == 1 and sum(vips_nums) == len(vips):
                log.info("VIPs in all nodes is balanced.")
                return True
            elif max(vips_nums) - min(vips_nums) == 1 and sum(vips_nums) == len(vips):
                log.info("VIPs in all nodes is balanced.")
                return True
            else:
                log.info("VIPs in all nodes is not balanced.vips nums:%s" % vips_nums)
                return False

    def enable_san(self, s_ip=None, access_zone_id=None):
        '''
        date    :   2018-06-05
        Description :   激活 san
        param   :   s_ip : 服务节点IP
        return  :   None
        '''
        if None == s_ip or None == access_zone_id:
            log.error("Please input server ip")
            os._exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=enable_san --access_zone_id=%s\"" % (s_ip, str(access_zone_id)))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Enable san on access_zone_id:%s error." % (str(access_zone_id)))
                os._exit(1)
            else:
                log.info("Enable san on access_zone_id:%s success." % (str(access_zone_id)))
                final = json.loads(final)

    def create_host_group(self, s_ip=None, hg_name=None):
        '''
        date    :   2018-06-06
        Description :   创建主机组
        param   :   s_ip : 服务节点IP hg_name : 主机组名称
        return  :   host group ID
        '''
        if None == s_ip or None == hg_name:
            log.error("Please input server ip")
            os._exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=create_host_group --name=%s\"" % (s_ip, str(hg_name)))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Create host group: %s error." % (hg_name))
                os._exit(1)
            else:
                log.info("Create host group: %s success." % (hg_name))
                final = json.loads(final)
                return final['result']

    def add_host(self, s_ip=None, h_name=None, hg_id=None):
        '''
        date    :   2018-06-06
        Description :   创建主机组
        param   :   s_ip : 服务节点IP hg_name : 主机组名称
        return  :   host ID,LIST
        '''
        if None == s_ip or None == h_name or None == hg_id:
            log.error("Please input server ip")
            os._exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=add_host --name=%s --host_group_id=%s\"" % (s_ip, str(h_name), str(hg_id)))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Create host:%s error." % (h_name))
                os._exit(1)
            else:
                log.info("Create host: %s success." % (h_name))
                final = json.loads(final)
                return final['result']

    def add_initiator(self, s_ip=None, h_id=None, iqn=None, alias=None):
        '''
        date    :   2018-06-06
        Description :   添加启动器
        param   :   
        return  :  initiator ID 
        '''
        if None == s_ip or None == h_id or None == iqn or None == alias:
            log.error("add_initiator:got wrong parameters.")
            os._exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=add_initiator --iqn=%s --alias=%s --host_id=%s --auth_type=NONE\"" % (
                s_ip, iqn, alias, h_id))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Add initiator error.")
                os._exit(1)
            else:
                log.info("Add initiator success.")
                final = json.loads(final)
                return final['result']

    def create_lun(self, s_ip=None, lun_name=None, lun_type="THIN", stor_pool_id=None, acc_zone_id=None,
                   total_bytes="99999999999", max_throughput="9000", max_iops="2000",
                   stripe_width="1", disk_parity_num="0", node_parity_num="0", replica_num="1"):
        '''
        date    :   2018-06-06
        Description :   添加启动器
        param   :   
        return  :  Lun ID 
        '''
        if None == s_ip or None == lun_name or None == stor_pool_id or None == acc_zone_id:
            log.error("Create lun:got wrong parameters.")
            os._exit(1)
        elif str(stor_pool_id) == "1":
            log.error("stor_pool_id can not set 1.")
            os._exit(1)
        else:
            cmd = (
                    "ssh %s \"pscli --command=create_lun --name=%s --type=%s --storage_pool_id=%s --access_zone_id=%s --total_bytes=%s --max_throughput=%s --max_iops=%s --stripe_width=%s --disk_parity_num=%s --node_parity_num=%s --replica_num=%s\"" % (
                s_ip, lun_name, lun_type, str(stor_pool_id), str(acc_zone_id),
                str(total_bytes), str(max_throughput), str(max_iops), str(stripe_width),
                str(disk_parity_num), str(node_parity_num), str(replica_num)))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Create lun error.")
                os._exit(1)
            else:
                log.info("Create lun success.")
                final = json.loads(final)
                return final['result']

    def map_lun(self, s_ip=None, lun_ids=None, hg_id=None):
        '''
        date    :   2018-06-09
        Description ： map lun
        param   :   lun_ids : 卷ID  hg_id : 主机组ID
        return  :   
        '''
        if None == s_ip or None == lun_ids or None == hg_id:
            log.error("Map lun:got wrong parameters.")
            os._exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=map_luns_to_host_group --lun_ids=%s --host_group_id=%s\"" % (
                s_ip, str(lun_ids), str(hg_id)))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Map lun error.")
                os._exit(1)
            else:
                log.info("Map lun success.")

    def write_iqn(self, cli_ip=None, iqn=None):
        '''
        date    :   2018-06-09
        Description ： write iqn
        param   :  cli_ip : 客户端IP iqn : iqn
        return  :   None
        '''
        if None == cli_ip or None == iqn:
            log.error("Write iqn:got wrong parameters.")
            os._exit(1)
        else:
            cmd = ("ssh %s \"echo InitiatorName=%s > /etc/iscsi/initiatorname.iscsi;service iscsid restart\"" % (
                cli_ip, str(iqn)))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Write iqn error.")
                os._exit(1)
            else:
                log.info("Write iqn success.")

    def delete_lun_map(self, s_ip=None, map_id=None):
        '''
        date    :   2018-06-19
        Description ： 
        param   :  s_ip : 服务节点IP map_id : map ID
        return  :   None
        '''
        if None == s_ip or None == map_id:
            log.error("Delete lun map:got wrong parameters.")
            os._exit(1)
        else:
            cmd = ("pscli --command=delete_lun_map --id=%s" % (str(map_id),))
            log.info(cmd)
            (res, final) = self.run_pscli_cmd(pscli_cmd=cmd, times=1)
            if res != 0:
                log.error(final)
                log.error("Delete map : %s error." % (str(map_id)))
                os._exit(1)
            else:
                log.info("Delete map : %s success." % (str(map_id)))

    def delete_lun(self, s_ip=None, lun_id=None):
        '''
        date    :   2018-06-19
        Description ： 
        param   :  s_ip : 服务节点IP id : lun ID
        return  :   None
        '''
        if None == lun_id:
            log.error("Delete lun:got wrong parameters.")
            os._exit(1)
        else:
            cmd = (" pscli --command=delete_lun --id=%s" % (str(lun_id)))
            log.info(cmd)
            (res, final) = self.run_pscli_cmd(s_ip=s_ip, pscli_cmd=cmd)
            if res != 0:
                log.error(final)
                log.error("Delete lun : %s error." % (str(lun_id)))
                os._exit(1)
            else:
                log.info("Delete lun : %s success." % (str(lun_id)))

    def remove_initiator(self, s_ip=None, ini_id=None):
        '''
        date    :   2018-07-02
        Description ： 
        param   :  s_ip : 服务节点IP ini_id : initiator ID
        return  :   None
        '''
        if None == s_ip or None == ini_id:
            log.error("Remove intiator:got wrong parameters.")
            os._exit(1)
        else:
            cmd = ("ssh %s \" pscli --command=remove_initiator --id=%s\"" % (s_ip, str(ini_id)))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Remove initiator : %s error." % (str(ini_id)))
                os._exit(1)
            else:
                log.info("Remove initiator : %s success." % (str(ini_id)))

    ###########################    获取信息相关操作    ####################
    def get_node_pool_disks(self, s_ip=None, ids=None, nodeid=1):
        '''
        date    :   2018-06-04
        Description :   获取节点池磁盘id
        param   :   ids : 节点池ID  nodeid : 节点ID
        return  :   list[diskid]
        '''
        disk_ids = []
        if None == s_ip:
            log.error("Got wrong server_ip: %s" % (s_ip))
            # os._exit(1)
        else:
            cmd = ("ssh %s \" pscli --command=get_free_disks_by_node_pool_id --ids=%s\"" % (s_ip, str(ids)))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Get node pool disk error.")
                os._exit(1)
            else:
                log.info("Get node pool disk success.")
            final = json.loads(final)
            finals = final['result']
            if len(finals) == 0:
                log.error("There is no disks.")
                os._exit(1)
            for i in range(0, len(finals[0]['children'])):
                if finals[0]['children'][i]['node_id'] == int(nodeid):
                    for j in range(0, len(finals[0]['children'][i]['children'])):
                        disk_ids.append(finals[0]['children'][i]['children'][j]['id'])
        if len(disk_ids) != 0:
            return disk_ids
        else:
            log.error("Found no disks.Maybe you put a wrong node id.")
            os._exit(1)

    def get_vip_address_pools(self, s_ip=None, n_id="1"):
        '''
        date    :   2018-05-15
        Description :   获取VIP
        param   :   s_ip : iscsi服务端IP;n_id : 节点ID
        return  :   VIP(二元列表)
        '''
        vip_list = []
        if None == s_ip:
            log.error("Got wrong server_ip: %s" % (s_ip))
            os._exit(1)
        else:
            cmd = ("ssh %s \" pscli --command=get_vip_address_pools --ids=%s\"" % (s_ip, str(n_id)))
            (res, final) = commands.getstatusoutput(cmd)
            log.info(cmd)
            if res != 0:
                log.error(final)
                log.error("Get_vip_address_pools error.")
                # os._exit(1)
            else:
                log.info("Get_vip_address_pools success.")
                final = json.loads(final)
                if final['result']['total'] == 0:
                    os._exit(1)
                else:
                    finals = final['result']['ip_address_pools']
                    for vip in finals:
                        vip_list.append(vip['vip_addresses'])
                log.info("Get VIP list: %s" % (vip_list))
                return vip_list

    def get_svip(self, s_ip=None, ids=1):
        '''
        date    :   2018-07-06
        Description :   获取SVIP
        param   :   s_ip : iscsi服务端IP;
        return  :   SVIP
        '''
        vip_list = []
        if None == s_ip:
            log.error("Got wrong server_ip: %s" % (s_ip))
            os._exit(1)
        else:
            cmd = ("ssh %s \" pscli --command=get_subnets --ids=%s\"" % (s_ip, str(ids)))
        (res, final) = commands.getstatusoutput(cmd)
        log.info(cmd)
        if res != 0:
            log.error(final)
            log.error("Get_subnets error.")
            # os._exit(1)
        else:
            log.info("Get_subnets success.")
        final = json.loads(final)
        if final['result']['total'] == 0:
            os._exit(1)
        else:
            finals = final['result']['subnets']
            for vip in finals:
                vip_list.append(vip['svip'])
        log.info("Get SVIP list: %s" % (vip_list))
        return vip_list

    def get_vip_address_pools_id(self, s_ip=None):
        '''
        date    :   2018-05-15
        Description :   获取VIP pool ID
        param   :   s_ip : iscsi服务端IP
        return  :   pool ID
        '''
        vip_id = []
        if None == s_ip:
            log.error("Got wrong server_ip: %s" % (s_ip))
            os._exit(1)
        else:
            cmd = ("ssh %s \" pscli --command=get_vip_address_pools\"" % (s_ip))
        (res, final) = commands.getstatusoutput(cmd)
        log.info(cmd)
        if res != 0:
            log.error(final)
            log.error("Get_vip_address_pools error.")
            os._exit(1)
        else:
            log.info("Get_vip_address_pools success.")
        final = json.loads(final)
        if final['result']['total'] == 0:
            os._exit(1)
        else:
            finals = final['result']['ip_address_pools']
            for vip in finals:
                vip_id.append(vip['id'])
        return vip_id

    def discover_scsi(self, client_ip, vip):
        '''
        date    :   2018-05-10
        Description :   发现iscsi服务器
        param   :   vip : VIP;client_ip : iscsi客户端IP
        return  :   target
        修改：在discovery中加入2>&1标准输出，规避discovery 提示timeout问题
        '''
        cmd = ("ssh %s \"iscsiadm -m discovery -t st -p %s 2>&1 \"" % (client_ip, vip))
        log.info(cmd)
        (res, target) = commands.getstatusoutput(cmd)
        if res != 0:
            log.error(target)
            log.error("Get target on %s error." % (vip))
            os._exit(1)
        else:
            log.info("Get target on %s success." % (vip))
            target = target.split(" ")[1]
            return target

    def iscsi_login(self, client_ip, iqn):
        '''
        date    :   2018-05-14
        Description :   登录
        param   :   client_ip : iscsi客户端IP;  iqn :   discover_scsi的返回值
        return  :   null
        '''
        cmd = ("ssh %s \"iscsiadm -m node -T %s -l\"" % (client_ip, iqn))
        (res, final) = commands.getstatusoutput(cmd)
        log.info(cmd)
        if res != 0:
            pass
        # log.error(final)
        #            log.error("Login on %s error." % (client_ip))
        else:
            pass
            # log.info("Login success on node %s." % (client_ip))

    def iscsi_logout(self, client_ip, vip=None):
        '''
        date    :   2018-05-14
        Description :   登出
        param   :   client_ip : iscsi客户端IP;  iqn :   discover_scsi的返回值
        return  :   null
        '''
        cmd1 = ("ssh root@%s 'iscsiadm -m node -u'" % client_ip)
        cmd2 = ("ssh root@%s 'iscsiadm -m node -o delete'" % client_ip)
        os.system(cmd1)
        os.system(cmd2)

    def iscsi_logout_all(self, client_ip):
        '''
        date    :   2018-05-14
        Description :   登出
        param   :   client_ip : iscsi客户端IP;  iqn :   discover_scsi的返回值
        return  :   null
        '''
        # cmd = ("ssh %s \"iscsiadm -m node --logoutall=all \"" % (client_ip))
        cmd = ("ssh %s \"iscsiadm -m node -u \"" % (client_ip))
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        if res != 0:
            log.error(final)
            log.error("Logout on %s error." % (client_ip))
        else:
            log.info("Logout success on node %s." % (client_ip))

    def ls_scsi_dev(self, client_ip):
        '''
        date    :   2018-05-16
        Description :  获取scsi设备名
        param   :   client_ip   :   iscsi客户端IP;
        return  :   scsi 设备名列表
        '''
        cmd = ("ssh %s \"lsscsi | grep Xstor\" | awk '{print $NF}'" % (client_ip))
        (res, final) = commands.getstatusoutput(cmd)
        log.info(cmd)
        if res != 0:
            log.error(final)
            log.error("Get scsi devices on %s error." % (client_ip))
            os._exit(1)
        else:
            log.info("Get scsi devices on %s success." % (client_ip))
        scsis = []
        scsis = final.split('\n')
        if len(scsis) == 0:
            log.error("There is no scsi devices on %s." % (client_ip))
            os._exit(1)
        return scsis

    def get_nodes(self, s_ip=None):
        '''
        date    :   2018-06-05
        Description :   获取节点ID
        param   :   s_ip : 服务节点IP
        return  :   节点ID
        '''
        nodeids = []
        # if None == s_ip:
        #     pass
        #     # log.error("Please input the corrent ip.")
        # else:
        # s_ip = s_ip.split()
        cmd = ("pscli --command=get_nodes")
        (res, final) = oSan().run_pscli_cmd(pscli_cmd=cmd)
        if res != 0:
            log.error("Get nodes error.")
            exit(1)
        else:
            log.info("Get nodes success.")
            final = json.loads(final)
            for i in range(0, len(final['result']['nodes'])):
                nodeids.append(final['result']['nodes'][i]['data_disks'][0]['nodeId'])
        return nodeids

    def get_storage_id(self, s_ip=None):
        '''
        date    :   2018-06-05
        Description :   获取存储池ID
        param   :   s_ip : 服务节点IP
        return  :   存储池ID
        '''
        storids = []
        if None == s_ip:
            log.error("Please input the correct ip.")
            os._exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=get_storage_pools\"" % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Get storage error.")
                os._exit(1)
            else:
                log.info("Get storage success.")
                final = json.loads(final)
                for i in range(0, final['result']['total']):
                    storids.append(final['result']['storage_pools'][i]['id'])
        return storids

    def get_subnet_id(self, s_ip=None):
        '''
        date    :   20.18-06-05
        Description :   获取subnet ID
        param   :   
        return  :   subnet ID
        '''
        subnetids = []
        if None == s_ip:
            log.error("Please input the corrent ip.")
            os._exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=get_subnets\"" % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Get subnet error.")
                os._exit(1)
            else:
                log.info("Get subnet success.")
                final = json.loads(final)
                for i in range(0, final['result']['total']):
                    subnetids.append(final['result']['subnets'][i]['id'])
        return subnetids

    def get_access_zone_id(self, s_ip=None):
        '''
        date    :   20.18-06-05
        Description :   获取访问区 ID
        param   :   
        return  :   access_zone ID
        '''
        access_zone_ids = []
        if None == s_ip:
            log.error("Please input the corrent ip.")
            os._exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=get_access_zones\"" % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Get access zone error.")
                os._exit(1)
            else:
                log.info("Get access zone success.")
                final = json.loads(final)
                for i in range(0, final['result']['total']):
                    access_zone_ids.append(final['result']['access_zones'][i]['id'])
        return access_zone_ids

    def get_access_node_ids(self, access_zone_id=1):
        """
        :param s_ip: node ip
        :return: access node ids list
        """
        cmd = ("ssh %s 'pscli --command=get_access_zones --ids=%d'" % (deploy_ips[0], access_zone_id))
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        if rc != 0:
            log.error(stdout)
            log.error("Get access zone error.")
            os._exit(1)
        else:
            log.info("Get access zone success.")
            final = json.loads(stdout)
            id = access_zone_id - 1
            node_ids = final['result']['access_zones'][id]['node_ids']
            return node_ids


    def get_hosts(self, s_ip=None):
        '''
        date    :   2018-06-06
        Description :   获取host ID
        param   ：  
        return  :   hosts ID
        '''
        hostids = []
        if None == s_ip:
            log.error("Please input the corrent ip.")
            os._exit(1)
        else:
            cmd = ("ssh %s \" pscli --command=get_hosts\"" % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if (res != 0):
                log.error(final)
                log.error("Get hosts error.")
                os._exit(1)
            else:
                log.info("Get hosts success.")
                final = json.loads(final)
                final = final['result']
                for i in range(0, final['total']):
                    hostids.append(final['hosts'][i]['id'])
            return hostids

    def get_host_groups(self, s_ip=None):
        '''
        date    :   2018-06-09
        Description :   获取host ID
        param   ：  
        return  :   host_group ID
        '''
        hostgroupids = []
        if None == s_ip:
            log.error("Please input the correct ip.")
            os._exit(1)
        else:
            cmd = ("ssh %s \" pscli --command=get_host_groups\"" % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if (res != 0):
                log.error(final)
                log.error("Get host group error.")
                os._exit(1)
            else:
                log.info("Get host group success.")
                final = json.loads(final)
                final = final['result']
                for i in range(0, final['total']):
                    hostgroupids.append(final['host_groups'][i]['id'])
            return hostgroupids

    def get_lun(self, s_ip=None):
        '''
        date    :   2018-06-09
        Description :   获取lun ID
        param   ：  
        return  :   lun ID
        '''
        log.info("will get all lun ids")
        lunids = []
        cmd = "pscli --command=get_luns"
        log.info(cmd)
        (res, final) = self.run_pscli_cmd(s_ip=s_ip, pscli_cmd=cmd)
        if res != 0:
            log.error(final)
            log.error("Get luns error.")
            os._exit(1)
        else:
            log.info("Get luns success.")
            final = json.loads(final)
            final = final['result']
            for i in range(0, final['total']):
                lunids.append(final['luns'][i]['id'])
        return lunids

    def get_lun_nums(self, s_ip=None):
        cmd = 'pscli --command=get_luns'
        log.info(cmd)
        res, final = self.run_pscli_cmd(s_ip=s_ip, pscli_cmd=cmd)
        if res != 0:
            log.error(final)
            log.error("Get luns total nums error.")
        else:
            log.info("Get luns total nums success.")
            result = json.loads(final)
            lun_nums = result['result']['total']
            return lun_nums

    def get_lun_maps(self, s_ip=None):
        '''
        date    :   2018-06-19
        Description :   获取lun map ID
        param   ：  
        return  :   lun map ID
        '''
        lunmapids = []
        cmd = "pscli --command=get_lun_maps"
        log.info(cmd)
        (res, final) = self.run_pscli_cmd(s_ip=s_ip, pscli_cmd=cmd)
        if res != 0:
            log.error(final)
            log.error("Get lun maps error.")
            os._exit(1)
        else:
            log.info("Get lun maps success.")
            final = json.loads(final)
            final = final['result']
            for i in range(0, final['total']):
                lunmapids.append(final['lun_maps'][i]['id'])
        return lunmapids

    def get_lun_maps_by_lunid(self, s_ip=None, lun_ids=None):
        '''
        date    :   2018-06-19
        Description :   获取lun map ID
        param   ：  
        return  :   lun map ID
        '''
        lunmapids = []
        if None == s_ip:
            log.error("Please input the correct ip.")
            os._exit(1)
        elif None == lun_ids:
            cmd = ("ssh %s \"pscli --command=get_lun_maps_by_lun_id \"" % (s_ip))
        else:
            cmd = ("ssh %s \"pscli --command=get_lun_maps_by_lun_id --lun_ids=%s\"" % (s_ip, str(lun_ids)))
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        if (res != 0):
            log.error(final)
            log.error("Get lun maps error.")
            os._exit(1)
        else:
            log.info("Get lun maps success.")
            final = json.loads(final)
            final = final['result']
            for i in range(0, final['total']):
                lunmapids.append(final['lun_maps'][i]['id'])
        return lunmapids

    def get_iqn(self, s_ip=None, ids=None):
        '''
        date    :   2018-06-09
        Description :   获取iqn
        param   ：  
        return  :   iqn
        '''
        iqn_ids = []
        if None == s_ip:
            log.error("Please input the correct ip.")
            os._exit(1)
        else:
            if None == ids:
                cmd = ("ssh %s \"pscli --command=get_initiators\"" % (s_ip))
            else:
                cmd = ("ssh %s \"pscli --command=get_initiators --ids=%s\"" % (s_ip, str(ids)))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if (res != 0):
                log.error(final)
                log.error("Get iqns error.")
                os._exit(1)
            else:
                log.info("Get iqns success.")
                final = json.loads(final)
                final = final['result']
                for i in range(0, final['total']):
                    iqn_ids.append(final['initiators'][i]['name'])
            return iqn_ids

    def get_initiators(self, s_ip=None):
        '''
        date    :   2018-06-09
        Description :   获取initiators ID
        param   ：  
        return  :   initiators ID
        '''
        iqn_ids = []
        if None == s_ip:
            log.error("Please input the correct ip.")
            os._exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=get_initiators\"" % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if (res != 0):
                log.error(final)
                log.error("Get initiators ID error.")
                os._exit(1)
            else:
                log.info("Get initiators ID success.")
                final = json.loads(final)
                final = final['result']
                for i in range(0, final['total']):
                    iqn_ids.append(final['initiators'][i]['id'])
            return iqn_ids

    def analysis_vip(self, vip=None):
        '''
        date    :   2018-06-22
        Description :  解析vip列表为单个vip
        param   :   vip : vip
        return  :   vip_list
        '''
        print vip
        vips = []
        if type(vip) == str:
            vip = vip.split(',')
        elif type(vip) == list and len(vip) == 1:
            vip = vip[0].split(',')
        for tmp_vip in vip:
            if '-' in tmp_vip:
                ip = re.match('(\d+.\d+.\d+).(\d+)-(\d+)', tmp_vip)
                for j in range(int(ip.group(2)), int(ip.group(3)) + 1):
                    vips.append(ip.group(1) + '.' + str(j))
            else:
                vips.append(tmp_vip)
        return vips

    def get_los_id(self, s_ip=None, lun_id=None):
        '''
        date    :   2018-07-11
        Description :   获取los ID
        param   ：  
        return  :   los ID
        '''
        #        losids = []
        #        if None == s_ip:
        #            log.error("Please input the correct ip.")
        #            os._exit(1)
        #        else:
        #            if None == lun_id:
        #                cmd = ("ssh %s \"pscli --command=get_luns\"" % (s_ip))
        #            else:
        #                cmd = ("ssh %s \"pscli --command=get_luns --ids=%s\"" % (s_ip,str(lun_id)))
        #            log.info(cmd)
        #            (res, final) = commands.getstatusoutput(cmd)
        #            if(res != 0):
        #                log.error(final)
        #                log.error("Get luns los error.")
        #                os._exit(1)
        #            else:
        #                log.info("Get luns los success.")
        #                final = json.loads(final)
        #                final = final['result']
        #                for i in range(0,final['total']):
        #                    losids.append(final['luns'][i]['id'])
        #            return losids
        nodeids = []
        if None == s_ip:
            log.error("Please input the corrent ip.")
            os._exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=get_nodes\"" % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Get nodes error.")
                os._exit(1)
            else:
                log.info("Get nodes success.")
                final = json.loads(final)
                for i in range(0, len(final['result']['nodes'])):
                    nodeids.append(final['result']['nodes'][i]['data_disks'][0]['nodeId'])
        return nodeids

    ###########################    vdbench相关操作    ####################
    # ===================================================
    # latest date :2018-08-2
    # author: wangxiang
    # ===================================================
    # 2018-08-2:
    # 修改者:wangxiang
    # 1.添加一些参数
    def gen_vdb_xml(self, max_range='100M', maxdata='100G', thread=16, offset=None, align=None, lun=None, xfersize=None,
                    rdpct=None, seekpct=None, interval=1, maxrange_multi_arg=None):
        '''
        date    :   2018-05-17
        Description :   生成vdbench配置文件
        param   :  vdbench标准配置参数
        return  :   vdbench xml file path
        '''
        t1 = datetime.datetime.now()
        template_file = get_config.get_tools_path() + "/osan/template"  # 获取配置文件模板路径
        vdb_xml = get_config.get_tools_path() + "/osan/vdb_xml." + str(t1.microsecond)  # vdbench测试所用的文件
        sd_num = 1  # 初始化sd数量
        threads = []
        # vdb_path = get_config.get_vdbench_path()        #获取vdbench路径
        if True == os.path.exists(vdb_xml):
            cmd = ("rm -rf %s" % (vdb_xml))
            log.info(cmd)
            commands.getstatusoutput(cmd)
        cmd = ("cp %s %s" % (template_file, vdb_xml))
        log.info(cmd)
        commands.getstatusoutput(cmd)
        if None == lun or len(lun) == 0:
            log.error("Found no scsi devices.")
            os._exit(1)
        if None != offset:
            cmd = ("sed -i '1s/$/,offset=%s/g' %s" % (str(offset), vdb_xml))  # 修改前偏移量
            #            log.info("Modify vdb_xml cmd %s" % (cmd))
            log.info(cmd)
            commands.getstatusoutput(cmd)
        if None != align:
            cmd = ("sed -i '1s/$/,align=%s/g' %s" % (str(align), vdb_xml))  # 修改后偏移量
            #            log.info("Modify vdb_xml cmd %s" % (cmd))
            log.info(cmd)
            commands.getstatusoutput(cmd)
        if None != rdpct:
            cmd = ("sed -i '2s/$/,rdpct=%s/g' %s" % (str(rdpct), vdb_xml))  # 修改读写占比
            log.info(cmd)
            commands.getstatusoutput(cmd)
        if None != seekpct:
            cmd = ("sed -i '2s/$/,seekpct=%s/g' %s" % (str(seekpct), vdb_xml))  # 修改读写占比
            #            log.info("Modify vdb_xml cmd %s" % (cmd))
            log.info(cmd)
            commands.getstatusoutput(cmd)
        if None != xfersize:
            cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=%s/g' %s" % (xfersize, vdb_xml))  # 修改xferrsize
            #            log.info("Modify vdb_xml cmd %s" % (cmd))
            log.info(cmd)
            commands.getstatusoutput(cmd)
        for dev_name in lun:
            if max_range and maxrange_multi_arg:
                sd_xml = ("sd=sd%d,lun=%s,range=(%s)" % (sd_num, dev_name, max_range))
            elif max_range:
                sd_xml = ("sd=sd%d,lun=%s,range=(0,%s)" % (sd_num, dev_name, max_range))
            else:
                sd_xml = ("sd=sd%d,lun=%s" % (sd_num, dev_name))
            wd_xml = ("wd=wd%d,sd=sd%d" % (sd_num, sd_num))
            cmd = ("sed -i '%da\%s' %s" % (sd_num, sd_xml, vdb_xml))  # 插入rd
            log.info(cmd)
            commands.getstatusoutput(cmd)
            cmd = ("sed -i '$i\%s' %s" % (wd_xml, vdb_xml))  # 插入wd
            log.info(cmd)
            commands.getstatusoutput(cmd)
            sd_num = sd_num + 1
            # threads.append("10")
        # threads = "3"
        '''
        if max_range:
            if isinstance(max_range[:-1], int):
                max = len(lun) * int(max_range[:-1]) * 2
                if max_range[-1] == 'G':
                    maxdata = str(max) + 'G'
                elif max_range[-1] == 'M':
                    maxdata = str(max / 1000 + 1) + 'G'
        '''
        cmd = ("sed -i -r 's/thread.*?\)/threads=%s/g' %s" % (thread, vdb_xml))  # 修改每个wd的进程数
        log.info(cmd)
        commands.getstatusoutput(cmd)
        cmd = ("sed -i -r 's/interval.*?/interval=%s/g' %s" % (interval, vdb_xml))  # 修改每个wd的interval
        log.info(cmd)
        commands.getstatusoutput(cmd)
        cmd = ("sed -r -i 's/maxdata=[0-9]+[a-zA-Z]+,/maxdata=%s,/g' %s" % (str(maxdata), vdb_xml))  # 修改每个wd的maxdata
        log.info(cmd)
        commands.getstatusoutput(cmd)
        cmd = ("sed -r -i '1idata_errors=3' %s" % (vdb_xml))
        log.info(cmd)
        commands.getstatusoutput(cmd)
        cmd = ("sed -r -i '1idebug=27' %s" % (vdb_xml))
        log.info(cmd)
        commands.getstatusoutput(cmd)
        log.info(vdb_xml)
        return vdb_xml

    def gen_stress_vdb(self, offset=None, align=None, lun_nums=512, xfersize='4k', rdpct=0, seekpct=0, iorate=1000, threads=64,
                       warmup=60, maxdata=None, elapsed=3600, model=None):
        """
        :fucktion: 生成vdbench压力参数
        :return:  vdbench压力配置文件
        """
        parm_time = datetime.datetime.now()
        vdb_xml = get_config.get_tools_path() + '/osan/vdb_xml.' + str(parm_time.microsecond)   # vdbench测试所用的文件
        if True == os.path.exists(vdb_xml):
            cmd = ("rm -f %s" % (vdb_xml))
            log.info(cmd)
            os.system(cmd)
        with open(vdb_xml, 'a+') as vdb_wt:
            vdb_wt.write('data_errors=3\n')
            vdb_wt.write('hd=default,vdbench=/home/vdbench,user=root,shell=ssh\n')
            count = 1
            for client in client_ips:
                vdb_wt.write('hd=hd%s,system=%s\n' % (str(count), client))
                count += 1
            if offset == None and align == None:
                vdb_wt.write('sd=default,journal=/root/vdbench/journal,openflags=o_direct\n')
            elif offset !=None and align == None:
                vdb_wt.write('sd=default,journal=/root/vdbench/journal,openflags=o_direct,offset=%s\n' % offset)
            elif offset == None and align != None:
                vdb_wt.write('sd=default,journal=/root/vdbench/journal,openflags=o_direct,align=%s\n' % align)
            else:
                vdb_wt.write('sd=default,journal=/root/vdbench/journal,openflags=o_direct,offset=%s,align=%s\n' % (offset, align))
            sd_count = 1
            for client in client_ips:
                disk_label_list = self.ls_scsi_dev(client)
                if lun_nums/len(client_ips) < len(disk_label_list):
                    disk_label_list = disk_label_list[0:lun_nums/len(client_ips)]
                for disk_label in disk_label_list:
                    vdb_wt.write('sd=sd%d,hd=hd%d,lun=%s\n' % (sd_count, client_ips.index(client)+1, disk_label))
                    sd_count += 1
            vdb_wt.write('wd=default,xfersize=%s,rdpct=%s,seekpct=%s\n' % (xfersize, rdpct, seekpct))
            wd_count = 1
            for client in client_ips:
                disk_label_list = self.ls_scsi_dev(client)
                if lun_nums/len(client_ips) < len(disk_label_list):
                    disk_label_list = disk_label_list[0:lun_nums/len(client_ips)]
                for disk_label in disk_label_list:
                    vdb_wt.write('wd=wd%d,sd=sd%d\n' % (wd_count, wd_count))
                    wd_count += 1
            if model == None and maxdata != None:
                vdb_wt.write('rd=run1,wd=wd*,iorate=%s,maxdata=%sG,threads=%s,elapsed=%s,warmup=%s,interval=1'
                             % (iorate,maxdata,threads,elapsed,warmup))
            elif model == None and maxdata == None:
                vdb_wt.write('rd=run1,wd=wd*,iorate=%s,threads=%s,elapsed=%d,warmup=%d,interval=1'
                             % (iorate, threads, elapsed, warmup))
            elif 'iorate' in model and 'thread' not in model:
                vdb_wt.write('rd=run1,wd=wd*,%s,threads=%s,elapsed=%d,warmup=%d,interval=1' % (model,threads,elapsed,warmup))
            elif 'thread' in model and 'iorate' not in model:
                vdb_wt.write('rd=run1,wd=wd*,iorate=%s,%s,elapsed=%d,warmup=%d,interval=1' % (iorate,model,elapsed,warmup))
            else:
                vdb_wt.write('rd=run1,wd=wd*,%s,elapsed=%d,warmup=%d,interval=1' % (model,elapsed,warmup))

        log.info(vdb_xml)
        return vdb_xml

    def view_vdb_result(self, client_ip=client_ips[0], output='stress_io_nor'):
        result_path = '/root/output/' + output
        cmd1 = ("ssh %s 'cat %s/summary.html' | grep 'avg' | awk -F 'avg' '{print $2}'" % (client_ip, result_path))
        rc1, result = commands.getstatusoutput(cmd1)
        cmd2 = ("ssh %s 'cat %s/totals.html' | grep 'Starting.*threads' | awk -F 'threads=' '{print $2}' | awk -F '</b>' '{print $1}'"
                % (client_ip, result_path))
        rc2, final = commands.getstatusoutput(cmd2)
        cmd3 = ("ssh %s 'cat %s/parmfile.html' | grep 'wd=default' | awk -F 'wd=default,' '{print $2}'" % (client_ip, result_path))
        rc3, final2 = commands.getstatusoutput(cmd3)
        lun_nums = self.get_lun_nums(deploy_ips[0])
        if 0 != rc1 or 0 != rc2:
            log.error("Can't view the output of vdbench in %s" % client_ip)
            os._exit(1)
        else:
            result_list = result.split('\n')
            threads_list = final.split('\n')
            iorate_list = []
            bw_list = []
            log.info("----------------------------------------------------------------------")
            log.info("Result count | iorate  | bandwidth | resp_time | resp_max | queue_depth | threads")
            count = 1
            for each_res in result_list:
                result = each_res.split()
                log.info("----------------------------------------------------------------------")
                res_line = ("Result %-5s | %-7s | %-9s | %-9s | %-8s | %-11s | %-7s"
                            % (str(count), result[1], result[2], result[5], result[8], result[10], threads_list[count - 1]))
                log.info(res_line)
                iorate_list.append(float(result[1]))
                bw_list.append(float(result[2]))
                count += 1
            log.info("----------------------------------------------------------------------")
            log.info("the IO model: %s" % final2)
            log.info("the Max IOPS: %s, threads:%s, LUN nums:%s"
                     % (max(iorate_list), threads_list[iorate_list.index(max(iorate_list))], str(lun_nums)))
            return None

    def change_xml(self, s_ip=None, jn_on=None, vdb_xml=None, whether_change="Y"):
        if whether_change == "Y":
            type_info = get_config.get_machine_type(CONF_FILE)
            node_num = len(oSan().get_nodes(s_ip))
            if node_num == 5:
                if type_info == "phy":
                    if jn_on != None:
                        # 修改xfersize
                        cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=(1k,10,4k,25,15k,20,128k,20,213k,25)/g' %s"
                               % (vdb_xml))
                        commands.getstatusoutput(cmd)
                        # 修改range
                        cmd = ("sed -r -i 's/range=.*\)/range=(0,3G)/g' %s" % (vdb_xml,))
                        commands.getstatusoutput(cmd)
                        # 修改iorate
                        cmd = ("sed -r -i 's/iorate=[0-9]+/iorate=1500/g' %s" % (vdb_xml,))
                        commands.getstatusoutput(cmd)

                        # cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=(8k)/g' %s"
                        #        % (vdb_xml))
                        # commands.getstatusoutput(cmd)
                        # # 修改range
                        # cmd = ("sed -r -i 's/range=.*\)/range=(0,100M)/g' %s" % (vdb_xml,))
                        # commands.getstatusoutput(cmd)
                        # # 修改iorate
                        # cmd = ("sed -r -i 's/iorate=[0-9]+/iorate=2000/g' %s" % (vdb_xml,))
                        # commands.getstatusoutput(cmd)
                        # 修改threads
                        cmd = ("sed -r -i 's/threads=[0-9]+/threads=16/g' %s" % (vdb_xml,))
                        commands.getstatusoutput(cmd)
                        # 修改maxdata
                        cmd = ('grep -c lun %s' % (vdb_xml,))
                        res, lun_num = commands.getstatusoutput(cmd)
                        maxdata = int(lun_num) * 3 + 4
                        cmd = ("sed -r -i 's/maxdata=[0-9]+[a-zA-Z]+,/maxdata=%sG,/g' %s" % (str(maxdata), vdb_xml,))
                        commands.getstatusoutput(cmd)
                    else:
                        # 修改xfersize
                        cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=(4k,30,15k,20,127k,20,213k,30)/g' %s"
                               % (vdb_xml,))
                        commands.getstatusoutput(cmd)
                        # 修改range
                        cmd = ("sed -r -i 's/range=.*\)/range=(0,5G)/g' %s" % (vdb_xml,))
                        commands.getstatusoutput(cmd)
                        # 修改iorate
                        cmd = ("sed -r -i 's/iorate=[0-9]+/iorate=1500/g' %s" % (vdb_xml,))
                        commands.getstatusoutput(cmd)

                        # # 修改xfersize
                        # cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=(8k)/g' %s"
                        #        % (vdb_xml,))
                        # commands.getstatusoutput(cmd)
                        # # 修改range
                        # cmd = ("sed -r -i 's/range=.*\)/range=(0,100M)/g' %s" % (vdb_xml,))
                        # commands.getstatusoutput(cmd)
                        # # 修改iorate
                        # cmd = ("sed -r -i 's/iorate=[0-9]+/iorate=2000/g' %s" % (vdb_xml,))
                        # commands.getstatusoutput(cmd)
                        # 修改threads
                        cmd = ("sed -r -i 's/threads=[0-9]+/threads=16/g' %s" % (vdb_xml,))
                        commands.getstatusoutput(cmd)
                        # 修改maxdata
                        cmd = ('grep -c lun %s' % (vdb_xml,))
                        res, lun_num = commands.getstatusoutput(cmd)
                        maxdata = int(lun_num) * 5 + 4
                        cmd = ("sed -r -i 's/maxdata=[0-9]+[a-zA-Z]+,/maxdata=%sG,/g' %s" % (str(maxdata), vdb_xml))
                        commands.getstatusoutput(cmd)
            elif node_num == 3:
                if type_info == "phy":
                    if jn_on != None:
                        # # 修改xfersize
                        # cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=(1k,20,3k,35,16k,20,127k,10,212k,15)/g' %s"
                        #        % (vdb_xml))
                        # commands.getstatusoutput(cmd)
                        # # 修改range
                        # cmd = ("sed -r -i 's/range=.*\)/range=(0,2G)/g' %s" % (vdb_xml,))
                        # commands.getstatusoutput(cmd)
                        # # 修改iorate
                        # cmd = ("sed -r -i 's/iorate=[0-9]+/iorate=1000/g' %s" % (vdb_xml,))
                        # commands.getstatusoutput(cmd)

                        # 修改xfersize
                        cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=(3k)/g' %s"
                               % (vdb_xml))
                        commands.getstatusoutput(cmd)
                        # 修改range
                        cmd = ("sed -r -i 's/range=.*\)/range=(0,100M)/g' %s" % (vdb_xml,))
                        commands.getstatusoutput(cmd)
                        # 修改iorate
                        cmd = ("sed -r -i 's/iorate=[0-9]+/iorate=400/g' %s" % (vdb_xml,))
                        commands.getstatusoutput(cmd)

                        # 修改threads
                        cmd = ("sed -r -i 's/threads=[0-9]+/threads=8/g' %s" % (vdb_xml,))
                        commands.getstatusoutput(cmd)
                        # 修改maxdata
                        cmd = ('grep -c lun %s' % (vdb_xml,))
                        res, lun_num = commands.getstatusoutput(cmd)
                        maxdata = int(lun_num) * 3 + 4
                        cmd = ("sed -r -i 's/maxdata=[0-9]+[a-zA-Z]+,/maxdata=%sG,/g' %s" % (str(maxdata), vdb_xml,))
                        commands.getstatusoutput(cmd)
                    else:
                        # # 修改xfersize
                        # cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=(1k,20,4k,30,15k,20,127k,10,213k,20)/g' %s"
                        #        % (vdb_xml,))
                        # commands.getstatusoutput(cmd)
                        # # 修改range
                        # cmd = ("sed -r -i 's/range=.*\)/range=(0,4G)/g' %s" % (vdb_xml,))
                        # commands.getstatusoutput(cmd)
                        # # 修改iorate
                        # cmd = ("sed -r -i 's/iorate=[0-9]+/iorate=1000/g' %s" % (vdb_xml,))
                        # commands.getstatusoutput(cmd)

                        # 修改xfersize
                        cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=(3k)/g' %s"
                               % (vdb_xml,))
                        commands.getstatusoutput(cmd)
                        # 修改range
                        cmd = ("sed -r -i 's/range=.*\)/range=(0,100M)/g' %s" % (vdb_xml,))
                        commands.getstatusoutput(cmd)
                        # 修改iorate
                        cmd = ("sed -r -i 's/iorate=[0-9]+/iorate=400/g' %s" % (vdb_xml,))
                        commands.getstatusoutput(cmd)

                        # 修改threads
                        cmd = ("sed -r -i 's/threads=[0-9]+/threads=8/g' %s" % (vdb_xml,))
                        commands.getstatusoutput(cmd)
                        # 修改maxdata
                        cmd = ('grep -c lun %s' % (vdb_xml,))
                        res, lun_num = commands.getstatusoutput(cmd)
                        maxdata = 100
                        cmd = ("sed -r -i 's/maxdata=[0-9]+[a-zA-Z]+,/maxdata=%sG,/g' %s" % (str(maxdata), vdb_xml))
                        commands.getstatusoutput(cmd)
                else:
                    if jn_on == None:
                        maxdata = 100
                        cmd = ("sed -r -i 's/maxdata=[0-9]+[a-zA-Z]+,/maxdata=%sG,/g' %s" % (str(maxdata), vdb_xml))
                        commands.getstatusoutput(cmd)

    def set_rcvr(self, val=1):
        """
        :Author:Diws
        :Date:20181224
        :Description:设置修复开关
        :param val: 'close'或者1，为关闭
        :return:
        """
        return
        if val == 'close':
            val = 1
        elif val == 'open':
            val = 0
        cmd = 'pscli --command=update_param --section=oJob --name=rcvr_allstop --current=%s' % (str(val),)
        log.info(cmd)
        res, output = self.run_pscli_cmd(pscli_cmd=cmd)
        if res == 0:
            log.info("set rcvr success.")
        else:
            log.error("set rcvr failed.")
            log.error(output)

    def run_vdb(self, client_ip, vdb_xml, jn_jro=None, output=None, time=1200, execute="Y", whether_change_xml="Y",
                need_judge=None, unmap='N'):
        """
        执行vdbench
        :param client_ip:主机端IP
        :param vdb_xml:
        :param jn_jro:
        :param output:
        :param time:   执行时间
        :param execute: 是否执行vdbench，N 为不执行，非N就会执行
        :param whether_change_xml：是否执行change_xml，默认执行
        :return:
        """
        #self.set_rcvr(1)  # IO 前关闭修复
        if execute == "N":
            log.info("Will not run  vdbench 。。。")
        else:
            if vdb_xml == None:
                log.error("Please input vdb xml.")
                os._exit(1)
            vdb_xml1 = "/home/vdbench/vdb_xml"
            vdb_path = get_config.get_vdbench_path()  # vdbench工具所在路径
            cmd = ("ssh %s 'mkdir -p /root/output/;mkdir -p /root/vdbench/journal/%s'" % (
                client_ip, str(output)))
            log.info(cmd)
            commands.getstatusoutput(cmd)
            if time != None:
                cmd1 = (
                        "ssh %s '%s/vdbench -f %s -jn -e %s -o /root/output/%s_jn'" % (
                    client_ip, vdb_path, vdb_xml1, str(time), str(output)))
                cmd2 = (
                        "ssh %s '%s/vdbench -f %s -jro -e %s -o /root/output/%s_jro'" % (
                    client_ip, vdb_path, vdb_xml1, str(time), str(output)))
            else:
                cmd1 = ("ssh %s '%s/vdbench -f %s -jn  -o /root/output/%s_jn'" % (
                    client_ip, vdb_path, vdb_xml1, str(output)))
                cmd2 = (
                        "ssh %s '%s/vdbench -f %s -jro -o /root/output/%s_jro'" % (
                    client_ip, vdb_path, vdb_xml1, str(output)))
            if None == jn_jro or jn_jro == "no":
                self.change_xml(vdb_xml=vdb_xml, whether_change=whether_change_xml)
                cmd = ("scp %s root@%s:/home/vdbench/vdb_xml" % (vdb_xml, client_ip,))
                log.info(cmd)
                res, final = commands.getstatusoutput(cmd)
                if res != 0:
                    print final
                    os._exit(1)
                if unmap == 'Y':
                    cmd = ("ssh %s '/home/vdbench_unmap/vdbench -f %s -e %s -o /root/output/%s_nor'" % (
                        client_ip, vdb_xml1, str(time), str(output)))
                else:
                    cmd = ("ssh %s '%s/vdbench -f %s -e %s -o /root/output/%s_nor'" % (
                        client_ip, vdb_path, vdb_xml1, str(time), str(output)))
                log.info(cmd)
                res, out = commands.getstatusoutput(cmd)
                if res != 0:
                    if need_judge:
                        cmd = (
                            "ssh {} \"cat  /root/output/{}_nor/logfile.html|grep 'java.lang.RuntimeException'\"").format(
                            client_ip, output)
                        log.info(cmd)
                        res, final = commands.getstatusoutput(cmd)
                        if res != 0:
                            os._exit(1)
                        else:
                            pass
                    else:
                        log.error("Error! Run vdbench on %s without data check error." % (client_ip,))
                        os._exit(1)
                else:
                    pass
            elif jn_jro == "jn":
                self.change_xml(jn_on="yes", vdb_xml=vdb_xml, whether_change=whether_change_xml)
                ch_cmd = ("sed -r -i 's/,offset=[0-9]+//g' %s" % (vdb_xml))
                commands.getstatusoutput(ch_cmd)
                ch_cmd = ("sed -r -i 's/,align=[0-9]+//g' %s" % (vdb_xml))
                commands.getstatusoutput(ch_cmd)
                cmd = ("scp %s root@%s:/home/vdbench/vdb_xml" % (vdb_xml, client_ip,))
                log.info(cmd)
                res, final = commands.getstatusoutput(cmd)
                if res != 0:
                    print final
                    os._exit(1)
                log.info(cmd1)
                res, out = commands.getstatusoutput(cmd1)
                if res != 0:
                    if need_judge:
                        pass
                    else:
                        log.error(
                            "Error! Run vdbench with 'jn' error.Vdbench log path is %s:/root/output/%s." % (client_ip, str(output)))
                        os._exit(1)
                else:
                    log.info("Vdbench jn log path is /root/output.")

            elif jn_jro == "jro":
                self.change_xml(jn_on="yes", vdb_xml=vdb_xml, whether_change=whether_change_xml)
                log.info(cmd2)
                res, out = commands.getstatusoutput(cmd2)
                if res != 0:
                    log.error(
                        "Error! Run vdbench with 'jro' error.Vdbench log path is %s:/root/output/%s." % (client_ip, str(output)))
                    os._exit(1)
                else:
                    log.info("Vdbench jro log path is /root/output.")
            else:
                ch_cmd = ("sed -r -i 's/,offset=[0-9]+//g' %s" % (vdb_xml))
                commands.getstatusoutput(ch_cmd)
                ch_cmd = ("sed -r -i 's/,align=[0-9]+//g' %s" % (vdb_xml))
                commands.getstatusoutput(ch_cmd)
                self.change_xml(jn_on="yes", vdb_xml=vdb_xml, whether_change=whether_change_xml)
                cmd = ("scp %s root@%s:/home/vdbench/vdb_xml" % (vdb_xml, client_ip,))
                log.info(cmd)
                res, final = commands.getstatusoutput(cmd)
                if res != 0:
                    print final
                    os._exit(1)
                res, out = commands.getstatusoutput(cmd1)
                log.info(cmd1)
                if res != 0:
                    log.error(
                        "Error! Run vdbench with journal verify error.Vdbench log path is %s:/root/output/%s." % (
                            client_ip, str(output)))
                    os._exit(1)
                else:
                    log.info("Vdbench log path is /root/output.")
                    log.info(cmd2)
                    res, out = commands.getstatusoutput(cmd2)
                    if res != 0:
                        log.error("Error! Vdbench check data error,journal path is %s:/root/vdbench/journal." % (client_ip,))
                        os._exit(1)
                    else:
                        pass
            log.info("Check vdbench process exit completely.")
            cmd = ("ssh %s 'ps aux | grep -v grep | grep vdbench'" % client_ip)
            rc = os.system(cmd)
            if 0 != rc:
                log.info("Vdbench process has been exit.")
            else:
                log.info("Kill all vdbench process in clients.")
                cmd = ("ssh %s 'killall -p vdbench'" % client_ip)
                os.system(cmd)

        #self.set_rcvr(0)  # IO 完成打开修复

    def auto_gen_vdb_xml(self, lun=None, thread=None):
        '''
        date    :   2018-05-22
        Description :   随机生成vdbench配置文件
        param   :  vdbench标准配置参数
        return  :   vdbench xml file path
        '''
        sd_num = 1
        wd_num = 1
        threads = []
        t1 = datetime.datetime.now()
        template_file = get_config.get_tools_path() + "/osan/auto_vdb" + str(t1.microsecond)  # 获取配置文件模板路径
        template = open(template_file, "w+")
        sd_default = "sd=default,journal=/root/vdbench/journal,openflags=o_direct\n"
        template.write(sd_default)
        # Write sd.
        for dev_name in lun:
            offset = random.randint(0, 9999)
            align = random.randint(0, 9999)
            offset = offset - (offset % 512)
            align = align - (align % 512)
            range_low = random.randint(0, 100)
            range_high = 3
            sd = ("sd=sd%d,lun=%s,offset=%d,align=%d,range=(%dM,%dG)\n" % (
                sd_num, dev_name, offset, align, range_low, range_high))
            sd_num = sd_num + 1
            template.write(sd)
        # Write wd.
        for dev_name in lun:
            # 读写比例
            rdpct = random.randint(0, 100)
            # 随机比例
            seekpct = random.randint(0, 100)
            # 读写块大小
            xfer1 = random.randint(1, 256)
            xfer2 = random.randint(1, 256)
            xfer3 = random.randint(1, 256)
            xfer4 = random.randint(1, 256)
            # 读写百分比
            seed = 100
            xfer_pcnt1 = random.randint(1, (seed / 2))
            xfer_pcnt2 = random.randint(1, (100 - xfer_pcnt1) / 2)
            xfer_pcnt3 = random.randint(1, (100 - xfer_pcnt2 - xfer_pcnt1) / 2)
            xfer_pcnt4 = 100 - xfer_pcnt1 - xfer_pcnt2 - xfer_pcnt3
            wd = ("wd=wd%d,sd=sd%d,xfersize=(%dk,%d,%dk,%d,%dk,%d,%dk,%d),rdpct=%d,seekpct=%d\n") % (wd_num, wd_num,
                                                                                                     xfer1, xfer_pcnt1,
                                                                                                     xfer2, xfer_pcnt2,
                                                                                                     xfer3, xfer_pcnt3,
                                                                                                     xfer4, xfer_pcnt4,
                                                                                                     rdpct, seekpct)
            wd_num = wd_num + 1
            template.write(wd)
        # 队列深度，默认为4
        # for dev_name in lun:
        if None == thread:
            threads = "3"
        else:
            threads = str(thread)
        rd = ("rd=run1,wd=wd*,iorate=300,elapsed=600,maxdata=500G,threads=%s,interval=1\n") % (
            re.sub("'| ", "", str(threads)))
        template.write(rd)
        template.close()
        return template_file

    def auto_gen_vdb_jn_xml(self, lun=None, thread=None, output=None):
        '''
        date    :   2018-05-22
        Description :   随机生成vdbench数据校验配置文件
        param   :  vdbench标准配置参数
        return  :   vdbench xml file path
        '''
        sd_num = 1
        wd_num = 1
        threads = []
        t1 = datetime.datetime.now()
        template_file = get_config.get_tools_path() + "/osan/auto_vdb" + str(t1.microsecond)  # 获取配置文件模板路径
        template = open(template_file, "w+")
        sd_default = "sd=default,journal=/root/vdbench/journal/%s,openflags=o_direct\n" % (str(output))
        template.write(sd_default)
        # Write sd.
        for dev_name in lun:
            # offset = random.randint(0,9999)
            # align = random.randint(0,9999)
            # offset = offset-(offset%512)
            # align = align-(align%512)
            # sd = ("sd=sd%d,lun=%s,offset=%d,align=%d\n" % (sd_num, dev_name,offset,align))
            range_low = random.randint(0, 100)
            # range_high = range_low+60
            range_high = 3
            sd = ("sd=sd%d,lun=%s,range=(%dM,%dG)\n" % (sd_num, dev_name, range_low, range_high))
            sd_num = sd_num + 1
            template.write(sd)
        # Write wd.
        for dev_name in lun:
            # 读写比例
            rdpct = random.randint(0, 100)
            # 随机比例
            seekpct = random.randint(0, 100)
            # 读写块大小
            seed = random.randint(1, 4)
            xfer1 = random.randint(1, 2)
            xfer2 = random.randint(1, 64)
            seed = random.randint(1, 4)
            xfer3 = xfer2 * seed
            seed = random.randint(1, 4)
            xfer4 = xfer2 * seed
            # 读写百分比
            seed = 100
            xfer_pcnt1 = random.randint(1, (seed / 2))
            xfer_pcnt2 = random.randint(1, (100 - xfer_pcnt1) / 2)
            xfer_pcnt3 = random.randint(1, (100 - xfer_pcnt2 - xfer_pcnt1) / 2)
            xfer_pcnt4 = 100 - xfer_pcnt1 - xfer_pcnt2 - xfer_pcnt3
            wd = ("wd=wd%d,sd=sd%d,xfersize=(%dk,%d,%dk,%d,%dk,%d,%dk,%d),rdpct=%d,seekpct=%d\n") % (wd_num, wd_num,
                                                                                                     xfer1, xfer_pcnt1,
                                                                                                     xfer2, xfer_pcnt2,
                                                                                                     xfer3, xfer_pcnt3,
                                                                                                     xfer4, xfer_pcnt4,
                                                                                                     rdpct, seekpct)
            wd_num = wd_num + 1
            template.write(wd)
        # 队列深度，默认为4
        #        for dev_name in lun:
        if None == thread:
            threads = "3"
        else:
            threads = str(thread)
        # threads = tuple(threads)
        #        threads = 4
        max_data = len(lun) * 3
        # rd = ("rd=run1,wd=wd*,iorate=max,elapsed=600h,maxdata=3,threads=%s,interval=1\n") %(re.sub("'| ","",str(threads)))
        rd = ("rd=run1,wd=wd*,iorate=300,elapsed=600h,maxdata=%dG,threads=(5),interval=1\n" % (max_data))
        template.write(rd)
        template.close()
        return template_file

    def vdb_write(self, sd=None, lun=None, wd=None, xfersize="4k", rdpct=0, seekpct=0, threads=4, align=None,
                  skew=None):
        write_file = get_config.get_tools_path() + "/osan/write_vdb"  # 获取配置文件模板路径
        if "default" == sd:
            w_file = open(write_file, "w+")
            sd_default = (
                "data_errors=3,misc=(fifo=1000)\nsd=default,journal=/root/vdbench/journal,openflags=o_direct\n")
            w_file.write(sd_default)
            rd = ("rd=run1,wd=wd*,iorate=200,elapsed=1600,maxdata=1G,interval=1\n")
            w_file.write(rd)
            w_file.close()
        elif None == lun or None == sd or None == wd:
            log.error("Got wrong parameter.")
            os._exit(1)
        else:
            w_file = open(write_file, "a+")
            if None == skew:
                sd_line = ("sd=%s,lun=%s,threads=%s\n" % (
                    sd, lun, str(threads)))
                wd_line = ("wd=%s,sd=%s,xfersize=%s,rdpct=%s,seekpct=%s\n" % (
                    wd, sd, str(xfersize), str(rdpct), str(seekpct)))
            else:
                sd_line = ("sd=%s,lun=%s,range=(0,100M),threads=%s\n" % (
                    sd, lun, str(threads)))
                wd_line = ("wd=%s,sd=%s,xfersize=%s,rdpct=%s,seekpct=%s,skew=%s\n" % (
                    wd, sd, str(xfersize), str(rdpct), str(seekpct), str(skew)))
            w_file.write(sd_line)
            w_file.write(wd_line)
            w_file.close()
        cmd = ("sort %s -o %s;s=`grep rd= %s `;sed -r -i 's/rd=.*//g' %s;sed -r -i '$a\\'$s %s " % (
            write_file, write_file, write_file, write_file, write_file))
        # cmd = ("s=`grep rd= %s `;sed -r -i '$a\\'$s %s ;sed -r -i 's/rd=.*//1' %s" % (write_file, write_file, write_file))
        log.info(cmd)
        res, output = commands.getstatusoutput(cmd)
        return write_file

    def save_vdb_log(self, c_ip=None, f_name=None, out=None):
        '''
        date    :   2018-06-14
        Description :   保存vdbench的日志
        param   :  c_ip : 客户端IP  f_name : 保存的目标文件名
        return  :   None
        '''
        if None == c_ip:
            log.error("Please check your IP you input.")
            os._exit(1)
        else:
            cmd = ('ssh %s "mkdir -p /root/vdb_summary/%s"' % (c_ip, str(out)))
            log.info(cmd)
            commands.getstatusoutput(cmd)
            cmd = ('ssh %s "mkdir -p /root/vdb_summary/%s/%s"' % (c_ip, str(out), f_name))
            log.info(cmd)
            commands.getstatusoutput(cmd)
            cmd = ("ssh %s 'mv /root/output/* /root/vdb_summary/%s/%s'" % (c_ip, str(out), f_name))
            log.info(cmd)
            res, output = commands.getstatusoutput(cmd)

    def vdb_check(self, c_ip=None, time=None, oper=None, output=None):
        '''
        date    :   2018-07-03
        Description :   检查vdbench的日志是否断流
        param   :   c_ip : 客户端IP  time : 断流时间  oper ：要检查的操作，支持iops和bw两种
        return  :   None
        '''
        if None == c_ip or None == output:
            log.error("Please check your IP you input or vdbench output directory.")
            os._exit(1)
        elif None == time:
            time = 60
        elif None == oper:
            oper = "iops"
        check_str_jn = output + '_jn'
        check_str_jro = output + '_jro'
        check_str_nor = output + '_nor'
        cmd_jn = ("ssh %s '[ -e /root/output/%s_jn ]'" % (c_ip, output))
        cmd_jro = ("ssh %s '[ -e /root/output/%s_jro ]'" % (c_ip, output))
        cmd_nor = ("ssh %s '[ -e /root/output/%s_nor ]'" % (c_ip, output))
        res_jn, out_jn = commands.getstatusoutput(cmd_jn)
        res_jro, out_jn = commands.getstatusoutput(cmd_jro)
        res_nor, out_jn = commands.getstatusoutput(cmd_nor)
        if res_jn != 0 and res_jro != 0:
            output = check_str_nor
        elif res_jn == 0 and res_jro != 0:
            output = check_str_jn
        elif res_jn == 0 and res_jro == 0:
            output = check_str_jro
        elif res_nor == 0:
            output = check_str_nor
        cmd = ("ssh %s 'ls /root/output/%s | grep -E ^sd[0-9]+.html'" % (c_ip, output))
        res, all_files = commands.getstatusoutput(cmd)
        all_files = all_files.split()
        for check_file in all_files:
            log.info("Begin to check %s." % (check_file,))
            if oper == "iops":
                if oper == "iops":
                    cmd = (
                        "ssh %s \"sed -n \'/elapse/,\$p\' /root/output/%s/%s  | grep -v -E 'var|delay|skip|^$|[a-z]' | "
                        "awk '{print \$3}' | grep -v '^$'\"" % (c_ip, output, check_file))
                res, outputs = commands.getstatusoutput(cmd)
                outputs = outputs.split()
                num = 0
                error_time = []
                for iops in outputs:
                    if iops == '0.00':
                        num += 1
                    else:
                        if num != 0:
                            error_time.append(str(num) + 's')
                        num = 0
                if outputs[-1] == '0.00':
                    error_time.append(str(num) + 's')
                log.info("%s/%s break time is :%s." % (output, check_file, error_time))
        for check_file in all_files:
            if oper == "iops":
                cmd = (
                    "ssh %s \"sed -n \'/elapse/,\$p\' /root/output/%s/%s  | grep -v -E 'var|delay|skip|^$|[a-z]' | "
                    "awk '{print \$3}' | grep -v '^$' | sed ':a;N;s/\\n//g;ta' | grep '\(0.00\)\{ %s\}'\""
                    % (c_ip, output, check_file, str(time)))
            else:
                cmd = (
                    "ssh %s \"sed -n \'/elapse/,\$p\' /root/output/%s/%s  | grep -v -E 'var|delay|skip|^$|[a-z]' | "
                    "awk '{print \$4}' | grep -v '^$' | sed ':a;N;s/\\n//g;ta' | grep '\(0.00\)\{ %s\}'\""
                    % (c_ip, output, check_file, str(time)))
        #log.info(cmd)
        res, output = commands.getstatusoutput(cmd)
        if res == 0:
            log.error("WHOOL!!! I detcted vdbench disconnect exceed %s seconds on node %s." % (str(time), c_ip))
            for core_ip in deploy_ips:
                cmd = ("ssh %s 'killall -11 oSan'" % (core_ip,))
                commands.getstatusoutput(cmd)
            time.sleep(200)
        else:
            log.info(
                "Vdbench execution completed successfully, and the disconnect time is not more than %s seconds no node %s ." % (
                    str(time), c_ip))

    ################################## pscli command ######################################
    def run_cmd(self, cmd, fault_node_ip=None):
        '''
        date    :   2018-07-05
        Description :   在xstor节点执行pscli命令
        param   :   cmd : 要执行的命令   fault_node_ip : 运行节点的IP
        return  :   None
        '''
        if (fault_node_ip != None):
            node_ips_list.remove(fault_node_ip)
        for node_ip in node_ips_list:
            # 判断节点是否可以ping通
            if False == ReliableTest.check_ping(node_ip):
                continue
            run_cmd = ('ssh %s "%s"' % (node_ip, cmd))
            print run_cmd
            rc, stdout = commands.getstatusoutput(run_cmd)
            if rc == 32512:
                continue
            if (rc != 0) and ('find master error' in stdout.splitlines()[-1]):
                num = 1
                logging.warn('%s return "find master error" %d times' % (run_cmd, num))
                while True:
                    time.sleep(20)
                    num += 1
                    rc, stdout = commands.getstatusoutput(run_cmd)
                    if (rc != 0) and ('find master error' in stdout.splitlines()[-1]):
                        logging.warn('%s return "find master error" %d times' % (cmd, num))
                    else:
                        break

    def get_node_by_vip(self, vip=None):
        '''
        date    :   2018-07-05
        Description :   通过vip获取管理IP
        parm    :   vip : 虚IP
        return  :   物理节点IP
        '''
        cmd = ("ssh %s \"ip a | grep 'inet ' | awk -F '/| ' '{print \$6}'\"" % (vip))
        rc, stdout = commands.getstatusoutput(cmd)
        for ip in stdout.split('\n'):
            if ip in node_ips_list:
                return ip

    def get_same_jnl_group(self, node_id):
        '''
        date    :   2018-07-05
        Description :   通过vip获取同组日志节点
        parm    :   vip : 虚IP
        return  :   同组日志节点ID
        '''
        # cmd = (
        #     "ssh %s \"/home/parastor/tools/nWatch -i %s -t oRole -c oRole#rolemgr_view_dump | grep -A 20 'grpview info' | grep node_id | grep 'node_stat: 0'| awk -F ' |,' '{print \$6}' | sort |uniq\"" % (
        #         node_ips_list[0], str(node_id)))
        # rc, stdout = commands.getstatusoutput(cmd)
        cmd = (
                "/home/parastor/tools/nWatch -i %s -t oRole -c oRole#rolemgr_view_dump | grep -A 20 'grpview info' | grep node_id | grep 'node_stat: 0'| awk -F ' |,' '{print \$6}' | sort |uniq"
                % (str(node_id)))
        log.info(cmd)
        rc, stdout = self.run_pscli_cmd(pscli_cmd=cmd)
        gids = stdout.split('\n')
        if 0 in gids:
            gids.remove(0)
        gids = map(int, gids)
        return gids

    def get_jnl_node_id(self):
        """
        :Usage:获取日志节点列表
        :return:list,日志节点列表
        """
        jnl_node_ids = []
        node_ids = self.get_nodes(s_ip=deploy_ips[1])
        for id in node_ids:
            cmd = ("ssh %s ' pscli --command=get_nodes --ids=%s'" % (deploy_ips[1], str(id)))
            log.info(cmd)
            res, output = commands.getstatusoutput(cmd)
            log.info(output)
            if res != 0:
                log.error("Get node info failed.")
                os._exit(1)
            else:
                if "SHARED" not in output:
                    continue
                else:
                    jnl_node_ids.append(id)
        return jnl_node_ids

    def run_pscli_cmd(self, pscli_cmd=None, time_out=120, s_ip=None, times=5):
        '''
        :Author:Diws
        :param cmd:
        :return:
        '''
        if pscli_cmd == None:
            log.error("Sorry, please input a command to run.")
            os._exit(1)
        if s_ip != None and (True is ReliableTest.check_ping(s_ip)):
            ssh_cmd = ("timeout %d ssh root@" % (time_out))
            cmd = ("%s%s \"%s\"" % (ssh_cmd, s_ip, pscli_cmd))
            log.info(cmd)
            for i in range(times):
                res, output = commands.getstatusoutput(cmd)
                if res == 0:
                    return res, output
                else:
                    log.error("node %s Try sending %s commands and wait %s at a time" % (s_ip, times, time_out))
        else:
            ssh_cmd = ("timeout %d ssh root@" % (time_out,))
            for d_ip in deploy_ips:
                if False is ReliableTest.check_ping(d_ip):
                    continue
                else:
                    cmd = ("%s%s \"%s\"" % (ssh_cmd, d_ip, pscli_cmd))
                    for i in range(times):
                        res, output = commands.getstatusoutput(cmd)
                        if res == 0:
                            return res, output
                        log.error("node %s Try sending %s commands and wait %s at a time" % (d_ip, times, time_out))
        return res, output

    def get_node_pool_id_name(self):
        """
        :Author:Diws
        :Date:20181207
        :Description:Get the id and name of the node pool
        :return:
        """
        node_pool_info = {}
        cmd = ("pscli --command=get_node_pools")
        res, output = self.run_pscli_cmd(pscli_cmd=cmd)
        output = json.loads(output)
        nodepools = output['result']['node_pools']
        for nodepool in nodepools:
            node_pool_info[nodepool['id']] = nodepool['name']
        return node_pool_info

    def init_win_log(self, case_sn=None):
        if windows_tag == 0:
            vdb_test.run_keyword('init_log', kwargs={'case_sn': case_sn})
            return 0
        else:
            return None

    def gen_win_vdb_conf(self, range_size='(100M,200M)', maxdata='2G', xfersize='(4k,100)',
                         seekpct=0, rdpct=0, iorate=120, threads=8, run_time=900, offset='', align=''):
        if windows_tag == 0:
            vdb_conf = vdb_test.run_keyword('gen_vdb_conf',
                                            kwargs={'range_size': range_size, 'maxdata': maxdata, 'xfersize': xfersize,
                                                    'seekpct': str(seekpct), 'rdpct': str(rdpct), 'iorate': str(iorate),
                                                    'threads': str(threads),
                                                    'run_time': str(run_time), 'offset': str(offset),
                                                    'align': str(align)})
            return vdb_conf
        else:
            return None

    def run_win_vdb(self, case_sn=None, vdb_conf=None, jn_jro=None, time=None):
        if windows_tag == 0:
            if None == case_sn:
                case_sn = 'UNKOWN'
            rc = vdb_test.run_keyword('run_vdb',
                                      kwargs={'case_sn': case_sn, 'vdb_conf': vdb_conf, 'jn_jro': jn_jro,
                                              'time': str(time)})
            log.info("rc的值为%s" % str(rc))
            if 0 == rc:
                log.info("run vdbench in windows host successful!!!")
                return 0
            else:
                log.info("run vdbench in windows host failed!!!")
                os._exit(1)
        else:
            return None

    def kill_win_vdb(self):
        if windows_tag == 0:
            rc = vdb_test.run_keyword('kill_win_vdb')
            if 0 == rc:
                log.info("kill vdbench process in windows host successful!")
                return 0
        else:
            return None

    def upload_vdb_output(self, log_host_ip, vdb_dir):
        if windows_tag == 0:
            vdb_test.run_keyword('upload_vdb_output', kwargs={'log_host_ip': log_host_ip, 'vdb_dir': vdb_dir})
        else:
            return None


if __name__ == '__main__':
    print oSan().get_nodes()
# -*- encoding=utf8 -*-
# @Time: 2018-08-01
# @Author: liuhe
# description:case使用到的公共函数

import os
import re
import sys
import time
import inspect
import random
import xml
import utils_path
import Lun_managerTest
import common
import common2
import commands
import breakdown
import prepare_clean
import log
import json
import prepare_x1000
# import prepare_clean
# import prepare_x1000
import get_config

import decorator_func
import ReliableTest

# import access_env
conf_file = get_config.CONFIG_FILE
deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP
new_ips = get_config.get_expand_ip_info()

# 类实例化
osan = Lun_managerTest.oSan()
com_lh = breakdown.Os_Reliable()
com_disk = common.Disk()
node = common.Node()
com2_osan = common2.oSan()
com_bd_disk = breakdown.disk()

# 读取系统vip和svip
svip = get_config.get_svip(conf_file)
vips = get_config.get_vip(conf_file)
pre_lun_num = 50  # xStor 运行caase前在测试环境中预先配置lun和lun map数量，虚拟机要注意容量和个数比例


def get_inter_ids():
    """
    :Auter: Liuhe
    :Description: 从节点中随机获取业务节点和非业务节点，若没有非业务节点从业务节点随机一个，前提异配置vip和svip才能使用
    :return: IP的列表，前半部分为业务节点后半部分为非业务节点
    """
    node_ip_list = []
    vip_pool = com2_osan.get_vip_address_pools(deploy_ips[0], "1")
    vip_list = com2_osan.analysis_vip(vip_pool[0])
    inter_ids = com_bd_disk.get_interface_node(vip_list)
    all_nodes_ids = com2_osan.get_nodes(deploy_ips[0])
    node_no_inter_ids = list(set(all_nodes_ids).difference(set(inter_ids)))
    if len(node_no_inter_ids) == 0:
        node_ips = get_config.get_env_ip_info(conf_file)
        return node_ips
    else:
        for i in inter_ids:
            inter_ip = deploy_ips[i - 1]
            node_ip_list.append(inter_ip)
        for i in node_no_inter_ids:
            no_inter_ip = deploy_ips[i - 1]
            node_ip_list.append(no_inter_ip)
        return node_ip_list


def get_current_function_name():
    """
    :return: 返回当前运行函数的函数名称
    """
    return inspect.stack()[1][3]


def create_access(ips=deploy_ips[0], node_ids=None, access_name="accesszone1"):
    if node_ids is None:
        node_ids_list = com2_osan.get_nodes(s_ip=ips)
        node_ids = ",".join("%s" % id for id in node_ids_list)
    log.info("from the node %s create access zone，add the access zone ID：%s ，the access zone name：%s" % (
        ips, node_ids, access_name))
    az_id = com2_osan.create_access_zone(s_ip=ips, node_id=node_ids, name=access_name)
    log.info("create access zone ID: %s" % (az_id))
    return az_id


def create_subnet(s_ip=deploy_ips[0], svip=svip[0], a_z_id=None, access_name="subnet1"):
    if a_z_id is None:
        a_z_id = osan.get_access_zone_id(s_ip)[0]
    log.info("Return by function \"create_subnet\" :from the node %s create SVIP" % (s_ip))
    sub_id = com2_osan.create_subnet(s_ip=s_ip, sv_ip=svip, access_zone_id=a_z_id, name=access_name)
    log.info("create SVIP success ID:%s" % (sub_id))
    return sub_id


def create_vip(s_ip=deploy_ips[0], subnet_id=None, vip_name="vip1.com", vip_pool=vips[0]):
    if subnet_id is None:
        subnet_id = osan.get_subnet_id(s_ip=deploy_ips[0])[0]
    log.info("create_vip :创建VIP %s，在节点 %s ,加入SVIP的ID号为：%s" % (vip_pool, s_ip, subnet_id))
    id = com2_osan.add_vip_address_pool(s_ip=s_ip, subnet_id=subnet_id, domain_name=vip_name, vip_addresses=vip_pool,
                                        rebalance_policy='RB_AUTOMATIC')
    return id


def enable_san(s_ip=deploy_ips[0]):
    az_id = osan.get_access_zone_id(s_ip)
    for id in az_id:
        log.info("从节点 %s 上，使能访问区%s的SAN协议" % (deploy_ips[0], id))
        osan.enable_san(s_ip=s_ip, access_zone_id=id)


def create_host_group(s_ip=deploy_ips[0]):
    log.info("从节点%s 上创建主机组" % (s_ip))
    osan.create_host_group(s_ip=s_ip, hg_name="hg_1")


def create_host(ips=deploy_ips[0]):
    hostg_id = osan.get_host_groups(s_ip=ips)
    log.info("从节点%s 上，将主机加入到主机组%s" % (ips, hostg_id[0]))
    osan.add_host(s_ip=ips, h_name="h_1", hg_id=hostg_id[0])


def create_add_initiator():
    host_ids = osan.get_hosts(deploy_ips[0])
    log.info("从节点 %s 上配置主机%s 的启动器" % (deploy_ips[0], host_ids[0]))
    osan.add_initiator(s_ip=deploy_ips[0], h_id=host_ids[0], iqn="iqn.1990-21.com.sugon", alias="sugon1990.initiator")


def create_lun(ips=deploy_ips[0], name="LUN1", size=None, type=None, access_id=None):
    s_pool_id = osan.get_storage_id(ips)
    data_pool_size = com_lh.get_storage_pool_size(id=s_pool_id[1])
    if access_id == None:
        log.info("the lun will assigned to the first access zone")
        access_id = osan.get_access_zone_id(ips)[0]
    if type == None:
        type_list = ["THIN", "THICK"]
        set_type = random.choice(type_list)
    else:
        set_type = type
    if size == None:
        cmd = ("ssh %s \" dmidecode -s system-product-name\"" % (ips))
        rc, stdout = commands.getstatusoutput(cmd)
        if "VMware" in stdout:
            if set_type == "THICK":
                set_size = 1073741824  # 虚拟机创建默认创建1G
            else:
                set_size = int(data_pool_size)
        else:
            if set_type == "THICK":
                set_size = 10737418240	  # 物理机创建默认创建10G
            else:
                set_size = int(data_pool_size)
    else:
        set_size = size
    log.info("In node %s,from the storage pool %s create %s lun %s assigned to %s access zone" % (
        ips, s_pool_id[1], type, name, access_id))
    lun_id = osan.create_lun(s_ip=ips, total_bytes=set_size, lun_type=set_type, lun_name=name,
                             stor_pool_id=s_pool_id[1],
                             acc_zone_id=access_id, max_throughput="0", max_iops="0")
    log.info("create LUN ID: %s success, will get lun name to check lun info!!!" % (lun_id))
    lun_name = osan.get_option_single(s_ip=ips, command="get_luns", indexname="luns", argv2="name", ids="ids",
                                      argv1=lun_id)
    if lun_name == name:
        log.info("Successfully create a lun with the name %s" % (lun_name))
        return lun_id
    else:
        log.error(
            "Create LUN failed. Error Info : \nGet LUN info node : %s \nget lun_name : %s \nWill except lun name : %s " % (
                ips, lun_name, name))
        os._exit(1)


def create_luns(s_ip=deploy_ips[0], nums=None, size=None, type=None, access_id=None):
    if nums == None:
        nums = random.randint(10, 30)
    log.info("will create numbers of lun:%s" % (nums))
    lun_names = com_lh.get_lun_name()
    if len(lun_names) >= pre_lun_num:  # 查看当前lun 名称数量，如果当前环境lun数量小于预设值，就用大写LUN
        name_type = "LUN"
    else:  # 当前环境lun 数量值小于预设值说明需要添加预设lun 使用小写lun
        name_type = "lun"
    log.info("get lun name numbers:%s ,will use name:%s" % (len(lun_names), name_type))
    for i in range(1, nums + 1):  # lun 名称编号，都从小到大排，用大小写区分是预设的还是已有的
        lun_name = name_type + str(i)
        create_lun(s_ip, lun_name, size=size, type=type, access_id=access_id)


def create_lun_map(ips=deploy_ips[0], lun_id=None, target_id=None):
    log.info("will create lun map")
    map_ids = []
    host_group_id = osan.get_host_groups(s_ip=ips)
    if lun_id is None:
        lun_ids = com_lh.get_unmap_lun(s_ip=ips)  # 默认没有lun map的都拿出来
        log.info("get unmap number of %s" % (lun_ids))
        log.info("Get Info:\nGet unmap lun ids:%s \nGet host_group_id:%s" % (lun_ids, host_group_id))
        if lun_ids:
            for id in lun_ids:
                log.info("in the node %s make the lun ID %s be aassigned to %s" % (ips, id, host_group_id[0]))
                map_id = osan.map_lun(s_ip=ips, lun_ids=id, hg_id=host_group_id[0], target_id=target_id)
                map_ids.append(map_id)
            log.info("create lun map finished")
            return map_ids
        else:
            log.info("get lun list is None")
    else:
        log.info("Get Info:\nGet unmap lun ids:%s \nGet host_group_id:%s" % (lun_id, host_group_id))
        map_id = osan.map_lun(s_ip=ips, lun_ids=lun_id, hg_id=host_group_id[0], target_id=target_id)
        log.info("create lun map finished")
        return map_id


def create_iscsi_login(cli_ips=client_ips[0]):
    """
    2018-10
    :param cli_ips: 主机管理IP
    :return: 无
    """
    target_list = osan.discover_scsi_list(client_ip=cli_ips, svip=svip[0])  # 从主机端拿到iqn
    log.info("Get Info:\nSvip list:%s \nTarget list:%s" % (svip[0], target_list))
    for tag in target_list:
        log.info("主机发现存储target：%s,主机 %s 将进行SCSI登录" % (tag, cli_ips))
        osan.iscsi_login(client_ip=cli_ips, iqn=tag)


def update_access(ips=deploy_ips[0], id_list='1,2,3'):
    log.info("update access")
    azs = osan.get_access_zone_id(s_ip=ips)
    log.info("获取当前访问区列表 ：%s , 将访问区%s 节点列表修改为 %s " % (azs, azs[0], id_list))
    rc = osan.update_access_zone(s_ip=ips, node_ids=id_list, access_zone_id=azs[0])
    return rc


def update_luns(s_ip=deploy_ips[0], id=None, size=None):
    """
    修改lun 名称修改为UPLUN+id号，size修改为原容量的2倍
    :param s_ip:
    :id: 制定ID进行扩容
    :size: 制定扩容大小
    :return:
    """
    log.info("from update_luns: will update luns")
    lun_ids = osan.get_lun(s_ip=s_ip)
    up_lun_ids = lun_ids[pre_lun_num:]
    lun_sizes = com_lh.get_lun_size_dict()
    if id:
        if id not in up_lun_ids:
            log.info("get the lun id %s is not new lun id, will pass" % (id))
            return
        elif id not in lun_ids:
            log.info("LUN id %s error" % (id))
    if type(size) == int or type(size) == str or size is None:
        log.info("check lun type of size is legal")
    else:
        log.info("lun size parameters are not legal. Error info:%s" % (type(size)))
    if id is None:
        if size is None:
            for i in up_lun_ids:
                lun_name = "UPLUN" + str(i)
                lun_size = int(lun_sizes[i] * 2)
                log.info("lun name up to %s , total_bytes from %s to %s" % (lun_name, lun_sizes[i], lun_size))
                osan.update_lun(s_ip=s_ip, lun_id=i, lun_name=lun_name, total_bytes=lun_size)
        else:
            if type(id) == list:
                up_lun_ids = id
            else:
                up_lun_ids = [id]
            for i in up_lun_ids:
                lun_name = "UPLUN" + str(i)
                lun_size = int(size * 2)
                log.info("lun name up to %s , total_bytes form %s to %s" % (lun_name, lun_sizes[i], lun_size))
                osan.update_lun(s_ip=s_ip, lun_id=i, lun_name=lun_name, total_bytes=lun_size)
    else:
        if size is None:
            if type(id) == list:
                up_lun_ids = id
            else:
                up_lun_ids = [id]
            for i in up_lun_ids:
                lun_name = "UPLUN" + str(i)
                lun_size = int(lun_sizes[i] * 2)
                log.info("lun name up to %s , total_bytes from %s to %s" % (lun_name, lun_sizes[i], lun_size))
                osan.update_lun(s_ip=s_ip, lun_id=i, lun_name=lun_name, total_bytes=lun_size)
        else:
            if type(id) == list:
                up_lun_ids = id
            else:
                up_lun_ids = [id]
            for i in up_lun_ids:
                lun_name = "UPLUN" + str(i)
                lun_size = int(size * 2)
                log.info("lun name up to %s , total_bytes from %s to %s" % (lun_name, lun_sizes[i], lun_size))
                osan.update_lun(s_ip=s_ip, lun_id=i, lun_name=lun_name, total_bytes=lun_size)
    return id


def clean_lun_map(ips=deploy_ips[0]):
    """
    2018-09
    :param ips: 节点IP，默认为第一个节点，忽略预设的lun map
    :return: 无
    """
    fun_name = get_current_function_name()
    lun_map_ids = osan.get_lun_maps(ips)
    del_map_ids = lun_map_ids[pre_lun_num:]
    log.info("LUN map will be cleaned up. be cleaned lun map ID is %s" % (del_map_ids))
    for lun_map_id in del_map_ids:
        log.info("Return by function %s :在节点 %s 删除LUN MAP ，映射ID: %s" % (fun_name, ips, lun_map_id))
        osan.delete_lun_map(s_ip=ips, map_id=lun_map_id)
    log.info("from clean_lun_map. clean lun map finished")


def clean_node_pools():
    node_pool_ids = osan.get_option(s_ip=deploy_ips[0], command="get_node_pools", indexname="node_pools", argv="id")
    log.info(node_pool_ids)
    for node_pool_id in node_pool_ids:
        osan.delete_node_pools(s_ip=deploy_ips[0], node_pool_id=node_pool_id)


def clean_lun(ips=deploy_ips[0]):
    """
    删除lun ，忽略预设的lun
    :param ips:节点IP
    :return:
    """

    fun_name = get_current_function_name()
    lun_ids = osan.get_lun(s_ip=ips)
    del_lun_ids = lun_ids[pre_lun_num:]
    log.info("Get Info:\nGet lun ids:%s" % (del_lun_ids))
    if len(del_lun_ids) is None:
        log.error("Do not find the system luns, lun_ids is None")
    else:
        for lun_id in del_lun_ids:
            log.info("Return by function %s :Remove the lun: %s from node:%s" % (fun_name, lun_id, ips))
            osan.delete_lun(s_ip=ips, lun_id=lun_id)


def clean_initiator():
    log.info("clean test enviroment")
    lun_map_ids = osan.get_lun_maps(deploy_ips[0])
    log.info("LUN map will be cleaned up. be cleaned lun map ID is %s" % (lun_map_ids))
    for lun_map_id in lun_map_ids:
        log.info("在节点 %s 删除LUN MAP ，映射ID: %s" % (deploy_ips[0], lun_map_id))
        osan.delete_lun_map(s_ip=deploy_ips[0], map_id=lun_map_id)
    lun_ids = osan.get_lun(s_ip=deploy_ips[0])
    log.info("Get Info:\nGet lun ids:%s , need delete after create new lun %s" % (lun_ids, pre_lun_num))
    for lun_id in lun_ids:
        log.info("Remove the lun: %s from node:%s" % (lun_id, deploy_ips[0]))
        osan.delete_lun(s_ip=deploy_ips[0], lun_id=lun_id)
    log.info("clean environment finished")
    ini_ids = osan.get_initiators(s_ip=deploy_ips[0])
    log.info("Get initiator ids:%s" % (ini_ids))
    for ini_id in ini_ids:
        log.info("在节点 %s 删除启动器 %s" % (deploy_ips[0], ini_ids))
        osan.remove_initiator(s_ip=deploy_ips[0], ini_id=ini_id)


def clean_host():
    host_ids = osan.get_hosts(s_ip=deploy_ips[0])
    log.info("get host id:%s" % (host_ids))
    for host_id in host_ids:
        log.info("在节点 %s 删除逻辑卷 %s" % (deploy_ips[0], host_id))
        osan.remove_hosts(s_ip=deploy_ips[0], id=host_id)


def clean_hostgroup(s_ip=deploy_ips[0]):
    hostgroup_ids = osan.get_host_groups(s_ip=s_ip)
    log.info("get host group :%s" % (hostgroup_ids))
    for hostgroup_id in hostgroup_ids:
        log.info("the host group %s will be clean, from %s" % (hostgroup_id, s_ip))
        osan.delete_host_groups(s_ip=s_ip, id=hostgroup_id)


def clean_vip_address_pool(s_ip=deploy_ips[0]):
    vip_pool_ids = com2_osan.get_vip_address_pools_id(s_ip=s_ip)
    log.info("get vip pool：%s " % (vip_pool_ids))
    for vip_pool_id in vip_pool_ids:
        log.info("the vip pool %s will be clean, from %s" % (vip_pool_id, s_ip))
        osan.delete_vip_address_pool(s_ip=s_ip, id=vip_pool_id)


def clean_subnet(s_ip=deploy_ips[0]):
    subnet_ids = osan.get_subnet_id(s_ip=s_ip)
    log.info("get SVIP:%s" % (subnet_ids))
    for subnet_id in subnet_ids:
        log.info("the vip %s will be clean, from %s" % (subnet_id, s_ip))
        osan.delete_subnet(s_ip=s_ip, id=subnet_id)


def clean_access_zone(ips=deploy_ips[0]):
    azs = osan.get_access_zone_id(s_ip=ips)
    log.info("get access zone:%s" % (azs))
    for az in azs:
        log.info("the access zone %s will be clean, from %s" % (az, ips))
        osan.delete_access_zone(s_ip=ips, azid=az)


def clean_storage_pool(ips=deploy_ips[0]):
    sto_pool_ids = osan.get_storage_id(s_ip=ips)
    log.info("get storage pool:%s" % (sto_pool_ids))
    for sto_pool_id in sto_pool_ids:
        log.info("the storage pool %s will be clean, from %s" % (sto_pool_id, ips))
        osan.delete_storage_pool(s_ip=ips, id=sto_pool_id)


def down_network(ipaddr, name):
    if type(name) == list:
        for eth in name:
            log.info("关闭节点 %s 网卡 %s " % (ipaddr, eth))
            com_lh.network_test(s_ip=ipaddr, net_name=eth, net_stat="down")
    if type(name) == str:
        log.info("关闭节点 %s 网卡 %s " % (ipaddr, name))
        com_lh.network_test(s_ip=ipaddr, net_name=name, net_stat="down")
    time.sleep(5)


def up_network(ipaddr, name):
    if type(name) == list:
        for eth in name:
            log.info("开启节点 %s 网卡 %s " % (ipaddr, eth))
            com_lh.network_test(s_ip=ipaddr, net_name=eth, net_stat="up")
    if type(name) == str:
        log.info("开启节点 %s 网卡 %s " % (ipaddr, name))
        com_lh.network_test(s_ip=ipaddr, net_name=name, net_stat="up")
    time.sleep(5)


def disable_san(s_ip=deploy_ips[0]):
    ids = com2_osan.get_access_zone_id(s_ip)
    for id in ids:
        log.info("access zone id:%(zone_id)s will disable san from %(send_ip)s" % {"zone_id": id, "send_ip": s_ip})
        osan.disable_san(s_ip=s_ip, access_zone_id=id, protocol_types="ISCSI", stop_server="true", force="true")


def get_svip(s_ip=None):
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
        cmd = ("ssh %s \"pscli --command=get_subnets\"" % (s_ip))
        (res, final) = commands.getstatusoutput(cmd)
        if res != 0:
            log.error("Get_subnets cmd:%s error info:%s" % (cmd, final))
            os._exit(1)
        else:
            log.info("Get_subnets success.")
        final = json.loads(final)
        svip_list_info = final['result']["subnets"]
        if svip_list_info:
            finals = final['result']['subnets']
            for vip in finals:
                vip_list.append(vip['svip'])
            return vip_list
        else:
            log.info("get svip is none")
            return


def get_vip_address_pools(s_ip=None):
    '''
    date    :   2018-05-15
    Description :   获取VIP
    param   :   s_ip : iscsi服务端IP;n_id : 节点ID
    return  :   VIP
    '''
    vip_list = []
    if None == s_ip:
        log.error("Got wrong server_ip: %s" % (s_ip))
        os._exit(1)
    else:
        cmd = ("ssh %s \"pscli --command=get_vip_address_pools\"" % (s_ip))
        (res, final) = commands.getstatusoutput(cmd)
        log.info(cmd)
        if res != 0:
            log.error("Get_vip_address_pools error.info:%s" % (final))
            os._exit(1)
        else:
            log.info("Get_vip_address_pools success.")
            final = json.loads(final)
            vip_list_info = final["result"]["ip_address_pools"]
            if vip_list_info:
                finals = final['result']['ip_address_pools']
                for vip in finals:
                    vip_list.append(vip['vip_addresses'])
                return vip_list
            else:
                log.info("get vip is none")
                return


def check_eth():
    """
    :Auther: Liu he
    :Description: 轮训检查各个节点数据管理网IP状态
    :return: 若节点管理IP异常直接退出，节点数据业务网异常尝试ifup拉起，若拉起失败返回失败
    """
    fun_name = get_current_function_name()
    node_ids = osan.get_nodes(s_ip=deploy_ips[0])
    for id in node_ids:
        ip = node.get_node_ip_by_id(id)
        eth_list = com_lh.get_eth_name(ip) + com_lh.get_vip_eth_name(ip)
        log.info("Return by function %s :Find The node %s have eth name list %s" % (fun_name, ip, eth_list))
        for eth in eth_list:
            cmd = ("ssh %s \"ethtool %s | grep \"Link\" \" " % (ip, eth))
            rc, stdout = commands.getstatusoutput(cmd)
            if rc != 0:
                log.info("Return by function %s :%s node not find %s" % (fun_name, ip, eth))
                os._exit(1)
            else:
                eth_link_status = stdout.split(":")[1].strip()
            if eth_link_status == "yes":
                log.info("Return by function %s :network %s link status is %s" % (fun_name, eth, eth_link_status))
            else:
                log.info("will try up %s" % (eth))
                cmd = ("ssh %s \" ifup %s\"" % (ip, eth))
                rc, stdout = commands.getstatusoutput(cmd)
                if rc != 0:
                    log.info("ifup eth %s fail" % (eth))
                else:
                    cmd2 = ("ssh %s \"ethtool %s | grep \"Link\" \" " % (ip, eth))
                    rc2, stdout2 = commands.getstatusoutput(cmd2)
                    re_eth_link_status = stdout2.split(":")[1].strip()
                    if re_eth_link_status == "yes":
                        log.info("try up eth %s success" % (eth))
                    else:
                        log.info("try up eth %s fail" % (eth))
                        os._exit(1)


def check_disk(d_except=None):
    """
    :Auther: Liu He
    :Description: 检查集群内各个节点硬盘数量，
    :param d_except: 默认磁盘数量，若设置值将把实际值和期望值进行对比，不填不进行对比
    :return: 返回各个节点硬盘数量和磁盘列表，若设置期望值会进行期望值与实际值对比
    """
    log.info("进行网卡和硬盘检查")
    len_disk_list = 0
    for ip in deploy_ips:
        disk_lists = []
        cmd = ("ssh %s \"lsscsi |grep \"\/dev\/sd\"\"" % (ip))
        rc, stdout = commands.getstatusoutput(cmd)
        if rc != 0:
            log.error("send cmd：%s failed,rc: %s" % (cmd, stdout))
            os._exit(1)
        else:
            disks = stdout.split("\n")
            for disk_info in disks:
                disk = disk_info.strip().split(" ")[-1]
                disk_lists.append(disk)
            len_disk_list = len(disk_lists)
            log.info("%s server have %s  HDD : %s" % (ip, len_disk_list, disk_lists))
    if d_except is not None:
        if d_except == len_disk_list:
            log.info("The system  disk numbers :%s ,meet requirement" % (len_disk_list))
        else:
            disk_numbers = d_except - len_disk_list
            log.error("The system lose disk numbers: %s, please check it" % (disk_numbers))
            exit(1)
    return len_disk_list


def check_vip_status():
    """
    :Auther: Liu he
    :Description: 从xml文件中拿到vip地址，逐个ping，发现不通尝试3次后仍然不通，判定vip丢失。case退出
    :return:
    """
    svip_list = get_svip(s_ip=deploy_ips[0])
    if svip_list == svip:  # 对比获取到的vip svip与配置中是否相同，不相同进行update
        log.info("get svip is setting svip")
    else:
        subnet_id = osan.get_subnet_id(deploy_ips[0])
        cmd = ("ssh %s \"pscli --command=update_subnet --id=%s --svip=%s --subnet_mask=%s\"" % (
            deploy_ips[0], subnet_id, svip[0], "255.255.255.0"))
        commands.getstatusoutput(cmd)
    get_vips = com_lh.get_all_vip_address()
    if vips == get_vips:
        log.info("get vip is setting vip")
    else:
        vip_pool_id = com2_osan.get_vip_address_pools_id(deploy_ips[0])
        osan.update_vip_address_pool(vip_id=vip_pool_id[0], s_ip=deploy_ips[0], vip_addresses=vips[0])
    lose_vip = []
    get_vip = []
    vip_list = com2_osan.analysis_vip(vips)
    log.info("from the host to check vip status.\nwill check vip list:%s" % vip_list)
    for ip in vip_list:
        for i in range(5):
            cmd = "ssh %s \"ping -c 2 %s\"" % (client_ips[0], ip)
            (res, output) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error("Can not attach %s, waiting 60s to try again." % (ip))
                time.sleep(60)
            else:
                log.info("The vip : %s is ok" % (ip))
                get_vip.append(ip)
                break
            if res != 0 and i == 5:
                log.info(cmd)
                log.error("try to 3th waiting 180s found VIP:%s can not attach, will exit" % (ip))
                lose_vip.append(ip)
    if len(lose_vip) == 0:
        log.info("have find vip:%s" % (get_vip))
        return
    else:
        log.error("find lost vip:%s" % (lose_vip))
        log.error("have find vip:%s" % (get_vip))
        os._exit(1)


def check_new_vip_status(new_vips_list):
    """
    :Auther: Liu he
    :Description: 从xml文件中拿到vip地址，逐个ping，发现不通尝试3次后仍然不通，判定vip丢失。case退出
    :return:
    """
    vips = com_lh.get_all_vip_address()
    lose_vip = []
    get_vip = []
    log.info("from the host to check vip status.\nwill check vip list:%s" % new_vips_list)
    for ip in new_vips_list:
        for i in range(3):
            cmd = "ssh %s \"ping -c 2 %s\"" % (client_ips[0], ip)
            (res, output) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error("Can not attach %s, waiting 60s to try again." % (ip))
                time.sleep(60)
            else:
                log.info("The vip : %s is ok" % (ip))
                get_vip.append(ip)
                break
            if res != 0 and i == 2:
                log.error("try to 3th waiting 180s found VIP:%s can not attach, will exit" % (ip))
                lose_vip.append(ip)
    if len(lose_vip) == 0:
        log.info("have find vip:%s" % (get_vip))
        return
    else:
        log.error("find lost vip:%s" % (lose_vip))
        log.error("have find vip:%s" % (get_vip))
        os._exit(1)


def check_san_enable_env():
    """
    :Auther: Liu he
    :Description:检查enable测试环境lun map，lun，initiator,host group,host,发现后删除
    :return:
    """
    lun_map_ids = osan.get_lun_maps(deploy_ips[0])
    if lun_map_ids:
        log.info("The system have lun maping ,will clean up")
        for lun_map_id in lun_map_ids:
            osan.delete_lun_map(s_ip=deploy_ips[0], map_id=lun_map_id)
    else:
        log.info("The system have not lun maping")
    log.info("will check lun ,if found it, clean up")
    lun_ids = osan.get_lun(s_ip=deploy_ips[0])
    if lun_ids:
        log.info("The system have lun, will clean")
        for lun_id in lun_ids:
            rc = osan.delete_lun(s_ip=deploy_ips[0], lun_id=lun_id)
            if rc is not None:
                exit(1)
    else:
        log.info("The system have not lun ")
    ini_ids = osan.get_initiators(s_ip=deploy_ips[0])
    if ini_ids:
        log.info("The system have initiator: %s, will clean" % (ini_ids))
        for ini_id in ini_ids:
            osan.remove_initiator(s_ip=deploy_ips[0], ini_id=ini_id)
    host_ids = osan.get_hosts(s_ip=deploy_ips[0])
    if host_ids:
        log.info("The system have host: %s, will clean" % (host_ids))
        for host_id in host_ids:
            osan.remove_hosts(deploy_ips[0], host_id)
    hostgroup_ids = osan.get_host_groups(s_ip=deploy_ips[0])
    if hostgroup_ids:
        log.info("The system have host group: %s, will clean" % (hostgroup_ids))
        for hostgroup_id in hostgroup_ids:
            osan.delete_host_groups(deploy_ips[0], hostgroup_id)


def check_lun_env():
    """
    :auther: Liuhe
    :Description:检查lun测试环境，hostgroup，host，initiator。存在跳过，不存在创建
    :return:
    """
    access_ids = com2_osan.get_access_zone_id(deploy_ips[0])
    if access_ids:
        log.info("The envireonment have access:%s" % (access_ids))
    else:
        log.info("The envireonment have not access, will create")
        create_access()
    svip_ips = get_svip(deploy_ips[0])
    if svip_ips:
        log.info("The envireonment have SVIP:%s" % (svip_ips))
    else:
        log.info("The environment have not SVIP, will create")
        create_subnet()
    vip_ids = get_vip_address_pools(deploy_ips[0])
    if vip_ids:
        log.info("The envireonment have vip pool:%s" % (vips))
    else:
        log.info("The environment have not vip pool, will create")
        create_vip()
    san_status = com_lh.get_san_state(deploy_ips[0])
    if san_status:
        if all(san_status) is True:
            log.info("check san is active,san status:%s" % (san_status))
        else:
            log.info("check san status is inactive, will enable san.info status: %s" % (san_status))
            enable_san()
    else:
        log.info("check san status is inactive, will enable san")
        enable_san()
    hostgroup_ids = osan.get_host_groups(s_ip=deploy_ips[0])
    if hostgroup_ids:
        log.info("get hostgroup :%s" % (hostgroup_ids))
    else:
        log.info("xstor will create host group")
        create_host_group()
    host_ids = osan.get_hosts(s_ip=deploy_ips[0])
    if host_ids:
        log.info("get xstor host : %s " % (host_ids))
    else:
        log.info("xstor will create host")
        create_host()
    ini_ids = osan.get_initiators(s_ip=deploy_ips[0])
    if ini_ids:
        log.info("get xstor initiators: %s " % (ini_ids))
    else:
        log.info("xstor will create initiators")
        create_add_initiator()


def check_add_node_xml(new_ip, node_ip):
    cmd1 = ("ssh %s \"cat /home/deploy/deploy_config_1.xml\"" % (node_ip))
    re, output = commands.getstatusoutput(cmd1)
    if re != 0:
        log.info("Get new Node config.xml ,will send a file to %s" % (node_ip))
        cmd = ("scp /home/deploy/deploy_config_1.xml %s:/home/deploy/" % (node_ip))
        rc, final = commands.getstatusoutput(cmd)
        log.info(cmd)
        if rc != 0:
            log.error("scp xml file failed:%s, will skip" % (final))
            os._exit(-1)
        log.info("check again")
        cmd = ("ssh %s \"cat /home/deploy/deploy_config_1.xml\"" % (node_ip))
        re, output = commands.getstatusoutput(cmd)
        if re != 0:
            log.info("check xml failed, will skip")
            os._exit(-1)
        else:
            log.info("xml file send success, will check it")
    cmd2 = ("ssh %s \"cat /home/deploy/deploy_config_1.xml |grep \<ip\> |head -1\"" % (node_ip))
    re, final = commands.getstatusoutput(cmd2)
    if re != 0:
        log.error("get manage ip failed re:%s,info:%s" % (re, final))
        os._exit(1)
    else:
        # 拿到的xml里的IP，不一定就是对的
        c_ip = final.strip(" ").split(">")[1].split("<")[0]
        if new_ip == c_ip:
            log.info("check new node IP success:%s" % (c_ip))
            return
        else:
            log.info("check new node IP not right, will change")
            new_ip = new_ip.split(".")[-1]
            cli_ip = c_ip.split(".")[-1]
            cmd = ("ssh %s \"sed -i 's/%s/%s/g' /home/deploy/deploy_config_1.xml \"" % (node_ip, cli_ip, new_ip))
            commands.getstatusoutput(cmd)
            log.info(cmd)
            return


def check_host():
    """
    :Auther: Liu he
    :description: 检查主机端session，发现有残留session会删除
    :param c_ip: 主机端IP
    :return:
    """
    for ip in client_ips:
        cmd = ("ssh %s \"iscsiadm -m node\"" % (ip))
        rc, stdout = commands.getstatusoutput(cmd)
        cmd2 = ("ssh %s \"iscsiadm -m session\"" % (ip))
        rc2, stdout = commands.getstatusoutput(cmd2)
        if rc == 0 or rc2 == 0:
            osan.iscsi_logout_all(ip)
            log.info("The host %s have xstor scsi session, have clean." % (ip))
        else:
            log.info("Host %s not find scsi session, will pass" % (ip))


def re_pre_lun():
    lun_map_ids = osan.get_lun_maps(deploy_ips[0])
    log.info("LUN map will be cleaned up. be cleaned lun map ID is %s" % (lun_map_ids))
    for lun_map_id in lun_map_ids:
        log.info("在节点 %s 删除LUN MAP ，映射ID: %s" % (deploy_ips[0], lun_map_id))
        osan.delete_lun_map(s_ip=deploy_ips[0], map_id=lun_map_id)
    lun_ids = osan.get_lun(s_ip=deploy_ips[0])
    log.info("Get Info:\nGet lun ids:%s , need delete after create new lun %s" % (lun_ids, pre_lun_num))
    for lun_id in lun_ids:
        log.info("Remove the lun: %s from node:%s" % (lun_id, deploy_ips[0]))
        osan.delete_lun(s_ip=deploy_ips[0], lun_id=lun_id)
    create_luns(s_ip=deploy_ips[0], nums=pre_lun_num, type="THIN")
    create_lun_map()


def clean_test_env(disk_num=None):
    '''
    :param disk_num: 预设硬盘个数，不符合预期直接退出
    :pre_lun: 测试环境预先配置lun数量
    :return: 每个节点硬盘数组成一个列表
    '''
    log.info("Check Xstor LUN test environment")
    check_lun_env()
    log.info("Check Node Network device")
    check_eth()  # 检查存储端网卡
    log.info("Check Node Disk Device")
    disks = check_disk(disk_num)  # 检查各个节点硬盘，不设置预期值将不进行对比
    log.info("Check xStor vip status")
    check_vip_status()  # 检查VIP是否都能ping通。不通则退出
    log.info("Check Host Device")
    check_host()  # 检查主机端scsi
    log.info("Check lun map ,if found it, will clean up")
    lun_map_ids = osan.get_lun_maps(deploy_ips[0])
    if len(lun_map_ids) > pre_lun_num:
        log.info("if The system have lun maping ,will clean up")
        clean_lun_map(deploy_ips[0])
    elif len(lun_map_ids) == pre_lun_num:
        log.info("Get The system number of lun map %s" % (pre_lun_num))
        log.info("will pass")
    elif len(lun_map_ids) < pre_lun_num:
        create_lun_map(deploy_ips[0])
    else:
        log.info("get lun map is %s, will need add lun " % (len(lun_map_ids)))
    log.info("5.Check lun ,if found it, clean up")
    lun_ids = osan.get_lun(s_ip=deploy_ips[0])
    log.info(lun_ids)
    if len(lun_ids) > pre_lun_num:
        log.info("The system have lun, will clean other luns")
        clean_lun_map(deploy_ips[0])
        clean_lun(deploy_ips[0])  # 删除多余lun
    elif len(lun_ids) == pre_lun_num:
        log.info("Get The system have number of lun %s" % (pre_lun_num))
        log.info("will pass")
    else:
        re_pre_lun()  # 删掉所有创建的lun 重新创建默认预设lun
    log.info("check test environment finished")
    return disks


def get_free_jnl_id():
    """
    :Usage:获取free日志节点ID
    :param s_ip: 服务节点IP
    :return: list，free日志节点ID
    """
    free_jnl_ids = []
    cmd = ('ssh %s "/home/parastor/tools/nWatch -t oRole -i 1 -c oRole#rolemgr_view_dump | grep -v fnc_version"' % (
        deploy_ips[0]))
    res, output = commands.getstatusoutput(cmd)
    if res != 0:
        log.error("cmd:%s Get oRole info error:%s" % (cmd, output))
    else:
        output = output.split('\n')
        for i in range(len(output)):
            j = 0
            if "free info" in output[i]:
                if "grpview info" in output[i + 1 + j]:
                    continue
                else:
                    ids = re.split(" |,", output[i + 1 + j])
                    free_jnl_ids.append(ids[2])
                    j += 1
        return list(set(free_jnl_ids))


def get_dataip_info(node_id=None):
    ctl_ips = ReliableTest.get_ctl_ips(node_ip=deploy_ips[0], node_id=node_id)
    data_ips = ReliableTest.get_data_ips(node_ip=deploy_ips[0], node_id=node_id)
    data_eths = ReliableTest.get_eth(node_ip=ctl_ips[0], test_ip=data_ips)
    extra_ips = ReliableTest.get_extra_ips(node_ip=ctl_ips[0], node_id=node_id, vip=vips, svip=svip)
    return data_eths, extra_ips


def get_ioip_info(node_id=None):
    ctl_ips = ReliableTest.get_ctl_ips(node_ip=deploy_ips[0], node_id=node_id)
    data_ips = ReliableTest.get_data_ips(node_ip=deploy_ips[0], node_id=node_id)
    io_eths = ReliableTest.get_eth(node_ip=ctl_ips[0], test_ip=vip)
    extra_ips = ReliableTest.get_extra_ips(node_ip=ctl_ips[0], node_id=node_id, vip=vips, svip=svip)
    return io_eths, extra_ips


def prepare():
    """
    :Usage:检查集群环境
    :return: None
    """
    nodes = osan.get_nodes(s_ip=deploy_ips[0])
    # 检查所有节点IP是否正常
    # log.info("检查所有节点IP是否正常.")
    for ip in deploy_ips:
        common.check_ip(ip)
    for id in nodes:
        dataip = ReliableTest.get_data_ips(node_ip=deploy_ips[0], node_id=id)
        cmd = ("ping -c 1 %s" % (dataip,))
        res, output = commands.getstatusoutput(cmd)
        if res != 0:
            deth, dextra = get_dataip_info(node_id=id)
            ReliableTest.run_up_net(dextra[0], deth)
            ioeth, ioextra = get_ioip_info(node_id=id)
            ReliableTest.run_up_net(ioextra[0], ioeth)
    vip = osan.get_vip_address_pools(n_id="1", s_ip=deploy_ips[0])
    vip = com2_osan.analysis_vip(vip[0])
    for ip in vip:
        cmd = ("ping -c 2 %s" % (ip,))
        res, output = commands.getstatusoutput(cmd)
        if res != 0:
            log.error("Sorry, the vip: %s can not attatch." % (ip,))
            os._exit(110)
    # 检查所有节点状态是否为HEALTHY
    # log.info("检查所有节点状态是否为HEALTHY.")
    for id in nodes:
        while 'HEALTHY' not in node.get_node_state(id):
            time.sleep(20)
            log.info("等待nodeid: %s 数据修复ing" % (str(id)))
    # 检查所有磁盘状态是否为HEALTHY
    # log.info("检查所有磁盘状态是否为HEALTHY.")
    for id in nodes:
        cmd = ("ssh %s ' pscli --command=get_disks --node_ids=%s | grep DISK_STATE '" % (deploy_ips[0], str(id)))
        res, output = commands.getstatusoutput(cmd)
        if res != 0:
            log.error("Get nodes failed.")
            os._exit(1)
        else:
            while 'ISOLATE' in output:
                time.sleep(20)
                log.info("磁盘状态是: ISOLATE，位于节点:nodeid  %s" % (str(id)))
                cmd = (
                        "ssh %s ' pscli --command=get_disks --node_ids=%s | grep DISK_STATE '" % (
                    deploy_ips[0], str(id)))
                res, output = commands.getstatusoutput(cmd)


def get_option(*args, **kwargs):
    """
     Xstor的查询操作(主要是对pscli查询的返回值进行取值操作)
    :param  kwargs['s_ip']: 服务器节点ip
    :param kwargs['command']:   要查询的命令
    :param kwargs ['indexname'] :json文件的节点
    :param kwargs['argv']:要查询的属性
    :return:
    """
    result = []
    if None == kwargs['s_ip']:
        pass
        exit(1)
    else:
        cmd = ("ssh {} \"pscli --command={}\"".format(kwargs['s_ip'], kwargs['command']))
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        if (res != 0):
            pass
            exit(1)
        else:
            final = json.loads(final)
            finals = final['result']
            log.info("get lun total numbers: %s" % (finals['total']))
            return finals['total']


def rel_check_before_run(file_name, jnl_rep=None, data_rep=None, free_jnl_num=None, **kwargs):
    """
    :Usage:可靠性测试部分，运行前检查环境
    :param filename: 日志文件
    :param node_num:集群内节点数
    :param jnl_rep:日志副本数
    :param data_rep:数据副本数
    :return: None
    """
    # 检查进程是否正常，节点个数是否满足测试要求,检查逻辑盘是否有坏对象
    prepare_clean.x1000_test_prepare(file_name, **kwargs)
    # 检查IP、节点、磁盘状态是否正常
    # prepare()
    # 检查oSan是否有坏对象
    com_bd_disk.check_bad_obj()
    # 检查逻辑节点是否有异常状态
    com_bd_disk.check_lnode_state()
    # 检查日志副本数是否满足测试s要求
    cur_jnl_rep = com_bd_disk.get_jnl_replica(s_ip=deploy_ips[0])
    cur_data_rep = com_bd_disk.get_min_lun_replica(s_ip=deploy_ips[0])
    if None != get_free_jnl_id():
        cur_jnl_num = len(get_free_jnl_id())
        if jnl_rep != None and cur_jnl_rep < jnl_rep:
            log.error(
                "I found you need jnl replica: %d [cur: %d]isn't euqal with the test request." % (jnl_rep, cur_jnl_rep))
            os._exit(-1)
            # 检查数据副本数是否满足测试要求
        elif data_rep != None and cur_data_rep < data_rep:
            log.error("I found you need  data replica: %d [cur: %d]isn't euqal with the test request." % (
                data_rep, cur_data_rep))
            os._exit(-1)
        elif free_jnl_num != None and cur_jnl_num < free_jnl_num:
            log.error("I found you need free jnl number: %d [cur: %d]isn't euqal with the test request." % (
                free_jnl_num, cur_jnl_num))
            os._exit(-1)


def get_os_type(s_ip):
    """
    :Auther: Liu he
    :Description: 读取机器类型
    :param s_ip: 测试节点IP地址
    :return: VM虚拟机将返回字符VM，其他类型机器返回"phy"
    ====================================================================================
    :注：该方法适用于多种虚拟机，stdout返回值在其他类型虚拟机上需要验证，物理机返回机器型号（若有）
    ====================================================================================
    """
    if "True" == ReliableTest.check_ping(s_ip):
        log.error("Node %s do not get info,Please check IP or the machine status" % (s_ip))
        os._exit(1)
    else:
        cmd = ("ssh %s \" dmidecode -s system-product-name\"" % (s_ip))
        rc, stdout = commands.getstatusoutput(cmd)
        if rc != 0:
            log.info("get  %s system type failed.\n Error Info : \n %s" % (s_ip, stdout))
            os._exit(1)
        else:
            if "VMware" in stdout:
                log.info("check %s the system is %s " % (s_ip, stdout))
                return "VM"
            else:
                log.info("Get The test %s machine is %s ,will return\"phy\"" % (s_ip, stdout))
                return "phy"


def down_node(node_ip, type_info, cmd=None):
    """
    :Auther: Liu he
    :param node_ip: 节点IP
    :param type_info: 节点类型，由get_os_type函数导入
    :param cmd: 是否使用命令关机，
    :return: 虚拟机返回虚拟机ID号，物理机返回IPMI地址
    """
    fun_name = get_current_function_name()
    var_list = [node_ip, type_info]
    if all(var_list):
        if type_info == "phy":
            if cmd is None:
                ipmi_ip = ReliableTest.get_ipmi_ip(node_ip)
                log.info("Ryturn by functoin \"%s\":The pyh node %s will IPMI to down os" % (fun_name, node_ip))
                if False == ReliableTest.run_down_node(ipmi_ip):
                    print("node %s down failed!!!" % node_ip)
                    os._exit(1)
                else:
                    return ipmi_ip
            else:
                ipmi_ip = ReliableTest.get_ipmi_ip(node_ip)
                com_lh.os_power_reset(node_ip, cmd)
                while True:
                    status = com_lh.get_power_status(bmc_ip=ipmi_ip)
                    if status == "off" and (cmd == "init 0" or cmd == 'echo o >/proc/sysrq-trigger'):
                        log.info("Ryturn by functoin \"%s\":The system %s power off success" % (fun_name, node_ip))
                        return ipmi_ip
                    elif status == "on" and (cmd == "init 6" or cmd == 'echo b >/proc/sysrq-trigger'):
                        log.info("Ryturn by functoin \"%s\":The system %s reboot success" % (fun_name, node_ip))
                        return ipmi_ip
                    else:
                        time.sleep(5)
        else:
            (esxi_ip, esxi_un, esxi_pw) = get_config.get_esxi(conf_file)
            if cmd is None:
                log.info("Ryturn by functoin \"%s\": the VMware node %s will power cut " % (fun_name, node_ip))
                vm_id = ReliableTest.run_down_vir_node(esxi_ip=esxi_ip[0], u_name=esxi_un[0], pw=esxi_pw[0],
                                                       node_ip=node_ip)
                log.info("Down node finished. VM ID : %s " % (vm_id))
                return vm_id
            else:
                log.info("Ryturn by functoin \"%s\":The node %s will down make cmd :%s" % (fun_name, node_ip, cmd))
                vm_id = com_lh.vm_id(esxi_ip=esxi_ip[0], u_name=esxi_un[0], pw=esxi_pw[0], node_ip=node_ip)
                com_lh.os_power_reset(node_ip, cmd)
                # com_lh.poweroff_os(s_ip=node_ip, cmd_c=cmd)
                while True:
                    vm_status = com_lh.get_vm_status(esxi_ip=esxi_ip[0], vm_name=esxi_un[0], pw=esxi_pw[0],
                                                     vm_id=vm_id).strip()
                    if vm_status == "Powered off" and (cmd == "init 0" or cmd == 'echo o >/proc/sysrq-trigger'):
                        log.info("Ryturn by functoin \"%s\":The vm system %s power off success. VM ID is : %s" % (
                            fun_name, node_ip, vm_id))
                        return vm_id
                    elif vm_status == "Powered on" and (cmd == "init 6" or cmd == 'echo b >/proc/sysrq-trigger'):
                        log.info("Ryturn by functoin \"%s\":The vm system %s reboot success. VM ID is : %s" % (
                            fun_name, node_ip, vm_id))
                        return vm_id
                    else:
                        time.sleep(5)
    else:
        log.error("Ryturn by functoin \"%s\":Variable ack is error: \n node_ip:%s \n type_info:%s \n cmd:%s" % (
            fun_name, node_ip, type_info, cmd))
        os._exit(1)


def up_node(node_info=None, type_info=None):
    """
    :Auther: Liuhe
    :Description: 节点开机，根据节点类型判断开机方式
    :param node_info: down_node的返回值
    :param type_info: 节点类型类型，由get_os_type返回值
    :return:
    """
    if type_info == "phy":
        log.info("The pyh node will IPMI to up os")
        if False == ReliableTest.run_up_node(node_info):
            print("node up failed!!!")
            os._exit(1)
    elif type_info == "VM":
        (esxi_ip, esxi_un, esxi_pw) = get_config.get_esxi(conf_file)
        com_lh.os_up(nums=node_info, esxi_ip=esxi_ip[0], u_name=esxi_un[0], pw=esxi_pw[0])
    else:
        log.error("get node types failed.\nnode_info:%s,type_info:%s " % (node_info, type_info))
        os._exit(1)


def from_xml_get_svip2():
    config_info = xml.dom.minidom.parse(conf_file)
    svips_info = config_info.getElementsByTagName('svips')[0]
    svips_infos = svips_info.getElementsByTagName('svip')
    svips_list = []
    for svip in svips_infos:
        ip = svip.getElementsByTagName('ip')[1].firstChild.nodeValue
        svips_list.append(ip)
    return svips_list


def from_xml_get_vip2():
    config_info = xml.dom.minidom.parse(conf_file)
    vips_info = config_info.getElementsByTagName('vips')[0]
    vips_infos = vips_info.getElementsByTagName('vip')
    vips_list = []
    for vip in vips_infos:
        ip = vip.getElementsByTagName('ip')[1].firstChild.nodeValue
        vips_list.append(ip)
    return vips_list


def vdb_test():
    log.info("step:lun will map")
    create_lun_map(deploy_ips[0])
    log.info("step: ISCSI login")
    create_iscsi_login()
    log.info("step:will running vdbench")
    lun_name = osan.ls_scsi_dev(client_ip=client_ips[0])
    if len(lun_name) > 10:
        lun_name = lun_name[:10]
    vdb_file = com2_osan.gen_vdb_xml(lun=lun_name, xfersize="4k", rdpct="50")
    log.info("step:start vdbench test")
    com2_osan.run_vdb(client_ip=client_ips[0], vdb_xml=vdb_file, output=client_ips[0], jn_jro="jn", time=180)
    com2_osan.run_vdb(client_ip=client_ips[0], vdb_xml=vdb_file, output=client_ips[0], jn_jro="jro")
    log.info("step:vdbench running finished")


def get_lun_default_los_id(lun_id):
    """
    :author:liuhe
    :Date:2019-3-4
    :Description:获取lun id和los id对应值
    :return: lun 默认los id
    """
    for ip in deploy_ips:
        if False is ReliableTest.check_ping(ip):
            continue
        cmd = ("ssh %s ' pscli --command=get_luns'" % (ip))
        log.info(cmd)
        res, output = commands.getstatusoutput(cmd)
        if res != 0:
            continue
        else:
            output = json.loads(output)
            luns_info = output['result']['luns']
            for info in luns_info:
                if lun_id == info["id"]:
                    default_id = info['default_target_id']
                    log.info("get default_target_id:%s" % (default_id))
                    return default_id


def main():
    # 初始化配置文件
    file_name = os.path.basename(__file__)
    file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
    log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
    log.init(log_file_path, True)
    clean_test_env()


if __name__ == '__main__':
    main()

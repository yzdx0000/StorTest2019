#!/usr/bin/python
# -*-coding:utf-8 -*

import os
import sys
import re
import json
import time
import commands
import utils_path
import common2
import common
import log
import get_config
import ReliableTest
import threading
import login
import random
import prepare_clean
import breakdown

conf_file = common2.CONF_FILE  # 配置文件路径
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
type_info = get_config.get_machine_type(conf_file)
if type_info == "vir":
    (esxi_ip, esxi_un, esxi_pw) = get_config.get_esxi(conf_file)
osan = common2.oSan()
node = common.Node()
disk = breakdown.disk()
# #获取vip
try:
    vip = osan.get_vip_address_pools(n_id="1", s_ip=deploy_ips[0])  # 获取vip,二维数组
    vip = osan.analysis_vip(vip[0])
    svip = osan.get_svip(s_ip=deploy_ips[0])
except Exception as e:
    log.info(e)

# 故障节点IP
def get_fault_ip():
    fault_ip = random.choice(deploy_ips)
    return fault_ip


def down_node(fault_ip=None):
    type_info = get_config.get_machine_type(conf_file)
    if type_info == "phy":
        ipmi_ip = ReliableTest.get_ipmi_ip(fault_ip)
        if False == ReliableTest.run_down_node(ipmi_ip):
            print ("node %s down failed!!!" % fault_ip)
            exit(1)
        else:
            return ipmi_ip
    else:
        (esxi_ip, esxi_un, esxi_pw) = get_config.get_esxi(conf_file)
        vm_id = ReliableTest.run_down_vir_node(esxi_ip=esxi_ip[0], u_name=esxi_un[0], pw=esxi_pw[0], node_ip=fault_ip)
        return vm_id


def up_node(node_info=None):
    type_info = get_config.get_machine_type(conf_file)
    if type_info == "phy":
        if False == ReliableTest.run_up_node(node_info):
            print ("node up failed!!!")
            exit(1)
    else:
        (esxi_ip, esxi_un, esxi_pw) = get_config.get_esxi(conf_file)
        ReliableTest.run_up_vir_node(esxi_ip=esxi_ip[0], u_name=esxi_un[0], pw=esxi_pw[0], vm_id=node_info)


def jnl_gp_id(vip=None):
    fault_ip_a = osan.get_node_by_vip(vip=vip)
    fault_id_a = node.get_node_id_by_ip(fault_ip_a)
    jnl_gp = osan.get_same_jnl_group(fault_id_a)
    return jnl_gp


def jnl_gp_ip(node_id=None):
    return node.get_node_ip_by_id(node_id)


def get_ctlip_info(node_id=None):
    ctl_ips = ReliableTest.get_ctl_ips(node_ip=deploy_ips[0], node_id=node_id)
    data_ips = ReliableTest.get_data_ips(node_ip=deploy_ips[0], node_id=node_id)
    ctl_eths = ReliableTest.get_eth(node_ip=ctl_ips[0], test_ip=ctl_ips)
    extra_ips = ReliableTest.get_extra_ips(node_ip=ctl_ips[0], node_id=node_id, vip=vip, svip=svip)
    return ctl_eths, extra_ips


def get_dataip_info(node_id=None):
    ctl_ips = ReliableTest.get_ctl_ips(node_ip=deploy_ips[0], node_id=node_id)
    data_ips = ReliableTest.get_data_ips(node_ip=deploy_ips[0], node_id=node_id)
    data_eths = ReliableTest.get_eth(node_ip=ctl_ips[0], test_ip=data_ips)
    extra_ips = ReliableTest.get_extra_ips(node_ip=ctl_ips[0], node_id=node_id, vip=vip, svip=svip)
    return data_eths, extra_ips


def get_data_eth(node_id=None):
    ctl_ips = ReliableTest.get_ctl_ips(node_ip=deploy_ips[0], node_id=node_id)
    data_ips = ReliableTest.get_data_ips(node_ip=deploy_ips[0], node_id=node_id)
    data_eths = ReliableTest.get_eth(node_ip=ctl_ips[0], test_ip=data_ips)
    return data_eths


def get_ioip_info(node_id=None):
    ctl_ips = ReliableTest.get_ctl_ips(node_ip=deploy_ips[0], node_id=node_id)
    data_ips = ReliableTest.get_data_ips(node_ip=deploy_ips[0], node_id=node_id)
    io_eths = ReliableTest.get_eth(node_ip=ctl_ips[0], test_ip=vip)
    extra_ips = ReliableTest.get_extra_ips(node_ip=ctl_ips[0], node_id=node_id, vip=vip, svip=svip)
    return io_eths, extra_ips


def get_io_eth(node_id=None):
    vip = osan.get_vip_address_pools(n_id="1", s_ip=deploy_ips[0])  # 获取vip,二维数组
    vip = osan.analysis_vip(vip[0])
    ctl_ips = ReliableTest.get_ctl_ips(node_ip=deploy_ips[0], node_id=node_id)
    io_eths = ReliableTest.get_eth(node_ip=ctl_ips[0], test_ip=vip)
    return io_eths


def get_orole_master_id(s_ip=None):
    '''
    :Usage:获取oRole主节点ID
    :param s_ip: 集群内任意节点IP
    :return: int，节点ID
    '''
    cmd = ('ssh %s "/home/parastor/tools/nWatch -t oRole -i 1 -c oRole#rolemgr_master_dump"' % (s_ip))
    res, output = commands.getstatusoutput(cmd)
    if res != 0:
        log.error('Get oRole master error.')
        # exit(1)
    else:
        master = output.strip().split(':')[-1]
        return master
    return


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
        log.error('Get oRole info error.')
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


def get_jnl_node_id():
    """
    :Usage:获取日志节点ID列表
    :return:list,日志节点列表
    """
    jnl_node_ids = []
    node_ids = osan.get_nodes(s_ip=deploy_ips[1])
    for id in node_ids:
        cmd = ("ssh %s ' pscli --command=get_nodes --ids=%s'" % (deploy_ips[1], str(id)))
        res, output = commands.getstatusoutput(cmd)
        if res != 0:
            log.error("Get node info failed.")
            os._exit(1)
        else:
            if "SHARED" not in output:
                continue
            else:
                jnl_node_ids.append(id)
    return jnl_node_ids


def get_non_free_node_id():
    """
    :Usage:获取非日志节点ID列表
    :return:list,非日志节点ID列表
    """
    node_ids = osan.get_nodes(s_ip=deploy_ips[1])
    free_jnl_id = get_free_jnl_id()
    jnl_node_id = get_jnl_node_id()
    non_free_node_ids = list(set(node_ids).difference(set(jnl_node_id)))
    non_free_node_ids = list(set(non_free_node_ids).difference(free_jnl_id))

    return non_free_node_ids


def get_io_node_id():
    """
    :Usage:获取业务节点
    :return: 业务节点的IP列表
    """
    io_node_list = []
    if all(vip):
        for node_vip in vip:
            node_ip = osan.get_node_by_vip(node_vip)
            node_id = node.get_node_id_by_ip(node_ip)
            io_node_list.append(node_id)
        io_node_ids = list(set(io_node_list))
        return io_node_ids
    else:
        log.error("vip is invalid.%s" % vip)
        os._exit(1)


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
                cmd = ("ssh %s ' pscli --command=get_disks --node_ids=%s | grep DISK_STATE '" % (
                deploy_ips[0], str(id)))
                res, output = commands.getstatusoutput(cmd)


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
    prepare_x1000.x1000_test_prepare(file_name, **kwargs)
    # 检查IP、节点、磁盘状态是否正常
    prepare()
    # 检查oSan是否有坏对象
    disk.check_bad_obj()
    # 检查逻辑节点是否有异常状态
    disk.check_lnode_state()
    # 检查日志副本数是否满足测试要求
    cur_jnl_rep = disk.get_jnl_replica(s_ip=deploy_ips[0])
    # cur_data_rep = disk.get_min_lun_replica(s_ip=deploy_ips[0])
    if None != get_free_jnl_id():
        cur_jnl_num = len(get_free_jnl_id())
    if jnl_rep != None and cur_jnl_rep < jnl_rep:
        log.error(
            "I found you need jnl replica: %d [cur: %d]isn't euqal with the test request." % (jnl_rep, cur_jnl_rep))
        os._exit(-1)
    # 检查数据副本数是否满足测试要求
    elif data_rep != None and cur_data_rep < data_rep:
        log.error(
            "I found you need  data replica: %d [cur: %d]isn't euqal with the test request." % (data_rep, cur_data_rep))
        os._exit(-1)
    elif free_jnl_num != None and cur_jnl_num < free_jnl_num:
        log.error("I found you need free jnl number: %d [cur: %d]isn't euqal with the test request." % (
        free_jnl_num, cur_jnl_num))
        os._exit(-1)


def check_host(ip):
    '''
    :Author:Diws
    :Date:20180905
    :param ip:
    :return:
    '''
    cmd = ("ssh %s 'hostname'" % (ip))
    rc, stdout = commands.getstatusoutput(cmd)
    while rc != 0:
        time.sleep(10)
        rc, stdout = commands.getstatusoutput(cmd)
        log.info("Sorry, the system does not OK.")
    cmd = ("ssh %s 'pscli --command=get_nodes'" % (ip))
    rc, stdout = commands.getstatusoutput(cmd)
    while rc != 0:
        time.sleep(10)
        rc, stdout = commands.getstatusoutput(cmd)
        log.info("Sorry, the xstor does not OK.")
    disk.restart_otrc(ip)
    nid = node.get_node_id_by_ip(ip)
    while 'HEALTHY' not in node.get_node_state(nid):
        time.sleep(20)
        log.info("等待节点恢复")

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
import prepare_x1000
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
# 获取vip
vip = osan.get_vip_address_pools(n_id="1", s_ip=deploy_ips[0])  # 获取vip,二维数组
vip = osan.analysis_vip(vip[0])
svip = osan.get_svip(s_ip=deploy_ips[0])
current_path = os.path.dirname(os.path.abspath(__file__))


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
    ctl_ips = ReliableTest.get_ctl_ips(node_ip=deploy_ips[0], node_id=node_id)
    io_eths = ReliableTest.get_eth(node_ip=ctl_ips[0], test_ip=vip)
    return io_eths


def get_orole_master_id(s_ip=None):
    '''
    :Usage:获取oRole主节点ID
    :param s_ip: 集群内任意节点IP
    :return: int，节点ID
    '''
    # cmd = ('ssh %s "/home/parastor/tools/nWatch -t oRole -i 1 -c oRole#rolemgr_master_dump"' % (s_ip))
    for d_ip in deploy_ips:
        if False is ReliableTest.check_ping(d_ip):
            continue
        else:
            n_id = disk.get_node_id_by_ip(n_ip=d_ip)
            cmd = '/home/parastor/tools/nWatch -t oRole -i %s -c oRole#rolemgr_master_dump' % (n_id)
            res, output = ReliableTest.run_pscli_cmd(pscli_cmd=cmd)
            # res, output = commands.getstatusoutput(cmd)
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
    for id in nodes:
        dataip = ReliableTest.get_data_ips(node_ip=deploy_ips[0], node_id=id)
        cmd = ("ping -c 1 %s" % (dataip,))
        res, output = commands.getstatusoutput(cmd)
        if res != 0:
            deth, dextra = get_dataip_info(node_id=id)
            ReliableTest.run_up_net(dextra[0], deth)
            # ioeth, ioextra = get_ioip_info(node_id=id)
            # ReliableTest.run_up_net(ioextra[0],ioeth)
    vip = osan.get_vip_address_pools(n_id="1", s_ip=deploy_ips[0])
    vip = osan.analysis_vip(vip[0])
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

    time.sleep(15)
    # 检查进程是否正常，节点个数是否满足测试要求,检查逻辑盘是否有坏对象
    prepare_x1000.x1000_test_prepare(file_name, **kwargs)
    # prepare_clean.x1000_test_prepare(file_name, **kwargs)
    # 检查IP、节点、磁盘状态是否正常
    # prepare()
    # 检查oSan是否有坏对象
    disk.check_bad_obj()
    # 检查逻辑节点是否有异常状态
    disk.check_lnode_state()
    # 检查日志副本数是否满足测试要求
    cur_jnl_rep = disk.get_jnl_replica(s_ip=deploy_ips[0])
    cur_data_rep = disk.get_min_lun_replica(s_ip=deploy_ips[0])
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
    cmd = ("ssh %s 'pscli --command=get_services'" % (ip))
    rc, stdout = commands.getstatusoutput(cmd)
    while rc != 0:
        time.sleep(10)
        rc, stdout = commands.getstatusoutput(cmd)
        log.info("Sorry, the xstor does not OK.")
    # disk.restart_otrc(ip)
    nid = disk.get_node_id_by_ip(n_ip=ip)
    while 'HEALTHY' not in node.get_node_state(nid):
        time.sleep(20)
        log.info("等待节点恢复")
    log.info("系统启动成功,节点已恢复正常.")


def modify_deploy_xml(dst_ip=None, ssd=True):
    """
    :Author:Diws
    :Date:20181206
    :return: str, /tmp/temp.xml
    """
    # 判断节点是否干净，有残留的话，重新清理一次
    cmd = ("ssh root@%s 'ls /home/parastor/tools/deployment/uninstall_local_software.py'" % (dst_ip,))
    res, output = commands.getstatusoutput(cmd)
    if res == 0:
        cmd = ("ssh root@%s 'python /home/parastor/tools/deployment/uninstall_local_software.py --reserve_log=0'" % (dst_ip,))
        commands.getstatusoutput(cmd)
    # 获取系统id，uuid，name
    sysid, uuid, name = disk.get_sysid_uuid()
    # 获取安装包名
    cmd = ('ls /home/StorTest/src_code/ofs/code/bin/*xz')
    res, output = commands.getstatusoutput(cmd)
    pkg = output.split('/')[-1]
    # 获取扩容节点hostname
    cmd = ("ssh root@%s 'hostname'" % (dst_ip,))
    res, hostname = commands.getstatusoutput(cmd)
    # 获取数据网
    data_ips = ReliableTest.get_data_ips(node_id=1)
    pres = []
    for data_ip in data_ips:
        cmd = ("echo %s | sed -r 's/(.*)(\.[0-9]+)/\\1/g'" % (data_ip,))
        (res, final) = commands.getstatusoutput(cmd)
        pres.append(final)
    dst_data_ips = []
    for pre in pres:
        cmd = ('ssh root@%s "ip a |grep %s | sed -n 1p"' % (dst_ip, pre))
        print cmd
        res, output = commands.getstatusoutput(cmd)
        if len(output)==0:
            cmd = ("echo %s | sed -r 's/(.*)(\.[0-9]+)/\\1/g'" % (pre,))
            (res, pre) = commands.getstatusoutput(cmd)
            cmd = ('ssh root@%s "ip a |grep %s | sed -n 1p"' % (dst_ip, pre))
            print cmd
            res, output = commands.getstatusoutput(cmd)
        if res != 0:
            log.error("Sorry,get data ip on %s failed.Please check if your node has %s." % (dst_ip, pre))
            os._exit(1)
        else:
            output = re.sub('  ', '', output)
            print output
            output = output.split(' ')
            print output
            output = output[1].split('/')[0]
            print output
            dst_data_ips.append(output)
    # 获取节点数量，计算节点位置
    nodes_num = osan.get_nodes()
    nodes_num = len(nodes_num)
    node_pos = (nodes_num + 3) * 2
    # 计算zk id
    zk_id = nodes_num + 1
    from xml.etree import ElementTree
    deploy_xml = current_path + '/add_node.xml'
    temp_xml = current_path + '/temp.xml'
    cmd = ('\cp %s %s' % (deploy_xml, temp_xml))
    commands.getstatusoutput(cmd)
    root_tree = ElementTree.parse(temp_xml)
    root = root_tree.getroot()
    # 修改系统uuid
    uuid_new = root.find('uuid')
    uuid_new.text = uuid
    # 修改系统id
    sysid_new = root.find('sysid')
    sysid_new.text = str(sysid)
    # 修改系统name
    name_new = root.find('name')
    name_new.text = str(name)
    # 修改包路径
    name_new = root.find('package_path')
    name_new.text = '/home/deploy/' + pkg
    # 修改hostname
    name_new = root.find('nodes/node/hostname')
    name_new.text = hostname
    # 修改管理IP
    name_new = root.find('nodes/node/ctl_ips/ip')
    name_new.text = dst_ip
    # 修改数据IP
    for dst_data_ip in dst_data_ips:
        name_new = root.find('nodes/node/data_ips')
        new_ele = ElementTree.Element('ip')
        new_ele.text = dst_data_ip
        name_new.append(new_ele)
    # 修改机柜位置
    name_new = root.find('nodes/node/position')
    name_new.text = str(node_pos)
    # 修改zk id
    # name_new = root.find('nodes/node/zookeeper/id')
    # name_new.text = str(zk_id)
    # 获取目标节点磁盘信息
    ssd_disks, data_disks = get_node_disks(dst_ip=dst_ip)
    # 修改共享盘
    tmp_val = 0
    if ssd == True:
        for ssd_disk in ssd_disks:
            name_news = root.find('nodes/node/disks')
            new_eles = ElementTree.Element('disk')
            name_news.append(new_eles)
            name_new = root.findall('nodes/node/disks/disk')[tmp_val]
            new_ele = ElementTree.Element('dev_name')
            new_ele.text = ssd_disk
            name_new.append(new_ele)
            new_ele = ElementTree.Element('usage')
            new_ele.text = "SHARED"
            name_new.append(new_ele)
            new_ele = ElementTree.Element('state')
            new_ele.text = "FREE"
            name_new.append(new_ele)
            tmp_val += 1
    # 修改数据盘
    for ssd_disk in data_disks:
        name_news = root.find('nodes/node/disks')
        new_eles = ElementTree.Element('disk')
        name_news.append(new_eles)
        name_new = root.findall('nodes/node/disks/disk')[tmp_val]
        new_ele = ElementTree.Element('dev_name')
        new_ele.text = ssd_disk
        name_new.append(new_ele)
        new_ele = ElementTree.Element('usage')
        new_ele.text = "DATA"
        name_new.append(new_ele)
        new_ele = ElementTree.Element('state')
        new_ele.text = "FREE"
        name_new.append(new_ele)
        tmp_val += 1
    # 保存修改
    root_tree.write(temp_xml)
    # 拷贝配置文件到各个节点
    for ip in deploy_ips:
        cmd = ("scp %s %s:/tmp/" % (temp_xml, ip))
        commands.getstatusoutput(cmd)
    dst_xml = '/tmp/temp.xml'
    return dst_xml


def get_node_disks(dst_ip=None):
    """
    :Author:Diws
    :Date:20181206
    :param dst_ip:目标节点IP
    :return: list, []
    """
    # 获取系统盘
    cmd = ("ssh root@%s 'lsblk |grep -w \'/\''" % (dst_ip,))
    res, output = commands.getstatusoutput(cmd)
    output = re.sub('[^a-z,A-Z, ]+', '', output)
    output = output.split(' ')
    sys_disk = '/dev/' + output[0]
    # 获取所有磁盘
    cmd = ("ssh root@%s \"lsscsi | grep dev|grep -v sr0 | awk '{print \$NF}'\"" % (dst_ip,))
    res, output = commands.getstatusoutput(cmd)
    all_disks = output.split()
    all_disks.remove(sys_disk)
    # 获取ssd
    cmd = ("ssh root@%s \"lsscsi | grep dev | grep -i ssd | awk '{print \$NF}'\"" % (dst_ip,))
    res, output = commands.getstatusoutput(cmd)
    ssd_disks = output.split()
    # 获取普通盘
    if len(ssd_disks) != 0:
        data_disks = list(set(all_disks).difference(set(ssd_disks)))
    else:
        ssd_disks = all_disks[:2]
        data_disks = all_disks[2:]
    return ssd_disks, data_disks


def get_cluster_cap():
    """
    :Author:Diws
    :Date:20181214
    :Description:获取集群可用容量
    :return: int, capacity of the cluster
    """
    cmd = 'pscli --command=get_system_perf'
    res, output = osan.run_pscli_cmd(pscli_cmd=cmd)
    output = json.loads(output)
    output = output['result']
    return output['total_bytes']/1024/1024/1024


def get_node_cap(n_id=None):
    """
    :Author:Diws
    :Date:20181214
    :Description:获取节点可用容量
    :return: int, capacity of the cluster
    """
    cmd = ('pscli --command=get_nodes --ids=%s' % (str(n_id),))
    res, output = osan.run_pscli_cmd(pscli_cmd=cmd)
    output = json.loads(output)
    return output['result']['nodes'][0]['avail_bytes']/1024/1024/1024


if __name__ == '__main__':
    modify_deploy_xml('10.2.42.11')
#!/usr/bin/python
# -*- encoding=utf8 -*-
####################################################################################
#
# Author: baorb
# date 2018-08-10
# @summary：
#    故障制造。
#
# @changelog：
####################################################################################
import time
import xml.dom.minidom
import commands
import threading
import subprocess
import os
import signal

import log
import common
import random


"""****************************** check environment **************************"""


def check_ping(node_ip, check_ip):
    """
    :author: liyao
    :date: 2018.08.22
    :description: 检查节点是否能ping通
    :param node_ip:被检查节点ip
    :return:
    """
    cmd = 'ping -c 3 %s | grep "0 received" | wc -l' % node_ip
    rc, stdout = common.run_command(check_ip, cmd)
    if '0' != stdout.strip():
        return False
    else:
        return True


def get_nodes_data_ip_by_ip():
    rc, stdout = common.get_nodes()
    common.judge_rc(rc, 0, "Execute command: get_nodes failed. \nstdout: %s" % (stdout))
    data_ip_lst = []
    stdout = common.json_loads(stdout)
    node_info_lst = stdout['result']['nodes']
    for node_info in node_info_lst:
        for data_ip_info in node_info['data_ips']:
            data_ip_lst.append(data_ip_info['ip_address'])

    return data_ip_lst

def get_nodes_data_ip_by_one_ctl_ip(ctl_ip):
    """
    :author: liuyzhb
    :date: 2019.03.18
    :description:
    :param node_ip: 根据具体节点的管理网获取节点的数据网ip
    :return:
    """
    rc, stdout = common.get_nodes()
    common.judge_rc(rc, 0, "Execute command: get_nodes failed. \nstdout: %s" % (stdout))
    data_ip_lst = []
    stdout = common.json_loads(stdout)
    node_info_lst = stdout['result']['nodes']

    for node_info in node_info_lst:
        ctl_ipaddr = node_info['ctl_ips'][0]['ip_address']
        log.info('ctl_ipaddr is')
        log.info(ctl_ipaddr)
        if ctl_ipaddr == str(ctl_ip):
            for data_ip_info in node_info['data_ips']:
                data_ip_lst.append(data_ip_info['ip_address'])
        else:
            log.info('node %s is not we find' %ctl_ipaddr)
    log.info('data_ips of %s is %s' %(ctl_ip,data_ip_lst))
    return data_ip_lst


def check_datanet(node_ip, node_data_ip_lst):
    cmd = 'ip addr | grep "inet "'
    rc, stdout = common.run_command(node_ip, cmd)
    if 0 != rc:
        log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    lines = stdout.strip().split('\n')
    for line in lines:
        ip = line.split()[1].split('/')[0]
        if ip in node_data_ip_lst:
            return True
    return False


def check_path(node_ip, path):
    cmd = 'ls %s' % path
    rc, stdout = common.run_command(node_ip, cmd)
    return rc


def check_node_connection(node_ip, check_ip):
    """
    :author: liyao
    :date: 2018.08.22
    :description: 检查节点是否启动和其上系统是否正常
    :param node_ip: 被检查节点ip
    :return:
    """
    cmd_not_found_rc = 127
    timeout_limit = 600
    time_used = 0
    while True:
        log.info('waiting for 20s')
        time.sleep(20)
        time_used = time_used + 20
        if time_used > timeout_limit:
            return -1

        # 检查节点是否能ping通
        if check_ping(node_ip, check_ip) is False:
            continue
        # 判断数据网是否正常
        data_ip_list = get_nodes_data_ip_by_ip()
        if check_datanet(node_ip, data_ip_list) is False:
            continue
        # 判断节点上是否有/home/parastor/conf
        if 0 != check_path(node_ip, '/home/parastor/conf'):
            continue
        # 判断节点上是否有集群
        cmd = 'pscli --command=get_master'
        rc, stdout = common.run_command(node_ip, cmd)
        if rc == cmd_not_found_rc:
            continue
        if (rc != 0) and ('FindMasterError' in stdout.strip().splitlines()[-1]):
            num = 1
            log.warn('%s return "FindMasterError" %d times' % (cmd, num))
        else:
            break

    return rc
def get_net_eth(node_ip):
    """
    :author: liuyzhb
    :date: 2019.03.16
    :description: 获取一个节点的数据网的网卡名称
    :param node_ip: 被检查节点ip
    :return:
    """
    data_ip_list = get_nodes_data_ip_by_one_ctl_ip(node_ip)
    log.info('data_ip_list is %s' %data_ip_list)
    eth_list = []
    for ip in data_ip_list:
        tem_dic = {}
        cmd1 = 'ip addr | grep %s' % ip
        rc, stdout = common.run_command(node_ip, cmd1)
        if 0 != rc:
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s" % (cmd1, stdout))
        else:
            eth_name = stdout.split()[-1]
            mask_int = int(stdout.split()[1].split('/')[-1])
            log.info('mask_int is %s' %mask_int)
            mask_str = exchange_maskint(mask_int)
            tem_dic["eth"] = eth_name
            tem_dic["dataip"] = ip
            tem_dic["mgrip"] = node_ip
            tem_dic["mask"] = mask_str
        eth_list.append(tem_dic)
    log.info('eth_list is %s' %eth_list)
    return eth_list
def part_net_down(node_id, num_of_eth, num_of_fault,time_of_repair):
    """
    :author:      liuyzhb
    :date:        2019.03.19
    :description: 給指定的一个节点执行断一个数据网，执行num次
    :return:
    """
    # 根据node_id获取node_ip
    node = common.Node()
    node_ip = node.get_node_ip_by_id(node_id)
    # 获取节点的数据网对应网口的网卡和mask的list
    eth_name_list, data_ip_list, mask_list = node.get_node_eth(node_id)
    log.info('eth_list of node_id %s is %s' % (str(node_id), eth_name_list))
    log.info('data_ip_list of node_id %s is %s' % (str(node_id), data_ip_list))
    log.info('mask_list of node_id %s is %s' % (str(node_id), mask_list))
    for n in range(num_of_fault):
        log.info('this is num %s eth fault' %n)
        randomdigit = random.sample(range(len(eth_name_list)), num_of_eth )
        log.info('randomdigit is %s' %randomdigit)
        for i in randomdigit:
            # 获取随机网卡名
            choose_eth = eth_name_list[i]
            choose_mask = mask_list[i]
            log.info('choose_eth is %s' % choose_eth)
            log.info('choose_mask is %s' % choose_mask)
            # 给选出来的网卡执行断网
            rc = down_eth(node_ip, choose_eth)
            if rc != 0:
                return -1
            log.info('down net %s in num %d finish' %(choose_eth, n))

        time.sleep(time_of_repair)
        for i in randomdigit:
            # 获取随机网卡名
            choose_eth = eth_name_list[i]
            choose_mask = mask_list[i]
            rc = up_eth(node_ip, choose_eth, choose_mask)
            if rc != 0:
                return -1
            log.info('up net %s in num %d finish' % (choose_eth, n))
    return 0



"""****************************** process fault ******************************"""


def kill_process(node_ip, pro_name):
    """
    :author:         baoruobing
    :date  :         2018.04.17
    :description:    kill进程
    :param node_ip:  节点ip
    :param pro_name: 进程名字
    :return:
    """
    pidof_pro = ['oStor', 'oPara', 'oRole', 'oMgcd', 'oJob', 'oOss', 'oOms']
    flag = False
    for pro in pidof_pro:
        if pro in pro_name:
            flag = True
            break
    if flag:
        ps_cmd = "pidof %s" % pro_name
        rc, stdout = common.run_command(node_ip, ps_cmd)
        if "" == stdout:
            return
        kill_cmd = ("kill -9 %s" % stdout)
        rc, stdout = common.run_command(node_ip, kill_cmd)
        common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s \n" % (kill_cmd, stdout),
                        exit_flag=False)
    else:
        ps_cmd = ("ps -ef|grep %s | grep -v grep" % pro_name)
        rc, stdout = common.run_command(node_ip, ps_cmd)
        if "" == stdout:
            return
        lines = stdout.split('\n')
        for line in lines:
            if line:
                vars = line.split()
                pid = vars[1]
                kill_cmd = ("kill -9 %s" % pid)
                rc, stdout = common.run_command(node_ip, kill_cmd)
                common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s \n" % (kill_cmd, stdout),
                                exit_flag=False)
    return

def kill_process_in_loop(interval, kill_times, node_ip, process):
    """
    :author:      zhanghan
    :date:        2019.03.14
    :parameters: interval：循环kill进程的时间间隔，int类型
                 kill_times：循环kill进程的次数，int类型
                 node_ip：节点ip
                 process：待kill的进程
    :description: kill指定节点的指定进程，循环多次执行
    :return:     无返回值
    """
    for times in range(kill_times):
        time.sleep(interval)
        kill_process(node_ip, process)

    return

def check_process(node_ip, process):
    """
    :author:        baoruobing
    :date  :        2018.04.17
    :Description:   检查节点中某个进程是否存在
    :param node_ip: 节点ip
    :param process: 进程名字
    :return:
    """
    ps_cmd = ("ps -ef | grep %s | grep -v grep" % process)
    rc, stdout = common.run_command(node_ip, ps_cmd)
    if 0 == rc:
        return True
    else:
        return False
def kill_process_and_rename(node_ip, process, rename_hold_time):
    """
    :author:      zhanghan
    :date:        2019.03.14
    :parameters：rename_hold_time：修改进程名称的维持时间，int类型
    :description: kill指定节点的指定进程，进程被kill前先将其名称rename，防止被自动拉起，超过指定时间后再将其名称恢复，恢复后进程可以被正常拉起
    :return:     0(执行成功)/-3(进程名称指定错误，不进行操作)/-2(进程不存在，不进行操作)/-1(重命名进程失败)
    """
    log.info("start fault")
    pidof_pro1 = ['oStor', 'oPara', 'oRole', 'oMgcd', 'oJob', 'oCnas']
    pidof_pro2 = ['oOss', 'oOms']
    pidof_pro = pidof_pro1 + pidof_pro2
    flag = False
    for pro in pidof_pro:
        if pro in process:
            flag = True
            break
    if flag:
        ps_cmd = "pidof %s" % process
        rc, stdout = command(ps_cmd, node_ip, timeout=60)
        if "" == stdout:
            return -2
        for num in range(3):
            if process not in pidof_pro2:
                cmd_rename = "mv /home/parastor/bin/%s /home/parastor/bin/%s_bak" % (
                    process, process)
            else:
                if "oOms" == process:
                    cmd_rename = "mv /home/parastor/oms/%s /home/parastor/oms/%s_bak" % (
                        process, process)
                else:
                    cmd_rename = "mv /home/parastor/oss/%s /home/parastor/oss/%s_bak" % (
                        process, process)
            rc, output = command(cmd_rename, node_ip, timeout=60)
            if 0 == rc:
                break
            else:
                time.sleep(1)
        else:
            log.info("Function:%s, operation rename process:%s excuted 3 times, all failed!" % ("kill_process_and_rename", process))
            return -1
        kill_cmd = ("kill -9 %s" % stdout)
        rc, stdout = command(kill_cmd, node_ip, timeout=60)
        if rc != 0:
            log.error(
                "node: %s, cmd: %s (process:%s) failed. \nstdout: %s \n" %
                (node_ip, kill_cmd, process, stdout))
        else:
            log.info(
                "node: %s, cmd: %s (process:%s) successed. \nstdout: %s \n" %
                (node_ip, kill_cmd, process, stdout))
        time.sleep(rename_hold_time)
        for num in range(3):
            if process not in pidof_pro2:
                cmd_rename_bak = "mv /home/parastor/bin/%s_bak /home/parastor/bin/%s" % (
                    process, process)
            else:
                if "oOms" == process:
                    cmd_rename_bak = "mv /home/parastor/oms/%s_bak /home/parastor/oms/%s" % (
                        process, process)
                else:
                    cmd_rename_bak = "mv /home/parastor/oss/%s_bak /home/parastor/oss/%s" % (
                        process, process)
            rc, output = command(cmd_rename_bak, node_ip, timeout=60)
            if 0 == rc:
                break
            else:
                time.sleep(1)
        else:
            log.info("Function:%s, operation rename process:%s excuted 3 times, all failed!" % (
            "kill_process_and_rename", process + '_bak'))
            return -1
    else:
        ps_cmd = ("ps -ef|grep %s | grep -v grep" % process)
        rc, stdout = command(ps_cmd, node_ip, timeout=60)
        if "" == stdout:
            return -2
        for num in range(3):
            if ("oJmw" == process) or ("oJmgs" == process):
                cmd_rename = "mv /home/parastor/bin/%s /home/parastor/bin/%s_bak" % (
                    process, process)
            elif "ctdb" == process:
                cmd_rename = "mv /home/parastor/cnas/smb/bin/%s /home/parastor/cnas/smb/bin/%s_bak" % (
                    process, process)
            elif "zk" == process:
                cmd_rename = "mv /home/parastor/tools/deployment/zk_crond.py /home/parastor/tools/deployment/zk_crond_bak.py"
            else:
                log.error(
                    "Process %s is not right, please check process name!!!" %
                    process)
                return -3
            rc, output = command(cmd_rename, node_ip, timeout=60)
            if 0 == rc:
                break
            else:
                time.sleep(1)
        else:
            log.info("Function:%s, operation rename process:%s excuted 3 times, all failed!" % (
                "kill_process_and_rename", process))
            return -1
        lines = stdout.split('\n')
        for line in lines:
            if line:
                vars = line.split()
                pid = vars[1]
                kill_cmd = ("kill -9 %s" % pid)
                rc, stdout = command(kill_cmd, node_ip, timeout=60)
                if rc != 0:
                    log.error(
                        "Execute command: \"%s\" failed. \nstdout: %s \n" %
                        (kill_cmd, stdout))
                else:
                    log.info(
                        "Execute command: \"%s\" successed. \nstdout: %s \n" %
                        (kill_cmd, stdout))
        time.sleep(rename_hold_time)
        for num in range(3):
            if ("oJmw" == process) or ("oJmgs" == process):
                cmd_rename_bak = "mv /home/parastor/bin/%s_bak /home/parastor/bin/%s" % (
                    process, process)
            elif "ctdb" == process:
                cmd_rename_bak = "mv /home/parastor/cnas/smb/bin/%s_bak /home/parastor/cnas/smb/bin/%s" % (
                    process, process)
            elif "zk" == process:
                cmd_rename_bak = "mv /home/parastor/tools/deployment/zk_crond_bak.py /home/parastor/tools/deployment/zk_crond.py"
            else:
                log.error(
                    "Process %s is not right, please check process name!!!" %
                    process)
                return -3
            rc, output = command(cmd_rename_bak, node_ip, timeout=60)
            if 0 == rc:
                break
            else:
                time.sleep(1)
        else:
            log.info("Function:%s, operation rename process:%s excuted 3 times, all failed!" % (
                "kill_process_and_rename", process + '_bak'))
            return -1
    return 0

def kill_process_and_rename_in_loop(node_ip, process, rename_hold_time,num_of_makefault):
    """
    :param node_ip:
    :param process:
    :param rename_hold_time:
    :return:
    """
    for num in range(num_of_makefault):
        log.info("fault num of kill_process_and_rename_in_loop is %s" %num)
        rc = kill_process_and_rename(node_ip, process, rename_hold_time)
        common.judge_rc(rc, 0, "run kill_process_and_rename failed!!!")
        time.sleep(300)


"""****************************** disk fault ******************************"""


def pullout_disk(node_ip, disk_scsi_id, disk_usage):
    """
    :author:             baoruobing
    :date  :             2018.04.17
    :Description:        某个节点中拔出一块磁盘
    :param node_ip:      节点ip
    :param disk_scsi_id: 磁盘的scsi id
    :param disk_usage:   磁盘的用途
    :return:
    """
    ob_node = common.Node()
    ndoe_id = ob_node.get_node_id_by_ip(node_ip)
    rc, stdout = common.get_disks(ndoe_id)
    json_info = common.json_loads(stdout)
    for disk in json_info['result']['disks']:
        log.info('devname:%s  usage:%s  uuid:%s  usedState:%s  storagePoolId:%s  storagePoolType:%s  speed_level :%s '
                 'speed_type:%s' % (disk['devname'], disk['usage'], disk['uuid'], disk['usedState'],
                                    disk['storagePoolId'], disk['storagePoolType'], disk['speed_level'],
                                    disk['speed_type']))
    cmd = "echo scsi remove-single-device %s > /proc/scsi/scsi" % disk_scsi_id
    common.run_command(node_ip, cmd)
    log.info('node %s pullout disk %s, disk usage is %s' % (node_ip, disk_scsi_id, disk_usage))
    return


def insert_disk(node_ip, disk_scsi_id, disk_usage):
    """
    :author:             baoruobing
    :date  :             2018.04.17
    :Description:        某个节点中插入一块磁盘
    :param node_ip:      (str)节点ip
    :param disk_scsi_id: (str)磁盘的scsi id
    :param disk_usage:   (str)磁盘的用途
    :return:
    """
    cmd1 = "echo scsi add-single-device %s > /proc/scsi/scsi" % disk_scsi_id
    log.info('node %s insert disk %s, disk usage is %s' % (node_ip, disk_scsi_id, disk_usage))
    common.run_command(node_ip, cmd1)
    time.sleep(5)
    cmd2 = "lsscsi"
    common.run_command(node_ip, cmd2)
    return

def data_disk_down_and_up(node_ip, disk_lsscsi_id_lst, fault_num, fault_time, wait_time, num_of_makefault):
    """
    拔数据盘故障
    """
    for num in  range(num_of_makefault):
        log.info("this is num %s make_fault" %num)
        num = num  + 1
        fault_disk_lsscsi_id_lst = random.sample(disk_lsscsi_id_lst, fault_num)
        """拔盘"""
        """不断ping节点，知道可以ping通"""
        start_time = time.time()
        while True:
            if common.check_ping(node_ip):
                break
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            log.info('node: %s cannot ping pass %dh:%dm:%ds' % (node_ip, h, m, s))
            time.sleep(20)
        for disk_lsscsi_id in fault_disk_lsscsi_id_lst:
            pullout_disk(node_ip, disk_lsscsi_id, "DATA")

        fault_disk_time = common.choose_time(fault_time)
        time.sleep(fault_disk_time)

        """插盘"""
        """不断ping节点，知道可以ping通"""
        start_time = time.time()
        while True:
            if common.check_ping(node_ip):
                break
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            log.info('node: %s cannot ping pass %dh:%dm:%ds' % (node_ip, h, m, s))
            time.sleep(20)
        for disk_lsscsi_id in fault_disk_lsscsi_id_lst:
            insert_disk(node_ip, disk_lsscsi_id, "DATA")

        wait_disk_time = common.choose_time(wait_time)
        time.sleep(wait_disk_time)



"""****************************** eth fault ******************************"""
def exchange_maskint(mask_int):
    bin_arr = ['0'] * 32
    for i in range(mask_int):
        bin_arr[i] = '1'
    tmpmask = [''.join(bin_arr[i * 8:i * 8 + 8]) for i in range(4)]
    tmpmask = [str(int(tmpstr, 2)) for tmpstr in tmpmask]
    return '.'.join(tmpmask)


def down_eth(node_ip, eth_list):
    """
    :author:         baoruobing
    :date  :         2018.04.17
    :description:    down一个节点的网关
    :param node_ip:  (str)节点ip
    :param eth_list: (list)要down的网关
    :return:
    """
    rc = 0
    if isinstance(eth_list, list) or isinstance(eth_list, tuple):
        eth_tmp_list = eth_list
    else:
        eth_tmp_list = [eth_list]

    for eth_name in eth_tmp_list:
        cmd = 'ifconfig %s down' % eth_name
        rc, stdout = common.run_command(node_ip, cmd)
        if rc != 0:
            return rc
    return rc


def up_eth(node_ip, eth_list, ip_mask_list):
    """
    :author:         baoruobing
    :date  :         2018.04.17
    :description:    down一个节点的网关
    :param node_ip:
    :param eth_list:
    :return:
    """
    rc = 0
    if isinstance(eth_list, list) or isinstance(eth_list, tuple):
        eth_tmp_list = eth_list
        ip_mask_tmp_list = ip_mask_list
    else:
        eth_tmp_list = [eth_list]
        ip_mask_tmp_list = [ip_mask_list]

    for eth_name in eth_tmp_list:
        ip_and_mask = ip_mask_tmp_list[eth_tmp_list.index(eth_name)]
        cmd = 'ifconfig %s %s up' % (eth_name, ip_and_mask)
        rc, stdout = common.run_command(node_ip, cmd)
        if rc != 0:
            return rc
    return rc




"""****************************** node fault ******************************"""


##############################################################################
# ##name  :      makeEasyTag
# ##parameter:   dom：xml对象
# ##             tagname：元素标签名字
# ##             value：文本节点内容
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 生成元素节点（子节点为文本节点）
##############################################################################
def make_text_tag(dom, tagname, value):
    tag = dom.createElement(tagname)
    text = dom.createTextNode(value)
    tag.appendChild(text)
    return tag


##############################################################################
# ##name  :      make_element_tag
# ##parameter:   dom：xml对象
# ##             parent_tag：父元素标签名字
# ##             child_tagname：子元素标签名字
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 生成元素节点（子节点为元素节点）
##############################################################################
def make_element_tag(dom, parent_tag, child_tagname):
    child_tag = dom.createElement(child_tagname)
    parent_tag.appendChild(child_tag)
    return child_tag


##############################################################################
# ##name  :      get_sysinfo
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取系统信息
##############################################################################
def get_sysinfo():
    rc, stdout = common.get_cluster_overview()
    common.judge_rc(rc, 0, "Execute command: get sysinfo failed. \nstdout: %s" % stdout)
    sys_info = common.json_loads(stdout)
    sys_name = sys_info['result']['name']
    sys_id = sys_info['result']['sysid']
    sys_uuid = sys_info['result']['uuid']
    return sys_name, sys_id, sys_uuid


##############################################################################
# ##name  :      xml_add_sysinfo
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加系统信息
##############################################################################
def xml_add_sysinfo(dom, root):
    sys_name, sys_id, sys_uuid = get_sysinfo()
    uuid = make_text_tag(dom, 'uuid', sys_uuid)
    sysid = make_text_tag(dom, 'sysid', str(sys_id))
    name = make_text_tag(dom, 'name', sys_name)
    package_path = make_text_tag(dom, 'package_path', '')
    root.appendChild(uuid)
    root.appendChild(sysid)
    root.appendChild(name)
    root.appendChild(package_path)
    return


##############################################################################
# ##name  :      xml_add_cache_ratio
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加缓存占比信息
##############################################################################
def xml_add_cache_ratio(dom, root):
    rc, stdout = common.get_params(section='MGR', name='shared_pool_cache_ratio')
    common.judge_rc(rc, 0, "Execute command: get params failed. \nstdout: %s" % stdout)
    cache_ratio_info = common.json_loads(stdout)
    cache_ratio_value = cache_ratio_info['result']['parameters'][0]['current']
    cache_ratio = make_text_tag(dom, 'cache_ratio', cache_ratio_value)
    root.appendChild(cache_ratio)
    return


##############################################################################
# ##name  :      xml_add_scenario_id
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加缓存文件系统类型
##############################################################################
def xml_add_scenario_id(dom, root):
    scenario_id_value = '1'
    scenario_id = make_text_tag(dom, 'scenario_id', scenario_id_value)
    root.appendChild(scenario_id)
    return


##############################################################################
# ##name  :      xml_add_eache_set
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加缓存SSD cache
##############################################################################
def xml_add_eache_set(dom, root):
    cache_set_value = '0'
    enable_cache_set = make_text_tag(dom, 'enable_cache_set', cache_set_value)
    root.appendChild(enable_cache_set)
    return


##############################################################################
# ##name  :      get_cabinetinfo
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取机柜信息
##############################################################################
def get_cabinetinfo():
    rc, stdout = common.get_cabinets()
    common.judge_rc(rc, 0, "Execute command: get cabinets failed. \nstdout: %s" % (stdout))
    cabinet_lst = []
    cabinet_info = common.json_loads(stdout)
    cabinets = cabinet_info['result']['cabinets']
    for cabinet in cabinets:
        height = cabinet['height']
        name = cabinet['name']
        cabinet_lst.append([name, height])
    return cabinet_lst


##############################################################################
# ##name  :      xml_add_cabinetinfo
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加机柜信息
##############################################################################
def xml_add_cabinetinfo(dom, root):
    cabinet_lst = get_cabinetinfo()
    xml_cabinets = make_element_tag(dom, root, 'cabinets')
    for cabinet in cabinet_lst:
        name = make_text_tag(dom, 'name', cabinet[0])
        height = make_text_tag(dom, 'height', str(cabinet[1]))
        xml_cabinet = make_element_tag(dom, xml_cabinets, 'cabinet')
        xml_cabinet.appendChild(name)
        xml_cabinet.appendChild(height)

    return


##############################################################################
# ##name  :      xml_add_nodeip
# ##parameter:   type:ip类型('ctl_ips', 'data_ips')
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加节点ip信息
##############################################################################
def xml_add_nodeip(dom, node, node_info, type):
    ctl_ips = make_element_tag(dom, node, type)
    ctl_ips_info = node_info[type]
    for crl_ip_info in ctl_ips_info:
        ip = make_text_tag(dom, 'ip', crl_ip_info['ip_address'])
        ctl_ips.appendChild(ip)
    return


##############################################################################
# ##name  :      xml_add_ipmiinfo
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加节点ipmi信息
##############################################################################
def xml_add_ipmiinfo(dom, node):
    ipmi = make_element_tag(dom, node, 'ipmi')
    ip = make_text_tag(dom, 'ip', '10.0.10.1')
    username = make_text_tag(dom, 'username', 'ipmi_username')
    password = make_text_tag(dom, 'password', 'ipmi_password')
    ipmi.appendChild(ip)
    ipmi.appendChild(username)
    ipmi.appendChild(password)
    return


##############################################################################
# ##name  :      xml_add_nodevs
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加节点nodevs信息
##############################################################################
def xml_add_nodevs(dom, node):
    nvdevs = make_element_tag(dom, node, 'nvdevs')
    device = make_element_tag(dom, nvdevs, 'device')
    sn = make_text_tag(dom, 'sn', 'nvdev1_sn')
    uuid = make_text_tag(dom, 'uuid', 'fdsfssf-42342-322-fsd')
    device.appendChild(sn)
    device.appendChild(uuid)
    return


##############################################################################
# ##name  :      xml_add_zkinfo
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加节点zk信息
##############################################################################
def xml_add_zkinfo(dom, node, node_info):
    zookeeper = make_element_tag(dom, node, 'zookeeper')
    # zk_ip = node_info['zk_ips'][0]
    # zk_id = node_info['zk_id']
    zk_ip = ''
    zk_id = 0
    ip = make_text_tag(dom, 'ip', zk_ip)
    id = make_text_tag(dom, 'id', str(zk_id))
    zookeeper.appendChild(ip)
    zookeeper.appendChild(id)
    return


##############################################################################
# ##name  :      xml_add_service
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加节点服务信息
##############################################################################
def xml_add_service(dom, node, node_info):
    services = make_element_tag(dom, node, 'services')
    services_info = node_info['services']
    for service_info in services_info:
        if service_info['service_type'] in ['oStor', 'oPara']:
            service = make_element_tag(dom, services, 'service')
            type = make_text_tag(dom, 'type', service_info['service_type'])
            service.appendChild(type)
    return


##############################################################################
# ##name  :      xml_add_diskinfo
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加节点硬盘信息
##############################################################################
def xml_add_diskinfo(dom, node, node_info):
    disks = make_element_tag(dom, node, 'disks')
    data_disks_info = node_info['data_disks']
    share_disks_info = node_info['shared_disks']
    disks_info = data_disks_info + share_disks_info
    for disk_info in disks_info:
        if disk_info['usedState'] == 'IN_USE':
            disk = make_element_tag(dom, disks, 'disk')
            dev_name = make_text_tag(dom, 'dev_name', disk_info['devname'])
            usage = make_text_tag(dom, 'usage', disk_info['usage'])
            state = make_text_tag(dom, 'state', 'FREE')
            disk.appendChild(dev_name)
            disk.appendChild(usage)
            disk.appendChild(state)
    return


##############################################################################
# ##name  :      xml_add_nodeinfo
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加节点信息
##############################################################################
def xml_add_nodeinfo(dom, root, node_id):
    nodes = make_element_tag(dom, root, 'nodes')
    node = make_element_tag(dom, nodes, 'node')
    rc, stdout = common.get_nodes(ids=node_id)
    common.judge_rc(rc, 0, "Execute command: get nodes failed. \nstdout: %s" % (stdout))
    node_json = common.json_loads(stdout)
    node_info = node_json['result']['nodes'][0]

    # 添加节点名
    hostname_value = node_info['node_name']
    hostname = make_text_tag(dom, 'hostname', hostname_value)
    node.appendChild(hostname)

    # 添加节点管理ip
    xml_add_nodeip(dom, node, node_info, 'ctl_ips')

    # 添加节点数据ip
    xml_add_nodeip(dom, node, node_info, 'data_ips')

    # 添加haip
    ha_ips = make_text_tag(dom, 'ha_ips', '')
    node.appendChild(ha_ips)

    # 添加节点机柜信息
    cabinet = make_text_tag(dom, 'cabinet', node_info['cabinet_name'])
    position = make_text_tag(dom, 'position', str(node_info['position']))
    node_model = make_text_tag(dom, 'node_model', node_info['model'])
    node.appendChild(cabinet)
    node.appendChild(position)
    node.appendChild(node_model)

    # 添加ipmi信息
    xml_add_ipmiinfo(dom, node)

    # 添加nvdevs信息
    xml_add_nodevs(dom, node)

    # 添加zk信息
    xml_add_zkinfo(dom, node, node_info)

    # 添加service信息
    xml_add_service(dom, node, node_info)

    # 添加硬盘信息
    xml_add_diskinfo(dom, node, node_info)
    return


##############################################################################
# ##name  :      Indent
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 将xml格式化
##############################################################################
def indent_xml(dom, node, indent=0):
    # Copy child list because it will change soon
    children = node.childNodes[:]
    # Main node doesn't need to be indented
    if indent:
        text = dom.createTextNode('\n' + '    ' * indent)
        node.parentNode.insertBefore(text, node)
    if children:
        # Append newline after last child, except for text nodes
        if children[-1].nodeType == node.ELEMENT_NODE:
            text = dom.createTextNode('\n' + '    ' * indent)
            node.appendChild(text)
        # Indent children which are elements
        for n in children:
            if n.nodeType == node.ELEMENT_NODE:
                indent_xml(dom, n, indent+1)
    return


def make_node_xml(node_id):
    impl = xml.dom.minidom.getDOMImplementation()
    dom = impl.createDocument(None, 'install_config', None)
    root = dom.documentElement

    # 添加系统信息
    xml_add_sysinfo(dom, root)

    # 添加缓存占比
    xml_add_cache_ratio(dom, root)

    # 添加文件系统
    xml_add_scenario_id(dom, root)

    # 添加ssd cache开关
    xml_add_eache_set(dom, root)

    # 添加机柜信息
    xml_add_cabinetinfo(dom, root)

    # 添加节点信息
    xml_add_nodeinfo(dom, root, node_id)

    # 添加网络检查
    check_network = make_text_tag(dom, 'check_network', '1')
    root.appendChild(check_network)

    # 写到xml文件中
    domcopy = dom.cloneNode(True)
    indent_xml(domcopy, domcopy.documentElement)
    config_file = '/tmp/deploy_config_sample_node1.xml'
    with open(config_file, 'wb') as f:
        # f = file(config_file, 'wb')
        domcopy.writexml(f, encoding='utf-8')
        domcopy.unlink()
    obj_node = common.Node()
    node_ip_lst = obj_node.get_nodes_ip()
    for node_ip in node_ip_lst:
        cmd = 'scp /tmp/deploy_config_sample_node1.xml root@%s:/tmp' % node_ip
        common.command(cmd)

    return config_file


def get_node_storage_pool_rel(node_id):
    """
    :author:        baoruobing
    :date  :        2018.08.11
    :description:   获取节点中所有磁盘的uuid和存储池id的关系
    :param node_id: 节点id
    :return:        (list)每一项都是列表，元素是磁盘的uuid和存储池的id,
                    [[uuid1, storage_pool_id1], [uuid2, storage_pool_id2]]
    """
    obj_disk = common.Disk()
    rc, node_disk_info = obj_disk.get_disk_info(node_id)
    common.judge_rc(rc, 0, 'get disks failed!!!')
    node_disk_info = common.json_loads(node_disk_info)
    disks_info = node_disk_info['result']['disks']
    relation_lst = []
    for disk_info in disks_info:
        if disk_info['usage'] != 'DATA' or disk_info['storagePoolId'] == 0:
            continue
        uuid = disk_info['uuid']
        storage_pool_id = disk_info['storagePoolId']
        lst = [uuid, storage_pool_id]
        relation_lst.append(lst)
    return relation_lst


def add_node_to_nodepool(node_pool_id, node_id):
    """
    :author:             baoruobing
    :date  :             2018.08.11
    :description:        将节点添加到节电池中
    :param node_pool_id: 节点池id
    :param node_id:      节点id
    :return:
    """
    obj_nodepool = common.Nodepool()
    node_pool_info = obj_nodepool.get_nodepool_info_by_id(node_pool_id)
    node_pool_info = common.json_loads(node_pool_info)
    node_id_lst = node_pool_info['result']['node_pools'][0]['node_ids'][:]
    node_pool_name = node_pool_info['result']['node_pools'][0]['name']

    node_id_lst.append(node_id)
    node_id_str = ','.join(map(str, node_id_lst))

    obj_nodepool.update_node_pool(node_pool_id, node_pool_name, node_id_str)
    return


def start_up_parastor():
    """
    :author:     baoruobing
    :date  :     2018.08.11
    :description:启动系统
    :return:
    """
    rc, stdout = common.startup()
    common.judge_rc(rc, 0, "start up failed!!!")
    return


def add_node_disks_to_storagepool(node_id, relation_lst):
    """
    :author:             baoruobing
    :date  :             2018.08.11
    :description:        添加一个节点中的所有磁盘到存储池中
    :param node_id:      (str)节点id
    :param relation_lst: (list)每一项都是列表，元素是磁盘的uuid和存储池的id
                         [[uuid1, storage_pool_id1], [uuid2, storage_pool_id2]]
    :return:
    """
    obj_disk = common.Disk()
    rc, node_disk_info = obj_disk.get_disk_info(node_id)
    common.judge_rc(rc, 0, "get disk failed!!!")
    node_disk_info = common.json_loads(node_disk_info)
    disks_info = node_disk_info['result']['disks']
    for disk_info in disks_info:
        for rel_tem in relation_lst:
            if disk_info['uuid'] == rel_tem[0]:
                rel_tem.append(disk_info['id'])
                break

    obj_storage_pool = common.Storagepool()
    for rel_tem in relation_lst:
        rc, stdout = obj_storage_pool.expand_storage_pool(rel_tem[1], rel_tem[2])
        common.judge_rc(rc, 0, "expand storage pool failed!!!")
    return




def command(cmd, node_ip=None, timeout=None):
    """
    执行shell命令
    """
    if node_ip:
        cmd1 = 'ssh %s "%s"' % (node_ip, cmd)
    else:
        cmd1 = cmd

    if timeout is None:
        process = subprocess.Popen(
            cmd1,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        output, unused_err = process.communicate()
        retcode = process.poll()
        return retcode, output
    else:
        result = [None, 0, "", "Timeout"]

        def target(result):
            p = subprocess.Popen(
                cmd1,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid)
            result[0] = p
            (result[2], result[3]) = p.communicate()
            result[1] = p.returncode

        thread = threading.Thread(target=target, kwargs={'result': result})
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            # Timeout
            p = result[0]
            wait_time = 5
            while p is None:
                time.sleep(1)
                p = result[0]
                wait_time -= wait_time
                if wait_time == 0:
                    print 'Create process for cmd %s failed.' % cmd
                    exit(1)
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            print 'Process %d is killed.' % p.pid
            thread.join()
        return result[1], result[2]



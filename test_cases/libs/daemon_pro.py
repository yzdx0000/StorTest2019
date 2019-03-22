#!/usr/bin/python
# -*- encoding=utf8 -*-

'''
:Author:Diws
:Data:20180904
:Description:守护进程
'''
import os
import commands
import ReliableTest
import logging
import time
import common2
import get_config
import log


conf_file = get_config.CONFIG_FILE
deploy_ips = get_config.get_env_ip_info(conf_file)
test_log_path = get_config.get_testlog_path()
type_info = get_config.get_machine_type(conf_file)
current_path_1 = os.path.dirname(os.path.abspath(__file__))


ipmi_ip = {}
vmid = {}
#获取所有节点IPMI IP或节点vmid


def get_machine_info():
    '''
    :Author:Diws
    :Date:20180904
    :Description:获取机器的impi地址或者vmid
    :return: dict，key:value :: deploy_ip:impi/vmid
    '''
    if type_info == 'phy':
        for ip in deploy_ips:
            ipmi_ip[ip] = ReliableTest.get_ipmi_ip(ip)
        return ipmi_ip
    else:
        (esxi_ip, esxi_un, esxi_pw) = get_config.get_esxi(conf_file)
        cmd_str = ("vim-cmd vmsvc/getallvms")
        cmd = ("%s/expect %s %s \"%s\" \"%s\" | awk '{print $1}' | grep -v -E [a-zA-Z].*"
               % (current_path_1, esxi_ip[0], esxi_un[0], esxi_pw[0], cmd_str))
        stdout = commands.getoutput(cmd)
        vmid_list = stdout.split('\n')
        vmid_dic = {}
        for vm_id in vmid_list:
            cmd_str = ("vim-cmd vmsvc/device.getdevices %s" % vm_id)
            cmd = ("%s/expect %s %s \"%s\" \"%s\"" % (current_path_1, esxi_ip[0], esxi_un[0], esxi_pw[0], cmd_str))
            vm_info = commands.getoutput(cmd)
            vmid_dic[vm_id] = vm_info
        for node_ip in deploy_ips:
            cmd1 = ("ssh %s \"ifconfig | grep -A 3 %s | grep ether | awk '{print \$2}'\"" % (node_ip, node_ip))
            rc, stdout = commands.getstatusoutput(cmd1)
            if 0 != rc:
                logging.error("Can not connect to the node.")
                exit(1)
            else:
                mac_addr = stdout
                for key in vmid_dic:
                    if mac_addr in vmid_dic[key]:
                        vmid[node_ip] = key
        print vmid
        return vmid


def restart_node(m_info=None):
    '''
    :Author:Diws
    :Date:20180904
    :Description:遍历所有节点，当该节点IP不通时，等待120s（避免正在出crash），然后强制重启该节点
    :param m_info: ipmi或vmid
    :return: None
    '''
    for ip in deploy_ips:
        if ReliableTest.check_ping(ip) == False:
            if type_info == 'phy':
                for i in range(3):
                    print "Begin down node %s through %s" % (ip, m_info[ip])
                    if False == ReliableTest.run_down_node(m_info[ip]):
                        print ("node %s down failed!!!" % ip)
                    else:
                        break
                time.sleep(30)
                for i in range(3):
                    print "Begin up node %s through %s" % (ip, m_info[ip])
                    if False == ReliableTest.run_up_node(m_info[ip]):
                        print ("%s up failed!!!" % (ip))
                    else:
                        break
            else:
                print "Begin down node %s through %s" % (ip, m_info[ip])
                (esxi_ip, esxi_un, esxi_pw) = get_config.get_esxi(conf_file)
                ReliableTest.run_down_vir_node(esxi_ip=esxi_ip[0], u_name=esxi_un[0], pw=esxi_pw[0], vm_id=m_info[ip])
                time.sleep(30)
                print "Begin up node %s through %s" % (ip, m_info[ip])
                ReliableTest.run_up_vir_node(esxi_ip=esxi_ip[0], u_name=esxi_un[0], pw=esxi_pw[0], vm_id=m_info[ip])


def pro_kill(pname, elapse):
    '''
    :Author:Diws
    :Date:20180904
    :Description:根据fname（脚本名）查询该脚本是否正在运行，如果在指定时间内结束，则正常退出，否则，强制将该进程杀掉
    :param fname:
    :return:
    '''
    pname = str(pname).split('/')[-1]
    cmd = (" ps aux |grep -v grep | grep %s | awk '{print $2}'" % (pname))
    res, pro_pid = commands.getstatusoutput(cmd)
    while pro_pid == '':
        res, pro_pid = commands.getstatusoutput(cmd)
    wait_num = 0
    while pro_pid != '':
        res, pro_pid = commands.getstatusoutput(cmd)
        time.sleep(2)
        wait_num += 1
        if wait_num == elapse/2:
            file_name = os.path.basename(__file__)
            file_name = file_name[:-3]
            log_file_path = log.get_log_path(file_name)
            log.init(log_file_path, True)
            cmd = ("kill -9 %s" % (str(pro_pid)))
            log.info("kill %s : %s" % (pname, cmd))
            print ("kill %s -- %s" % (pname, str(pro_pid)))
            commands.getstatusoutput(cmd)
            return
    return



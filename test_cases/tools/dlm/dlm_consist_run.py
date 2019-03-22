#!/usr/bin/python
#-*-coding:utf-8-*-

################################################################################
#                                                                              #
#        Copyright (C), 1995-2014, Sugon Information Industry Co., Ltd.        #
#                                                                              #
################################################################################
# File Name     : tc_run.py                                                    #
# Module Name   : Testing Framework                                            #
# Version       : 1.0.0                                                        #
# Author        : Zhang Jianbin <zhangjb@sugon.com>                            #
# Created Date  : 2014/05/05                                                   #
# Description   : Run DLM's system test                                        #
#                                                                              #
# History       :                                                              #
# 1.Date         : 2014/05/05                                                  #
#   Author       : Zhang Jianbin <zhangjb@sugon.com>                           #
#   Modification : Creating file                                               #
#                                                                              #
################################################################################
import commands, os, sys, string, ConfigParser,subprocess, time, json
import xml.etree.ElementTree as ET
sys.path.append('.')
from common.dlm_print import *
from common.dlm_lib import *
from common.dlm_config import *

#获取当前脚本路径
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))


MAX_NP = 12
VERSION = ''
MGRIP = ''
HMOSIP = ''
CLICNT = 0
MPINP = 1
ST_CONFIG_FILE = os.path.join(ROOT_DIR, 'bin', 'st_config')
NODES_FILE = os.path.join(ROOT_DIR, 'bin', 'nodes.xml')
CLIENTS_FILE = os.path.join(ROOT_DIR, 'bin', 'clients.xml')
NODES_CONFIG = os.path.join(ROOT_DIR, 'bin', 'nodes_config')
G_OPARAS = []
G_OSTORS = []
G_CLIENTS = []
G_MAX_FILE_NUM = ''
G_MAX_SUB_FILE_NUM = ''
G_MAX_BUF_CNT = ''
G_CLIENT_DIR = ''

# clean st
'''************************* common functions *************************'''

def dlm_st_consist_test_run():
    global CLICNT
    global MPINP
    global G_MAX_FILE_NUM
    global G_MAX_SUB_FILE_NUM
    global G_MAX_BUF_CNT
    global G_CLIENT_DIR
    global VERSION
    failed = 0

    np = MPINP * string.atoi(CLICNT)
    run_cmd = 'mpirun -np ' + str(np) + ' --allow-run-as-root --machinefile ' \
              + ROOT_DIR + '/bin/machines ' + ROOT_DIR + '/bin/dlm_consist -f ' \
              + G_MAX_FILE_NUM + ' -s ' + G_MAX_SUB_FILE_NUM + ' -b ' \
              + G_MAX_BUF_CNT + ' -c ' + CLICNT + ' -p ' + G_CLIENT_DIR + '/'

    print_beauty(run_cmd)
    print_beauty('Run ST Begin')
    subp = subprocess.Popen(run_cmd, shell=True, stdout=subprocess.PIPE)
    c = subp.stdout.readline()
    while c:
        if c.find('Failed') > 0:
            print_beauty('Run ST FAILED')
            dlm_log_append(c)
            failed = 1

        print_beauty(c.strip("\r\n"))
        c = subp.stdout.readline()

    if (failed > 0):
        dlm_log_append('\nRun ST FAILED\n')

    if 'P200' == VERSION:
        failed = dlm_check_cores()
        if failed == 1:
            sys.exit(-1)
    elif 'P300' == VERSION:
        cmd = "python ./bin/check_core.py"
        rc, output = commands.getstatusoutput(cmd)
        if 0 != rc:
            sys.exit(-1)

    return 0

def dlm_st_consist_read_config(filename):
    cf = ConfigParser.ConfigParser()
    try:
        cf.read(filename)
    except:
        print_beauty('Read config file FAILED')
        dlm_log_append('Read config file FAILED\n')
    return cf

def dlm_st_consist_get_mgrip():
    global VERSION
    global MGRIP
    global MPINP
    global G_MAX_FILE_NUM
    global G_MAX_SUB_FILE_NUM
    global G_MAX_BUF_CNT
    global G_CLIENT_DIR


    ret = -1
    cf = dlm_st_consist_read_config(ST_CONFIG_FILE)
    sections = cf.sections()
    for section in sections:
        if section == 'parastor':
            VERSION = cf.get(section, 'version')
            MGRIP = cf.get(section, 'mgrip')
            MPINP = cf.getint(section, 'mpinp')
            G_MAX_FILE_NUM = cf.get(section, 'filenum')
            G_MAX_SUB_FILE_NUM = cf.get(section, 'subfilenum')
            G_MAX_BUF_CNT = cf.get(section, 'bufcnt')
            G_CLIENT_DIR = cf.get(section, 'client_dir')
            print_beauty('Get MGRIP(%s) MPINP(%d) Success' %(MGRIP, MPINP))
            return 0
    return ret

def dlm_add_section_nodes_config(cf, section):
    cf.add_section(section)

def dlm_save_nodes_config(cf, section, key, value):
    cf.set(section, key, value)

'''************************* P200 functions *************************'''

def dlm_st_do_add_group(ip, group, id):
    cmd = 'ssh ' + ip + ' groupadd ' + group + ' -g ' + str(id)
    os.system(cmd)


def dlm_st_do_add_user(ip, user, group, id):
    cmd = 'ssh ' + ip + ' useradd ' + user + ' -u ' + str(id) + ' -g ' + group
    os.system(cmd)


def dlm_st_group_exist(ip, group):
    cmd = 'ssh ' + ip + ' grep ' + group + ' /etc/group > /dev/null; echo $?'
    (ret, output) = commands.getstatusoutput(cmd)
    if output == '0':
        return 1

    return 0


def dlm_st_user_exist(ip, user):
    cmd = 'ssh ' + ip + ' grep ' + user + ' /etc/passwd > /dev/null; echo $?'
    (ret, output) = commands.getstatusoutput(cmd)
    if output == '0':
        return 1

    return 0


def __dlm_st_add_user(ip):
    global CLICNT

    group = 'dlm_group'
    id = 2000
    user = 'dlm_user'

    for i in range(string.atoi(CLICNT)):
        t_group = group + str(i)
        t_id = id + i

        t_user = user + str(i)
        if dlm_st_group_exist(ip, t_group) == 1:
            continue
        dlm_st_do_add_group(ip, t_group, t_id)

        if dlm_st_user_exist(ip, t_user) == 1:
            continue
        dlm_st_do_add_user(ip, t_user, t_group, t_id)


def dlm_st_add_user():
    for client in G_CLIENTS:
        if client[1] <= 2:
            continue
        __dlm_st_add_user(client[6])


def dlm_st_cp_reboot():
    for opara in G_OPARAS:
        cmd = 'scp ' + ROOT_DIR + '/bin/reboot.py ' + opara[6] + ':/home/ > /dev/null'
        os.system(cmd)

    for ostor in G_OSTORS:
        cmd = 'scp ' + ROOT_DIR + '/bin/reboot.py ' + ostor[6] + ':/home/ > /dev/null'
        os.system(cmd)


def dlm_st_consist_uncompress():
    os.system('rm -rf ' + ROOT_DIR + '/mos*')
    os.system('rm -rf ' + ROOT_DIR + '/ds*')


def dlm_clean_st():
    return

def dlm_do_check_core(ip):
    cmd = 'ssh ' + ip + ' ls /home/parastor/log/core*'
    (ret, output) = commands.getstatusoutput(cmd)
    if ret == 0:
        print_beauty('consist test FAILED, check core in %s' %ip)
        dlm_log_append('CHECK ST consist test FAILED\n')
        return 1
    else:
        return 0
         
def dlm_check_cores():
    global G_OPARAS
    global G_OSTORS

    for opara in G_OPARAS:
        rc = dlm_do_check_core(opara[6])
        if rc == 1:
            return rc
    

    for ostor in G_OSTORS:
        rc = dlm_do_check_core(ostor[6])
        if rc == 1:
            return rc

def dlm_st_consist_test_clicnt():
    global CLICNT
    cmd = 'wc ' + ROOT_DIR + '/bin/machines -l | awk \'{print $1}\''
    (ret, output) = commands.getstatusoutput(cmd)
    if ret != 0:
        print_beauty('Find cli cnt FAILED')
        dlm_log_append('Find cli cnt FAILED\n')
	return ret
    else:
        print_beauty('Find cli cnt(%s)Success' %(output))

    CLICNT = output
        
    return ret

def dlm_st_consist_get_hmosip():
    global HMOSIP
    global MGRIP
    cmd = 'ssh '+ MGRIP + ' " /home/parastor/bin/parastor_sysctl getip NODETYPE=oPara NODEID=1" | awk -F# \'{print $3}\' | awk -F: \'{print $2}\''
    (ret, output) = commands.getstatusoutput(cmd)
    if ret != 0:
        print_beauty('Get HMOSIP FAILED')
        dlm_log_append('Get HMOSIP FAILED\n')
	return ret
    else:
        print_beauty('Get HMOSIP(%s) Success' %output)

    HMOSIP = output
    return ret

def dlm_get_eth(ctlip, ip):
    cmd = 'ssh ' + ctlip + ' "/usr/bin/tac /etc/sysconfig/network-scripts/ifcfg-eth* | grep -E \'DEVICE|IPADDR\' "' + \
          ' | sed \'N;s/\\n/ /\' | sed \'s/=/:/g\' | sed \'s/ /:/g\'| sed \'s/"//g\' |awk -F: \'{print $2,$4}\' | grep ' + \
          ip + ' | awk \'{print $2}\''
    (ret, output) = commands.getstatusoutput(cmd)
    if ret != 0:
        print_beauty('Get ETH FAILED')
        dlm_log_append('Get ETH FAILED\n')
	return ret
    
    return output

def dlm_handle_ctlip(ctlip, cf, section, tmp, list):
    list.append(ctlip)
    dlm_save_nodes_config(cf, section, 'ctl_ip_' + str(tmp), ctlip)
    eth = dlm_get_eth(ctlip, ctlip)
    list.append(eth)
    dlm_save_nodes_config(cf, section, 'ctl_eth_' + str(tmp), eth)

def dlm_handle_dataip(ctlip, dip, cf, section, tmp, list):
    list.append(dip)
    dlm_save_nodes_config(cf, section, 'data_ip_' + str(tmp), dip)
    eth = dlm_get_eth(ctlip, dip)
    list.append(eth)
    dlm_save_nodes_config(cf, section, 'data_eth_' + str(tmp), eth)

def dlm_handle_haip(ctlip, haip, cf, section, tmp, list):
    list.append(haip)
    dlm_save_nodes_config(cf, section, 'ha_ip_' + str(tmp), haip)
    eth = dlm_get_eth(ctlip, haip)
    list.append(eth)
    dlm_save_nodes_config(cf, section, 'ha_eth_' + str(tmp), eth)

def dlm_fake_ip(ip):
    tip = ip.split(".", 1)
    for t in tip:
        if t.find('.') >= 0:
            continue
        else:
            t_int = int(t, 16)
            t_int = t_int + int('10', 16)
            t_hex = hex(t_int)
            break
    ret = t_hex[2:] + '.' + tip[1]
    return ret

def dlm_fake_haip(dip, ctlip, cf, section, tmp, list):
    haip = dlm_fake_ip(dip)
    dlm_handle_haip(ctlip, haip, cf, section, tmp, list)
    return haip

def dlm_fake_dataip(ctlip, cf, section, tmp, list):
    dip = dlm_fake_ip(ctlip)
    dlm_handle_dataip(ctlip, dip, cf, section, tmp, list)
    dlm_fake_haip(dip, ctlip, cf, section, tmp, list)

def dlm_find_oparas(root, cf):
    cnt = 0
    for oPara in root.getiterator('oPara'):
        for node in oPara.getiterator('node'):
            list = 'a_' + str(cnt)
            list = []
            list.append('oPara')
            id = string.atoi(node.find('id').text)
            list.append(id)
            section = 'oPara_' + node.find('id').text
            dlm_add_section_nodes_config(cf, section)
            dlm_save_nodes_config(cf, section, 'id', id)
            tmp = 0
            for ctlips in node.getiterator('ctlips'):
                ctlip = ctlips.find('ctlip').text
                dlm_handle_ctlip(ctlip, cf, section, tmp, list)
                tmp = tmp + 1

            tmp = 0
            for dataip in node.getiterator('dataip'):
                for ip in dataip.getiterator('ip'):
                    dip = ip.find('addr').text
                    dlm_handle_dataip(ctlip, dip, cf, section, tmp, list)
                    tmp = tmp + 1

            tmp = 0
            for ha in node.getiterator('HA'):
                for ip in ha.getiterator('ip'):
                    haip = ip.find('addr').text
                    dlm_handle_haip(ctlip, haip, cf, section, tmp, list)
                    tmp = tmp + 1
            G_OPARAS.append(list)

            cnt = cnt + 1

    for opara in G_OPARAS:
        print_beauty(opara)

def dlm_handle_ostor_disks(nodeid, cf, section, ctlip):
    cnt = 0
    cmd = 'ssh ' + MGRIP + ' /home/parastor/bin/sysctl/parastor_monitor checknodeperf nodetype=oStor nodeid=' + nodeid +  \
          '| grep diskclass:Stor | awk -F# \'{print $4}\' | awk -F: \'{print $2}\''
    (ret, output) = commands.getstatusoutput(cmd)
    if ret != 0:
        print_beauty('Get oStor disks FAILED')
        dlm_log_append('Get oStor disks FAILED\n')
        return ret
    
    disks = output.split()
    for disk in disks:
        cf.set(section, 'disk_' + str(cnt), disk)
        cmd = 'ssh ' + ctlip + ' ls /sys/block/' + disk[5:] + '/device/scsi_disk/'
        (ret, output) = commands.getstatusoutput(cmd)
        if ret != 0:
            print_beauty('Get oStor disks FAILED')
            dlm_log_append('Get oStor disks FAILED\n')
            return ret
        else:
            cf.set(section, 'disk_desc_' + str(cnt), output)
        cnt = cnt + 1
        
    return output
    

def dlm_find_ostors(root, cf):
    cnt = 0
    for oStor in root.getiterator('oStor'):
        for node in oStor.getiterator('node'):
            list = 'a_' + str(cnt)
            list = []
            list.append('oStor')
            id_str = node.find('id').text
            id = string.atoi(id_str)
            section = 'oStor_' + id_str
            dlm_add_section_nodes_config(cf, section)
            list.append(id)
            dlm_save_nodes_config(cf, section, 'id', id)
            tmp = 0
            for ctlips in node.getiterator('ctlips'):
                ctlip = ctlips.find('ctlip').text
                dlm_handle_ctlip(ctlip, cf, section, tmp, list)
                tmp = tmp + 1

            tmp = 0
            for dataip in node.getiterator('dataip'):
                for dataip in node.getiterator('dataip'):
                    for ip in dataip.getiterator('ip'):
                        dip = ip.find('addr').text
                        dlm_handle_dataip(ctlip, dip, cf, section, tmp, list)
                        dlm_fake_haip(dip, ctlip, cf, section, tmp, list)
                        tmp = tmp + 1
            G_OSTORS.append(list)
            dlm_handle_ostor_disks(id_str, cf, section, ctlip)

            cnt = cnt + 1

    for ostor in G_OSTORS:
        print_beauty(ostor)

def dlm_find_clients_P200(root, cf):
    cnt = 0

    for client in root.getiterator('client'):
        list = 'a_' + str(cnt)
        list = []
        list.append('oApp')
        id = string.atoi(client.find('id').text)
        section = 'oApp_' + client.find('id').text
        dlm_add_section_nodes_config(cf, section)
        list.append(id)
        dlm_save_nodes_config(cf, section, 'id', id)
        tmp = 0
        for ctlips in client.getiterator('ctlips'):
            ctlip = ctlips.find('ctlip').text
            dlm_handle_ctlip(ctlip, cf, section, tmp, list)
            dlm_fake_dataip(ctlip, cf, section, tmp, list)
            tmp = tmp + 1
        G_CLIENTS.append(list)

        cnt = cnt + 1

    for client in G_CLIENTS:
        print_beauty(client)

def dlm_find_nodes_P200(cf):
    global MGRIP
    os.system('scp root@' + MGRIP + ':/home/parastor/conf/xml/nodes.xml ' + ROOT_DIR + '/bin/ > /dev/null')
    os.system('scp root@' + MGRIP + ':/home/parastor/conf/xml/clients.xml ' + ROOT_DIR + '/bin/ > /dev/null')
    node_tree = ET.parse(NODES_FILE)
    node_root = node_tree.getroot()

    client_tree = ET.parse(CLIENTS_FILE)
    client_root = client_tree.getroot()

    dlm_find_oparas(node_root, cf)
    dlm_find_ostors(node_root, cf)
    dlm_find_clients_P200(client_root, cf)

'''************************* P300 functions *************************'''
def dlm_get_eth_P300(ctlip, ip):
    cmd = 'ssh %s "ip addr | grep %s"' %(ctlip, ip)
    (ret, output) = commands.getstatusoutput(cmd)
    if ret != 0:
        print_beauty('Get ETH FAILED')
        dlm_log_append('Get ETH FAILED\n')
        return None
    else:
        eth_name = output.split()[-1]
        return eth_name

def dlm_config_ctlip_P300(ctlip, cf, section, tmp):
    dlm_save_nodes_config(cf, section, 'ctl_ip_' + str(tmp), ctlip)
    eth = dlm_get_eth_P300(ctlip, ctlip)
    dlm_save_nodes_config(cf, section, 'ctl_eth_' + str(tmp), eth)

def dlm_config_dataip_P300(ctlip, dataip, cf, section, tmp):
    dlm_save_nodes_config(cf, section, 'data_ip_' + str(tmp), dataip)
    eth = dlm_get_eth_P300(ctlip, dataip)
    dlm_save_nodes_config(cf, section, 'data_eth_' + str(tmp), eth)

def dlm_find_parastor_nodes_P300(cf):
    global MGRIP

    cmd = "ssh %s pscli --command=get_nodes" %MGRIP
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        print_beauty("get_nodes failed!!!")
        sys.exit(-1)

    result = json_loads(stdout)
    nodes_info = result['result']['nodes']

    for node_info in nodes_info:
        section = 'node_' + str(node_info['node_id'])
        dlm_add_section_nodes_config(cf, section)
        dlm_save_nodes_config(cf, section, 'id', node_info['node_id'])
        tmp = 0
        ctl_ips = node_info['ctl_ips']
        for ctl_ip_info in ctl_ips:
            ctl_ip = ctl_ip_info['ip_address']
            dlm_config_ctlip_P300(ctl_ip, cf, section, tmp)
            tmp += 1

        tmp = 0
        data_ips = node_info['data_ips']
        for data_ip_info in data_ips:
            data_ip = data_ip_info['ip_address']
            dlm_config_dataip_P300(ctl_ip, data_ip, cf, section, tmp)
            tmp += 1

        flag = False
        services = node_info['services']
        for service in services:
            if service['service_type'] == 'oJmgs':
                flag = True
                break
        if False == flag:
            dlm_save_nodes_config(cf, section, 'MGR_node', 'no')
        else:
            dlm_save_nodes_config(cf, section, 'MGR_node', 'yes')

    return

def dlm_find_clients_P300(cf):
    global MGRIP

    cmd = "ssh %s pscli --command=get_clients" % MGRIP
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        print_beauty("get_nodes failed!!!")
        sys.exit(-1)

    result = json_loads(stdout)
    clients_info = result['result']
    cnt = 0
    for client_info in clients_info:
        if client_info['inTimeStatus'] == 'SERV_STATE_OK':
            section = 'client_' + str(cnt)
            cnt += 1
            dlm_add_section_nodes_config(cf, section)

            ctl_ip = client_info['ip']
            dlm_config_ctlip_P300(ctl_ip, cf, section, '0')

            id = client_info['node_id']
            dlm_save_nodes_config(cf, section, 'id', id)

    return

def dlm_find_nodes_P300(cf):
    dlm_find_parastor_nodes_P300(cf)
    dlm_find_clients_P300(cf)
    return

'''************************* common functions *************************'''

def json_loads(stdout):
    try:
        stdout = stdout.replace('\\', '')
        stdout_str = json.loads(stdout, strict=False)
        return stdout_str
    except:
        print stdout
    return


def dlm_st_consist_get_env():
    global VERSION
    ret = dlm_st_consist_get_mgrip()
    if ret != 0:
        return ret

    os.system('rm -rf ' + NODES_CONFIG)
    os.system('touch ' + NODES_CONFIG)
    if VERSION == 'P200':
        cf = dlm_st_consist_read_config(NODES_CONFIG)
        dlm_find_nodes_P200(cf)
        cf.write(open(NODES_CONFIG, "w"))
    elif VERSION == 'P300':
        cf = dlm_st_consist_read_config(NODES_CONFIG)
        dlm_find_nodes_P300(cf)
        cf.write(open(NODES_CONFIG, "w"))
        print_beauty("config get_nodes finished!!!")
    else:
        print_beauty("st_config's version is error!!! please input P200 or P300")
        sys.exit(-1)
    return ret

def dlm_st_consist_init():
    #dlm_st_consist_uncompress()

    ret = dlm_st_consist_test_clicnt()
    if ret < 0:
        return ret

    ret = dlm_st_consist_get_env()
    if ret != 0:
        return ret


    #dlm_st_add_user()
    #dlm_st_cp_reboot()

    return ret
    
def dlm_exec_st_consist_test():
    ret = dlm_st_consist_init()
    if ret != 0:
        return ret 
    ret = dlm_st_consist_test_run()
    return ret

def dlm_exec_st_test():
    print_a_hash_line()
    time = commands.getoutput('date')
    print_beauty('ALL System Testcases Start(' + time + ')')

    dlm_exec_st_consist_test()

    print_a_hash_line()
    time = commands.getoutput('date')
    print_beauty('All System Testcases Passed'+ '(' + time + ')')
    print_a_hash_line()

def main():
    dlm_exec_st_test()

if __name__ == '__main__':
    main()

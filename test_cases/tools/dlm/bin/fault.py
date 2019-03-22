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
# Description   : Run testcases of DLM                                         #
#                                                                              #
# History       :                                                              #
# 1.Date         : 2014/05/05                                                  #
#   Author       : Zhang Jianbin <zhangjb@sugon.com>                           #
#   Modification : Creating file                                               #
#                                                                              #
################################################################################
import commands, os, sys, string, getopt, ConfigParser, time

ROOT_DIR = '/mnt/parastor/'
g_node_config = ROOT_DIR + 'bin/nodes_config'
g_st_config = ROOT_DIR + 'bin/st_config'
g_opara_log_path = '/home/parastor/log/'
g_opara_log_name = ['oPara.log_0', 'oPara.log_1']
g_nodetypes = ['oPara', 'oStor', 'oApp']
g_nettypes = ['ctl', 'data', 'net']
g_hmgr_ip = ''
g_smgr_ip = ''
g_mgr_ip = ''
g_hmgr_hopara_share = 0
g_smgr_gopara_share = 0

def dlm_clean_opara_log(ip):
    return

    cmd = 'ssh ' + ip + ' ls ' + g_opara_log_path
    (ret, output) = commands.getstatusoutput(cmd)
    if ret != 0:
        print("Failed to get log files, err%d" %ret)
        return
    list = output.split()
    for l in list:
        cmd = 'ssh ' + ip + ' "echo > ' + g_opara_log_path + l + '"'
        os.system(cmd)

def dlm_read_config(filename):
    cf = ConfigParser.ConfigParser()
    try:
        cf.read(filename)
    except:
        print("Read config file %s FAILED" %(filename))
    return cf

def dlm_find_section(cf, nodetype, nodeid):
    for section in cf.sections():
        if section.find(nodetype) < 0:
            continue
        if cf.getint(section, 'id') != nodeid:
            continue
        else:
            return section
    return 0

def dlm_get_haip(cf, nodetype, nodeid):
    ip = ''
    section = dlm_find_section(cf, nodetype, nodeid)
    if section == 0:
        return ip
    ip = cf.get(section, 'ha_ip_0')
    #print("Get node(%s:%d) HAIP:%s" %(nodetype, nodeid, ip))
    return ip

def dlm_get_cmgrip():
    ip = ''
    cf = dlm_read_config(g_st_config)
    for section in cf.sections():
        if section == 'parastor':
            ip = cf.get(section, 'cmgrip')
            break
    #print("Get Cur_MGR_IP:%s" %(ip))
    return ip

def dlm_set_cmgrip(cmgrip):
    cf = dlm_read_config(g_st_config)
    for section in cf.sections():
        if section == 'parastor':
            cf.set(section, 'cmgrip', cmgrip)
            cf.write(open(g_st_config, "w"))

def dlm_change_cmgrip(nodetype, nodeid):
    if nodetype == 'oPara' and nodeid == 1:
        dlm_set_cmgrip(g_smgr_ip)
        print("change to %s" %g_smgr_ip)
    if nodetype == 'oPara' and nodeid == 2:
        dlm_set_cmgrip(g_hmgr_ip)
        print("change to %s" %g_hmgr_ip)

def dlm_check_status(cmd, desc):
    print cmd
    list = desc.split('|')
    print list
    while (1):
        found = 0
        (ret, output) = commands.getstatusoutput(cmd)
        if ret != 0:
            print('Failed to get output, cmd %s' %(cmd))
            continue
        else:
            #print("get:%s, expected:%s" %(output, desc))
            for l in list:
                if output == l:
                    found = 1
                    break
            if found == 1:
                break
            else:
                time.sleep(3)
                continue

def dlm_check_mgr_net_updown(nodeid, net, isdown):
    global g_hmgr_hopara_share
    global g_smgr_gopara_share
    ip = dlm_get_cmgrip()

    if isdown == 1 or g_hmgr_hopara_share == 0 or g_smgr_gopara_share == 0 :
        return
    
    cmd = 'ssh ' + ip + ' /home/parastor/bin/sysctl/parastor_monitor checkstat '\
          '| grep MGR | grep nodeid:' + str(nodeid) + ' | awk -F# \'{print $3}\' | awk -F: \'{print $2}\''

    dlm_check_status(cmd, 'mgsha_standby')
    
    cmd = 'ssh ' + ip + ' /home/parastor/bin/sysctl/parastor_monitor checkstat '\
          '| grep MGR | grep nodeid:' + str(nodeid) + ' | awk -F# \'{print $4}\' | awk -F: \'{print $2}\''

    dlm_check_status(cmd, 'ok')

def dlm_check_opara_net_updown(nodeid, net, isdown):
    ip = dlm_get_cmgrip()

    if net == 'ctl':
        if isdown == 1:
            desc = 'abnormal'
        else:
            desc = 'ok'
        cmd = 'ssh ' + ip + ' /home/parastor/bin/sysctl/parastor_monitor checkstat '\
              '| grep oPara | grep nodeid:' + str(nodeid) +' | awk -F# \'{print $5}\' | awk -F: \'{print $2}\''

        dlm_check_status(cmd, desc)
        dlm_check_mgr_net_updown(nodeid, net, isdown) 
    elif net == 'data':
        if isdown == 1:
            if nodeid == 0:
                desc = 'shutdown'
            else:
                desc = 'takeover'
        else:
            desc = 'ok'
        cmd = 'ssh ' + ip + ' /home/parastor/bin/sysctl/parastor_monitor checkstat '\
              '| grep mosgrp | head -n 1 | awk -F# \'{print $3}\' | awk -F: \'{print $2}\''

        dlm_check_status(cmd, desc)
    else:
        print("No check nodetype:%s, nodeid:%d, net:%s, isdown:%d" %(nodetype, nodeid, net, isdown))

def dlm_check_oapp_net_updown(nodeid, net, isdown):
    if isdown == 0:
        time.sleep(5)

def dlm_check_ostor_net_updown(nodeid, net, isdown):
    if isdown == 0:
        time.sleep(5)

def dlm_check_net_updown(nodetype, nodeid, net, isdown):
    if nodetype == 'oPara':
        dlm_check_opara_net_updown(nodeid, net, isdown)
    elif nodetype == 'oApp':
        dlm_check_oapp_net_updown(nodeid, net, isdown)  
    elif nodetype == 'oStor':
        dlm_check_ostor_net_updown(nodeid, net, isdown)

def __dlm_do_handle_ifdown(cf, nodetype, nodeid, net):
    global g_mgr_ip

    ip = dlm_get_cmgrip()

    section = dlm_find_section(cf, nodetype, nodeid)
    if section == 0:
        return section
    ha_ip = cf.get(section, 'ha_ip_0')
    net_ip = cf.get(section, net + '_ip_0')
    eth = cf.get(section, net + '_eth_0')
    cmd = 'ssh ' + ha_ip + ' ifconfig %s down' % eth
    print("CMD: %s(%s)" %(cmd, net_ip))
    os.system(cmd)
    if net == 'ctl' and ip == ha_ip:
        dlm_change_cmgrip(nodetype, nodeid)

def dlm_do_handle_ifdown(cf, nodetype, nodeid, net, ischeck):
    if nodeid == 0:
        tid = 1
        while(1):
            ret = __dlm_do_handle_ifdown(cf, nodetype, tid, net)
            if ret == 0:
                break
            tid += 1
    
        if ischeck == 1:
            dlm_check_net_updown(nodetype, nodeid, net, 1)
    else:
        __dlm_do_handle_ifdown(cf, nodetype, nodeid, net)
        if ischeck == 1:
            dlm_check_net_updown(nodetype, nodeid, net, 1)

def dlm_handle_ifdown(cf, nodetype, nodeid, net):
    if net == "net":
        for i in range(len(g_nettypes) - 1):
            tmp_net = g_nettypes[i]
            dlm_do_handle_ifdown(cf, nodetype, nodeid, tmp_net, 0)
        dlm_check_net_updown(nodetype, nodeid, 'ctl', 1)
    else:
        dlm_do_handle_ifdown(cf, nodetype, nodeid, net, 1)

def __dlm_do_handle_ifup(cf, nodetype, nodeid, net):
    section = dlm_find_section(cf, nodetype, nodeid)
    if section == 0:
        return section
    ha_ip = cf.get(section, 'ha_ip_0')
    net_ip = cf.get(section, net + '_ip_0')
    eth = cf.get(section, net + '_eth_0')
    cmd = 'ssh ' + ha_ip + ' ifconfig %s up' % eth
    print("CMD: %s(%s)" %(cmd, net_ip))
    os.system(cmd)

def dlm_do_handle_ifup(cf, nodetype, nodeid, net, ischeck):
    if nodeid == 0:
        tid = 1
        while(1):
            ret = __dlm_do_handle_ifup(cf, nodetype, tid, net)
            if ret == 0:
                break
            tid += 1
        if ischeck == 1:
            dlm_check_net_updown(nodetype, nodeid, net, 0)
    else:
        __dlm_do_handle_ifup(cf, nodetype, nodeid, net)
        if ischeck == 1:
            dlm_check_net_updown(nodetype, nodeid, net, 0)

def dlm_handle_ifup(cf, nodetype, nodeid, net):
    if net == 'net':
        for i in range(len(g_nettypes) - 1):
            tmp_net = g_nettypes[i]
            dlm_do_handle_ifup(cf, nodetype, nodeid, tmp_net, 0)
        dlm_check_net_updown(nodetype, nodeid, 'ctl', 0)
    else:
        dlm_do_handle_ifup(cf, nodetype, nodeid, net, 1)

def __dlm_check_kill_opara(cf, nodetype, nodeid):
    global g_opara_log_name
    found = 0

    ha_ip = dlm_get_haip(cf, nodetype, nodeid)
    if ha_ip == '':
        return 0

    while(1):
        for name in g_opara_log_name:
            cmd = 'ssh ' + ha_ip + ' grep \\"Recov finished\\" ' + g_opara_log_path + name
            #print("check kill opara:%s" %(cmd))
            (ret, output) = commands.getstatusoutput(cmd)
            if ret != 0:
                time.sleep(1)
                continue
            else:
                found = 1
                break
        if found == 1:
            break
    cmd = 'ssh ' + ha_ip + ' "echo > "' + g_opara_log_path + name
    #print("clean up opara log:%s" %(cmd))
    os.system(cmd)

def dlm_check_kill_opara(cf, nodetype, nodeid):
    if nodeid == 0:
        tid = 1
        while(1):
            ret = __dlm_check_kill_opara(cf, nodetype, tid)
            if ret == 0:
                break
            tid += 1
    else:
        ret = __dlm_check_kill_opara(cf, nodetype, nodeid)

def dlm_check_kill_ostor(cf, nodetype, nodeid):
    print("Kill ostor")
    ip = dlm_get_cmgrip()
    
    time.sleep(10)
    cmd = 'ssh ' + ip + ' /home/parastor/bin/sysctl/parastor_monitor checkstat '\
          '| grep oStor | grep nodeid:' + str(nodeid) + ' | awk -F# \'{print $4}\' | awk -F: \'{print $2}\''

    dlm_check_status(cmd, 'shutdown')
    dlm_check_status(cmd, 'ok')
    
    cmd = 'ssh ' + ip + ' /home/parastor/bin/sysctl/parastor_monitor checkperf '\
          '| grep parastor_bad_objs | awk -F# \'{print $3}\' | awk -F: \'{print $2}\''

    dlm_check_status(cmd, '0')


def dlm_check_kill(cf, nodetype, nodeid):
    if nodetype == 'oPara':
        dlm_check_kill_opara(cf, nodetype, nodeid)
    elif nodetype == 'oStor':
        dlm_check_kill_ostor(cf, nodetype, nodeid)
    else:
        sys.exit(-1)

def dlm_find_kill_service(nodetype):
    if nodetype == 'oPara':
        service = 'oPara'
    elif nodetype == 'oStor':
        service = 'oStor'
    else:
        sys.exit(-1)

    return service

def __dlm_handle_kill(cf, nodetype, nodeid):
    service = dlm_find_kill_service(nodetype)
    ha_ip = dlm_get_haip(cf, nodetype, nodeid)
    if ha_ip == '':
        return 0

    dlm_clean_opara_log(ha_ip)
    cmd = 'ssh ' + ha_ip + ' pkill -9 ' + service
    print("CMD: %s" %(cmd))
    if service == 'oPara':
	os.system('sleep 10')
    os.system(cmd)

def dlm_handle_kill(cf, nodetype, nodeid, net):
    if nodeid == 0:
        tid = 1
        while(1):
            ret = __dlm_handle_kill(cf, nodetype, tid)
            if ret == 0:
                break
            tid += 1
        dlm_check_kill(cf, nodetype, nodeid)
    else:
        __dlm_handle_kill(cf, nodetype, nodeid)
        dlm_check_kill(cf, nodetype, nodeid)

    #dlm_clean_opara_log(dlm_get_cmgrip())

def __dlm_handle_reboot(cf, nodetype, nodeid, ischange):
    ip = dlm_get_cmgrip()
    ha_ip = dlm_get_haip(cf, nodetype, nodeid)
    if ha_ip == '':
        return 0

    #dlm_clean_opara_log(ha_ip)

    if ischange == 1 and ip == ha_ip:
        dlm_change_cmgrip(nodetype, nodeid)
    #cmd = 'ssh ' + ha_ip + ' "echo b > /proc/sysrq-trigger &"'
    cmd = 'ssh ' + ha_ip + ' "python /home/reboot.py 1>/dev/null &"'
    #cmd = 'ssh ' + ha_ip + ' "reboot"'
    print("CMD: %s" %(cmd))
    os.system(cmd)

def dlm_check_reboot_all_opara(cf, nodetype, nodeid):
    global g_hmgr_ip
    ip = g_hmgr_ip
    
    time.sleep(30)
    cmd = 'ssh ' + ip + ' /home/parastor/bin/sysctl/parastor_monitor checkstat '\
          '| grep oPara | grep nodeid:1 | awk -F# \'{print $5}\' | awk -F: \'{print $2}\''
    dlm_check_status(cmd, 'ok')
    dlm_clean_opara_log(ip)

def dlm_check_reboot_single_opara(cf, nodetype, nodeid):
    ip = dlm_get_cmgrip()

    cmd = 'ssh ' + ip + ' /home/parastor/bin/sysctl/parastor_monitor checkstat '\
          '| grep oPara | grep nodeid:' + str(nodeid) +' | awk -F# \'{print $5}\' | awk -F: \'{print $2}\''

    time.sleep(30)
    dlm_check_status(cmd, 'abnormal|shutdown')
    dlm_check_status(cmd, 'ok')
    dlm_clean_opara_log(ip)

def dlm_check_reboot_opara(cf, nodetype, nodeid, all):
    if all == 1:
        dlm_check_reboot_all_opara(cf, nodetype, nodeid)
    else:
        dlm_check_reboot_single_opara(cf, nodetype, nodeid)

def dlm_check_reboot_ostor(cf, nodetype, nodeid, all):
    ip = dlm_get_cmgrip()
    cmd = 'ssh ' + ip + ' /home/parastor/bin/sysctl/parastor_monitor checkstat '\
          '| grep oStor | grep nodeid:' + str(nodeid) +' | awk -F# \'{print $4}\' | awk -F: \'{print $2}\''

    time.sleep(30)
    dlm_check_status(cmd, 'abnormal|shutdown')
    dlm_check_status(cmd, 'ok')
    

def dlm_check_reboot(cf, nodetype, nodeid, all):
    if nodetype == 'oPara':
        dlm_check_reboot_opara(cf, nodetype, nodeid, all)
    elif nodetype == 'oStor':
        dlm_check_reboot_ostor(cf, nodetype, nodeid, all)
    else:
        print("Check reboot(%s:%d)" %(nodetype, nodeid))

def dlm_handle_reboot(cf, nodetype, nodeid, net):
    if nodeid == 0:
        tid = 1
        while(1):
            ret = __dlm_handle_reboot(cf, nodetype, tid, 0)
            if ret == 0:
                break
            tid += 1
        dlm_check_reboot(cf, nodetype, nodeid, 1)
    else:
        __dlm_handle_reboot(cf, nodetype, nodeid, 1)
        dlm_check_reboot(cf, nodetype, nodeid, 0)

def dlm_handle_shutdown(cf, nodetype, nodeid, net):
    print("shutdown")

def dlm_handle_poweroff(cf, nodetype, nodeid, net):
    print("poweroff")

def dlm_handle_poweron(cf, nodetype, nodeid, net):
    print("poweron")

def dlm_handle_disk(cf, section):
    disk_desc = ''
    disk = cf.get(section, 'disk_desc_0')
    list = disk.split(':')
    for i in range(len(list)):
        disk_desc = disk_desc + list[i] + ' '

    return disk_desc

def dlm_handle_adddisk(cf, nodetype, nodeid, net):
    if nodetype != 'oStor':
        sys.exit(-1)

    section = dlm_find_section(cf, nodetype, nodeid)
    ha_ip = cf.get(section, 'ha_ip_0')
    d = cf.get(section, 'disk_0')
    disk_desc = dlm_handle_disk(cf, section)

    cmd = 'ssh ' + ha_ip + ' "echo \"scsi add-single-device ' + disk_desc + '\" > /proc/scsi/scsi"'
    print("CMD: %s (add disk %s)" %(cmd, d))
    os.system(cmd)

def dlm_handle_rmdisk(cf, nodetype, nodeid, net):
    if nodetype != 'oStor':
        sys.exit(-1)

    section = dlm_find_section(cf, nodetype, nodeid)
    ha_ip = cf.get(section, 'ha_ip_0')
    d = cf.get(section, 'disk_0')
    disk_desc = dlm_handle_disk(cf, section)

    cmd = 'ssh ' + ha_ip + ' "echo \"scsi remove-single-device ' + disk_desc + '\" > /proc/scsi/scsi"'
    print("CMD: %s (remove disk %s)" %(cmd, d))
    os.system(cmd)


g_cmd_actions = {'ifdown': dlm_handle_ifdown,
                 'ifup': dlm_handle_ifup,
                 'kill': dlm_handle_kill,
                 'reboot': dlm_handle_reboot,
                 'shutdown': dlm_handle_shutdown,
                 'poweroff': dlm_handle_poweroff,
                 'poweron': dlm_handle_poweron,
                 'rmdisk': dlm_handle_rmdisk,
                 'adddisk': dlm_handle_adddisk}

def dlm_fault_usage():
    print 'fulty.py usage:'
    print '-c/--cmd         : command.'
    print '-t/--nodetype    : nodetype.'
    print '-i/--nodeid      : nodeid.'
    print '-n/--net         : net.'

def dlm_check_params(cmd, nodetype, nodeid):
    if not g_cmd_actions.has_key(cmd):
        print("Wrong cmd: %s" %(cmd))
        return 1

    if nodeid < 0:
        print("Wrong nodeid: %d" %(nodeid))
        return 1

    found = 0
    for ntype in g_nodetypes:
        if ntype.find(nodetype) < 0:
            continue
        else:
            found = 1
            break
    if found == 0:
        print("Wrong nodetype: %s" %(nodetype))
        return 1

    return 0

def dlm_init(cf):
    global g_hmgr_ip
    global g_smgr_ip
    global g_mgr_ip
    global g_hmgr_hopara_share
    global g_smgr_gopara_share

    st_cf = dlm_read_config(g_st_config)
    for section in st_cf.sections():
        if section == 'parastor':
            g_hmgr_ip = st_cf.get(section, 'mgrip')
            g_smgr_ip = st_cf.get(section, 'smgrip')
            g_mgr_ip = st_cf.get(section, 'cmgrip')
            print('Get HMGRIP(%s) SMGRIP(%s) CMGRIP(%s) Success' %(g_hmgr_ip, g_smgr_ip, g_mgr_ip))
            break
    
    for section in cf.sections():
        if section.find('oPara') >= 0 and cf.getint(section, 'id') == 1:
            if cf.get(section, 'ha_ip_0') == g_hmgr_ip:
                g_hmgr_hopara_share = 1
                #print('HMGR Share with HoPara')
             
        if section.find('oPara') >= 0 and cf.getint(section, 'id') == 2:
            if cf.get(section, 'ha_ip_0') == g_smgr_ip:
                g_smgr_gopara_share = 1
                #print('SMGR Share with GoPara')

    return 0

def main():
    cmd = ''
    nodetype= ''
    nodeid = 0
    net = ''
    opts, args = getopt.getopt(sys.argv[1:], 'c:t:i:n:h', ['cmd=', 'nodetype=', 'nodeid=', 'net='])
    for op, value in opts:
        if op in ("-c", "--cmd"):
            cmd = value
        elif op in ("-t", "--nodetype"):
            nodetype = value
        elif op in ("-i", "--nodeid"):
            nodeid = string.atoi(value)
        elif op in ("-n", "--net"):
            net = value
        else:
            dlm_fault_usage()
            sys.exit(-1)

    ret = dlm_check_params(cmd, nodetype, nodeid)
    if ret != 0:
        sys.exit(-1)

    cf = dlm_read_config(g_node_config)
    dlm_init(cf)
    g_cmd_actions.get(cmd)(cf, nodetype, nodeid, net)

if __name__ == '__main__':
    main()
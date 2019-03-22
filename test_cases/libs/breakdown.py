#!/usr/bin/python
# -*- encoding=utf8 -*-

import os
import warnings
import json
import shell
import common2
import time
import subprocess
import commands
import log
import get_config
import sys
import signal
import threading
import xml
import re
import random
import datetime
import ReliableTest
import common
import binascii
import Lun_managerTest
import decorator_func

reload(sys)
sys.setdefaultencoding('utf-8')

# global CONF_FILE

conf_file = get_config.CONFIG_FILE
# CONF_FILE = "/home/StorTest/conf/x1000_test_config.xml"
node_ips_list = get_config.get_env_ip_info(conf_file)
# 获取集群IP列表和客户端列表
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
CLEAN_ENV = "No"
current_path_1 = os.path.dirname(os.path.abspath(__file__))
node = common.Node()
com2 = common2.oSan()
osan = common2.oSan()

class Os_Reliable():
    '''
    poweroff_os
    oJmgs_master_id
    check_process_stat
    run_pause_process
    run_process
    json_loads
    get_date_eth
    get_san_state
    network_test
    get_vm_status
    vm_id
    get_node_id_by_ip
    check_badobj
    add_node
    del_node
    get_master_zk
    get_master_oRole
    get_cmd_status
    get_os_status
    kill_thread
    pasue_thread
    run_pasue_threads
    time_limit
    get_unuse_disk_uuid
    add_disks
    get_share_monopoly_disk_ids
    get_diskid_by_name
    get_physicalid_by_name
    get_diskid_by_name
    get_physicalid_by_name
    remove_disk
    insert_disk
    run_down_disk_wait
    run_down_node_wait
    get_node_state
    get_lun_size_dict
    '''

    def __init__(self):
        pass

    def dd_command(self,cli_ip=None,disk=None,bs=1024,count=100000,need_judge=None):
        cmd=('ssh %s "dd  if=/dev/zero of=%s bs=%s count=%s oflag=direct"' % (cli_ip,disk,bs,count))
        log.info(cmd)
        (rc, stdout) = commands.getstatusoutput(cmd)
        if  rc:
            if need_judge:
                log.error(stdout)
                return stdout
            else:
                log.error("Error!execute  command failed!info:%s" % stdout)
                exit(1)
        else:
            log.info(stdout)



    def get_thin_lun(self, node_ip=None):
        """
        :Author:wuyuqiao
        :return: thin_lun ID list
        :param:node_ip:集群任意一管理节点IP
        """
        cmd = ('ssh %s "pscli --command=get_luns"' % node_ip)
        log.info(cmd)
        (rc, stdout) = commands.getstatusoutput(cmd)
        if 0 != rc:
            log.error("Error!execute pscli command failed!info:%s" % stdout)
        else:
            thin_lun = []
            result = json.loads(stdout)
            lun_list = result['result']['luns']
            if not all(lun_list):
                log.error("Error!no lun exsits!")
                os._exit(1)
            else:
                for lun in lun_list:
                    if 'LUN_TYPE_THIN' == lun['lun_type']:
                        thin_lun.append(lun['id'])
            if not len(thin_lun):
                log.error("Error!no THIN lun exsits in system!")
                os._exit(1)
            else:
                return thin_lun

    def get_thick_lun(self, node_ip=None):
        """
        :Author:wuyuqiao
        :return: thick_lun ID list
        :param:node_ip:集群任意一管理节点IP
        """
        cmd = ('ssh %s "pscli --command=get_luns"' % node_ip)
        log.info(cmd)
        (rc, stdout) = commands.getstatusoutput(cmd)
        if 0 != rc:
            log.error("Error!execute pscli command failed!info:%s" % stdout)
            os._exit(1)
        else:
            thick_lun = []
            result = json.loads(stdout)
            lun_list = result['result']['luns']
            if not all(lun_list):
                log.error("Error!no lun exsits!")
                os._exit(1)
            else:
                for lun in lun_list:
                    if 'LUN_TYPE_THICK' == lun['lun_type']:
                        thick_lun.append(lun['id'])
            # if not len(thick_lun):
            #     log.error("Error!no THICK lun exsits in system!")
            #     os._exit(1)
            # else:
            return thick_lun

    def compare_data(self):
        """
        :Author: wangxiang
        :Date: 2018-8-20
        :Description: 数据修复/重建完成后，比较内部数据一致性
        :return:
        change_log:

            ===================================================
            2018-08-20:
            change:wangxiang
            1.描述:创建，先占个位置；等工具出来再写
        """
        time.sleep(30)
        log.info("start check  badobj")
        # disk().check_bad_obj()
        disk().multi_check_part_lun_uniform_by_ip()
        pass

    def asyn_ntp(self):
        cli_ips = client_ips
        ser_ips = deploy_ips

        for cli_ip in cli_ips:
            cmd1 = "ssh root@{} \"sed -r -i -e 's/^server.*//g' -e 's/^#server.*//g' /etc/ntp.conf; sed -i ':a;N;s/\\n\\n//g;ba' /etc/ntp.conf\"".format(
                cli_ip)
            commands.getstatusoutput(cmd1)
            for ser_ip in ser_ips:
                cmd2 = "ssh root@{} \"echo server {} >>/etc/ntp.conf ;systemctl  restart  ntpd\"".format(cli_ip, ser_ip)

                commands.getstatusoutput(cmd2)

    def check_disk_state(self, node_ip=None, disk_uuid=None, disk_state=None, wait_time=360000):
        '''
        :Usge:通过磁盘UUID检查节点磁盘状态
        :Arthur:wangxiang
        :param node_ip: 节点IP
        :param disk_uuid: 磁盘uuid
        :param wait_time: 超时时间，等待重建任务完成，若过了超时时间还未完成，则报错退出
        :return: 磁盘状态：DISK_STATE_ISOLATE  DISK_STATE_HEALTHY  DISK_STATE_REBUILDING_PASSIVE  DISK_STATE_ZOMBIE
        '''
        time.sleep(5)
        node_id = node.get_node_id_by_ip(node_ip)
        while True:
            cmd = ("ssh %s 'pscli --command=get_disks --node_ids=%d'" % (node_ip, node_id))
            log.info(cmd)
            (res, output) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error("Get disks info replica failed!!!")
                os._exit(1)
            else:
                result = json.loads(output)
                disk_list = result['result']['disks']
                for disk in disk_list:
                    if disk['uuid'] == disk_uuid:
                        if disk['state'] == disk_state:
                            return 0
                        else:
                            log.info("Waiting for Rebuilding to be completed")
                            log.info("The %s disk status is %s" % (disk['devname'], disk['state']))
                            time.sleep(120)
                            break
                    else:
                        pass

    def os_power_reset(self, s_ip=None, cmd_c=None, wait_time=30):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description: send to OS power on or off cmd
        :param s_ip(str): node IP
        :param cmd_c(str): command to node EXP:"init 0","init 6".....
        :return:
        """
        if cmd_c == "init 6":
            log.info("CMD: init 6 change to echo b >/proc/sysrq-trigger")
            cmd_c = 'echo b >/proc/sysrq-trigger'
            cmd = ("timeout 10 ssh %s \" %s \"" % (s_ip, cmd_c))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            log.info("%s os %s poweroff success, waiting %s to check it. info:%s" % (s_ip, cmd_c, wait_time, final))
            time.sleep(wait_time)
            return
        else:
            cmd = ("ssh %s \"%s\"" % (s_ip, cmd_c))
            (res, final) = commands.getstatusoutput(cmd)
            log.info("send:\"%s\"" % (cmd))
            if res != 0:
                log.info("%s os %s poweroff success, waiting %s to check it ." % (s_ip, cmd_c, wait_time))
                time.sleep(wait_time)
                return
            else:
                log.info("%s os %s poweroff fail, Error info: %s" % (s_ip, cmd_c, final))
                os._exit(1)
    def poweroff_os(self, s_ip=None, cmd_c=None, wait_time=30):
        """

        :param s_ip: 
        :param cmd_c:
        :param wait_time:
        :return:
        """
        if '6' in cmd_c or 'reboot' in cmd_c:
            cmd_c = 'echo b >/proc/sysrq-trigger'
        cmd = ("timeout 10 ssh %s \" %s \"" % (s_ip, cmd_c))
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        log.info("%s os %s poweroff success, waiting %s to check it. info:%s" % (s_ip, cmd_c, wait_time, final))

        time.sleep(wait_time)

    def os_down_new(self, mac_type="vir", falut_ip=None, cmd_c=None, ipmi_ip=None):
        '''节点关机'''
        warnings.warn("This function is no longer recommended", DeprecationWarning)
        if mac_type == "vir":
            cmd = ("ssh %s \" %s \"" % (falut_ip, cmd_c))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.info("%s os  poweroff success" % (falut_ip))
                time.sleep(60)
            else:
                log.info("%s os  poweroff fail" % (falut_ip))
                os._exit(1)
        elif mac_type == "phy":
            if ipmi_ip == None:
                log.info("please the arg  ipmi_ip")
                os._exit(1)
            else:
                cmd1 = 'ipmitool -H %s -I lan -U admin -P admin power off' % ipmi_ip
                cmd2 = 'ipmitool -H %s -I lan -U ADMIN -P ADMIN power off' % ipmi_ip
                rc, stdout = commands.getstatusoutput(cmd1)
                if 0 != rc:
                    if 'Invalid user name' in stdout:
                        rc, stdout = commands.getstatusoutput(cmd2)
                        if 0 != rc:
                            return False
                        else:
                            return True
                    else:
                        return False
                else:
                    return True
        else:
            log.info("please give a right machine_type .may be  phy  or   vir ?")
            os._exit(1)

    def os_up_new(self, mac_type="vir", ipmi_ip=None, esxi_ip=None, u_name=None, pw=None, vm_id=None):
        warnings.warn("This function is no longer recommended", DeprecationWarning)
        if mac_type == "vir":
            str1 = "vim-cmd vmsvc/power.on %s" % (str(vm_id))
            cmd = ("%s/expect %s %s \"%s\" \"%s\"" % (current_path_1, esxi_ip, u_name, pw, str1))
            rc, stdout = commands.getstatusoutput(cmd)
            if rc != 0:
                log.info("Up virtual machine failed.")
                os._exit(1)
            elif mac_type == "phy":
                if ipmi_ip == None:
                    log.info("please the arg  ipmi_ip")
                    os._exit(1)
                else:
                    cmd1 = 'ipmitool -H %s -I lan -U admin -P admin power on' % ipmi_ip
                    cmd2 = 'ipmitool -H %s -I lan -U ADMIN -P ADMIN power on' % ipmi_ip
                    rc, stdout = commands.getstatusoutput(cmd1)
                    if 0 != rc:
                        if 'Invalid user name' in stdout:
                            rc, stdout = commands.getstatusoutput(cmd2)
                            if 0 != rc:
                                return False
                            else:
                                return True
                        else:
                            return False
                    else:
                        return True
            else:
                log.info("please give a right machine_type .may be  phy  or   vir ?")
                os._exit(1)

    def init_otrace(self):
        """
        :Author: Liu he
        :Date: 2018-8-20
        :Description: 初始化otrace，配置otrace服务
        :return:
        """
        for ip in deploy_ips:
            cmd = ("ssh %s \"[ -d /home/parastor/log/otrace/ ]\" >/dev/null 2>&1;echo $?" % (ip))
            re, stdout = commands.getstatusoutput(cmd)
            if stdout == 1:
                log.error("the system environment is clear ")
            else:
                cmd1 = (
                        "ssh %s \"rm -rf /home/parastor/log/otrace/ ; rm -rf /dev/shm/otrace_buf /dev/shm/sem.otrace_tp ;sleep 2 ;/home/parastor/tools/otraced -d\"" % (
                    ip))
                rc, stdout = commands.getstatusoutput(cmd1)
                if rc == 0:
                    log.info("cmd \"rm\" and restart otraced have finished")

            cmd = ("ssh %s \"mkdir /home/parastor/log/otrace/\"" % (ip))
            re, stdout = commands.getstatusoutput(cmd)
            if re != 0:
                log.error("mkdir otrace failed")
                os._exit(1)
            else:
                log.info("mkdir otrace success")
                cmd2 = (
                        "ssh %s \"/home/parastor/tools/otraced -d;sleep 1 ; /home/parastor/tools/otrc -z on;sleep 1 ;/home/parastor/tools/otrc -i | grep ring\"" % (
                    ip))
                rc, stdout2 = commands.getstatusoutput(cmd2)
                if rc != 0:
                    log.info("start otrace failed")
                else:
                    otrace_status = stdout2.split(":")[2].split(" ")[0]
                    # print otrace_status
                    if otrace_status == "0x00000042":
                        log.info("start otrace success")
                        cmd3 = (
                                "ssh %s \"/home/parastor/tools/otrc -o /home/parastor/log/otrace/otrace.data -s 4096 -S \\\"IOPREP|DJNL|DPC|LMPC|LIOC\\\" \"" % (
                            ip))
                        rc3, stdout3 = commands.getstatusoutput(cmd3)
                        print stdout3
                        # print rc3
                        if rc3 != 0:
                            log.info("otrace.data.0 set failed")
                        else:
                            log.info("otrace.date.0 set success")
                    else:
                        log.info("start otrace failed,please check")
                        os._exit(1)

    def oJmgs_master_id(self):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description: 在系统节点列表中轮询查询oJmgs主进程节点IP and id号
        :return: final:node ID ;m_ojmgs_ip:node IP
        """
        while True:
            for s_ip in node_ips_list:
                # print ("try get master from %s" % s_ip)
                cmd = ("ssh %s \"pscli --command=get_master | grep node_id | cut -d \' \' -f 10 \" " % (s_ip))
                log.info(cmd)
                (res, final) = commands.getstatusoutput(cmd)
                if 0 == res:
                    log.info("get oJmgs master node id is %s " % (final))
                    m_ojmgs_ip = common.Node().get_node_ip_by_id(final)
                    # m_ojmgs_ip = node_ips_list[int(final) - 1]
                    return final, m_ojmgs_ip
                else:
                    time.sleep(30)

    ##############################################################################
    ###name  :      check_process_stat
    ###parameter:   命令参考 node_ip节点IP，p_name进程名称
    ###author:      wuyq
    ###date  :      2018.8.13
    ###Description: 在系统中查询某个节点的某个进程的状态是否正常
    ##############################################################################
    def check_process_stat(self, node_ip, p_name):
        node_id = node.get_node_id_by_ip(node_ip)
        cmd = ('ssh %s "pscli --command=get_services --node_ids=%s"' % (node_ip, node_id))
        log.info(cmd)
        (rc, stdout) = commands.getstatusoutput(cmd)
        if rc != 0:
            log.info('the node is Error...')
        else:
            data = json.loads(stdout)
        count = 0
        while count < len(data['result']['nodes'][0]['services']):
            # state=data['result']['nodes'][0]['services'][0]['inTimeStatus']
            service = data['result']['nodes'][0]['services'][count]['service_type']
            if service == p_name:
                state = data['result']['nodes'][0]['services'][count]['inTimeStatus']
                state_str = state.split('_')
                state = state_str[2]
                log.info('The %s service of the %s node is %s' % (p_name, node_ip, state))
                return state
            count += 1

    def run_pause_process(self, p_name=None, p_ip=None):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description: 使用kill -19 [pid] 方式将进程暂时挂起
        :param p_name(str): 进程名称
        :param p_ip(str): 进程所在节点
        :return:
        """
        ps_cmd = ('ssh %s \"ps -ef | grep %s | grep -v grep\"' % (p_ip, p_name))
        rc, stdout = commands.getstatusoutput(ps_cmd)
        if '' == stdout:
            return
        log.info(stdout)
        lines = stdout.split('\n')
        for line in lines:
            vars = line.split()
            pid = vars[1]
            kill_cmd = ('ssh %s "kill -19 %s"' % (p_ip, pid))
            log.info('node %s kill %s' % (p_ip, p_name))
            rc, stdout = commands.getstatusoutput(kill_cmd)
            if 0 != rc:
                log.error("Execute command: \"%s\" failed. \nstdout: %s" % (kill_cmd, stdout))
        return

    def run_process(self, p_name=None, p_ip=None):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description: kill -18 [pid]恢复挂起进程
        :param p_name(str): 进程名称
        :param p_ip(str): 进程所在节点
        :return:
        """
        ps_cmd = ('ssh %s \"ps -ef | grep %s | grep -v grep\"' % (p_ip, p_name))
        rc, stdout = commands.getstatusoutput(ps_cmd)
        if '' == stdout:
            return
        log.info(stdout)
        lines = stdout.split('\n')
        for line in lines:
            vars = line.split()
            pid = vars[1]
            kill_cmd = ('ssh %s "kill -18 %s"' % (p_ip, pid))
            log.info('node %s %s have recover' % (p_ip, p_name))
            rc, stdout = commands.getstatusoutput(kill_cmd)
            if 0 != rc:
                log.error("Execute command: \"%s\" failed. \nstdout: %s" % (kill_cmd, stdout))
        return

    def json_loads(self, stdout):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description: 将传入的字符串格式化,  从ReliableTest库移植过来
        :param stdout: 需要格式化的字符
        :return:
        """
        try:
            stdout = stdout.replace('\\', '')
            stdout_str = json.loads(stdout, strict=False)
            return stdout_str
        except Exception, e:
            log.error(stdout)
            raise Exception("Error msg is %s" % e)

    def get_date_eth(self, node_id, s_ip):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description: 获取本节点的数据网的eth名字
        :param node_id(str): 节点ID号
        :param s_ip(str): 节点IP地址
        :return:SS
        """
        cmd = ("ssh %s \"pscli --command=get_nodes --ids=%s \" " % (s_ip, node_id))
        log.info(cmd)
        data_ip_list = []
        rc, stdout = commands.getstatusoutput(cmd)
        if 0 != rc:
            raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        else:
            result = json.loads(stdout)
            data_ips = result['result']['nodes'][0]['data_ips']
            for data_ip in data_ips:
                ip = data_ip['ip_address']
                data_ip_list.append(ip)
        eth_list = []
        for ip in data_ip_list:
            tem_dic = {}
            cmd1 = 'ssh %s "ip addr | grep %s"' % (s_ip, ip)
            rc, stdout = commands.getstatusoutput(cmd1)
            if 0 != rc:
                raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd1, stdout))
            else:
                eth_name = stdout.split()[-1]
                tem_dic["eth"] = eth_name

            cmd2 = 'ssh %s "ifconfig | grep %s"' % (s_ip, ip)
            rc, stdout = commands.getstatusoutput(cmd2)
            if 0 != rc:
                raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd2, stdout))
            else:
                mask = stdout.strip().split()[3]
                tem_dic["dataip"] = ip
                tem_dic["mgrip"] = s_ip
                tem_dic["mask"] = mask
            eth_list.append(tem_dic)
        return eth_list

    def get_node_eth_list(self, node_ip):
        """
        :Auther:Liu he
        :Description: 获取指定节点所有网卡名称
        :param node_ip:
        :return:
        """
        eth_list = []
        cmd = ("ssh %s \"ip addr |grep \"BROADCAST\"\"" % (node_ip))
        rc, ouput = commands.getstatusoutput(cmd)
        if rc != 0:
            log.error("get eth list failed")
            os._exit(1)
        else:
            eth_name = ouput.split("\n")
            for i in range(len(eth_name)):
                name = eth_name[i].split(": ")[1]
                eth_list.append(name)
        return eth_list

    def get_vip_eth_name(self, node_ip):
        """
        :Auther: Liu he
        :Description:获取指定存储节点业务网卡名称
        :param node_ip:
        :return:
        """
        vips = get_config.get_vip(conf_file)
        log.info("form \"get_vip_eth_name\" function, from node_ip %s, test_ip %s" % (node_ip, vips))
        node_eth_list = ReliableTest.get_eth(node_ip=node_ip, test_ip=vips)
        log.info("Get vip network name:%s" % (node_eth_list))
        return node_eth_list

    def get_eth_name(self, s_ip):
        """
        :Auther: Liu he
        :param s_ip: 存储节点IP
        :return: 该节点所有网卡名称
        """
        if s_ip:
            name_list = []
            s_id = self.get_node_id_by_ip(s_ip)
            cmd = ("ssh %s \"pscli --command=get_nodes --ids=%s\" " % (s_ip, s_id))
            log.info(cmd)
            rc, stdout = commands.getstatusoutput(cmd)
            if rc != 0:
                log.error("get node info failed !!!\nError Info: %s" % (stdout))
                os._exit(1)
            else:
                stdout = json.loads(stdout)
                nodes = stdout['result']['nodes'][0]
                log.info("check node ID : %s" % s_id)
                for i in range(len(nodes['internalNetworkInterfaces'])):
                    manage_net_name = nodes['internalNetworkInterfaces'][i]['name']
                    name_list.append(manage_net_name.encode("utf-8"))
            # log.info("Find The node %s have eth name list %s" % (s_ip, name_list) )
            log.info("Get eth list:%s" % (name_list))
            return name_list
        else:
            log.error("s_ip is None, Please check")
            os._exit(1)

    def get_san_state(self, s_ip=None):
        """
        :Auther: Liu he
        :Description: 获取san状态(默认第一个访问区)
        :return: 开启返回True 未开启返回False
        """
        param_list = [s_ip]
        if all(param_list):
            cmd = ("pscli --command=get_access_zones")
            log.info(cmd)
            # rc, stdout = commands.getstatusoutput(cmd)
            rc, stdout = com2.run_pscli_cmd(cmd, time_out=300, times=1)
            if rc != 0:
                log.error("get cmd failed,Error infor:%s" % (stdout))
                os._exit(1)
            else:
                status_san = []
                stdout = json.loads(stdout)
                chk_san = stdout["result"]["access_zones"]
                if chk_san:
                    for i in range(len(chk_san)):
                        san_state = stdout["result"]["access_zones"][i]["enable_san"]
                        status_san.append(san_state)
                    return status_san
                else:
                    return
        else:
            log.error("param is None error :s_ip :%s " % (s_ip))
            os._exit(1)

    def network_test(self, s_ip=None, net_name=None, net_stat=None):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description: 将指定节点上的网卡进行关闭和开启
        :param s_ip: s_ip节点IP地址
        :param net_name: 需要测试的网卡名称
        :param net_stat: net_stat=“down” or “up”
        :return:
        """
        log.info("testing network is %s , will %s" % (net_name, net_stat))
        if net_stat == "down":
            cmd = ("ssh %s \" ifdown %s\"" % (s_ip, net_name))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error("ifdown error")
                os._exit(1)
            else:
                log.info("%s in %s ifdown success" % (net_name, s_ip))
                return
        elif net_stat == "up":
            cmd = ("ssh %s \" ifup %s\"" % (s_ip, net_name))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error("ifup error")
                os._exit(1)
            else:
                log.info("%s ifup success" % (net_name))
                return
        else:
            log.error("check network")
            os._exit(1)

    def net_flash_test(self, node_ip=None, netname=None, times=10, interval=30):
        """
        :Arthur: wuyuqiao
        :param node_ip: 需要闪断数据网的节点
        :param net_name: 单个网卡名字或网卡列表
        :param times: 闪断次数
        :param interval: 闪断间隔秒数
        :return: 无
        """
        param_list = [node_ip, netname, times, interval]
        if all(param_list):
            if type(netname) == str:
                for count in range(times):
                    log.info('第 %d 次闪断数据网' % (count + 1))
                    log.info('节点数据网卡断开,网卡:%s' % netname)
                    self.network_test(node_ip, netname, 'down')
                    time.sleep(interval)
                    log.info('节点数据网卡恢复,网卡:%s' % netname)
                    self.network_test(node_ip, netname, 'up')
                    time.sleep(45)
            elif type(netname) == list:
                for count in range(times):
                    log.info('第 %d 次闪断数据网' % (count + 1))
                    for eth in netname:
                        log.info('节点数据网卡断开,网卡:%s' % eth)
                        self.network_test(node_ip, eth, 'down')
                    time.sleep(interval)
                    for eth in netname:
                        log.info('节点数据网卡恢复,网卡:%s' % eth)
                        self.network_test(node_ip, eth, 'up')
                    time.sleep(30)
            else:
                log.error('netname Parameter is invalid ')
                os._exit(1)
        else:
            log.error("iterable is error: \n node_ip:%s \n netname:%s \n times:%d \n interval:%d" % (
                node_ip, netname, times, interval))
            os._exit(1)

    def vm_id(self, esxi_ip=None, u_name=None, pw=None, node_ip=None, vm_id=None):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description: 通过虚拟机IP获取虚拟节点在虚拟机中的id号
        :param esxi_ ip: 虚拟机管理节点IP
        :param u_name: 虚拟机用户名
        :param pw: 密码
        :param node_ip: 虚拟机IP
        :param vm_id: 虚拟机id号（选填）
        :return:
        """
        if None == vm_id:
            cmd1 = ("ssh %s \"ifconfig | grep -A 3 %s | grep ether | awk '{print \$2}'\"" % (node_ip, node_ip))
            rc, stdout = commands.getstatusoutput(cmd1)
            if 0 != rc:
                log.error("Can not attatch the node.")
                os._exit(1)
            else:
                mac = stdout
                str1 = "for i in \`vim-cmd vmsvc/getallvms | awk '{print \$1}' | grep -v -E [a-zA-Z].*\`;do vim-cmd vmsvc/device.getdevices \$i | grep -i -q %s && echo \$i;done" % (
                    mac)
                cmd = ("%s/expect %s %s \"%s\" \"%s\"" % (current_path_1, esxi_ip, u_name, pw, str1))
                rc, stdout = commands.getstatusoutput(cmd)
                vm_id = stdout.split("\n")[2]
        log.info("get vMware ID: %s" % (vm_id))
        return vm_id

    def get_vm_status(self, esxi_ip, vm_name, pw, vm_id):
        """
        :Auther: Liu He
        :Description: 通过VMWare宿主机获取虚拟机开机状态
        :param esxi_ip: 虚拟机IP
        :param vm_name: VMware登录用户名
        :param pw: 密码
        :param vm_id: 节点ID
        :return: 虚拟机运行状态，Powered off or Powered on
        """
        # str1 = "esxcli vm process list"
        arg_list = [esxi_ip, vm_name, pw, vm_id]
        if all(arg_list):
            str1 = "vim-cmd vmsvc/power.getstate %s " % (vm_id)
            cmd = ("%s/expect %s %s \"%s\" \"%s\"" % (current_path_1, esxi_ip, vm_name, pw, str1))
            log.info(cmd)
            rc, stdout = commands.getstatusoutput(cmd)
            if rc != 0:
                log.info("can not get vm system status,please check vm.Error Infor: %s" % (stdout))
                os._exit(1)
            else:
                get_info = stdout.split("\n")
                # log.debug(get_info)
                node_status = get_info[-1]
                log.info("get vm status is %s" % (node_status))
                return node_status
        else:
            log.error("In parameter: %s " % (arg_list))
            os._exit(1)

    def get_power_status(self, bmc_ip):
        """
        :Auther: Liu He
        :Description: 通过BMC获取物理机开机状态
        :param bmc_ip: BMC ip 地址
        :param bmc_name: BMC用户名
        :param bmc_pw: 密码
        :return（str）: 虚拟机运行状态，on or off
        """
        arg_list = [bmc_ip]
        if all(arg_list):
            cmd1 = ("ipmitool -H %s -I lan -U admin -P admin power status" % (bmc_ip))
            cmd2 = ("ipmitool -H %s -I lan -U ADMIN -P ADMIN power status" % (bmc_ip))
            rc, stdout = commands.getstatusoutput(cmd1)
            log.info(cmd1)
            if 0 != rc:
                rc, stdout = commands.getstatusoutput(cmd2)
                log.info(cmd2)
                if 0 != rc:
                    log.info(stdout)
                    return False
                else:
                    node_status = stdout.strip().split(" ")[-1]
                    log.info("get The machine status is %s" % (node_status))
                    return node_status
            else:
                node_status = stdout.strip().split(" ")[-1]
                log.info("get The machine status is %s" % (node_status))
                return node_status

    def get_node_id_by_ip(self, node_ip):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description: 通过节点IP地址获取该节点在系统中的id号
        :param node_ip: 虚拟机IP
        :return: node ID
        """
        cmd = (" ssh %s \"pscli --command=get_nodes\"" % (node_ip))
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        else:
            msg = json.loads(stdout)
            nodes_info = msg["result"]["nodes"]
            for node in nodes_info:
                ctl_ip = node["ctl_ips"][0]["ip_address"]
                if node_ip == ctl_ip:
                    return node["node_id"]
            log.info("there is not a node's ip is %s!!!" % node_ip)
            return None

    def get_lun_id_by_name(self, s_ip, lun_name):
        """
        :Auther: Liu he
        :Description: 通过lun name 获取lun id号
        :param s_ip: 任意集群节点IP
        :param lun_name: 要搜索的lun 名称
        :return: 检索到的lun id号
        """
        cmd = ("ssh %s \"pscli --command=get_luns\"" % (s_ip))
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        if rc != 0:
            log.error("cmd failed!!! %s" % (cmd))
            os._exit(1)
        else:
            stdout = json.loads(stdout)
            lun = stdout["result"]["luns"]
            for i in range(len(lun)):
                name = stdout["result"]["luns"][i]["name"]
                if name == lun_name:
                    lun_id = stdout["result"]["luns"][i]["id"]
                    return lun_id
            return

    def get_map_by_lun(self, s_ip, lun_info):
        """
        :Auther: Liu he
        :Description: 通过 已映射的lun名称，查找对应mapid
        :param s_ip:  任意节点IP
        :param lun_name: 查找lun map所对应的lun 名称
        :return: lun map ID
        """
        usg_list = [s_ip, lun_info]
        if all(usg_list):
            if str(lun_info).isdigit():
                lun_id = lun_info
                log.info("Return by \"get_map_by_name\" Get LUN ID:%s" % (lun_id))
            else:
                lun_id = self.get_lun_id_by_name(s_ip, lun_info)
                log.info("Return by \"get_map_by_name\" Get LUN ID:%s" % (lun_id))
            cmd = ("ssh %s \"pscli --command=get_lun_maps\"" % (s_ip))
            log.info(cmd)
            rc, stdout = commands.getstatusoutput(cmd)
            if rc != 0:
                log.error("cmd failed!!! %s" % (cmd))
                os._exit(1)
            else:
                stdout = json.loads(stdout)
                map = stdout["result"]["lun_maps"]
                for i in range(len(map)):
                    by_map_lun_id = map[i]["lun_id"]
                    if by_map_lun_id == lun_id:
                        map_id = map[i]["id"]
                        return map_id
        else:
            log.error("You need check The %s" % (usg_list))
            os._exit(1)

    def get_matid(self, node_ip):
        """
        :Author: wangxiang
        :Date: 2018-8-30
        :Description: 获取oJob主
        :param node_ip: 虚拟机IP
        :return:
        """
        node_ID = self.get_node_id_by_ip(node_ip)
        cmd = ("ssh %s \"/home/parastor/tools/nWatch  -t oJob -i %s -c JOB#jobinfo\"" % (node_ip, node_ID))
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        if 0 != rc or 'failed' in stdout.splitlines()[0]:
            log.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            return -1
        master_job_id = stdout.split(',')[0].split(":")[-2].split()[0]
        return master_job_id

    def check_rcvredobj(self, node_ip):
        """
        :Author: wangxiang
        :Date: 2018-8-27
        :Description: 通过IP地址检查该节点上是否有修复任务，
        :param node_ip: 虚拟机IP
        :return:
        """
        decorator_func.timer(30)
        node_ID = self.get_node_id_by_ip(node_ip)
        cmd = ("ssh %s \"/home/parastor/tools/nWatch -t oJob -i %s -c RCVR#jobinfo\"" % (node_ip, node_ID))
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        if 0 != rc or 'failed' in stdout.splitlines()[0]:
            log.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            return -1
        master_job_id = stdout.split(',')[0].split()[-1]
        log.info("The master job id is %s" % master_job_id)

        cmd = ("ssh %s \"/home/parastor/tools/nWatch -t oJob -i %s -c RCVR#repairjob\" " % (node_ip, master_job_id))
        log.info(cmd)
        rc, result_badobj = commands.getstatusoutput(cmd)
        if 0 != rc or 'failed' in stdout.splitlines()[0]:
            log.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, result_badobj))
            return -1
        result_tmp = result_badobj.split()
        if "0" != result_tmp[-1]:
            log.info("masterjob = %s, badobj_num = %s" % (master_job_id, result_tmp[-1]))
            return result_tmp[-1]

        log.info("The current environment does not have badobj")
        return 0

    def add_node(slef, node_ip, config_file):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description: 添加节点
        :param node_id: node ID
        :param config_file: 节点配置文件
        :return:
        """
        usage_list = [node_ip, config_file]
        if all(usage_list):
            cmd = ("ssh %s \"pscli --command=add_nodes --config_file=%s\" " % (node_ip, config_file))
            log.info('add node: %s' % (cmd))
            rc, stdout = commands.getstatusoutput(cmd)
            if 0 != rc:
                log.error("Execute command: \"%s\" failed. \nError Info:\n%s" % (cmd, stdout))
                os._exit(1)
            else:
                log.info("Add node is success")
                return
        else:
            log.error("iterable is error,Error Info:\n node_ip:%s \n config_file:%s " % (node_ip, conf_file))
            os._exit(1)

    def del_node(slef, node_ip, node_id):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description: 删除节点
        :param node_ip: 节点IP
        :param node_id: 节点ID
        :return:
        """
        usage_list = [node_ip, node_id]
        if usage_list:
            cmd = ("ssh %s \"pscli --command=remove_node --id=%s\" " % (node_ip, node_id))
            log.info('remove node: %s' % (cmd))
            rc, stdout = commands.getstatusoutput(cmd)
            if 0 != rc:
                log.error("Execute command: \"%s\" failed. \nError Info:\n%s" % (cmd, stdout))
                os._exit(1)
            else:
                log.info("delete node success")
                return
        else:
            log.error("iterable is error: \n  node_ip:%s \n config_file:%s " % (node_ip, node_id))
            os._exit(1)

    ##############################################################################
    ###name  :      get_master_zk
    ###parameter:   参数 node_ip:节点IP，
    ###author:      wuyq
    ###date  :      2018.08.09
    ###Description: oRole master IP address
    ##############################################################################
    def get_master_zk(self, deploy_ips=[]):
        for node_ip in deploy_ips:
            cmd = ("ssh %s \"ls /root/zk/bin/zkCli.sh\"" % (node_ip))
            rc, output = commands.getstatusoutput(cmd)
            if rc != 0:
                zk_dir = "/home/parastor/conf/zk"
            else:
                zk_dir = "/root/zk"
            cmd = ('ssh %s "%s/bin/zkServer.sh status"' % (node_ip, zk_dir))
            log.info(cmd)
            (rc, stdout) = commands.getstatusoutput(cmd)
            if rc != 0:
                log.warn("the node is not Stor node...")
            else:
                lines = stdout.split('\n')
                data_line = lines[len(lines) - 1]
                if 'leader' in data_line:
                    master_node_ip = node_ip
                    log.info("zk master node ip is %s " % (master_node_ip))
                    return master_node_ip


    def get_master_oRole(self, s_ip=None):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description: from ZoooKeeper get oRole master IP address
        :param s_ip: 节点IP
        :return: master oRole process node ip
        change:
        ===========================
            修改添加过滤日志
        """
        orole_nodeid, orole_nodeip = Os_Reliable().oJmgs_master_id()
        return orole_nodeip


    def get_master_orole2(self, s_ip):
        """
        :Auther:Liu he
        :Description: 通过nwatch命令拿到主oRole Id和IP
        :param s_ip: 任意节点IP
        :return: 主oRole ip地址
        """
        usg_list = [s_ip]
        if all(usg_list):
            node_id = self.get_node_id_by_ip(s_ip)
            cmd = (
                    "ssh %s \"/home/parastor/tools/nWatch -i %s -t oRole -c oRole#rolemgr_master_dump\"" % (
            s_ip, node_id))
            log.info(cmd)
            rc, stdout = commands.getstatusoutput(cmd)
            if rc != 0:
                log.error("cmd failed:%s \nError Info:%s" % (cmd, stdout))
                os._exit(1)
            else:
                master_id = stdout.split(":")[-1]
                master_ip = common.Node().get_node_ip_by_id(master_id)
                log.info("get oRole master IP:%s " % (master_ip))
                return master_ip
        else:
            log.error("usage Error:%s" % (usg_list))
            os._exit(1)

    def get_opara_jnl(self):
        for ip in deploy_ips:
            if False is ReliableTest.check_ping(ip):
                continue
            else:
                node_id = self.get_node_id_by_ip(ip)
                cmd = ("ssh %s \"/home/parastor/tools/nWatch -t oRole -i %s --command=oRole#rolemgr_view_dump\"" % (
                    ip, node_id))
                print cmd
                re, output = commands.getstatusoutput(cmd)
                if re != 0:
                    log.error("get rolemgr_view_dump failed")
                else:
                    jtype1 = output.split("======================jtype:1 info=======================")[1]
                    lnode_info = jtype1.split("\n")
                    for line in lnode_info:
                        if "lnodeid:" in line:
                            id = line.split(",")[0].split(" ")[-1]
                            log.info("get opara jnl id:%s" % (id))
                            return id

    def get_cmd_status(self, s_ip=None, cmd_name=None):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description: get cmd running status
        :param s_ip(str): node ip
        :param cmd_name(str): cmd name
        :return:
        """
        cmd = ("ssh %s \"ps aux |grep %s |grep -v grep\" " % (s_ip, cmd_name))  # 先在指定节点上抓取状态，只抓一次防止时间过短在其他节点上遗漏
        rc, stdout = commands.getstatusoutput(cmd)
        log.info(cmd)
        if rc == 0:
            log.info("form %s system has detected the \"%s\" command." % (s_ip, cmd_name))
            return 0
        nums = 0
        while nums <= 1000:  # 指定节点上没有抓取到状态，在所有节点上循环进行
            for ip in deploy_ips:
                cmd = ("ssh %s \"ps aux |grep %s |grep -v grep\" " % (ip, cmd_name))
                rc, stdout = commands.getstatusoutput(cmd)
                if rc == 0:
                    log.info("form %s system has detected the \"%s\" command. will make next step" % (ip, cmd_name))
                    return 0
            nums += 1
        log.info("The %s is better than 1000th without detecting the \"%s\" command" % (s_ip, cmd_name))
        return 1

    def get_access_zone_node(self, az_id=None):
        """
        :Auther: Liu he
        :Description: 检查集群中所有在访问区中的节点
        :return: 节点列表
        """
        cmd = ("pscli --command=get_access_zones")
        rc, output = com2.run_pscli_cmd(cmd, times=1)
        if rc != 0:
            log.error("get access zone failed.%s" % (output))
        else:
            node_list = []
            output = json.loads(output)
            access_list = output["result"]["access_zones"]
            for access in access_list:
                if az_id is None:
                    node_id = access["node_ids"]
                    node_list.extend(node_id)
                else:
                    if access['id'] == int(az_id):
                        node_id = access["node_ids"]
                        node_list.extend(node_id)
            log.info("Get enable san node list is %s" % (node_list))
            return node_list

    def get_os_status(self, s_ip=None):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description: get the system status
        :param s_ip: node ip
        :return:
        =======================
            在节点状态中加入服务状态检查，检查等待时间200s，若200s未恢复报错退出
        =======================
        """
        while True:
            cmd = ("ssh %s \"hostname\"" % (s_ip))
            rc, stdout = commands.getstatusoutput(cmd)
            if rc != 0:
                log.info("waiting the system {} up ".format(s_ip))
                time.sleep(10)
            else:
                cmd = ("ssh %s \"pscli --all|grep get_system_state \"" % (s_ip))
                rc, final = commands.getstatusoutput(cmd)
                if rc != 0:
                    log.info("The %s system have not \"pscli\"，Stop manually if not as expected " % (stdout))
                    return
                else:
                    i = 0
                    log.info("check the system is up ,get the hostname is %s " % (stdout))
                    while i < 600:
                        rc = common.check_service_state()
                        if rc == True:
                            log.info("About after os up Waiting %ss "
                                     "The %s system service status recover OK." % (i, stdout))
                            return 0
                        elif i >= 597:
                            log.error(
                                "Waiting %ss The %s system have status not recover ,need to checking" % (i, stdout))
                            os._exit(1)
                        else:
                            i += 3
                            time.sleep(3)

    def get_os_status_1(self, s_ip=None):
        """
        :Author: wangxiang
        :Date: 2018-9-18
        :Description: get the system status
        :param s_ip: node ip
        :return:
        """
        while True:
            cmd = ("ssh %s \"hostname\"" % (s_ip))
            rc, stdout = commands.getstatusoutput(cmd)
            if rc != 0:
                log.info("waiting the system {} up ".format(s_ip))
                time.sleep(15)
            else:
                log.info("check the system is up ,get the hostname is %s,ip is %s " % (stdout, s_ip))
                return 0

    def kill_thread(self, s_ip=None, p_name=None, t_name=None):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description: 查杀线程
        :param s_ip: 节点IP
        :param p_name: process name
        :param t_name: thread name
        :return:
        """
        cmd = (" ssh %s \" pgrep %s\"" % (s_ip, p_name))
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        if rc != 0:
            log.error("the node have not %s" % p_name)
            os._exit(1)
        else:
            cmd = ("ssh %s \" ps -T -p %s | grep pmgr | tail -n 1| awk '{print \$2}'\"" % (s_ip, stdout))
            log.info(cmd)
            rc, final = commands.getstatusoutput(cmd)
            if rc != 0:
                log.error("%s have node find" % t_name)
                os._exit(1)
            else:
                i = 0
                while final.strip() == '':
                    time.sleep(30)
                    rc, final = commands.getstatusoutput(cmd)
                    i += 1
                    if i == 3:
                        log.info("try again to get pmgr failed")
                        os._exit(1)
                else:
                    cmd = ("ssh %s \" kill -9 %s\"" % (s_ip, final))
                    log.info(cmd)
                    rc, finals = commands.getstatusoutput(cmd)
                    if rc != 0:
                        log.error("kill %s fail. error info:\n %s" % (t_name, finals))
                        os._exit(1)
                    else:
                        log.info("kill success %s" % (t_name))
                        time.sleep(10)
        return

    def pasue_thread(self, s_ip=None, p_name=None, t_name=None):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description: 挂起线程
        :param s_ip: 节点IP
        :param p_name: process name
        :param t_name: threads name
        :return:
        """
        cmd = (" ssh %s \" pgrep %s\"" % (s_ip, p_name))
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        if rc != 0:
            log.error("the node have not oRole")
        else:
            cmd = ("ssh %s \" ps -T -p %s | grep pmgr | tail -n 1 |awk '{print \$2}' \"" % (s_ip, stdout))
            log.info(cmd)
            rc, final = commands.getstatusoutput(cmd)
            if rc != 0:
                log.error("oPmgr have node find")
                os._exit(1)
            else:
                print final
                cmd = ("ssh %s \" kill -19 %s\"" % (s_ip, final))
                log.info(cmd)
                rc, finals = commands.getstatusoutput(cmd)
                if rc != 0:
                    log.error("kill %s fail" % (t_name))
                    os._exit(1)
                else:
                    log.info("kill success %s" % (t_name))
        return

    def run_pasue_threads(self, s_ip=None, p_name=None, t_name=None):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description: running 线程
        :param s_ip: 节点IP
        :param p_name: process name
        :param t_name: threads name
        :return:
        """
        cmd = (" ssh %s \" pgrep %s\"" % (s_ip, p_name))
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        if rc != 0:
            log.error("the node have not oRole")
        else:
            cmd = ("ssh %s \" ps -T -p %s | grep pmgr | tail -n 1| awk '{print \$2}'  \"" % (s_ip, stdout))
            log.info(cmd)
            rc, final = commands.getstatusoutput(cmd)
            if rc != 0:
                log.error("oPmgr have node find")
                os._exit(1)
            else:
                print final
                cmd = ("ssh %s \" kill -18 %s\"" % (s_ip, final))
                log.info(cmd)
                rc, finals = commands.getstatusoutput(cmd)
                if rc != 0:
                    log.error("kill %s fail" % (t_name))
                else:
                    log.info("kill success %s" % (t_name))
        return

    def time_limit(self, interval):
        """
        :Author: Liu he
        :Date: 2018-8-13
        :Description:超时检测
        :param interval: limit time
        :return:
        """

        def wraps(func):
            def handler():
                raise RuntimeError()

            def deco(*args, **kwargs):
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(interval)
                res = func(*args, **kwargs)
                signal.alarm(0)
                return res

            return deco

        return wraps

    def get_unuse_disk_uuid(self, s_ip=None):
        '''
        :Author: Liu he
        :Date: 2018-8-13
        :Description:获取节点内盘的uuid
        :param node_ids: 节点id
        :return:
        =========
            修改排除已挂载的硬盘作为空闲盘
        '''
        node_ids = self.get_node_id_by_ip(s_ip)
        uuids = []
        cmd = ("ssh %s \"pscli --command=get_node_stat --ids=%s\"" % (s_ip, node_ids))
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        d_list = stdout.split("\n")
        for disk_info in d_list[4:]:
            disk_id = disk_info.strip(" ").split(" ")[0]
            if disk_id == "0":
                d_uuid = disk_info.strip(" ").split(" ")[-1]
                d_name = disk_info.strip(" ").split(" ")[8]
                cmd2 = ("ssh %s \" df -h | grep %s\"" % (s_ip, d_name))
                rc, stdout2 = commands.getstatusoutput(cmd2)
                if rc != 0:
                    uuids.append(d_uuid)
        if uuids:
            log.info("from node (ID) %s get unuse disk uuid is %s" % (node_ids, uuids))
            return uuids
        else:
            log.info("the node %s have not disk, need check mount disk " % (node_ids))
            os._exit(-1)

    def get_all_data_disk_id(self):
        '''
        :By:Diws
        :Date:20181009
        :return:list,所有共享盘ID
        '''
        disk_ids = []
        nodes = osan.get_nodes(s_ip=deploy_ips)
        for n_id in nodes:
            cmd = ("ssh root@%s ' pscli --command=get_disks --node_ids=%s'" % (deploy_ips[0], str(n_id)))
            log.info(cmd)
            res, output = commands.getstatusoutput(cmd)
            if res != 0:
                log.info("Get disks failed.")
                exit(1)
            else:
                output = json.loads(output)
                output = output['result']
                for i in range(len(output['disks'])):
                    if output['disks'][i]['usage'] == 'DATA':
                        disk_ids.append(output['disks'][i]['id'])
        disk_ids = list(set(disk_ids))
        if 0 in disk_ids:
            disk_ids.remove(0)
        return disk_ids

    def add_disks(self, s_ip=None, node_ids=None, uuid=None, usage=None, storage_id="2"):
        '''
        :Author: Liu he
        :Date: 2018-8-13
        :Description:添加硬盘
        :param node_ids: 节点id
        :param uuid: 硬盘的uuid
        :param usage: (DATA,SHARE)
        :return:
        ========================
        修改：添加参数判断功能，去掉添加失败重试函数重试方法，添加成功及返回成功，失败直接退出
            node_ids 如果手动写就按照手动写的执行，如果不写就按照是s_ip的地址拿去node id
        '''
        time.sleep(10)
        if node_ids is None:
            node_ids = self.get_node_id_by_ip(s_ip)
        us_list = [s_ip, node_ids, uuid, usage, storage_id]
        if all(us_list):
            while True:
                disk_state = disk().check_disk_state(s_ip, uuid)
                log.info("The disk's state is %s" % (disk_state))
                if disk_state == 'DISK_STATE_HEALTHY':
                    break
                time.sleep(30)
            # data_disk_ids = re.sub('\[|\]| ', '', str(self.get_all_data_disk_id()))
            # cmd = (
            # "ssh root@%s '/home/parastor/cli/pscli --command=change_disk_speed_level --disk_ids=%s --speed_level=MID'" % (
            # deploy_ips[0], data_disk_ids))
            # res, output = commands.getstatusoutput(cmd)
            # if res != 0:
            #     print output
            cmd = (
                    "ssh %s \"pscli --command=add_disks --node_ids=%s --disk_uuids=%s --usage=%s --storage_pool_id=%s\"" % (
                s_ip, node_ids, uuid, usage, storage_id))
            log.info(cmd)
            rc, stdout = commands.getstatusoutput(cmd)
            if rc != 0:
                log.info("add disk fail!will EXIT.Error Info: %s" % (stdout))
                time.sleep(10)
                os._exit(1)
            else:
                log.info("add %s disk success" % (usage))
                return
        else:
            log.error("iterable is error: \n  s_ip:%s \n node_ids:%s \n uuid:%s \n usage:%s \n storage_id:%s " % (
                s_ip, node_ids, uuid, usage, storage_id))
            os._exit(1)

    # ===================================================
    # latest date :2018-08-1
    # author: wangxiang
    # ===================================================
    # 2018-08-1:
    # 修改者:wangxiang
    # 1.创建
    def get_share_monopoly_disk_ids(self, s_ip, node_id):
        """
        Description: 获取本节点的所有共享硬盘和数据硬盘
        :param s_ip(str):
        :param node_id(int):
        :return:
        """
        cmd = ("ssh %s pscli --command=get_disks --node_ids=%s" % (s_ip, node_id))
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        else:
            msg = json.loads(stdout)
            share_disk_names = []
            monopoly_disk_names = []
            disks_pool = msg['result']['disks']
            for disk in disks_pool:
                if disk['usage'] == 'SHARED' and disk['usedState'] == 'IN_USE' and disk[
                    'state'] == 'DISK_STATE_HEALTHY':
                    share_disk_names.append(disk['devname'])
                elif disk['usage'] == 'DATA' and disk['usedState'] == 'IN_USE' and disk[
                    'state'] == 'DISK_STATE_HEALTHY':
                    monopoly_disk_names.append(disk['devname'])

        return share_disk_names, monopoly_disk_names

    # ===================================================
    # latest date :2018-08-1
    # author: wangxiang
    # ===================================================
    # 2018-08-1:
    # 修改者:wangxiang
    # 1.创建
    def get_diskid_by_name(self, s_ip, node_id, disk_name):
        """
        Description: 根据磁盘名字获取磁盘id
        :param s_ip(str):
        :param node_id(int):
        :param disk_name(str):
        :return: disk_id
        """
        cmd = "ssh %s pscli --command=get_disks --node_ids=%s" % (s_ip, node_id)
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        else:
            result = json.loads(stdout)
            disk_list = result['result']['disks']
            for disk in disk_list:
                if disk['devname'] == disk_name:
                    return disk['id']
        return None

    # ===================================================
    # latest date :2018-08-1
    # author: wangxiang
    # ===================================================
    # 2018-08-1:
    # 修改者:wangxiang
    # 1.创建
    def get_physicalid_by_name(self, node_ip, disk_name):
        """
        Description: 获取某个节点的一个硬盘的物理id （2:0:0:1）
        :param node_ip: 节点ip
        :param disk_name:硬盘名字
        :return:
        """
        cmd = 'ssh %s "lsscsi"' % node_ip
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        else:
            list_stdout = stdout.split('\n')
            for mem in list_stdout:
                if disk_name in mem:
                    list_mem = mem.split()
                    id = list_mem[0]
                    id = id[1:-1]
                    return id
        return None

    def get_name_by_physicalid(self, node_ip, physicalid):
        """
        Description: 根据物理硬盘id，获取某个节点的一个硬盘的名字
        :param node_ip: 节点ip
        :param physicalid:硬盘物理ID:2:0:0:0
        :return:
        """
        cmd = 'ssh %s "lsscsi"' % node_ip
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        else:
            list_stdout = stdout.split('\n')
            for mem in list_stdout:
                if physicalid in mem:
                    list_mem = mem.split()
                    id = list_mem[-1]
                    id = id[:]
                    return id
        return None

    # ===================================================
    # latest date :2018-08-1
    # author: wangxiang
    # ===================================================
    # 2018-08-1:
    # 修改者:wangxiang
    # 1.创建
    def remove_disk(self, node_ip, disk_id, disk_usage):
        """
        Description: 拔出某个节点的一个硬盘
        :param node_ip:要拔硬盘的节点ip
        :param disk_id:硬盘的物理id(2:0:0:0)
        :param disk_usage:硬盘的用途(DATA   SHARED)
        :return:
        """
        if not disk_id == None:
            # cmd = 'ssh %s \"echo scsi remove-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id)
            cmd = 'ssh %s "echo 1 > /sys/class/scsi_device/%s/device/delete"' % (node_ip, disk_id)
            log.info(cmd)
            log.info('node %s remove disk %s, disk usage is %s' % (node_ip, disk_id, disk_usage))
            rc, stdout = commands.getstatusoutput(cmd)
            log.info(stdout)
            if 0 != rc:
                log.error('node %s remove disk %s fault!!!' % (node_ip, disk_id))
                os._exit(1)
            else:
                time.sleep(5)
        else:
            log.info('%s is  None!' % disk_id)
            os._exit(1)
        time.sleep(5)
        return

    # ===================================================
    # latest date :2018-08-1
    # author: wangxiang
    # ===================================================
    # 2018-08-1:
    # 修改者:wangxiang
    # 1.创建
    def insert_disk(self, node_ip, disk_id, disk_usage):
        """
        Description: 插入某个节点的一个硬盘
        :param node_ip:
        :param disk_id:
        :param disk_usage:
        :return:
        """
        cmd = 'ssh %s \"echo scsi add-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id)
        log.info(cmd)
        log.info('node %s add disk %s, disk usage is %s' % (node_ip, disk_id, disk_usage))
        rc, stdout = commands.getstatusoutput(cmd)
        if 0 != rc:
            log.error('node %s add disk %s fault!!!' % (node_ip, disk_id))
            os._exit(1)
        time.sleep(5)
        cmd = 'ssh %s \"lsscsi\"' % node_ip
        rc, stdout = commands.getstatusoutput(cmd)
        log.info(stdout)
        return

    # ===================================================
    # latest date :2018-08-2
    # author: wangxiang
    # ===================================================
    # 2018-08-1:
    # 修改者:wangxiang
    # 1.创建
    def run_down_disk_wait(self, s_ip, timeout):
        """
        修改磁盘超时参数
        :param s_ip(str):节点IP
        :param timeout(str): 超时时间
        :return:
        """
        cmd = "ssh %s pscli --command=update_param --section=MGR --name=disk_isolate2rebuild_timeout --current=%s " % (
            s_ip, timeout)
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        if 0 != rc:
            log.error('update param failed!!!')
            os._exit(1)
            return False

    # ==================================================
    # latest date :2018-08-14
    # author: wangxiang
    # ===================================================
    # 2018-08-14:
    # 修改者:wangxiang
    # 1.创建
    def run_down_node_wait(self, s_ip, timeout):
        """
        修改节点超时参数
        :param s_ip(str):节点IP
        :param timeout(str): 超时时间
        :return:
        """
        cmd = "ssh %s pscli --command=update_param --section=MGR --name=node_isolate_timeout --current=%s " % (
            s_ip, timeout)
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        if 0 != rc:
            log.error('update param failed!!!')
            os._exit(1)
            return False

    def os_up(self, nums, esxi_ip, u_name, pw):
        """
        :Auther: Liu he
        :Description: 将虚拟机开机，10分钟未开机认为开机失败
        :param nums: 节点ID
        :param esxi_ip: 虚拟机IP
        :param u_name: 虚拟机用户名（管理员）
        :param pw: 虚拟机密码
        :return:
        """
        for i in range(600):
            vm_status = self.get_vm_status(esxi_ip, u_name, pw, nums).strip()
            if vm_status == "Powered off":
                log.info("Return by function \"os_up\" :will send power on to vm %s." % (nums))
                ReliableTest.run_up_vir_node(esxi_ip=esxi_ip, u_name=u_name, pw=pw, vm_id=nums)
                time.sleep(20)
            elif vm_status == "Powered on":
                log.info("Return by function \"os_up\" :waiting the os up finish.")
                return
            elif i == 599:
                log.info("Return by function \"os_up\" :The vm lost when waiting 600s, "
                         "you need check vm os,Error Info: %s " % (vm_status))
                os._exit(1)
            else:
                time.sleep(1)

    def up_cpu(self, n_ip):
        """
        :Auther: Liu he
        :Description: 提高CPU利用率
        :return:
        """
        cmd = (
                "ssh %s \" for i in \\`seq 1 $(cat /proc/cpuinfo |grep \"physical id\" |wc -l)\\`; do dd if=/dev/zero of=/dev/null & done\"" % (
            n_ip))
        rc, stdout = commands.getstatusoutput(cmd)
        log.info(cmd)
        if rc != 0:
            log.error("up CPU use ratio failed!!!!,Error info:%s " % (stdout))
            os._exit(1)
        else:
            log.info("up CPU use ratio success")
            return

    def recover_cpu(self, n_ip):
        """
        :Auther: Liu he
        :Description:恢复CPU利用率
        :return:
        """
        cmd = (
                "ssh %s \" for i in \\`seq 1 $(cat /proc/cpuinfo |grep \"physical id\" |wc -l)\\`; do pkill -9 dd & done\"" % (
            n_ip))
        rc, stdout = commands.getstatusoutput(cmd)
        if rc != 0:
            log.error("recover CPU use ratio failed!!!!!")
            os._exit(1)
        else:
            log.info("recover CPU use ratio success")

    def get_unuse_mem(self, ips):
        """
        :Auther: Liu he
        :Description:获取未使用的内存，单位GB
        :param ips:
        :return:
        """

        cmd = ("ssh %s \"free -g |awk \"NR==2\"|awk \'{print\$4}\' \"" % (ips))
        rc, stdout = commands.getstatusoutput(cmd)
        if rc != 0:
            log.error("get member failed!!!,Error Infor:%s" % (stdout))
            os._exit(1)
        else:
            log.info("get unuse memory :%s" % (stdout))
            return stdout

    def up_member(self, n_ip):
        """
        :Auther: Liu he
        :Description: 将剩余内存全部占用默认占用100s
        :param n_ip:
        :return:
        """
        mem_size = self.get_unuse_mem(n_ip)
        up_mem_size = int(mem_size)
        if up_mem_size == 0:
            log.info("Now memory is full,will do not Increase the memory")
            time.sleep(100)
            return
        else:
            log.info("%s node will run test_mem ,will consume memory %sGB" % (n_ip, mem_size))
            cmd = (
                    "ssh %s \"echo \\\"import time \ns = ' ' * (%s * 1024 * 1024 * 1024) \ntime.sleep(100) \n\\\">/root/test_mem.py\"" % (
                n_ip, up_mem_size))
            rc, stdout = commands.getstatusoutput(cmd)
            if rc != 0:
                log.error(" %s create mem_test faill,info: %s" % (n_ip, stdout))
                os._exit(1)
            else:
                log.info("will running test_mem")
                cmd = ("ssh %s \"python /root/test_mem.py\"" % (n_ip))
                rc, stdout = commands.getstatusoutput(cmd)
                if rc != 0:
                    log.error("%s Runing test_mem.py failed!!!!.error info: %s " % (n_ip, stdout))
                    os._exit(1)
                else:
                    log.info("runing test_mem.py finish,will clean")
                    cmd = ("ssh %s \" rm -rf  /root/test_mem.py\"" % (n_ip))
                    commands.getstatusoutput(cmd)
        return

    def get_node_state(self, node_ip=None):
        '''
        :Auther: Liu he
        :Description: 获取节点服务状态
        :param node_ip:需要获取状态的节点IP
        :return: 节点的状态 :NODE_STATE_HEALTHY ,NODE_STATE_ISOLATE  NODE_STATE_ISOLATE_REBUILDING  NODE_STATE_ZOMBIE
        '''
        if node_ip:
            node_id = node.get_node_id_by_ip(node_ip)
            cmd = ('ssh %s "pscli --command=get_nodes --ids=%s"' % (deploy_ips[0], node_id))
            log.info(cmd)
            (rc, stdout) = commands.getstatusoutput(cmd)
            if rc != 0:
                log.error("Error!get nodes info failed:%s" % stdout)
                os._exit(1)
            else:
                result = json.loads(stdout)
                node_info = result['result']['nodes'][0]
                node_state = node_info['state']
                log.info("Return by \"get_node_state\":The node %s state is %s" % (node_ip, node_state))
                return node_state
        else:
            log.error("Error!node ip is invalid!!: %s" % node_ip)
            os._exit(1)

    def get_access_zones(self, node_ip=None):
        '''
        :Description:获取所有访问分区
        :param node_ip:节点IP
        :return: 访问分区ID列表
        '''
        if node_ip:
            cmd = ('ssh %s "pscli --command=get_access_zones"' % node_ip)
            log.info(cmd)
            (rc, stdout) = commands.getstatusoutput(cmd)
            if 0 != rc:
                log.error("Error!get nodes info failed:%s" % stdout)
                os._exit(1)
            else:
                result = json.loads(stdout)
                zone_info = result['result']['access_zones']
                access_zone_ids = []
                for zone in zone_info:
                    access_zone_ids.append(zone['id'])
                log.info("Return by \"get_access_zones\":get access_zone_id:%s" % (access_zone_ids))
                return access_zone_ids
        else:
            log.error("Error!node ip is invalid!! %s" % node_ip)
            os._exit(1)

    def get_node_ids_by_zone(self, zone_id=None):
        '''
        :Description:根据访问分区id获取分区中节点ID
        :param zone_id: 访问分区ID
        :return: 访问分区节点ID列表
        '''
        if zone_id:
            cmd = ('ssh %s "pscli --command=get_access_zones"' % deploy_ips[0])
            log.info(cmd)
            (rc, stdout) = commands.getstatusoutput(cmd)
            if 0 != rc:
                log.error("Error!get nodes info failed:%s" % stdout)
                os._exit(1)
            else:
                result = json.loads(stdout)
                zone_info = result['result']['access_zones']
                for zone in zone_info:
                    if zone['id'] == zone_id:
                        return zone['node_ids']
                log.error("can not find any node in the access zone!")
        else:
            log.error("Error!node ip is invalid!! %s" % deploy_ips[0])
            os._exit(1)

    def change_process_state(self, node_ip=None, process_name=None, up_down=None):
        """
        :Description:将某一节点的进程杀死,并不让其拉起或让其拉起
        :param node_ip:
        :param process_name:
        :return:
        """
        if all((node_ip, process_name, up_down)):
            if up_down == 'down':
                cmd_bin = (
                        'ssh %s "mv /home/parastor/bin/%s /home/parastor/bin/%s.bak"' % (
                node_ip, process_name, process_name))
                (rc, stdout) = commands.getstatusoutput(cmd_bin)
                if 0 != rc:
                    log.error("update process bin file failed!info:%s" % stdout)
                else:
                    log.info("update process bin file successful!")
                ReliableTest.run_kill_process(node_ip, process_name)
            elif up_down == 'up':
                cmd_bin = (
                        'ssh %s "mv /home/parastor/bin/%s.bak /home/parastor/bin/%s"' % (
                node_ip, process_name, process_name))
                (rc, stdout) = commands.getstatusoutput(cmd_bin)
                if 0 != rc:
                    log.error("update process bin file failed!info:%s" % stdout)
                else:
                    log.info("update process bin file successful!")
            else:
                log.error("param is invalid!info:%s" % up_down)
        else:
            log.error("exsits some param invalid!info:%s,%s,%s" % (node_ip, process_name, up_down))

    def get_unmap_vip(self, s_ip):
        vips = get_config.get_vip(conf_file)
        vip_list = com2.analysis_vip(vips[0])
        target_list = Lun_managerTest.oSan().get_map_target(s_ip=s_ip)
        for iqn in target_list:
            iqn = iqn.encode("utf-8")
            lun_map_vip = iqn.split("target.")[-1]
            if lun_map_vip in vip_list:
                vip_list.remove(lun_map_vip)
        return vip_list

    def get_map_vip(self, s_ip):
        target_list = Lun_managerTest.oSan().get_map_target(s_ip=s_ip)
        lun_map_vips = []
        for iqn in target_list:
            iqn = iqn.encode("utf-8")
            lun_map_vip = iqn.split("target.")[-1]
            lun_map_vips.append(lun_map_vip)
        return lun_map_vips

    def get_unmap_lun(self, s_ip=None):
        '''
        date    :   2018-11-20
        Description :   获取没有进行lun 映射的lun ID
        return  :   lun ID
        '''
        log.info("will get unmap lun ids")
        if None == s_ip:
            log.error("Please input the correct ip.")
            os._exit(1)
        else:
            lun_ids = com2.get_lun(s_ip)
            cmd = ("ssh %s \"pscli --command=get_lun_maps\"" % (s_ip))
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
                    lun_id = final['lun_maps'][i]['lun_id']
                    if lun_id in lun_ids:
                        lun_ids.remove(lun_id)
            lun_ids.sort()
            return lun_ids

    def get_all_vip_address(self):
        '''
        date    :   2018-05-15
        Description :   获取VIP
        param   :   s_ip : iscsi服务端IP;n_id : 节点ID
        return  :   VIP(二元列表)
        '''
        vip_list = []
        for s_ip in deploy_ips:
            if False is ReliableTest.check_ping(s_ip):
                continue
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
                            vip_list.extend(vip['vip_addresses'])
                    log.info("Get VIP list: %s" % (vip_list))
                    return vip_list

    def get_lun_size_dict(self):
        """
        :auther: Liu he
        :description: 获取lunID和容量
        :param s_ip:
        :return: 返回LUN ID和LUN容量对应的字典
        """
        lun_size_dict = {}
        cmd = ("pscli --command=get_luns")
        log.info(cmd)
        res, final = com2.run_pscli_cmd(pscli_cmd=cmd, time_out=300, times=1)
        if (res != 0):
            log.error(final)
            log.error("Get luns error.")
            exit(1)
        else:
            log.info("Get luns success.")
            final = json.loads(final)
            final = final['result']
            # print final
            for i in range(0, final['total']):
                id = final["luns"][i]["id"]
                # print final["luns"][i]['total_bytes']
                lun_size =final["luns"][i]['total_bytes']
                lun_size_dict[id] = lun_size
        return lun_size_dict

    def get_zk_total_num(self):
        """
        :auther:Liu he
        :description: 获取集群zk节点数量
        :return:
        """
        cmd = ("pscli --command=get_cluster_overview")
        rc, output = com2.run_pscli_cmd(pscli_cmd=cmd, time_out=300, times=1)
        if rc != 0:
            log.error("get cluster overview failed:error info:%s" % (output))
        else:
            output = json.loads(output)
            zk_infos = output["result"]["zk_servers"]
            return len(zk_infos)

    def get_storage_pool_size(self, id=1):
        """
        :Auther:Liuhe
        :param pool_id:存储池ID，为1
        :return: 返回存储池1的总容量，单位字节
        """
        cmd = ("pscli --command=get_storage_pools")
        rc, output = com2.run_pscli_cmd(pscli_cmd=cmd, time_out=300, times=1)
        if rc !=0:
            log.error("get_storage_pools cmd failed. error infor:%s" % (output))
            os._exit(1)
        else:
            output = json.loads(output)
            pool_infos = output["result"]["storage_pools"]
            for i in range(len(pool_infos)):
                pool_id = pool_infos[i]["id"]
                if pool_id == id:
                    return pool_infos[i]["total_bytes"]

    def get_lun_name(self):
        '''
        date    :   Liu he
        Description :   获取lun name
        return  :   lun ID
        '''
        lun_names = []
        cmd = ("pscli --command=get_luns")
        log.info(cmd)
        res, final = com2.run_pscli_cmd(pscli_cmd=cmd, time_out=300, times=1)
        if (res != 0):
            log.error(final)
            log.error("Get luns error.")
            exit(1)
        else:
            log.info("Get luns success.")
            final = json.loads(final)
            final = final['result']
            for i in range(0, final['total']):
                lun_names.append(final['luns'][i]['name'])
        return lun_names

    def get_osan_los_master(self, id):
        log.info("will find LUN ID:%s. where are in node list" % (id))
        for ip in deploy_ips:
            node_id = node.get_node_id_by_ip(ip)
            cmd = ("ssh %(node_ip)s \"/home/parastor/tools/nWatch -t oSan -i %(id)s -c oSan#get_lcache\"" % {'node_ip': ip,
                                                                                                             'id': node_id})
            rc, output = commands.getstatusoutput(cmd)
            log.info(cmd)
            lun_infos_list = output.split("\n")
            lun_id_list = []
            for out in lun_infos_list:
                if "LUN ID" in out:
                    lun_id = out.split(":")[-1].strip()
                    lun_id_list.append(lun_id)
            chk_id_list = list(set(lun_id_list))
            for chk_id in chk_id_list:
                if int(chk_id) == id:
                    log.info("Get the lun in node %s. need set read ahead lun ID is %s" % (ip, id))
                    return node_id


    def set_cache(self, id, mode, size=0, s_ip=None, stype="dpc_lun_ra"):
        mode_status = {"0": "down", "1": "auto", "2": "manual", }
        node_id = self.get_node_id_by_ip(s_ip)
        # if set_lun_node_id is None:
        for i in range(4):
            set_lun_node_id = self.get_osan_los_master(id)
            if set_lun_node_id is not None:
                # set_lun_node_id = get_osan_los_master(id)
                set_lun_node_ip = node.get_node_ip_by_id(set_lun_node_id)
                break
            if i == 3:
                log.error("get set lun node ID is :%s " % (set_lun_node_id))
                os._exit(1)
            time.sleep(60)
        if mode == "2":
            size = str(3 * 1) + "M"  # 如果mode=2 需要设置size为条带宽度*1M大小
        log.info("set read ahead osan node id: %(node_id)s , node ip: %(ip)s" % {'node_id': set_lun_node_id,
                                                                                 'ip': set_lun_node_ip})
        cmd = ("ssh {} \"/home/parastor/tools/nWatch -t oSan -i {} -c oSan#{} -a \\\"{} {} {}\\\"\"".format(set_lun_node_ip,
                                                                                                            set_lun_node_id,
                                                                                                            stype, id, mode,
                                                                                                            size))
        log.info(cmd)
        res, output = commands.getstatusoutput(cmd)
        log.info(output)
        if res != 0 or "can not find lunsb" in output:
            log.info(output)
            log.error("The node %s set %s is failed, please check" % (node_id, stype))
            os._exit(1)
        else:
            time.sleep(2)
            '''验证是否生效'''
            cmd = ("ssh %s \"/home/parastor/tools/nWatch -t oSan -i %s -c oSan#dpc_lun_status -a \"%s\"\"" % (
                set_lun_node_ip, set_lun_node_id, id))
            log.info(cmd)
            rc, output = commands.getstatusoutput(cmd)
            if rc != 0:
                log.error("get lun read ahead status failed")
            elif "can not find lunsb for " in output:
                log.info("The lun have node set read ahead")
            else:
                lun_status = output.split(", ")[3].split(':')[-1].strip()
                log.info("get lun %(lunid)s lun read head status: %(status)s" % {'lunid': id, 'status': lun_status})
                if int(lun_status) == int(mode):
                    log.info("The node %s set %s success.\nGet oSan#dpc_lun_status:%s " % (node_id, stype, output))
                else:
                    log.error("The node %s set %s failed.\n%s " % (node_id, stype, output))
                    os._exit(1)

    def get_targets_id_and_vip(self, s_ip):
        '''
        date    :   Liu he
        Description :   获取target id和vip
        return  :   字典类型id 和 vip
        '''
        target_ids = {}
        if None is s_ip:
            log.error("Please input the correct ip.")
            os._exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=get_targets\"" % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if (res != 0):
                log.error(final)
                log.error("Get targets ID error.")
                os._exit(1)
            else:
                log.info("Get targets ID success.")
                final = json.loads(final)
                final = final['result']
                for i in range(0, final['total']):
                    target_id = final['targets'][i]['id']
                    vip = final['targets'][i]['ipAddr']
                    target_ids[vip] = target_id
                return target_ids

    def bond_conf(self, node_ip=None, eth_list=None, bond_name=None, mode=1, switch=1):
        """
        :Description:对节点的某两个网卡进行bond4配置
        :param node_ip: 节点IP
        :param eth_list: 网卡，需给列表
        :param net_name: bond名字，eg.bond0,bond1...
        :param mode: bond模式，0轮询模式，1主备模式，2均衡模式
        :param switch: 1配置bond,0清除bond
        :return:
        """
        if len(eth_list) < 2:
            log.error("Ethernet is less than 2.Can't configure bond.")
            os._exit(1)
        net_conf_list = []
        for eth_name in eth_list:
            net_conf = ('/etc/sysconfig/network-scripts/ifcfg-%s' % eth_name)
            net_conf_list.append(net_conf)
            self.network_test(node_ip, eth_name, 'down')
        if switch == 1:
            # 修改原有网卡配置文件
            log.info("Modify the network card configuration file.")
            for net_conf in net_conf_list:
                log.info("Modify the ethernet config %s." % net_conf)
                cmd1 = ("ssh %s 'sed -i \"s/IPADDR/#&/g\" %s'" % (node_ip, net_conf))
                os.system(cmd1)
                cmd2 = ("ssh %s 'sed -i \"s/NETMASK/#&/g\" %s'" % (node_ip, net_conf))
                os.system(cmd2)
                cmd3 = ("ssh %s 'sed -i \"s/BOOTPROTO.*/BOOTPROTO=none/g\" %s'" % (node_ip, net_conf))
                os.system(cmd3)
                cmd4 = ("ssh %s 'sed -i \"\$a MASTER=%s\" %s'" % (node_ip, bond_name, net_conf))
                os.system(cmd4)
                cmd5 = ("ssh %s 'sed -i \"\$a SLAVE=yes\" %s'" % (node_ip, net_conf))
                os.system(cmd5)
            for eth_name in eth_list:
                log.info("Make the Ethernet is disabled.Eth: %s." % eth_name)
                self.network_test(node_ip, eth_name, 'up')

            # 创建bond网卡配置文件
            log.info("Create bond ethernet configuration file.")
            cmd_ip = ("ssh %s 'cat %s' | grep IPADDR | awk -F '=' '{print $2}'" % (node_ip, net_conf_list[0]))
            io_ip = commands.getoutput(cmd_ip)
            cmd_mask = ("ssh %s 'cat %s' | grep NETMASK | awk -F '=' '{print $2}'" % (node_ip, net_conf_list[0]))
            io_mask = commands.getoutput(cmd_mask)
            bond_ifcfg = ("/etc/sysconfig/network-scripts/ifcfg-%s" % bond_name)
            cmd_create = ("ssh %s 'echo 3>%s'" % (node_ip, bond_ifcfg))
            os.system(cmd_create)
            cmd1 = ("ssh %s 'echo \"DEVICE=%s\" >> %s'" % (node_ip, bond_name, bond_ifcfg))
            os.system(cmd1)
            cmd2 = ("ssh %s 'sed -i \"\$a TYPE=Ethernet\" %s'" % (node_ip, bond_ifcfg))
            os.system(cmd2)
            cmd3 = ("ssh %s 'sed -i \"\$a ONBOOT=yes\" %s'" % (node_ip, bond_ifcfg))
            os.system(cmd3)
            cmd4 = ("ssh %s 'sed -i \"\$a BOOTPROTO=static\" %s'" % (node_ip, bond_ifcfg))
            os.system(cmd4)
            cmd5 = ("ssh %s 'sed -i \"\$a IPADDR=%s\" %s'" % (node_ip, io_ip, bond_ifcfg))
            os.system(cmd5)
            cmd6 = ("ssh %s 'sed -i \"\$a NETMASK=%s\" %s'" % (node_ip, io_mask, bond_ifcfg))
            os.system(cmd6)
            cmd7 = ("ssh %s 'sed -i \"\$a BONDING_MASTER=yes\" %s'" % (node_ip, bond_ifcfg))
            os.system(cmd7)
            #cmd8 = ("ssh %s 'sed -i \"\$a BONDING_OPTS=\"mode=%s miimon=100\"\" %s'" % (node_ip, mode, bond_ifcfg))
            #os.system(cmd8)

            log.info("Loading up the %s module and ifup the %s" % (bond_name, bond_name))
            dist_conf = "/etc/modprobe.d/modprobe.conf"
            cmd_create = ("ssh %s 'echo 3>%s'" % (node_ip, dist_conf))
            os.system(cmd_create)
            cmd_conf1 = ("ssh %s 'echo \"alias %s bonding\" >> %s'" % (node_ip, bond_name, dist_conf))
            os.system(cmd_conf1)
            cmd_conf2 = ("ssh %s 'sed -i \"\$a options %s miimon=100 mode=%s\" %s'" % (node_ip, bond_name, mode, dist_conf))
            os.system(cmd_conf2)

            cmd_start = ("ssh %s 'modprobe bonding'" % node_ip)
            rc1 = os.system(cmd_start)
            cmd_check = ("ssh %s 'lsmod' | grep bond" % node_ip)
            final = commands.getoutput(cmd_check)
            cmd_up = ("ssh %s 'ifup %s'" % (node_ip, bond_name))
            rc2 = os.system(cmd_up)
            for eth_name in eth_list:
                log.info("Make the Ethernet is up.Eth: %s." % eth_name)
                self.network_test(node_ip, eth_name, 'up')
            log.info("The bond modprobe info: %s" % final)
            if rc1 == 0 and rc2 == 0 and final != '':
                log.info("The node %s network bond config successful." % node_ip)
                cmd = ("ssh %s 'cat /proc/net/bonding/%s'" % (node_ip, bond_name))
                final = commands.getoutput(cmd)
                log.info(final)
            else:
                log.error("The node %s network bond config failed." % node_ip)
                os._exit(1)

        elif switch == 0:
            log.info("Unload the %s module and ifdown the %s." % (bond_name, bond_name))
            cmd_close = ("ssh %s 'modprobe -r bonding'" % node_ip)
            rc1 = os.system(cmd_close)
            cmd_down = ("ssh %s 'ifdown %s'" % (node_ip, bond_name))
            rc2 = os.system(cmd_down)
            if rc1 == 0 and rc2 == 0:
                log.info("The node %s network bond close successful." % node_ip)
            else:
                log.info("The node %s network bond close failed." % node_ip)

            # 恢复原有网卡配置文件
            log.info("Restore the network card configuration file.")
            for net_conf in net_conf_list:
                log.info("Modify the ethernet config %s." % net_conf)
                cmd0 = ("ssh %s 'sed -i \"s/BOOTPROTO=.*/BOOTPROTO=static/g\" %s'" % (node_ip, net_conf))
                os.system(cmd0)
                cmd1 = ("ssh %s 'sed -i \"s/#IPADDR/IPADDR/g\" %s'" % (node_ip, net_conf))
                os.system(cmd1)
                cmd2 = ("ssh %s 'sed -i \"s/#NETMASK/NETMASK/g\" %s'" % (node_ip, net_conf))
                os.system(cmd2)
                cmd3 = ("ssh %s 'sed -i \"/MASTER/d\" %s'" % (node_ip, net_conf))
                os.system(cmd3)
                cmd4 = ("ssh %s 'sed -i \"/SLAVE/d\" %s'" % (node_ip, net_conf))
                os.system(cmd4)
            bond_ifcfg = ("/etc/sysconfig/network-scripts/ifcfg-%s" % bond_name)
            cmd_del = ("ssh %s 'rm -f %s'" % (node_ip, bond_ifcfg))
            os.system(cmd_del)

            for eth_name in eth_list:
                log.info("Make the Ethernet is down.Eth: %s." % eth_name)
                self.network_test(node_ip, eth_name, 'down')
            for eth_name in eth_list:
                log.info("Make the Ethernet is up.Eth: %s." % eth_name)
                self.network_test(node_ip, eth_name, 'up')
            log.info("All network has returned to normal.")
        else:
            log.error("Your Switch is invalid values.Make sure it is one of 1/2")
            os._exit(1)

    def get_vips_with_node(self):
        """
        :function:According to the node for getting the VIP and create a dictionary
        :return: a dictionary, key-node_ip, values-vips.
        """
        master_ip = self.get_master_oRole(deploy_ips[0])
        master_id = node.get_node_id_by_ip(master_ip)
        cmd = ("ssh %s '/home/parastor/tools/nWatch -t oRole -i %s -c oPmgr#pmgr_vip_ctxt_dump'"
               "| grep addr | awk -F 'addr:' '{print $2}'" % (master_ip, master_id))
        log.info(cmd)
        rc, final = commands.getstatusoutput(cmd)
        if rc != 0:
            log.error("Run cmd failed.info:%s" % final)
        else:
            info_list = final.split('\n')
            vip_dict = {}
            for node_ip in deploy_ips:
                node_id = node.get_node_id_by_ip(node_ip)
                vip_dict[node_ip] = []
                jud_info = ("nodeid:%s" % str(node_id))
                for info in info_list:
                    if 'SUPER' not in info and jud_info in info:
                        vip = info.split(',')[0]
                        vip_dict[node_ip].append(vip)
            return vip_dict

    def get_business_nodes(self):
        """
        :function:Access to all business nodes in cluster
        :return: business_nodes_ids list
        """
        cmd = ("ssh %s 'pscli --command=get_access_zones'" % deploy_ips[0])
        rc, final = commands.getstatusoutput(cmd)
        if rc != 0:
            log.error("Get access zones failed.info:%s" % final)
        else:
            result = json.loads(final)
            nodes = result['result']['access_zones'][0]['nodes']
            node_ids = []
            for node in nodes:
                node_ids.append(node['node_id'])
            return node_ids

class disk():
    '''
    get_rw_disk_by_node_id
    get_disk_phyid_by_name
    get_diskid_by_name
    get_disk_uuid_by_name
    delete_disk
    add_disk
    get_disk_pool
    get_diskid_in_disk_pool
    get_nodeinfo_by_diskid
    get_storage_poolid_by_diskid
    get_disk_id_by_uuid
    expand_disk_2_storage_pool
    get_lun_size
    get_jnl_replica
    get_disk_state
    get_interface_node
    '''

    def get_rw_disk_by_node_id(self, s_ip=None, node_id=None, disk_type=None):
        '''
        :Usage : get disks which are reading or writing by nodeid
        :param s_ip: server ip
        :param node_id: node id to check
        :disk_type : data or shared
        :return: list,list of disk names
        '''
        disks = []
        cmd = ("ssh %s 'pscli --command=get_disks --node_ids=%s'" % (s_ip, str(node_id)))
        log.info(cmd)
        (res, output) = commands.getstatusoutput(cmd)
        if res != 0:
            log.error("Get disk name failed.")
            os._exit(1)
        else:
            result = json.loads(output)
            disk_list = result['result']['disks']
            for disk in disk_list:
                if disk_type == "share" or disk_type == "SHARE":
                    if disk["usage"] == "SHARED" and disk["usedState"] == "IN_USE":
                        disks.append(disk["devname"])

                else:
                    if disk["usage"] == "DATA" and disk['usedState'] == "IN_USE":
                        disks.append(disk["devname"])
            return disks

    def get_disk_phyid_by_name(self, s_ip=None, disk_name=None):
        '''
        :Usage : get disk physic id by disk name
        :param s_ip: node ip to get the disk
        :param disk_name:disk name ,ex:/dev/sdb
        :return: list,disks' phy id ex:0 0 1 0
        '''
        uuids = []
        for disk in disk_name:
            cmd = ("ssh %s 'lsscsi |grep -w %s'" % (s_ip, disk))
            log.info(cmd)
            (res, output) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error("Get disk uuid failed.")
                os._exit(1)
            else:
                uuids.append(re.sub(':', ' ', re.sub('\[|\]', '', output.split()[0])))
        return uuids

    def get_diskid_by_name(self, s_ip=None, node_id=None, disk_name=None):
        '''
        :Usage : get disk name by node id and disk name
        :param s_ip: server ip
        :param node_id: node id on which to check the disk
        :param disk_name: ex:/dev/sdb
        :return:int, disk id
        '''
        cmd = ("ssh %s 'pscli --command=get_disks --node_ids=%s'" % (s_ip, str(node_id)))
        log.info(cmd)
        (res, output) = commands.getstatusoutput(cmd)
        log.info(output)
        if res != 0:
            log.error("Get disk id failed.")
            os._exit(1)
        else:
            result = json.loads(output)
            disk_list = result['result']['disks']
            for disk in disk_list:
                if disk["devname"] == disk_name:
                    return disk["id"]

    def get_disk_uuid_by_name(self, s_ip=None, node_id=None, disk_name=None):
        '''
        :Usage : get disk uuid by its name and node id
        :param s_ip: server ip
        :param node_id: node where the disk locate
        :param disk_name: ex: /dev/sdb
        :return: str,disk's uuid
        '''
        cmd = ("ssh %s 'pscli --command=get_disks --node_ids=%s'" % (s_ip, str(node_id)))
        rc, stdout = commands.getstatusoutput(cmd)
        log.info(cmd)
        log.info(stdout)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            os._exit(1)
        else:
            result = json.loads(stdout)
            disk_list = result['result']['disks']
            for disk in disk_list:
                if disk['devname'] == disk_name:
                    return disk['uuid']

    def delete_disk(self, s_ip=None, disk_id=None):
        '''
        :Usage : delete disk by pscli command
        :param s_ip: node ip to delete the disk
        :param disk_id: disk id
        :return: None
        '''
        cmd = ("ssh %s 'pscli --command=remove_disks --disk_ids=%s'" % (s_ip, str(disk_id)))
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        log.info(stdout)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            os._exit(1)
        return

    def add_disk(self, s_ip=None, uuid=None, usage=None, node_id=None, err=True):
        '''
        :Usage : add disk on one node through pscli command
        :param s_ip: node ip to add disk
        :param uuid: disk's uuid
        :param usage: data or share
        :return: None
        '''
        time.sleep(15)
        us_list = [s_ip, node_id, uuid, usage]
        if all(us_list):
            for count in range(5):
                disk_state = disk().check_disk_state(s_ip, uuid, err=err)
                log.info("The disk's state is %s" % (disk_state))
                if disk_state == 'DISK_STATE_HEALTHY':
                    break
                time.sleep(20)
        cmd = ("ssh %s 'pscli --command=add_disks --node_ids=%s --disk_uuids=%s --usage=%s'" % (
            s_ip, str(node_id), uuid, usage))
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        log.info(stdout)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            if err:
                os._exit(1)
            else:
                return False
        else:
            log.info("Add disk success.")
            # data_disk_ids = re.sub('\[|\]| ', '', str(self.get_all_data_disk_id()))
            # cmd = ("ssh root@%s '/home/parastor/cli/pscli --command=change_disk_speed_level --disk_ids=%s --speed_level=MID'"
            #        % (deploy_ips[0], data_disk_ids))
            # res, output = commands.getstatusoutput(cmd)
            # if res != 0 :
            #     print output

    def get_disk_pool(self, s_ip=None, ids=None):
        '''
        :Usage : get disk pool by storage id
        :param s_ip:server ip
        :return: list,disk pool id
        '''
        disk_pool_id = []
        cmd = ("ssh %s \"pscli --command=get_storage_pool_stat --ids=%s| awk '{print \$4}'\"" % (s_ip, str(ids)))
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        log.info(stdout)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            os._exit(1)
        else:
            for line in stdout.strip().split("\n"):
                if line == "disk_pool_id" or line == '':
                    continue
                else:
                    disk_pool_id.append(line)
            return disk_pool_id

    def get_diskid_in_disk_pool(self, s_ip=None, s_id=None):
        '''
        :Usage : get disk id by storage id
        :param s_ip:server ip
        :param d_pool_id: storage id
        :return:dict,disk id in the same disk pool
        '''
        disk_pool_id = {}
        disk_id = []
        cmd = ("ssh %s \"pscli --command=get_storage_pool_stat --ids=%s| "
               "awk '(diskid=NF-1)(poolid=NF-2)"
               "{if (poolid>0)print \$poolid,\$diskid;"
               "else if (diskid>0 && poolid<=0)print \$diskid}'\"" % (s_ip, str(s_id)))
        log.info(cmd)
        rc, stdout = commands.getstatusoutput(cmd)
        log.info(stdout)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            os._exit(1)
        else:
            for id in stdout.split("\n"):
                if id == 'disk_pool_id disk_id':
                    continue
                else:
                    ids = id.split()
                    if len(ids) == 2:
                        disk_id = []
                        id_key = ids[0]
                        disk_id.append(ids[1])
                        disk_pool_id[id_key] = disk_id
                    else:
                        disk_id.append(id)
                        disk_pool_id[id_key] = disk_id
            return disk_pool_id

    def get_nodeinfo_by_diskid(self, s_ip=None, disk_id=None):
        '''
        :Usage : get node ctr ip ,node id ,disk name by disk id
        :param s_ip: server ip
        :param disk_id: disk id
        :return: list,int,list
        '''
        osan = common2.oSan()
        node_ids = osan.get_nodes(s_ip=s_ip)
        for node_id in node_ids:
            cmd = ("ssh %s 'pscli --command=get_disks --node_ids=%s'" % (s_ip, str(node_id)))
            log.info(cmd)
            (res, output) = commands.getstatusoutput(cmd)
            log.info(output)
            if res != 0:
                log.error("Get disk id failed.")
                os._exit(1)
            else:
                result = json.loads(output)
                disk_list = result['result']['disks']
                for disk in disk_list:
                    if str(disk["id"]) == str(disk_id):
                        d_name = []
                        ctl_ips = ReliableTest.get_ctl_ips(node_ip=s_ip, node_id=node_id)
                        ips = osan.analysis_vip(ctl_ips)
                        name = disk["devname"]
                        d_name.append(name)
                        return ips, node_id, d_name

    def get_storage_poolid_by_diskid(self, s_ip=None, node_id=None, disk_id=None):
        '''
        :Usage : get strage pool id by disk id
        :param s_ip: server ip
        :param node_id:
        :param disk_id:
        :return:int
        '''
        cmd = ("ssh %s 'pscli --command=get_disks --node_ids=%s'" % (s_ip, str(node_id)))
        log.info(cmd)
        (res, output) = commands.getstatusoutput(cmd)
        log.info(output)
        if res != 0:
            log.error("Get disk info failed.")
            os._exit(1)
        else:
            msg = json.loads(output)
            disks_info = msg["result"]["disks"]
            for disk in disks_info:
                if disk['id'] == disk_id:
                    return disk['storagePoolId']
            log.info("there is not a disk's id is %s!!!" % (str(disk_id)))
            return None

    def get_disk_id_by_uuid(self, s_ip=None, node_id=None, disk_uuid=None, err=True):
        '''
        :Usage : get disk id by its uuid
        :param s_ip:
        :param node_idd:
        :param disk_uuid:
        :return: int
        '''
        cmd = ("ssh %s 'pscli --command=get_disks --node_ids=%s'" % (s_ip, str(node_id)))
        log.info(cmd)
        (res, output) = commands.getstatusoutput(cmd)
        log.info(output)
        if res != 0:
            log.error("Get disk info failed.")
            if err:
                os._exit(1)
            else:
                return False
        else:
            result = json.loads(output)
            disk_list = result['result']['disks']
            for disk in disk_list:
                if disk['uuid'] == disk_uuid:
                    return disk['id']
        return None

    def expand_disk_2_storage_pool(self, s_ip=None, stor_id=None, disk_id=None, err=True):
        '''
        :Usage : add disk to storage pool
        :param s_ip:
        :param stor_id:
        :param disk_id:
        :return:None
        '''
        cmd = ("ssh %s 'pscli --command=expand_storage_pool --storage_pool_id=%s --disk_ids=%s'" % (
            s_ip, str(stor_id), str(disk_id)))
        log.info(cmd)
        (res, output) = commands.getstatusoutput(cmd)
        log.info(output)
        if res != 0:
            log.error("Add disk: %s to storage pool: %s failed." % (str(disk_id), str(stor_id)))
            if err:
                os._exit(1)
            else:
                return False

    def expand_disk_2_storage_pool_by_uuid(self, s_ip=None, node_id=None, uuid=None, storage_pool_id=None):
        '''
        :Usage : add disk to storage pool by its uuid
        :param s_ip:
        :param node_id:
        :param uuid:
        :return:
        '''
        disk_id = self.get_disk_id_by_uuid(s_ip=s_ip, node_id=node_id, disk_uuid=uuid, err=False)
        self.expand_disk_2_storage_pool(s_ip=s_ip, stor_id=storage_pool_id, disk_id=disk_id, err=False)
        print "Node %s add disk %s to storatepool %s success." % (str(node_id), str(disk_id), str(storage_pool_id))

    def get_lun_size(self, c_ip=None, lun=None, unit="$6"):
        '''
        :Usage : get lun's size
        :param c_ip:
        :param lun:
        :return: int,unit: $6  Byte  $3  GB
        '''
        if unit == "$6":
            cmd = ("ssh %s \"fdisk -l %s 2> /dev/null | grep '%s' | awk -F ',| ' '{print \$6}'\"" % (c_ip, lun, lun))
        elif unit == "$3":
            cmd = ("ssh %s \"fdisk -l %s 2> /dev/null | grep '%s' | awk -F ',| ' '{print \$3}'\"" % (c_ip, lun, lun))
        log.info(cmd)
        (res, output) = commands.getstatusoutput(cmd)
        log.info(output)
        if res != 0:
            log.error("Get %s size failed." % (lun))
            os._exit(1)
        else:
            return int(output)

    def parted_lun(self, c_ip=None, lun=None, min_size=None, max_size=None):
        '''
        :Usage : make a part for the disk by parted tool
        :param c_ip: host ip
        :param lun: lun to make part
        :param min_size: range
        :param max_size: range
        :return: part name
        '''
        # range_1 : min:0G,max:4G
        # range_2 : min:4G,max:16384G(16T)
        # range_3 : min:16384G,max:65536G(64T)
        # range_4 : min:65536G,max:262144G(256T)

        # Judge if the lun is exist
        cmd = ("ssh %s 'ls %s1'" % (c_ip, lun))
        log.info(cmd)

        (res, output) = commands.getstatusoutput(cmd)
        log.info(output)
        if res != 0:
            lun_size = self.get_lun_size(c_ip=c_ip, lun=lun, unit="$3")
            lun_size = int(lun_size.split('.')[0])
            if min_size == None or max_size == None:
                if lun_size <= 4:
                    return lun
                elif lun_size <= 16384 and lun_size > 4:
                    range_num = random.randint(0, 1)
                    if range_num == 0:
                        min_size = random.randint(0, 4)
                        max_size = min_size + 2
                    else:
                        min_size = random.randint(0, lun_size - 2)
                        max_size = min_size + 2
                elif lun_size > 16384 and lun_size <= 65536:
                    range_num = random.randint(0, 2)
                    if range_num == 0:
                        min_size = random.randint(0, 4)
                        max_size = min_size + 2
                    elif range_num == 1:
                        min_size = random.randint(4, 16384)
                        max_size = min_size + 2
                    else:
                        min_size = random.randint(16384, lun_size - 2)
                        max_size = min_size + 2
                else:
                    range_num = random.randint(0, 3)
                    if range_num == 0:
                        min_size = random.randint(0, 4)
                        max_size = min_size + 2
                    elif range_num == 1:
                        min_size = random.randint(4, 16384)
                        max_size = min_size + 2
                    elif range_num == 2:
                        min_size = random.randint(16384, 65536)
                        max_size = min_size + 2
                    else:
                        min_size = random.randint(65536, lun_size - 2)
                        max_size = min_size + 2

            cmd = (
                    "ssh %s 'parted -s %s mklabel gpt mkpart primary %sG %sG'" % (
            c_ip, lun, str(min_size), str(max_size)))
            log.info(cmd)
            (res, output) = commands.getstatusoutput(cmd)
            log.info(output)
            if res != 0:
                log.error("Parted %s and mkpart %s to %s on %s failed." % (lun, str(min_size), str(max_size), c_ip))
                os._exit(1)
            else:
                return lun + '1'
        else:
            return lun + '1'

    def del_lun_part(self, c_ip=None, lun=None):
        '''
        :Usage : delete the lun partion
        :param c_ip: host ip
        :param lun: lun name
        :return: None
        '''
        cmd = ("ssh %s 'parted -s %s rm 1'" % (c_ip, lun))
        log.info(cmd)
        (res, output) = commands.getstatusoutput(cmd)
        log.info(output)
        if res != 0:
            log.error("Rm partion %s on %s failed." % (lun, c_ip))
            log.error(output)
        else:
            return

    def get_jnl_replica(self, s_ip=None):
        '''
        :Usage :获取共享盘副本数
        :param s_ip: 集群节点IP
        :return: int，副本数
        '''
        cmd = ("ssh %s 'pscli --command=get_jnl_replica'" % (s_ip))
        log.info(cmd)
        (res, output) = commands.getstatusoutput(cmd)
        log.info(output)
        if res != 0:
            log.error("Get shared disk replica info failed.")
            os._exit(1)
        else:
            result = json.loads(output)
            return result['result']['jnl_replica']
        return None

    def get_disk_state(self, s_ip=None, disk_id=None):
        '''
        :Usge:通过磁盘ID获取磁盘状态
        :param s_ip: 集群节点IP
        :param disk_id: 磁盘ID
        :return: str，磁盘状态
        :磁盘状态:DISK_STATE_ISOLATE  DISK_STATE_HEALTHY  DISK_STATE_REBUILDING_PASSIVE  DISK_STATE_ZOMBIE
        '''
        ips, node_id, d_name = self.get_nodeinfo_by_diskid(s_ip=s_ip, disk_id=disk_id)
        cmd = ("ssh %s 'pscli --command=get_disks --node_ids=%d'" % (s_ip, node_id))
        log.info(cmd)
        (res, output) = commands.getstatusoutput(cmd)
        log.info(output)
        if res != 0:
            log.error("Get shared disk replica info failed.")
            os._exit(1)
        else:
            result = json.loads(output)
            disk_list = result['result']['disks']
            for disk in disk_list:
                if disk['id'] == disk_id:
                    return disk['state']
        return None

    def check_disk_state(self, node_ip=None, disk_uuid=None, err=True):
        '''
        :Usge:通过磁盘UUID检查节点磁盘状态
        :Arthur:wuyuqiao
        :param node_ip: 节点IP
        :param disk_uuid: 磁盘uuid
        :return: 磁盘状态：DISK_STATE_ISOLATE  DISK_STATE_HEALTHY  DISK_STATE_REBUILDING_PASSIVE  DISK_STATE_ZOMBIE
        '''
        node_id = node.get_node_id_by_ip(node_ip)

        cmd = ("ssh %s 'pscli --command=get_disks --node_ids=%d'" % (node_ip, node_id))
        log.info(cmd)
        (res, output) = commands.getstatusoutput(cmd)
        log.info(output)
        if res != 0:
            log.error("Get disks info replica failed!!!")
            if err:
                os._exit(1)
            else:
                return False
        else:
            result = json.loads(output)
            disk_list = result['result']['disks']
            for disk in disk_list:
                if disk['uuid'] == disk_uuid:
                    log.info("The %s disk status is %s" % (disk['devname'], disk['state']))
                    return disk['state']

            log.error("Can't find the disk or the disk_uuid has been changed!")
            log.error("The disk's uuid is %s" % (disk_uuid))
            return None

    def get_interface_node(self, vips=None):
        '''
        :Usage:获取业务接入点的节点ID
        :return: list，接入点节点ID
        '''
        node_ids = []
        for sip in deploy_ips:
            for vip in vips:
                cmd = ("ssh %s 'ip a |grep %s'" % (sip, vip))
                (res, output) = commands.getstatusoutput(cmd)
                if res == 0:
                    node_id = node.get_node_id_by_ip(sip)
                    node_ids.append(node_id)
                    break
        return node_ids

    def get_jnl_node_id(self):
        """
        :Usage:获取日志节点列表
        :return:list,日志节点列表
        """
        jnl_node_ids = []
        node_ids = osan.get_nodes(s_ip=deploy_ips[1])
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

    def get_min_lun_replica(self, s_ip=None):
        """
        :Author:diws
        :Date:2018-08-10
        :Usage:获取lun最小副本数
        :param s_ip: 集群节点IP
        :return: int，最小副本数
        :Chagelog:
        """
        lun_ids = osan.get_lun(s_ip=s_ip)
        if lun_ids:
            lun_rep_nums = []
            cmd = ("ssh %s ' pscli --command=get_luns'" % (s_ip))
            log.info(cmd)
            res, output = commands.getstatusoutput(cmd)
            log.info(output)
            if res != 0:
                log.error("Get luns error.")
                os._exit(1)
            else:
                result = json.loads(output)
                lun_list = result['result']['luns']
                for lun in lun_list:
                    lun_rep_nums.append(lun["layout"]["replica_num"])
                return (int(min(lun_rep_nums)))
            return
        else:
            log.info("the storage system have not lun")

    def check_bad_obj(self):
        """
        :Author:diws
        :Date:2018-08-10
        :Usage:检查集群内是否有坏对象
        :return:
        """
        # 此处加延时，时为了等坏对象统计上来。防止出现坏对象没上报就去检查的情况。
        time.sleep(180)
        com_os = Os_Reliable()
        for d_ip in deploy_ips:
            if False is ReliableTest.check_ping(d_ip):
                continue
            else:
                san_status = com_os.get_san_state(d_ip)
                if san_status:
                    if all(san_status) is True:
                        log.info("check san status is active")
                        break
                    elif True in san_status:
                        log.info("have a part of node list san status is active:%s" % (san_status))
                        break
                    else:
                        log.info("check san status is inactive, check_bad_obj will pass")
                        return
                else:
                    log.info("check xstor have not access, check_bad_obj will pass")
                    return
        for c_ip in client_ips:
            cmd = ("ssh %s 'ps aux |grep -v grep | grep vdb'" % (c_ip,))
            res, output = commands.getstatusoutput(cmd)
            while res == 0:
                res, output = commands.getstatusoutput(cmd)
                log.info("check node %s vdb process exists" % (c_ip))
                time.sleep(20)
        for ip in deploy_ips:
            if False == ReliableTest.check_ping(ip):
                continue
            else:
                cmd = ('ssh root@%s "ps -C oSan"' % (ip,))
                res, output = commands.getstatusoutput(cmd)
                if res != 0:
                    continue
                n_id = node.get_node_id_by_ip(ip)
                cmd = ("ssh %s '/home/parastor/tools/nWatch -t oSan -i %s -c oSan#badobjnr'" % (ip, str(n_id)))
                log.info(cmd)
                res, output = commands.getstatusoutput(cmd)
                if (res == 0 and 'support' in output) or (res != 0):
                    time.sleep(10)
                    for i in range(5):
                        res, output = commands.getstatusoutput(cmd)
                        if res == 0 and 'support' not in output:
                            break
                        time.sleep(20)
                        if i == 4:
                            log.error("Check bad obj failed after %s times.\noutput Info:%s" % (i, output))
                            exit(1)
                # badobjnr = output.split(":")[-1].strip()
                log.info(output)
                badobjnr = output.split('\n')[0].split(":")[-1].strip()
                log.info("Check badobj number is %s." % (str(badobjnr)))
                while str(badobjnr) != '0':
                    badobjnr_init = badobjnr
                    # time.sleep(300)   #等待5分钟改为每分钟检查一次
                    for n in range(6):
                        time.sleep(60)
                        res, output = commands.getstatusoutput(cmd)
                        if (res == 0 and 'support' in output) or (res != 0):
                            time.sleep(10)
                            for i in range(5):
                                res, output = commands.getstatusoutput(cmd)
                                if res == 0 and 'support' not in output:
                                    break
                                time.sleep(20)
                                if i == 4:
                                    log.error("Check bad obj failed after 5 times.")
                                    exit(1)
                                    # badobjnr = output.split(":")[-1].strip()
                        log.info(output)
                        badobjnr = output.split('\n')[0].split(":")[-1].strip()
                        if int(badobjnr) == 0:
                            break
                        elif n == 5:
                            if int(badobjnr_init) == int(badobjnr):
                                log.info(
                                    "On node %s oSan#badobjnr is %s after 5 minitues." % (str(n_id), str(badobjnr)))
                                log.error(
                                    "Found bad obj didn't repair in five minitues, so I cored automaticlly on each node.")
                                time.sleep(300)
                                for core_ip in deploy_ips:
                                    cmd = ("ssh %s 'killall -11 oSan'" % (core_ip,))
                                    commands.getstatusoutput(cmd)
                                cmd = 'pscli --command=get_nodes'
                                res, output = osan.run_pscli_cmd(pscli_cmd=cmd)
                                log.error(output)
                                os._exit(110)
                                # elif int(badobjnr_init) / (int(badobjnr_init) - int(badobjnr)) > 6:
                                #     log.error("Repair time is expand 30 minitues.")
                                #     os._exit(110)

    def check_lnode_state(self):
        """
        :Arthor:wuyuqiao
        :Usage:检查集群的逻辑节点状态是否正常
        """
        com_os = Os_Reliable()
        san_status = com_os.get_san_state(deploy_ips[0])
        if san_status:
            if all(san_status) is True:
                log.info("check san status is active")
            else:
                log.info("check san status is inactive, check_lnode_state will pass")
                return
        else:
            log.info("check xstor have not access, check_lnode_state will pass")
            return
        log.info("******************** check lnode state ********************")
        nodes = osan.get_nodes(s_ip=deploy_ips)
        for node_id in nodes:
            current_node_ip = node.get_node_ip_by_id(str(node_id))
            cmd = ('ssh root@%s "ps -C oSan"' % (current_node_ip,))
            res, output = commands.getstatusoutput(cmd)
            if res != 0:
                continue
            cmd = ('ssh %s "/home/parastor/tools/nWatch -t oSan -i %s -c oSan#jnlins_dump"' % (
                current_node_ip, node_id))
            log.info(cmd)
            res, output = commands.getstatusoutput(cmd)
            log.info(output)
            if res != 0:
                log.error("Check lnode state failed!!!info:%s" % output)
                os._exit(1)
            else:
                cmd = (
                        'ssh %s "/home/parastor/tools/nWatch -t oSan -i %s -c oSan#jnlins_dump" | grep lnodeid' % (
                    current_node_ip, node_id))
                log.info(cmd)
                output = commands.getoutput(cmd)
                log.info(output)
                if output == '':
                    log.info("Warning:The node %s has not any lnode!" % current_node_ip)
                else:
                    lnode_stor = []
                    for count in range(4):
                        error_state = 0
                        lnode_error_list = ''
                        res, output = commands.getstatusoutput(cmd)
                        if res != 0:
                            log.error("Check lnode state failed!!!info:%s" % output)
                            os._exit(1)
                        else:
                            lnode_list = output.split('\n')
                            for lnode in lnode_list:
                                lnode_state_ls = lnode.split(':')
                                lnode_state_tmp = lnode_state_ls[2]
                                lnode_state = lnode_state_tmp[0]
                                if lnode_state != '6':
                                    lnode_error_list = lnode_error_list + lnode + '\n'
                                    error_state += 1
                            if 0 == error_state:
                                log.info("node %s all lnode state is OK!" % current_node_ip)
                                break
                            else:
                                log.info("The node %s has lnode in ERROR state!info:\n%s" % (
                                    current_node_ip, lnode_error_list))
                                lnode_stor.append(lnode_error_list)
                                if 0 != count and lnode_error_list == lnode_stor[count - 1]:
                                    log.error(
                                        "The node %s lnode state is not changed after 3 minutes.Maybe stuck!" % current_node_ip)
                                    os._exit(1)
                                else:
                                    log.info("The node %s lnode state is ERROR...waiting 3 minutes" % current_node_ip)
                        time.sleep(180)

    def restart_otrc(self, ip):
        '''
        :Autor:Diws
        :Date:20180906
        :param ip:集群节点IP
        :return:None
        '''
        print "None"
        # cmd = ("ssh %s ' /home/parastor/tools/otrc -i'" % (ip,))
        # res, output = commands.getstatusoutput(cmd)
        # if res != 0:
        #     # enable_otrc = ("ssh %s '/home/parastor/tools/otraced -d'" % (ip,))
        #     enable_otrc = ("ssh %s 'echo hello'" % (ip,))
        #     res, output = commands.getstatusoutput(enable_otrc)
        #     if res != 0:
        #         log.info(output)
        #         return None
        #     enable_log = (
        #         "ssh %s '/home/parastor/tools/otrc -o /home/parastor/log/otrace/otrace.data -s 4096 -S \"IOPREP|DJNL|DPC|LMPC|LIOC\"'" % (
        #             ip,))
        #     res, output = commands.getstatusoutput(enable_log)
        #     if res != 0:
        #         log.info(output)
        #         return None
        #     otrc_on = ("ssh %s '/home/parastor/tools/otrc -z on'" % (ip,))
        #     res, output = commands.getstatusoutput(otrc_on)
        #     if res != 0:
        #         log.info(output)
        #         return None

    def get_all_shared_disk_id(self):
        '''
        :By:Diws
        :Date:20181009
        :return:list,所有共享盘ID
        '''
        disk_ids = []
        nodes = osan.get_nodes(s_ip=deploy_ips)
        for n_id in nodes:
            cmd = ("ssh root@%s ' pscli --command=get_disks --node_ids=%s'" % (deploy_ips[0], str(n_id)))
            log.info(cmd)
            res, output = commands.getstatusoutput(cmd)
            # log.info(output)
            if res != 0:
                log.info("Get disks failed.")
                exit(1)
            else:
                output = json.loads(output)
                output = output['result']
                for i in range(len(output['disks'])):
                    if output['disks'][i]['usage'] == 'SHARED':
                        disk_ids.append(output['disks'][i]['id'])
        disk_ids = list(set(disk_ids))
        if 0 in disk_ids:
            disk_ids.remove(0)
        return disk_ids

    def get_all_data_disk_id(self):
        '''
        :By:Diws
        :Date:20181009
        :return:list,所有共享盘ID
        '''
        disk_ids = []
        nodes = osan.get_nodes(s_ip=deploy_ips)
        for n_id in nodes:
            cmd = ("ssh root@%s ' pscli --command=get_disks --node_ids=%s'" % (deploy_ips[0], str(n_id)))
            log.info(cmd)
            res, output = commands.getstatusoutput(cmd)
            log.info(output)
            if res != 0:
                log.info("Get disks failed.")
                exit(1)
            else:
                output = json.loads(output)
                output = output['result']
                for i in range(len(output['disks'])):
                    if output['disks'][i]['usage'] == 'DATA':
                        disk_ids.append(output['disks'][i]['id'])
        disk_ids = list(set(disk_ids))
        if 0 in disk_ids:
            disk_ids.remove(0)
        return disk_ids

    def get_assign_data_disk_id(self, s_ip, node_id):
        """
        获取指定节点的物理盘
        :Author:wangxiang
        :Date:2018-10-16
        :type node_id: int
        :type s_ip: str
        :param s_ip :
        :param node_id :
        :return:
        """
        disk_ids = []
        if all([s_ip, node_id]):
            cmd = ("ssh root@%s ' pscli --command=get_disks --node_ids=%s'" % (s_ip, str(node_id)))
            log.info(cmd)
            res, output = commands.getstatusoutput(cmd)
            # log.info(output)
            if res != 0:
                log.info("Get disks failed.")
                exit(1)
            else:
                output = json.loads(output)
                output = output['result']
                for i in range(len(output['disks'])):
                    if output['disks'][i]['usage'] == 'DATA':
                        disk_ids.append(output['disks'][i]['id'])
        else:
            log.error("get  error arg!")
            exit(1)
        disk_ids = list(set(disk_ids))
        if 0 in disk_ids:
            disk_ids.remove(0)
        return disk_ids

    def get_lun_los_pair(self):
        """
        :author:diws
        :Date:20181010
        :Description:获取lun id和los id对应值
        :return: dict,losid:lunid
        """
        lun_los_pair = {}
        for ip in deploy_ips:
            if False is ReliableTest.check_ping(ip):
                continue
            cmd = ("ssh root@%s ' pscli --command=get_luns'" % (ip,))
            log.info(cmd)
            res, output = commands.getstatusoutput(cmd)
            log.info(output)
            if res != 0:
                continue
            else:
                output = json.loads(output)
                output = output['result']['luns']
                for i in range(len(output)):
                    lun_los_pair[output[i]['lunMaps'][0]['lun_id']] = output[i]['lunMaps'][0]['target_id']
                break
        return lun_los_pair

    def get_jnl_state(self, removed_ip=None):
        """
        :Author: Diws
        :Description:获取所有los节点日志状态
        :return: dict,{losid:[nodeid, los_state]},los state:0|1|2|3|4|5|6,6为正常服务，1-5为日志接管中间阶段，
                0为初始化，其他值：不处理
        """
        losids = disk().get_lun_los_pair().values()
        jnl_state = {}
        losids = list(set(losids))
        if removed_ip in deploy_ips:
            deploy_ips.remove(removed_ip)
        for ip in deploy_ips:
            if False is ReliableTest.check_ping(ip):
                continue
            else:
                cmd = ('ssh root@%s "ps -C oSan"' % (ip,))
                res, output = commands.getstatusoutput(cmd)
                if res != 0:
                    continue
                n_id = node.get_node_id_by_ip(ip)
                cmd = ("ssh root@%s '/home/parastor/tools/nWatch -t oSan -i %d -c oSan#jnlins_dump'"% (ip, n_id))
                stdout = commands.getoutput(cmd)
                lnode_info = stdout.split('\n')
                for losid in losids:
                    lnodeid = ('lnodeid:%d' % losid)
                    for lnode in lnode_info:
                        if lnodeid in lnode:
                            status = lnode.split('|')[0][-1]
                            jnl_state[losid] = [n_id, status]
        return jnl_state

    def get_node_ip_by_id(self, removed_ip=None, n_id=None):
        """
        :Author:Diws
        :param removed_ip: 不处理的节点IP
        :return:str,节点IP
        """
        if None != removed_ip:
            if type(removed_ip) == str:
                removed_ip = removed_ip.split()
            for rm_ip in removed_ip:
                if rm_ip in deploy_ips:
                    deploy_ips.remove(rm_ip)
        err_flag = 1
        for d_ip in deploy_ips:
            if False is ReliableTest.check_ping(d_ip):
                continue
            cmd = ("ssh root@%s 'pscli --command=get_nodes --ids=%s'" % (d_ip, str(n_id)))
            for i in range(3):
                res, output = commands.getstatusoutput(cmd)
                log.info(cmd)
                if res != 0:
                    err_flag = 1
                    time.sleep(10)
                else:
                    err_flag = 0
                    break
            if err_flag == 0:
                break
        if err_flag == 1:
            log.error(output)
            log.error("Get nodes failed.")
            exit(1)
        msg = json.loads(output)
        node_ip = msg['result']['nodes'][0]['ctl_ips'][0]['ip_address']
        return node_ip

    def get_node_id_by_ip(self, removed_ip=None, n_ip=None):
        """
        :Author:Diws
        :param removed_ip: 不处理的节点IP
        :n_ip:管理节点IP
        :return:int,节点ID
        """
        if None != removed_ip:
            if type(removed_ip) == str:
                removed_ip = removed_ip.split()
            for rm_ip in removed_ip:
                if rm_ip in deploy_ips:
                    deploy_ips.remove(rm_ip)
        err_flag = 1
        for d_ip in deploy_ips:
            if False is ReliableTest.check_ping(d_ip):
                continue
            cmd = ("ssh root@%s 'pscli --command=get_nodes'" % (d_ip,))
            for i in range(3):
                log.info(cmd)
                res, output = commands.getstatusoutput(cmd)
                # log.info(output)
                if res != 0:
                    err_flag = 1
                    time.sleep(10)
                else:
                    err_flag = 0
                    break
            if err_flag == 0:
                break
        if err_flag == 1:
            log.error("Get nodes failed.")
            exit(1)
        output = json.loads(output)
        nodes_info = output["result"]["nodes"]
        for node in nodes_info:
            ctl_ip = node["ctl_ips"][0]["ip_address"]
            if n_ip == ctl_ip:
                return node["node_id"]
        log.warn("there is not a node's ip is %s!!!" % n_ip)
        return None

    def get_nodeip_by_losid(self, losid=None):
        """
        :Author:Diws
        :Date:20181105
        :Description:根据losid获取los所在节点IP
        :param losid: los ID
        :return: 节点IP
        """
        nodes = osan.get_nodes()
        for nid in nodes:
            cmd = ("/home/parastor/tools/nWatch -t oSan -i %s -c oSan#jnlins_dump" % (str(nid)))
            res, output = osan.run_pscli_cmd(pscli_cmd=cmd)
            check_str = ('lnodeid:%s' % (str(losid)))
            if check_str in output:
                sip = disk().get_node_ip_by_id(n_id=nid)
                return sip
        return None

    def check_part_lun_data_uniform_by_ip(self, s_ip=None):
        """
        :Author: Diws
        :Date: 20181105
        :Description: 比较报单对象副本一致性
        :param s_ip: 集群节点IP
        :return:
        """
        button = xml.dom.minidom.parse(conf_file)
        button = button.getElementsByTagName('uniform')[0].firstChild.nodeValue
        if button == "off":
            return
        disk().check_bad_obj()
        bad_obj_info = {}
        losids = []
        losid_ip = {}
        """检查入参"""
        if False is ReliableTest.check_ping(s_ip):
            log.error("Can not attatch the ip %s you want to check." % (s_ip))
            return
        elif s_ip == None:
            log.error("You must input a ip to check.")
            return
        """生成的临时配置文件，位置为脚本执行节点/tmp目录下"""
        tmp_log_file = ("/tmp/tmp_log_file_%s" % (s_ip))
        cmd = ("ssh root@%s 'grep srrf_obj_end /home/parastor/log/imp_oSan.log*' | cat - > %s" % (s_ip, tmp_log_file))
        res, output = commands.getstatusoutput(cmd)
        if res == 0:
            with open(tmp_log_file, 'r') as log_file:
                for line in log_file:
                    if 'lunid' in line and 'losid' in line and 'segidx' in line:
                        line = re.sub('\[|\]', ' ', line)
                        line = line.split(' ')
                        for seg in line:
                            if 'lunid' in seg:
                                lunid = re.sub('\(|\)', ' ', seg).split()[-1]
                            elif 'losid' in seg:
                                lid = re.sub('\(|\)', ' ', seg).split()[-1]
                            elif 'segidx' in seg:
                                segidx = re.sub('\(|\)', ' ', seg).split()[-1]
                        bad_obj_info[lunid, segidx] = lid
            log.info("######## bad obj on %s are: ########\n" % (s_ip,))
            # print bad_obj_info
            # log.info(bad_obj_info)
            if len(bad_obj_info) == 0:
                return
            for losid in bad_obj_info.values():
                losids.append(losid)
            losids = list(set(losids))
            for losid in losids:
                nip = disk().get_nodeip_by_losid(losid=losid)
                losid_ip[losid] = nip
            for losinfo in bad_obj_info.keys():
                bad_obj_info[losinfo] = losid_ip[bad_obj_info[losinfo]]
            log.info(bad_obj_info)
            seg_num = 0
            for segidx in bad_obj_info.keys():
                if bad_obj_info[segidx] != None:
                    cmd = ("ssh root@%s '/home/parastor/tools/ecodecheck/san-repchk.sh %s %s %s'" % (
                        bad_obj_info[segidx], str(segidx[1]), str(segidx[0]), bad_obj_info[segidx]))
                    res, output = commands.getstatusoutput(cmd)
                    log.info(cmd)
                    if 'diff' in output:
                        log.error(output)
                        log.error("Check part lun data uniform failed.")
                        os._exit(1)
                seg_num += 1
                if seg_num == 11:
                    break
            log.info("Check part lun data uniform success.")

    def multi_check_part_lun_uniform_by_ip(self):
        button = xml.dom.minidom.parse(conf_file)
        button = button.getElementsByTagName('uniform')[0].firstChild.nodeValue
        if button == "on":
            check_threads = []
            for sip in deploy_ips:
                check_threads.append(threading.Thread(target=disk().check_part_lun_data_uniform_by_ip, args=(sip,)))
            for check_thread in check_threads:
                check_thread.setDaemon(True)
                check_thread.start()
            for check_thread in check_threads:
                check_thread.join()
        else:
            pass

    def check_part_lun_data_uniform_by_id(self, l_id=None):
        """
        :Author: Diws
        :Date: 20181106
        :Description: 比较报单对象副本一致性
        :param s_ip: 集群节点IP
        :return:
        """
        disk().check_bad_obj()
        bad_obj_info = {}
        losids = []
        losid_ip = {}
        check_str = 'lunid(%s)' % (str(l_id))
        """检查入参"""
        if l_id == None:
            log.error("You must input a ip to check.")
        # tmp_log_file = ("/log_tmp")
        for s_ip in deploy_ips:
            if False is ReliableTest.check_ping(d_ip):
                continue
            else:
                """生成的临时配置文件，位置为脚本执行节点/tmp目录下"""
                tmp_log_file = ("/tmp/tmp_log_file_%s" % (s_ip))
                cmd = ("ssh root@%s 'grep srrf_obj_end /home/parastor/log/imp_oSan.log*' | cat - > %s" % (
                    s_ip, tmp_log_file))
                res, output = commands.getstatusoutput(cmd)
                if res == 0:
                    with open(tmp_log_file, 'r') as log_file:
                        for line in log_file:
                            if check_str in line and 'losid' in line and 'segidx' in line:
                                line = re.sub('\[|\]', ' ', line)
                                line = line.split(' ')
                                for seg in line:
                                    if 'lunid' in seg:
                                        lunid = re.sub('\(|\)', ' ', seg).split()[-1]
                                    elif 'losid' in seg:
                                        lid = re.sub('\(|\)', ' ', seg).split()[-1]
                                    elif 'segidx' in seg:
                                        segidx = re.sub('\(|\)', ' ', seg).split()[-1]
                                bad_obj_info[lunid, segidx] = lid
                    log.info("######## bad obj on %s are: ########\n" % (s_ip,))
                    log.info(bad_obj_info)
                    for losid in bad_obj_info.values():
                        losids.append(losid)
                    losids = list(set(losids))
                    for losid in losids:
                        nip = disk().get_nodeip_by_losid(losid=losid)
                        losid_ip[losid] = nip
                    for losinfo in bad_obj_info.keys():
                        bad_obj_info[losinfo] = losid_ip[bad_obj_info[losinfo]]
                    log.info(bad_obj_info)
                    for segidx in bad_obj_info.keys():
                        if bad_obj_info[segidx] != None:
                            cmd = ("ssh root@%s '/home/parastor/tools/ecodecheck/san-repchk.sh %s %s %s'" % (
                                bad_obj_info[segidx], str(segidx[1]), str(segidx[0]), bad_obj_info[segidx]))
                            res, output = commands.getstatusoutput(cmd)
                            if 'diff' in output:
                                log.error(output)
                                log.error("Check part lun data uniform failed.")
                                exit(1)
                    log.info("Check part lun data uniform success.")

    def get_sysid(self):
        """
        :Author : Diws
        :Date: 20181114
        :param ip:
        :return:
        """
        for ip in deploy_ips:
            if False is ReliableTest.check_ping(ip):
                continue
            else:
                cmd = ("ssh %s 'grep sysid /home/parastor/conf/node.xml'" % (ip,))
                res, output = commands.getstatusoutput(cmd)
                if res == 0:
                    sysid = re.sub('<|>', ',', output)
                    return sysid.split(',')[2]

    def get_sysid_uuid(self):
        """
        :Author:Diws
        :Date:20181206
        :return: the id and uuid of the testing cluster
        """
        cmd = "pscli --command=get_cluster_overview"
        res, output = com2.run_pscli_cmd(pscli_cmd=cmd)
        output = json.loads(output)
        output = output['result']
        return output['sysid'], output['uuid'], output['name']

    def check_baljob(self, check_state='yes'):
        """
        :Author:Diws
        :Date:20181207
        :Description:检查均衡是否完成
        :return:
        """
        nodes = osan.get_nodes()
        for node in nodes:
            cmd = ("/home/parastor/tools/nWatch -i %s -t oPara -c oPara#vmgr_balrecord_dump" % (str(node),))
            log.info(cmd)
            res, output = osan.run_pscli_cmd(pscli_cmd=cmd)
            log.info(output)
            if '-110' in output:
                break
            else:
                if check_state == 'yes':
                    while ' 0 baljob' not in output:
                        time.sleep(10)
                        log.info("Waiting for balance.......")
                        log.info(output)
                else:
                    if ' 0 baljob' not in output:
                        log.info('Begin balance job.')
                        return True

    def get_disk_cap(self):
        """
        :Author:Diws
        :Date:20181207
        :Description:获取每个磁盘池中，每个磁盘的容量
        :return: dict
        """
        total_info = {}
        cmd = "pscli --command=get_nodes"
        res, output = osan.run_pscli_cmd(pscli_cmd=cmd)
        output = json.loads(output)['result']['nodes']
        for s_ip in deploy_ips:
            if ReliableTest.check_ping(s_ip):
                # 获取存储池id
                storage_pool_ids = osan.get_storage_id(s_ip=s_ip)
                # 遍历每个存储池
                for s_p_id in storage_pool_ids:
                    disk_pool_info = {}
                    # 获取每个存储池中，每个磁盘池中的磁盘id,disk_infos: dict, key:value--disk_pool_id:[diskid1,diskid2]
                    disk_infos = self.get_diskid_in_disk_pool(s_ip=s_ip, s_id=s_p_id)
                    # 遍历每个磁盘池
                    for d_p_id in disk_infos.keys():
                        disk_cap_info = {}
                        # 遍历每个磁盘
                        for d_id in disk_infos[d_p_id]:
                            gotcha = 0
                            # 查找每个节点
                            for n_id in output:
                                # 获取该节点所有磁盘id
                                for d_disk in n_id['data_disks']:
                                    if str(d_id) == str(d_disk['id']):
                                        disk_cap_info[d_id] = round(
                                            float(d_disk['used_bytes']) / float(d_disk['total_bytes']), 2)
                                        gotcha = 1
                                        break
                                if gotcha == 1:
                                    break
                                for d_disk in n_id['shared_disks']:
                                    if str(d_id) == str(d_disk['id']):
                                        disk_cap_info[d_id] = round(
                                            float(d_disk['used_bytes']) / float(d_disk['total_bytes']), 2)
                                        gotcha = 1
                                        break
                                if gotcha == 1:
                                    break
                        disk_pool_info[d_p_id] = disk_cap_info
                    total_info[s_p_id] = disk_pool_info
                return total_info

    def comp_disk_cap(self, disk_cap_info):
        """
        :Author:Diws
        :Date:20181210
        :Description:根据传入的磁盘信息，比较每个存储池内，每个磁盘池中每个盘的容量
        :param disk_cap_info:
        :return:
        """
        for sid in disk_cap_info.keys():
            for did in disk_cap_info[sid].keys():
                b_cap = max(disk_cap_info[sid][did], key=disk_cap_info[sid][did].get)
                s_cap = min(disk_cap_info[sid][did], key=disk_cap_info[sid][did].get)
                if (float(disk_cap_info[sid][did][b_cap]) - float(disk_cap_info[sid][did][s_cap])) > 0.1:
                    log.error("There is some disk is not balance, and they are:%d %d." % (int(b_cap), int(s_cap)))
                    # os._exit(1)

    def set_disk_uuid(self, s_ip=None, disk_name=None):
        """
        :Author:Diws
        :Data:20181210
        :param s_ip: 目标节点IP
        :param disk_name: 磁盘名
        :return:uuid
        """
        pass
        cmd = 'uuidgen -r'
        res, generate_uuid = commands.getstatusoutput(cmd)
        cmd = ("ssh root@%s 'parted -s %s p'" % (s_ip, disk_name))
        log.info(cmd)
        res, output = commands.getstatusoutput(cmd)
        log.info(output)
        if 'primary' in output or 'ext' in output:
            log.error("You are going to format your system disk.")
            os._exit(1)
        for ip in deploy_ips:
            if ReliableTest.check_ping(ip):
                cmd = ("ssh root@%s 'scp /home/parastor/tools/hardware/disk/disk_set_uuid %s/tmp'" % (ip, s_ip))
                commands.getstatusoutput(cmd)
            break
        cmd = ("ssh root@%s 'parted -s %s mklabel gpt;/tmp/disk_set_uuid %s %s'" % (
            s_ip, disk_name, disk_name, generate_uuid))
        log.info(cmd)
        res, output = commands.getstatusoutput(cmd)
        log.info(output)
        if res != 0:
            log.error("Format disk error.")
            os._exit(1)
        else:
            return generate_uuid

    def get_free_disk_uuid_by_node_id(self, node_id=None, disk_type='data'):
        """
        :Author:Diws
        :Date:20181210
        :param node_id:节点ID
        :return: uuid list
        """
        disks = []
        cmd = ("pscli --command=get_disks --node_ids=%s" % (str(node_id),))
        log.info(cmd)
        res, output = osan.run_pscli_cmd(pscli_cmd=cmd)
        if res != 0:
            log.error("Get disk name failed.")
            os._exit(1)
        else:
            result = json.loads(output)
            disk_list = result['result']['disks']
            if disk_type == 'data' or disk_type == 'DATA':
                for disk in disk_list:
                    if disk["usedState"] == "UNUSED" and (disk["speed_level"] == "MID" or disk["speed_level"] == "LOW"):
                        disks.append(disk["uuid"])
            else:
                for disk in disk_list:
                    if disk["usedState"] == "UNUSED" and disk["speed_level"] == "HIGH":
                        disks.append(disk["uuid"])
            return disks

    def get_free_disk_info_by_node_id(self, node_id=None, disk_type='data'):
        """
        :Author:Diws
        :Date:20181211
        :param node_id:节点ID
        :return: dict: {disk_name:[disk_uuid, disk_phy_id]}
        """
        disk_info = {}
        node_ip = self.get_node_ip_by_id(n_id=node_id)
        cmd = ("pscli --command=get_disks --node_ids=%s" % (str(node_id),))
        log.info(cmd)
        res, output = osan.run_pscli_cmd(pscli_cmd=cmd)
        if res != 0:
            log.error("Get disk name failed.")
            os._exit(1)
        else:
            result = json.loads(output)
            disk_list = result['result']['disks']
            if disk_type == 'data' or disk_type == 'DATA':
                for disk in disk_list:
                    if disk["usedState"] == "UNUSED" and (disk["speed_level"] == "MID" or disk["speed_level"] == "LOW"):
                        disks = []
                        disk_name = disk['devname']
                        disk_uuid = disk["uuid"]
                        disks.append(disk_name)
                        disk_phyid = self.get_disk_phyid_by_name(s_ip=node_ip, disk_name=disks)
                        disk_info[disk_name] = [disk_uuid, disk_phyid[0]]
            else:
                for disk in disk_list:
                    if disk["usedState"] == "UNUSED" and disk["speed_level"] == "HIGH":
                        disks = []
                        disk_name = disk['devname']
                        disk_uuid = disk["uuid"]
                        disks.append(disk_name)
                        disk_phyid = self.get_disk_phyid_by_name(s_ip=node_ip, disk_name=disks)
                        disk_info[disk_name] = [disk_uuid, disk_phyid[0]]
            return disk_info

    def seprate_ojmgs_orole(self):
        """
        :Author:Diws
        :Date:20181224
        :Description:将主oJmgs和主oRole分离
        :return:
        """
        master_ojmgs_id, master_ojmgs_ip = Os_Reliable().oJmgs_master_id()
        master_orole_ip = Os_Reliable().get_master_orole2(deploy_ips[0])
        master_orole_id = self.get_node_id_by_ip(n_ip=master_orole_ip)
        if int(master_ojmgs_id) == int(master_orole_id):
            Os_Reliable().change_process_state(node_ip=master_orole_ip, process_name='oRole', up_down='down')
            time.sleep(60)
            Os_Reliable().change_process_state(node_ip=master_orole_ip, process_name='oRole', up_down='up')

    def get_disk_ids_by_node_id(self, disk_type=None):
        """
        :Author:Diws
        :Date:20181227
        :Description:根据节点id返回该节点所有used状态的磁盘id
        :return:
        """
        disk_info = {}
        nodes = osan.get_nodes()
        for nid in nodes:
            disk_ids = []
            cmd = ('pscli --command=get_disks --node_ids=%s' % (str(nid),))
            res, output = osan.run_pscli_cmd(pscli_cmd=cmd)
            output = json.loads(output)
            disks = output['result']['disks']
            if disk_type is None:
                for disk in disks:
                    if disk['usage'] == 'DATA' and disk['usedState'] == 'FREE':
                        disk_ids.append(disk['id'])
            else:
                for disk in disks:
                    if disk['usage'] == 'DATA' and disk['usedState'] == 'FREE' and 'SAS' not in disk['speed_type']:
                        disk_ids.append(disk['id'])
            disk_info[nid] = disk_ids
        return disk_info

    def get_disk_uuid_by_diskid(self, disk_id=None):
        '''
        :Author:Diws
        :Date:20190109
        '''
        cmd = "pscli --command=get_nodes"
        res, output = osan.run_pscli_cmd(pscli_cmd=cmd)
        result = json.loads(output)
        node_lists = result['result']['nodes']
        for node in node_lists:
            data_disks = node['data_disks']
            for data_disk in data_disks:
                if data_disk['id'] == int(disk_id):
                    return data_disk['uuid']
            share_disks = node['shared_disks']
            for share_disk in share_disks:
                if share_disk['id'] == int(disk_id):
                    return share_disk['uuid']

    def get_storage_pool_id(self):
        """
        :Author:Diws
        :Date:20190109
        :return: list,存储池id
        """
        sp_list = []
        cmd = 'pscli --command=get_storage_pools'
        res, output = osan.run_pscli_cmd(pscli_cmd=cmd)
        output = json.loads(output)
        storage_pools = output['result']['storage_pools']
        for s_p in storage_pools:
            sp_list.append(s_p['id'])
        return sp_list

    def get_free_jnl_id(self):
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

    def get_jnl_grp_id(self):
        """
        :Date:2019-02-19
        :Author:Diws
        :Description:获取日志组
        :return: list, 日志组ID
        """
        cmd = ("/home/parastor/tools/nWatch -t oRole -i 1 -c oRole#rolemgr_view_dump  |grep 'grpid' | uniq | sed -s 's/-->//g' ")
        res, output = osan.run_pscli_cmd(pscli_cmd=cmd)
        output = output.split('\n')
        g_nr = []
        for info in output:
            g_nr.append(re.sub(', ','',info).split(' ')[-1])
        return g_nr

    def get_jnl_id_by_grp_id(self, grp_id=None):
        """
        :Date:2019-02-19
        :Author:Diws
        :Description:通过日志组id获取该组内所有日志节点ID
        :param grp_id: 日志组ID
        :return: list，节点ID
        """
        grp_id = int(grp_id)
        cmd = ("/home/parastor/tools/nWatch -t oRole -i 1 -c oRole#rolemgr_view_dump  |grep -E 'grpid|lnodenr'|  "
               "sed -s 's/-->//g' | grep -v 'version'")
        res, output = osan.run_pscli_cmd(pscli_cmd=cmd)
        output = output.split('\n')
        check_grp_id = 'grpid: %d' % (grp_id)
        index_nr_1 = 0
        index_nr_2= 0
        node_id = []
        for info in output:
            index_nr_1 += 1
            if check_grp_id in info:
                check_grp_info = output[index_nr_1:]
                break
        for info in check_grp_info:
            index_nr_2 += 1
            if 'grpid' in info:
                check_grp_info = check_grp_info[:index_nr_2]
                break
        for g_info in check_grp_info:
            tmp = g_info.split(',')
            for tmpinfo in tmp:
                if 'node_id' in tmpinfo:
                    node_id.append(tmpinfo.split()[-1])
        return node_id

    def get_node_ids_in_node_pool(self):
        """
        :Date:2019-02-19
        :Author:Diws
        :return: dict, 节点池id(int):节点ID(list)
        """
        node_pool_info = {}
        cmd = "pscli --command=get_node_pools"
        res, output = osan.run_pscli_cmd(cmd)
        output = json.loads(output)
        node_pools = output['result']['node_pools']
        for node_pool in node_pools:
            node_pool_id = node_pool['id']
            node_ids = node_pool['node_ids']
            node_pool_info[node_pool_id] = node_ids
        return node_pool_info

    def get_disk_symbol(self, node_ip=None):
        node_id = node.get_node_id_by_ip(node_ip)
        cmd = ("ssh %s 'pscli --command=get_disks --node_ids=%s'" % (node_ip, node_id))
        rc, stdout = commands.getstatusoutput(cmd)
        data_disks = []
        share_disks = []
        if rc == 0:
            log.info("get node %s disks successful." % node_ip)
            temp_final = json.loads(stdout)
            final = temp_final['result']['disks']
            for disk_info in final:
                if disk_info['storagePoolType'] == 'SHARED':
                    share_disks.append(disk_info['devname'])
                elif disk_info['storagePoolType'] == 'BLOCK':
                    data_disks.append(disk_info['devname'])
                else:
                    pass
            return share_disks, data_disks
        else:
            log.error("get disks symbol failed.Info:%s" % stdout)

    def get_disk_await(self, node_ip=None, disk_symbol=None):
        disk = disk_symbol.split('/')[2]
        cmd = ("ssh %s 'iostat -x 1 30 %s' | grep %s" % (node_ip, disk_symbol, disk))
        rc ,stdout = commands.getstatusoutput(cmd)
        await_list = []
        if rc == 0:
            final_info = stdout.split('\n')
            for final in final_info:
                await_info = final.split()
                result = await_info[9]
                await_list.append(float(result))
            avg_await = sum(await_list)/len(await_list)
            return avg_await
        else:
            log.error("get disk await failed.Info:%s" % stdout)





if __name__ == '__main__':
    pass
    # Os_Reliable().asyn_ntp()
    # disk_ids = disk().get_all_data_disk_id()
    # disk().modify_deploy_xml(dst_ip=deploy_ips[0])
    # print disk().get_node_disks(dst_ip='10.2.43.21')
    # print disk().get_free_disk_uuid_by_node_id(node_id=1,disk_type='data')
    # print disk().get_free_disk_info_by_node_id(node_id=1, disk_type='data')
    # print Os_Reliable().get_access_zone_node()
    # print Os_Reliable().get_access_zone_node(az_id=1)
    # print disk().get_node_ids_in_node_pool()

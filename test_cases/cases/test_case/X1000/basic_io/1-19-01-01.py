#!/usr/bin/python
# -*-coding:utf-8 -*

import os
import sys
import commands

import threading
import utils_path
import Lun_managerTest
import common2
import log
import get_config
import login

conf_file = common2.CONF_FILE  # 配置文件路径

file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件

deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP
osan = common2.oSan()


def run_vdb1():
    seekpct1 = 0
    rdpct1 = 30
    offset = "2048"
    xfersize1 = "(3k,100)"
    lun1 = osan.ls_scsi_dev(client_ips[0])
    mix_S_align = osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=seekpct1, rdpct=rdpct1)
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0],jn_jro="jn", whether_change_xml="N")

def iscsi_login():
    (vip, lun) = login.login()
    print vip
    print lun
    return vip , lun

def iscsi_logout(vip):
    for ip in vip:
        osan.iscsi_logout(client_ips[0], vip=ip)


def change_scsi(c_ip):
    log.info("备份iscsi配置文件")
    cmd1 = ("ssh %s \"cp /etc/iscsi/iscsid.conf /etc/iscsi/iscsid.conf.bak\"" % (c_ip))
    commands.getstatusoutput(cmd1)
    log.info("修改InitialR2T 参数,重启scsi服务")
    cmd2 = (
        "ssh %s \"sed -ni 's/node.session.iscsi.InitialR2T = .*/ode.session.iscsi.InitialR2T = Yes/p' /etc/iscsi/iscsid.conf;systemctl restart iscsid.service\"" % (
            c_ip))
    commands.getstatusoutput(cmd2)

def re_scsi(c_ip):
    log.info("还原iscsi配置文件")
    cmd1 = ("ssh %s \"cp /etc/iscsi/iscsid.conf.bak /etc/iscsi/iscsid.conf\"" % (c_ip))
    commands.getstatusoutput(cmd1)
    cmd2 = ("ssh %s \"systemctl restart iscsid.service\"" % (c_ip))
    commands.getstatusoutput(cmd2)

def case():
    log.info("step:1修改scsi配置文件")
    change_scsi(client_ips[0])
    log.info("step:2.挂载运行vdbench")
    vip, lun = iscsi_login()
    run_vdb1()
    log.info("step:3退出登录,还原iscsi")
    iscsi_logout(vip)
    re_scsi(client_ips[0])

def main():
    case()

if __name__ == '__main__':
    main()
#!/usr/bin/python
#-*-coding:utf-8 -*

import os,sys
import utils_path
import common2
import log
import get_config
import login

import commands

conf_file = common2.CONF_FILE    #配置文件路径

file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)     #获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)       #初始化日志文件

deploy_ips = get_config.get_env_ip_info(conf_file)       #获取集群IP列表
client_ips = get_config.get_allclient_ip()      #获取客户端IP

osan = common2.oSan()
(vip, lun) = login.login()
cmd = ("ssh %s 'dd if=/var/log/messages of=%s;hexdump -C -n 512 %s;sg_unmap --lba=0x1234 --num=100 %s;hexdump -C -n 512 %s'" % (client_ips[0], lun[0], lun[0], lun[0], lun[0]))
(res, final) = commands.getstatusoutput(cmd)
log.info(cmd)
if res != 0:
    log.error("Test failed.")
    exit(1)
else:
    log.info("Test success.")
    log.info(final)
#登出
for ip in vip:
    osan.iscsi_logout(client_ips[0],vip=ip)



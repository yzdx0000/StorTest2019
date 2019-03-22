#!/usr/bin/python
#-*-coding:utf-8 -*

import os,sys
import utils_path
import common2
import log
import get_config
import login
import commands
import random

conf_file = common2.CONF_FILE    #配置文件路径
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)     #获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)       #初始化日志文件

deploy_ips = get_config.get_env_ip_info(conf_file)       #获取集群IP列表
client_ips = get_config.get_allclient_ip()      #获取客户端IP

osan = common2.oSan()
(vip,lun) = login.login()
#lun = ['/dev/sdh','/dev/sdi','/dev/sdj','/dev/sdk','/dev/sdl','/dev/sdm','/dev/sdn','/dev/sdo']
#生成vdbench测试用的配置文件
#运行vdbench
jn_jro_on = random.randint(0,1)
if jn_jro_on == 0:
    log.info("Run vdbench without data check.")
    vdb_xml = osan.auto_gen_vdb_xml(lun=lun, thread=5)
    print vdb_xml
    cmd = ("cat %s" % (vdb_xml))
    res, output = commands.getstatusoutput(cmd)
    log.info(output)
    osan.run_vdb(client_ips[0], vdb_xml,output=deploy_ips[0])
else:
    log.info("Run vdbench with data check.")
    vdb_xml = osan.auto_gen_vdb_jn_xml(lun=lun, thread=5,output=deploy_ips[0])
    print vdb_xml
    cmd = ("cat %s" % (vdb_xml))
    res, output = commands.getstatusoutput(cmd)
    log.info(output)
    osan.run_vdb(client_ips[0], vdb_xml, jn_jro=jn_jro_on,output=deploy_ips[0])
#登出
osan.iscsi_logout(client_ips[0],vip=vip[0])

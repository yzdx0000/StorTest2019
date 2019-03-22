#!/usr/bin/python
#-*-coding:utf-8 -*

import os,sys
import utils_path
import common2
import log
import get_config
import login


conf_file = common2.CONF_FILE    #配置文件路径

file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)     #获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)       #初始化日志文件

deploy_ips = get_config.get_env_ip_info(conf_file)       #获取集群IP列表
client_ips = get_config.get_allclient_ip()      #获取客户端IP

osan = common2.oSan()
(vip, lun) = login.login()

#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 0
#offset = "2048"
align = "2048"
xfersize = "(15k,20,31k,10,63k,30,255k,40),unmappct=20"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, seekpct=seekpct, rdpct=rdpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml, output=deploy_ips[0], unmap="Y")
#登出
for ip in vip:
    osan.iscsi_logout(client_ips[0],vip=ip)



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
if len(lun) < 2 :
    log.error("There is not enough luns on the hosts, we must require two luns.")
    exit(1)
#修改vdbench配置文件的参数值
rdpct1 = 100
rdpct2 = 0
seekpct1 = 30
seekpct2 = 80
#offset = "8192"
#align = "3072"
xfersize1 = "(256k,20,384k,10,1536k,30,8192k,40),unmappct=20"
xfersize2 = "(257k,20,513k,10,1023k,30,4078k,40),unmappct=20"
#vdb_write(self,sd=None,lun=None,wd=None,offset=0,align=0,xfersize="4k",rdpct=0,seekpct=0,threads=4)
osan.vdb_write(sd="default")
for i in range(0,len(lun)):
    j=i+1
    if i % 2 == 0:
        vdb_xml = osan.vdb_write(sd="sd"+str(j),lun=lun[i],wd="wd"+str(j),xfersize=xfersize1,seekpct=seekpct1,rdpct=rdpct1)
    else:
        vdb_xml = osan.vdb_write(sd="sd"+str(j),lun=lun[i],wd="wd"+str(j),xfersize=xfersize2,seekpct=seekpct2,rdpct=rdpct2)
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
#jn_jro = "no"
osan.run_vdb(client_ips[0], vdb_xml, output=deploy_ips[0], unmap="Y")
#登出
for ip in vip:
    osan.iscsi_logout(client_ips[0],vip=ip)



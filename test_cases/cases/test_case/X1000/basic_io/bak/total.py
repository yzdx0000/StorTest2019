#!/usr/bin/python
#-*-coding:utf-8 -*

import os,sys
import utils_path
import common2
import log
import get_config

conf_file = common2.CONF_FILE    #配置文件路径
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)     #获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)       #初始化日志文件

deploy_ips = get_config.get_env_ip_info(conf_file)       #获取集群IP列表
client_ips = get_config.get_allclient_ip()      #获取客户端IP

osan = common2.oSan()
vip = osan.get_vip_address_pools(n_id="1",s_ip=deploy_ips[0])   #获取vip,二维数组
target = osan.discover_scsi(client_ips[0],vip[0][0])        #f发现target
osan.iscsi_login(client_ips[0], target)         #登录target
lun = osan.ls_scsi_dev(client_ips[0])       #获取Xstor设备

###### 1-01-01-01.py ########
log.info("1-01-01-01.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
offset = "2048"
#align = "1024"
xfersize = "(4k,20,8k,10,32k,30,128k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, offset=offset, seekpct=seekpct, rdpct=rdpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-01.py test success.")
###### 1-01-01-02.py ########
log.info("1-01-01-02.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
offset = "2048"
#align = "1024"
xfersize = "(1k,20,5k,10,30k,30,127k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, offset=offset, seekpct=seekpct, rdpct=rdpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-02.py test success.")
###### 1-01-01-03.py ########
log.info("1-01-01-03.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
offset = "2048"
#align = "1024"
xfersize = "(16k,20,32k,10,64k,30,192k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, offset=offset, seekpct=seekpct, rdpct=rdpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-03.py test success.")
###### 1-01-01-04.py ########
log.info("1-01-01-04.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
offset = "2048"
#align = "1024"
xfersize = "(15k,20,31k,10,63k,30,255k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, offset=offset, seekpct=seekpct, rdpct=rdpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-04.py test success.")
###### 1-01-01-05.py ########
log.info("1-01-01-05.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
#offset = "2048"
align = "2048"
xfersize = "(4k,20,8k,10,32k,30,128k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, seekpct=seekpct, rdpct=rdpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-05.py test success.")
###### 1-01-01-06.py ########
log.info("1-01-01-06.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
#offset = "2048"
align = "2048"
xfersize = "(1k,20,5k,10,30k,30,127k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, seekpct=seekpct, rdpct=rdpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-06.py test success.")
###### 1-01-01-07.py ########
log.info("1-01-01-07.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
#offset = "2048"
align = "2048"
xfersize = "(16k,20,32k,10,64k,30,192k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, seekpct=seekpct, rdpct=rdpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-07.py test success.")
###### 1-01-01-08.py ########
log.info("1-01-01-08.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
#offset = "2048"
align = "2048"
xfersize = "(15k,20,31k,10,63k,30,255k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, seekpct=seekpct, rdpct=rdpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-08.py test success.")
###### 1-01-01-09.py ########
log.info("1-01-01-09.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
offset = "8192"
align = "3072"
xfersize = "(1k,20,5k,10,30k,30,127k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-09.py test success.")
###### 1-01-01-10.py ########
log.info("1-01-01-10.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
offset = "8192"
align = "3072"
xfersize = "(4k,20,8k,10,32k,30,128k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-10.py test success.")
###### 1-01-01-11.py ########
log.info("1-01-01-11.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
offset = "8192"
align = "3072"
xfersize = "(16k,20,32k,10,64k,30,192k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-11.py test success.")
###### 1-01-01-12.py ########
log.info("1-01-01-12.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
offset = "8192"
align = "3072"
xfersize = "(15k,20,31k,10,63k,30,255k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-12.py test success.")
###### 1-01-01-13.py ########
log.info("1-01-01-13.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
offset = "2048"
#align = "3072"
xfersize = "(260k,20,520k,10,1020k,30,4080k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-13.py test success.")
###### 1-01-01-14.py ########
log.info("1-01-01-14.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
offset = "2048"
#align = "3072"
xfersize = "(257k,20,513k,10,1023k,30,4078k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-14.py test success.")
###### 1-01-01-15.py ########
log.info("1-01-01-15.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
offset = "2048"
#align = "3072"
xfersize = "(256k,20,512k,10,1024k,30,4096k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-15.py test success.")
###### 1-01-01-16.py ########
log.info("1-01-01-16.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
offset = "2048"
#align = "3072"
xfersize = "(270k,20,520k,10,1036k,30,4095k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-16.py test success.")
###### 1-01-01-17.py ########
log.info("1-01-01-17.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
#offset = "2048"
align = "2048"
xfersize = "(256k,20,512k,10,1024k,30,4096k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-17.py test success.")
###### 1-01-01-18.py ########
log.info("1-01-01-18.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
#offset = "2048"
align = "2048"
xfersize = "(257k,20,517k,10,1027k,30,4093k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-18.py test success.")
###### 1-01-01-19.py ########
log.info("1-01-01-19.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
#offset = "2048"
align = "2048"
xfersize = "(256k,20,384k,10,1536k,30,8192k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-19.py test success.")
###### 1-01-01-20.py ########
log.info("1-01-01-20.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
#offset = "2048"
align = "2048"
xfersize = "(240k,20,390k,10,1036k,30,4090k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-20.py test success.")
###### 1-01-01-21.py ########
log.info("1-01-01-21.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
offset = "8192"
align = "3072"
xfersize = "(256k,20,512k,10,1024k,30,4096k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-21.py test success.")
###### 1-01-01-22.py ########
log.info("1-01-01-22.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
offset = "8192"
align = "3072"
xfersize = "(257k,20,517k,10,1027k,30,4093k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, rdpct=rdpct, offset=offset, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-22.py test success.")
###### 1-01-01-23.py ########
log.info("1-01-01-23.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
offset = "8192"
align = "3072"
xfersize = "(256k,20,384k,10,1536k,30,8192k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-23.py test success.")
###### 1-01-01-24.py ########
log.info("1-01-01-24.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
offset = "8192"
align = "3072"
xfersize = "(240k,20,390k,10,1036k,30,4090k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-01-01-24.py test success.")
###### 1-02-01-01.py ########
log.info("1-02-01-01.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
#offset = "8192"
#align = "3072"
xfersize = "(4k,20,8k,10,32k,30,128k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-02-01-01.py test success.")
###### 1-02-01-02.py ########
log.info("1-02-01-02.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
#offset = "8192"
#align = "3072"
xfersize = "(1k,20,5k,10,30k,30,127k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-02-01-02.py test success.")
###### 1-02-01-03.py ########
log.info("1-02-01-03.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
#offset = "8192"
#align = "3072"
xfersize = "(16k,20,32k,10,64k,30,192k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-02-01-03.py test success.")
###### 1-02-01-04.py ########
log.info("1-02-01-04.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
#offset = "8192"
#align = "3072"
xfersize = "(15k,20,31k,10,63k,30,255k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-02-01-04.py test success.")
###### 1-02-02-01.py ########
log.info("1-02-02-01.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
#offset = "8192"
#align = "3072"
xfersize = "(256k,20,512k,10,1024k,30,4096k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-02-02-01.py test success.")
###### 1-02-02-02.py ########
log.info("1-02-02-02.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
#offset = "8192"
#align = "3072"
xfersize = "(257k,20,517k,10,1027k,30,4093k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-02-02-02.py test success.")
###### 1-02-02-03.py ########
log.info("1-02-02-03.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
#offset = "8192"
#align = "3072"
xfersize = "(256k,20,384k,10,1536k,30,8192k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-02-02-03.py test success.")
###### 1-02-02-04.py ########
log.info("1-02-02-04.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 50
#offset = "8192"
#align = "3072"
xfersize = "(240k,20,390k,10,1036k,30,4090k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-02-02-04.py test success.")
###### 1-03-01-01.py ########
log.info("1-03-01-01.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
offset = "2048"
#align = "1024"
xfersize = "(4k,20,8k,10,32k,30,128k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, offset=offset, seekpct=seekpct, rdpct=rdpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-01-01.py test success.")
###### 1-03-01-02.py ########
log.info("1-03-01-02.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
offset = "2048"
#align = "1024"
xfersize = "(1k,20,5k,10,30k,30,127k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, offset=offset, seekpct=seekpct, rdpct=rdpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-01-02.py test success.")
###### 1-03-01-03.py ########
log.info("1-03-01-03.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
offset = "2048"
#align = "1024"
xfersize = "(16k,20,32k,10,64k,30,192k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, offset=offset, seekpct=seekpct, rdpct=rdpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-01-03.py test success.")
###### 1-03-01-04.py ########
log.info("1-03-01-04.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
offset = "2048"
#align = "1024"
xfersize = "(15k,20,31k,10,63k,30,255k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, offset=offset, seekpct=seekpct, rdpct=rdpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-01-04.py test success.")
###### 1-03-01-05.py ########
log.info("1-03-01-05.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
#offset = "2048"
align = "2048"
xfersize = "(4k,20,8k,10,32k,30,128k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, seekpct=seekpct, rdpct=rdpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-01-05.py test success.")
###### 1-03-01-06.py ########
log.info("1-03-01-06.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
#offset = "2048"
align = "2048"
xfersize = "(1k,20,5k,10,30k,30,127k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, seekpct=seekpct, rdpct=rdpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-01-06.py test success.")
###### 1-03-01-07.py ########
log.info("1-03-01-07.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
#offset = "2048"
align = "2048"
xfersize = "(16k,20,32k,10,64k,30,192k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, seekpct=seekpct, rdpct=rdpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-01-07.py test success.")
###### 1-03-01-08.py ########
log.info("1-03-01-08.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
#offset = "2048"
align = "2048"
xfersize = "(15k,20,31k,10,63k,30,255k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, seekpct=seekpct, rdpct=rdpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-01-08.py test success.")
###### 1-03-01-09.py ########
log.info("1-03-01-09.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
offset = "8192"
align = "3072"
xfersize = "(1k,20,5k,10,30k,30,127k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-01-09.py test success.")
###### 1-03-01-10.py ########
log.info("1-03-01-10.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
offset = "8192"
align = "3072"
xfersize = "(4k,20,8k,10,32k,30,128k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-01-10.py test success.")
###### 1-03-01-11.py ########
log.info("1-03-01-11.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
offset = "8192"
align = "3072"
xfersize = "(16k,20,32k,10,64k,30,192k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-01-11.py test success.")
###### 1-03-01-12.py ########
log.info("1-03-01-12.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
offset = "8192"
align = "3072"
xfersize = "(15k,20,31k,10,63k,30,255k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-01-12.py test success.")
###### 1-03-02-01.py ########
log.info("1-03-02-01.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
offset = "2048"
#align = "3072"
xfersize = "(256k,20,512k,10,1024k,30,4096k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-02-01.py test success.")
###### 1-03-02-02.py ########
log.info("1-03-02-02.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
offset = "2048"
#align = "3072"
xfersize = "(257k,20,517k,10,1027k,30,4093k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-02-02.py test success.")
###### 1-03-02-03.py ########
log.info("1-03-02-03.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
offset = "2048"
#align = "3072"
xfersize = "(256k,20,384k,10,1536k,30,8192k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-02-03.py test success.")
###### 1-03-02-04.py ########
log.info("1-03-02-04.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
offset = "2048"
#align = "3072"
xfersize = "(240k,20,390k,10,1036k,30,4090k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-02-04.py test success.")
###### 1-03-02-05.py ########
log.info("1-03-02-05.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
align = "2048"
#align = "3072"
xfersize = "(256k,20,512k,10,1024k,30,4096k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-02-05.py test success.")
###### 1-03-02-06.py ########
log.info("1-03-02-06.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
#offset = "2048"
align = "2048"
xfersize = "(257k,20,517k,10,1027k,30,4093k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-02-06.py test success.")
###### 1-03-02-07.py ########
log.info("1-03-02-07.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
#offset = "2048"
align = "2048"
xfersize = "(256k,20,384k,10,1536k,30,8192k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-02-07.py test success.")
###### 1-03-02-08.py ########
log.info("1-03-02-08.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
#offset = "2048"
align = "2048"
xfersize = "(240k,20,390k,10,1036k,30,4090k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-02-08.py test success.")
###### 1-03-02-09.py ########
log.info("1-03-02-09.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
offset = "8192"
align = "3072"
xfersize = "(256k,20,512k,10,1024k,30,4096k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-02-09.py test success.")
###### 1-03-02-10.py ########
log.info("1-03-02-10.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
offset = "8192"
align = "3072"
xfersize = "(257k,20,517k,10,1027k,30,4093k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-02-10.py test success.")
###### 1-03-02-11.py ########
log.info("1-03-02-11.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
offset = "8192"
align = "3072"
xfersize = "(256k,20,384k,10,1536k,30,8192k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-02-11.py test success.")
###### 1-03-02-12.py ########
log.info("1-03-02-12.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
offset = "8192"
align = "3072"
xfersize = "(240k,20,390k,10,1036k,30,4090k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
osan.run_vdb(client_ips[0], vdb_xml)
log.info("1-03-02-12.py test success.")
###### 1-04-01-01.py ########
log.info("1-04-01-01.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
#offset = "8192"
#align = "3072"
xfersize = "(4k,20,8k,10,32k,30,128k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
jn_jro = "yes"
osan.run_vdb(client_ips[0], vdb_xml, jn_jro=jn_jro)
log.info("1-04-01-01.py test success.")
###### 1-04-01-02.py ########
log.info("1-04-01-02.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
#offset = "8192"
#align = "3072"
xfersize = "(1k,20,5k,10,30k,30,127k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
jn_jro = "yes"
osan.run_vdb(client_ips[0], vdb_xml, jn_jro=jn_jro)
log.info("1-04-01-02.py test success.")
###### 1-04-01-03.py ########
log.info("1-04-01-03.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
#offset = "8192"
#align = "3072"
xfersize = "(16k,20,32k,10,64k,30,192k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
jn_jro = "yes"
osan.run_vdb(client_ips[0], vdb_xml, jn_jro=jn_jro)
log.info("1-04-01-03.py test success.")
###### 1-04-01-04.py ########
log.info("1-04-01-04.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
#offset = "8192"
#align = "3072"
xfersize = "(15k,20,31k,10,63k,30,255k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
jn_jro = "yes"
osan.run_vdb(client_ips[0], vdb_xml, jn_jro=jn_jro)
log.info("1-04-01-04.py test success.")
###### 1-04-02-01.py ########
log.info("1-04-02-01.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
#offset = "8192"
#align = "3072"
xfersize = "(256k,20,512k,10,1024k,30,4096k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
jn_jro = "yes"
osan.run_vdb(client_ips[0], vdb_xml, jn_jro=jn_jro)
log.info("1-04-02-01.py test success.")
###### 1-04-02-02.py ########
log.info("1-04-02-02.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
#offset = "8192"
#align = "3072"
xfersize = "(257k,20,517k,10,1027k,30,4093k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
jn_jro = "yes"
osan.run_vdb(client_ips[0], vdb_xml, jn_jro=jn_jro)
log.info("1-04-02-02.py test success.")
###### 1-04-02-03.py ########
log.info("1-04-02-03.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
#offset = "8192"
#align = "3072"
xfersize = "(256k,20,284k,10,1536k,30,8192k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
jn_jro = "yes"
osan.run_vdb(client_ips[0], vdb_xml, jn_jro=jn_jro)
log.info("1-04-02-03.py test success.")
###### 1-04-02-04.py ########
log.info("1-04-02-04.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 0
seekpct = 50
#offset = "8192"
#align = "3072"
xfersize = "(240k,20,390k,10,1036k,30,4090k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, seekpct=seekpct)
print vdb_xml
#运行vdbench
jn_jro = "yes"
osan.run_vdb(client_ips[0], vdb_xml, jn_jro=jn_jro)
log.info("1-04-02-04.py test success.")
###### 1-05-01-01.py ########
log.info("1-05-01-01.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 0
offset = "2048"
#align = "3072"
xfersize = "(4k,20,8k,10,32k,30,128k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, offset=offset, seekpct=seekpct)
print vdb_xml
#运行vdbench
jn_jro = "yes"
osan.run_vdb(client_ips[0], vdb_xml, jn_jro=jn_jro)
log.info("1-05-01-01.py test success.")
###### 1-05-01-02.py ########
log.info("1-05-01-02.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 0
offset = "2048"
#align = "3072"
xfersize = "(2k,20,5k,10,30k,30,127k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, offset=offset, seekpct=seekpct)
print vdb_xml
#运行vdbench
jn_jro = "yes"
osan.run_vdb(client_ips[0], vdb_xml, jn_jro=jn_jro)
log.info("1-05-01-02.py test success.")
###### 1-05-01-03.py ########
log.info("1-05-01-03.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 0
offset = "2048"
#align = "3072"
xfersize = "(16k,20,32k,10,64k,30,192k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, offset=offset, seekpct=seekpct)
print vdb_xml
#运行vdbench
jn_jro = "yes"
osan.run_vdb(client_ips[0], vdb_xml, jn_jro=jn_jro)
log.info("1-05-01-03.py test success.")
###### 1-05-01-04.py ########
log.info("1-05-01-04.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 0
offset = "2048"
#align = "3072"
xfersize = "(15k,20,31k,10,63k,30,255k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, offset=offset, seekpct=seekpct)
print vdb_xml
#运行vdbench
jn_jro = "yes"
osan.run_vdb(client_ips[0], vdb_xml, jn_jro=jn_jro)
log.info("1-05-01-04.py test success.")
###### 1-05-01-05.py ########
log.info("1-05-01-05.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 0
#offset = "2048"
align = "2048"
xfersize = "(4k,20,8k,10,32k,30,128k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, align=align, seekpct=seekpct)
print vdb_xml
#运行vdbench
jn_jro = "yes"
osan.run_vdb(client_ips[0], vdb_xml, jn_jro=jn_jro)
log.info("1-05-01-05.py test success.")
###### 1-05-01-06.py ########
log.info("1-05-01-06.py test begin.")
#修改vdbench配置文件的参数值
rdpct = 100
seekpct = 0
#offset = "2048"
align = "2048"
xfersize = "(1k,20,5k,10,30k,30,127k,40)"
#生成vdbench测试用的配置文件
#模板：vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct, seekpct=seekpct)
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, rdpct=rdpct, align=align, seekpct=seekpct)
print vdb_xml
#运行vdbench
jn_jro = "yes"
osan.run_vdb(client_ips[0], vdb_xml, jn_jro=jn_jro)
log.info("1-05-01-06.py test success.")

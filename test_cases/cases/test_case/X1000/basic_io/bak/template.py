#-*-coding:utf-8 -*

import os,sys
import utils_path
import common2
import log
import get_config

conf_file = common2.CONF_FILE
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)     #获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)       #初始化日志文件

deploy_ips = get_config.get_env_ip_info(conf_file)       #获取集群IP列表
client_ips = get_config.get_allclient_ip()      #获取客户端IP
print deploy_ips
print client_ips
exit(1)
osan = common2.oSan()
vip = osan.get_vip_address_pools(n_id="1",s_ip=deploy_ips[0])
target = osan.discover_scsi(client_ips[0],vip[0][0])
iscsi = osan.iscsi_login(client_ips[0], target)
#iscsi = osan.iscsi_logout("10.22.129.6", target)
lun = osan.ls_scsi_dev(client_ips[0])
#lun=['/dev/sda','/dev/sdb','/dev/sdc']
rdpct = 50
offset = "1024"
align = "1024"
xfersize = "(1k,20,2k,80)"
vdb_xml = osan.gen_vdb_xml(lun=lun, xfersize=xfersize, align=align, offset=offset, rdpct=rdpct)
osan.run_vdb(client_ips[0], vdb_xml)

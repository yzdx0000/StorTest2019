#-*-coding:utf-8 -*

import utils_path
import common2
import get_config
import log
import os
import commands
import json
conf_file = common2.CONF_FILE    #配置文件路径

file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)     #获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)       #初始化日志文件

osan = common2.oSan()
deploy_ips = get_config.get_env_ip_info(conf_file)       #获取集群IP列表
client_ips = get_config.get_allclient_ip()      #获取客户端IP
svip = get_config.get_svip(conf_file)
log.info("svips:"+str(svip))
vip = get_config.get_vip(conf_file)
log.info("vips:"+str(vip))
storid = osan.get_storage_id(s_ip=deploy_ips[0])
nodeid = osan.get_nodes(s_ip=deploy_ips[0])
acc_zone_ids = osan.create_access_zone(s_ip=deploy_ips[0],node_id=str(nodeid).strip("[|]| ").replace(" ",""),name="acc_0")
osan.create_subnet(s_ip=deploy_ips[0],sv_ip=svip[0],access_zone_id=acc_zone_ids,name="subnet1")
sub_id =  osan.get_subnet_id(s_ip=deploy_ips[0])
osan.add_vip_address_pool(s_ip=deploy_ips[0],subnet_id=sub_id[0],domain_name="vip1.com",vip=vip[0])
osan.enable_san(s_ip=deploy_ips[0],access_zone_id=acc_zone_ids)
hg_id1 = osan.create_host_group(s_ip=deploy_ips[0],hg_name="hg_1")
hg_id2 = osan.create_host_group(s_ip=deploy_ips[0],hg_name="hg_2")
h_id1 = osan.add_host(s_ip=deploy_ips[0],h_name="h_1",hg_id=hg_id1[0])
h_id2 = osan.add_host(s_ip=deploy_ips[0],h_name="h_2",hg_id=hg_id2[0])
osan.add_initiator(s_ip=deploy_ips[0],h_id=h_id1[0],iqn="iqn.1990-21.com.sugon",alias="dws_20.initiator")
osan.add_initiator(s_ip=deploy_ips[0],h_id=h_id2[0],iqn="iqn.1991-21.com.sugon",alias="dws_21.initiator")
#cmd = ("ssh %s 'pscli --command=get_node_pools'" % (deploy_ips[0]))
#rep = []
#strip = []
#(res, final) = commands.getstatusoutput(cmd)
#if res != 0:
#    log.error("Get node pool error.")
#    exit(1)
#else:
#    final = json.loads(final)
#    if final['result']['total'] == 0:
#        exit(1)
#    else:
#        finals = final['result']['node_pools']
#        for reps in finals:
#            rep.append(reps['replica_num'])
#            strip.append(reps['stripe_width'])
#print rep
#print strip
for i in range(0,12):
    osan.create_lun(s_ip=deploy_ips[0],lun_name="lun_"+str(i),stor_pool_id=storid[1],acc_zone_id=acc_zone_ids)
lun = osan.get_lun(s_ip=deploy_ips[0])
for i in lun:
    if i%2 == 0:
        osan.map_lun(s_ip=deploy_ips[0],lun_ids=i,hg_id=hg_id1[0])
    else:
        osan.map_lun(s_ip=deploy_ips[0],lun_ids=i,hg_id=hg_id2[0])

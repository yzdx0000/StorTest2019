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
cmd = ("ssh %s 'pscli --command=get_node_pools'" % (deploy_ips[0]))
rep = []
strip = []
(res, final) = commands.getstatusoutput(cmd)
if res != 0:
    log.error("Get node pool error.")
    exit(1)
else:
    final = json.loads(final)
    if final['result']['total'] == 0:
        exit(1)
    else:
        finals = final['result']['node_pools']
        for rep in finals:
            rep.append(rep['replica_num'])
            strip.append(rep['stripe_width'])
print rep
print strip
exit(1)
for i in range(0,12):
    osan.create_lun(s_ip=deploy_ips[0],lun_name="lun_"+str(i),stor_pool_id=storid[1],acc_zone_id=acc_zone_ids)
lun = osan.get_lun(s_ip=deploy_ips[0])
for i in lun:
    osan.map_lun(s_ip=deploy_ips[0],lun_ids=i,hg_id=hg_id[0])

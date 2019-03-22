#-*-coding:utf-8 -*

import utils_path
import common2
import get_config

conf_file = common2.CONF_FILE    #配置文件路径
osan = common2.oSan()
deploy_ips = get_config.get_env_ip_info(conf_file)
lun_map_ids = osan.get_lun_maps(deploy_ips[0])
#for lun_map_id in lun_map_ids:
#    osan.delete_lun_map(s_ip=deploy_ips[0],map_id=lun_map_id)
lun_ids = osan.get_lun(s_ip=deploy_ips[0])
#for lun_id in lun_ids:
#    print lun_id
#    osan.delete_lun(s_ip=deploy_ips[0],lun_id=lun_id)
ini_ids = osan.get_initiators(s_ip=deploy_ips[0])
for ini_id in  ini_ids:
    print ini_id
    osan.remove_initiator(s_ip=deploy_ips[0],ini_id=ini_id)

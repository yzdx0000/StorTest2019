#-*-coding:utf-8 -*

import utils_path
import common2
import get_config
import Lun_managerTest
import log

conf_file = common2.CONF_FILE    #配置文件路径
svip = get_config.get_svip(conf_file)
lun_osan = Lun_managerTest.oSan()
def login():
    deploy_ips = get_config.get_env_ip_info(conf_file)
    client_ips = get_config.get_allclient_ip()
    osan = common2.oSan()
    vip = osan.get_vip_address_pools(n_id="1",s_ip=deploy_ips[0])
    vip = osan.analysis_vip(vip[0])
    for c_ip in client_ips:
        target_list = lun_osan.discover_scsi_list(client_ip=c_ip, svip=svip[0])
        log.info("Get Info:\nSvip list:%s \nTarget list:%s" % (svip[0], target_list))
        for tag in target_list:
            log.info("主机发现存储target：%s,主机 %s 将进行SCSI登录" % (tag, c_ip))
            osan.iscsi_login(client_ip=c_ip, iqn=tag)
    return vip

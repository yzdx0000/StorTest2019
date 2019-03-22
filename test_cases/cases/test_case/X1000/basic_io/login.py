#-*-coding:utf-8 -*

import utils_path
import common2
import get_config
import time
import log
import Lun_managerTest
conf_file = common2.CONF_FILE    #配置文件路径
lun_osan = Lun_managerTest.oSan()
svip = get_config.get_svip(conf_file)

def login():
    deploy_ips = get_config.get_env_ip_info(conf_file)       #获取集群IP列表
    client_ips = get_config.get_allclient_ip()      #获取客户端IP
#    deploy_ips = ["10.22.128.66"]       #获取集群IP列表
#    client_ips = ["10.22.128.69"]      #获取客户端IP
    osan = common2.oSan()
    lun = []
    vip_pool_id = osan.get_vip_address_pools_id(s_ip=deploy_ips[0])
    # iqn = osan.get_iqn(s_ip=deploy_ips[0],ids=vip_pool_id[0])
    # osan.write_iqn(cli_ip=client_ips[0],iqn=iqn[0])
    vip = osan.get_vip_address_pools(n_id="1",s_ip=deploy_ips[0])   #获取vip,二维数组
    vip = osan.analysis_vip(vip[0])
    for c_ip in client_ips:
        target_list = lun_osan.discover_scsi_list(client_ip=c_ip, svip=svip[0])
        log.info("Get Info:\nSvip list:%s \nTarget list:%s" % (svip[0], target_list))
        for tag in target_list:
            log.info("主机发现存储target：%s,主机 %s 将进行SCSI登录" % (tag, c_ip))
            osan.iscsi_login(client_ip=c_ip, iqn=tag)
    time.sleep(2)
    lun = osan.ls_scsi_dev(client_ips[0])       #获取Xstor设备
    return vip, lun

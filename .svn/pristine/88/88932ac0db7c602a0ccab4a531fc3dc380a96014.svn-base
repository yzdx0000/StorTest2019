#-*-coding:utf-8 -*

import utils_path
import common2
import get_config

conf_file = common2.CONF_FILE    #配置文件路径
print (conf_file)
def login():
    deploy_ips = get_config.get_env_ip_info(conf_file)       #获取集群IP列表
    client_ips = get_config.get_allclient_ip()      #获取客户端IP
    osan = common2.oSan()
    iqn = osan.get_iqn(s_ip=deploy_ips[0])
    osan.write_iqn(cli_ip=client_ips[0],iqn=iqn[0])
    osan.write_iqn(cli_ip=client_ips[1],iqn=iqn[1])
    vip = osan.get_vip_address_pools(n_id="1",s_ip=deploy_ips[0])   #获取vip,二维数组
    vip = osan.analysis_vip(vip[0])
    for ip in vip:
        for cli in client_ips:
            target = osan.discover_scsi(cli, ip)        #f发现target
            osan.iscsi_login(cli, target)         #登录target
    #osan.iscsi_logout(client_ips[0])
    #osan.iscsi_logout(client_ips[1])
    #lun = osan.ls_scsi_dev(client_ips[0])       #获取Xstor设备
    return vip

if __name__ == '__main__':
    login()

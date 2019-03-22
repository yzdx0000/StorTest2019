# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:创建lun映射

步骤:
1）配置节点池，配置存储池，创建访问区
2）配置SVIP，添加VIP
3）配置主机组，添加主机添加启动器，创建lun映射

检查项:
1）lun映射状态成功
"""
import os, sys
import time
import utils_path
import Lun_managerTest
import common
import log
import error
import get_config
import login
import error
import decorator_func
from get_config import config_parser as cp
import env_manage_lun_manage

"""初始化日志和全局变量"""
conf_file = get_config.CONFIG_FILE  # 配置文件路径
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件

log.info("---------------全局初始化操作-----------------")
node_ip1 = env_manage_lun_manage.node_ip1
node_ip2 = env_manage_lun_manage.deploy_ips[1]
client_ip1 = env_manage_lun_manage.client_ips[0]
client_ip2 = env_manage_lun_manage.client_ips[1]
esxi_ip = env_manage_lun_manage.Esxi_ips
osan = Lun_managerTest.oSan()
deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP


def case():
    storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
    az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]

    hg_id = osan.create_host_group(s_ip=deploy_ips[0], hg_name='myhostgroup1')
    h_id = osan.add_host(s_ip=deploy_ips[0], h_name='host1', hg_id=hg_id)
    ini_id = osan.add_initiator(s_ip=deploy_ips[0], h_id=h_id, iqn=cp("add_initiator", "iqn"),
                                alias=cp("add_initiator", "alias"), auth_type="CHAP", user=cp("CHAP", "CHAP_user"),
                                passwd=cp("CHAP", "CHAP_passwd"))
    decorator_func.judge_target(
        osan.get_option_single(s_ip=deploy_ips[0], command="get_initiators", indexname="initiators"
                               , argv2="auth_type", ids="ids", argv1=ini_id),
        "CHAP")
    osan.update_initiator(s_ip=deploy_ips[0], ini_id=ini_id, alias=cp("add_initiator", "alias"), auth_type='CHAP',
                          user=cp("CHAP", "CHAP_user"), passwd=cp('CHAP', 'CHAP_updated_passwd'))
    osan.update_iscsid_conf(cli_ip=client_ips[0], CHAPTYPE='CHAP_updated_passwd', s_ip=client_ips[0])
    global lun_id
    for i in range(1, 2):
        lun_id = osan.create_lun(s_ip=deploy_ips[0], total_bytes='1073741824', lun_type="THIN",
                                 lun_name='LUN{}'.format(i),
                                 stor_pool_id=storage_pool_id, acc_zone_id=az_id)
        log.info(lun_id)

        decorator_func.judge_target(
            osan.get_option_single(s_ip=deploy_ips[0], command="get_luns", indexname="luns"
                                   , argv2="name", ids="ids", argv1=lun_id),
            'LUN{}'.format(i))
    lun_ids = osan.get_lun(s_ip=deploy_ips[0])
    for lun_id in lun_ids:
        lun_map_id = osan.map_lun(s_ip=deploy_ips[0], lun_ids=lun_id, hg_id=hg_id)
        decorator_func.judge_target(
            osan.get_option_single(s_ip=deploy_ips[0], command='get_lun_maps', indexname='lun_maps',
                                   argv2="lun_map_state",
                                   ids="ids", argv1=lun_map_id),
            'LUNMAP_READY')
    login.login()
    msg = env_manage_lun_manage.osan.ls_scsi_dev(client_ip1)
    env_manage_lun_manage.assert_ins.assertEqual(1, len(msg))


# @decorator_func.tasklet(int(cp('timeout', 'second')), maxretry=int(cp('timeout', 'maxretry')))
def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean()
    case()  # 用例步骤
    env_manage_lun_manage.revert_env()
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()

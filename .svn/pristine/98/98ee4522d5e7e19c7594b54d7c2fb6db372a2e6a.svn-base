# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容：客户端重启自动挂载

步骤:
1）配置访问区，配置节点池，配置存储池，配置主机组，添加主机，添加启动器
2）将逻辑卷映射至主机
3）重启客户端操作系统

检查项:
1）节点池，存储池，主机组，主机创建成功
2）重启完成后逻辑卷自动挂载
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
    # osan.update_param(s_ip=deploy_ips[0], section='MGR', name='min_meta_replica', current='1')  # 降级模式
    """osan.create_node_pool(s_ip=deploy_ips[0], node_ids=cp('create_node_pool', 'node_ids'),
                          replica_num=cp("create_node_pool", "replica_num"),
                          stripe_width=cp('create_node_pool', 'stripe_width'),
                          disk_parity_num=cp("create_node_pool", "disk_parity_num"),
                          node_parity_num=cp("create_node_pool", "node_parity_num"),
                          name="nodepool1")
    osan.startup(s_ip=deploy_ips[0])
    osan.create_storage_pool(s_ip=deploy_ips[0], node_pool_ids='1', name='pool1')
    osan.update_param(s_ip=deploy_ips[0], section='MGR', name='mgcd_auto_mount_flag', current='0')  # 解除自动挂载
    osan.create_access_zone(s_ip=deploy_ips[0], node_id='1,2,3', name='accesszone1')
    osan.create_subnet(s_ip=deploy_ips[0], access_zone_id='1', name='subnet1', sv_ip=cp("create_subnet", "sv_ip"),
                       mask=cp("create_subnet", "mask"),
                       gate_way=cp("create_subnet", "gate_way"),
                       network_interface=cp("create_subnet", "network_interface"))
    osan.add_vip_address_pool(s_ip=deploy_ips[0], subnet_id='1', domain_name=cp("add_vip_address_pool", "domain_name"),
                              vip=cp("add_vip_address_pool", "vip"))
    osan.enable_san(s_ip=deploy_ips[0], access_zone_id=1)"""
    hg_id1 = env_manage_lun_manage.osan.create_host_group(s_ip=deploy_ips[0], hg_name="hg_1")
    hg_id2 = env_manage_lun_manage.osan.create_host_group(s_ip=deploy_ips[0], hg_name="hg_2")
    h_id1 = env_manage_lun_manage.osan.add_host(s_ip=deploy_ips[0], h_name="h_1", hg_id=hg_id1)
    h_id2 = env_manage_lun_manage.osan.add_host(s_ip=deploy_ips[0], h_name="h_2", hg_id=hg_id2)
    ini_id1 = env_manage_lun_manage.osan.add_initiator(s_ip=deploy_ips[0], h_id=h_id1, iqn=cp('add_initiator', 'iqn'),
                                                       alias=cp('add_initiator', 'alias'))
    ini_id2 = env_manage_lun_manage.osan.add_initiator(s_ip=deploy_ips[0], h_id=h_id2, iqn=cp('add_initiator', 'iqn1'),
                                                       alias=cp('add_initiator', 'alias1'))
    osan.update_iscsid_conf(cli_ip=client_ips[0], CHAPTYPE='None', s_ip=client_ips[0])
    osan.update_iscsid_conf(cli_ip=client_ips[0], CHAPTYPE='None', s_ip=client_ips[1])
    global lun_id
    for i in range(5):
        lun_id = osan.create_lun(s_ip=deploy_ips[0], total_bytes='1073741824', lun_type="THIN",
                                 lun_name='LUN{}'.format(i),
                                 stor_pool_id=2, acc_zone_id=1)
        log.info(lun_id)

        decorator_func.judge_target(
            osan.get_option_single(s_ip=deploy_ips[0], command="get_luns", indexname="luns"
                                   , argv2="name", ids="ids", argv1=lun_id),
            'LUN{}'.format(i))
    lun_ids = osan.get_lun(s_ip=deploy_ips[0])
    for lun_id in lun_ids:
        lun_map_id = osan.map_lun(s_ip=deploy_ips[0], lun_ids=lun_id, hg_id=hg_id1)
        decorator_func.judge_target(
            osan.get_option_single(s_ip=deploy_ips[0], command='get_lun_maps', indexname='lun_maps',
                                   argv2="lun_map_state",
                                   ids="ids", argv1=lun_map_id),
            'LUNMAP_READY')
    login.login()

    msg = osan.ls_scsi_dev(client_ip=client_ips[0])
    env_manage_lun_manage.assert_ins.assertEqual(len(msg), 5, 'xstor device is  not found!')
    env_manage_lun_manage.iscsi_logout()
    env_manage_lun_manage.clean_lun_map()
    for lun_id in lun_ids:
        lun_map_id = osan.map_lun(s_ip=deploy_ips[0], lun_ids=lun_id, hg_id=hg_id2)
        decorator_func.judge_target(
            osan.get_option_single(s_ip=deploy_ips[0], command='get_lun_maps', indexname='lun_maps',
                                   argv2="lun_map_state",
                                   ids="ids", argv1=lun_map_id),
            'LUNMAP_READY')

    login.login()

    msg = osan.ls_scsi_dev(client_ip=client_ips[1])
    env_manage_lun_manage.assert_ins.assertEqual(len(msg), 5, 'xstor device is  not found!')


# @decorator_func.tasklet(int(env_manage.cp('timeout', 'second')), maxretry=int(env_manage.cp('timeout', 'maxretry')))
def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean()
    case()  # 用例步骤
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()

# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:精简卷和逻辑卷在同一池内交替创建

步骤:
1）在访问区配置中，每个节点取1块磁盘创建副本模式存储池，共创建三个存储池pool1，pool2，pool3；
2）创建逻辑卷属性默认，选择pool2存储池，创建逻辑卷LUN1，容量5GB，创建精简卷LUN2，容量10GB，创建逻辑卷LUN3，容量15GB，创建精简卷LUN4，容量20GB；
3）提交后创建成功。

检查项:
1）存储池创建成功
2）精简卷创建成功，逻辑卷列表中可查看到该逻辑卷
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

deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP

osan = Lun_managerTest.oSan()

"""读取存储池的容量"""
storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
storage_pool_size = env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1,
                                                                 command='get_storage_pools', ids="ids",
                                                                 indexname="storage_pools",
                                                                 argv2="total_bytes",
                                                                 argv1=storage_pool_id)


def case():
    """osan.uninstall_Xstor(deploy_ips[0])

    osan.install_Xstor(deploy_ips[0])
    # osan.update_param(s_ip=deploy_ips[0], section='MGR', name='min_meta_replica', current='1')  # 降级模式
    osan.create_node_pool(s_ip=deploy_ips[0], node_ids=cp('create_node_pool', 'node_ids'),
                          replica_num=cp("create_node_pool", "replica_num"),
                          stripe_width=cp('create_node_pool', 'stripe_width'),
                          disk_parity_num=cp("create_node_pool", "disk_parity_num"),
                          node_parity_num=cp("create_node_pool", "node_parity_num"),
                          name="nodepool1")
    osan.startup(s_ip=deploy_ips[0])
    osan.create_storage_pool(s_ip=deploy_ips[0], node_pool_ids='1', name='pool1', disk_ids='2,7,11')
    osan.create_storage_pool(s_ip=deploy_ips[0], node_pool_ids='1', name='pool2', disk_ids='3,6,10')
    osan.create_storage_pool(s_ip=deploy_ips[0], node_pool_ids='1', name='pool3', disk_ids='4,8,12')
    osan.update_param(s_ip=deploy_ips[0], section='MGR', name='mgcd_auto_mount_flag', current='0')  # 解除自动挂载
    osan.create_access_zone(s_ip=deploy_ips[0], node_id='1,2,3', name='accesszone1')
    osan.create_subnet(s_ip=deploy_ips[0], access_zone_id='1', name='subnet1', sv_ip=cp("create_subnet", "sv_ip"),
                       mask=cp("create_subnet", "mask"),
                       gate_way=cp("create_subnet", "gate_way"),
                       network_interface=cp("create_subnet", "network_interface"))
    osan.add_vip_address_pool(s_ip=deploy_ips[0], subnet_id='1', domain_name=cp("add_vip_address_pool", "domain_name"),
                              vip=cp("add_vip_address_pool", "vip"))
    osan.enable_san(s_ip=deploy_ips[0], access_zone_id=1)"""
    lun_id = osan.create_lun(s_ip=deploy_ips[0], total_bytes='5368709120', lun_type="THICK",
                             lun_name='LUN1',
                             stor_pool_id=storage_pool_id, acc_zone_id=az_id)
    decorator_func.judge_target(
        osan.get_option_single(s_ip=deploy_ips[0], command="get_luns", indexname="luns"
                               , argv2="lun_type", ids="ids", argv1=lun_id),
        'LUN_TYPE_THICK')
    lun_id = osan.create_lun(s_ip=deploy_ips[0], total_bytes='10737418240', lun_type="THIN",
                             lun_name='LUN2',
                             stor_pool_id=storage_pool_id, acc_zone_id=az_id)
    decorator_func.judge_target(
        osan.get_option_single(s_ip=deploy_ips[0], command="get_luns", indexname="luns"
                               , argv2="lun_type", ids="ids", argv1=lun_id),
        'LUN_TYPE_THIN')
    lun_id = osan.create_lun(s_ip=deploy_ips[0], total_bytes='16106127360', lun_type="THICK",
                             lun_name='LUN3',
                             stor_pool_id=storage_pool_id, acc_zone_id=az_id)
    decorator_func.judge_target(
        osan.get_option_single(s_ip=deploy_ips[0], command="get_luns", indexname="luns"
                               , argv2="lun_type", ids="ids", argv1=lun_id),
        'LUN_TYPE_THICK')
    lun_id = osan.create_lun(s_ip=deploy_ips[0], total_bytes='21474836480', lun_type="THIN",
                             lun_name='LUN4',
                             stor_pool_id=storage_pool_id, acc_zone_id=az_id)
    decorator_func.judge_target(
        osan.get_option_single(s_ip=deploy_ips[0], command="get_luns", indexname="luns"
                               , argv2="lun_type", ids="ids", argv1=lun_id),
        'LUN_TYPE_THIN')


# @decorator_func.tasklet(int(cp('timeout', 'second')), maxretry=int(cp('timeout', 'maxretry')))
def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean()
    case()
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()
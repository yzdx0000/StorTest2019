# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:p量添加主机到主机组

步骤:
1、配置节点池，配置存储池，创建访问区
2、配置SVIP，添加VIP，配置创建主机组
3、主机组中批量添加10个主机 （add_hosts_to_group）

检查项:
1、节点池，存储池，访问区创建成功
2、创建SVIP、VIP成功，主机组成功创建
3、主机添加成功
4、移除主机成功，主机在系统中依然存在
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

"""读取存储池的容量"""
storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
storage_pool_size = env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1,
                                                                 command='get_storage_pools', ids="ids",
                                                                 indexname="storage_pools",
                                                                 argv2="total_bytes",
                                                                 argv1=storage_pool_id)


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

    hg_id = env_manage_lun_manage.osan.create_host_group(s_ip=node_ip1, hg_name='myhostgroup1')
    for i in range(10):
        env_manage_lun_manage.osan.add_host(s_ip=node_ip1, h_name='host{}'.format(i), hg_id=hg_id)


# @decorator_func.tasklet(int(env_manage.cp('timeout', 'second')), maxretry=int(env_manage.cp('timeout', 'maxretry')))
def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.rel_check_before_run(filename=file_name)  # 环境检测和准备
    env_manage_lun_manage.clean()
    case()  # 用例步骤
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()

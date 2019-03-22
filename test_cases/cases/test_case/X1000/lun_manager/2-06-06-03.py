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

node_ip = env_manage_lun_manage.deploy_ips[0]

file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件


def case():
    # osan.update_param(s_ip=deploy_ips[0], section='MGR', name='min_meta_replica', current='1')  # 降级模式
    nodeids = env_manage_lun_manage.osan.get_nodes(s_ip=node_ip)
    nodes_ids = (",".join('%s' % id for id in nodeids))

    node_pool_id = env_manage_lun_manage.osan.create_node_pool(s_ip=node_ip, node_ids=nodes_ids,
                                                               replica_num=cp("create_node_pool", "replica_num"),
                                                               stripe_width=cp('create_node_pool', 'stripe_width'),
                                                               disk_parity_num=cp("create_node_pool", "disk_parity_num"),
                                                               node_parity_num=cp("create_node_pool", "node_parity_num"),
                                                               name=cp('create_node_pool', 'name'))
    env_manage_lun_manage.osan.startup(s_ip=node_ip)
    stor_id = env_manage_lun_manage.osan.create_storage_pool(s_ip=node_ip, node_pool_ids=node_pool_id, name='pool1')
    env_manage_lun_manage.osan.update_param(s_ip=node_ip, section=cp('update_param', 'section'),
                                            name=cp('update_param', 'name'),
                                            current=cp('update_param', 'current'))  # 解除自动挂载
    az_id = env_manage_lun_manage.osan.create_access_zone(s_ip=node_ip, node_id=nodes_ids, name='qwertyuiopasdfghjklzxcvbnm12345')

    sub_id = env_manage_lun_manage.osan.create_subnet(s_ip=node_ip, access_zone_id=az_id, name='subnet1',
                                                      sv_ip=cp("create_subnet", "sv_ip"),
                                                      mask=cp("create_subnet", "mask"),
                                                      vv_ip=cp("create_subnet", "vv_ip"),
                                                      gate_way=cp("create_subnet", "gate_way"),
                                                      network_interface=cp("create_subnet", "network_interface"))
    decorator_func.judge_target(
        env_manage_lun_manage.osan.get_option_single(s_ip=node_ip, command="get_subnets", indexname="subnets"
                                                     , argv2="name", ids="ids", argv1=sub_id), "subnet1")
    for i in range(1, 4):
        env_manage_lun_manage.osan.enable_san(s_ip=node_ip, access_zone_id=az_id)


#@decorator_func.tasklet(int(env_manage.cp('timeout', 'second')), maxretry=int(env_manage.cp('timeout', 'maxretry')))
def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean()
    case()  # 用例步骤
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()

# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:主机组创建

步骤:
1）配置节点池，配置存储池，创建访问区
2）配置SVIP，添加VIP，配置创建一个主机组

检查项:
1）节点池，存储池，访问区创建成功
2）创建SVIP、VIP成功，主机组成功创建
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

"""读取存储池的容量"""
storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
storage_pool_size = env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1,
                                                                 command='get_storage_pools', ids="ids",
                                                                 indexname="storage_pools",
                                                                 argv2="total_bytes",
                                                                 argv1=storage_pool_id)


def case():
    hg_id = osan.create_host_group(s_ip=deploy_ips[0], hg_name='myhostgroup2')
    decorator_func.judge_target(
        osan.get_option_single(s_ip=deploy_ips[0], command="get_host_groups", indexname="host_groups"
                               , argv2="name", ids="ids", argv1=hg_id), "myhostgroup2")
    h_id = osan.add_host(s_ip=deploy_ips[0], h_name='host1', hg_id=hg_id)
    decorator_func.judge_target(
        osan.get_option_single(s_ip=deploy_ips[0], command="get_hosts", indexname="hosts"
                               , argv2="name", ids="ids", argv1=h_id), "host1")


#@decorator_func.tasklet(int(env_manage.cp('timeout', 'second')), maxretry=int(env_manage.cp('timeout', 'maxretry')))
def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean()
    case()
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()
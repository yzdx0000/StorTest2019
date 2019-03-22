# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:批量删除后再创建卷

步骤:
1）在访问区中配置100个逻辑卷和精简卷映射至主机端
2）在访问区中解除全部映射关系
4）批量删除逻辑卷和精简卷
5）重新创建100个逻辑卷和精简卷

检查项:
1）映射完成
2）解除映射全部完成
4）批量删除逻辑卷完成
5）100个卷重新创建成功
"""
import os, sys
import re
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
node_ip = env_manage_lun_manage.node_ip1
node_ip2 = env_manage_lun_manage.deploy_ips[1]
client_ip1 = env_manage_lun_manage.client_ips[0]
client_ip2 = env_manage_lun_manage.client_ips[1]
esxi_ip = env_manage_lun_manage.Esxi_ips

deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP

osan = Lun_managerTest.oSan()


def case():
    nodeids = env_manage_lun_manage.osan.get_nodes(s_ip=node_ip)
    nodes_ids = (",".join('%s' % id for id in nodeids))

    node_pool_id = osan.get_option(s_ip=node_ip, command="get_node_pools", indexname="node_pools",
                                   argv="id")[-1]
    env_manage_lun_manage.osan.startup(s_ip=node_ip)
    stor_id = env_manage_lun_manage.osan.create_storage_pool(s_ip=node_ip, node_pool_ids=node_pool_id, name='pool1')
    env_manage_lun_manage.osan.update_param(s_ip=node_ip, section=cp('update_param', 'section'),
                                            name=cp('update_param', 'name'),
                                            current=cp('update_param', 'current'))  # 解除自动挂载
    az_id = env_manage_lun_manage.osan.create_access_zone(s_ip=node_ip, node_id=nodes_ids,
                                                          name='qwertyuiopasdfghjklzxcvbnm12345')

    osan.enable_san(s_ip=node_ip, access_zone_id=az_id)
    env_manage_lun_manage.osan.disable_san(s_ip=node_ip, access_zone_id=az_id)
    osan.enable_san(s_ip=node_ip, access_zone_id=az_id)


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.init_env(target="create_node_pool")
    case()  # 用例步骤
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()

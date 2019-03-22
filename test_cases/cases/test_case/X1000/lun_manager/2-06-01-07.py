# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:访问区创建

步骤:
1）配置节点池设置副本数为3
2）创建存储池，使用全部磁盘
3）通过管理端cli命令创建访问区“pscli --command=create_access_zone --node_ids=1,2,3 --name=accesszone1”

检查项:
1）节点池创建成功
2）存储池创建成功
3）访问区创建成功
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
node_ids_list = env_manage_lun_manage.osan.get_nodes(node_ip1)
node_ids = ",".join('%s' % id for id in node_ids_list)

osan = Lun_managerTest.oSan()


def case():
    node_pool_id = \
        env_manage_lun_manage.osan.get_option(s_ip=node_ip1, command="get_node_pools", indexname="node_pools",
                                              argv="id")[-1]
    osan.startup(node_ip1)
    env_manage_lun_manage.osan.create_storage_pool(s_ip=node_ip1, node_pool_ids=node_pool_id, name='storage_pool1', )
    az_id1 = osan.create_access_zone(s_ip=deploy_ips[0], node_id=node_ids_list[0], name='accesszonetest1')
    az_id2 = osan.create_access_zone(s_ip=deploy_ips[0], node_id=node_ids[1], name='accesszonetest2')
    az_id3 = osan.create_access_zone(s_ip=deploy_ips[0], node_id=node_ids[2], name='accesszonetest3')

    azs = osan.get_access_zone_id(s_ip=node_ip1)
    log.info(azs)
    for az in azs:
        osan.disable_san(s_ip=node_ip1, access_zone_id=az)
        osan.delete_access_zone(s_ip=node_ip1, azid=az)


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean(target="storage_pool")
    case()  # 用例步骤
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()
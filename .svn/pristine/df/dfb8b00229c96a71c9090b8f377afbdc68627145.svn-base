# !/usr/bin/python
# -*-coding:utf-8 -*

import os, sys
import time
import random
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
    storage_pool_id = env_manage_lun_manage.osan.create_storage_pool(s_ip=node_ip1, node_pool_ids=node_pool_id,
                                                                     name='storage_pool1')
    az_id = env_manage_lun_manage.osan.create_access_zone(s_ip=node_ip1, node_id=node_ids, name='accesszone1')
    env_manage_lun_manage.osan.enable_san(node_ip1, az_id)
    hg_id = env_manage_lun_manage.osan.create_host_group(node_ip1, "hg_name_1")
    [env_manage_lun_manage.osan.add_host(node_ip1, "h_name{}".format(i), hg_id) for i in range(10)]

    [env_manage_lun_manage.osan.update_host(node_ip1, h_id, name="hg_name_update{}".format(h_id))
     for h_id in random.sample(env_manage_lun_manage.osan.get_hosts(node_ip1), 5)]

    [env_manage_lun_manage.osan.add_initiator(node_ip1, h_id, cp("add_initiator", "iqn")+"{}".format(h_id),
                                              alias=cp("add_initiator", "alias")+"{}".format(h_id)) for h_id in
     env_manage_lun_manage.osan.get_hosts(node_ip1)]

    [env_manage_lun_manage.osan.update_initiator(s_ip=node_ip1, ini_id=ini_id,
                                                 alias=cp("add_initiator", "alias").format(ini_id), auth_type="CHAP",
                                                 user="wx{}".format(ini_id), passwd="asdf12{}".format(ini_id))
     for ini_id in random.sample(env_manage_lun_manage.osan.get_initiators(node_ip1), 5)]

    [env_manage_lun_manage.osan.remove_initiator(s_ip=node_ip1, ini_id=ini_id) for ini_id in
     random.sample(env_manage_lun_manage.osan.get_initiators(node_ip1), 6)]

    [env_manage_lun_manage.osan.update_host(node_ip1, h_id, "hg_update_{}".format(h_id)) for h_id in
     env_manage_lun_manage.osan.get_hosts(node_ip1)]

    env_manage_lun_manage.clean_initiator()
    env_manage_lun_manage.clean_host()
    env_manage_lun_manage.clean_hostgroup()


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    # env_manage_lun_manage.clean(target="storage_pool")
    env_manage_lun_manage.init_env(target="create_node_pool", reboot_node=1)
    case()  # 用例步骤
    env_manage_lun_manage.init_env(reboot_node=1)  # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()

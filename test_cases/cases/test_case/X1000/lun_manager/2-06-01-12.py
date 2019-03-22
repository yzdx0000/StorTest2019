# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:访问区业务子网和网卡数规格

步骤:
1）配置节点池设置副本数为3
2）创建存储池，使用全部磁盘
3）创建一个访问区
4）创建4个业务子网（配置4个网卡），并配置对应的VIP地址池

检查项:
4）业务子网创建成功，IP地址池创建成功
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
log.info("此case至少需要4个用于配置subnet的网卡!!!!")
node_ip1 = env_manage_lun_manage.node_ip1
node_ip2 = env_manage_lun_manage.deploy_ips[1]
node_ip3 = env_manage_lun_manage.deploy_ips[2]
client_ip1 = env_manage_lun_manage.client_ips[0]
client_ip2 = env_manage_lun_manage.client_ips[1]
esxi_ip = env_manage_lun_manage.Esxi_ips

deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP


osan = Lun_managerTest.oSan()



def case():
    node_pool_id = \
    env_manage_lun_manage.osan.get_option(s_ip=node_ip1, command="get_node_pools", indexname="node_pools",
                                          argv="id")[-1]
    osan.startup(node_ip1)
    env_manage_lun_manage.osan.create_storage_pool(s_ip=node_ip1, node_pool_ids=node_pool_id, name='storage_pool1', )
    node_ids_list = env_manage_lun_manage.osan.get_nodes(node_ip1)
    node_ids = ",".join('%s' % id for id in node_ids_list)
    az_id = osan.create_access_zone(s_ip=deploy_ips[0], node_id=node_ids, name='accesszonetest')
    sub_id1 = osan.create_subnet(s_ip=node_ip1, access_zone_id=az_id, name='subnet1',
                                sv_ip=cp("create_subnet", "sv_ip"),
                                mask=cp("create_subnet", "mask"),
                                vv_ip=cp("create_subnet", "vv_ip"),
                                gate_way=cp("create_subnet", "gate_way"),
                                network_interface=cp("create_subnet", "network_interface"))
    svip = osan.get_option_single(s_ip=node_ip1,
                                  command='get_subnets', ids="ids",
                                  indexname="subnets",
                                  argv2="svip",
                                  argv1=sub_id1)
    sub_id2 = osan.create_subnet(s_ip=node_ip1, access_zone_id=az_id, name='subnet2',
                                sv_ip=cp("create_subnet", "sv_ip2"),
                                mask=cp("create_subnet", "mask"),
                                vv_ip=cp("create_subnet", "vv_ip2"),
                                gate_way=cp("create_subnet", "gate_way"),
                                network_interface=cp("create_subnet", "network_interface"))
    svip2 = osan.get_option_single(s_ip=node_ip1,
                                  command='get_subnets', ids="ids",
                                  indexname="subnets",
                                  argv2="svip",
                                  argv1=sub_id2)
    sub_id3 = osan.create_subnet(s_ip=node_ip3, access_zone_id=az_id, name='subnet3',
                                sv_ip=cp("create_subnet", "sv_ip3"),
                                mask=cp("create_subnet", "mask"),
                                vv_ip=cp("create_subnet", "vv_ip3"),
                                gate_way=cp("create_subnet", "gate_way"),
                                network_interface=cp("create_subnet", "network_interface"))
    svip3 = osan.get_option_single(s_ip=node_ip1,
                                  command='get_subnets', ids="ids",
                                  indexname="subnets",
                                  argv2="svip",
                                  argv1=sub_id3)

    sub_id4 = osan.create_subnet(s_ip=node_ip3, access_zone_id=az_id, name='subnet4',
                                 sv_ip=cp("create_subnet", "sv_ip4"),
                                 mask=cp("create_subnet", "mask"),
                                 vv_ip=cp("create_subnet", "vv_ip4"),
                                 gate_way=cp("create_subnet", "gate_way"),
                                 network_interface=cp("create_subnet", "network_interface"))
    svip4 = osan.get_option_single(s_ip=node_ip1,
                                  command='get_subnets', ids="ids",
                                  indexname="subnets",
                                  argv2="svip",
                                  argv1=sub_id4)
    new_vip1 = osan.check_ping_ip(svip,1)
    osan.add_vip_address_pool(s_ip=node_ip1, subnet_id=sub_id1,
                              domain_name="{}1".format(cp("add_vip_address_pool", "domain_name")),
                              vip=new_vip1)
    new_vip2 = osan.check_ping_ip(svip2, 1)
    osan.add_vip_address_pool(s_ip=node_ip1, subnet_id=sub_id2,
                              domain_name="{}2".format(cp("add_vip_address_pool", "domain_name")),
                              vip=new_vip2)
    new_vip3 = osan.check_ping_ip(svip3, 1)
    osan.add_vip_address_pool(s_ip=node_ip1, subnet_id=sub_id3,
                              domain_name="{}3".format(cp("add_vip_address_pool", "domain_name")),
                              vip=new_vip3)
    new_vip4 = osan.check_ping_ip(svip4, 1)
    osan.add_vip_address_pool(s_ip=node_ip1, subnet_id=sub_id4,
                              domain_name="{}4".format(cp("add_vip_address_pool", "domain_name")),
                              vip=new_vip4)


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.init_env(target="create_node_pool")
    case()  # 用例步骤
    env_manage_lun_manage.init_env(reboot_node=1)  # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()
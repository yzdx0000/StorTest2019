# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:带业务子网删除

步骤:
1）配置节点池设置副本数为3
2）创建存储池，使用全部磁盘
3）创建访问区
4）在访问区中配置业务子网，和VIP后，删除访问区

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
    az_id = osan.create_access_zone(s_ip=deploy_ips[0], node_id=node_ids, name='accesszonetest')
    env_manage_lun_manage.osan.enable_san(node_ip1, az_id)
    sub_id = osan.create_subnet(s_ip=node_ip1, access_zone_id=az_id, name='subnet1',
                                sv_ip=cp("create_subnet", "sv_ip"),
                                mask=cp("create_subnet", "mask"),
                                vv_ip=cp("create_subnet", "vv_ip"),
                                gate_way=cp("create_subnet", "gate_way"),
                                network_interface=cp("create_subnet", "network_interface"))
    svip = osan.get_option_single(s_ip=deploy_ips[0],
                                  command='get_subnets', ids="ids",
                                  indexname="subnets",
                                  argv2="svip",
                                  argv1=sub_id)
    new_ip = env_manage_lun_manage.osan.check_ping_ip(svip, len(node_ids_list) * 4)
    osan.add_vip_address_pool(s_ip=node_ip1, subnet_id=sub_id,
                              domain_name=cp("add_vip_address_pool", "domain_name"),
                              vip=new_ip)


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean(target="access_zone")
    case()  # 用例步骤
    env_manage_lun_manage.init_env(reboot_node=1)  # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()

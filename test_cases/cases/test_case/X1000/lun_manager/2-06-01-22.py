# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:无业务时iSCSI服务停止

步骤:
1、配置节点池设置副本数为3
2、创建存储池，使用全部磁盘
3、创建一个访问区
4、启动iSCSI
5、配置子网，VIP地址池
6、禁止iSCSI
7、检查VIP的分配情况

检查项:
4、iSCSI启动成功
6、iSCSI停止成功
7、VIP的分配与iSCSI服务停止前一致
"""
# testlink case: 1000-34166
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
import env_manage_repair_test
import ReliableTest

"""初始化日志和全局变量"""
conf_file = get_config.CONFIG_FILE  # 配置文件路径
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件

log.info("---------------全局初始化操作-----------------")
node_ip1 = env_manage_lun_manage.node_ip1
node_ip2 = env_manage_lun_manage.deploy_ips[1]
node_ip3 = env_manage_lun_manage.deploy_ips[2]
client_ip1 = env_manage_lun_manage.client_ips[0]
client_ip2 = env_manage_lun_manage.client_ips[1]
esxi_ip = env_manage_lun_manage.Esxi_ips

deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP

osan = Lun_managerTest.oSan()


def step1(arg=1):
    global az_id
    storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
    node_ids_list = env_manage_lun_manage.osan.get_nodes(node_ip1)
    node_ids = ",".join('%s' % id for id in node_ids_list)
    az_id = osan.create_access_zone(s_ip=deploy_ips[0],
                                    node_id="{},{},{}".format(node_ids_list[0], node_ids_list[1], node_ids_list[2]),
                                    name='accesszonetest')

    osan.enable_san(s_ip=node_ip1, access_zone_id=az_id)
    sub_id1 = osan.create_subnet(s_ip=node_ip1, access_zone_id=az_id, name='subnet1',
                                 sv_ip=cp("create_subnet", "sv_ip"),
                                 mask=cp("create_subnet", "mask"),
                                 vv_ip=cp("create_subnet", "vv_ip"),
                                 gate_way=cp("create_subnet", "gate_way"),
                                 network_interface=cp("create_subnet", "network_interface"))
    osan.add_vip_address_pool(s_ip=node_ip1, subnet_id=sub_id1,
                              domain_name=cp("add_vip_address_pool", "domain_name"),
                              vip=cp("add_vip_address_pool", "vips"))
    osan.disable_san(s_ip=node_ip1, access_zone_id=az_id)

    #检查VIP的分配情况(ping 一下vip，预期能ping通)
    vip = env_manage_lun_manage.co2_osan.get_vip_address_pools(n_id="1", s_ip=deploy_ips[0])  # 获取vip,二维数组
    vip = env_manage_lun_manage.co2_osan.analysis_vip(vip[0])
    for ip in vip:
        if ReliableTest.check_ping(ip) is False:
            exit(1)


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean(target="access_zone")
    step1()
    env_manage_lun_manage.init_env(reboot_node=1)  # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()

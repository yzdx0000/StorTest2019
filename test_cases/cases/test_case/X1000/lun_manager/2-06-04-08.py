# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:修改SVIP和名称

步骤:
1、创建节点池
2、创建存储池，使用全部磁盘
3、创建访问区
4、创建SVIP，填写zone id，svip name，IP地址，掩码，网关，网卡名称，提交后可成功创建
5、修改该业务子网的SVIP和名称

检查项:
1、节点池创建成功
2、存储池创建成功
3、访问区创建成功
4、成功创建SVIP
5、成功修改SVIP和子网名称
"""
# testlink case: 1000-34176
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


def case():
    global node_ids_list
    global az_id
    node_ids_list = env_manage_lun_manage.osan.get_nodes(node_ip1)
    node_ids = ",".join('%s' % id for id in node_ids_list)
    node_pool_id = \
        env_manage_lun_manage.osan.get_option(s_ip=node_ip1, command="get_node_pools", indexname="node_pools",
                                              argv="id")[-1]
    osan.startup(node_ip1)
    storage_pool_id = env_manage_lun_manage.osan.create_storage_pool(s_ip=node_ip1, node_pool_ids=node_pool_id,
                                                                     name='storage_pool1', )
    az_id = osan.create_access_zone(s_ip=deploy_ips[0],
                                    node_id="{},{},{}".format(node_ids_list[0], node_ids_list[1], node_ids_list[2]),
                                    name='accesszonetest')
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
    env_manage_lun_manage.osan.delete_subnet(node_ip1,sub_id1)




def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean(target="storage_pool")
    # env_manage_lun_manage.init_env(target="create_node_pool",reboot_node=1)
    case()  # 用例步骤
    decorator_func.pass_flag()
    env_manage_lun_manage.init_env(reboot_node=1) # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试


if __name__ == '__main__':
    main()
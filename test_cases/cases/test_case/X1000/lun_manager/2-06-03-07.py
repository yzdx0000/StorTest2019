# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:删除含有lun的存储池

步骤:
1、配置节点池设置副本数为3
2、创建存储池，使用全部磁盘
3、创建访问区和对于的VIP地址池
4、创建一条LUN
5、删除存储池

检查项:
5、存储池删除失败
"""
# testlink case: 1000-34061
import os, sys
import random
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
    storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
    az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
    lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, lun_type="THIN",
                                                   lun_name='LUN1',
                                                   stor_pool_id=storage_pool_id,
                                                   acc_zone_id=az_id)
    msg = env_manage_lun_manage.osan.delete_storage_pool(s_ip=node_ip1, id=storage_pool_id, needjudge=1)
    env_manage_lun_manage.assert_ins.assertNotequal(msg, '', 'judge failed')


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.init_env(target="create_vip_address",reboot_node=1)
    case()  # 用例步骤
    decorator_func.pass_flag()
    env_manage_lun_manage.init_env(reboot_node=1) # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试


if __name__ == '__main__':
    main()

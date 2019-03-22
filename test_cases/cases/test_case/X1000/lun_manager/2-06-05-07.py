# -*- coding:utf-8 _*-
"""
@author: wangxiang
@file: 2-06-05-01.py
@time: 2018/07/06
"""
"""
测试内容:访问区创建

步骤:
1）配置节点池设置副本数为3
2）创建存储池，使用全部磁盘
3）通过管理端cli命令创建访问区

检查项:
1）节点池创建成功
2）存储池创建成功
3）访问区创建成功
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

    storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=deploy_ips[0], type="BLOCK")
    az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=deploy_ips[0])[0]

    env_manage_lun_manage.osan.enable_san(deploy_ips[0], az_id)
    hg_id = env_manage_lun_manage.osan.create_host_group(s_ip=deploy_ips[0], hg_name='myhostgroup1')

    h_id = env_manage_lun_manage.osan.add_host(s_ip=deploy_ips[0], h_name='host1', hg_id=hg_id)
    env_manage_lun_manage.osan.add_initiator(s_ip=deploy_ips[0], h_id=h_id, iqn=cp("add_initiator", "iqn"),
                                             alias=cp("add_initiator", "alias"))
    lun_id = env_manage_lun_manage.osan.create_lun(s_ip=deploy_ips[0], lun_type="THIN",
                                                   lun_name='LUNtest',
                                                   stor_pool_id=storage_pool_id, acc_zone_id=az_id)
    log.info(lun_id)

    decorator_func.judge_target(
        env_manage_lun_manage.osan.get_option_single(s_ip=deploy_ips[0], command="get_luns", indexname="luns"
                                                     , argv2="name", ids="ids", argv1=lun_id),
        'LUNtest')
    lun_map_id = env_manage_lun_manage.osan.map_lun(s_ip=deploy_ips[0], lun_ids=lun_id, hg_id=hg_id)
    decorator_func.judge_target(
        env_manage_lun_manage.osan.get_option_single(s_ip=deploy_ips[0], command='get_lun_maps', indexname='lun_maps',
                                                     argv2="lun_map_state",
                                                     ids="ids", argv1=lun_map_id),
        'LUNMAP_READY')

    vip_pool_ids = osan.get_option(s_ip=node_ip, command="get_vip_address_pools", indexname="ip_address_pools",
                                   argv="id")
    msg=osan.delete_vip_address_pool(s_ip=node_ip, id=vip_pool_ids[0],need_judge=1)
    env_manage_lun_manage.assert_ins.assertNotequal(msg, '', 'judge failed')


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean()
    case()  # 用例步骤
    env_manage_lun_manage.init_env(reboot_node=1) # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()
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
from multiprocessing import Pool
# testlink case: 1000-34097

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

"""读取存储池的容量"""
storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
storage_pool_size = env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1,
                                                                 command='get_storage_pools', ids="ids",
                                                                 indexname="storage_pools",
                                                                 argv2="total_bytes",
                                                                 argv1=storage_pool_id)

iqn_list = ['iqn.1994-05189.com.sugon', 'iqn.1994-05190.com.sugon', 'iqn.1994-05191.com.sugon',
            'iqn.1994-05192.com.sugon', 'iqn.1994-05193.com.sugon', 'iqn.1994-05194.com.sugon',
            'iqn.1994-05195.com.sugon', 'iqn.1994-05196.com.sugon', 'iqn.1994-05197.com.sugon',
            'iqn.1994-05198.com.sugon', ]


def lun_map1(arg=1):
    hg_id = osan.create_host_group(s_ip=deploy_ips[0], hg_name='myhostgroup1')

    h_id = osan.add_host(s_ip=deploy_ips[0], h_name='host1', hg_id=hg_id)
    osan.add_initiator(s_ip=deploy_ips[0], h_id=h_id, iqn=iqn_list[0],
                       alias="alias1")

    for i in range(10):
        lun_id = osan.create_lun(s_ip=deploy_ips[0], total_bytes='1024000', lun_type="THIN",
                                 lun_name='LUN{}'.format(i),
                                 stor_pool_id=storage_pool_id, acc_zone_id=az_id)

        lun_map_id = osan.map_lun(s_ip=deploy_ips[0], lun_ids=lun_id, hg_id=hg_id)
        decorator_func.judge_target(
            osan.get_option_single(s_ip=deploy_ips[0], command='get_lun_maps', indexname='lun_maps',
                                   argv2="lun_map_state",
                                   ids="ids", argv1=lun_map_id),
            'LUNMAP_READY')


def lun_map2(arg=1):
    hg_id = osan.create_host_group(s_ip=deploy_ips[0], hg_name='myhostgroup2')

    h_id = osan.add_host(s_ip=deploy_ips[0], h_name='host2', hg_id=hg_id)
    osan.add_initiator(s_ip=deploy_ips[0], h_id=h_id, iqn=iqn_list[1],
                       alias="alias2")

    for i in range(10, 20):
        lun_id = osan.create_lun(s_ip=deploy_ips[0], total_bytes='1024000', lun_type="THIN",
                                 lun_name='LUN{}'.format(i),
                                 stor_pool_id=storage_pool_id, acc_zone_id=az_id)

        lun_map_id = osan.map_lun(s_ip=deploy_ips[0], lun_ids=lun_id, hg_id=hg_id)
        decorator_func.judge_target(
            osan.get_option_single(s_ip=deploy_ips[0], command='get_lun_maps', indexname='lun_maps',
                                   argv2="lun_map_state",
                                   ids="ids", argv1=lun_map_id),
            'LUNMAP_READY')


def lun_map3(arg=1):
    hg_id = osan.create_host_group(s_ip=deploy_ips[0], hg_name='myhostgroup3')

    h_id = osan.add_host(s_ip=deploy_ips[0], h_name='host3', hg_id=hg_id)
    osan.add_initiator(s_ip=deploy_ips[0], h_id=h_id, iqn=iqn_list[2],
                       alias="alias3")

    for i in range(20, 30):
        lun_id = osan.create_lun(s_ip=deploy_ips[0], total_bytes='1024000', lun_type="THIN",
                                 lun_name='LUN{}'.format(i),
                                 stor_pool_id=storage_pool_id, acc_zone_id=az_id)

        lun_map_id = osan.map_lun(s_ip=deploy_ips[0], lun_ids=lun_id, hg_id=hg_id)
        decorator_func.judge_target(
            osan.get_option_single(s_ip=deploy_ips[0], command='get_lun_maps', indexname='lun_maps',
                                   argv2="lun_map_state",
                                   ids="ids", argv1=lun_map_id),
            'LUNMAP_READY')


def lun_map4(arg=1):
    hg_id = osan.create_host_group(s_ip=deploy_ips[0], hg_name='myhostgroup4')

    h_id = osan.add_host(s_ip=deploy_ips[0], h_name='host4', hg_id=hg_id)
    osan.add_initiator(s_ip=deploy_ips[0], h_id=h_id, iqn=iqn_list[3],
                       alias="alias4")

    for i in range(30, 40):
        lun_id = osan.create_lun(s_ip=deploy_ips[0], total_bytes='1024000', lun_type="THIN",
                                 lun_name='LUN{}'.format(i),
                                 stor_pool_id=storage_pool_id, acc_zone_id=az_id)

        lun_map_id = osan.map_lun(s_ip=deploy_ips[0], lun_ids=lun_id, hg_id=hg_id)
        decorator_func.judge_target(
            osan.get_option_single(s_ip=deploy_ips[0], command='get_lun_maps', indexname='lun_maps',
                                   argv2="lun_map_state",
                                   ids="ids", argv1=lun_map_id),
            'LUNMAP_READY')


def lun_map5(arg=1):
    hg_id = osan.create_host_group(s_ip=deploy_ips[0], hg_name='myhostgroup5')

    h_id = osan.add_host(s_ip=deploy_ips[0], h_name='host5', hg_id=hg_id)
    osan.add_initiator(s_ip=deploy_ips[0], h_id=h_id, iqn=iqn_list[4],
                       alias="alias5")

    for i in range(40, 50):
        lun_id = osan.create_lun(s_ip=deploy_ips[0], total_bytes='1024000', lun_type="THIN",
                                 lun_name='LUN{}'.format(i),
                                 stor_pool_id=storage_pool_id, acc_zone_id=az_id)

        lun_map_id = osan.map_lun(s_ip=deploy_ips[0], lun_ids=lun_id, hg_id=hg_id)
        decorator_func.judge_target(
            osan.get_option_single(s_ip=deploy_ips[0], command='get_lun_maps', indexname='lun_maps',
                                   argv2="lun_map_state",
                                   ids="ids", argv1=lun_map_id),
            'LUNMAP_READY')


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean()
    decorator_func.multi_threads(lun_map1, lun_map2, lun_map3, lun_map4, lun_map5)
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()

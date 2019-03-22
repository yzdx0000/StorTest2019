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


def lun_map1(arg=1):
    hg_id = osan.create_host_group(s_ip=deploy_ips[0], hg_name='myhostgroup1')

    h_id = osan.add_host(s_ip=deploy_ips[0], h_name='host1', hg_id=hg_id)
    osan.add_initiator(s_ip=deploy_ips[0], h_id=h_id, iqn=cp("add_initiator", "iqn"),
                       alias=cp("add_initiator", "alias"))

    for i in range(15):
        lun_id = osan.create_lun(s_ip=deploy_ips[0], total_bytes='1024000', lun_type="THIN",
                                 lun_name='LUN{}'.format(i),
                                 stor_pool_id=storage_pool_id, acc_zone_id=az_id)

    node_ids_list = env_manage_lun_manage.osan.get_nodes(node_ip1)
    node_ids = ",".join('%s' % id for id in node_ids_list)

    exe_id = env_manage_lun_manage.Reliable_osan.get_node_id_by_ip(node_ip1)

    targets = env_manage_lun_manage.osan.gen_dict_mul(s_ip=node_ip1, command="get_targets", arg1="nodeId",
                                                      arg2="id",
                                                      arg3="targets", target=exe_id)

    node_id1 = env_manage_lun_manage.Reliable_osan.get_node_id_by_ip(node_ip1)
    luns1 = env_manage_lun_manage.osan.get_luns_by_node_id(node_id=node_id1)

    node_id3 = env_manage_lun_manage.Reliable_osan.get_node_id_by_ip(deploy_ips[2])
    luns3 = env_manage_lun_manage.osan.get_luns_by_node_id(node_id=node_id3)
    for lun in luns1:
        env_manage_lun_manage.osan.lun_map_by_target(node_ip1, lun_ids=lun, target_id=targets[0], hp_id=hg_id)
    for lun in luns3:
        env_manage_lun_manage.osan.map_lun(s_ip=node_ip1, lun_ids=lun, hg_id=hg_id)


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean()
    lun_map1()
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()
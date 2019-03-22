# -*- coding:utf-8 _*-
"""
@author: wangxiang
@file: 2-06-02-11.py
"""
"""
测试内容:批量创建精简卷

步骤:
1）在访问区配置中，每个节点取1块磁盘创建副本模式存储池，共创建三个存储池pool1，pool2，pool3；
2）选择批量创建精简卷，选择存储池pool1，逻辑卷名称为LUN，设置个数为100；
3）提交后开始批量创建。

检查项:
1）存储池创建成功
4）逻辑卷创建成功，逻辑卷列表中可查看到该逻辑卷
"""
# testlink case: 1000-33493
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

    node_ids_list = env_manage_lun_manage.osan.get_nodes(deploy_ips[0])
    node_ids = ",".join('%s' % id for id in node_ids_list)

    fault_node_id = env_manage_lun_manage.break_down.get_node_id_by_ip(n_ip=node_ip1)
    """获取指定节点数据盘和共享盘"""
    share_disk, data_disk = env_manage_lun_manage.Reliable_osan.get_share_monopoly_disk_ids(s_ip=node_ip1,
                                                                                             node_id=fault_node_id)
    disk_ids = []
    for data_disk in data_disk:
        disk_phy_id = env_manage_lun_manage.Reliable_osan.get_physicalid_by_name(node_ip1, data_disk)
        disk_ids.append(disk_phy_id)
    disk_phy_id = disk_ids[0]  # 磁盘物理id1

    env_manage_lun_manage.Reliable_osan.remove_disk(node_ip1, disk_phy_id, "DATA")
    msg = osan.create_access_zone(s_ip=deploy_ips[0], node_id=node_ids, name='accesszonetest')


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.init_env(target="create_storage_pool")
    case()  # 用例步骤
    env_manage_lun_manage.init_env(reboot_node=1)  # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()
# -*- coding:utf-8 _*-
# Author:wangxiang
# Date  :2018-10-13
"""
测试内容:精简卷容量显示（管理端）

步骤:
1）在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1；
2）创建精简卷属性默认，选择pool1存储池，创建精简卷LUN1；
3）创建完成后在存储管理端检查容量显示，已用0GB，最大容量为设置容量

检查项:
1）存储池创建成功
2）逻辑卷创建成功
5）显示正确
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

osan = Lun_managerTest.oSan()

"""读取存储池的容量"""
storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
storage_pool_size = env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1,
                                                                 command='get_storage_pools', ids="ids",
                                                                 indexname="storage_pools",
                                                                 argv2="total_bytes",
                                                                 argv1=storage_pool_id)


def case():
    log.info("创建逻辑卷属性默认，选择pool1存储池，创建逻辑卷LUN1")
    lun_id1 = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes='102400000', lun_type="THIN",
                                                    lun_name='LUN1',
                                                    stor_pool_id=storage_pool_id, acc_zone_id=az_id)

    env_manage_lun_manage.assert_ins.assertEqual(
        osan.get_option_single(s_ip=deploy_ips[0], command="get_luns", indexname="luns"
                               , argv2="total_bytes", ids="ids", argv1=lun_id1),
        102400000)


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean()  # 环境清理
    case()  # 用例步骤
    env_manage_lun_manage.clean()  # 环境清理


if __name__ == '__main__':
    main()

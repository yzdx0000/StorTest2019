# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:精简卷容量超过物理容量创建

步骤:
1）在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1；
2）创建精简逻辑卷属性默认，选择pool1存储池，创建精简逻辑卷LUN1，设置容量比物理容量大；
3）可正常创建

检查项:
1）存储池创建成功
2）精简卷创建成功，逻辑卷列表中可查看到该逻辑卷
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
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件

log.info("---------------全局初始化操作-----------------")
node_ip1 = env_manage_lun_manage.deploy_ips[0]
node_ip2 = env_manage_lun_manage.deploy_ips[1]
client_ip1 = env_manage_lun_manage.client_ips[0]
esxi_ip = env_manage_lun_manage.Esxi_ips

osan = Lun_managerTest.oSan()

"""读取存储池的容量"""
storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
storage_pool_size = env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1,
                                                                 command='get_storage_pools', ids="ids",
                                                                 indexname="storage_pools",
                                                                 argv2="total_bytes",
                                                                 argv1=storage_pool_id)
log.info("id为{}的存储池容量为{} byte".format(storage_pool_id, storage_pool_size))


def case():
    lun_id = osan.create_lun(s_ip=node_ip1, total_bytes=1, lun_type="THICK",
                             lun_name='LUN1',
                             stor_pool_id=storage_pool_id, acc_zone_id=az_id)

    decorator_func.judge_target(
        osan.get_option_single(s_ip=node_ip1, command="get_luns", indexname="luns"
                               , argv2="lun_type", ids="ids", argv1=lun_id),
        'LUN_TYPE_THICK')

# @decorator_func.tasklet(int(env_manage.cp('timeout', 'second')), maxretry=int(env_manage.cp('timeout', 'maxretry')))
def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean()
    case()  # 用例步骤
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()
    pass
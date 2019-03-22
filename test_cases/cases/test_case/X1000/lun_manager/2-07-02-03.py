# -*- coding:utf-8 _*-
"""
测试内容:删除多个thin lun预留空间释放

步骤:
1、在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1，容量为50G；并创建和配置对于的访问分区和vip地址池；
2、创建40条精简卷；
3、删除20条精简卷；
4、等删除精简卷的空间释放完成后，创建1条40G大小的逻辑卷

检查项:
1、步骤2，40条精简卷创建成功；
2、步骤3，20条精简卷删除成功，预留空间释放10G；
3、步骤4，逻辑卷创建成功；
"""

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
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件

log.info("---------------全局初始化操作-----------------")
node_ip1 = env_manage_lun_manage.deploy_ips[0]
node_ip2 = env_manage_lun_manage.deploy_ips[1]
client_ip1 = env_manage_lun_manage.client_ips[0]
esxi_ip = env_manage_lun_manage.Esxi_ips

"""读取存储池的容量"""
storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
storage_pool_size = int(env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1,
                                                                     command='get_storage_pools', ids="ids",
                                                                     indexname="storage_pools",
                                                                     argv2="total_bytes",
                                                                     argv1=storage_pool_id) / int(
    cp("reserve", "replica_num")) / float(cp("reserve", "multiple")))
log.info("id为{}的存储池容量为{} byte".format(storage_pool_id, storage_pool_size))
"""根据存储池容量计算和thin  lun预留容量(256M)计算应该创建的lun数量"""
lun_num = 10
thick_lun_size = storage_pool_size
log.info("要创建的lun个数 为{}".format(lun_num))


def create_lun():
    for i in range(lun_num):
        lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=storage_pool_size, lun_type="THIN",
                                                       lun_name='LUN_{}'.format(i),
                                                       stor_pool_id=storage_pool_id, acc_zone_id=az_id)
        decorator_func.judge_target(
            env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1, command="get_luns", indexname="luns"
                                                         , argv2="name", ids="ids", argv1=lun_id),
            'LUN_{}'.format(i))

    lun_ids = env_manage_lun_manage.osan.get_lun(s_ip=node_ip1)

    log.info(lun_ids)
    env_manage_lun_manage.clean_lun()

    env_manage_lun_manage.osan.reserve_wait(storage_pool_id=storage_pool_id)

    env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=thick_lun_size, lun_type="THICK",
                                          lun_name='LUN_THICK',
                                          stor_pool_id=storage_pool_id, acc_zone_id=az_id)


def case():
    log.info("在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1，容量为50G；并创建和配置对于的访问分区和vip地址池;创建200条精简卷")
    log.info("2、创建40条精简卷；删除20条精简卷；等删除精简卷的空间释放完成后，创建1条40G大小的逻辑卷")
    create_lun()


def main():
    env_manage_lun_manage.revert_env()

    error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.osan.xstor_pre_config(node_ip1, 0, 1)

    env_manage_lun_manage.clean()

    case()  # 用例步骤

    env_manage_lun_manage.clean()
    env_manage_lun_manage.osan.xstor_pre_config(node_ip1, 1, 0)
    decorator_func.pass_flag()


if __name__ == '__main__':
    common.case_main(main)  # 主函数执行入口

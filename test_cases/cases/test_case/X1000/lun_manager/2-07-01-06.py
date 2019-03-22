# -*- coding:utf-8 _*-
"""
测试内容:并发创建大量thick lun

步骤:
1、在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1 ；并创建和配置对于的访问分区和vip地址池；
2、并发创建100条逻辑卷，卷的容量总和不超过存储池大小

检查项:
1、步骤2，逻辑卷创建成功
"""

import os
import sys
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
node_ip1 = env_manage_lun_manage.node_ip1
node_ip2 = env_manage_lun_manage.deploy_ips[1]
client_ip1 = env_manage_lun_manage.client_ips[0]
esxi_ip = env_manage_lun_manage.Esxi_ips

"""读取存储池的容量"""
storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
storage_pool_size = env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1,
                                                                 command='get_storage_pools', ids="ids",
                                                                 indexname="storage_pools",
                                                                 argv2="total_bytes",
                                                                 argv1=storage_pool_id) / int(
    cp("reserve", "replica_num"))
log.info("id为{}的存储池容量为{} byte".format(storage_pool_id, storage_pool_size))
avg_lun_size = int(storage_pool_size / 100/ float(cp("reserve", "multiple")))
log.info("lun size为{}".format(avg_lun_size))


def create_lun_thick(arg=1):
    i2 = random.randint(100000001, 1000000000)
    lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=avg_lun_size, lun_type="THICK",
                                                   lun_name='LUN{}'.format(i2),
                                                   stor_pool_id=storage_pool_id, acc_zone_id=az_id)


def case():
    log.info("在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1 50G；并创建和配置对于的访问分区和vip地址池；")
    log.info("并发创建100条逻辑卷，卷的容量总和不超过存储池大小")
    lun_num1 = env_manage_lun_manage.osan.get_lun(s_ip=node_ip1)  # 执行前查询lun数量
    decorator_func.thread_para(100, create_lun_thick)
    lun_total = len(lun_num1) + 100  # 执行完成后lun的总数
    while True:
        lun_num2 = env_manage_lun_manage.osan.get_lun(s_ip=node_ip1)  # 执行开始后查询lun数量
        log.info("Wait execute finish ...")
        if len(lun_num2) == lun_total:
            break


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

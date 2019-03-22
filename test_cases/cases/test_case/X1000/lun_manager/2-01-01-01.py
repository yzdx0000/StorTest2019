# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:指定池创建逻辑卷

步骤:
1）配置访问区，创建存储池pool1，pool2，pool3
2）创建逻辑卷属性默认，选择pool2存储池，创建逻辑卷LUN1；
3）提交后创建成功

检查项:
1）存储池创建成功
2）逻辑卷创建成功，逻辑卷列表中可查看到该逻辑卷
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
node_ip1 = env_manage_lun_manage.node_ip1
node_ip2 = env_manage_lun_manage.deploy_ips[1]
client_ip1 = env_manage_lun_manage.client_ips[0]
client_ip2 = env_manage_lun_manage.client_ips[1]
esxi_ip = env_manage_lun_manage.Esxi_ips

"""读取存储池的容量"""
storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
storage_pool_size = env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1,
                                                                 command='get_storage_pools', ids="ids",
                                                                 indexname="storage_pools",
                                                                 argv2="total_bytes",
                                                                 argv1=storage_pool_id)


def case():
    lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes='102400000', lun_type="THICK",
                                                   lun_name='LUN1',
                                                   stor_pool_id=storage_pool_id, acc_zone_id=az_id)
    log.info(lun_id)
    decorator_func.judge_target(
        env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1, command="get_luns", indexname="luns"
                                                     , argv2="name", ids="ids", argv1=lun_id),
        'LUN1')


# @decorator_func.tasklet(int(cp('timeout', 'second')), maxretry=int(cp('timeout', 'maxretry')))
def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    # env_manage_lun_manage.rel_check_before_run(filename=file_name)  # 环境检测和准备
    env_manage_lun_manage.clean()
    case()  # 用例步骤
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()

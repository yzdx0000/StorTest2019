# -*- coding:utf-8 _*-
"""
测试内容:多存储池创建thin lun和thick lun

步骤:
1、在访问区配置中，每个节点取1块磁盘创建副本模式2个存储池，创建存储池pool1 50G，创建存储池pool2 50G ；并创建和配置对于的访问分区和vip地址池；
2、每个存储池并发创建20条1G大小逻辑卷和100条精简卷

检查项:
1、步骤2，逻辑卷和精简卷均创建成功
"""

import os, sys
import random
import threading
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

FLAG = True  # True为使用THICK lun占一部分及空间再写;Flase为不创建THICK lun占空间
thin_lun_total = 5368709120  # 要写的thin lun大小设置为5G

env_manage_lun_manage.init_env(target="enable_san", is_display_raw_capacity=1, osan_space_check=0, storage_pool_num=3)

"""读取存储池的容量"""
storage_pool_id_total = env_manage_lun_manage.osan.get_storage_id(node_ip1)
storage_pool_id_share = []
storage_pool_id_share.append(env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="SHARED"))
storage_pool_id_data = list(set(storage_pool_id_total) ^ set(storage_pool_id_share))
storage_pool_id_1 = storage_pool_id_data[-1]
storage_pool_id_2 = storage_pool_id_data[-2]
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
storage_pool_size1 = int(env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1,
                                                                      command='get_storage_pools', ids="ids",
                                                                      indexname="storage_pools",
                                                                      argv2="total_bytes",
                                                                      argv1=storage_pool_id_1) / int(
    cp("reserve", "replica_num")) / float(cp("reserve", "multiple")))
storage_pool_size2 = int(env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1,
                                                                      command='get_storage_pools', ids="ids",
                                                                      indexname="storage_pools",
                                                                      argv2="total_bytes",
                                                                      argv1=storage_pool_id_2) / int(
    cp("reserve", "replica_num")) / float(cp("reserve", "multiple")))
log.info("id为{}的存储池容量为{} byte".format(storage_pool_id_1, storage_pool_size1))
log.info("id为{}的存储池容量为{} byte".format(storage_pool_id_2, storage_pool_size2))
thick_lun_size1 = int((storage_pool_size1 - thin_lun_total) / 10)
thick_lun_size2 = int((storage_pool_size2 - thin_lun_total) / 10)
thin_lun_num1 = int(thin_lun_total / int(cp("reserve", "thin_lun_reserve")))

thin_lun_num2 = int(thin_lun_total / int(cp("reserve", "thin_lun_reserve")))

log.info("要创建的thin lun个数分别为{},{}".format(thin_lun_num1, thin_lun_num2))

need_size1 = int(10 * thick_lun_size1 + thin_lun_total)
need_size2 = int(10 * thick_lun_size2 + thin_lun_total)
if any([storage_pool_size1 <= need_size1, storage_pool_size2 <= need_size2]):
    log.error("存储池空间不足，建议换大硬盘!")
    exit(-1)


def create_lun_thick1(arg1):
    lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=thick_lun_size1, lun_type="THICK",
                                                   lun_name='LUN{}'.format(arg1),
                                                   stor_pool_id=storage_pool_id_1, acc_zone_id=az_id)


def create_lun_thick2(arg2):
    lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=thick_lun_size2, lun_type="THICK",
                                                   lun_name='LUN{}'.format(arg2),
                                                   stor_pool_id=storage_pool_id_2, acc_zone_id=az_id)


def create_lun_thin1(arg1):
    lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=storage_pool_size1, lun_type="THIN",
                                                   lun_name='LUN{}'.format(arg1),
                                                   stor_pool_id=storage_pool_id_1, acc_zone_id=az_id)


def create_lun_thin2(arg2):
    lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=storage_pool_size2, lun_type="THIN",
                                                   lun_name='LUN{}'.format(arg2),
                                                   stor_pool_id=storage_pool_id_2, acc_zone_id=az_id)


def case():
    log.info("在访问区配置中，每个节点取1块磁盘创建副本模式2个存储池，创建存储池pool1 50G，创建存储池pool2 50G ；并创建和配置对于的访问分区和vip地址池；")
    log.info("每个存储池并发创建20条1G大小逻辑卷和100条精简卷")
    lun_num1 = env_manage_lun_manage.osan.get_lun(s_ip=node_ip1)  # 执行前查询lun数量
    threads = []
    for i in range(thin_lun_num1):
        threads.append(threading.Thread(target=create_lun_thin1, args=(i,)))
    for j in range(thin_lun_num1, thin_lun_num1 + thin_lun_num2):
        threads.append(threading.Thread(target=create_lun_thin2, args=(j,)))
    for a in range(thin_lun_num1 + thin_lun_num2, thin_lun_num1 + thin_lun_num2 + 10):
        threads.append(threading.Thread(target=create_lun_thick1, args=(a,)))
    for b in range(thin_lun_num1 + thin_lun_num2 + 10, thin_lun_num1 + thin_lun_num2 + 20):
        threads.append(threading.Thread(target=create_lun_thick2, args=(b,)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    lun_total = len(lun_num1) + 10 * 2 + thin_lun_num1 + thin_lun_num2  # 执行完成后lun的总数
    log.info(lun_total)
    while True:
        lun_num2 = env_manage_lun_manage.osan.get_lun(s_ip=node_ip1)  # 执行开始后查询lun数量
        log.info("Wait execute finish ...")
        time.sleep(20)
        if len(lun_num2) == lun_total:
            break


def main():
    env_manage_lun_manage.revert_env()

    env_manage_lun_manage.clean()

    case()  # 用例步骤

    decorator_func.pass_flag()


if __name__ == '__main__':
    common.case_main(main)  # 主函数执行入口
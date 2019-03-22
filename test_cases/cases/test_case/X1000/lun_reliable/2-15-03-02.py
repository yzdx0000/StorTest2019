# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-7

'''
测试内容:节点异常情况下创建逻辑卷
测试步骤：
1）配置访问区等设置，创建逻辑卷
2）使用3块盘创建一个存储池，
3）删除创建的逻辑卷，逻辑卷删除过程中拔掉其中两块磁盘
检查项：
成功删除

'''

# testlink case: 1000-33687
import os
import time
import random
import commands
import threading
import utils_path
import log
import common
import ReliableTest
import prepare_x1000
import env_manage
import decorator_func

'''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log


def setup():
    '''获取业务节点IP和非业务节点IP'''
    global node_ip1
    global node_ip2
    global client_ip1
    node_ip1 = env_manage.get_inter_ids()[0]  # 业务节点IP
    node_ip2 = env_manage.get_inter_ids()[1]  # 业务节点IP
    client_ip1 = env_manage.client_ips[0]


def get_disk(node_ip):
    node_id = env_manage.com_lh.get_node_id_by_ip(node_ip)
    share_disk, data_disk = env_manage.com_lh.get_share_monopoly_disk_ids(s_ip=node_ip, node_id=node_id)
    disks = data_disk
    disk_ids = []
    for data_disk in disks:
        disk_id = env_manage.com_lh.get_physicalid_by_name(node_ip, data_disk)
        disk_ids.append(disk_id)
    log.info(disk_ids)
    diskid = random.choice(disk_ids)
    return diskid


def remove_disk(node_ips, disk_ids):
    env_manage.com_lh.remove_disk(node_ip=node_ips, disk_id=disk_ids, disk_usage="DATA")


def insert_disk(node_ips, disk_ids):
    log.info("the disk will insert")
    time.sleep(60)
    env_manage.com_lh.insert_disk(node_ip=node_ips, disk_id=disk_ids, disk_usage="DATA")


def case():
    log.info("step:1.从磁盘池随机选取两个数据盘")
    disk_id1 = get_disk(node_ip1)
    disk_id2 = get_disk(node_ip2)
    log.info("硬盘 %s 将被拔出" % (disk_id1))
    log.info("硬盘 %s 将被拔出" % (disk_id2))
    log.info("step:2.创建逻辑卷过程中将磁盘拔出")
    threads = []
    t1 = threading.Thread(target=env_manage.create_lun, args=(node_ip1, "newLUN1"))
    threads.append(t1)
    t2 = threading.Thread(target=remove_disk, args=(node_ip1, disk_id1))
    threads.append(t2)
    t3 = threading.Thread(target=remove_disk, args=(node_ip2, disk_id2))
    threads.append(t3)
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    log.info("step:3.恢复数据盘")
    insert_disk(node_ip1, disk_id1)
    insert_disk(node_ip2, disk_id2)


def main():
    init_disk = env_manage.clean_test_env()
    setup()
    case()
    log.info("step:4.检查清理环境")
    disks = env_manage.clean_test_env()
    if init_disk == disks:
        log.info("check system all node disk %s success" % disks)
    else:
        log.info("check system all node disk %s have lost" % disks)
        exit(1)
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Date:20181220
Author:Diws
:Description:
1、创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6；
3、在主机1上运行vdbench -f mix-S-Align.conf -jn在主机lun1-lun6上预埋数据容量到到总容量的90%；
4、向节点中加入2块新SSD，设置SSD位共享盘，触发数据均衡；
5、数据均衡过程中，断开逻辑卷连接，批量删除逻辑卷；
"""
import os
import time
import threading
import re
import random
import utils_path
import env_manage_lun_manage
import common2
import get_config
import Lun_managerTest
import error
import breakdown
import ReliableTest
import log
import login
import write_data

lun_osan = Lun_managerTest.oSan()
osan = common2.oSan()
disk = breakdown.disk()
os_rel = breakdown.Os_Reliable()
# 初始化全局变量
conf_file = common2.CONF_FILE
# 获取集群节点管理IP
deploy_ips = get_config.get_env_ip_info(conf_file)
# 获取客户端节点管理IP
client_ips = get_config.get_allclient_ip()
# login
vip = login.login()
# 初始化日志，检查环境是否满足测试要求
file_name = os.path.basename(__file__)
file_name = file_name[:-3]
error.rel_check_before_run(file_name, node_num=3)
fault_ip = random.choice(deploy_ips)
fault_id = disk.get_node_id_by_ip(n_ip=fault_ip)
free_disk_uuids = disk.get_free_disk_info_by_node_id(node_id=fault_id, disk_type='share')
if len(free_disk_uuids) == 0:
    log.info("There in no free disks on %s." % (fault_ip,))
    os._exit(-1)
log.info("节点%s free磁盘：%s." % (str(fault_id), free_disk_uuids))
free_disk_uuid_keys = free_disk_uuids.keys()[:1]
log.info("新添加的磁盘%s." % (free_disk_uuid_keys,))
try:
    os.mkfifo('/tmp/err_fifo', 0777)
except:
    log.info('mkfifo finished.')


def add_disk():
    """
    :Description:添加磁盘
    :return: None
    """
    time.sleep(60)
    log.info("4、向节点中加入2块新SSD，设置SSD位共享盘，触发数据均衡.")
    err_fifo = os.open('/tmp/err_fifo', os.O_RDWR)
    os.write(err_fifo, 'error')
    os.close(err_fifo)
    for d_n in free_disk_uuid_keys:
        res = disk.add_disk(s_ip=fault_ip, uuid=free_disk_uuids[d_n][0], usage="SHARED", node_id=fault_id, err=False)
        if res is False:
            log.error("Add disk to nodepool failed.")
    for d_n in free_disk_uuid_keys:
        res = disk.expand_disk_2_storage_pool_by_uuid(s_ip=fault_ip, node_id=fault_id,
                                                      uuid=free_disk_uuids[d_n][0], storage_pool_id=1)
        if res is False:
            log.error("Add disk to diskpool failed.")


def down_pro():
    """
    :Description:读取命名管道，当开始添加磁盘时候，延迟1.5s，然后拔盘
    :return:
    """
    read_pipe = os.open('/tmp/err_fifo', os.O_RDONLY)
    while True:
        line = os.read(read_pipe, 10)
        if 'err' in line:
            break
    time.sleep(1.5)
    log.info('检查是否开始均衡.')
    check_num = 1
    while disk.check_baljob(check_state='no') is not True:
        time.sleep(5)
        check_num += 1
        if check_num == 60:
            break
    log.info("5、数据均衡过程中，断开逻辑卷连接，批量删除逻辑卷.")
    env_manage_lun_manage.clean('lun')


def main():
    write_data.preare_vdb()
    test_threads = []
    test_threads.append(threading.Thread(target=add_disk))
    test_threads.append(threading.Thread(target=down_pro))
    for test_thread in test_threads:
        test_thread.setDaemon(True)
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()
    os._exit(-110)


if __name__ == '__main__':
    main()

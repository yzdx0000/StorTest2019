#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Date:20181217
Author:Diws
:Description:
1、创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6；
3、在主机1上运行vdbench -f mix-S-Align.conf -jn在主机lun1-lun6上预埋数据容量到到总容量的90%；
4、将新节点加入到节点池中，将磁盘加入到磁盘池中，触发数据均衡；
5、数据均衡过程中，断开逻辑卷连接，删除逻辑卷；
"""
import os
import time
import threading
import re
import random
import utils_path
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
# 获取可扩容节点IP
expand_ips = get_config.get_expand_ip_info()
dst_ip = expand_ips[0]
try:
    os.mkfifo('/tmp/err_fifo', 0777)
except:
    log.info('mkfifo finished.')


def generate_xml():
    """
    :Description:生成配置文件
    :return: 配置文件路径
    """
    if len(expand_ips) == 0:
        log.error("Sorry, I can't find any nodes to expand, please check /home/StorTest/conf/x1000_test_config.xml")
        os._exit(1)
    log.info("生成部署用的配置文件，带共享盘的那种.")
    xml_path = error.modify_deploy_xml(dst_ip=dst_ip, )
    return xml_path


def add_node():
    """
    :Description:添加节点
    :return: None
    """
    c_cap = error.get_cluster_cap()
    log.info("Before your operation, the capicaty os cluster is %d." % (c_cap,))
    s_ip = None
    for s_ip in deploy_ips:
        if True is ReliableTest.check_ping(s_ip):
            break
    xml_file = generate_xml()
    time.sleep(60)
    # 添加节点
    log.info("4、在步骤3中的业务运行过程中，向节点池中加入新节点.")
    output = lun_osan.add_nodes(s_ip=s_ip, conf_file=xml_file, err=False)
    if output is False:
        return
    node_id = output['result'][0]
    log.info(output)
    err_fifo = os.open('/tmp/err_fifo', os.O_RDWR)
    os.write(err_fifo, 'error')
    os.close(err_fifo)
    # 获取所有节点
    nodes = osan.get_nodes()
    node_ids = re.sub('\[|\]| ', '', str(nodes))
    node_pool_info = osan.get_node_pool_id_name()
    log.info("获取节点池id和name：%s." % (node_pool_info,))
    log.info("添加节点到节点池.")
    for key in node_pool_info.keys():
        node_pool_id = key
        node_pool_name = node_pool_info[key]
        for s_ip in deploy_ips:
            if ReliableTest.check_ping(s_ip):
                res = lun_osan.update_node_pool(s_ip, node_ids, node_pool_id, node_pool_name, err=False)
                break
        break
    data_disks = disk.get_disk_ids_by_node_id(disk_type="SAS")[node_id]
    log.info("获取新添加的节点的数据盘: %s." % (data_disks,))
    log.info("将数据盘添加到存储池.")
    for s_ip in deploy_ips:
        if ReliableTest.check_ping(s_ip):
            for data_disk in data_disks:
                disk.expand_disk_2_storage_pool(s_ip=s_ip, stor_id=2, disk_id=data_disk)
            break
    log.info("将新添加的节点加到访问区.")
    for s_ip in deploy_ips:
        if ReliableTest.check_ping(s_ip):
            # 获取访问区id
            access_zone_id = osan.get_access_zone_id(s_ip=deploy_ips[0])
            # 更新访问区
            lun_osan.update_access_zone(s_ip, access_zone_id[0], node_ids)
            break
    c_cap = error.get_cluster_cap()
    log.info("After your operation, the capicaty os cluster is %d." % (c_cap,))


def down_net():
    """
    :Description:移除扩容节点的一块数据盘
    :return: None
    """
    read_pipe = os.open('/tmp/err_fifo', os.O_RDONLY | os.O_TRUNC)
    while True:
        line = os.read(read_pipe, 10)
        if 'err' in line:
            break
    log.info('检查是否开始均衡.')
    check_num = 1
    while disk.check_baljob(check_state='no') is not True:
        time.sleep(5)
        check_num += 1
        if check_num == 60:
            break
    log.info("5、数据均衡过程中，断开逻辑卷连接，删除逻辑卷.")
    lun = osan.get_lun()
    lun_maps = osan.get_lun_maps()
    log.info("删除卷映射.")
    for i in lun_maps:
        osan.delete_lun_map(map_id=i)
    for i in lun:
        osan.delete_lun(lun_id=i)


def main():
    write_data.preare_vdb()
    test_threads = []
    test_threads.append(threading.Thread(target=add_node))
    test_threads.append(threading.Thread(target=down_net))
    for test_thread in test_threads:
        test_thread.setDaemon(True)
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()
    os._exit(-110)


if __name__ == '__main__':
    main()

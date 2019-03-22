#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Date:20181211
Author:Diws
:Description:
1、创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
4、在步骤3中的业务运行过程中，向3个节点中各加入2块新SSD盘，将新盘设置共享盘，存储节点启动均衡；
5、业务执行完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
6、数据均衡完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
7、检查均衡后硬盘容量，比较存储内部数据一致性；
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
# 生成vdb配置文件
mix_1 = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                         xfersize="(5k,100)",
                         seekpct=0,
                         rdpct=0)
mix_2 = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(3k,100)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)


def add_disk(pipe_write):
    """
    :Description:添加磁盘
    :return: None
    """
    time.sleep(60)
    for fault_ip in deploy_ips:
        fault_id = disk.get_node_id_by_ip(n_ip=fault_ip)
        free_disk_uuids = disk.get_free_disk_uuid_by_node_id(node_id=fault_id, disk_type='share')
        if len(free_disk_uuids) == 0:
            log.info('On node %s did not find any disks.' % (fault_ip,))
            continue
        log.info("节点%s free磁盘：%s." % (str(fault_ip), free_disk_uuids))
        free_disk_uuids = free_disk_uuids[:2]
        log.info("4、在步骤3中的业务运行过程中，向3个节点中各加入2块新SSD盘.")
        for d_n in free_disk_uuids:
            disk.add_disk(s_ip=fault_ip, uuid=d_n, usage="SHARED", node_id=fault_id)
        log.info("4、添加到共享池中，存储节点启动均衡")
        # for d_n in free_disk_uuids:
        #     disk.expand_disk_2_storage_pool_by_uuid(s_ip=fault_ip, node_id=fault_id, uuid=d_n, storage_pool_id=1)
    os.write(pipe_write, "success")


def vdb_jn(pipe_read):
    """
    :Description:执行带校验的vdb
    :param pipe_read: 匿名管道，当添加节点成功后，才执行下一个步骤
    :return:
    """
    log.info("3、在主机1上运行vdbench -f mix-S-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_1, output=deploy_ips[0], jn_jro="jn")
    while True:
        disk_info = os.read(pipe_read, 30)
        if len(disk_info) != 0:
            log.info(disk_info)
            log.info("Add disk finished.")
            break
    log.info("5、业务执行完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_1, output=deploy_ips[0], jn_jro="jro")
    # 检查均衡
    log.info("检查均衡是否完成.")
    disk.check_baljob()
    log.info("6、数据均衡完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_1, output=deploy_ips[0], jn_jro="jro")
    log.info("7、检查均衡后硬盘和节点容量，比较存储内部数据一致性.")
    disk_cap_info = disk.get_disk_cap()
    log.info("获取磁盘使用率信息:%s." % (disk_cap_info,))
    disk.comp_disk_cap(disk_cap_info)
    log.info("比较存储内部数据一致性.")
    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    """
    :Description:执行不带校验的vdb
    :return:
    """
    log.info("3、在主机2上运行vdbench -f mix-S.conf.")
    osan.run_vdb(client_ips[1], mix_2, output=deploy_ips[0], time=1200)


def main():
    write_data.preare_vdb()
    pipe_read, pipe_write = os.pipe()
    test_threads = []
    test_threads.append(threading.Thread(target=add_disk, args=(pipe_write,)))
    test_threads.append(threading.Thread(target=vdb_jn, args=(pipe_read,)))
    test_threads.append(threading.Thread(target=vdb_run))
    for test_thread in test_threads:
        test_thread.setDaemon(True)
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()
    os._exit(-110)


if __name__ == '__main__':
    main()

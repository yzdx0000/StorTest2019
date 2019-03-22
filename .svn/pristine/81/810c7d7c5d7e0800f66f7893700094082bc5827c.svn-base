# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-7

'''
测试内容:业务过程中磁盘异常
测试步骤：
1）配置访问区等设置，创建逻辑卷，映射至主机
2）主机端对逻辑卷进行读写业务，过程中将磁盘中的一块磁盘拔出
3）检查业务不中断
检查项：
业务不中断


'''

# testlink case: 1000-33688
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


def get_disk():
    node_id = env_manage.com_lh.get_node_id_by_ip(node_ip1)
    share_disk, data_disk = env_manage.com_lh.get_share_monopoly_disk_ids(s_ip=node_ip1, node_id=node_id)
    disk_ids = []
    for data_disk in data_disk:
        disk_id = env_manage.com_lh.get_physicalid_by_name(node_ip1, data_disk)
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


def vdb_test():
    log.info("vdbench 进行读写业务")
    lun_name = env_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    if len(lun_name) > 10:
        lun_name = lun_name[:10]
    log.info("主机端扫描到的逻辑卷：%s" % (lun_name))
    vdb_file = env_manage.com2_osan.gen_vdb_xml(lun=lun_name, xfersize="4k", rdpct="50")
    env_manage.com2_osan.run_vdb(client_ip=client_ip1, vdb_xml=vdb_file, output=node_ip1, jn_jro="jn", time=300)
    env_manage.com2_osan.run_vdb(client_ip=client_ip1, vdb_xml=vdb_file, output=node_ip1, jn_jro="jro")


def vdb_result():
    log.info("保存vdb测试结果")
    env_manage.osan.save_vdb_log(c_ip=client_ip1, f_name="vdbtest")


def check_client():
    disk_name = env_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    if disk_name is None:
        return
    else:
        env_manage.osan.iscsi_logout_all(client_ip1)


def case():
    log.info("step:1.创建逻辑卷，随机选取一个数据盘,创建lun map")
    env_manage.create_lun()  # 创建lun
    disk_id = get_disk()
    env_manage.create_lun_map()
    log.info("step:2.ISCSI 登录")
    env_manage.create_iscsi_login(client_ip1)
    log.info("step:3.vdbench测试过程中将磁盘拔掉")
    threads = []
    t1 = threading.Thread(target=vdb_test)  # vdbench自动测试
    threads.append(t1)
    t2 = threading.Thread(target=remove_disk, args=(node_ip1, disk_id))  # 同时进行拔盘
    threads.append(t2)
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    log.info("step:4.检查运行结果，插回磁盘")
    insert_disk(node_ip1, disk_id)
    vdb_result()


def main():
    init_disk = env_manage.clean_test_env()
    setup()
    case()
    log.info("step:5.检查清理测试环境")
    check_client()
    env_manage.clean_lun_map()
    env_manage.clean_lun()
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

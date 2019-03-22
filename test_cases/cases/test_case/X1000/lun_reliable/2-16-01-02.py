# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-7

'''
测试内容:删除卷过程中添加磁盘
测试步骤：
1）使用三个节点创建节点池创建存储池，在该存储池中创建逻辑卷，
2）创建完成后，删除逻辑卷，删除过程中从该存储池中添加新磁盘
检查项：
添加新磁盘无异常
删除无异常
'''

# testlink case: 1000-33692
import os
import threading
import utils_path
import log
import common
import prepare_x1000
import ReliableTest
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


uuids = []


def add_new_disk(n_ip):
    new_disk_uuids = env_manage.com_lh.get_unuse_disk_uuid(s_ip=n_ip)
    s_pool_id = env_manage.osan.get_storage_id(s_ip=n_ip)
    for uuid in new_disk_uuids:
        uuids.append(uuid)
        log.info("will add disk UUID is : %s" % (uuid))
        env_manage.com_lh.add_disks(s_ip=n_ip, uuid=uuid, usage="DATA", storage_id=s_pool_id[1])


def remove_disk(uuids):
    log.info("deleting disk, waiting better long .......")
    for id in uuids:
        disk_id = env_manage.com_bd_disk.get_disk_id_by_uuid(s_ip=node_ip1, node_id=1, disk_uuid=id)
        env_manage.com_bd_disk.delete_disk(node_ip1, disk_id)
    log.info("finished")


def case():
    log.info("step:1.创建逻辑卷")
    env_manage.create_lun()
    log.info("step:2.删除逻辑卷过程中向存储中添加新硬盘")
    threads = []
    t1 = threading.Thread(target=env_manage.clean_lun, args=(node_ip1,))
    threads.append(t1)
    t2 = threading.Thread(target=add_new_disk, args=(node_ip1,))
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main():
    setup()
    check_disk = env_manage.com_lh.get_unuse_disk_uuid(node_ip1)
    if len(check_disk) > 0:
        init_disk = env_manage.clean_test_env()
        case()
        log.info("step:2.清理检查测试环境")
        remove_disk(uuids)
        disks = env_manage.clean_test_env()
        if init_disk == disks:
            log.info("check system all node disk %s success" % disks)
        else:
            log.info("check system all node disk %s have lost" % disks)
            exit(1)
    else:
        log.info("please insert new disk, finish test")
        exit(1)
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)

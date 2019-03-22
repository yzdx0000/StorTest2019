# -*-coding:utf-8 -*
import os
import time
import threading
import random

import utils_path
import vdbench_common as this
import common
import log
import get_config
import prepare_clean

#
# Author: caizhenxing
# date 2018/12/19
# @summary：
#           1磁盘1网络
# @steps:
#           1、部署集群，2+2:2配比，挂载2个以上私有客户端；
#           2、vdbench混合业务脚本（2客户端以上），写入数据./vdbench -f test -jn；
#           3、format结束后，执行读写操作，拔出一块数据盘，观察业务情况；
#           4、修复过程中，断开另外一个节点的所有网络，观察业务情况；
#           5、修复过程中，使用vdbench检查数据一致性./vdbench -f test -jro；
#           6、修复完成后，使用vdbench检查数据一致性./vdbench -f test -jro；
# @changelog：
#

# testlink case: 3.0-41760
# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
VOLUME = os.path.join(prepare_clean.MOUNT_PAHT, FILE_NAME)
client_ip_list = get_config.get_allclient_ip()
sys_ip_list = get_config.get_allparastor_ips()
fault_ip = None


def case():
    """更新磁盘重建的等待时间"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')
    common.update_param("MGR", "node_isolate_timeout", "86400000")
    test_threads = []
    (pipein, pipeout) = os.pipe()
    test_threads.append(threading.Thread(target=up_down, args=(pipein,)))
    test_threads.append(threading.Thread(target=vdb_jn, args=(pipeout,)))
    for test_thread in test_threads:
        test_thread.setDaemon(True)
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()


def up_down(pipein):

    """更新磁盘重建的等待时间"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')

    global fault_ip

    time.sleep(120)
    while True:
        line = os.read(pipein, 32)
        if 'pull' in line:
            break
    log.info("\033[1;31;40m在业务运行过程中，将随机拔出一节点的一块数据盘；\033[0m")
    disk_name_dict, node_id_lst = this.get_disk_nodeid_uuid_usage(is_data_disk=True, disk_num_each_node=1)
    this.pullout_disk(disk_name_dict)
    time.sleep(70)

    log.info("\033[1;31;40m在修复过程中，将另一节点的网卡全部down掉（除管理ip）；\033[0m")
    node = common.Node()
    del_ip = node.get_node_ip_by_id(node_id_lst[0])
    sys_ip_list.remove(del_ip)
    node_ip = random.choice(sys_ip_list)
    fault_ip = node_ip
    del_ip_eth_name = this.get_node_eth_name_lst(node_ip, is_specified=True)
    all_eth_name = this.get_node_eth_name_lst(node_ip)
    for ip in del_ip_eth_name:
        all_eth_name.remove(ip)
    this.down_node_net(node_ip, all_eth_name)
    while True:
        line = os.read(pipein, 32)
        if 'add' in line:
            break
    time.sleep(30)
    log.info("\033[1;31;40m测试结束，重新up网卡及将拔出的磁盘重新添加回系统；\033[0m")
    this.up_node_net(node_ip, all_eth_name)
    this.insert_disk(disk_name_dict)
    this.del_disk(disk_name_dict)
    this.add_disk(disk_name_dict)
    log.info("\033[1;31;40m####################up_down_finish########################\033[0m")
    '''将等待时间的参数修改回来'''
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '18000000')


def vdb_jn(pipeout):
    log.info("\033[1;31;40mRun vdbench to create data on %s.\033[0m" % client_ip_list)
    this.vdbench_run(VOLUME, run_create=True, ip_list=client_ip_list)
    log.info("\033[1;31;40mRun vdbench with jn on %s.\033[0m" % client_ip_list)
    os.write(pipeout, "pull_disk")
    this.vdbench_run(VOLUME, run_write_jn=True, ip_list=client_ip_list, elapsed=360)
    log.info("\033[1;31;40mRun vdbench with jro.\033[0m")
    this.vdbench_run(VOLUME, run_check=True, ip_list=client_ip_list)
    this.check_rebuild_job(fault_node_ip=fault_ip)
    log.info("\033[1;31;40m数据修复完成，比较存储内部数据一致性；\033[0m")
    log.info("\033[1;31;40mRun vdbench with jro.\033[0m")
    this.vdbench_run(VOLUME, run_check=True, ip_list=client_ip_list)
    os.write(pipeout, "add_disk")
    this.vdbench_run(VOLUME, run_clean=True, ip_list=client_ip_list)


def main():
    prepare_clean.defect_test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.defect_test_prepare(FILE_NAME, env_check=False)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

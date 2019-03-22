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
# date 2018/12/17
# @summary：
#           整集群下电
# @steps:
#           1、部署集群，4+2:1配比，挂载2个以上私有客户端；
#           2、vdbench混合业务脚本（2客户端以上），写入数据./vdbench -f test -jn；
#           3、format结束后，执行读写操作，整集群关机（shutdown或断电）操作，观察业务情况；
#           4、集群上电恢复，观察业务状态；
#           5、使用vdbench检查数据一致性./vdbench -f test -jro；
# @changelog：
#

# testlink case: 3.0-41653
# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
VOLUME = os.path.join(prepare_clean.MOUNT_PAHT, FILE_NAME)
client_ip_list = get_config.get_allclient_ip()
sys_ip_list = get_config.get_allparastor_ips()
esxi_info = get_config.get_esxi_info()
fault_ip = None
read_path, write_path = this.creat_pipe()


def case():
    test_threads = []
    (pipein, pipeout) = os.pipe()
    test_threads.append(threading.Thread(target=up_down, args=(pipein,)))
    test_threads.append(threading.Thread(target=vdb_jn, args=(pipeout,)))
    for test_thread in test_threads:
        test_thread.setDaemon(True)
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()


def up_down():
    global fault_ip
    """更新磁盘重建的等待时间"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '18000000')

    read_file = os.open(read_path, os.O_RDONLY)
    while True:
        line = os.read(read_file, 32)
        if 'down' in line:
            break
    time.sleep(60)
    log.info("\033[1;31;40m在业务运行过程中，将整集群下电关机；\033[0m")

    data_lst = this.down_node(sys_ip_list)
    log.info("\033[1;31;40m等待2分钟\033[0m")
    time.sleep(120)
    log.info("\033[1;31;40m整集群上电\033[0m")
    this.up_node(data_lst)
    write_file = os.open(write_path, os.O_CREAT | os.O_RDWR)
    os.write(write_file, "up_node")
    log.info("\033[1;31;40m####################up_down_finish########################\033[0m")
    '''将等待时间的参数修改回来'''
    # common.update_param('MGR', 'disk_isolate2rebuild_timeout', '18000000')


def vdb_jn():
    log.info("\033[1;31;40mRun vdbench to create data on %s.\033[0m" % client_ip_list)
    this.vdbench_run(VOLUME, run_create=True, ip_list=client_ip_list)
    log.info("\033[1;31;40mRun vdbench with jn on %s.\033[0m" % client_ip_list)
    this.vdbench_run(VOLUME, run_write_jn=True, ip_list=client_ip_list, elapsed=300, is_fault_exit=False)
    write_file = os.open(read_path, os.O_CREAT | os.O_RDWR)
    os.write(write_file, "down_node")
    read_file = os.open(write_path, os.O_RDONLY)
    while True:
        line = os.read(read_file, 32)
        if 'up' in line:
            break
    this.check_ping(sys_ip_list)
    this.verify_node_stat()
    this.check_rebuild_job()
    log.info("\033[1;31;40mAll of the services are OK.\033[0m")
    log.info("\033[1;31;40m数据修复/重建完成，比较存储内部数据一致性；\033[0m")
    log.info("\033[1;31;40mRun vdbench with jro.\033[0m")
    this.vdbench_run(VOLUME, run_check=True, ip_list=client_ip_list)
    this.vdbench_run(VOLUME, run_clean=True, ip_list=client_ip_list)
    log.info("\033[1;31;40m+++++++++++++++++++++++run_vdbench_finish++++++++++++++++++++++++++\033[0m")


def main():
    prepare_clean.defect_test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.defect_test_prepare(FILE_NAME, env_check=False)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

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
#           数据双网，断1网客户端
# @steps:
#           1、部署集群，3副本配比，两根数据网，挂载2个以上私有客户端；
#           2、vdbench混合业务脚本（2客户端以上），写入数据./vdbench -f test -jn；
#           3、format结束后，执行读写操作，客户端数据网断掉1根，观察业务情况；
# @changelog：
#

# testlink case: 3.0-41749
# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
VOLUME = os.path.join(prepare_clean.MOUNT_PAHT, FILE_NAME)
client_ip_list = get_config.get_allclient_ip()
read_path, write_path = this.creat_pipe()


def case():
    """更新磁盘重建的等待时间"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')
    common.update_param("MGR", "node_isolate_timeout", "86400000")
    test_threads = []
    test_threads.append(threading.Thread(target=up_down))
    test_threads.append(threading.Thread(target=vdb_jn))
    for test_thread in test_threads:
        test_thread.setDaemon(True)
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()


def up_down():
    args = this.get_random_client_data_ip_and_eth()
    read_file = os.open(read_path, os.O_RDONLY)
    while True:
        line = os.read(read_file, 32)
        if 'down' in line:
            break

    time.sleep(120)
    log.info("\033[1;31;40m在业务运行过程中，将断开客户端随机一数据网；\033[0m")
    this.down_node_net(*args)

    time.sleep(120)
    log.info("\033[1;31;40m重新up网卡；\033[0m")
    this.up_node_net(*args)
    write_file = os.open(write_path, os.O_CREAT | os.O_RDWR)
    os.write(write_file, "up_eth")
    log.info("\033[1;31;40m####################up_down_finish########################\033[0m")


def vdb_jn():
    log.info("\033[1;31;40mRun vdbench to create data on %s.\033[0m" % client_ip_list)
    this.vdbench_run(VOLUME, run_create=True, ip_list=client_ip_list)
    write_file = os.open(read_path, os.O_CREAT | os.O_RDWR)
    os.write(write_file, "down_eth")
    log.info("\033[1;31;40mRun vdbench with jn on %s.\033[0m" % client_ip_list)
    this.vdbench_run(VOLUME, run_write_jn=True, ip_list=client_ip_list)
    # log.info("\033[1;31;40mRun vdbench with jro.\033[0m")
    # this.vdbench_run(VOLUME, run_check=True, ip_list=client_ip_list)
    read_file = os.open(write_path, os.O_RDONLY)
    while True:
        line = os.read(read_file, 32)
        if 'up' in line:
            break

    this.check_rebuild_job()
    log.info("\033[1;31;40m数据修复完成，比较存储内部数据一致性；\033[0m")
    log.info("\033[1;31;40mRun vdbench with jro.\033[0m")
    this.vdbench_run(VOLUME, run_check=True, ip_list=client_ip_list)
    this.vdbench_run(VOLUME, run_clean=True, ip_list=client_ip_list)


def main():
    prepare_clean.defect_test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.defect_test_prepare(FILE_NAME, env_check=False)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

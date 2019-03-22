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
# date 2018/12/18
# @summary：
#           不带lmos日志角色节点删除
# @steps:
#           1、部署集群，4+2:1配比，挂载2个以上私有客户端；
#           2、vdbench混合业务脚本（2客户端以上），写入数据./vdbench -f test -jn；
#           3、format结束后，执行读写操作，通过gui删除不带lmos日志角色，观察业务情况；
#           4、修复过程中，使用vdbench检查数据一致性./vdbench -f test -jro；
#           5、修复完成后，使用vdbench检查数据一致性./vdbench -f test -jro；
# @changelog：
#

# testlink case: 3.0-41657
# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
VOLUME = os.path.join(prepare_clean.MOUNT_PAHT, FILE_NAME)
client_ip_list = get_config.get_allclient_ip()
sys_ip_list = get_config.get_allparastor_ips()
esxi_info = get_config.get_esxi_info()
fault_ip = None


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


def up_down(pipein):
    global fault_ip
    """更新磁盘重建的等待时间"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')
    common.update_param("MGR", "node_isolate_timeout", "300000")

    while True:
        line = os.read(pipein, 32)
        if 'down' in line:
            break
    time.sleep(60)
    log.info("\033[1;31;40m在业务运行过程中，将一不带lmos日志角色节点删除；\033[0m")
    ip_lst = []
    lmos_node_ip_lst = this.get_lmos_ip_lst(is_lmos=False)
    while True:
        node_ip = random.choice(lmos_node_ip_lst)
        if node_ip not in client_ip_list:
            fault_ip = node_ip
            ip_lst.append(node_ip)
            break
    config_file = this.create_config_file(ip_lst)

    # this.up_node(data_lst)
    # this.check_ping(ip_lst)
    this.remove_nodes(ip_lst)
    while True:
        line = os.read(pipein, 32)
        if 'up' in line:
            break

    '''将等待时间的参数修改回来'''
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '3600000', fault_node_ip=ip_lst[0])
    common.update_param("MGR", "node_isolate_timeout", "86400000", fault_node_ip=ip_lst[0])
    log.info("\033[1;31;40m####################Begin to restore the environment ########################\033[0m")
    this.add_nodes(config_file)
    log.info("\033[1;31;40m####################Finish restore the environment ########################\033[0m")
    log.info("\033[1;31;40m####################up_down_finish########################\033[0m")
    '''将等待时间的参数修改回来'''
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '18000000')


def vdb_jn(pipeout):
    log.info("\033[1;31;40mRun vdbench to create data on %s.\033[0m" % client_ip_list)
    this.vdbench_run(VOLUME, run_create=True, ip_list=client_ip_list)
    log.info("\033[1;31;40mRun vdbench with jn on %s.\033[0m" % client_ip_list)
    os.write(pipeout, "down_node")
    this.vdbench_run(VOLUME, run_write_jn=True, ip_list=client_ip_list, elapsed=360)
    log.info("\033[1;31;40mRun vdbench with jro.\033[0m")
    this.vdbench_run(VOLUME, run_check=True, ip_list=client_ip_list)
    this.check_rebuild_job(fault_node_ip=fault_ip)
    log.info("\033[1;31;40m数据修复/重建完成，比较存储内部数据一致性；\033[0m")
    log.info("\033[1;31;40mRun vdbench with jro.\033[0m")
    this.vdbench_run(VOLUME, run_check=True, ip_list=client_ip_list)
    os.write(pipeout, "up_node")
    this.vdbench_run(VOLUME, run_clean=True, ip_list=client_ip_list)
    log.info("\033[1;31;40m+++++++++++++++++++++++run_vdbench_finish++++++++++++++++++++++++++\033[0m")


def main():
    prepare_clean.defect_test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.defect_test_prepare(FILE_NAME, env_check=False)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

# -*-coding:utf-8 -*
import os
import time
import threading

import utils_path
import vdbench_common as this
import common
import log
import get_config
import prepare_clean

#
# Author: caizhenxing
# date 2018/12/3
# @summary：
#           不同节点分别同时坏一块数据盘
# @steps:
#           1、部署集群，4+2:1配比，挂载2个以上私有客户端；
#           2、vdbench混合业务脚本（2客户端以上），写入数据./vdbench -f test -jn；
#           3、format结束后，执行读写操作，不同节点同时拔出一块数据盘，观察业务情况；
#           4、修复过程中，使用vdbench检查数据一致性./vdbench -f test -jro；
#           5、修复完成后，使用vdbench检查数据一致性./vdbench -f test -jro；
# @changelog：
#

# testlink case: 3.0-41698
# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
VOLUME = os.path.join(prepare_clean.MOUNT_PAHT, FILE_NAME)
client_ip_list = get_config.get_allclient_ip()


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
    """更新磁盘重建的等待时间"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')
    while True:
        line = os.read(pipein, 32)
        if 'pull' in line:
            break
    time.sleep(60)
    log.info("\033[1;31;40m在业务运行过程中，不同节点各拔出一块数据盘；\033[0m")
    disk_name_dict, node_id_lst = this.get_disk_nodeid_uuid_usage(is_data_disk=True,
                                                                  count_of_node=2,
                                                                  disk_num_each_node=1)
    this.pullout_disk(disk_name_dict)
    while True:
        line = os.read(pipein, 32)
        if 'add' in line:
            break

    log.info("\033[1;31;40m####################Begin to restore the environment ########################\033[0m")
    this.insert_disk(disk_name_dict)
    this.del_disk(disk_name_dict)
    this.add_disk(disk_name_dict)
    log.info("\033[1;31;40m####################Finish restore the environment ########################\033[0m")
    log.info("\033[1;31;40m####################up_down_finish########################\033[0m")
    '''将等待时间的参数修改回来'''
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '18000000')


def vdb_jn(pipeout):
    log.info("\033[1;31;40mRun vdbench to create data on %s.\033[0m" % client_ip_list)
    this.vdbench_run(VOLUME, run_create=True, ip_list=client_ip_list)
    log.info("\033[1;31;40mRun vdbench with jn on %s.\033[0m" % client_ip_list)
    os.write(pipeout, "pull_disk")
    this.vdbench_run(VOLUME, run_write_jn=True, ip_list=client_ip_list)
    log.info("\033[1;31;40mRun vdbench with jro.\033[0m")
    this.vdbench_run(VOLUME, run_check=True, ip_list=client_ip_list)
    this.check_rebuild_job()
    log.info("\033[1;31;40m数据修复/重建完成，比较存储内部数据一致性；\033[0m")
    log.info("\033[1;31;40mRun vdbench with jro.\033[0m")
    this.vdbench_run(VOLUME, run_check=True, ip_list=client_ip_list)
    os.write(pipeout, "add_disk")
    this.vdbench_run(VOLUME, run_clean=True, ip_list=client_ip_list)
    log.info("\033[1;31;40m+++++++++++++++++++++++run_vdbench_finish++++++++++++++++++++++++++\033[0m")


def main():
    prepare_clean.defect_test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.defect_test_prepare(FILE_NAME, env_check=False)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

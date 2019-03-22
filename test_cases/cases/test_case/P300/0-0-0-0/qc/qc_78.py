# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import shell
import get_config
import prepare_clean
import make_fault

#################################################################
#
# Author: chenjy1
# Date: 2018-07-30
# @summary：
#    三节点物理机跑4k mdtest，一块硬盘疑似掉了，导致出现oStor的core
# @steps:
#    1，开启子进程跑mdtest
#    2，拔一块数据盘
#    3, 等跑完后插盘
#    4，判断是不是触发了被动重建,按相应流程处理
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
MDTEST_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME, "mdtest")
MACHINES_PATH = '/tmp/machines'


def mdtest_large_data(exe_ip):
    """
    :author :             cheninyu
    :date:                2018.07.30
    :description:         跑mdtest
    :param exe_ip:       执行命令的ip
    :return:             无
    """
    cmd = 'mpirun -hostfile %s -np 10 -allow-run-as-root mdtest -z 2 -b 2 -I 11 -C -i 2 -d %s' % (MACHINES_PATH, MDTEST_PATH)
    rc, stdout = common.run_command(exe_ip, cmd)
    if rc != 0:
        raise Exception("mdtest execution is failed!!!!!!")
    return


def case():
    log.info("----------case----------")

    """随机选取集群内的一个节点，获取节点的数据盘的物理id"""
    """获取集群内所有节点的id"""
    ob_node = common.Node()
    ob_disk = common.Disk()
    ob_storage_pool = common.Storagepool()
    nodeid_list = ob_node.get_nodes_id()

    """随机选一个节点"""
    fault_node_id = random.choice(nodeid_list)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    """获取节点内的所有数据盘的物理id"""
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)

    """随机获取一个数据盘"""
    fault_disk_name = random.choice(monopoly_disk_names)
    fault_disk_physical_id = ob_disk.get_physicalid_by_name(fault_node_ip, fault_disk_name)
    fault_disk_id = ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name)
    fault_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_disk_name)
    fault_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_disk_name)
    storage_pool_id = ob_disk.get_storage_pool_id_by_diskid(fault_node_id, fault_disk_id)

    '''确保磁盘重建的等待时间为默认值'''
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '3600000')

    client_ip_lst = get_config.get_allclient_ip()

    """准备mdtest的配置文件"""
    common.rm_exe(client_ip_lst[0], MACHINES_PATH)
    cmd = 'echo "%s slots=10\n" > %s' % (client_ip_lst[0], MACHINES_PATH)
    rc, stdout = common.run_command(client_ip_lst[0], cmd)
    if rc != 0:
        raise Exception('mdtest configure file failed !!!')

    cmd = 'mkdir -p %s ' % MDTEST_PATH
    rc, stdout = common.run_command(client_ip_lst[0], cmd)
    if rc != 0:
        raise Exception('mdtest path failed !!!')

    log.info("1> 开启子进程跑mdtest")
    p1 = Process(target=mdtest_large_data, args=(client_ip_lst[0],))
    p1.start()

    log.info('wait 60s')
    time.sleep(60)

    log.info("2> 拔一块数据盘")
    make_fault.pullout_disk(fault_node_ip, fault_disk_physical_id, fault_disk_usage)

    p1.join()

    log.info("3> 等跑完后插盘")
    make_fault.insert_disk(fault_node_ip, fault_disk_physical_id, fault_disk_usage)

    """获取故障磁盘状态"""
    log.info("4> 判断是不是触发了被动重建,按相应流程处理")
    rc, disk_info = ob_disk.get_disk_info(fault_node_id)
    disks = common.json_loads(disk_info)
    for cur_disk in disks['result']['disks']:
        if cur_disk['uuid'] == fault_disk_uuid:
            if cur_disk['state'] == 'DISK_STATE_REBUILDING_PASSIVE' or \
                            cur_disk['state'] == 'DISK_STATE_ZOMBIE':
                """不断检查重建任务是否存在"""
                start_time = time.time()
                while True:
                    if False == common.check_rebuild_job():
                        log.info('rebuild job finish!!!')
                        break
                    time.sleep(20)
                    exist_time = int(time.time() - start_time)
                    m, s = divmod(exist_time, 60)
                    h, m = divmod(m, 60)
                    log.info('rebuild job exist %dh:%dm:%ds' % (h, m, s))
                """不断检查坏对象是否修复"""
                count = 0
                while True:
                    count += 1
                    log.info("the %d times check badjobnr" % count)
                    log.info("wait 60 seconds")
                    time.sleep(60)
                    if True == common.check_badjobnr():
                        break

                log.info('wait 60s')
                time.sleep(60)

                """删除磁盘"""
                ob_disk.remove_disks(fault_disk_id)

                log.info('wait 180s')
                time.sleep(180)

                """加入磁盘,并且加入存储池"""
                ob_disk.add_disks(fault_node_id, fault_disk_uuid, fault_disk_usage)
                fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)
                ob_storage_pool.expand_storage_pool(storage_pool_id, fault_disk_id_new)

    log.info('wait 30s')
    time.sleep(30)

    """检查所有的磁盘状态是否正确"""
    if True != common.check_alldisks_health():
        raise Exception("some disks is not health")

    if p1.exitcode != 0:
        raise Exception("mdtest is failed!!!!!!")

    """检查系统"""
    common.ckeck_system()

    log.info("case succeed!")


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
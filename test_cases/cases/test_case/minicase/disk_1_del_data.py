# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import tool_use
import get_config
import prepare_clean

#################################################################
#
# author 张芳芳
# date 2018-07-06
# @summary：
#    本测试主要测试删盘测试，进行重建。
# @steps:
#    1, 修改磁盘重建等待时间
#    2，使用vdbench创建文件和数据校验
#    3，同时在一个节点上每隔5分钟随机删除一块数据盘，重建之后再添加回去
#
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
MINI_TRUE_PATH = os.path.join(prepare_clean.MINICASE_PATH, FILE_NAME)      # /mnt/volume1/mini_case/3_0015_truncate_test


def case():
    log.info("----------case----------")
    '''随机选取集群内的一个节点，获取节点的数据盘的物理id'''
    '''获取集群内所有节点的id'''
    ob_node = common.Node()
    ob_disk = common.Disk()
    ob_storage_pool = common.Storagepool()
    nodeid_list = ob_node.get_nodes_id()

    '''随机选一个节点'''
    fault_node_id = random.choice(nodeid_list)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    '''获取节点内的所有数据盘的物理id'''
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)

    """随机获取一个数据盘"""
    fault_disk_name = random.choice(monopoly_disk_names)
    fault_disk_id = ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name)
    fault_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_disk_name)
    fault_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_disk_name)
    storage_pool_id = ob_disk.get_storage_pool_id_by_diskid(fault_node_id, fault_disk_id)
    log.info("fault_node_id : %s"
             "\nfault_disk_name : %s"
             "\nfault_disk_id : %s"
             "\nfault_disk_uuid : %s"
             "\nfault_disk_usage : %s"
             "\nstorage_pool_id : %s"
             % (str(fault_node_id),
                fault_disk_name,
                fault_disk_id,
                fault_disk_uuid,
                fault_disk_usage,
                str(storage_pool_id)))

    client_ip_lst = get_config.get_allclient_ip()

    p1 = Process(target=tool_use.vdbench_run, args=(MINI_TRUE_PATH, client_ip_lst[0], client_ip_lst[1]),
                 kwargs={'run_create': True, 'run_check_write': True})
    p2 = Process(target=ob_disk.remove_disks_asyn, args=(fault_disk_id,))

    p1.start()
    time.sleep(10)
    p2.start()

    p1.join()
    p2.join()

    log.info('wait 60s')
    time.sleep(60)

    """检查磁盘是否删除"""
    start_time = time.time()
    while True:
        if 0 == ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name):
            log.info('node %s disk %s delete success!!!' % (fault_node_ip, fault_disk_name))
            break
        time.sleep(20)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('node %s disk %s delete %dh:%dm:%ds' % (fault_node_ip, fault_disk_name, h, m, s))

    """不断检查重建任务是否存在"""
    start_time = time.time()
    while True:
        if not common.check_rebuild_job():
            log.info('rebuild job finish!!!')
            break
        time.sleep(20)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('rebuild job exist %dh:%dm:%ds' % (h, m, s))

    """加入磁盘,并且加入存储池"""
    rc, stdout = ob_disk.add_disks(fault_node_id, fault_disk_uuid, fault_disk_usage)
    common.judge_rc(rc, 0, 'add_disks failed')
    fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)
    rc, stdout = ob_storage_pool.expand_storage_pool(storage_pool_id, fault_disk_id_new)
    common.judge_rc(rc, 0, 'expand_storage_pool failed')

    '''将等待时间的参数修改回来'''
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '3600000')

    common.judge_rc(p1.exitcode, 0, 'vdbench create and check_write')

    '''不断检查坏对象是否修复'''
    count = 0
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 60 seconds")
        time.sleep(60)
        if common.check_badjobnr():
            break

    '''再跑01检查数据的正确性'''
    tool_use.vdbench_run(MINI_TRUE_PATH, client_ip_lst[0], client_ip_lst[1], run_check=True)

    '''检查系统'''
    common.ckeck_system()
    log.info("case succeed!")


def main():
    prepare_clean.minicase_test_prepare(FILE_NAME)
    case()
    prepare_clean.minicase_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)
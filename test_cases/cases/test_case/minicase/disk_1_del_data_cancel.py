# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random
import traceback

import utils_path
import common
import log
import tool_use
import prepare_clean
import get_config

#################################################################
#
# Author: baorb
# date 2017-08-21
# @summary：
#    本测试主要测试删除和取消删除硬盘。
# @steps:
#    1，使用vdbench创建文件和数据校验
#    2，同时在一个节点上每隔一段时间随机删除并取消删除数据盘
#
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
MINI_TRUE_PATH = os.path.join(prepare_clean.MINICASE_PATH, FILE_NAME)      # /mnt/volume1/mini_case/3_0015_truncate_test


def case_main(fun):
    """
    :author:         baoruobing
    :date  :         2018.04.17
    :description:    提供给脚本的main函数，可以捕获脚本运行中的异常
    :param fun:     函数对象，一般为脚本入口函数
    :param args:    函数参数
    :param kwargs:  函数参数
    :return:
    """
    def _aa(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except Exception:
            log.error("case failed!!!", exc_info=1)
            traceback.print_exc()
            exit(1)
    return _aa


@case_main
def delete_disk():
    '''获取集群内所有节点的id'''
    ob_node = common.Node()
    ob_disk = common.Disk()
    nodeid_list = ob_node.get_nodes_id()

    '''随机选一个节点'''
    node_id = random.choice(nodeid_list)
    log.info("node id = %s" % node_id)

    '''获取一个节点内所有的共享硬盘和数据硬盘'''
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(node_id)

    '''根据节点id获取节点ip'''
    disk_id_list = []
    rc, stdout = ob_disk.get_disk_info(node_id)
    common.judge_rc(rc, 0, 'get disks failed!!!')
    result = common.json_loads(stdout)
    disk_list = result['result']['disks']
    for disk in disk_list:
        if disk['devname'] in monopoly_disk_names:
            disk_id_list.append(disk['id'])

    time.sleep(10)

    for i in range(5):
        fault_disk_id = random.choice(disk_id_list)
        fault_disk_name = ob_disk.get_disk_name_by_id(node_id, fault_disk_id)
        fault_disk_uuid = ob_disk.get_disk_uuid_by_name(node_id, fault_disk_name)
        fault_disk_usage = ob_disk.get_disk_usage_by_name(node_id, fault_disk_name)
        storage_pool_id = ob_disk.get_storage_pool_id_by_diskid(node_id, fault_disk_id)

        ob_disk.remove_disks_asyn(fault_disk_id)
        time.sleep(10)
        rc, stdout = ob_disk.cancel_delete_disk(fault_disk_id)
        if rc != 0:
            stdout = common.json_loads(stdout)
            if stdout['err_msg'] == 'DISK_NO_FOUND':
                """磁盘已经删除,需要添加"""
                ob_storage_pool = common.Storagepool()
                rc, stdout = ob_disk.add_disks(node_id, fault_disk_uuid, fault_disk_usage)
                common.judge_rc(rc, 0, 'add_disks failed')
                fault_disk_id_new = ob_disk.get_disk_id_by_uuid(node_id, fault_disk_uuid)
                rc, stdout = ob_storage_pool.expand_storage_pool(storage_pool_id, fault_disk_id_new)
                common.judge_rc(rc, 0, 'expand_storage_pool failed')
            else:
                common.except_exit('cancle remove disk failed!!!')
        time.sleep(10)
    return


def case():
    log.info("----------case----------")
    '''获取存储集群的节点ip'''
    client_ip_lst = get_config.get_allclient_ip()

    p1 = Process(target=tool_use.vdbench_run, args=(MINI_TRUE_PATH, client_ip_lst[0], client_ip_lst[1]),
                 kwargs={'run_create': True, 'run_check_write': True})
    p2 = Process(target=delete_disk)

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    common.judge_rc(p1.exitcode, 0, 'vdbench_run')
    common.judge_rc(p2.exitcode, 0, 'delete_disk')

    '''不断检查坏对象是否修复'''
    log.info("wait 60 seconds")
    time.sleep(60)
    while True:
        print "wait 60 seconds"
        time.sleep(60)
        if common.check_badjobnr():
            break

    '''再跑01检查数据的正确性'''
    tool_use.vdbench_run(MINI_TRUE_PATH, client_ip_lst[0], client_ip_lst[1], run_check=True)
    log.info("case succeed!")


def main():
    prepare_clean.minicase_test_prepare(FILE_NAME)
    case()
    prepare_clean.minicase_test_clean(FILE_NAME)
    log.info('succeed!')
    return


if __name__ == '__main__':
    common.case_main(main)
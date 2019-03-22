# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import tool_use
import log
import prepare_clean
import get_config
import make_fault

####################################################################################
#
# Author:chenjy1
# Date: 2018-08-14
# @summary：
#     集群中磁盘处于rebuilding状态时，其他zombie状态的磁盘也无法删除
# @steps:
#    1、修改磁盘重建超时参数为30秒
#    2、拔一块盘A等待30秒，等磁盘变为僵尸状态
#    3、vdbench创建文件。同时拔另一块盘B，等重建
#    4、重建时删除盘A，预期可以删除掉
#    5、恢复环境
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
VDBENCH_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)          # /mnt/volume1/defect_case/qc_571


def wait_disk_remove(fault_node_id, fault_disk_id, is_wait=True):
    """
    Author:                      chenjy1
    :date:                       2018.08.14
    :description:                随机拔出插入一块共享盘
    :param fault_node_id:       (int)故障节点ID
    :param fault_disk_id:       (int)故障磁盘ID
    :param is_wait:             (bool)是否判断删除时间
    :return:                    (bool)是否删除掉
    """
    obj_disk = common.Disk()
    flag_remove_disk = False
    start_time = time.time()
    while True:
        if obj_disk.check_disk_exist(fault_node_id, fault_disk_id):  # 盘存在则继续等，三分钟后仍存在则退出报错
            time.sleep(10)
            exist_time = int(time.time() - start_time)
            if is_wait:
                if exist_time > 180:
                    break
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            log.info('disk exist %dh:%dm:%ds' % (h, m, s))
        else:
            flag_remove_disk = True
            log.info("disk have been deleted!")
            break
    return flag_remove_disk


def case():
    log.info("case begin")

    log.info("1> 修改磁盘超时重建参数为30秒")
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')

    log.info("2> 拔一块盘A等待30秒，等磁盘变为僵尸状态")
    '''获取集群节点信息'''
    ob_node = common.Node()
    ob_disk = common.Disk()
    ob_storage_pool = common.Storagepool()
    node_id_lst = ob_node.get_nodes_id()

    '''随机选一个节点'''
    fault_node_id = random.choice(node_id_lst)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    '''获取故障节点内所有的共享硬盘和数据硬盘'''
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)
    """随机选择一个数据盘"""
    fault_disk_name_lst = random.sample(monopoly_disk_names, 2)
    """获取故障盘的scsi id, id, uuid, 盘类型, 存储池id"""
    fault_disk_physicalid_lst = []
    fault_disk_id_lst = []
    fault_disk_uuid_lst = []
    fault_disk_usage_lst = []
    storage_pool_id_lst = []
    for fault_disk_name in fault_disk_name_lst:
        """物理id"""
        fault_disk_physicalid = ob_disk.get_physicalid_by_name(fault_node_ip, fault_disk_name)
        fault_disk_physicalid_lst.append(fault_disk_physicalid)
        """id"""
        fault_disk_id = ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name)
        fault_disk_id_lst.append(fault_disk_id)
        """uuid"""
        fault_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_disk_name)
        fault_disk_uuid_lst.append(fault_disk_uuid)
        """usage"""
        fault_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_disk_name)
        fault_disk_usage_lst.append(fault_disk_usage)
        """存储池id"""
        storage_pool_id = ob_disk.get_storage_pool_id_by_diskid(fault_node_id, fault_disk_id)
        storage_pool_id_lst.append(storage_pool_id)

        log.info("fault_node_id : %s"
                 "\nfault_disk_name : %s"
                 "\nfault_disk_physicalid : %s"
                 "\nfault_disk_uuid : %s"
                 "\nfault_disk_usage : %s"
                 "\nfault_disk_id : %s"
                 "\nstorage_pool_id : %s"
                 % (str(fault_node_id),
                    fault_disk_name,
                    fault_disk_physicalid,
                    fault_disk_uuid,
                    fault_disk_usage,
                    str(fault_disk_id),
                    str(storage_pool_id)))

    """拔盘A"""
    make_fault.pullout_disk(fault_node_ip, fault_disk_physicalid_lst[0], fault_disk_usage_lst[0])

    start_time = time.time()
    while True:
        if "DISK_STATE_ZOMBIE" == ob_disk.get_disk_state_by_id(fault_node_id, fault_disk_id_lst[0]):
            break
        time.sleep(10)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('wait ZOMBIE state %dh:%dm:%ds' % (h, m, s))

    log.info("3> vdbench创建文件。同时拔另一块盘B，等重建")
    client_ip_lst = get_config.get_allclient_ip()
    p1 = Process(target=tool_use.vdbench_run, args=(VDBENCH_PATH, client_ip_lst[0], client_ip_lst[1]),
                 kwargs={'run_create': True})
    p2 = Process(target=make_fault.pullout_disk,
                 args=(fault_node_ip, fault_disk_physicalid_lst[1], fault_disk_usage_lst[1]))
    p1.daemon = True  # 进程都设置为守护进程，为了脚本退出时子进程也能终止
    p2.daemon = True
    p1.start()
    time.sleep(120)
    p2.start()

    """等待拔盘操作完成"""
    p2.join()

    """等待变为被动重建"""
    while True:
        if "DISK_STATE_REBUILDING_PASSIVE" == ob_disk.get_disk_state_by_id(fault_node_id, fault_disk_id_lst[1]):
            break
        time.sleep(10)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('wait REBUILDING_PASSIVE state %dh:%dm:%ds' % (h, m, s))

    log.info("4> 重建时删除盘A，预期可以删除掉")
    ob_disk.remove_disks_asyn(fault_disk_id_lst[0])
    flag_remove_disk_a = wait_disk_remove(fault_node_id, fault_disk_id_lst[0])

    log.info("5> 恢复环境")

    p1.join()

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

    make_fault.insert_disk(fault_node_ip, fault_disk_physicalid_lst[0], fault_disk_usage_lst[0])
    make_fault.insert_disk(fault_node_ip, fault_disk_physicalid_lst[1], fault_disk_usage_lst[1])

    """删除磁盘"""
    ob_disk.remove_disks_asyn(fault_disk_id_lst[1])  # 删除磁盘都用异步，然后检查
    flag_remove_disk_b = wait_disk_remove(fault_node_id, fault_disk_id_lst[1], is_wait=False)

    """加入磁盘,并且加入存储池"""
    for i in range(len(fault_disk_id_lst)):
        ob_disk.add_disks(fault_node_id, fault_disk_uuid_lst[i], fault_disk_usage_lst[i])
        fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid_lst[i])
        ob_storage_pool.expand_storage_pool(storage_pool_id_lst[i], fault_disk_id_new)

    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '3600000')

    """查看存在被动重建时是否能删除僵尸盘"""
    common.judge_rc(flag_remove_disk_a, True, "ZOMBIE disk can not be deleted when REBUILDING_PASSIVE exists")
    common.judge_rc(flag_remove_disk_b, True, "disk b can not be deleted")
    common.judge_rc(p1.exitcode, 0, "vdbench_run failed")

    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)

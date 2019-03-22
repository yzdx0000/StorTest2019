# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import snap_common
import log
import prepare_clean
import get_config
import make_fault
import event_common

####################################################################################
#
# Author: liyao
# date 2018-07-24
# @summary：
#    硬盘故障告警检测
# @steps:
#   1、部署3节点集群环境
#   2、执行pscli --command=clean_alarms清除现有告警信息
#   3、拔出单节点的一块数据盘，等待被动重建
#   4、执行get_alarms查看告警信息是否正确
#   5、将磁盘重新插入
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
EVENT_TRUE_PATH = os.path.join(event_common.EVENT_TEST_PATH, FILE_NAME)
DATA_DIR = os.path.join(EVENT_TRUE_PATH, 'data_dir')                  # /mnt/volume1/event/events_5_3_1_11/data_dir/
CREATE_EVENT_PATH = os.path.join('event', FILE_NAME)                   # /event/events_5_3_6_21
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


def case():
    # 2> 执行pscli --command=clean_alarms清除现有告警信息
    rc, pscli_info = event_common.clean_alarms()
    common.judge_rc(rc, 0, 'clean_alarms falied')

    log.info('waiting for 10s')
    time.sleep(10)

    # 3> 拔出单节点的一块数据盘，等待被动重建
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
    fault_disk_physical_id = ob_disk.get_physicalid_by_name(fault_node_ip, fault_disk_name)
    fault_disk_id = ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name)
    fault_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_disk_name)
    fault_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_disk_name)
    storage_pool_id = ob_disk.get_storage_pool_id_by_diskid(fault_node_id, fault_disk_id)

    client_ip_lst = get_config.get_allclient_ip()

    '''更新磁盘重建的等待时间'''
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')
    p1 = Process(target=make_fault.pullout_disk, args=(fault_node_ip, fault_disk_physical_id, fault_disk_usage))
    p1.start()

    rc, pscli_info = event_common.get_alarms()

    time_waiting = 10
    sleep_mark = True
    while sleep_mark:
        log.info('waiting for %s' % time_waiting)
        time.sleep(time_waiting)
        rc, pscli_info = event_common.get_alarms()
        if rc != 0:
            log.info('system has not prepared well !!!')
            sleep_mark = True
        else:
            sleep_mark = False

    p1.join()

    # 4> 执行get_alarms查看告警信息是否正确
    code = '0x01020042'
    description = 'A disk fault has occurred !!'
    event_common.check_alarms_result(code, description)

    # 5> 将磁盘重新插入
    '''不断检查坏对象是否修复'''
    count = 0
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 60 seconds")
        time.sleep(60)
        if common.check_badjobnr():
            break

    # 恢复环境
    ''' 等待重建完成'''
    start_time = time.time()
    while True:
        if common.check_rebuild_job() is False:
            log.info('rebuild job finish!!!')
            break
        time.sleep(20)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('rebuild job exist %dh:%dm:%ds' % (h, m, s))

    """插入磁盘"""
    make_fault.insert_disk(fault_node_ip, fault_disk_physical_id, fault_disk_usage)

    log.info('wait 60s')
    time.sleep(60)

    """删除待移除磁盘"""
    rc, stdout = ob_disk.remove_disks(fault_disk_id)
    common.judge_rc(rc, 0, "remove disk failed")

    log.info('remove disk please wait 60s')
    time.sleep(60)

    """加入磁盘,并且加入存储池"""
    ob_disk.add_disks(fault_node_id, fault_disk_uuid, fault_disk_usage)
    fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)
    ob_storage_pool.expand_storage_pool(storage_pool_id, fault_disk_id_new)

    '''将等待时间的参数修改回来'''
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '3600000')


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

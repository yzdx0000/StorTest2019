
# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import snap_common
import log
import tool_use
import prepare_clean
import make_fault

####################################################################################
#
# author:梁晓昱
# date 2018-07-17
# @summary：
#      随机两个节点，每个节点选一块数据盘，进行拔盘操作，被动重建完成后将磁盘插回（参考1node.py，构建字典列表存放节点和磁盘）
# @steps:
#    1、部署3节点集群，配比4 2 1；
#    2、使用iozone创建多个文件；
#    3、vdbench创建数据过程中，拔出一个节点的两块数据盘；
#    4、不等被动重建完成后，将磁盘插回；
#
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
MINI_TRUE_PATH = os.path.join(prepare_clean.MINICASE_PATH, FILE_NAME)      # /mnt/volume1/mini_case/3_0015_truncate_test

NODE_DISK_NUM = 2     # 一共有两个点、两个盘


def pullout_disks(node_disk):
    """
    拔出某ip上的数据盘
    :param node_disk:
    :return:
    """
    log.info('waiting for 10s')
    time.sleep(10)
    for disk_info in node_disk:
        make_fault.pullout_disk(disk_info['node_ip'], disk_info['phyid'], disk_info['usage'])
        time.sleep(30)

    time.sleep(10)
    return


def insert_disks(node_disk):
    """
    传入某ip上的数据盘
    :param node_disk:
    :return:
    """
    log.info('waiting for 10s')
    time.sleep(10)
    for disk_info in node_disk:
        make_fault.insert_disk(disk_info['node_ip'], disk_info['phyid'], disk_info['usage'])
        time.sleep(30)
    return


def case():
    """更新磁盘重建的等待时间"""
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '18000000')

    '''添加文件'''
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, str(i))
        cmd = ("iozone -s 1m -i 0 -f %s -w" % test_file)
        rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
        common.judge_rc(rc, 0, 'iozone %s' % test_file)

    ''' 
    随机选取集群内的一个节点，获取节点的数据盘的物理id；
    获取集群内所有节点的id——>确定节点id,再确定节点上选取的硬盘id；
    '''
    ob_node = common.Node()
    ob_disk = common.Disk()
    node_id_lst = ob_node.get_nodes_id()

    # 提前赋值，仅为减少不安全提示
    node_disk_dic_lst = []
    disk_count = 0
    node_id_choose_cmp = 0
    '''
    NODE_DISK_NUM选定的磁盘数大于获得的磁盘列表成员数时，继续while循环取盘；
    否则，完成选盘；
    '''

    while NODE_DISK_NUM > len(node_disk_dic_lst):
        '''
        随机选节点；
        disk_count为0，通过random赋初值；
        '''
        if 0 == disk_count:
            node_id_choose = random.choice(node_id_lst)
            node_id_choose_cmp = node_id_choose
        else:
            node_id_choose = random.choice(node_id_lst)
            '''
            disk_count不为0：再次选盘；
            比较本次所选磁盘与首次选盘是否相同;相同则继续随机选盘,直至不同
            '''
            while node_id_choose_cmp == node_id_choose:
                node_id_choose = random.choice(node_id_lst)

        share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(node_id_choose)
        node_disk_name_choose = random.choice(monopoly_disk_names)

        # node_disk_dic重新分配内存，才能append新的对象（值）
        node_disk_dic = {}
        node_disk_dic['node_id'] = node_id_choose

        node_disk_dic['disk_name'] = node_disk_name_choose
        node_disk_dic['disk_id'] = ob_disk.get_diskid_by_name(node_id_choose, node_disk_name_choose)
        node_disk_dic['uuid'] = ob_disk.get_disk_uuid_by_name(node_id_choose, node_disk_name_choose)
        node_disk_dic['usage'] = ob_disk.get_disk_usage_by_name(node_id_choose, node_disk_name_choose)
        node_disk_dic['storage_pool'] = ob_disk.get_storage_pool_id_by_diskid(node_id_choose, node_disk_dic['disk_id'])
        node_disk_dic['node_ip'] = ob_node.get_node_ip_by_id(node_id_choose)
        node_disk_dic['phyid'] = ob_disk.get_physicalid_by_name(node_disk_dic['node_ip'], node_disk_name_choose)

        node_disk_dic_lst.append(node_disk_dic)

        disk_count += 1

        log.info("The %d time node_id_choose:%d\n" % (disk_count, node_id_choose))

    log.info("FINISH:node_disk choosed:\n%s" % node_disk_dic_lst)

    '''随机拔除两个节点的数据盘 '''
    p1 = Process(target=tool_use.vdbench_run,
                 args=(MINI_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2),
                 kwargs={'run_create': True, 'run_check_write': True})
    p2 = Process(target=pullout_disks, args=(node_disk_dic_lst,))
    p1.start()
    time.sleep(10)
    p2.start()

    p1.join()
    time.sleep(1)
    p2.join()

    # 4> 将磁盘插回；添加孤立状态的磁盘
    log.info('wait 60s:after join process')
    time.sleep(60)

    """将磁盘重新插入"""
    insert_disks(node_disk_dic_lst)
    log.info('wait 60s:insert disks')
    time.sleep(60)

    '''再跑检查数据的正确性'''
    tool_use.vdbench_run(MINI_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_check=True)

    '''检查系统'''
    common.ckeck_system()
    log.info("ckerebuild job existck_system finished")

    common.judge_rc(p1.exitcode, 0, 'vdbench')
    log.info("case succeed!")
    return


def main():
    prepare_clean.minicase_test_prepare(FILE_NAME)
    case()
    prepare_clean.minicase_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
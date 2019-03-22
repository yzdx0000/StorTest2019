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

"""
 author:梁晓昱
 date 2018-07-17
@summary：
      随机两个节点，每个节点选一块数据盘，进行拔盘操作，被动重建完成后将磁盘插回（参考1node.py，构建字典列表存放节点和磁盘）
@steps:
    1、部署3节点集群，配比4 2 1；
    2、使用iozone创建多个文件；
    3、vdbench创建数据过程中，拔出一个节点的两块数据盘；
    4、被动重建完成后，将磁盘插回；
    5、恢复等待重建的时间，清理数据；
@changelog：
    0728:PEP8规范修改；注意配置文件中不能有相同IP的客户端
    0804：两个随机节点的选取实现改用random已有的方法
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
MINI_TRUE_PATH = os.path.join(prepare_clean.MINICASE_PATH, FILE_NAME)     # /mnt/volume1/mini_case/3_0015_truncate_test

NODE_DISK_NUM = 2


def pullout_disks(node_disk):
    """
    author:LiangXiaoyu
    func:将硬盘列表的硬盘拔出
    :param node_disk: 已经确定的硬盘列表，在此例中为两个节点各选一块盘
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
    author:LiangXiaoyu
    func:将硬盘列表的硬盘插入
    :param node_disk: 已经确定的硬盘列表，在此例中为两个节点各选一块盘
    :return:
    """
    log.info('waiting for 10s')
    time.sleep(10)
    for disk_info in node_disk:
        make_fault.insert_disk(disk_info['node_ip'], disk_info['phyid'], disk_info['usage'])
        time.sleep(30)
    return


def case():
    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')
    """使用iozone创建多个文件"""
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, '%d' % i)
        cmd = ("iozone -s 1m -i 0 -f %s -w" % test_file)
        rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
        common.judge_rc(rc, 0, 'iozone %s' % test_file)

    ''' 
    随机选取集群内的一个节点，获取节点的数据盘的物理id；
    获取集群内所有节点的id——>确定节点id,再确定节点上选取的硬盘id；
    '''
    ob_node = common.Node()
    ob_disk = common.Disk()
    ob_storage_pool = common.Storagepool()
    node_id_lst = ob_node.get_nodes_id()

    # 提前赋值，减少if分支中的不安全提示
    node_disk_dic_lst = []
    disk_count = 0

    """
    NODE_DISK_NUM选定的磁盘数大于获得的磁盘列表成员数时，继续while循环取盘；
    否则，完成选盘；
    """
    node_id_choosed_lst = random.sample(node_id_lst, 2)
    while NODE_DISK_NUM > len(node_disk_dic_lst):
        """
        选节点；
        disk_count为0，为random选出的两节点列表赋值，每次+1；
        """
        node_id_choose = node_id_choosed_lst[disk_count]
        share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(node_id_choose)
        node_disk_name_choose = random.choice(monopoly_disk_names)
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

    """随机拔除两个节点的数据盘"""
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

    # 4> 被动重建完成后，将磁盘插回；删除僵尸状态的磁盘，并再次添加
    log.info('wait 90s:after join process')
    time.sleep(90)

    """不断检查重建任务是否存在"""
    start_time = time.time()
    while True:
        if False is common.check_rebuild_job():
            log.info('rebuild job finish!!!')
            break
        time.sleep(20)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('rebuild job exist %dh:%dm:%ds' % (h, m, s))
    """将磁盘重新插入"""
    insert_disks(node_disk_dic_lst)
    log.info('wait 60s:insert disks')
    time.sleep(60)

    common.update_param('MGR', 'disk_isolate2rebuild_timeout', '3600000')

    """删、加磁盘"""
    for k in range(len(node_disk_dic_lst)):
        ob_disk.remove_disks(node_disk_dic_lst[k]['disk_id'])
        log.info('wait 180s:remove disks')
        time.sleep(180)
        """加入磁盘,并且加入存储池"""
        rc, stdout = ob_disk.add_disks(node_disk_dic_lst[k]['node_id'], node_disk_dic_lst[k]['uuid'], node_disk_dic_lst[k]['usage'])
        common.judge_rc(rc, 0, 'add_disks failed')
        fault_disk_id_new = ob_disk.get_disk_id_by_uuid(node_disk_dic_lst[k]['node_id'], node_disk_dic_lst[k]['uuid'])
        rc, stdout = ob_storage_pool.expand_storage_pool(node_disk_dic_lst[k]['storage_pool'], fault_disk_id_new)
        common.judge_rc(rc, 0, 'expand_storage_pool failed')

    """不断检查坏对象是否修复"""
    count = 0
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 60 seconds")
        time.sleep(60)
        if True is common.check_badjobnr():
            log.info("check badjobnr finished")
            break

    """再跑检查数据的正确性"""
    tool_use.vdbench_run(MINI_TRUE_PATH, snap_common.CLIENT_IP_1,
                         snap_common.CLIENT_IP_2, run_check=True)

    """检查系统状态"""
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
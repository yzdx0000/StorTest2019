# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time

import utils_path
import common
import snap_common
import log
import make_fault
import prepare_clean

####################################################################################
#
# Author: liyao
# date 2018-04-20
# @summary：
#    创建嵌套目录快照，目录内容修改过程中，断掉主lmos节点的数据网
# @steps:
#    1、部署3节点集群，配比4 2 1；
#    2、创建深度为10的目录，每层创建一个快照（每层都有文件）；
#    3、修改所有文件的内容时，断掉非lmos的数据网；
#    4、到目录/mnt/parastor/.snapshot下检查各个快照的数据的正确性；
#    5、删除快照；
#    6、检查是否有快照路径入口；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/liyao/snap/snap_13_1_3_10
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_1_3_10


def file_revise():
    """ 修改各层目录下的文件"""
    snap_true_path_mem = SNAP_TRUE_PATH
    for i in range(10):
        snap_true_path_mem = os.path.join(snap_true_path_mem, str(i))
        file_name = os.path.join(snap_true_path_mem, 'snap_file')
        cmd = 'echo %s > %s' % (str(i) * 20, file_name)
        common.run_command(snap_common.CLIENT_IP_1, cmd)
    return


def case():
    """2> 创建深度为10的目录，各层都有文件；每层创建一个快照"""
    snap_true_path_mem = SNAP_TRUE_PATH
    create_snap_path_mem = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH

    md5_list = []
    for i in range(10):
        """创建目录"""
        snap_true_path_mem = os.path.join(snap_true_path_mem, str(i))
        file_name = os.path.join(snap_true_path_mem, 'snap_file')
        cmd = 'mkdir %s' % snap_true_path_mem
        common.run_command(snap_common.CLIENT_IP_1, cmd)
        cmd = 'echo %s > %s' % (str(i) * 6, file_name)
        common.run_command(snap_common.CLIENT_IP_1, cmd)
        create_snap_path_mem = os.path.join(create_snap_path_mem, str(i))

        """获取md5码"""
        rc, md5sum = snap_common.get_file_md5(snap_common.CLIENT_IP_2, file_name)
        md5_list.append(md5sum)

        """创建快照"""
        snap_name = FILE_NAME + '_snapshot_%d' % i
        rc, stdout = snap_common.create_snapshot(snap_name, create_snap_path_mem)
        if 0 != rc:
            log.error('create_snapshot %s failed!!!' % snap_name)
            raise Exception('create_snapshot %s failed!!!' % snap_name)

    """3> 修改所有文件的内容时，断掉非主lmos的数据网"""
    """获取lmos节点id"""
    lmos_node_id = snap_common.get_lmos_node_id()
    node_obj = common.Node()
    sys_node_id_lst = node_obj.get_nodes_id()
    fault_node_id = None
    for node_id in sys_node_id_lst:
        if node_id != int(lmos_node_id):
            fault_node_id = node_id
            break

    fault_node_ip = node_obj.get_node_ip_by_id(fault_node_id)
    eth_list, data_ip_list, ip_mask_lst = node_obj.get_node_eth(fault_node_id)

    p1 = Process(target=file_revise)
    p2 = Process(target=make_fault.down_eth, args=(fault_node_ip, eth_list))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    if p1.exitcode != 0:
        raise Exception("file revision failed!!!!!!")

    """4> 到目录/mnt/parastor/.snapshot下检查各个快照的数据的正确性"""
    md5_check_list = []
    for i in range(10):
        snap_name = FILE_NAME + '_snapshot_%d' % i
        snap_file = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name, 'snap_file')
        """获取md5码"""
        rc, md5sum = snap_common.get_file_md5(snap_common.CLIENT_IP_2, snap_file)
        md5_check_list.append(md5sum)

    md5_list_str = 'source_md5_list: ', md5_list
    md5_check_list_str = 'snap_md5_list: ', md5_check_list
    log.info(md5_list_str)
    log.info(md5_check_list_str)
    if md5_list != md5_check_list:
        log.error('snap file is not right!!!')
        raise Exception('snap file is not right!!!')
    start_time = time.time()
    while True:
        time.sleep(20)
        if common.check_ping(fault_node_ip):
            break
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('node %s cannot ping pass %dh:%dm:%ds' % (fault_node_ip, h, m, s))
    log.info('wait 20s')
    time.sleep(20)
    """恢复网络"""
    make_fault.up_eth(fault_node_ip, eth_list, ip_mask_lst)

    """检查数据是否完全修复"""
    log.info('waiting for 120s')
    time.sleep(120)
    count = 0
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 60 seconds")
        time.sleep(60)
        if common.check_badjobnr():
            break

    """5> 删除快照"""
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (FILE_NAME))
        raise Exception('%s delete snapshot failed!!!' % (FILE_NAME))
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
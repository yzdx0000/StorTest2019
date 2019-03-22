# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time

import utils_path
import log
import common
import tool_use
import make_fault
import snap_common
import prepare_clean


####################################################################################
#
# Author: baorb
# date 2018-01-19
# @summary：
#    kill非主lmos节点的oPara，读取快照文件
# @steps:
#    1、部署3个客户端；
#    2、客户端1在目录/mnt/parastor/snap/下执行vdbench 00脚本（创建文件）；
#    3、对目录/mnt/parastor/snap/创建快照a1；
#    4、客户端2在目录/mnt/parastor/snap/下执行vdbench 01（修改文件数据）；
#    5、客户端2在目录/mnt/parastor/.snapshot/下执行vdbench 02脚本（校验数据正确性），在读的过程中kill非主lmos节点的oPara；
#    6、删除快照；
#    7、3个客户端检查是否有快照路径入口；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_0_0


def kill_lmos_opara():
    # 获取所有节点的id
    node_info = common.Node()
    node_ip_lst = node_info.get_nodes_id()
    # 获取lmos节点id
    lmos_node_id = snap_common.get_lmos_node_id()

    for node_id in node_ip_lst:
        if int(node_id) != int(lmos_node_id):
            break

    node_ip = node_info.get_node_ip_by_id(int(node_id))

    time.sleep(10)
    while True:
        make_fault.kill_process(node_ip, 'oPara')
        time.sleep(120)


def case():
    # 2> 运行00脚本
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_create=True)

    # 3> 对目录创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 4> 运行01脚本
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_write=True)

    # 运行02脚本
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)

    # 5> 并行02脚本校验数据，kill非主lmos节点的oPara
    p1 = Process(target=tool_use.vdbench_run,
                 args=(snap_path, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2),
                 kwargs={'run_check': True})
    p2 = Process(target=kill_lmos_opara)

    p1.start()
    p2.start()

    p1.join()
    p2.terminate()
    p2.join()

    if p1.exitcode != 0:
        raise Exception("vdbench is failed!!!!!!")

    # 6> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (path))
        raise Exception('%s delete snapshot failed!!!' % (path))

    time.sleep(10)

    # 7> 3个客户端检查快照路径入口是否存在
    snap_common.check_snap_entry(snap_path)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
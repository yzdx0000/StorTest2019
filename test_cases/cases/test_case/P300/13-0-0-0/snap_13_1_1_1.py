# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time

import utils_path
import common
import snap_common
import log
import tool_use
import prepare_clean
import make_fault


####################################################################################
#
# Author: baorb
# date 2018-01-19
# @summary：
#    创建快照时，kill 主lmos节点的oPara
# @steps:
#    1、执行00 vdbench脚本创建数据；
#    2、对目录创建快照，同时kill 非主lmos节点的oPara
#    3、运行01 vdbench脚本修改数据；
#    4、运行02 vdbench脚本校验数据；
#    5、删除快照；
#    6、检查快照路径入口是否存在；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0


def kill_lmos_opara():
    # 获取lmos节点id
    node_id = snap_common.get_lmos_node_id()

    node_info = common.Node()
    node_ip = node_info.get_node_ip_by_id(int(node_id))

    time.sleep(1)
    make_fault.kill_process(node_ip, 'oPara')


def case():
    # 1> 运行00脚本
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_create=True)

    #cmd1 = 'scp -r /tmp/vdb_control.file root@%s:/tmp' % snap_common.CLIENT_IP_2
    #cmd2 = 'scp -r /tmp/vdb_control.file root@%s:/tmp' % snap_common.CLIENT_IP_3
    #common.run_command(snap_common.CLIENT_IP_1, cmd1)
    #common.run_command(snap_common.CLIENT_IP_1, cmd2)

    # 对目录创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH

    def _create_snapshot(snap_name, path):
        rc, stdout = snap_common.create_snapshot(snap_name, path)
        if 0 != rc:
            log.error('create_snapshot %s failed!!!' % snap_name)
            raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 2> 并行创建快照，kill住lmos节点的oPara
    p1 = Process(target=_create_snapshot, args=(snap_name, path,))
    p2 = Process(target=kill_lmos_opara)

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    if p1.exitcode != 0:
        raise Exception("vdbench is failed!!!!!!")

    # 3> 运行01脚本
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_write=True)

    # 4> 运行02脚本
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    tool_use.vdbench_run(snap_path, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_check=True)

    # 5> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (path))
        raise Exception('%s delete snapshot failed!!!' % (path))

    time.sleep(10)

    # 6> 3个客户端检查快照路径入口是否存在
    snap_common.check_snap_entry(snap_path)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
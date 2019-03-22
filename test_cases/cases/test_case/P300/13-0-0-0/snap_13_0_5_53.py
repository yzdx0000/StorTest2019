# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time

import utils_path
import common
import snap_common
import log
import prepare_clean
import tool_use

####################################################################################
#
# Author: liyao
# date 2018-06-27
# @summary：
#    对目录创建快照a2过程中，revert快照a1
# @steps:
#    1、部署3个客户端；
#    2、客户端1在目录/mnt/parastor/snap/下执行vdbench 00脚本（创建文件）；
#    3、对目录/mnt/parastor/snap/创建快照a1；
#    4、客户端2在目录/mnt/parastor/snap/下执行vdbench（修改文件数据）；
#    5、revert快照a1过程中创建快照a2；
#    6、删除快照；
#    7、3个客户端检查是否有快照路径入口；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_5_52
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_5_52


def case():
    # 2> 运行00脚本
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_create=True)

    #cmd1 = 'scp -r /tmp/vdb_control.file root@%s:/tmp' % snap_common.CLIENT_IP_2
    #cmd2 = 'scp -r /tmp/vdb_control.file root@%s:/tmp' % snap_common.CLIENT_IP_3
    #common.run_command(snap_common.CLIENT_IP_1, cmd1)
    #common.run_command(snap_common.CLIENT_IP_1, cmd2)

    # 3> 对目录创建第一个快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 4> 使用vdbench修改数据
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_write=True)
    log.info('waiting for 10s')
    time.sleep(10)

    # 4> revert第一个快照过程中创建第二个快照
    snap_name_again = FILE_NAME + '_snapshot2'
    p1 = Process(target=snap_common.revert_snapshot_by_name, args=(snap_name,))
    p2 = Process(target=snap_common.create_snapshot, args=(snap_name_again, path,))

    p1.start()
    log.info('waiting for 5s')
    time.sleep(5)
    p2.start()

    p1.join()
    p2.join()

    if p1.exitcode != 0:
        raise Exception("vdbench is failed!!!!!!")

    # 5> 运行02脚本
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_check=True)

    # 6> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (path))
        raise Exception('%s delete snapshot failed!!!' % (path))

    time.sleep(10)

    # 7> 3个客户端检查快照路径入口是否存在
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    snap_common.check_snap_entry(snap_path)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

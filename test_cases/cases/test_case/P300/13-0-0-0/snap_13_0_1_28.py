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
# date 2018-07-04
# @summary：
#    快照修改过程中，校验隐藏目录下的快照文件
# @steps:
#    1、部署3个客户端；
#    2、在/mnt/volume1/snap/snap_13_0_1_28/下使用vdbench00脚本创建数据
#    3、对目录/mnt/volume1/snap/snap_13_0_1_28/创建快照
#    4、修改源文件，同时对隐藏目录/mnt/volume1/.snapshot/下的快照文件进行校验
#    5、清理环境，删除快照及数据
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_1_28
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_1_28


def case():
    obj_vdbench = tool_use.Vdbenchrun()
    obj_vdbench.run_create(SNAP_TRUE_PATH, SNAP_TRUE_PATH, snap_common.CLIENT_IP_1)

    cmd1 = 'scp -r /tmp/vdb_control.file root@%s:/tmp' % snap_common.CLIENT_IP_2
    cmd2 = 'scp -r /tmp/vdb_control.file root@%s:/tmp' % snap_common.CLIENT_IP_3
    common.run_command(snap_common.CLIENT_IP_1, cmd1)
    common.run_command(snap_common.CLIENT_IP_1, cmd2)

    # 3> 对目录创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 4> 修改源文件，同时校验隐藏目录下的快照文件
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    p1 = Process(target=obj_vdbench.run_write,
                 args=(SNAP_TRUE_PATH, snap_common.CLIENT_IP_2))
    p2 = Process(target=obj_vdbench.run_check,
                 args=(snap_path, SNAP_TRUE_PATH, snap_common.CLIENT_IP_3))

    p1.start()
    time.sleep(10)
    p2.start()

    p1.join()
    p2.join()

    common.judge_rc(p1.exitcode, 0, 'dbench run_write')
    common.judge_rc(p2.exitcode, 0, 'dbench run_check')

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
# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import tool_use
import get_config
import prepare_clean

####################################################################################
#
# Author: baorb
# date 2018-01-19
# @summary：
#    快照revert过程中，创建快照。
# @steps:
#    1、/mnt/parastor/snap/运行00vdbench创建数据；
#    2、对目录创建快照a1；
#    3、/mnt/parastor/snap/运行01vdbench修改数据；
#    4、对快照进行revert，在revert过程中对/mnt/parastor/snap/创建快照a2；
#    5、查询快照(使用pscli --command=get_snapshot)；
#    6、到/mnt/parastor/.snapshot/观察快照a2的内容；
#    7、删除快照；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                     # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)                 # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)      # /snap/snap_13_0_0_0


def case():
    # 1> 运行00脚本
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_create=True)

    # 2> 创建快照
    snap_name_1 = FILE_NAME + '_snapshot_1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name_1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name_1)
        raise Exception('create_snapshot %s failed!!!' % snap_name_1)

    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name_1)

    # 3> 运行01脚本
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_write=True)

    # 4> 对快照进行revert同时创建快照
    snap_name_2 = FILE_NAME + '_snapshot_2'
    snap_info = snap_common.get_snapshot_by_name(snap_name_1)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name_1)
        raise Exception("revert snapshot %s failed!!!" % snap_name_1)
    rc, stdout = snap_common.create_snapshot(snap_name_2, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name_2)
        raise Exception('create_snapshot %s failed!!!' % snap_name_2)
    snap_common.check_revert_finished(snap_id)

    # 5> 查询快照a2是否创建成功
    snapshot1_info = snap_common.get_snapshot_by_name(snap_name_2)
    if -1 == snapshot1_info:
        log.error('snap %s is not exist!!!' % snap_name_2)
        raise Exception('snap %s is not exist!!!' % snap_name_2)

    # 6> 执行02脚本
    tool_use.vdbench_run(snap_path, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_check=True)

    # 7> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('delete_snapshot %s failed!!!' % FILE_NAME)
        raise Exception('delete_snapshot %s failed!!!' % FILE_NAME)


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
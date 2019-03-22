# -*-coding:utf-8 -*
import os
import time
import json

import utils_path
import common
import snap_common
import log
import prepare_clean

####################################################################################
#
# Author: baorb
# date 2018-01-19
# @summary：
#    对快照入口路径创建快照。
# @steps:
#    1、创建快照a1；
#    2、对/mnt/volume1/.snapshot创建快照a2；
#    3、对/mnt/volume1/.snapshot/a1创建快照a3；
#    4、删除快照a1
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_0_0


def case():
    # 1> 创建快照1
    name1 = FILE_NAME + '_snapshot_1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % name1)
        raise Exception('create_snapshot %s failed!!!' % name1)

    # 2> 创建快照2
    name2 = FILE_NAME + '_snapshot_2'
    path = snap_common.VOLUME_NAME + ':/' + snap_common.SNAPSHOT_PAHT
    rc, stdout = snap_common.create_snapshot(name2, path)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != 'Item is not exist':
        log.error('create_snapshot %s failed!!!' % name2)
        raise Exception('create_snapshot %s failed!!!' % name2)

    # 3> 创建快照3
    name3 = FILE_NAME + '_snapshot_3'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(snap_common.SNAPSHOT_PAHT, name1)
    rc, stdout = snap_common.create_snapshot(name3, path)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != 'Item is not exist':
        log.error('create_snapshot %s failed!!!' % name3)
        raise Exception('create_snapshot %s failed!!!' % name3)

    # 4> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete failed!!!' % (FILE_NAME))
        raise Exception('%s delete failed!!!' % (FILE_NAME))

    time.sleep(10)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
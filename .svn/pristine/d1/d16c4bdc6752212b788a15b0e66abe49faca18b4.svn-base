# -*-coding:utf-8 -*
import os
import time
import json

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean

####################################################################################
#
# Author: baorb
# date 2018-01-19
# @summary：
#    不断循环创建快照。
# @steps:
#    1、对一个目录不间断的创建快照，直到1000个；
#
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                     # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)                 # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)      # /snap/snap_13_0_0_0


def case():
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    for i in range(1000):
        name = FILE_NAME + '_snapshot_%d' % i
        rc, stdout = snap_common.create_snapshot(name, path)
        if 0 != rc:
            log.error('create_snapshot %s failed!!!' % name)
            raise Exception('create_snapshot %s failed!!!' % name)

    log.info('wait 10')
    time.sleep(10)

    snap_num = snap_common.get_snapshot_num()
    common.judge_rc(snap_num, 1000, "snapshot num is not 1000, is %d" % snap_num)

    """删除快照"""
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('delete_snapshot %s failed!!!' % FILE_NAME)
        raise Exception('delete_snapshot %s failed!!!' % FILE_NAME)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

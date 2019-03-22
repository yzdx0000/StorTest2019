# -*-coding:utf-8 -*
from multiprocessing import Process
import os

import utils_path
import common
import snap_common
import log
import prepare_clean

####################################################################################
#
# Author: baorb
# Date: 2018-07-04
# @summary：
#    同时对一个目录创建三个快照
# @steps:
#    1、对一个目录创建三个快照；
#    2、查询三个快照存在；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_1_27
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_1_27


def create_snap(name, path):
    rc, stdout = snap_common.create_snapshot(name, path)
    common.judge_rc(rc, 0, 'create_snapshot %s' % name)


def case():
    log.info("同时创建三个快照")
    snap_name_1 = FILE_NAME + '_snapshot_1'
    snap_name_2 = FILE_NAME + '_snapshot_2'
    snap_name_3 = FILE_NAME + '_snapshot_3'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    p1 = Process(target=create_snap, args=(snap_name_1, path))
    p2 = Process(target=create_snap, args=(snap_name_2, path))
    p3 = Process(target=create_snap, args=(snap_name_3, path))

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()

    common.judge_rc(p1.exitcode, 0, 'create snapshot %s' % snap_name_1)
    common.judge_rc(p2.exitcode, 0, 'create snapshot %s' % snap_name_2)
    common.judge_rc(p3.exitcode, 0, 'create snapshot %s' % snap_name_3)

    log.info("检查三个快照")
    rc, snap_lst = snap_common.get_snapshot_ids_by_name(snap_name_1)
    common.judge_rc(rc, 0, 'get snap %s' % snap_name_1)
    rc, snap_lst = snap_common.get_snapshot_ids_by_name(snap_name_2)
    common.judge_rc(rc, 0, 'get snap %s' % snap_name_2)
    rc, snap_lst = snap_common.get_snapshot_ids_by_name(snap_name_3)
    common.judge_rc(rc, 0, 'get snap %s' % snap_name_3)


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
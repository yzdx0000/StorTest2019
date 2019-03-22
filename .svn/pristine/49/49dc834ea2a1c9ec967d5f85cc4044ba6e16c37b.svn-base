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
#    对同一个目录重复创建删除快照50次
# @steps:
#    1、对同一个目录重复创建删除快照50次；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_1_29
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_1_29


def case():
    log.info("对一个目录重复创建删除快照50次")
    snap_name_1 = FILE_NAME + '_snapshot_1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    for i in range(50):
        """创建快照"""
        rc, stdout = snap_common.create_snapshot(snap_name_1, path)
        common.judge_rc(rc, 0, '%d time create snap %s' % (i, snap_name_1))
        """删除快照"""
        rc, stdout = snap_common.delete_snapshot_by_name(snap_name_1)
        common.judge_rc(rc, 0, '%d time delete snap %s' % (i, snap_name_1))


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
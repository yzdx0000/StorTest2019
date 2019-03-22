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
# Author: liyao
# date 2018-05-03
# @summary：
#    文件修改时对其创建快照
# @steps:
#    1、创建文件/mnt/parastor/snap/test_file1(64m)；
#    2、不断对文件进行写；
#    3、对文件创建快照；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/liyao/snap/snap_13_0_1_8
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_1_8


def file_revision(file_path):
    '''连续修改文件数据'''
    i = 1
    while True:
        i = i + 1
        cmd = "echo %d >> %s" % (i, file_path)
        common.run_command(snap_common.CLIENT_IP_1, cmd)


def snapshot_create(snap_name, path):
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)
    return


def case():
    # 1> 创建文件/mnt/liyao/snap/snap_13_0_1_8/test_file1
    test_file1 = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    cmd = 'dd if=%s of=%s bs=1M count=64' % (snap_common.get_system_disk(snap_common.CLIENT_IP_1), test_file1)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 2> 对文件创建快照并行修改文件
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH

    p1 = Process(target=snapshot_create, args=(snap_name, path,))
    p2 = Process(target=file_revision, args=(test_file1,))

    p1.start()
    p2.start()

    p1.join()
    p2.terminate()
    p2.join()

    if p1.exitcode != 0:
        raise Exception("snapshot %s is not created!!!!!!" % snap_name)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean

####################################################################################
#
# Author: liyao
# date 2018-05-03
# @summary：
#    源文件修改过程中，删除快照
# @steps:
#    1、创建文件/mnt/parastor/snap/test_file1(64m),对文件创建快照；
#    2、对文件进行写，写的过程中删除快照；
#    3、查询快照(使用pscli --command=get_snapshot)；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/liyao/snap/snap_13_0_1_16
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_1_16


def file_revision(file_path):
    '''连续修改文件数据'''
    i = 1
    while True:
        i = i + 1
        cmd = "echo %d >> %s" % (i, file_path)
        common.run_command(snap_common.CLIENT_IP_1, cmd)


def snapshot_delete(path):
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (path))
        raise Exception('%s delete snapshot failed!!!' % (path))
    return


def case():
    # 1> 创建文件/mnt/liyao/snap/snap_13_0_1_8/test_file1，并对文件创建快照
    test_file1 = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    cmd = 'dd if=%s of=%s bs=1M count=64' % (snap_common.get_system_disk(snap_common.CLIENT_IP_1), test_file1)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    snap_common.create_snapshot(snap_name, path)

    # 2> 修改文件过程中删除快照
    p1 = Process(target=snapshot_delete, args=(path,))
    p2 = Process(target=file_revision, args=(test_file1,))

    p1.start()
    p2.start()

    p1.join()
    p2.terminate()
    p2.join()

    if p1.exitcode != 0:
        raise Exception("snapshot %s is not deleted!!!!!!" % snap_name)

    # 3> 查询快照
    log.info('waiting for 20s')
    time.sleep(20)
    snapshot1_info = snap_common.get_snapshot_by_name(snap_name)
    if -1 != snapshot1_info and snapshot1_info['state'] != 'SNAPSHOT_DELETING':
        log.error('snap %s is not deleted!!!' % snap_name)
        raise Exception('snap %s is not deleted!!!' % snap_name)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
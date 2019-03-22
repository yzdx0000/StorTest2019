# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import prepare_clean

####################################################################################
#
# Author: liyao
# date 2018-04-26
# @summary：
#    创建单个文件快照后，删除源文件，查看快照空间统计的正确性。
# @steps:
#    1、部署3个客户端；
#    2、/mnt/liyao/snap下创建大小为20M的非空文件test_file1；
#    3、对目录创建快照；
#    4、删除源文件；
#    5、查看快照空间统计的正确性；
#    6、删除快照；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_3_5
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_3_5


def case():
    '''2>创建文件'''
    file_path = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    cmd = 'dd if=/dev/sda1 of=%s bs=1M count=20' % file_path
    common.run_command(snap_common.SYSTEM_IP, cmd)
    file_size = 20 * 1024 * 1024

    '''3> 创建快照'''
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    '''4> 删除文件'''
    common.rm_exe(snap_common.SYSTEM_IP, file_path)
    log.info('waiting for 150s')
    time.sleep(150)

    '''5>查看快照空间统计的正确性'''
    snapshot = snap_common.get_snapshot_by_name(snap_name)
    actual_snap_size = int(snapshot['size'])
    expect_snap_size = file_size

    '''判断空间统计的正确性'''
    log.info('actual_snap_size = %d' % actual_snap_size)
    log.info('expect_snap_size = %d' % expect_snap_size)
    if actual_snap_size == expect_snap_size:
        log.info('snap size statistic is correct.')
    else:
        log.error('snap size statistic is wrong !!!')
        raise Exception('snap size statistic is wrong !!!')

    '''6>删除快照'''
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete failed!!!' % (path))
        raise Exception('%s delete failed!!!' % (path))
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
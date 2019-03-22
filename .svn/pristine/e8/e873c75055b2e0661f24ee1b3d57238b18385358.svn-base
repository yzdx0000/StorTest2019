# -*-coding:utf-8 -*
import os

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
#    嵌套目录下创建多个快照。
# @steps:
#    1、创建目录/mnt/parastor/snap/和/mnt/parastor/snap/test_dir1/，创建文件/mnt/parastor/snap/test_file1；
#    2、对目录/mnt/parastor/snap/创建快照a1；
#    3、对目录/mnt/parastor/snap/test_dir1/创建快照a2；
#    4、对文件/mnt/parastor/snap/test_file1创建快照a3；
#    5、删除快照a1、a2、a3；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_0_0


def case():
    # 1> 创建子目录
    test_dir_1 = os.path.join(SNAP_TRUE_PATH, 'test_dir_1')
    cmd = 'mkdir %s' % test_dir_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建子文件
    test_file_1 = os.path.join(SNAP_TRUE_PATH, 'test_file_1')
    cmd = 'touch %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 2> 创建快照1
    name1 = FILE_NAME + '_snapshot1'
    path1 = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(name1, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % name1)
        raise Exception('create_snapshot %s failed!!!' % name1)

    # 3> 创建快照2
    name2 = FILE_NAME + '_snapshot2'
    path2 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_dir_1')
    rc, stdout = snap_common.create_snapshot(name2, path2)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % name2)
        raise Exception('create_snapshot %s failed!!!' % name2)

    # 4> 创建快照3
    name3 = FILE_NAME + '_snapshot3'
    path3 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file_1')
    rc, stdout = snap_common.create_snapshot(name3, path3)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % name3)
        raise Exception('create_snapshot %s failed!!!' % name3)

    # 5> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(CREATE_SNAP_PATH)
    if 0 != rc:
        log.error('%s delete failed!!!' % (CREATE_SNAP_PATH))
        raise Exception('%s delete failed!!!' % (CREATE_SNAP_PATH))
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
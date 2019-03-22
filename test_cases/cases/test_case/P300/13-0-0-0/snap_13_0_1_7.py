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
#    硬链接创建快照。
# @steps:
#    1、对文件/mnt/parastor/snap/test_file1创建硬链接/mnt/parastor/snap/test_file_hd(使用ln命令)；
#    2、对文件/mnt/parastor/snap/test_file1创建快照a1；
#    3、对硬链接/mnt/parastor/snap/test_file_hd创建快照a2；
#    4、查询快照；
#    5、删除快照；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_0_0


def case():
    # 创建子文件
    test_file_1 = os.path.join(SNAP_TRUE_PATH, 'test_file_1')
    cmd = 'touch %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 1> 创建硬链接
    cmd = 'ln %s %s/test_file_hd' % (test_file_1, SNAP_TRUE_PATH)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 2> 对文件创建快照
    name1 = FILE_NAME + '_snapshot1'
    path1 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file_1')
    rc, stdout = snap_common.create_snapshot(name1, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % name1)
        raise Exception('create_snapshot %s failed!!!' % name1)

    # 3> 对硬链接创建快照
    name2 = FILE_NAME + '_snapshot2'
    path2 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file_hd')
    rc, stdout = snap_common.create_snapshot(name2, path2)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % name2)
        raise Exception('create_snapshot %s failed!!!' % name2)

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
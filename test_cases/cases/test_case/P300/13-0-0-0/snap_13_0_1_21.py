# -*-coding:utf-8 -*
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
# Author: baorb
# date 2018-01-19
# @summary：
#    255层嵌套路径创建快照。
# @steps:
#    1、创建255层目录，每个目录都创建快照；
#    2、创建第256层目录，创建快照；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_0_0


def case():
    # 1> 创建255层目录，每个目录创建快照
    snap_true_path_mem = SNAP_TRUE_PATH
    create_snap_path_mem = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    for i in range(250):
        # 创建目录
        snap_true_path_mem = os.path.join(snap_true_path_mem, str(i))
        cmd = 'mkdir %s' % snap_true_path_mem
        common.run_command(snap_common.CLIENT_IP_1, cmd)
        create_snap_path_mem = os.path.join(create_snap_path_mem, str(i))
        # 创建快照
        for j in range(4):
            name = FILE_NAME + '_snapshot_%d_%d' % (i, j)
            rc, stdout = snap_common.create_snapshot(name, create_snap_path_mem)
            if 0 != rc:
                log.error('create_snapshot %s failed!!!' % name)
                raise Exception('create_snapshot %s failed!!!' % name)

    # 2> 创建1001个快照
    name = FILE_NAME + '_snapshot'
    rc, stdout = snap_common.create_snapshot(name, CREATE_SNAP_PATH)
    if 0 == rc:
        log.error('create_snapshot %s failed!!!' % name)
        raise Exception('create_snapshot %s failed!!!' % name)

    # 删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete failed!!!' % (FILE_NAME))
        raise Exception('%s delete failed!!!' % (FILE_NAME))
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
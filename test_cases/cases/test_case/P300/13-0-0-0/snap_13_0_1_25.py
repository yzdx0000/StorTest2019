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
# Author: baorb
# date 2018-01-19
# @summary：
#    文件名带特殊字符，对文件创建快照。
# @steps:
#    1、创建文件，文件名中包含特殊字符，创建快照a1；
#    2、创建文件，文件名中包含数字和中文字符，创建快照a2；
#    3、删除快照；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_0_0


def case():
    # 创建文件
    file_name1 = os.path.join(SNAP_TRUE_PATH, '@a#!$%^*-=_+?<>,.')
    cmd = 'touch %s' % file_name1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 1> 创建快照
    name1 = FILE_NAME + '_snapshot_1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, '@a#!$%^*-=_+?<>,.')
    rc, stdout = snap_common.create_snapshot(name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % name1)
        raise Exception('create_snapshot %s failed!!!' % name1)

    # 创建文件
    file_name2 = os.path.join(SNAP_TRUE_PATH, '测试文件123')
    cmd = 'touch %s' % file_name2
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 2> 创建快照
    name2 = FILE_NAME + '_snapshot_2'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, '测试文件123')
    rc, stdout = snap_common.create_snapshot(name2, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % name2)
        raise Exception('create_snapshot %s failed!!!' % name2)

    # 3> 删除快照
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
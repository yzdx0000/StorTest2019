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
#    特殊字符和名字长度检查。
# @steps:
#    1、对/mnt/parastor/snap/test文件创建快照，名字含有特殊字符(！~*%#^?.-_等)；
#    2、对/mnt/parastor/snap/test文件创建快照，名字长度超过32个字符；
#    3、对/mnt/parastor/snap/test文件创建快照，名字长度为31个字符；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_0_0


def case():
    # 1> 创建快照，含特殊字符
    name1 = FILE_NAME + '~!%?,.'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(name1, path)
    stdout = common.json_loads(stdout)
    if 14003 != stdout['err_no']:
        log.error('create_snapshot %s failed!!!' % name1)
        raise Exception('create_snapshot %s failed!!!' % name1)

    # 2> 创建快照，名字长度超过32个字符
    name_part = ''
    for i in range(0, 32-len(FILE_NAME)):
        name_part += 'a'
    name2 = FILE_NAME + name_part
    rc, stdout = snap_common.create_snapshot(name2, path)
    stdout = common.json_loads(stdout)
    if 14003 != stdout['err_no']:
        log.error('create_snapshot %s failed!!!' % name2)
        raise Exception('create_snapshot %s failed!!!' % name2)

    # 3> 创建快照，名字长度为31个字符
    name_part = ''
    for i in range(0, 31 - len(FILE_NAME)):
        name_part += 'a'
    name3 = FILE_NAME + name_part
    rc, stdout = snap_common.create_snapshot(name3, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % name3)
        raise Exception('create_snapshot %s failed!!!' % name3)

    # 6> 删除所有快照
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
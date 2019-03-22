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
#    对不存在的文件创建快照。
# @steps:
#    1、对不存在的文件创建快照；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_0_0


def case():
    # 1> 创建快照
    name = FILE_NAME + '_snapshot_1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file_1')
    rc, stdout = snap_common.create_snapshot(name, path)
    stdout = common.json_loads(stdout)
    if 'Item is not exist' != stdout['detail_err_msg']:
        log.error('create_snapshot %s failed!!!' % name)
        raise Exception('create_snapshot %s failed!!!' % name)


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
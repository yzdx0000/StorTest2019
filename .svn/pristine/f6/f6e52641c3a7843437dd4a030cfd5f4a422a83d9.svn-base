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
# Date: 2018-01-19
# @summary：
#    目录名带特殊字符，对目录创建快照。
# @steps:
#    1、创建目录，目录名中包含特殊字符，创建快照a1；
#    2、创建目录，目录名中包含数字和中文字符，创建快照a2；
#    3、删除快照；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/P300_696
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/P300_696


def case():
    log.info("创建名字带有中文的目录")
    path_name = os.path.join(SNAP_TRUE_PATH, '测试目录123')
    cmd = 'mkdir %s' % path_name
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    log.info("创建快照")
    name1 = FILE_NAME + '_snapshot_1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, '测试目录123')
    rc, stdout = snap_common.create_snapshot(name1, path)
    common.judge_rc(rc, 0, 'create_snapshot %s' % name1)

    log.info("查询快照信息是否正确")
    snap_info = snap_common.get_snapshot_by_name(name1)
    common.judge_rc_unequal(snap_info, -1, 'get snapshot')
    if snap_info['path'] != path:
        common.except_exit('snap path:%s  expect path:%s' % (snap_info['path'], path))

    log.info("删除快照")
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    common.judge_rc(rc, 0, '%s delete' % FILE_NAME)
    time.sleep(10)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
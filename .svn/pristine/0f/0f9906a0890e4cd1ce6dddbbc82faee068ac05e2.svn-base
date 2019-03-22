#-*-coding:utf-8 -*
import os
import time
import json

import utils_path
import common
import snap_common
import log
import prepare_clean

####################################################################################
#
# Author: baorb
# date 2018-01-19
#@summary：
#    父目录revert的过程中子目录revert
#@steps:
#    1、部署3个客户端；
#    2、创建目录/mnt/parastor/snap_parent/snap_child/，对目录/mnt/parastor/snap_parent/创建快照a1；
#    3、修改/mnt/parastor/snap_parent/snap_child/下的内容，对目录/mnt/parastor/snap_parent/snap_child/创建快照a2；
#    4、对快照a1 revert的同时，对快照a2 revert；
#    5、到目录/mnt/parastor/snap_parent/下观察内容；
#    6、删除快照；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0

def case():
    # 2> 创建目录
    test_dir_parent = os.path.join(SNAP_TRUE_PATH, 'snap_parent_dir')
    cmd = 'mkdir %s' % test_dir_parent
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    test_dir_child = os.path.join(test_dir_parent, 'snap_child_dir')
    cmd = 'mkdir %s' % test_dir_child
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建文件
    test_file = os.path.join(test_dir_child, 'snap_file_test')
    cmd = 'echo 111111 > %s' % test_file
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建快照a1
    snap_name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'snap_parent_dir')
    rc, stdout = snap_common.create_snapshot(snap_name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 3> 修改文件内容
    cmd = 'echo 222222 > %s' % test_file
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建快照a2
    snap_name2 = FILE_NAME + '_snapshot2'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'snap_parent_dir', 'snap_child_dir')
    rc, stdout = snap_common.create_snapshot(snap_name2, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name2)
        raise Exception('create_snapshot %s failed!!!' % snap_name2)

    # 4> 同时对快照1和2进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name1)
    snap_id1 = snap_info['id']
    snap_info = snap_common.get_snapshot_by_name(snap_name2)
    snap_id2 = snap_info['id']

    rc, stdout = snap_common.revert_snapshot_by_id(snap_id1)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name1)
        raise Exception("revert snapshot %s failed!!!" % snap_name1)

    rc, stdout = snap_common.revert_snapshot_by_id(snap_id2)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name2)
        raise Exception("revert snapshot %s failed!!!" % snap_name2)
    snap_common.check_revert_finished(snap_id1)
    snap_common.check_revert_finished(snap_id2)

    # 5> 检查文件内容
    cmd = 'cat %s' % test_file
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if stdout.strip() != '222222':
        log.error('%s is not right!!!' % test_file)
        raise Exception('%s is not right!!!' % test_file)

    # 6> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (path))
        raise Exception('%s delete snapshot failed!!!' % (path))

    time.sleep(10)

    return

def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
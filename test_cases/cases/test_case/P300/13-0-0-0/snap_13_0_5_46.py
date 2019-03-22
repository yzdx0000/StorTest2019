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
#    修改快照文件上几层目录的名字
#@steps:
#    1、对目录/mnt/volume1/snap/test_dir1/test_dir2创建快照a1；
#    2、修改目录/mnt/volume1/snap/test_dir1为/mnt/volume1/snap/test_dir3，对快照a1进行revert；
#    3、修改目录/mnt/volume1/snap/test_dir3为/mnt/volume1/snap/test_dir1，对快照a1进行revert；
#    4、修改目录/mnt/volume1/snap/为/mnt/volume1/snap1，对快照a1进行revert；
#    5、删除快照；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0

def case():
    # 创建目录
    test_dir1 = os.path.join(SNAP_TRUE_PATH, 'test_dir1')
    cmd = 'mkdir %s' % test_dir1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    test_dir2 = os.path.join(test_dir1, 'test_dir2')
    cmd = 'mkdir %s' % test_dir2
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    test_dir3 = os.path.join(test_dir2, 'test_dir3')
    cmd = 'mkdir %s' % test_dir3
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 1> 创建快照
    snap_name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_dir1', 'test_dir2', 'test_dir3')
    rc, stdout = snap_common.create_snapshot(snap_name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 2> 修改目录名字
    test_dir2_new = os.path.join(test_dir1, 'test_dir2_new')
    cmd = 'mv %s %s' % (test_dir2, test_dir2_new)
    common.run_command(snap_common.CLIENT_IP_2, cmd)

    # 对快照进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name1)
    snap_id1 = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id1)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != 'Item is not exist':
        log.error("revert snapshot %s failed!!!" % snap_name1)
        raise Exception("revert snapshot %s failed!!!" % snap_name1)

    # 3> 修改目录名字
    cmd = 'mv %s %s' % (test_dir2_new, test_dir2)
    common.run_command(snap_common.CLIENT_IP_2, cmd)

    # 对快照进行revert
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id1)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name1)
        raise Exception("revert snapshot %s failed!!!" % snap_name1)

    # 4> 修改目录名字
    test_dir1_new = os.path.join(SNAP_TRUE_PATH, 'test_dir1_new')
    cmd = 'mv %s %s' % (test_dir1, test_dir1_new)
    common.run_command(snap_common.CLIENT_IP_2, cmd)

    # 对快照进行revert
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id1)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != 'Item is not exist':
        log.error("revert snapshot %s failed!!!" % snap_name1)
        raise Exception("revert snapshot %s failed!!!" % snap_name1)

    # 5> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (path))
        raise Exception('%s delete snapshot failed!!!' % (path))

    time.sleep(10)

    # 6> 3个客户端检查快照路径入口是否存在
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name1)
    snap_common.check_snap_entry(snap_path)

def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
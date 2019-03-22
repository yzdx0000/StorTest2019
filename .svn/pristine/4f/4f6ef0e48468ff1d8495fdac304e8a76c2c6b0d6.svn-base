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
#    同一个目录路径上创建1001个快照，最后一个创建失败
#@steps:
#    1、在路径/mnt/parastor/snap_parent/snap_child/上创建1000个快照
#      （/mnt/parastor/、/mnt/parastor/snap_parent/、/mnt/parastor/snap_parent/snap_child/都创建快照）；
#    2、对目录/mnt/parastor/snap_parent/snap_child/创建第1001个快照；
#    3、删除快照；
#    4、3个客户端检查是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0

def case():
    """检查路径上是否有快照"""
    rc, snapshot_id_lst = snap_common.get_snapshot_ids_by_path(snap_common.SNAP_PATH)
    if rc == 0:
        log.warn("%s snapshot is not 0!!!" % snap_common.SNAP_PATH)
        return

    # 创建子目录
    dir_parent_1 = os.path.join(SNAP_TRUE_PATH, 'snap_parent_dir')
    cmd = 'mkdir %s' % dir_parent_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    dir_child_1 = os.path.join(dir_parent_1, 'snap_child_dir')
    cmd = 'mkdir %s' % dir_child_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 1> 创建1000个快照
    for i in range(333):
        snap_name1 = FILE_NAME + '_snapshot_%d' % i
        path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
        rc, stdout = snap_common.create_snapshot(snap_name1, path)
        if 0 != rc:
            log.error('create_snapshot %s failed!!!' % snap_name1)
            raise Exception('create_snapshot %s failed!!!' % snap_name1)

        snap_name2 = FILE_NAME + '_parent_%d' % i
        path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'snap_parent_dir')
        rc, stdout = snap_common.create_snapshot(snap_name2, path)
        if 0 != rc:
            log.error('create_snapshot %s failed!!!' % snap_name2)
            raise Exception('create_snapshot %s failed!!!' % snap_name2)

        snap_name3 = FILE_NAME + '_child_%d' % i
        path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'snap_parent_dir', 'snap_child_dir')
        rc, stdout = snap_common.create_snapshot(snap_name3, path)
        if 0 != rc:
            log.error('create_snapshot %s failed!!!' % snap_name3)
            raise Exception('create_snapshot %s failed!!!' % snap_name3)

    snap_name3 = FILE_NAME + '_child_333'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'snap_parent_dir', 'snap_child_dir')
    rc, stdout = snap_common.create_snapshot(snap_name3, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name3)
        raise Exception('create_snapshot %s failed!!!' % snap_name3)

    # 2> 创建第1001个快照
    snap_name1 = FILE_NAME + '_snapshot'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name1, path)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != 'Too many snapshots created!':
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    snap_name2 = FILE_NAME + '_parent'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name2, path)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != 'Too many snapshots created!':
        log.error('create_snapshot %s failed!!!' % snap_name2)
        raise Exception('create_snapshot %s failed!!!' % snap_name2)

    snap_name3 = FILE_NAME + '_child'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name3, path)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != 'Too many snapshots created!':
        log.error('create_snapshot %s failed!!!' % snap_name3)
        raise Exception('create_snapshot %s failed!!!' % snap_name3)

    # 3> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (FILE_NAME))
        raise Exception('%s delete snapshot failed!!!' % (FILE_NAME))

    # 检查快照是否删除
    start_time = time.time()
    while True:
        time.sleep(5)
        rc = snap_common.check_snap_exist(FILE_NAME)
        if rc == True:
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            log.info('%dh:%dm:%ds, snapshot %s still not delete!' % (h, m, s, FILE_NAME))
        else:
            break

    time.sleep(10)

    return

def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
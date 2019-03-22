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
#    父目录a子目录b，b创建快照，删除a，revert后，是否有a
#@steps:
#    1、部署3个客户端；
#    2、对目录/mnt/parastor/snap_parent/snap_child/创建快照a1；
#    3、删除目录/mnt/parastor/snap_parent/；
#    4、对快照a1进行revert，3个客户端观察/mnt/parastor/snap_parent/下的内容；
#    5、删除快照；
#    6、3个客户端检查是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0

def case():
    # 创建子目录
    dir_parent_1 = os.path.join(SNAP_TRUE_PATH, 'snap_parent_dir')
    cmd = 'mkdir %s' % dir_parent_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    dir_child_1 = os.path.join(dir_parent_1, 'snap_child_dir')
    cmd = 'mkdir %s' % dir_child_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 2> 创建快照
    snap_name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'snap_parent_dir', 'snap_child_dir')
    rc, stdout = snap_common.create_snapshot(snap_name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 3> 删除父目录
    common.rm_exe(snap_common.CLIENT_IP_1,dir_parent_1)

    # 4> 对快照进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name1)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
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

    return

def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
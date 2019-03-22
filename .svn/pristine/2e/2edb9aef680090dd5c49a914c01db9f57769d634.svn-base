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
#    创建单个目录快照，删除目录，执行revert，目录回滚到之前的内容
#@steps:
#    1、部署3个客户端；
#    2、在目录/mnt/parastor/snap/下创建子目录test_dir1和子文件test_file1；
#    3、对目录/mnt/parastor/snap/创建快照a1；
#    4、客户端1删除目录/mnt/parastor/snap/test_dir1/；
#    5、对快照a1进行revert；
#    6、3个客户端检查/mnt/parastor/snap/的属性和内容；
#    7、客户端2删除目录/mnt/parastor/snap/；
#    8、对快照a1进行revert；
#    9、3个客户端检查/mnt/parastor/snap/的属性和内容；
#    10、删除快照；
#    11、3个客户端检查是否有快照路径入口；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0

def case():
    # 2> 创建子目录
    dir_path_1 = os.path.join(SNAP_TRUE_PATH, 'test_dir_1')
    cmd = 'mkdir %s' % dir_path_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建子目录
    dir_path_1_1 = os.path.join(dir_path_1, 'test_dir_1_1')
    cmd = 'mkdir %s' % dir_path_1_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 3> 创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_dir_1')
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 4> 删除目录
    common.rm_exe(snap_common.CLIENT_IP_1,dir_path_1_1)


    # 5> 对快照进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name)
        raise Exception("revert snapshot %s failed!!!" % snap_name)
    snap_common.check_revert_finished(snap_id)

    # 6> 检查目录
    cmd = 'ls %s' % dir_path_1_1
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.error("%s is not exist!!!" % dir_path_1_1)
        raise Exception("%s is not exist!!!" % dir_path_1_1)

    # 7> 删除目录
    common.rm_exe(snap_common.CLIENT_IP_1,dir_path_1)

    # 8> 对快照进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != 'Item is not exist':
        log.error("revert snapshot %s failed!!!" % snap_name)
        raise Exception("revert snapshot %s failed!!!" % snap_name)

    # 10> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (path))
        raise Exception('%s delete snapshot failed!!!' % (path))

    time.sleep(10)

    # 11> 3个客户端检查快照路径入口是否存在
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    snap_common.check_snap_entry(snap_path)

    return

def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
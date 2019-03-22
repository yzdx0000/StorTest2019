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
#    给子目录做快照，修改后再对父目录创建快照，先后revert子目录、父目录，每次内容正确
#@steps:
#    1、部署3个客户端；
#    2、创建目录/mnt/parastor/snap_parent/snap_child/，snap_child目录下有文件test_file1和目录test_dir1；
#    3、对目录/mnt/parastor/snap_parent/snap_child/创建快照a1；
#    4、客户端1 snap_child目录下修改文件test_file1内容，删除目录test_dir1，创建文件test_file2和目录test_dir2；
#    5、对目录/mnt/parastor/snap_parent/创建快照a2；
#    6、对快照a1 revert，3个客户端观察/mnt/parastor/snap_parent/下的内容；
#    7、对快照a2 revert，3个客户端观察/mnt/parastor/snap_parent/下的内容；
#    8、删除快照；
#    9、3个客户端检查是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0

def case():
    # 2> 创建子目录
    dir_parent_1 = os.path.join(SNAP_TRUE_PATH, 'snap_parent_dir')
    cmd = 'mkdir %s' % dir_parent_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    dir_child_1 = os.path.join(dir_parent_1, 'snap_child_dir')
    cmd = 'mkdir %s' % dir_child_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建子文件
    file_test_1 = os.path.join(dir_child_1, 'test_file_1')
    cmd = 'echo 111 > %s' % file_test_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建子目录
    dir_test_1 = os.path.join(dir_child_1, 'test_dir_1')
    cmd = 'mkdir %s' % dir_test_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 3> 创建快照
    snap_name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'snap_parent_dir', 'snap_child_dir')
    rc, stdout = snap_common.create_snapshot(snap_name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 4> 修改文件内容
    cmd = 'echo 222 > %s' % file_test_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 删除子目录
    common.rm_exe(snap_common.CLIENT_IP_1,dir_test_1)

    # 创建子文件
    file_test_2 = os.path.join(dir_child_1, 'test_file_2')
    cmd = 'echo aaa > %s' % file_test_2
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建子目录
    dir_test_2 = os.path.join(dir_child_1, 'test_dir_2')
    cmd = 'mkdir %s' % dir_test_2
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 5> 创建快照2
    snap_name2 = FILE_NAME + '_snapshot2'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'snap_parent_dir')
    rc, stdout = snap_common.create_snapshot(snap_name2, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name2)
        raise Exception('create_snapshot %s failed!!!' % snap_name2)

    # 6> 对快照1进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name1)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name1)
        raise Exception("revert snapshot %s failed!!!" % snap_name1)
    snap_common.check_revert_finished(snap_id)

    # 检查文件内容
    cmd = 'cat %s' % file_test_1
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if stdout.strip() != '111':
        log.error("%s is not right!!!" % file_test_1)
        raise Exception("%s is not right!!!" % file_test_1)

    cmd = 'ls %s' % dir_test_1
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if rc != 0:
        log.error("%s is not exist!!!" % dir_test_1)
        raise Exception("%s is not exist!!!" % dir_test_1)

    cmd = 'ls %s' % file_test_2
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if rc == 0:
        log.error("%s is exist!!!" % file_test_2)
        raise Exception("%s is exist!!!" % file_test_2)

    cmd = 'ls %s' % dir_test_2
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if rc == 0:
        log.error("%s is exist!!!" % dir_test_2)
        raise Exception("%s is exist!!!" % dir_test_2)

    # 7> 对快照2进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name2)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name2)
        raise Exception("revert snapshot %s failed!!!" % snap_name2)
    snap_common.check_revert_finished(snap_id)

    # 检查文件内容
    cmd = 'cat %s' % file_test_1
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if stdout.strip() != '222':
        log.error("%s is not right!!!" % file_test_1)
        raise Exception("%s is not right!!!" % file_test_1)

    cmd = 'ls %s' % dir_test_1
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if rc == 0:
        log.error("%s is exist!!!" % dir_test_1)
        raise Exception("%s is exist!!!" % dir_test_1)

    cmd = 'cat %s' % file_test_2
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if stdout.strip() != 'aaa':
        log.error("%s is not right!!!" % file_test_2)
        raise Exception("%s is not right!!!" % file_test_2)

    cmd = 'ls %s' % dir_test_2
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if rc != 0:
        log.error("%s is not exist!!!" % dir_test_2)
        raise Exception("%s is not exist!!!" % dir_test_2)

    # 8> 删除快照
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
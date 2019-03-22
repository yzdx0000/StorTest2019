#-*-coding:utf-8 -*
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
#@summary：
#    创建单个文件快照，移动文件，执行revert，文件内容回滚到之前的内容，移出去的文件是否删除
#@steps:
#    1、部署3个客户端；
#    2、对文件/mnt/parastor/snap/test_file1创建快照a1；
#    3、mv文件/mnt/parastor/snap/test_file1到/mnt/parastor/snap/test_dir/test_file1；
#    4、对快照a1执行revert；
#    5、3个客户端查看文件/mnt/parastor/snap/test_file1;
#    6、mv文件/mnt/parastor/snap/test_file1到/mnt/parastor/snap1/test_file1；
#    7、对快照a1执行revert；
#    8、3个客户端查看文件/mnt/parastor/snap/test_file1；
#    9、删除快照；
#    10、3个客户端查看是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0

def case():
    # 创建子文件
    file_path = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    test_str = '111111'
    cmd = 'echo %s > %s' % (test_str, file_path)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 2> 创建快照
    snap_name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 3> mv文件到其他地方
    dir_path = os.path.join(SNAP_TRUE_PATH, 'test_dir')
    cmd = 'mv %s %s' % (file_path, dir_path)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 4> 对快照进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name1)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name1)
        raise Exception("revert snapshot %s failed!!!" % snap_name1)
    snap_common.check_revert_finished(snap_id)

    # 5> 检查文件内容
    cmd = 'cat %s' % file_path
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if stdout.strip() != '111111':
        log.error("%s is not right!!!" % snap_name1)
        raise Exception("%s is not right!!!" % snap_name1)
    file_new_path = os.path.join(dir_path, 'test_file1')
    cmd = 'ls %s' % file_new_path
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if rc == 0:
        log.error("%s is exist!!!" % snap_name1)
        raise Exception("%s is exist!!!" % snap_name1)

    # 6> mv文件到其他地方
    dir_path1 = os.path.join(os.path.dirname(snap_common.SNAP_PATH), 'snap1')
    cmd = 'mkdir %s' % dir_path1
    common.run_command(snap_common.CLIENT_IP_1, cmd)
    cmd = 'mv %s %s' % (dir_path, dir_path1)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 7> 对快照进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name1)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name1)
        raise Exception("revert snapshot %s failed!!!" % snap_name1)
    snap_common.check_revert_finished(snap_id)

    # 8> 检查文件内容
    cmd = 'cat %s' % file_path
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if stdout.strip() != '111111':
        log.error("%s is not right!!!" % snap_name1)
        raise Exception("%s is not right!!!" % snap_name1)

    # 9> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (path))
        raise Exception('%s delete snapshot failed!!!' % (path))

    time.sleep(10)

    # 10> 3个客户端检查快照路径入口是否存在
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
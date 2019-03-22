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
#    嵌套目录下创建多个快照，浏览快照。
#@steps:
#    1、部署3个客户端；
#    2、创建文件/mnt/parastor/snap/test_dir1/test_dir11/test_file1；
#    3、对目录/mnt/parastor/snap/创建快照a1；
#    4、对目录/mnt/parastor/snap/test_dir1/创建快照a2；
#    5、对目录/mnt/parastor/snap/test_dir1/test_dir11/创建快照a3；
#    6、修改/mnt/parastor/snap/test_dir1/test_dir11/test_file1文件内容；
#    7、3个客户端进入/mnt/parastor/.snapshot目录浏览a1快照数据；
#    8、删除快照；
#    9、3个客户端查看是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_0_0

def case():
    # 2> 创建目录
    test_dir_1 = os.path.join(SNAP_TRUE_PATH, 'test_dir_1')
    cmd = 'mkdir %s' % test_dir_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    test_dir_11 = os.path.join(test_dir_1, 'test_dir_11')
    cmd = 'mkdir %s' % test_dir_11
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    test_file_1 = os.path.join(test_dir_11, 'test_file_1')
    cmd = 'echo 111 > %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 获取文件md5值
    rc, file_md5 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, test_file_1)

    # 3、4、5> 创建快照
    snap_name1 = FILE_NAME + '_snapshot1'
    path1 = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name1, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    snap_name2 = FILE_NAME + '_snapshot2'
    path2 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_dir_1')
    rc, stdout = snap_common.create_snapshot(snap_name2, path2)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name2)
        raise Exception('create_snapshot %s failed!!!' % snap_name2)

    snap_name3 = FILE_NAME + '_snapshot3'
    path3 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_dir_1', 'test_dir_11')
    rc, stdout = snap_common.create_snapshot(snap_name3, path3)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name3)
        raise Exception('create_snapshot %s failed!!!' % snap_name3)

    # 6> 修改文件内容
    cmd = 'echo aaa >> %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 7> 查看快照文件md5值
    snap_path1 = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name1)
    snap_path2 = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name2)
    snap_path3 = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name3)
    snap_file_1 = os.path.join(snap_path1, 'test_dir_1', 'test_dir_11', 'test_file_1')
    snap_file_2 = os.path.join(snap_path2, 'test_dir_11', 'test_file_1')
    snap_file_3 = os.path.join(snap_path3, 'test_file_1')
    snap_common.check_snap_md5(file_md5, snap_file_1)
    snap_common.check_snap_md5(file_md5, snap_file_2)
    snap_common.check_snap_md5(file_md5, snap_file_3)

    # 8> 手动删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete failed!!!' % (FILE_NAME))
        raise Exception('%s delete failed!!!' % (FILE_NAME))

    log.info('waiting for 10s')
    time.sleep(10)
    judge_mark = True
    while judge_mark:
        delete_check = snap_common.get_snapshot_by_name(snap_name1)
        if delete_check != -1:
            log.info('waiting for 10s')
            time.sleep(10)
        else:
            judge_mark = False

    # 9> 3个客户端检查快照路径入口是否存在
    snap_common.check_snap_entry(snap_path1)

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
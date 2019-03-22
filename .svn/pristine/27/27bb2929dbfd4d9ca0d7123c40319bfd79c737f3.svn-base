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
#    对单个文件创建多个快照，每个快照之间对文件做不同的操作
#@steps:
#    1、部署3个客户端；
#    2、对文件创建快照a1（文件有内容）；
#    3、客户端1修改源文件的内容，创建快照a2；
#    4、客户端2使用truncate修改源文件的内容，创建快照a3；
#    5、客户端3修改源文件的权限，创建快照a4；
#    6、客户端1修改源文件的名字，创建快照a5；
#    7、客户端2删除源文件；
#    8、3个客户端分别查看快照a12345的内容；
#    9、删除所有快照；
#    10、3个客户端查看是否还有快照入口；
#
#@changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_0_0

def case():
    # 创建文件
    file_path1 = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    test_str_1 = '1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111' \
                 '1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'
    cmd = 'echo %s > %s' % (test_str_1, file_path1)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 2> 创建快照
    snap_name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file1')
    rc, stdout = snap_common.create_snapshot(snap_name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 获取文件的md5值
    rc, file_md5_1_0 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, file_path1)
    if rc != 0:
        log.error('get %s md5 failed!!!' % file_path1)
        raise Exception('get %s md5 failed!!!' % file_path1)

    # 修改文件内容
    test_str_2 = '2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222' \
                 '2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222'
    cmd = 'echo %s >> %s' % (test_str_2, file_path1)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 3> 创建快照
    snap_name2 = FILE_NAME + '_snapshot2'
    rc, stdout = snap_common.create_snapshot(snap_name2, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name2)
        raise Exception('create_snapshot %s failed!!!' % snap_name2)

    # 获取文件的md5值
    rc, file_md5_2_0 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, file_path1)
    if rc != 0:
        log.error('get %s md5 failed!!!' % file_path1)
        raise Exception('get %s md5 failed!!!' % file_path1)

    # 使用truncate修改文件
    cmd = 'truncate %s -s 10' % file_path1
    common.run_command(snap_common.CLIENT_IP_2, cmd)

    # 4> 创建快照
    snap_name3 = FILE_NAME + '_snapshot3'
    rc, stdout = snap_common.create_snapshot(snap_name3, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name3)
        raise Exception('create_snapshot %s failed!!!' % snap_name3)

    # 获取文件的md5值
    rc, file_md5_3_0 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, file_path1)
    if rc != 0:
        log.error('get %s md5 failed!!!' % file_path1)
        raise Exception('get %s md5 failed!!!' % file_path1)

    # 获取文件的权限
    rc, file_permission_0 = snap_common.get_file_permission(snap_common.CLIENT_IP_1, file_path1)

    # 修改文件权限
    cmd = 'chmod 777 %s' % file_path1
    common.run_command(snap_common.CLIENT_IP_3, cmd)

    # 5> 创建快照
    snap_name4 = FILE_NAME + '_snapshot4'
    rc, stdout = snap_common.create_snapshot(snap_name4, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name4)
        raise Exception('create_snapshot %s failed!!!' % snap_name4)


    # 修改文件的名字
    file_path2 = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    cmd = 'mv %s %s' % (file_path1, file_path2)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 6> 创建快照
    snap_name5 = FILE_NAME + '_snapshot5'
    rc, stdout = snap_common.create_snapshot(snap_name5, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name5)
        raise Exception('create_snapshot %s failed!!!' % snap_name5)

    # 7> 删除文件
    common.rm_exe(snap_common.CLIENT_IP_1,file_path2)

    # 8> 检查快照1的md5值
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name1)
    snap_common.check_snap_md5(file_md5_1_0, snap_path)

    # 检查快照2的md5值
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name2)
    snap_common.check_snap_md5(file_md5_2_0, snap_path)

    # 检查快照3的权限
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name3)
    rc, file_permission_1 = snap_common.get_file_permission(snap_common.CLIENT_IP_1, snap_path)
    if file_permission_1 != file_permission_0:
        log.error('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_1, snap_path))
        raise Exception('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_1, snap_path))
    rc, file_permission_2 = snap_common.get_file_permission(snap_common.CLIENT_IP_2, snap_path)
    if file_permission_2 != file_permission_0:
        log.error('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_2, snap_path))
        raise Exception('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_2, snap_path))
    rc, file_permission_2 = snap_common.get_file_permission(snap_common.CLIENT_IP_3, snap_path)
    if file_permission_2 != file_permission_0:
        log.error('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_3, snap_path))
        raise Exception('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_3, snap_path))

    # 检查快照4的md5
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name4)
    snap_common.check_snap_md5(file_md5_3_0, snap_path)

    # 9> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete failed!!!' % (path))
        raise Exception('%s delete failed!!!' % (path))

    time.sleep(10)

    # 10> 3个客户端检查快照路径入口是否存在
    snap_common.check_snap_entry(snap_path)

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)

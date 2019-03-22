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
#    创建单个文件快照，修改文件属性，执行revert，文件内容回滚到之前的内容
#@steps:
#    1、对文件/mnt/parastor/snap/test_file1创建快照a1；
#    2、修改文件/mnt/parastor/snap/test_file1的权限和所属用户、用户组；
#    3、对快照a1执行revert；
#    4、3个客户端查看文件/mnt/parastor/snap/test_file1；
#    5、删除快照策略;
#    6、3个客户端查看是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0

def case():
    # 创建文件
    file_path1 = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    test_str_1 = '1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111' \
                 '1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'
    cmd = 'echo %s > %s' % (test_str_1, file_path1)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 1> 创建快照
    snap_name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file1')
    rc, stdout = snap_common.create_snapshot(snap_name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 2> 获取文件权限和用户和用户组
    rc, file_permission_0 = snap_common.get_file_permission(snap_common.CLIENT_IP_1, file_path1)
    user_first, user_group_first = snap_common.get_file_user_and_group(snap_common.CLIENT_IP_1, file_path1)

    # 修改文件权限
    cmd = 'chmod 755 %s' % file_path1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建用户组和用户
    snap_common.create_user_group(snap_common.CLIENT_IP_1, snap_common.SNAP_GROUP)
    snap_common.create_user(snap_common.CLIENT_IP_1, snap_common.SNAP_USER, snap_common.SNAP_GROUP)

    # 修改文件的用户和用户组
    snap_common.chgrp_file_user_group(snap_common.CLIENT_IP_1, file_path1, snap_common.SNAP_GROUP)
    snap_common.chown_file_user(snap_common.CLIENT_IP_1, file_path1, snap_common.SNAP_USER)

    user_second, user_group_second = snap_common.get_file_user_and_group(snap_common.CLIENT_IP_1, file_path1)
    if user_second != snap_common.SNAP_USER or user_group_second != snap_common.SNAP_GROUP:
        log.error('file %s user is %s, user_grp is %s' % (file_path1, user_second, user_group_second))
        raise Exception('file %s user is %s, user_grp is %s' % (file_path1, user_second, user_group_second))

    # 3> 对快照进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name1)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name1)
        raise Exception("revert snapshot %s failed!!!" % snap_name1)
    snap_common.check_revert_finished(snap_id)

    # 4> 获取权限和用户和用户组
    rc, file_permission_1 = snap_common.get_file_permission(snap_common.CLIENT_IP_1, file_path1)
    user_check, user_group_check = snap_common.get_file_user_and_group(snap_common.CLIENT_IP_1, file_path1)
    if file_permission_0 != file_permission_1:
        log.error('file %s permission is not right' % file_path1)
        raise Exception('file %s permission is not right' % file_path1)
    if user_first != user_check:
        log.error('file %s user is not right' % file_path1)
        raise Exception('file %s user is not right' % file_path1)
    if user_group_first != user_group_check:
        log.error('file %s user_group is not right' % file_path1)
        raise Exception('file %s user_group is not right' % file_path1)

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

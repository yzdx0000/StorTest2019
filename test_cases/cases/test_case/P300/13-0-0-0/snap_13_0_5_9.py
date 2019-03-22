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
#    创建多个文件快照（同一文件），按照快照创建顺序revert，每次文件内容是正确的
#     （每个快照之间分别对文件进行修改内容、修改属性、修改名字、移动位置、删除文件）
#@steps:
#    1、部署3个客户端；
#    2、对文件/mnt/parastor/snap/test_file1创建快照a1；
#    3、客户端1修改文件/mnt/parastor/snap/test_file1内容，创建快照a2；
#    4、客户端2修改文件/mnt/parastor/snap/test_file1权限、用户、用户组，创建快照a3；
#    5、客户端3mv文件/mnt/parastor/snap/test_file1到/mnt/parastor/snap1/test_file1，创建快照a4;
#    6、客户端1修改文件/mnt/parastor/snap1/test_file1为/mnt/parastor/snap1/test_file2，创建快照a5；
#    7、客户端2删除文件/mnt/parastor/snap1/test_file2；
#    8、按照a5、a4、a3、a2、a1的顺序revert，每次观察文件是否正确；
#    9、删除快照；
#    10、3个客户端检查是否有快照路径入口；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0

def case():
    # 创建文件
    file_path_1 = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    test_str = '111111'
    cmd = 'echo %s > %s' % (test_str, file_path_1)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 修改文件权限
    cmd = 'chmod 755 %s' % file_path_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 2> 创建快照1
    snap_name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 3> 修改文件内容
    cmd = 'echo 222 > %s' % file_path_1
    common.run_command(snap_common.CLIENT_IP_2, cmd)

    # 创建快照2
    snap_name2 = FILE_NAME + '_snapshot2'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name2, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name2)
        raise Exception('create_snapshot %s failed!!!' % snap_name2)

    # 4> 修改文件权限
    cmd = 'chmod 533 %s' % file_path_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)
    # 修改文件用户组和用户
    snap_common.create_user_group(snap_common.CLIENT_IP_1, snap_common.SNAP_GROUP)
    snap_common.create_user(snap_common.CLIENT_IP_1, snap_common.SNAP_USER, snap_common.SNAP_GROUP)
    snap_common.scp_passwd_and_group_to_all_other_nodes(snap_common.CLIENT_IP_1)
    snap_common.chgrp_file_user_group(snap_common.CLIENT_IP_1, file_path_1, snap_common.SNAP_GROUP)
    snap_common.chown_file_user(snap_common.CLIENT_IP_1, file_path_1, snap_common.SNAP_USER)


    # 创建快照3
    snap_name3 = FILE_NAME + '_snapshot3'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name3, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name3)
        raise Exception('create_snapshot %s failed!!!' % snap_name3)

    # 5> 移动文件
    dir_path = os.path.join(SNAP_TRUE_PATH, 'test_dir1')
    cmd = 'mkdir %s' % dir_path
    common.run_command(snap_common.CLIENT_IP_1, cmd)
    cmd = 'mv %s %s' % (file_path_1, dir_path)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建快照4
    snap_name4 = FILE_NAME + '_snapshot4'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name4, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name4)
        raise Exception('create_snapshot %s failed!!!' % snap_name4)

    # 6> 修改文件名字
    file_path_2 = os.path.join(dir_path, 'test_file1')
    file_new_path = os.path.join(dir_path, 'test_file2')
    cmd = 'mv %s %s' % (file_path_2, file_new_path)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建快照5
    snap_name5 = FILE_NAME + '_snapshot5'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name5, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name5)
        raise Exception('create_snapshot %s failed!!!' % snap_name5)

    # 7> 删除文件
    common.rm_exe(snap_common.CLIENT_IP_1,file_new_path)

    # 8> 对快照a5进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name5)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name5)
        raise Exception("revert snapshot %s failed!!!" % snap_name5)
    snap_common.check_revert_finished(snap_id)

    # 检查文件内容和权限 用户 用户组
    cmd = 'ls %s' % file_path_2
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if rc == 0:
        log.error("%s is exist!!!" % file_path_2)
        raise Exception("%s is exist!!!" % file_path_2)

    cmd = 'cat %s' % file_new_path
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if stdout.strip() != '222':
        log.error("%s is not right!!!" % file_new_path)
        raise Exception("%s is not right!!!" % file_new_path)

    rc, stdout = snap_common.get_file_permission(snap_common.CLIENT_IP_2, file_new_path)
    if stdout != '533':
        log.error("%s permission is not right!!!" % file_new_path)
        raise Exception("%s permission is not right!!!" % file_new_path)

    user, user_group = snap_common.get_file_user_and_group(snap_common.CLIENT_IP_2, file_new_path)
    if user != snap_common.SNAP_USER or user_group != snap_common.SNAP_GROUP:
        log.error("%s user or user_grp is not right!!!" % file_new_path)
        raise Exception("%s user or user_grp is not right!!!" % file_new_path)

    # 对快照a4进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name4)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name4)
        raise Exception("revert snapshot %s failed!!!" % snap_name4)
    snap_common.check_revert_finished(snap_id)

    # 检查文件内容和权限 用户 用户组
    cmd = 'ls %s' % file_path_1
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if rc == 0:
        log.error("%s is exist!!!" % file_path_1)
        raise Exception("%s is exist!!!" % file_path_1)

    cmd = 'cat %s' % file_path_2
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if stdout.strip() != '222':
        log.error("%s is not right!!!" % file_path_2)
        raise Exception("%s is not right!!!" % file_path_2)

    rc, stdout = snap_common.get_file_permission(snap_common.CLIENT_IP_2, file_path_2)
    if stdout != '533':
        log.error("%s permission is not right!!!" % file_path_2)
        raise Exception("%s permission is not right!!!" % file_path_2)

    user, user_group = snap_common.get_file_user_and_group(snap_common.CLIENT_IP_2, file_path_2)
    if user != snap_common.SNAP_USER or user_group != snap_common.SNAP_GROUP:
        log.error("%s user or user_grp is not right!!!" % file_path_2)
        raise Exception("%s user or user_grp is not right!!!" % file_path_2)

    # 对快照a3进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name3)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name3)
        raise Exception("revert snapshot %s failed!!!" % snap_name3)
    snap_common.check_revert_finished(snap_id)

    # 检查文件内容和权限 用户 用户组
    cmd = 'cat %s' % file_path_1
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if stdout.strip() != '222':
        log.error("%s is not right!!!" % file_path_1)
        raise Exception("%s is not right!!!" % file_path_1)

    rc, stdout = snap_common.get_file_permission(snap_common.CLIENT_IP_2, file_path_1)
    if stdout != '533':
        log.error("%s permission is not right!!!" % file_path_1)
        raise Exception("%s permission is not right!!!" % file_path_1)

    user, user_group = snap_common.get_file_user_and_group(snap_common.CLIENT_IP_2, file_path_1)
    if user != snap_common.SNAP_USER or user_group != snap_common.SNAP_GROUP:
        log.error("%s user or user_grp is not right!!!" % file_path_1)
        raise Exception("%s user or user_grp is not right!!!" % file_path_1)

    # 对快照a2进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name2)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name2)
        raise Exception("revert snapshot %s failed!!!" % snap_name2)
    snap_common.check_revert_finished(snap_id)

    # 检查文件内容和权限 用户 用户组
    cmd = 'cat %s' % file_path_1
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if stdout.strip() != '222':
        log.error("%s is not right!!!" % file_path_1)
        raise Exception("%s is not right!!!" % file_path_1)

    rc, stdout = snap_common.get_file_permission(snap_common.CLIENT_IP_2, file_path_1)
    if stdout != '755':
        log.error("%s permission is not right!!!" % file_path_1)
        raise Exception("%s permission is not right!!!" % file_path_1)

    user, user_group = snap_common.get_file_user_and_group(snap_common.CLIENT_IP_2, file_path_1)
    if user != 'root' or user_group != 'root':
        log.error("%s user or user_grp is not right!!!" % file_path_1)
        raise Exception("%s user or user_grp is not right!!!" % file_path_1)

    # 对快照1进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name1)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name1)
        raise Exception("revert snapshot %s failed!!!" % snap_name1)
    snap_common.check_revert_finished(snap_id)

    # 检查文件内容和权限 用户 用户组
    cmd = 'cat %s' % file_path_1
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if stdout.strip() != '111111':
        log.error("%s is not right!!!" % file_path_1)
        raise Exception("%s is not right!!!" % file_path_1)

    rc, stdout = snap_common.get_file_permission(snap_common.CLIENT_IP_2, file_path_1)
    if stdout != '755':
        log.error("%s permission is not right!!!" % file_path_1)
        raise Exception("%s permission is not right!!!" % file_path_1)

    user, user_group = snap_common.get_file_user_and_group(snap_common.CLIENT_IP_2, file_path_1)
    if user != 'root' or user_group != 'root':
        log.error("%s user or user_grp is not right!!!" % file_path_1)
        raise Exception("%s user or user_grp is not right!!!" % file_path_1)

    # 9> 删除快照
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
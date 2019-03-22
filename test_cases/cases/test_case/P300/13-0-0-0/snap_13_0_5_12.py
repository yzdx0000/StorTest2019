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
#    创建单个目录快照，修改目录属性，执行revert，目录回滚到之前的内容
#@steps:
#    1、部署3个客户端；
#    2、在目录/mnt/parastor/snap/下创建子目录test_dir1和子文件test_file1；
#    3、对目录/mnt/parastor/snap/创建快照a1；
#    4、客户端1修改目录/mnt/parastor/snap/ 的权限、用户和用户组；
#    5、对快照a1进行revert；
#    6、3个客户端检查/mnt/parastor/snap/的属性和内容；
#    7、删除快照；
#    8、3个客户端检查是否有快照路径入口；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0

def case():
    # 2> 创建子目录
    dir_path_1 = os.path.join(SNAP_TRUE_PATH, 'test_dir1')
    cmd = 'mkdir %s' % (dir_path_1)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建子文件
    file_path_1 = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    cmd = 'echo 111 > %s' % file_path_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 修改目录权限
    cmd = 'chmod 755 %s' % dir_path_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 3> 创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_dir1')
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 4> 修改目录的权限、用户和用户组
    cmd = 'chmod 533 %s' % dir_path_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    snap_common.create_user_group(snap_common.CLIENT_IP_1, snap_common.SNAP_GROUP)
    snap_common.create_user(snap_common.CLIENT_IP_1, snap_common.SNAP_USER, snap_common.SNAP_GROUP)
    snap_common.scp_passwd_and_group_to_all_other_nodes(snap_common.CLIENT_IP_1)
    snap_common.chgrp_file_user_group(snap_common.CLIENT_IP_1, dir_path_1, snap_common.SNAP_GROUP)
    snap_common.chown_file_user(snap_common.CLIENT_IP_1, dir_path_1, snap_common.SNAP_USER)

    # 5> 对快照进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name)
        raise Exception("revert snapshot %s failed!!!" % snap_name)
    snap_common.check_revert_finished(snap_id)

    # 6> 检查目录权限、用户和用户组
    rc, stdout = snap_common.get_file_permission(snap_common.CLIENT_IP_2, dir_path_1)
    if stdout != '755':
        log.error("%s permission is not right!!!" % dir_path_1)
        raise Exception("%s permission is not right!!!" % dir_path_1)

    user, user_group = snap_common.get_dir_user_and_group(snap_common.CLIENT_IP_2, dir_path_1)
    if user.strip() != 'root' or user_group.strip() != 'root':
        log.error("%s user or user_grp is not right!!!" % dir_path_1)
        raise Exception("%s user or user_grp is not right!!!" % dir_path_1)

    cmd = 'ls %s' % file_path_1
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if rc != 0:
        log.error("%s user or user_grp is not right!!!" % dir_path_1)
        raise Exception("%s user or user_grp is not right!!!" % dir_path_1)

    # 7> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (path))
        raise Exception('%s delete snapshot failed!!!' % (path))

    time.sleep(10)

    # 8> 3个客户端检查快照路径入口是否存在
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

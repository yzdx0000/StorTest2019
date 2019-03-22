#-*-coding:utf-8 -*
#!/usr/bin/python

import os
import time
import commands

import utils_path
import common
import snap_common
import log
import prepare_clean

#=================================================================================
#  latest update:2018-05-11                                                     =
#  author:wangguanglin                                                           =
#=================================================================================
# 2018-05-11:
# 修改者：wangguanglin
#@summary：
#   创建多个目录快照（同一目录），按照快照创建顺序revert，
#   每次目录内容是正确的（每个快照之间分别对目录进行修改内容、修改属性、修改名字、移动位置、删除目录）
#@steps:
#   1、部署3个客户端；
#   2、/mnt/wangguanglin/snap/snap_13_0_5_20下创建目录test_dir1，test_dir1下还有子目录和文件，对目录/mnt/parastor/snap/创建快照a1；
#   3、客户端1在目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1/下修改子目录和文件内容；
#   4、对目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1/创建快照a2；
#   5、客户端2修改//mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1/的权限、用户和用户组；
#   6、对目录/mnt/wangguanglin/snap/snap_13_0_5_20/创建快照a3；
#   7、客户端1修改目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1/为/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir2/;
#   8、对目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir2/创建快照a4；
#   9、客户端2删除目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir2/；
#   10、对目录//mnt/wangguanglin/snap/snap_13_0_5_20/创建快照a5；
#   11、按照a3、a1、a4、a5、a2的顺序依次revert，观察快照源目录情况；
#   12、删除快照；
#   13、3个客户端检查是否有快照路径入口；
#
#changelog:
######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/wangguanglin/snap/snap_13_0_5_20
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_5_20


def case():
    """创建子目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1"""
    test_dir = os.path.join(SNAP_TRUE_PATH, 'test_dir1')
    cmd = 'mkdir %s' % test_dir
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """创建子目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1/test1"""
    test_dir1 = os.path.join(test_dir, 'test1')
    cmd = 'mkdir %s' % test_dir1
    common.run_command(snap_common.CLIENT_IP_1, cmd)
    test_file = os.path.join(test_dir, 'test_file')
    cmd = 'touch %s' % test_file
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1创建快照1"""
    snap_name1 = FILE_NAME + '_snapshot1'
    path1 = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name1, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)


    """客户端1在目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1下修改子目录和文件内容"""

    """客户端1修改/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1/test1目录名"""
    test_dir12 = os.path.join(test_dir, 'test12')
    cmd = 'mv %s %s' % (test_dir1, test_dir12)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """客户端1在目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1下修改文件内容"""
    cmd = 'echo 111 >> %s' % test_file
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """对目录/mnt/wangguanglin/snapsnap_13_0_5_20/test_dir1创建快照2"""
    snap_name2 = FILE_NAME + '_snapshot2'
    rc, stdout = snap_common.create_snapshot(snap_name2, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name2)
        raise Exception('create_snapshot %s failed!!!' % snap_name2)

    """客户端2修改/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1的权限、用户和用户组"""
    cmd = 'chmod 522 %s' % test_dir
    common.run_command(snap_common.CLIENT_IP_1, cmd)
    """修改文件用户组和用户"""
    snap_common.create_user_group(snap_common.CLIENT_IP_1, snap_common.SNAP_GROUP)
    snap_common.create_user(snap_common.CLIENT_IP_1, snap_common.SNAP_USER, snap_common.SNAP_GROUP)
    snap_common.scp_passwd_and_group_to_all_other_nodes(snap_common.CLIENT_IP_1)
    snap_common.chgrp_file_user_group(snap_common.CLIENT_IP_1, test_dir, snap_common.SNAP_GROUP)
    snap_common.chown_file_user(snap_common.CLIENT_IP_1, test_dir, snap_common.SNAP_USER)

    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1创建快照3"""
    snap_name3 = FILE_NAME + '_snapshot3'
    rc, stdout = snap_common.create_snapshot(snap_name3, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name3)
        raise Exception('create_snapshot %s failed!!!' % snap_name3)

    """
    客户端1修改目录/mnt/parastor/snap/snap_13_0_5_20/test_dir1
    为/mnt/parastor/snap/snap_13_0_5_20/test_dir2
    """
    test_dir2 = os.path.join(SNAP_TRUE_PATH, 'test_dir2')
    cmd = 'mv %s %s' % (test_dir, test_dir2)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20/创建快照4"""
    snap_name4 = FILE_NAME + '_snapshot4'
    rc, stdout = snap_common.create_snapshot(snap_name4, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name4)
        raise Exception('create_snapshot %s failed!!!' % snap_name4)


    """客户端2删除/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir2"""
    cmd='rm -rf %s'% test_dir2
    common.run_command(snap_common.CLIENT_IP_2, cmd)

    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1创建快照5"""
    snap_name5 = FILE_NAME + '_snapshot5'
    rc, stdout = snap_common.create_snapshot(snap_name5, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name5)
        raise Exception('create_snapshot %s failed!!!' % snap_name5)

    """对快照3进行revert"""
    snap_info3 = snap_common.get_snapshot_by_name(snap_name3)
    snap_id3 = snap_info3['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id3)
    if 0 != rc:
        log.error('revert_snapshot %s failed!!!' % snap_name3)
        raise Exception('revert_snapshot %s failed!!!' % snap_name3)
    snap_common.check_revert_finished(snap_id3)

    """检查文件内容和权限 用户 用户组"""
    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20下是否是目录test_dir1"""
    cmd='ls %s'% SNAP_TRUE_PATH
    rc,stdout=common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip() != 'test_dir1':
        log.error(' %s item failed!!!' % snap_name1)
        raise Exception(' %s item failed!!!' % snap_name1)
    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1下是否为目录test12"""
    cmd="ls -l %s| grep '^d'"% test_dir
    rc,stdout=common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip().split()[-1] != 'test12':
        log.error(' %s item failed!!!' % snap_name1)
        raise Exception(' %s item failed!!!' % snap_name1)
    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1下是否是文件test_file,并且内容为111"""
    cmd="ls -l %s| grep '^-'"% test_dir
    rc,stdout=common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip().split()[-1] != 'test_file':
        log.error(' %s item failed!!!' % snap_name1)
        raise Exception(' %s item failed!!!' % snap_name1)
    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1下文件test_file内容是否为111"""
    cmd="cat %s"% test_file
    rc,stdout=common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip()!= '111':
        log.error(' %s item failed!!!' % test_file)
        raise Exception(' %s item failed!!!' % test_file)
    """检查文件权限"""
    rc, stdout = snap_common.get_file_permission(snap_common.CLIENT_IP_2, test_dir)
    if stdout != '522':
        log.error("%s permission is not right!!!" % test_dir)
        raise Exception("%s permission is not right!!!" % test_dir)
    """检查文件用户 用户组"""
    user, user_group = snap_common.get_dir_user_and_group(snap_common.CLIENT_IP_2, test_dir)
    if user != 'snap_user' or user_group != 'snap_group':
        log.error("%s user or user_grp is not right!!!" % test_dir)
        raise Exception("%s user or user_grp is not right!!!" % test_dir)

    """对快照1进行revert"""
    snap_info1 = snap_common.get_snapshot_by_name(snap_name1)
    snap_id1 = snap_info1['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id1)
    if 0 != rc:
        log.error('revert_snapshot %s failed!!!' % snap_name1)
        raise Exception('revert_snapshot %s failed!!!' % snap_name1)
    snap_common.check_revert_finished(snap_id1)

    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20下是否是目录test_dir1"""
    cmd='ls %s'% SNAP_TRUE_PATH
    rc,stdout=common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip() != 'test_dir1':
        log.error(' %s item failed!!!' % snap_name1)
        raise Exception(' %s item failed!!!' % snap_name1)
    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1下是否是目录test1"""
    cmd="ls -l %s| grep '^d'"% test_dir
    rc,stdout=common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip().split()[-1] != 'test1':
        log.error(' %s item failed!!!' % snap_name1)
        raise Exception(' %s item failed!!!' % snap_name1)
    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1下是否是文件test_file,并且内容为空"""
    cmd="ls -l %s| grep '^-'"% test_dir
    rc,stdout=common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip().split()[-1] != 'test_file':
        log.error(' %s item failed!!!' % snap_name1)
        raise Exception(' %s item failed!!!' % snap_name1)
    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1下文件test_file内容是否为空"""
    cmd="cat %s"% test_file
    rc,stdout=common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip()!= '':
        log.error(' %s item failed!!!' % test_file)
        raise Exception(' %s item failed!!!' % test_file)

    """对快照4进行revert"""
    snap_info4 = snap_common.get_snapshot_by_name(snap_name4)
    snap_id4 = snap_info4['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id4)
    if 0 != rc:
        log.error('revert_snapshot %s failed!!!' % snap_name4)
        raise Exception('revert_snapshot %s failed!!!' % snap_name4)
    snap_common.check_revert_finished(snap_id4)

    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20下是否是目录test_dir2"""
    cmd='ls %s'% SNAP_TRUE_PATH
    rc,stdout=common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip() != 'test_dir2':
        log.error(' %s item failed!!!' % snap_name1)
        raise Exception(' %s item failed!!!' % snap_name1)

    """对快照5进行revert"""
    snap_info5 = snap_common.get_snapshot_by_name(snap_name5)
    snap_id5 = snap_info5['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id5)
    if 0 != rc:
        log.error('revert_snapshot %s failed!!!' % snap_name5)
        raise Exception('revert_snapshot %s failed!!!' % snap_name5)
    snap_common.check_revert_finished(snap_id5)

    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20校验目录里面的内容是否为空的"""
    cmd='ls %s'% SNAP_TRUE_PATH
    rc,stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if '' != stdout:
        log.error(' %s item failed!!!' % snap_name1)
        raise Exception(' %s item failed!!!' % snap_name1)

    """对快照2进行revert"""
    snap_info2 = snap_common.get_snapshot_by_name(snap_name2)
    snap_id2 = snap_info2['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id2)
    if 0 != rc:
        log.error('revert_snapshot %s failed!!!' % snap_name2)
        raise Exception('revert_snapshot %s failed!!!' % snap_name2)
    snap_common.check_revert_finished(snap_id2)

    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20下是否是目录test_dir1"""
    cmd='ls %s'% SNAP_TRUE_PATH
    rc,stdout=common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip() != 'test_dir1':
        log.error(' %s item failed!!!' % snap_name1)
        raise Exception(' %s item failed!!!' % snap_name1)
    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1下是否为目录test12"""
    cmd="ls -l %s| grep '^d'"% test_dir
    rc,stdout=common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip().split()[-1] != 'test12':
        log.error(' %s item failed!!!' % snap_name1)
        raise Exception(' %s item failed!!!' % snap_name1)
    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1下是否是文件test_file,并且内容为111"""
    cmd="ls -l %s| grep '^-'"% test_dir
    rc,stdout=common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip().split()[-1] != 'test_file':
        log.error(' %s item failed!!!' % snap_name1)
        raise Exception(' %s item failed!!!' % snap_name1)
    """对目录/mnt/wangguanglin/snap/snap_13_0_5_20/test_dir1下文件test_file内容是否为111"""
    cmd="cat %s"% test_file
    rc,stdout=common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip()!= '111':
        log.error(' %s item failed!!!' % test_file)
        raise Exception(' %s item failed!!!' % test_file)

    """ 删除快照"""
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete failed!!!' % (FILE_NAME))
        raise Exception('%s delete failed!!!' % (FILE_NAME))

    return

def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)

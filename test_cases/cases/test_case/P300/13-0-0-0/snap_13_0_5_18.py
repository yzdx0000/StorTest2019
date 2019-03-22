# -*-coding:utf-8 -*
# !/usr/bin/python

import os
import time
import commands

import utils_path
import common
import snap_common
import log
import tool_use
import prepare_clean
import get_config

# =================================================================================
#  latest update:2018-05-10                                                    =
#  author:wangguanglin                                                           =
# =================================================================================
# 2018-05-08:
# 修改者：wangguanglin
# @summary：
#   创建多个目录快照（同一目录），按照快照创建逆序revert，
#   每次目录内容是正确的（每个快照之间分别对目录进行修改内容、修改属性、修改名字、移动位置、删除目录）
# @steps:
#   1、部署3个客户端；
#   2、对目录/mnt/wangguanglin/snap/创建快照a1；
#   3、客户端1在目录/mnt/wangguanglin/snap/下跑vdbench 00脚本（创建文件）；
#   4、对目录/mnt/wangguanglin/snap/创建快照a2；
#   5、客户端2在目录/mnt/wangguanglin/snap/下跑vdbench 00脚本（修改一个参数，修改文件内容）；
#   6、对目录/mnt/wangguanglin/snap/创建快照a3；
#   7、客户端3修改目录/mnt/wangguanglin/snap/的权限；
#   8、对目录/mnt/wangguanglin/snap/创建快照a4；
#   9、客户端1修改目录/mnt/wangguanglin/snap/为/mnt/parastor/snap1/;
#   10、对目录/mnt/wangguanglin/snap1/创建快照a5；
#   11、客户端2删除目录/mnt/wangguanglin/snap1/；
#   12、按照a5、a4、a3、a2（a2需要跑vdbench 01脚本进行数据校验）、a1的顺序依次revert，观察快照源目录情况；
#   13、删除快照；
#   14、3个客户端检查是否有快照路径入口；
#
# changelog:
######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/wangguanglin/snap/snap_13_0_5_18
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_5_18


def case():
    """对目录/mnt/wangguanglin/snap/snap_13_0_5_18创建快照1"""
    snap_name1 = FILE_NAME + '_snapshot1'
    path1 = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name1, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    """创建子目录/mnt/wangguanglin/snap/snap_13_0_5_17/vdbench"""
    test_dir = os.path.join(SNAP_TRUE_PATH, 'vdbench')
    cmd = 'mkdir %s' % test_dir
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """客户端1对目录/mnt/wangguanglin/snap/snap_13_0_5_18执行vdbench 00脚本"""
    tool_use.vdbench_run(test_dir, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_create=True)

    """对目录/mnt/wangguanglin/snap/snap_13_0_5_18创建快照2"""
    snap_name2 = FILE_NAME + '_snapshot2'
    rc, stdout = snap_common.create_snapshot(snap_name2, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name2)
        raise Exception('create_snapshot %s failed!!!' % snap_name2)

    """客户端2对目录/mnt/wangguanglin/snap/snap_13_0_5_18执行vdbench 修改文件内容"""
    tool_use.vdbench_run(test_dir, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_write=True)

    """对目录/mnt/wangguanglin/snap/snap_13_0_5_18创建快照3"""
    snap_name3 = FILE_NAME + '_snapshot3'
    rc, stdout = snap_common.create_snapshot(snap_name3, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name3)
        raise Exception('create_snapshot %s failed!!!' % snap_name3)

    """客户端3修改/mnt/wangguanglin/snap/snap_13_0_5_18权限"""
    cmd = 'chmod 522 %s' % SNAP_TRUE_PATH
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """对目录/mnt/wangguanglin/snap/snap_13_0_5_18创建快照4"""
    snap_name4 = FILE_NAME + '_snapshot4'
    rc, stdout = snap_common.create_snapshot(snap_name4, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name4)
        raise Exception('create_snapshot %s failed!!!' % snap_name4)

    """客户端1修改/mnt/wangguanglin/snap/snap_13_0_5_18/vdbench目录名"""
    test_dir1 = os.path.join(SNAP_TRUE_PATH, 'vdbench1')
    cmd = 'mv %s %s' % (test_dir, test_dir1)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """对目录/mnt/wangguanglin/snap/snap_13_0_5_18创建快照5"""
    snap_name5 = FILE_NAME + '_snapshot5'
    rc, stdout = snap_common.create_snapshot(snap_name5, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name5)
        raise Exception('create_snapshot %s failed!!!' % snap_name5)

    """客户端2删除/mnt/wangguanglin/snap/snap_13_0_5_18/vdbench1"""
    cmd = 'rm -rf %s' % test_dir1
    common.run_command(snap_common.CLIENT_IP_2, cmd)

    """对快照5进行revert"""
    snap_info5 = snap_common.get_snapshot_by_name(snap_name5)
    snap_id5 = snap_info5['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id5)
    if 0 != rc:
        log.error('revert_snapshot %s failed!!!' % snap_name5)
        raise Exception('revert_snapshot %s failed!!!' % snap_name5)
    snap_common.check_revert_finished(snap_id5)

    """对目录/mnt/wangguanglin/snap/snap_13_0_5_18校验目录里面的内容是否为目录vdbench1"""
    cmd = 'ls %s' % SNAP_TRUE_PATH
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip() != 'vdbench1':
        log.error('%s item failed!!!' % snap_name5)
        raise Exception('%s item failed!!!' % snap_name5)

    """对快照4进行revert"""
    snap_info4 = snap_common.get_snapshot_by_name(snap_name4)
    snap_id4 = snap_info4['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id4)
    if 0 != rc:
        log.error('revert_snapshot %s failed!!!' % snap_name4)
        raise Exception('revert_snapshot %s failed!!!' % snap_name4)
    snap_common.check_revert_finished(snap_id4)

    """获取文件权限"""
    rc, stdout = snap_common.get_file_permission(snap_common.CLIENT_IP_2, SNAP_TRUE_PATH)
    if stdout != '522':
        log.error("%s permission is not right!!!" % SNAP_TRUE_PATH)
        raise Exception("%s permission is not right!!!" % SNAP_TRUE_PATH)

    """对快照3进行revert"""
    snap_info3 = snap_common.get_snapshot_by_name(snap_name3)
    snap_id3 = snap_info3['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id3)
    if 0 != rc:
        log.error('revert_snapshot %s failed!!!' % snap_name3)
        raise Exception('revert_snapshot %s failed!!!' % snap_name3)
    snap_common.check_revert_finished(snap_id3)

    """对快照2进行revert"""
    snap_info2 = snap_common.get_snapshot_by_name(snap_name2)
    snap_id2 = snap_info2['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id2)
    if 0 != rc:
        log.error('revert_snapshot %s failed!!!' % snap_name2)
        raise Exception('revert_snapshot %s failed!!!' % snap_name2)
    snap_common.check_revert_finished(snap_id2)

    """客户端2对目录/mnt/wangguanglin/snap/snap_13_0_5_18执行vdbench 01 脚本(校验数据一致性)"""
    tool_use.vdbench_run(test_dir, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_check=True)

    """对快照1进行revert"""
    snap_info1 = snap_common.get_snapshot_by_name(snap_name1)
    snap_id1 = snap_info1['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id1)
    if 0 != rc:
        log.error('revert_snapshot %s failed!!!' % snap_name1)
        raise Exception('revert_snapshot %s failed!!!' % snap_name1)
    snap_common.check_revert_finished(snap_id1)

    """对目录/mnt/wangguanglin/snap/snap_13_0_5_18校验目录里面的内容是否为空的"""
    cmd = 'ls %s' % SNAP_TRUE_PATH
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if '' != stdout:
        log.error(' %s item failed!!!' % snap_name1)
        raise Exception(' %s item failed!!!' % snap_name1)

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
